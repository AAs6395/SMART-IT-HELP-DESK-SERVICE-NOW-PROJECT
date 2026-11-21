"""
routes/support.py
-----------------
Dashboard for IT support staff. They only ever see tickets assigned to them.
"""

from flask import Blueprint, g, render_template

from models import Ticket, TicketHistory
from utils import login_required

support_bp = Blueprint("support", __name__, url_prefix="/support")


@support_bp.route("/dashboard")
@login_required("support", "admin")
def dashboard():
    """Support dashboard: workload, assigned tickets and recent activity."""
    base = Ticket.query.filter_by(assigned_to=g.user.id)

    stats = {
        "total": base.count(),
        "pending": base.filter(Ticket.status.in_(["Assigned", "Open"])).count(),
        "in_progress": base.filter(Ticket.status == "In Progress").count(),
        "resolved": base.filter(Ticket.status.in_(["Resolved", "Closed"])).count(),
    }

    assigned_tickets = (
        base.order_by(Ticket.priority.desc(), Ticket.created_at.desc()).limit(10).all()
    )

    # Recent activity on this staff member's tickets.
    recent_updates = (
        TicketHistory.query.join(Ticket, TicketHistory.ticket_id == Ticket.id)
        .filter(Ticket.assigned_to == g.user.id)
        .order_by(TicketHistory.created_at.desc())
        .limit(8)
        .all()
    )

    return render_template(
        "support_dashboard.html",
        stats=stats,
        assigned_tickets=assigned_tickets,
        recent_updates=recent_updates,
    )
