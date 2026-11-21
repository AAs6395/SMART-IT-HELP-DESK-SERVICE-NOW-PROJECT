"""
tests/test_app.py
-----------------
Automated tests for the Smart IT Help Desk Management System.

Run from the project root with:
    python -m pytest -v

The tests use their own SQLite file (instance/test_helpdesk.db) which is
deleted before and after every run, so the demo database is never touched.
"""

import os
import shutil
import sys
import tempfile

import pytest

# Make sure the project root is importable when pytest is started from anywhere.
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import create_app  # noqa: E402
from extensions import db  # noqa: E402
from models import (  # noqa: E402
    Category,
    Comment,
    KnowledgeArticle,
    Notification,
    Ticket,
    TicketHistory,
    User,
)

@pytest.fixture()
def app():
    """
    Create a fresh application and database for each test.

    Every test gets its own temporary SQLite file, so the demo database in
    instance/helpdesk.db is never touched (and Windows file locks cannot
    interfere with the next test).
    """
    temp_dir = tempfile.mkdtemp(prefix="helpdesk_test_")
    db_path = os.path.join(temp_dir, "test_helpdesk.db").replace("\\", "/")

    application = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///" + db_path,
            # CSRF is disabled only in tests; the real app always enforces it.
            "WTF_CSRF_ENABLED": False,
            # Tests start from an empty ticket table (no sample dataset).
            "SEED_SAMPLE_DATA": False,
            "UPLOAD_FOLDER": os.path.join(temp_dir, "uploads"),
        }
    )

    yield application

    with application.app_context():
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture()
def client(app):
    return app.test_client()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def login(client, email, password):
    return client.post(
        "/login",
        data={"email": email, "password": password},
        follow_redirects=True,
    )


def logout(client):
    return client.get("/logout", follow_redirects=True)


def first_category_id(app):
    with app.app_context():
        return Category.query.order_by(Category.id).first().id


def create_ticket(client, app, title="Computer Not Starting", priority="High"):
    return client.post(
        "/tickets/new",
        data={
            "title": title,
            "description": "My computer is not starting after pressing the power button.",
            "category_id": first_category_id(app),
            "priority": priority,
        },
        follow_redirects=True,
    )


# ---------------------------------------------------------------------------
# 1. Registration
# ---------------------------------------------------------------------------
def test_user_registration(client, app):
    response = client.post(
        "/register",
        data={
            "name": "New Employee",
            "email": "new.employee@helpdesk.com",
            "department": "Library",
            "phone": "03001234567",
            "password": "Secret123",
            "confirm_password": "Secret123",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Account created successfully" in response.data

    with app.app_context():
        user = User.query.filter_by(email="new.employee@helpdesk.com").first()
        assert user is not None
        assert user.role == "user"
        # Password must be hashed, never stored in plain text.
        assert user.password_hash != "Secret123"
        assert user.check_password("Secret123")


def test_registration_rejects_duplicate_email(client):
    response = client.post(
        "/register",
        data={
            "name": "Duplicate User",
            "email": "user@helpdesk.com",
            "password": "Secret123",
            "confirm_password": "Secret123",
        },
        follow_redirects=True,
    )
    assert b"already exists" in response.data


# ---------------------------------------------------------------------------
# 2 & 3. Login
# ---------------------------------------------------------------------------
def test_login_success_redirects_to_role_dashboard(client):
    response = client.post(
        "/login",
        data={"email": "admin@helpdesk.com", "password": "Admin@123"},
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert "/admin/dashboard" in response.headers["Location"]


@pytest.mark.parametrize(
    "email,password",
    [
        ("admin@helpdesk.com", "wrong-password"),
        ("doesnotexist@helpdesk.com", "Admin@123"),
    ],
)
def test_invalid_login_is_rejected(client, email, password):
    response = login(client, email, password)
    assert b"Invalid email or password" in response.data


# ---------------------------------------------------------------------------
# 4. Ticket creation
# ---------------------------------------------------------------------------
def test_ticket_creation(client, app):
    login(client, "user@helpdesk.com", "User@123")
    response = create_ticket(client, app)
    assert b"created successfully" in response.data

    with app.app_context():
        ticket = Ticket.query.first()
        assert ticket is not None
        assert ticket.ticket_number.startswith("TKT-")
        assert ticket.status == "Open"
        assert ticket.priority == "High"
        assert ticket.assigned_to is None
        assert ticket.created_at is not None

        # Automation: the admin is notified and history is recorded.
        admin = User.query.filter_by(role="admin").first()
        assert Notification.query.filter_by(user_id=admin.id).count() >= 1
        assert TicketHistory.query.filter_by(ticket_id=ticket.id).count() == 1


# ---------------------------------------------------------------------------
# 5. Ticket assignment (admin)
# ---------------------------------------------------------------------------
def test_admin_can_assign_ticket(client, app):
    login(client, "user@helpdesk.com", "User@123")
    create_ticket(client, app)
    logout(client)

    login(client, "admin@helpdesk.com", "Admin@123")
    with app.app_context():
        ticket = Ticket.query.first()
        ticket_id = ticket.id
        staff = User.query.filter_by(role="support").first()
        staff_id = staff.id

    response = client.post(
        f"/tickets/{ticket_id}/assign",
        data={"assigned_to": staff_id},
        follow_redirects=True,
    )
    assert b"Ticket assigned to" in response.data

    with app.app_context():
        ticket = db.session.get(Ticket, ticket_id)
        assert ticket.assigned_to == staff_id
        assert ticket.status == "Assigned"

        # Automation: the assigned staff member is notified.
        assert Notification.query.filter_by(user_id=staff_id).count() >= 1


# ---------------------------------------------------------------------------
# 6 & 8. Status update and resolution (support staff)
# ---------------------------------------------------------------------------
def test_support_can_start_and_resolve_ticket(client, app):
    # Prepare: create the ticket and assign it.
    login(client, "user@helpdesk.com", "User@123")
    create_ticket(client, app)
    logout(client)

    with app.app_context():
        ticket_id = Ticket.query.first().id
        staff_id = User.query.filter_by(role="support").first().id

    login(client, "admin@helpdesk.com", "Admin@123")
    client.post(f"/tickets/{ticket_id}/assign", data={"assigned_to": staff_id})
    logout(client)

    # Support staff starts working.
    login(client, "support@helpdesk.com", "Support@123")
    response = client.post(
        f"/tickets/{ticket_id}/status",
        data={"new_status": "In Progress"},
        follow_redirects=True,
    )
    assert b"updated to In Progress" in response.data

    with app.app_context():
        assert db.session.get(Ticket, ticket_id).status == "In Progress"

    # Resolution requires notes.
    response = client.post(
        f"/tickets/{ticket_id}/status",
        data={"new_status": "Resolved", "resolution_notes": ""},
        follow_redirects=True,
    )
    assert b"resolution notes" in response.data.lower()

    response = client.post(
        f"/tickets/{ticket_id}/status",
        data={
            "new_status": "Resolved",
            "resolution_notes": "Replaced the faulty power supply unit and tested the PC.",
        },
        follow_redirects=True,
    )
    assert b"updated to Resolved" in response.data

    with app.app_context():
        ticket = db.session.get(Ticket, ticket_id)
        assert ticket.status == "Resolved"
        assert ticket.resolved_at is not None
        assert "power supply" in ticket.resolution_notes

        # History contains the status changes.
        statuses = [h.new_status for h in ticket.history]
        assert "In Progress" in statuses
        assert "Resolved" in statuses

        # The employee was notified about the resolution.
        employee = User.query.filter_by(role="user").first()
        messages = [n.message for n in Notification.query.filter_by(user_id=employee.id)]
        assert any("Resolved" in message for message in messages)


# ---------------------------------------------------------------------------
# 7. Unauthorized access prevention
# ---------------------------------------------------------------------------
def test_protected_pages_require_login(client):
    response = client.get("/tickets/")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]

    response = client.get("/admin/dashboard")
    assert response.status_code == 302


def test_user_cannot_open_admin_dashboard(client):
    login(client, "user@helpdesk.com", "User@123")
    response = client.get("/admin/dashboard")
    assert response.status_code == 403


def test_user_cannot_open_another_users_ticket(client, app):
    login(client, "user@helpdesk.com", "User@123")
    create_ticket(client, app)
    logout(client)

    # Create a second employee directly in the database.
    with app.app_context():
        other = User(name="Other Employee", email="other@helpdesk.com", role="user")
        other.set_password("Other@123")
        db.session.add(other)
        db.session.commit()

    login(client, "other@helpdesk.com", "Other@123")
    with app.app_context():
        ticket_id = Ticket.query.first().id
    response = client.get(f"/tickets/{ticket_id}")
    assert response.status_code == 403


def test_support_cannot_change_priority(client, app):
    login(client, "user@helpdesk.com", "User@123")
    create_ticket(client, app)
    logout(client)

    with app.app_context():
        ticket_id = Ticket.query.first().id
        staff_id = User.query.filter_by(role="support").first().id

    login(client, "admin@helpdesk.com", "Admin@123")
    client.post(f"/tickets/{ticket_id}/assign", data={"assigned_to": staff_id})
    logout(client)

    login(client, "support@helpdesk.com", "Support@123")
    response = client.post(f"/tickets/{ticket_id}/priority", data={"priority": "Critical"})
    assert response.status_code == 403


# ---------------------------------------------------------------------------
# 9. Admin dashboard statistics come from the database
# ---------------------------------------------------------------------------
def test_admin_dashboard_statistics(client, app):
    login(client, "user@helpdesk.com", "User@123")
    create_ticket(client, app, title="Printer not printing")
    logout(client)

    login(client, "admin@helpdesk.com", "Admin@123")
    response = client.get("/admin/dashboard")
    assert response.status_code == 200
    assert b"Total Tickets" in response.data

    with app.app_context():
        assert Ticket.query.count() == 1
        assert Ticket.query.filter_by(status="Open").count() == 1
        assert Category.query.count() == 7


def test_reports_and_csv_export(client, app):
    login(client, "user@helpdesk.com", "User@123")
    create_ticket(client, app, title="Email not syncing")
    logout(client)

    login(client, "admin@helpdesk.com", "Admin@123")
    assert client.get("/admin/reports").status_code == 200

    response = client.get("/admin/reports/export")
    assert response.status_code == 200
    assert response.mimetype == "text/csv"
    assert b"Ticket ID" in response.data
    assert b"Email not syncing" in response.data


# ---------------------------------------------------------------------------
# Extra: comments
# ---------------------------------------------------------------------------
def test_comment_can_be_added(client, app):
    login(client, "user@helpdesk.com", "User@123")
    create_ticket(client, app)

    with app.app_context():
        ticket_id = Ticket.query.first().id

    response = client.post(
        f"/tickets/{ticket_id}/comment",
        data={"comment_text": "The monitor is also blinking, adding that detail."},
        follow_redirects=True,
    )
    assert b"Comment added" in response.data

    with app.app_context():
        comment = Comment.query.first()
        assert comment is not None
        assert "monitor" in comment.comment_text


# ---------------------------------------------------------------------------
# Extra: Knowledge Base & Deflection
# ---------------------------------------------------------------------------
def test_knowledge_base_and_deflection(client, app):
    login(client, "user@helpdesk.com", "User@123")

    # Knowledge Base index page loads
    res = client.get("/kb/")
    assert res.status_code == 200
    assert b"Knowledge Base" in res.data

    # Deflection API suggestion search
    res = client.get("/kb/suggest?q=wifi")
    assert res.status_code == 200
    data = res.get_json()
    assert data["count"] >= 1
    assert any("Wi-Fi" in art["title"] or "wifi" in art["title"].lower() for art in data["articles"])

    with app.app_context():
        article = KnowledgeArticle.query.first()
        old_helpful = article.helpful_count

    # Mark helpful
    res = client.post(f"/kb/{article.id}/helpful", headers={"X-Requested-With": "XMLHttpRequest"})
    assert res.status_code == 200
    assert res.get_json()["helpful_count"] == old_helpful + 1


# ---------------------------------------------------------------------------
# Extra: SLA calculations
# ---------------------------------------------------------------------------
def test_sla_targets_and_deadlines(client, app):
    login(client, "user@helpdesk.com", "User@123")
    create_ticket(client, app, title="Critical Server Down", priority="Critical")

    with app.app_context():
        ticket = Ticket.query.filter_by(title="Critical Server Down").first()
        assert ticket is not None
        assert ticket.sla_hours == 4
        sla = ticket.sla_status
        assert "4h" in sla["label"] or "left" in sla["label"] or sla["is_breached"] is not None

