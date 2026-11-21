"""
routes/tickets.py
-----------------
Everything about tickets:
    * create a ticket (with attachment)
    * list / search / filter / sort tickets (scoped by role)
    * ticket details with comments, resolution notes and history
    * assign / change priority / change status / delete
    * download an attachment (permission checked)

Every change also creates a notification and a ticket history entry, which
implements the automated workflow required by the project.
"""

import os
from datetime import datetime

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    g,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from sqlalchemy import case, or_

from extensions import db
from models import (
    Category,
    Comment,
    TICKET_PRIORITIES,
    TICKET_STATUSES,
    Ticket,
    User,
)
from utils import (
    create_notification,
    get_ticket_or_403,
    log_activity,
    login_required,
    next_ticket_number,
    save_attachment,
)

tickets_bp = Blueprint("tickets", __name__, url_prefix="/tickets")

# Which statuses support staff are allowed to set.
SUPPORT_ALLOWED_STATUSES = ("In Progress", "Resolved", "Closed")


def _support_staff_choices():
    """Active support staff, used in the admin assignment dropdown."""
    return User.query.filter_by(role="support", is_active=True).order_by(User.name).all()


@tickets_bp.route("/")
@login_required()
def list_tickets():
    """Ticket table with search, filters and sorting. Scope depends on role."""
    query = Ticket.query

    if g.user.role == "user":
        query = query.filter(Ticket.created_by == g.user.id)
    elif g.user.role == "support":
        query = query.filter(Ticket.assigned_to == g.user.id)

    # Search
    search = request.args.get("q", "").strip()
    if search:
        like = f"%{search}%"
        query = query.filter(
            or_(
                Ticket.ticket_number.ilike(like),
                Ticket.title.ilike(like),
                Ticket.description.ilike(like),
            )
        )

    # Filters
    status = request.args.get("status", "").strip()
    priority = request.args.get("priority", "").strip()
    category_id = request.args.get("category", type=int)
    date_from = request.args.get("date_from", "").strip()
    date_to = request.args.get("date_to", "").strip()

    if status in TICKET_STATUSES:
        query = query.filter(Ticket.status == status)
    if priority in TICKET_PRIORITIES:
        query = query.filter(Ticket.priority == priority)
    if category_id:
        query = query.filter(Ticket.category_id == category_id)
    try:
        if date_from:
            query = query.filter(
                Ticket.created_at >= datetime.strptime(date_from, "%Y-%m-%d")
            )
        if date_to:
            query = query.filter(
                Ticket.created_at
                <= datetime.strptime(date_to, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
            )
    except ValueError:
        flash("Invalid date filter was ignored.", "warning")

    # Sorting
    sort = request.args.get("sort", "newest")
    if sort == "oldest":
        query = query.order_by(Ticket.created_at.asc())
    elif sort == "priority":
        query = query.order_by(
            case(
                (Ticket.priority == "Critical", 1),
                (Ticket.priority == "High", 2),
                (Ticket.priority == "Medium", 3),
                else_=4,
            ),
            Ticket.created_at.desc(),
        )
    elif sort == "status":
        query = query.order_by(Ticket.status.asc(), Ticket.created_at.desc())
    else:
        sort = "newest"
        query = query.order_by(Ticket.created_at.desc())

    return render_template(
        "ticket_list.html",
        tickets=query.all(),
        categories=Category.query.order_by(Category.name).all(),
        statuses=TICKET_STATUSES,
        priorities=TICKET_PRIORITIES,
        filters={
            "q": search,
            "status": status,
            "priority": priority,
            "category": category_id or "",
            "date_from": date_from,
            "date_to": date_to,
            "sort": sort,
        },
    )


@tickets_bp.route("/new", methods=["GET", "POST"])
@login_required()
def create():
    """Create a new support ticket."""
    categories = Category.query.order_by(Category.name).all()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        category_id = request.form.get("category_id", type=int)
        priority = request.form.get("priority", "Medium").strip()

        errors = []
        if len(title) < 5:
            errors.append("The ticket title must be at least 5 characters long.")
        if len(description) < 15:
            errors.append("Please describe the problem in at least 15 characters.")
        if not category_id or db.session.get(Category, category_id) is None:
            errors.append("Please choose a valid category.")
        if priority not in TICKET_PRIORITIES:
            errors.append("Please choose a valid priority.")

        if errors:
            for message in errors:
                flash(message, "danger")
            return (
                render_template(
                    "create_ticket.html",
                    categories=categories,
                    priorities=TICKET_PRIORITIES,
                    form=request.form,
                ),
                400,
            )

        # Save the attachment first so an invalid file does not create a ticket.
        try:
            attachment = save_attachment(
                request.files.get("attachment"),
                current_app.config["UPLOAD_FOLDER"],
                current_app.config["ALLOWED_EXTENSIONS"],
            )
        except ValueError as error:
            flash(str(error), "danger")
            return (
                render_template(
                    "create_ticket.html",
                    categories=categories,
                    priorities=TICKET_PRIORITIES,
                    form=request.form,
                ),
                400,
            )

        # ---- Automation 1: create the ticket, set defaults, notify admins ----
        ticket = Ticket(
            ticket_number=next_ticket_number(),
            title=title,
            description=description,
            category_id=category_id,
            priority=priority,
            status="Open",
            created_by=g.user.id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            attachment=attachment,
        )
        db.session.add(ticket)
        db.session.flush()  # get the id before writing history/notifications

        log_activity(
            ticket,
            g.user,
            f"Ticket {ticket.ticket_number} created with status Open.",
            old_status=None,
            new_status="Open",
        )

        ticket_link = url_for("tickets.detail", ticket_id=ticket.id)
        for admin in User.query.filter_by(role="admin", is_active=True).all():
            create_notification(
                admin.id,
                f"New ticket {ticket.ticket_number}: {ticket.title}",
                ticket_link,
            )
        create_notification(
            g.user.id,
            f"Your ticket {ticket.ticket_number} was submitted successfully.",
            ticket_link,
        )
        db.session.commit()

        flash(f"Ticket {ticket.ticket_number} created successfully.", "success")
        return redirect(url_for("tickets.detail", ticket_id=ticket.id))

    return render_template(
        "create_ticket.html",
        categories=categories,
        priorities=TICKET_PRIORITIES,
        form={},
    )


@tickets_bp.route("/<int:ticket_id>")
@login_required()
def detail(ticket_id):
    """Full ticket page: details, comments, resolution notes and history."""
    ticket = get_ticket_or_403(ticket_id, g.user)

    can_manage = g.user.role == "admin" or (
        g.user.role == "support" and ticket.assigned_to == g.user.id
    )
    allowed_statuses = []
    if g.user.role == "admin":
        allowed_statuses = list(TICKET_STATUSES)
    elif can_manage:
        # Support staff can start, resolve or close their own tickets.
        allowed_statuses = list(SUPPORT_ALLOWED_STATUSES)

    return render_template(
        "ticket_details.html",
        ticket=ticket,
        can_manage=can_manage,
        allowed_statuses=allowed_statuses,
        support_staff=_support_staff_choices() if g.user.role == "admin" else [],
        priorities=TICKET_PRIORITIES,
        statuses=TICKET_STATUSES,
    )


@tickets_bp.route("/<int:ticket_id>/comment", methods=["POST"])
@login_required()
def add_comment(ticket_id):
    """Add a comment to a ticket (owner, assigned staff or admin)."""
    ticket = get_ticket_or_403(ticket_id, g.user)
    text = request.form.get("comment_text", "").strip()

    if len(text) < 2:
        flash("Please write a comment before submitting.", "danger")
        return redirect(url_for("tickets.detail", ticket_id=ticket.id))

    comment = Comment(ticket_id=ticket.id, user_id=g.user.id, comment_text=text)
    db.session.add(comment)

    log_activity(ticket, g.user, f"{g.user.name} added a comment.")

    # Notify the other people involved in the ticket.
    link = url_for("tickets.detail", ticket_id=ticket.id)
    recipients = {ticket.created_by, ticket.assigned_to}
    recipients.discard(None)
    recipients.discard(g.user.id)
    for user_id in recipients:
        create_notification(
            user_id, f"New comment on ticket {ticket.ticket_number}.", link
        )

    ticket.updated_at = datetime.now()
    db.session.commit()

    flash("Comment added.", "success")
    return redirect(url_for("tickets.detail", ticket_id=ticket.id))


@tickets_bp.route("/<int:ticket_id>/status", methods=["POST"])
@login_required("admin", "support")
def update_status(ticket_id):
    """Change the ticket status (and optionally save resolution notes)."""
    ticket = get_ticket_or_403(ticket_id, g.user)

    if g.user.role == "support" and ticket.assigned_to != g.user.id:
        abort(403)

    new_status = request.form.get("new_status", "").strip()
    if new_status not in TICKET_STATUSES:
        flash("Unknown status.", "danger")
        return redirect(url_for("tickets.detail", ticket_id=ticket.id))

    if g.user.role == "support" and new_status not in SUPPORT_ALLOWED_STATUSES:
        flash("Support staff can only move a ticket to In Progress, Resolved or Closed.", "danger")
        return redirect(url_for("tickets.detail", ticket_id=ticket.id))

    old_status = ticket.status
    notes = request.form.get("resolution_notes", "").strip()

    if new_status == "Resolved":
        notes = notes or (ticket.resolution_notes or "")
        if len(notes) < 5:
            flash("Please enter resolution notes before marking the ticket as Resolved.", "danger")
            return redirect(url_for("tickets.detail", ticket_id=ticket.id))
        ticket.resolution_notes = notes
        ticket.resolved_at = datetime.now()
    elif old_status == "Resolved":
        # Re-opening a ticket clears the resolution date.
        ticket.resolved_at = None

    if notes and new_status != "Resolved":
        ticket.resolution_notes = notes

    # Automation 3: support staff working on an unassigned ticket.
    if new_status == "In Progress" and ticket.assigned_to is None and g.user.role == "support":
        ticket.assigned_to = g.user.id

    ticket.status = new_status
    ticket.updated_at = datetime.now()

    log_activity(
        ticket,
        g.user,
        f"Status changed from {old_status} to {new_status} by {g.user.name}.",
        old_status=old_status,
        new_status=new_status,
    )

    # Automation 3 & 4: notify the employee.
    link = url_for("tickets.detail", ticket_id=ticket.id)
    create_notification(
        ticket.created_by,
        f"Ticket {ticket.ticket_number} is now {new_status}.",
        link,
    )

    db.session.commit()
    flash(f"Ticket status updated to {new_status}.", "success")
    return redirect(url_for("tickets.detail", ticket_id=ticket.id))


@tickets_bp.route("/<int:ticket_id>/assign", methods=["POST"])
@login_required("admin")
def assign(ticket_id):
    """Assign a ticket to a support staff member (Automation 2)."""
    ticket = get_ticket_or_403(ticket_id, g.user)
    assigned_to = request.form.get("assigned_to", type=int)

    if not assigned_to:
        # Unassign
        if ticket.assigned_to:
            old_staff = ticket.assignee.name
            ticket.assigned_to = None
            log_activity(ticket, g.user, f"Ticket unassigned from {old_staff}.")
            db.session.commit()
            flash("Ticket is no longer assigned.", "success")
        return redirect(url_for("tickets.detail", ticket_id=ticket.id))

    staff = db.session.get(User, assigned_to)
    if staff is None or staff.role != "support" or not staff.is_active:
        flash("Please choose a valid, active support staff member.", "danger")
        return redirect(url_for("tickets.detail", ticket_id=ticket.id))

    old_status = ticket.status
    ticket.assigned_to = staff.id
    if ticket.status in ("Open", "Assigned"):
        ticket.status = "Assigned"
    ticket.updated_at = datetime.now()

    log_activity(
        ticket,
        g.user,
        f"Ticket assigned to {staff.name} by {g.user.name}.",
        old_status=old_status,
        new_status=ticket.status,
    )

    link = url_for("tickets.detail", ticket_id=ticket.id)
    create_notification(
        staff.id,
        f"New ticket assigned to you: {ticket.ticket_number} - {ticket.title}",
        link,
    )
    create_notification(
        ticket.created_by,
        f"Your ticket {ticket.ticket_number} was assigned to {staff.name}.",
        link,
    )

    db.session.commit()
    flash(f"Ticket assigned to {staff.name}.", "success")
    return redirect(url_for("tickets.detail", ticket_id=ticket.id))


@tickets_bp.route("/<int:ticket_id>/priority", methods=["POST"])
@login_required("admin")
def update_priority(ticket_id):
    """Admin can change the priority of a ticket."""
    ticket = get_ticket_or_403(ticket_id, g.user)
    priority = request.form.get("priority", "").strip()

    if priority not in TICKET_PRIORITIES:
        flash("Unknown priority.", "danger")
        return redirect(url_for("tickets.detail", ticket_id=ticket.id))

    old_priority = ticket.priority
    ticket.priority = priority
    ticket.updated_at = datetime.now()
    log_activity(
        ticket,
        g.user,
        f"Priority changed from {old_priority} to {priority} by {g.user.name}.",
    )
    create_notification(
        ticket.created_by,
        f"Priority of ticket {ticket.ticket_number} changed to {priority}.",
        url_for("tickets.detail", ticket_id=ticket.id),
    )
    db.session.commit()

    flash(f"Priority updated to {priority}.", "success")
    return redirect(url_for("tickets.detail", ticket_id=ticket.id))


@tickets_bp.route("/<int:ticket_id>/delete", methods=["POST"])
@login_required("admin")
def delete(ticket_id):
    """Admin can remove an inappropriate or test ticket."""
    ticket = get_ticket_or_403(ticket_id, g.user)
    number = ticket.ticket_number

    # Remove the uploaded file as well (if any).
    if ticket.attachment:
        file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], ticket.attachment)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                pass

    db.session.delete(ticket)
    db.session.commit()
    flash(f"Ticket {number} has been deleted.", "success")
    return redirect(url_for("tickets.list_tickets"))


@tickets_bp.route("/<int:ticket_id>/attachment")
@login_required()
def attachment(ticket_id):
    """Serve an attachment only to people allowed to see the ticket."""
    ticket = get_ticket_or_403(ticket_id, g.user)
    if not ticket.attachment:
        abort(404)
    return send_from_directory(
        current_app.config["UPLOAD_FOLDER"], ticket.attachment, as_attachment=True
    )
