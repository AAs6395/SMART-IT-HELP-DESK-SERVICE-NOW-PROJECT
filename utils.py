"""
utils.py
--------
Small helper functions used by several routes:
    * login_required  -> protects pages and checks the user role
    * create_notification -> writes an in-app notification row
    * log_activity    -> writes a ticket history row
    * next_ticket_number -> generates readable IDs such as TKT-1001
    * save_attachment -> validates and stores uploaded files safely
"""

import os
import uuid
from functools import wraps

from flask import abort, flash, g, redirect, request, url_for
from werkzeug.utils import secure_filename

from extensions import db
from models import Notification, Ticket, TicketHistory


def login_required(*roles):
    """
    Decorator that requires a logged-in user.

    Usage:
        @login_required()               # any logged in user
        @login_required("admin")        # only administrators
        @login_required("admin", "support")
    """

    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            user = getattr(g, "user", None)
            if user is None:
                flash("Please log in to continue.", "warning")
                return redirect(url_for("auth.login", next=request.path))
            if roles and user.role not in roles:
                abort(403)
            return view(*args, **kwargs)

        return wrapped

    return decorator


def create_notification(user_id, message, link=None):
    """Save one in-app notification for a user."""
    if not user_id:
        return
    notification = Notification(user_id=user_id, message=message, link=link)
    db.session.add(notification)


def log_activity(ticket, user, description, old_status=None, new_status=None):
    """Append a row to the ticket activity history (used for the audit trail)."""
    entry = TicketHistory(
        ticket_id=ticket.id,
        changed_by=user.id,
        old_status=old_status if old_status is not None else ticket.status,
        new_status=new_status if new_status is not None else ticket.status,
        activity_description=description,
    )
    db.session.add(entry)


def next_ticket_number():
    """Return the next free readable ticket number, e.g. TKT-1001."""
    last = Ticket.query.order_by(Ticket.id.desc()).first()
    number = 1001
    if last and last.ticket_number and "-" in last.ticket_number:
        try:
            number = int(last.ticket_number.split("-")[1]) + 1
        except ValueError:
            number = 1000 + Ticket.query.count() + 1

    # Make sure the number is really unused (protects against deletions).
    while Ticket.query.filter_by(ticket_number=f"TKT-{number}").first():
        number += 1
    return f"TKT-{number}"


def allowed_file(filename, allowed_extensions):
    """True when the file has one of the allowed extensions."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


def save_attachment(file_storage, upload_folder, allowed_extensions):
    """
    Validate and save an uploaded file.

    Returns the stored file name, or None when no file was provided.
    Raises ValueError with a friendly message when the file is not allowed.
    """
    if file_storage is None or not file_storage.filename:
        return None

    original = secure_filename(file_storage.filename)
    if not original:
        raise ValueError("The uploaded file name is not valid.")

    if not allowed_file(original, allowed_extensions):
        raise ValueError(
            "Unsupported file type. Allowed types: "
            + ", ".join(sorted(allowed_extensions))
        )

    # Prefix with a random token so two users can never overwrite each other.
    stored_name = f"{uuid.uuid4().hex[:10]}_{original}"
    os.makedirs(upload_folder, exist_ok=True)
    file_storage.save(os.path.join(upload_folder, stored_name))
    return stored_name


def get_ticket_or_403(ticket_id, user):
    """
    Load a ticket and make sure the current user is allowed to see it.

    * admin   -> any ticket
    * support -> only tickets assigned to them (or created by them)
    * user    -> only tickets they created
    """
    ticket = db.session.get(Ticket, ticket_id)
    if ticket is None:
        abort(404)

    if user.role == "admin":
        return ticket
    if user.role == "support" and ticket.assigned_to == user.id:
        return ticket
    if ticket.created_by == user.id:
        return ticket
    abort(403)
