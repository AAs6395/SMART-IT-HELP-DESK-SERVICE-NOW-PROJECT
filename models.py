"""
models.py
---------
Database models for the Smart IT Help Desk Management System.

Tables:
    users             -> every person who can log in (user / support / admin)
    categories        -> ticket categories (Hardware, Software, ...)
    tickets           -> the support tickets
    comments          -> conversation on a ticket
    notifications     -> in-app notifications
    ticket_history    -> audit trail of status / assignment changes
"""

from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db

# ---------------------------------------------------------------------------
# Controlled vocabularies used across the whole application
# ---------------------------------------------------------------------------
ROLES = ("user", "support", "admin")

TICKET_STATUSES = ("Open", "Assigned", "In Progress", "Resolved", "Closed")
TICKET_PRIORITIES = ("Low", "Medium", "High", "Critical")

# Service Level Agreement (SLA) target resolution times in hours
SLA_HOURS_MAP = {
    "Critical": 4,   # 4 hours
    "High": 8,       # 8 hours
    "Medium": 24,    # 24 hours (1 day)
    "Low": 48,       # 48 hours (2 days)
}

TICKET_CATEGORIES = (
    "Hardware Issue",
    "Software Issue",
    "Network Problem",
    "Printer Issue",
    "Login and Password Issue",
    "Email Issue",
    "Other Technical Issues",
)


class User(db.Model):
    """A person who can log in. The `role` column decides what they can do."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")
    department = db.Column(db.String(100))
    phone = db.Column(db.String(30))
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    # Relationships
    created_tickets = db.relationship(
        "Ticket",
        foreign_keys="Ticket.created_by",
        back_populates="creator",
        cascade="all, delete-orphan",
    )
    assigned_tickets = db.relationship(
        "Ticket", foreign_keys="Ticket.assigned_to", back_populates="assignee"
    )
    comments = db.relationship("Comment", back_populates="author", cascade="all, delete-orphan")
    notifications = db.relationship(
        "Notification", back_populates="user", cascade="all, delete-orphan"
    )

    # ------------------------------------------------------------------
    # Password helpers - plain passwords are NEVER stored in the database.
    # ------------------------------------------------------------------
    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)

    @property
    def role_label(self):
        return {"admin": "Administrator", "support": "IT Support Staff", "user": "Employee"}.get(
            self.role, self.role.title()
        )

    def __repr__(self):  # helpful while debugging
        return f"<User {self.email} ({self.role})>"


class Category(db.Model):
    """A ticket category, e.g. 'Hardware Issue'."""

    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))

    tickets = db.relationship("Ticket", back_populates="category")

    def __repr__(self):
        return f"<Category {self.name}>"


class Ticket(db.Model):
    """A single IT support ticket."""

    __tablename__ = "tickets"

    id = db.Column(db.Integer, primary_key=True)
    ticket_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    priority = db.Column(db.String(20), nullable=False, default="Medium")
    status = db.Column(db.String(20), nullable=False, default="Open")

    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey("users.id"))

    attachment = db.Column(db.String(255))          # stored file name (optional)
    resolution_notes = db.Column(db.Text)           # filled in when resolved

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    resolved_at = db.Column(db.DateTime)

    # Relationships
    category = db.relationship("Category", back_populates="tickets")
    creator = db.relationship(
        "User", foreign_keys=[created_by], back_populates="created_tickets"
    )
    assignee = db.relationship(
        "User", foreign_keys=[assigned_to], back_populates="assigned_tickets"
    )
    comments = db.relationship(
        "Comment",
        back_populates="ticket",
        cascade="all, delete-orphan",
        order_by="Comment.created_at",
    )
    history = db.relationship(
        "TicketHistory",
        back_populates="ticket",
        cascade="all, delete-orphan",
        order_by="TicketHistory.created_at",
    )

    # ------------------------------------------------------------------
    # Small helpers used by the HTML templates to pick the right colours.
    # ------------------------------------------------------------------
    @property
    def status_class(self):
        return {
            "Open": "badge-open",
            "Assigned": "badge-assigned",
            "In Progress": "badge-progress",
            "Resolved": "badge-resolved",
            "Closed": "badge-closed",
        }.get(self.status, "badge-closed")

    @property
    def priority_class(self):
        return {
            "Low": "prio-low",
            "Medium": "prio-medium",
            "High": "prio-high",
            "Critical": "prio-critical",
        }.get(self.priority, "prio-low")

    @property
    def is_open(self):
        return self.status not in ("Resolved", "Closed")

    # ------------------------------------------------------------------
    # SLA (Service Level Agreement) properties & countdown helpers
    # ------------------------------------------------------------------
    @property
    def sla_hours(self):
        return SLA_HOURS_MAP.get(self.priority, 24)

    @property
    def sla_deadline(self):
        from datetime import timedelta
        base_time = self.created_at or datetime.now()
        return base_time + timedelta(hours=self.sla_hours)

    @property
    def is_sla_breached(self):
        now = datetime.now()
        if self.status in ("Resolved", "Closed"):
            if self.resolved_at:
                return self.resolved_at > self.sla_deadline
            return False
        return now > self.sla_deadline

    @property
    def sla_status(self):
        now = datetime.now()
        deadline = self.sla_deadline

        if self.status in ("Resolved", "Closed"):
            if self.resolved_at:
                if self.resolved_at <= deadline:
                    hours_taken = round((self.resolved_at - (self.created_at or self.resolved_at)).total_seconds() / 3600, 1)
                    return {
                        "state": "met",
                        "badge_class": "badge-sla-met",
                        "label": "SLA Met",
                        "detail": f"Resolved in {hours_taken}h ({self.sla_hours}h SLA target)",
                        "icon": "bi-check2-circle",
                        "seconds_remaining": 0,
                        "deadline_str": deadline.strftime("%d %b %Y, %H:%M"),
                        "is_breached": False,
                    }
                else:
                    overdue = round((self.resolved_at - deadline).total_seconds() / 3600, 1)
                    return {
                        "state": "breached_resolved",
                        "badge_class": "badge-sla-breached",
                        "label": f"Resolved Overdue (+{overdue}h)",
                        "detail": f"Exceeded {self.sla_hours}h SLA target by {overdue}h",
                        "icon": "bi-exclamation-octagon-fill",
                        "seconds_remaining": 0,
                        "deadline_str": deadline.strftime("%d %b %Y, %H:%M"),
                        "is_breached": True,
                    }
            return {
                "state": "met",
                "badge_class": "badge-sla-met",
                "label": "SLA Met",
                "detail": f"Target: {self.sla_hours}h",
                "icon": "bi-check2-circle",
                "seconds_remaining": 0,
                "deadline_str": deadline.strftime("%d %b %Y, %H:%M"),
                "is_breached": False,
            }

        # Ticket is active/unresolved
        if now > deadline:
            overdue_sec = (now - deadline).total_seconds()
            overdue_h = int(overdue_sec // 3600)
            overdue_m = int((overdue_sec % 3600) // 60)
            label = f"SLA Breached (+{overdue_h}h {overdue_m}m)" if overdue_h > 0 else f"SLA Breached (+{overdue_m}m)"
            return {
                "state": "breached",
                "badge_class": "badge-sla-breached",
                "label": label,
                "detail": f"Overdue past target of {self.sla_hours} hours",
                "icon": "bi-fire",
                "seconds_remaining": 0,
                "deadline_str": deadline.strftime("%d %b %Y, %H:%M"),
                "is_breached": True,
            }
        else:
            rem_sec = (deadline - now).total_seconds()
            rem_h = int(rem_sec // 3600)
            rem_m = int((rem_sec % 3600) // 60)
            total_sec = self.sla_hours * 3600
            pct_left = rem_sec / total_sec

            if pct_left < 0.25:
                badge_class = "badge-sla-warning"
                icon = "bi-exclamation-triangle"
            else:
                badge_class = "badge-sla-ontrack"
                icon = "bi-hourglass-split"

            time_str = f"{rem_h}h {rem_m}m left" if rem_h > 0 else f"{rem_m}m left"
            return {
                "state": "active",
                "badge_class": badge_class,
                "label": time_str,
                "detail": f"Target: {self.sla_hours}h resolution deadline",
                "icon": icon,
                "seconds_remaining": int(rem_sec),
                "deadline_str": deadline.strftime("%d %b %Y, %H:%M"),
                "is_breached": False,
            }

    def __repr__(self):
        return f"<Ticket {self.ticket_number} {self.status}>"


class Comment(db.Model):
    """A comment written by the ticket owner, the assigned staff or an admin."""

    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey("tickets.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    comment_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    ticket = db.relationship("Ticket", back_populates="comments")
    author = db.relationship("User", back_populates="comments")

    def __repr__(self):
        return f"<Comment {self.id} on ticket {self.ticket_id}>"


class Notification(db.Model):
    """In-app notification shown in the bell menu and on the notifications page."""

    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    link = db.Column(db.String(255))  # optional URL to open when clicked
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    user = db.relationship("User", back_populates="notifications")

    def __repr__(self):
        return f"<Notification {self.id} user={self.user_id}>"


class TicketHistory(db.Model):
    """Audit trail: every important change made to a ticket."""

    __tablename__ = "ticket_history"

    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey("tickets.id"), nullable=False)
    changed_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    old_status = db.Column(db.String(20))
    new_status = db.Column(db.String(20))
    activity_description = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    ticket = db.relationship("Ticket", back_populates="history")
    user = db.relationship("User")

    def __repr__(self):
        return f"<TicketHistory {self.id} ticket={self.ticket_id}>"


class KnowledgeArticle(db.Model):
    """A self-service knowledge base solution article used for ticket deflection."""

    __tablename__ = "knowledge_articles"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    keywords = db.Column(db.String(255), default="")  # search tags / tokens
    solution = db.Column(db.Text, nullable=False)
    views = db.Column(db.Integer, nullable=False, default=0)
    helpful_count = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    category = db.relationship("Category")

    def __repr__(self):
        return f"<KnowledgeArticle {self.id} '{self.title}'>"

