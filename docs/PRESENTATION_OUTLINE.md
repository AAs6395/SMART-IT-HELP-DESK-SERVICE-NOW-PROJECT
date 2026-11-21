# Presentation Outline — Smart IT Help Desk Management System

**Target duration:** 10 minutes presentation + 5 minutes demonstration.
**Total slides:** 12.

---

## Slide 1 — Title

* **Title:** Smart IT Help Desk Management System
* **Subtitle:** A web-based ticket management solution for college IT support
* Student name, roll number, department, guide name, academic year.
* One line: "Python Flask · SQLite · HTML/CSS/JavaScript"

**Speaker note:** Greet the panel, state your name and the project title, and say
in one sentence what the system does.

---

## Slide 2 — Problem Statement

* Complaints arrive by phone, email, walk-in or paper register.
* Complaints get lost and responsibility is unclear.
* Employees cannot check the status of their own issue.
* No history and no measurable statistics for the IT department.
* Bullet question: *"How many complaints were resolved last month, and by whom?"*

---

## Slide 3 — Objectives

1. Centralise IT complaint reporting.
2. Auto-generate unique ticket IDs.
3. Assign tickets to support staff with priorities.
4. Track status through a defined workflow.
5. Notify users about every change.
6. Provide live dashboards, charts and CSV reports.
7. Enforce role-based security.

---

## Slide 4 — Existing vs Proposed System

| Manual system | Proposed system |
|---|---|
| Phone / register | Web ticket form |
| No ID | Auto `TKT-1001` numbering |
| Verbal assignment | Admin assignment with notification |
| "Any update?" | Live status tracking |
| No record | Full activity history |
| Manual counting | Live charts and CSV reports |

---

## Slide 5 — Technology Stack

* **Backend:** Python 3, Flask 3, Flask-SQLAlchemy, Flask-WTF
* **Frontend:** HTML5, CSS3, Vanilla JavaScript, Bootstrap 5, Chart.js
* **Database:** SQLite
* **Security:** Werkzeug password hashing, Flask sessions, CSRF tokens
* **Testing:** pytest
* **Tools:** VS Code, browser, localhost

**Speaker note:** Emphasise that no paid service or internet connection is needed —
all libraries are bundled in `static/vendor/`.

---

## Slide 6 — System Architecture

Three-tier diagram:

```
Browser (HTML/CSS/JS/Chart.js)
        ↓ HTTP
Flask application (routes + models + automation)
        ↓ SQLAlchemy
SQLite database (6 tables)
```

* Mention blueprints: auth, user, support, tickets, admin, notifications.
* Mention who talks to what: role decorator → route → ORM → database.

---

## Slide 7 — Database Design

* Six tables: **users, categories, tickets, comments, notifications, ticket_history**.
* Relationship highlights:
  * User 1:N Ticket (creator)
  * User 1:N Ticket (assignee)
  * Category 1:N Ticket
  * Ticket 1:N Comments / History
  * User 1:N Notifications
* Show the ER diagram from the documentation.

---

## Slide 8 — User Roles and Features

**Employee:** register, create ticket, track status, comment, notifications, profile.

**Support Staff:** view only assigned tickets, set In Progress, comment, resolve with notes, workload view.

**Administrator:** all tickets, assign, priority, status, users, categories, reports, CSV, delete test records.

**Speaker note:** Point out that support accounts are created by the admin only.

---

## Slide 9 — Ticket Workflow

```
Open ──assign──► Assigned ──start──► In Progress ──resolve──► Resolved ──close──► Closed
```

* Each transition writes a history row.
* Each transition notifies the right people.
* Resolution requires notes and records a resolution timestamp.

---

## Slide 10 — Dashboards and Reports

* **Admin:** 8 statistic cards + 4 Chart.js charts (status doughnut, priority bar,
  category pie, monthly line) + recent tickets.
* **Employee:** submitted / open / in-progress / resolved counters, recent list,
  status bars, notifications.
* **Support:** assigned / pending / in-progress / resolved counters, workload bars,
  recent updates.
* **Reports:** date filters, per-staff workload, CSV export.

---

## Slide 11 — Security and Testing

**Security**

* Werkzeug password hashing.
* Session authentication + role-based authorisation (HTTP 403).
* CSRF protection on all POST forms.
* Employees cannot open other employees' tickets.
* Upload allow-list, 5 MB cap, secure filenames.
* SQLAlchemy parameterised queries.

**Testing**

* 15 pytest cases: registration, login, invalid login, ticket creation,
  assignment, status update, resolution, unauthorised access, dashboard
  statistics, CSV export, comments.
* Result: **15 passed**.

---

## Slide 12 — Conclusion and Future Scope

**Achievements**

* Complete working help desk with three roles and a real database.
* Automated workflow, notifications and full audit history.
* Professional, responsive interface that runs offline.

**Future scope**

* Email/SMS notifications, SLA timers, multiple attachments, pagination,
  knowledge base, PDF reports, REST API for a mobile app.

**Closing line:** "Thank you — I would be happy to demonstrate the complete
ticket lifecycle live."

---

### Presentation tips

* Keep slides text-light; show screenshots on slides 8–10 if the projector allows.
* Rehearse the demo separately using `docs/DEMO_SCRIPT.md`.
* Have the application already running and logged out before you start.
* Keep `docs/CAPSTONE_DOCUMENTATION.md` open for detailed questions.
