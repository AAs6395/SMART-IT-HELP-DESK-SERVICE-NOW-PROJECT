"""
routes/user.py
--------------
Dashboard and profile page for normal employees.
"""

from flask import Blueprint, flash, g, redirect, render_template, request, url_for

from extensions import db
from models import Notification, Ticket, User
from routes.auth import EMAIL_PATTERN, MIN_PASSWORD_LENGTH
from utils import login_required

user_bp = Blueprint("user", __name__, url_prefix="/user")


@user_bp.route("/dashboard")
@login_required("user", "admin", "support")
def dashboard():
    """Employee dashboard: personal statistics, recent tickets, notifications."""
    base = Ticket.query.filter_by(created_by=g.user.id)

    stats = {
        "total": base.count(),
        "open": base.filter(Ticket.status == "Open").count(),
        "assigned": base.filter(Ticket.status == "Assigned").count(),
        "in_progress": base.filter(Ticket.status == "In Progress").count(),
        "resolved": base.filter(Ticket.status.in_(["Resolved", "Closed"])).count(),
    }

    recent_tickets = (
        base.order_by(Ticket.created_at.desc()).limit(6).all()
    )
    notifications = (
        Notification.query.filter_by(user_id=g.user.id)
        .order_by(Notification.created_at.desc())
        .limit(5)
        .all()
    )

    return render_template(
        "user_dashboard.html",
        stats=stats,
        recent_tickets=recent_tickets,
        notifications=notifications,
    )


@user_bp.route("/profile", methods=["GET", "POST"])
@login_required()
def profile():
    """Let any logged-in user update their basic information."""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        department = request.form.get("department", "").strip()
        phone = request.form.get("phone", "").strip()
        current_password = request.form.get("current_password", "")
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")

        errors = []
        if len(name) < 3:
            errors.append("Name must be at least 3 characters long.")
        if not EMAIL_PATTERN.match(email):
            errors.append("Please enter a valid email address.")

        other = User.query.filter(
            db.func.lower(User.email) == email, User.id != g.user.id
        ).first()
        if other:
            errors.append("That email address is already used by another account.")

        # Changing the password is optional, but needs the current password.
        if new_password or confirm_password:
            if not g.user.check_password(current_password):
                errors.append("Your current password is incorrect.")
            if new_password != confirm_password:
                errors.append("The new passwords do not match.")
            if len(new_password) < MIN_PASSWORD_LENGTH:
                errors.append(f"New password must be at least {MIN_PASSWORD_LENGTH} characters.")

        if errors:
            for message in errors:
                flash(message, "danger")
            return render_template("profile.html", form=request.form), 400

        g.user.name = name
        g.user.email = email
        g.user.department = department
        g.user.phone = phone
        if new_password:
            g.user.set_password(new_password)

        db.session.commit()
        flash("Your profile has been updated.", "success")
        return redirect(url_for("user.profile"))

    return render_template("profile.html", form={})
