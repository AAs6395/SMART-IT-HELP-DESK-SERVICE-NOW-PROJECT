"""
routes/admin.py
---------------
Administrator area:
    * dashboard with live statistics and Chart.js data
    * user management (view, add support staff, activate / deactivate)
    * category management
    * reports with date filters and CSV export
"""

import csv
import io
from datetime import datetime

from flask import (
    Blueprint,
    Response,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
)
from sqlalchemy import func

from extensions import db
from models import Category, TICKET_PRIORITIES, TICKET_STATUSES, Ticket, User
from routes.auth import EMAIL_PATTERN, MIN_PASSWORD_LENGTH
from utils import login_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _status_counts(query=None):
    """Return {status: count} for all five ticket statuses."""
    query = query or Ticket.query
    return {
        status: query.filter(Ticket.status == status).count() for status in TICKET_STATUSES
    }


def _priority_counts(query=None):
    query = query or Ticket.query
    return {
        priority: query.filter(Ticket.priority == priority).count()
        for priority in TICKET_PRIORITIES
    }


def _category_counts(query=None):
    query = query or Ticket.query
    rows = (
        query.with_entities(Category.name, func.count(Ticket.id))
        .join(Category, Ticket.category_id == Category.id)
        .group_by(Category.id)
        .order_by(Category.name)
        .all()
    )
    return [(name, count) for name, count in rows]


def _monthly_counts(query=None, months=6):
    """Ticket counts for the last `months` months -> [(label, count), ...]."""
    query = query or Ticket.query
    rows = (
        query.with_entities(func.strftime("%Y-%m", Ticket.created_at), func.count(Ticket.id))
        .group_by(func.strftime("%Y-%m", Ticket.created_at))
        .all()
    )
    lookup = {key: count for key, count in rows}

    today = datetime.now()
    series = []
    for offset in range(months - 1, -1, -1):
        year, month = today.year, today.month - offset
        while month <= 0:
            month += 12
            year -= 1
        key = f"{year:04d}-{month:02d}"
        series.append((datetime(year, month, 1).strftime("%b %Y"), lookup.get(key, 0)))
    return series


def _parse_date(value):
    """Convert a HTML date input value (YYYY-MM-DD) into a date, safely."""
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def _report_query(date_from, date_to):
    """Base ticket query filtered by an optional date range."""
    query = Ticket.query
    if date_from:
        query = query.filter(Ticket.created_at >= datetime.combine(date_from, datetime.min.time()))
    if date_to:
        query = query.filter(Ticket.created_at <= datetime.combine(date_to, datetime.max.time()))
    return query


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
@admin_bp.route("/dashboard")
@login_required("admin")
def dashboard():
    status_counts = _status_counts()
    priority_counts = _priority_counts()
    category_counts = _category_counts()
    monthly_counts = _monthly_counts()

    stats = {
        "total": Ticket.query.count(),
        "open": status_counts["Open"],
        "assigned": status_counts["Assigned"],
        "in_progress": status_counts["In Progress"],
        "resolved": status_counts["Resolved"],
        "closed": status_counts["Closed"],
        "users": User.query.filter_by(role="user").count(),
        "support_staff": User.query.filter_by(role="support").count(),
        "unresolved": status_counts["Open"]
        + status_counts["Assigned"]
        + status_counts["In Progress"],
    }

    unresolved_tickets = Ticket.query.filter(Ticket.status.in_(["Open", "Assigned", "In Progress"])).all()
    sla_breached_count = sum(1 for t in unresolved_tickets if t.is_sla_breached)

    recent_tickets = Ticket.query.order_by(Ticket.created_at.desc()).limit(8).all()

    chart_data = {
        "status_labels": list(status_counts.keys()),
        "status_values": list(status_counts.values()),
        "priority_labels": list(priority_counts.keys()),
        "priority_values": list(priority_counts.values()),
        "category_labels": [name for name, _ in category_counts],
        "category_values": [count for _, count in category_counts],
        "monthly_labels": [label for label, _ in monthly_counts],
        "monthly_values": [count for _, count in monthly_counts],
    }

    return render_template(
        "admin_dashboard.html",
        stats=stats,
        recent_tickets=recent_tickets,
        chart_data=chart_data,
        sla_breached_count=sla_breached_count,
    )


# ---------------------------------------------------------------------------
# User management
# ---------------------------------------------------------------------------
@admin_bp.route("/users")
@login_required("admin")
def users():
    query = User.query
    search = request.args.get("q", "").strip()
    role = request.args.get("role", "").strip()

    if search:
        like = f"%{search}%"
        query = query.filter(db.or_(User.name.ilike(like), User.email.ilike(like)))
    if role in ("user", "support", "admin"):
        query = query.filter(User.role == role)

    all_users = query.order_by(User.created_at.desc()).all()
    return render_template(
        "manage_users.html",
        users=all_users,
        search=search,
        role=role,
        support_staff=User.query.filter_by(role="support").order_by(User.name).all(),
    )


@admin_bp.route("/users/new", methods=["POST"])
@login_required("admin")
def add_support_staff():
    """Create a support staff account (only admins can do this)."""
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    department = request.form.get("department", "IT Support").strip()
    password = request.form.get("password", "")
    confirm = request.form.get("confirm_password", "")

    errors = []
    if len(name) < 3:
        errors.append("Staff name must be at least 3 characters long.")
    if not EMAIL_PATTERN.match(email):
        errors.append("Please enter a valid email address.")
    if len(password) < MIN_PASSWORD_LENGTH:
        errors.append(f"Password must be at least {MIN_PASSWORD_LENGTH} characters long.")
    if password != confirm:
        errors.append("The two passwords do not match.")
    if User.query.filter(db.func.lower(User.email) == email).first():
        errors.append("An account with this email address already exists.")

    if errors:
        for message in errors:
            flash(message, "danger")
    else:
        staff = User(name=name, email=email, department=department, role="support")
        staff.set_password(password)
        db.session.add(staff)
        db.session.commit()
        flash(f"Support staff account created for {name}.", "success")

    return redirect(url_for("admin.users"))


@admin_bp.route("/users/<int:user_id>/toggle", methods=["POST"])
@login_required("admin")
def toggle_user(user_id):
    """Activate or deactivate an account (never deletes history)."""
    user = db.get_or_404(User, user_id)
    if user.id == g.user.id:
        flash("You cannot deactivate your own account.", "warning")
        return redirect(url_for("admin.users"))

    user.is_active = not user.is_active
    db.session.commit()
    state = "activated" if user.is_active else "deactivated"
    flash(f"Account for {user.name} has been {state}.", "success")
    return redirect(url_for("admin.users"))


# ---------------------------------------------------------------------------
# Category management
# ---------------------------------------------------------------------------
@admin_bp.route("/categories", methods=["GET", "POST"])
@login_required("admin")
def categories():
    edit_id = request.args.get("edit", type=int)
    editing = db.session.get(Category, edit_id) if edit_id else None

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        category_id = request.form.get("category_id", type=int)

        if len(name) < 3:
            flash("Category name must be at least 3 characters long.", "danger")
            return redirect(url_for("admin.categories"))

        duplicate = Category.query.filter(
            db.func.lower(Category.name) == name.lower()
        ).first()
        if duplicate and duplicate.id != category_id:
            flash("A category with that name already exists.", "danger")
            return redirect(url_for("admin.categories"))

        if category_id:
            category = db.get_or_404(Category, category_id)
            category.name = name
            category.description = description
            flash("Category updated successfully.", "success")
        else:
            db.session.add(Category(name=name, description=description))
            flash("Category added successfully.", "success")

        db.session.commit()
        return redirect(url_for("admin.categories"))

    all_categories = Category.query.order_by(Category.name).all()
    counts = dict(
        db.session.query(Ticket.category_id, func.count(Ticket.id))
        .group_by(Ticket.category_id)
        .all()
    )
    return render_template(
        "categories.html", categories=all_categories, counts=counts, editing=editing
    )


@admin_bp.route("/categories/<int:category_id>/delete", methods=["POST"])
@login_required("admin")
def delete_category(category_id):
    category = db.get_or_404(Category, category_id)
    ticket_count = Ticket.query.filter_by(category_id=category.id).count()
    if ticket_count:
        flash(
            f"'{category.name}' cannot be deleted because {ticket_count} ticket(s) use it.",
            "warning",
        )
    else:
        db.session.delete(category)
        db.session.commit()
        flash("Category deleted.", "success")
    return redirect(url_for("admin.categories"))


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------
@admin_bp.route("/reports")
@login_required("admin")
def reports():
    date_from = _parse_date(request.args.get("date_from"))
    date_to = _parse_date(request.args.get("date_to"))
    query = _report_query(date_from, date_to)

    tickets = query.order_by(Ticket.created_at.desc()).all()
    status_counts = _status_counts(query)
    priority_counts = _priority_counts(query)

    staff_rows = []
    for staff in User.query.filter_by(role="support").order_by(User.name).all():
        staff_tickets = query.filter(Ticket.assigned_to == staff.id)
        staff_rows.append(
            {
                "name": staff.name,
                "assigned": staff_tickets.count(),
                "resolved": staff_tickets.filter(
                    Ticket.status.in_(["Resolved", "Closed"])
                ).count(),
                "pending": staff_tickets.filter(
                    Ticket.status.in_(["Open", "Assigned", "In Progress"])
                ).count(),
            }
        )

    return render_template(
        "reports.html",
        tickets=tickets,
        total=len(tickets),
        resolved=status_counts["Resolved"] + status_counts["Closed"],
        pending=status_counts["Open"] + status_counts["Assigned"] + status_counts["In Progress"],
        status_counts=status_counts,
        priority_counts=priority_counts,
        category_counts=_category_counts(query),
        monthly_counts=_monthly_counts(query, months=12),
        staff_rows=staff_rows,
        date_from=request.args.get("date_from", ""),
        date_to=request.args.get("date_to", ""),
    )


@admin_bp.route("/reports/export")
@login_required("admin")
def export_report():
    """Download the filtered ticket list as a CSV file."""
    date_from = _parse_date(request.args.get("date_from"))
    date_to = _parse_date(request.args.get("date_to"))
    tickets = (
        _report_query(date_from, date_to).order_by(Ticket.created_at.desc()).all()
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "Ticket ID",
            "Title",
            "Category",
            "Priority",
            "Status",
            "Submitted By",
            "Assigned To",
            "Created At",
            "Resolved At",
            "Resolution Notes",
        ]
    )
    for ticket in tickets:
        writer.writerow(
            [
                ticket.ticket_number,
                ticket.title,
                ticket.category.name if ticket.category else "",
                ticket.priority,
                ticket.status,
                ticket.creator.name if ticket.creator else "",
                ticket.assignee.name if ticket.assignee else "Unassigned",
                ticket.created_at.strftime("%Y-%m-%d %H:%M"),
                ticket.resolved_at.strftime("%Y-%m-%d %H:%M") if ticket.resolved_at else "",
                (ticket.resolution_notes or "").replace("\n", " "),
            ]
        )

    filename = f"helpdesk_tickets_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    return Response(
        "\ufeff" + output.getvalue(),  # BOM so Excel opens it correctly
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
