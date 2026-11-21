"""
routes/notifications.py
-----------------------
In-app notification list, mark-as-read actions.
"""

from flask import Blueprint, g, redirect, render_template, request, url_for

from extensions import db
from models import Notification
from utils import login_required

notifications_bp = Blueprint("notifications", __name__, url_prefix="/notifications")


@notifications_bp.route("/")
@login_required()
def list_notifications():
    items = (
        Notification.query.filter_by(user_id=g.user.id)
        .order_by(Notification.created_at.desc())
        .all()
    )
    return render_template("notifications.html", notifications=items)


@notifications_bp.route("/<int:notification_id>/read", methods=["POST"])
@login_required()
def mark_read(notification_id):
    notification = db.get_or_404(Notification, notification_id)
    if notification.user_id != g.user.id:
        return redirect(url_for("notifications.list_notifications"))

    notification.is_read = True
    db.session.commit()

    target = request.form.get("next") or notification.link
    if target and target.startswith("/") and not target.startswith("//"):
        return redirect(target)
    return redirect(url_for("notifications.list_notifications"))


@notifications_bp.route("/read-all", methods=["POST"])
@login_required()
def mark_all_read():
    Notification.query.filter_by(user_id=g.user.id, is_read=False).update({"is_read": True})
    db.session.commit()
    return redirect(url_for("notifications.list_notifications"))
