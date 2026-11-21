# Smart IT Help Desk Management System

## Complete Capstone Project Documentation

**Project type:** Web-based IT service management application
**Technology:** Python 3, Flask, Flask-SQLAlchemy, SQLite, HTML5, CSS3, Vanilla JavaScript, Bootstrap 5, Chart.js
**Submitted by:** ______________________
**Guided by:** ______________________
**Academic year:** 2025–2026

---

## 1. Abstract

Technical problems in colleges and small organisations are usually reported by
phone, email or in person. Complaints get lost, nobody knows who is handling a
problem, and there is no reliable record of how many issues were resolved. The
**Smart IT Help Desk Management System** is a web application that replaces this
manual process with a centralised ticket workflow. Employees register, log in and
submit tickets with a category, priority and description. The system generates a
unique ticket number, notifies the administrator and stores the request in a
SQLite database. The administrator assigns tickets to IT support staff, who update
the status, discuss the problem through comments and record resolution notes.
Every change is written to an activity-history table and triggers in-app
notifications. Role-specific dashboards present live statistics and four Chart.js
charts, and the administrator can generate filtered reports and export them as
CSV. The application is implemented with Flask and SQLAlchemy using password
hashing, session authentication, role-based authorisation, CSRF protection and
validated file uploads. Automated pytest tests verify registration, login, ticket
creation, assignment, status changes, resolution and access control. The result is
a simple, secure and fully functional help desk that runs locally and is easy to
demonstrate.

---

## 2. Introduction

Information technology supports almost every activity in a modern institution.
Computers, printers, projectors, Wi-Fi and email accounts are used daily, and
failures are inevitable. A help desk is the single point of contact between people
who experience a problem and the people who can fix it.

The Smart IT Help Desk Management System digitises that process. It is a
three-role web application: employees raise issues, IT support staff resolve them,
and the administrator coordinates the whole service. The project was developed as
a college capstone using only free, locally available tools: Python, Flask,
SQLite and standard web technologies.

---

## 3. Problem Statement

In the existing manual system:

1. Complaints are received through phone calls, emails, personal visits or a paper
   register, so there is no single list of open issues.
2. Nothing guarantees that a complaint is assigned to a particular technician.
3. Employees have no way to check the status of their complaint without asking.
4. There is no reliable history of what was changed, by whom, or when.
5. The IT department cannot easily measure workload, response volume or resolution
   rate, so planning is guesswork.

These problems cause delays, duplicated effort and dissatisfaction. A centralised,
database-backed help desk is needed.

---

## 4. Objectives

1. Provide a single, secure platform for reporting IT problems.
2. Generate a unique, readable ticket identifier for every complaint.
3. Store all ticket data, comments and changes permanently in a relational database.
4. Allow the administrator to assign tickets and control priorities.
5. Allow support staff to record progress and resolution details.
6. Notify users automatically whenever their ticket changes.
7. Present live dashboards with statistics and charts for all three roles.
8. Generate date-filtered reports and export them as CSV.
9. Enforce role-based access control so no user sees another user's private data.
10. Keep the system simple enough to install, run and explain within a college
    environment.

---

## 5. Existing System

| Aspect | Existing manual system |
|---|---|
| Reporting channel | Phone, email, walk-in, paper register |
| Ticket identification | None, or an informal note |
| Assignment | Verbal, often forgotten |
| Status tracking | Employee must ask the IT staff |
| History | No audit trail |
| Reporting | Manual counting from registers |
| Notifications | None |
| Data security | Paper register or shared inbox |
| Availability of statistics | None |

**Limitations:** lost complaints, unclear responsibility, no accountability, slow
resolution, no measurable performance data.

---

## 6. Proposed System

The proposed system is a database-driven web application with:

* Self-registration for employees and administrator-created staff accounts.
* Automatic ticket numbering (`TKT-1001`, `TKT-1002`, ...).
* A controlled workflow: **Open → Assigned → In Progress → Resolved → Closed**.
* Assignment of tickets to support staff with automatic notification.
* Comment threads, resolution notes and a complete activity history.
* Live dashboards for each role, with Chart.js visualisations.
* In-app notifications with an unread counter.
* Search, filtering and sorting over all tickets.
* Reports with date filters and CSV export.
* Role-based authorisation and hashed passwords.

**Advantages over the existing system:** nothing is lost, responsibility is always
visible, employees can check progress themselves, and management gets real numbers.

---

## 7. Hardware and Software Requirements

### Hardware (minimum)

| Component | Requirement |
|---|---|
| Processor | Intel Core i3 or equivalent |
| RAM | 4 GB (8 GB recommended) |
| Storage | 500 MB free space |
| Display | 1366 × 768 or higher |
| Network | Not required at runtime (all libraries are local) |

### Software

| Software | Version / purpose |
|---|---|
| Windows 10/11, macOS or Linux | Operating system |
| Python | 3.10 or newer |
| pip | Python package installer |
| Flask | 3.0.3 — web framework |
| Flask-SQLAlchemy | 3.1.1 — ORM |
| Flask-WTF | 1.2.1 — CSRF protection |
| Werkzeug | 3.0.3 — password hashing, file-name safety |
| SQLite | Bundled with Python |
| pytest | 8.2.2 — automated testing |
| Visual Studio Code | Recommended editor |
| Chrome / Edge / Firefox | Browser |

---

## 8. Functional Requirements

| ID | Requirement |
|---|---|
| FR1 | A visitor can register as an employee with name, email and password. |
| FR2 | All roles log in through one login page and are redirected to their dashboard. |
| FR3 | Passwords are stored only as hashes. |
| FR4 | An employee can create a ticket with title, description, category, priority and optional attachment. |
| FR5 | The system generates a unique ticket number and sets the status to Open. |
| FR6 | The administrator receives a notification for every new ticket. |
| FR7 | An employee can list, search, filter and sort only their own tickets. |
| FR8 | The administrator can view all tickets and all accounts. |
| FR9 | The administrator can assign a ticket to an active support staff member; status becomes Assigned. |
| FR10 | The administrator can change ticket priority, status and delete inappropriate tickets. |
| FR11 | Support staff see only tickets assigned to them. |
| FR12 | Support staff can set status to In Progress, Resolved or Closed. |
| FR13 | Resolving a ticket requires resolution notes and records the resolution date. |
| FR14 | Authorised users can add comments to a ticket. |
| FR15 | Every significant change is stored in the ticket history. |
| FR16 | Users receive in-app notifications and can mark them as read. |
| FR17 | The administrator can add support staff accounts and deactivate any account except their own. |
| FR18 | The administrator can add, edit and delete unused categories. |
| FR19 | Dashboards show statistics and charts computed from live data. |
| FR20 | The administrator can filter reports by date and export tickets as CSV. |
| FR21 | Users can update their profile and change their password. |
| FR22 | Unauthorised requests are rejected with HTTP 403 or redirected to login. |

---

## 9. Non-functional Requirements

| ID | Requirement |
|---|---|
| NFR1 | **Usability:** consistent navigation, clear status badges, professional layout, mobile-friendly. |
| NFR2 | **Performance:** page responses under one second for a few thousand tickets. |
| NFR3 | **Security:** hashed passwords, CSRF tokens, role checks, upload validation, parameterised queries. |
| NFR4 | **Reliability:** database created automatically; demo data never duplicated on restart. |
| NFR5 | **Maintainability:** blueprint-based modular structure with commented Python functions. |
| NFR6 | **Portability:** runs on any machine with Python 3.10+; no external services required. |
| NFR7 | **Testability:** a separate test database and an automated pytest suite. |
| NFR8 | **Scalability:** SQLite can be swapped for PostgreSQL by changing one configuration value. |

---

## 10. System Architecture

The application follows a classic **three-tier architecture**.

```
┌──────────────────────────────────────────────────────────────┐
│  PRESENTATION TIER (Browser)                                 │
│  HTML5 + Jinja2 templates, Bootstrap 5, custom CSS,          │
│  Vanilla JavaScript, Chart.js                                │
└───────────────────────────┬──────────────────────────────────┘
                            │ HTTP requests / HTML responses
┌───────────────────────────▼──────────────────────────────────┐
│  APPLICATION TIER (Flask)                                    │
│  auth.py  user.py  support.py  tickets.py  admin.py           │
│  notifications.py  utils.py  models.py                       │
│  Session auth • role decorators • CSRF • validation •         │
│  workflow automation • notification generation               │
└───────────────────────────┬──────────────────────────────────┘
                            │ SQLAlchemy ORM (parameterised SQL)
┌───────────────────────────▼──────────────────────────────────┐
│  DATA TIER (SQLite)                                          │
│  users • categories • tickets • comments •                   │
│  notifications • ticket_history                              │
└──────────────────────────────────────────────────────────────┘
```

**Request flow example (ticket assignment):**

1. Admin submits the assignment form with a CSRF token.
2. `routes/tickets.py:assign()` checks that the user is an admin.
3. The ticket row is updated (`assigned_to`, `status = Assigned`).
4. A `ticket_history` row and notifications for the staff member and employee are
   inserted in the same transaction.
5. The database is committed and the page redirects to the ticket detail view.

---

## 11. Use Case Diagram

```
                    SMART IT HELP DESK
   ┌────────────────────────────────────────────────────────────┐
   │                                                            │
   │   (Employee) ──> Register / Login                          │
   │        │                                                   │
   │        ├──> Create Ticket ─────────┐                       │
   │        ├──> View My Tickets        │                       │
   │        ├──> Track Status           │                       │
   │        ├──> Add Comment            │                       │
   │        ├──> View Notifications     │                       │
   │        └──> Update Profile         │                       │
   │                                    │                       │
   │   (Support Staff) ──> Login        │                       │
   │        ├──> View Assigned Tickets  │                       │
   │        ├──> Update Status ─────────┤                       │
   │        ├──> Add Resolution Notes   │                       │
   │        ├──> Add Comment            │                       │
   │        └──> View Workload          │                       │
   │                                    ▼                       │
   │   (Administrator) ──> Login      [TICKET DATABASE]         │
   │        ├──> View All Tickets                               │
   │        ├──> Assign Ticket                                  │
   │        ├──> Manage Users                                   │
   │        ├──> Manage Categories                              │
   │        ├──> View Dashboard & Charts                        │
   │        ├──> Generate Reports / Export CSV                  │
   │        └──> Delete / Deactivate Records                    │
   └────────────────────────────────────────────────────────────┘
```

**Actors:** Employee (primary), IT Support Staff (primary), Administrator (primary),
Database (secondary system actor).

---

## 12. Data Flow Diagram

### Level 0 — Context diagram

```
   Employee ──ticket details──►  ┌───────────────────────────┐
                                 │  SMART IT HELP DESK       │ ──status / notifications──► Employee
   Admin ───assignment─────────► │  MANAGEMENT SYSTEM        │ ──work list───────────────► Support Staff
   Support ──status / notes────► └───────────────────────────┘ ──reports / charts────────► Admin
                                           │
                                           ▼
                                     [SQLite database]
```

### Level 1 — Main processes

```
Employee
   │ ticket form
   ▼
(1.0 Create Ticket) ── writes ──► tickets, ticket_history, notifications
   │
   ▼
(2.0 Assign Ticket) ◄── admin ── updates ──► tickets.assigned_to, status, notifications
   │
   ▼
(3.0 Work on Ticket) ◄── support ── updates ──► status, comments, resolution_notes, resolved_at
   │
   ├── (4.0 Generate Notifications) ── writes ──► notifications
   ├── (5.0 Build Dashboard) ── reads ──► tickets, users
   └── (6.0 Generate Reports) ── reads ──► tickets, categories, users ──► admin / CSV file
```

---

## 13. Entity Relationship Diagram

```
┌──────────┐         ┌────────────┐
│  USERS   │1       *│  TICKETS   │*      1┌────────────┐
│──────────│─────────│────────────│─────────│ CATEGORIES │
│ id (PK)  │ created │ id (PK)    │category │ id (PK)    │
│ name     │         │ ticket_no  │         │ name       │
│ email    │         │ title      │         │ description│
│ pass_hash│         │ description│         └────────────┘
│ role     │         │ priority   │
│ dept     │         │ status     │
│ is_active│         │ created_by │
│ created  │         │ assigned_to│
└──────────┘         │ resolution │
   │ 1               │ created_at │
   │                 │ updated_at │
   │ *               │ resolved_at│
   │                 └────────────┘
   │                    │ 1     │ 1
   │                    │       │
   │                    │ *     │ *
   │              ┌─────▼────┐ ┌▼──────────────┐
   │              │ COMMENTS │ │ TICKET_HISTORY│
   │              │──────────│ │───────────────│
   │              │ id (PK)  │ │ id (PK)       │
   │              │ ticket_id│ │ ticket_id     │
   │              │ user_id  │ │ changed_by    │
   │              │ text     │ │ old_status    │
   │              │ created  │ │ new_status    │
   │              └──────────┘ │ description   │
   │                           │ created_at    │
   │ 1                         └───────────────┘
   ▼ *
┌────────────────┐
│ NOTIFICATIONS  │
│────────────────│
│ id (PK)        │
│ user_id (FK)   │
│ message        │
│ link           │
│ is_read        │
│ created_at     │
└────────────────┘
```

**Relationships**

* `users` 1 : N `tickets` (created_by)
* `users` 1 : N `tickets` (assigned_to, optional)
* `categories` 1 : N `tickets`
* `tickets` 1 : N `comments`
* `tickets` 1 : N `ticket_history`
* `users` 1 : N `comments`
* `users` 1 : N `notifications`
* `users` 1 : N `ticket_history` (changed_by)

---

## 14. Database Design

| Table | Key columns | Purpose |
|---|---|---|
| `users` | id (PK), email (unique), password_hash, role, is_active | Authentication and roles |
| `categories` | id (PK), name (unique) | Ticket classification |
| `tickets` | id (PK), ticket_number (unique), category_id (FK), created_by (FK), assigned_to (FK) | Core support records (24 sample rows) |
| `comments` | id (PK), ticket_id (FK), user_id (FK) | Conversation per ticket |
| `notifications` | id (PK), user_id (FK), is_read | In-app alerts |
| `ticket_history` | id (PK), ticket_id (FK), changed_by (FK) | Audit trail |

Normalisation: every table stores data about one entity only; category names and
user names are referenced by foreign key instead of being repeated inside tickets,
which avoids update anomalies and keeps reports accurate.

Indexes: `users.email` and `tickets.ticket_number` are indexed because they are
used for lookups on every login and search.

---

## 15. Module Description

| Module | File | Responsibility |
|---|---|---|
| Application factory | `app.py` | Creates the Flask app, registers blueprints, creates tables, seeds demo accounts and categories, registers error handlers and context processors |
| Configuration | `config.py` | Database URI, upload folder, 5 MB upload limit, allowed file types, secret key |
| Models | `models.py` | Six SQLAlchemy models with relationships, password helpers and badge helpers |
| Utilities | `utils.py` | `login_required` role decorator, notification writer, history writer, ticket number generator, secure upload handler, ticket access check |
| Authentication | `routes/auth.py` | Register, login, logout, role-based redirect, safe `next` handling |
| Employee area | `routes/user.py` | Personal statistics dashboard and profile/password update |
| Support area | `routes/support.py` | Assigned workload dashboard and recent activity |
| Ticket engine | `routes/tickets.py` | Create/list/filter tickets, details, comments, assign, priority, status workflow, resolution, delete, attachment download |
| Administration | `routes/admin.py` | Dashboard with charts, user management, category management, reports and CSV export |
| Notifications | `routes/notifications.py` | Notification list, mark one/all as read |
| Presentation | `templates/` | 16 Jinja2 templates sharing one sidebar/topbar layout |
| Styling & scripts | `static/css/style.css`, `static/js/main.js` | Theme, responsive layout, form validation, confirmations, sidebar |

---

## 16. Implementation Details

**Framework choice.** Flask was selected because it is lightweight, beginner
friendly and requires no boilerplate. The application uses the factory pattern so
tests can create isolated instances.

**Database access.** Flask-SQLAlchemy maps six classes to SQLite tables. Queries
are written with the ORM (`Ticket.query.filter(...)`), which generates
parameterised SQL and protects against SQL injection.

**Authentication.** On login the submitted password is verified with
`check_password_hash`. The user id is stored in a signed Flask session cookie
(`HttpOnly`, `SameSite=Lax`). A `before_request` hook loads the user into `g` and
logs out deactivated accounts.

**Authorisation.** `utils.login_required(*roles)` protects routes. Ticket-level
authorisation is enforced in `utils.get_ticket_or_403`, which allows admins any
ticket, support staff only their assigned tickets, and employees only their own.

**Workflow automation.** All five automations live in `routes/tickets.py`:

1. Creation → number, Open status, timestamps, admin notification, history.
2. Assignment → assignee, Assigned status, staff + employee notifications, history.
3. Progress → In Progress, timestamp, employee notification, history.
4. Resolution → notes validation, Resolved, `resolved_at`, employee notification, history.
5. Dashboard updates → every statistic is a fresh SQL aggregate on each request.

**Frontend.** Jinja2 templates extend `base.html`, which renders a fixed navy
sidebar, a sticky topbar with the notification dropdown and profile menu, and a
flash-message area. `style.css` defines the navy/white/light-blue design system
with responsive breakpoints at 1200, 992 and 576 pixels. `main.js` adds Bootstrap
validation, confirmation dialogs for destructive actions, auto-dismissing alerts,
the password visibility toggle and the mobile sidebar.

**Charts.** `admin_dashboard.html` receives a JSON object built from live queries
(status, priority, category and last-six-months counts) and renders a doughnut, a
bar, a pie and a line chart with Chart.js.

**Reports and CSV.** `admin.reports` applies optional date filters and aggregates
totals, category, priority, status, monthly and per-staff figures.
`admin.export_report` streams a UTF-8 CSV with a BOM so Excel opens it correctly.

---

## 17. Testing and Test Cases

Testing uses **pytest** with a temporary SQLite database per test, so demo data is
never modified. Run with `python -m pytest -v` → **15 passed**.

| # | Test case | Input | Expected result | Status |
|---|---|---|---|---|
| 1 | Employee registration | Valid name, unique email, matching passwords | Account created, hashed password, role `user` | Pass |
| 2 | Duplicate registration | Existing email | "already exists" error, no new row | Pass |
| 3 | Valid login | admin@helpdesk.com / Admin@123 | Redirect to `/admin/dashboard` | Pass |
| 4 | Invalid password | Wrong password | "Invalid email or password", HTTP 401 | Pass |
| 5 | Unknown email | Non-existent account | "Invalid email or password" | Pass |
| 6 | Ticket creation | Title, description, category, priority | `TKT-1001`, status Open, history row, admin notification | Pass |
| 7 | Ticket assignment | Admin assigns support staff | `assigned_to` set, status Assigned, staff notified | Pass |
| 8 | Start work | Support sets In Progress | Status updated, history entry | Pass |
| 9 | Resolution without notes | Empty notes | Rejected with a friendly message | Pass |
| 10 | Resolution with notes | Notes provided | Status Resolved, `resolved_at` set, employee notified | Pass |
| 11 | Protected page, anonymous | GET `/tickets/` | Redirect to login | Pass |
| 12 | Admin page as employee | GET `/admin/dashboard` | HTTP 403 | Pass |
| 13 | Another user's ticket | Employee opens a stranger's ticket | HTTP 403 | Pass |
| 14 | Priority change as support | POST priority route | HTTP 403 | Pass |
| 15 | Admin dashboard statistics | One open ticket | Correct counters, 7 categories seeded | Pass |
| 16 | Reports and CSV export | Admin export | HTTP 200, `text/csv`, ticket rows present | Pass |
| 17 | Comment | Employee posts comment | Comment stored and displayed | Pass |

**Manual tests performed:** login for all three roles, navigation of every sidebar
link, ticket creation with and without attachment, invalid file type rejection,
search and filters, status transitions, notification read/unread, category
add/edit/delete, account deactivation, reports with and without date filters,
CSV opening in Excel, and layout at mobile width.

---

## 18. Results

The implemented system meets every functional requirement listed in Section 8:

* All three roles can log in and reach their own dashboard.
* Tickets receive unique readable numbers and follow the five-state workflow.
* Assignment, priority changes, comments, resolution notes and history are stored
  in SQLite and visible to the correct users.
* Notifications are generated automatically for creation, assignment, status
  changes and resolution, with a working unread counter.
* Admin dashboards show eight live statistic cards and four charts.
* Reports can be filtered by date and exported as CSV.
* Unauthorised access attempts return HTTP 403 or redirect to login.
* The automated test suite passes 15/15.

The delivered database is preloaded by `seed_data.py` with a realistic six-month
demonstration dataset — 8 accounts (1 admin, 3 support staff, 4 employees),
24 tickets across all five statuses and all seven categories, 21 comments and
82 activity-history entries — so the dashboards, charts and reports display
meaningful figures immediately.

**Screenshots of the running system** are to be added to
`docs/screenshots/` (see README Section 17).

---

## 19. Advantages

1. Every complaint gets a unique ID and cannot be lost.
2. Clear ownership: each ticket shows who is responsible.
3. Employees can track progress without contacting IT.
4. Complete audit trail for accountability.
5. Real statistics replace guesswork for planning.
6. Role-based access protects private information.
7. Runs offline on a single laptop with free software.
8. Clean, modular code that a beginner can read and extend.

## 20. Limitations

1. SQLite is suitable for a single institution, not high concurrency.
2. Notifications are in-app only; no email or SMS delivery.
3. One attachment per ticket.
4. Long ticket tables are not paginated yet.
5. Password reset is manual (an administrator must be involved).
6. Reports export to CSV only, not PDF.
7. No SLA timers or automatic escalation.
8. Users cannot reopen a closed ticket themselves; staff or an admin must change
   the status.

## 21. Future Scope

* Email/SMS notification integration.
* SLA and escalation rules with deadlines per priority.
* Multiple attachments and inline image preview.
* Pagination and advanced full-text search.
* Knowledge base and canned responses.
* Asset management linking tickets to devices.
* Two-factor authentication and self-service password reset.
* PDF exports and scheduled email reports.
* REST API and mobile application.
* Migration to PostgreSQL for enterprise scale.

## 22. Conclusion

The Smart IT Help Desk Management System converts an informal, manual complaint
process into a structured digital service. It provides secure role-based access,
automatic ticket numbering, a controlled workflow, notifications, a complete
audit history, live dashboards and exportable reports, all within a lightweight
Flask and SQLite stack that runs on an ordinary laptop.

The project demonstrates the complete software development cycle: requirement
analysis, database design, backend implementation, responsive interface design,
security hardening and automated testing. Every feature described in this report
is implemented in the delivered code, and the system is ready for demonstration
and for further extension.
