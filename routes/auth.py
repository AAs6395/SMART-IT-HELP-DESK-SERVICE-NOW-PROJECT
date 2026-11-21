"""
routes/auth.py
--------------
Login, registration, logout and the home redirect.
All three roles use the same login page; after login the user is sent to the
dashboard that matches their role.
"""

import re

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for

from extensions import db
from models import User

auth_bp = Blueprint("auth", __name__)

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")
MIN_PASSWORD_LENGTH = 6


def dashboard_url_for(user):
    """Return the dashboard URL that belongs to the user's role."""
    endpoints = {
        "admin": "admin.dashboard",
        "support": "support.dashboard",
        "user": "user.dashboard",
    }
    return url_for(endpoints.get(user.role, "auth.login"))


def _safe_next(target):
    """Only allow internal redirects (prevents open-redirect attacks)."""
    if target and target.startswith("/") and not target.startswith("//"):
        return target
    return None


@auth_bp.route("/")
def index():
    if getattr(g, "user", None):
        return redirect(dashboard_url_for(g.user))
    return redirect(url_for("auth.login"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Authenticate a user by email and password."""
    if getattr(g, "user", None):
        return redirect(dashboard_url_for(g.user))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Please enter both your email address and password.", "danger")
            return render_template("login.html", email=email), 400

        user = User.query.filter(db.func.lower(User.email) == email).first()
        if user is None or not user.check_password(password):
            flash("Invalid email or password. Please try again.", "danger")
            return render_template("login.html", email=email), 401

        if not user.is_active:
            flash("This account has been deactivated. Please contact the administrator.", "danger")
            return render_template("login.html", email=email), 403

        # Fresh session for every login (prevents session fixation).
        session.clear()
        session["user_id"] = user.id

        flash(f"Welcome back, {user.name.split()[0]}!", "success")
        return redirect(_safe_next(request.args.get("next")) or dashboard_url_for(user))

    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Self-registration for normal employees (role 'user')."""
    if getattr(g, "user", None):
        return redirect(dashboard_url_for(g.user))

    form = {}

    if request.method == "POST":
        form = {
            "name": request.form.get("name", "").strip(),
            "email": request.form.get("email", "").strip().lower(),
            "department": request.form.get("department", "").strip(),
            "phone": request.form.get("phone", "").strip(),
        }
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        errors = []
        if len(form["name"]) < 3:
            errors.append("Please enter your full name (at least 3 characters).")
        if not EMAIL_PATTERN.match(form["email"]):
            errors.append("Please enter a valid email address.")
        if len(password) < MIN_PASSWORD_LENGTH:
            errors.append(f"Password must be at least {MIN_PASSWORD_LENGTH} characters long.")
        if password != confirm:
            errors.append("The two passwords do not match.")
        if User.query.filter(db.func.lower(User.email) == form["email"]).first():
            errors.append("An account with this email address already exists.")

        if errors:
            for message in errors:
                flash(message, "danger")
            return render_template("register.html", form=form), 400

        user = User(
            name=form["name"],
            email=form["email"],
            department=form["department"],
            phone=form["phone"],
            role="user",
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("Account created successfully. You can now log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html", form=form)


@auth_bp.route("/logout")
def logout():
    """End the session and return to the login page."""
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("auth.login"))
