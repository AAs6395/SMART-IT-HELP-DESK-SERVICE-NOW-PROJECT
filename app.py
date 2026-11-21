"""
app.py
------
Entry point of the Smart IT Help Desk Management System.

Run the project with:
    python app.py
and open http://127.0.0.1:5000/
"""

import os

from flask import Flask, flash, g, redirect, render_template, request, session, url_for

from config import Config
from extensions import csrf, db
from models import Category, Notification, TICKET_CATEGORIES, Ticket, User


def create_app(test_config=None):
    """Application factory used by app.py, flask run and the pytest fixtures."""
    """
    Application factory.

    Using a factory (instead of a global app object) lets the tests create a
    fresh application with its own separate database.
    """
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    # Create the folders we need before the database is opened.
    os.makedirs(os.path.join(os.path.dirname(__file__), "instance"), exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Attach extensions
    db.init_app(app)
    csrf.init_app(app)

    # ------------------------------------------------------------------
    # Blueprints (each file in routes/ handles one area of the system)
    # ------------------------------------------------------------------
    from routes.admin import admin_bp
    from routes.auth import auth_bp
    from routes.knowledge_base import kb_bp
    from routes.notifications import notifications_bp
    from routes.support import support_bp
    from routes.tickets import tickets_bp
    from routes.user import user_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(support_bp)
    app.register_blueprint(tickets_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(kb_bp)

    # ------------------------------------------------------------------
    # Before every request: load the logged-in user from the session.
    # ------------------------------------------------------------------
    @app.before_request
    def load_logged_in_user():
        user_id = session.get("user_id")
        g.user = db.session.get(User, user_id) if user_id else None

        # If the account was deactivated, log it out immediately.
        if g.user is not None and not g.user.is_active:
            session.clear()
            g.user = None

    # Values available inside every template.
    @app.context_processor
    def inject_globals():
        unread_count = 0
        latest_notifications = []
        if getattr(g, "user", None):
            unread_count = Notification.query.filter_by(
                user_id=g.user.id, is_read=False
            ).count()
            latest_notifications = (
                Notification.query.filter_by(user_id=g.user.id)
                .order_by(Notification.created_at.desc())
                .limit(5)
                .all()
            )
        return dict(
            unread_count=unread_count,
            latest_notifications=latest_notifications,
            dashboard_endpoint={
                "admin": "admin.dashboard",
                "support": "support.dashboard",
                "user": "user.dashboard",
            }.get(getattr(getattr(g, "user", None), "role", ""), "auth.login"),
        )

    # ------------------------------------------------------------------
    # Friendly error pages
    # ------------------------------------------------------------------
    @app.errorhandler(403)
    def forbidden(error):
        return render_template("403.html"), 403

    @app.errorhandler(404)
    def not_found(error):
        return render_template("404.html"), 404

    @app.errorhandler(413)
    def too_large(error):
        flash("The uploaded file is too large (maximum 5 MB).", "danger")
        return redirect(request.referrer or url_for("auth.index"))

    # ------------------------------------------------------------------
    # Create tables and demo accounts on first start
    # ------------------------------------------------------------------
    with app.app_context():
        db.create_all()
        seed_demo_data()

        # Demonstration dataset (tickets, comments, history, notifications).
        # It only runs when the tickets table is empty; tests disable it.
        if app.config.get("SEED_SAMPLE_DATA", True):
            from seed_data import seed_sample_data

            seed_sample_data()

    return app


def seed_demo_data():
    """
    Create the demo accounts and the default ticket categories.

    Everything is created only when it does not already exist, so restarting
    the application never duplicates or overwrites data.
    """
    demo_users = [
        {
            "name": "System Administrator",
            "email": "admin@helpdesk.com",
            "password": "Admin@123",
            "role": "admin",
            "department": "IT Department",
        },
        {
            "name": "Sam Support",
            "email": "support@helpdesk.com",
            "password": "Support@123",
            "role": "support",
            "department": "IT Support",
        },
        {
            "name": "Umar Employee",
            "email": "user@helpdesk.com",
            "password": "User@123",
            "role": "user",
            "department": "Accounts",
        },
    ]

    for data in demo_users:
        existing = User.query.filter_by(email=data["email"]).first()
        if existing is None:
            user = User(
                name=data["name"],
                email=data["email"],
                role=data["role"],
                department=data["department"],
            )
            user.set_password(data["password"])
            db.session.add(user)

    category_descriptions = {
        "Hardware Issue": "Desktop, laptop, monitor or any physical device problem.",
        "Software Issue": "Application installation, crash or license problems.",
        "Network Problem": "Internet, Wi-Fi or office network connectivity issues.",
        "Printer Issue": "Printer not working, paper jam or scanning problems.",
        "Login and Password Issue": "Account access, password reset or lockout.",
        "Email Issue": "Email sending, receiving or mailbox configuration.",
        "Other Technical Issues": "Anything that does not fit the categories above.",
    }

    for name in TICKET_CATEGORIES:
        if Category.query.filter_by(name=name).first() is None:
            db.session.add(Category(name=name, description=category_descriptions.get(name, "")))

    db.session.commit()

    # Seed default self-service Knowledge Base articles
    from seed_data import seed_knowledge_base
    seed_knowledge_base()


# The module level app object is what `flask run` uses and what `python app.py`
# starts. Tests call create_app() directly with their own configuration.
app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
