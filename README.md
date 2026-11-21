# Smart IT Help Desk Management System

A full-stack web application for reporting, assigning and resolving IT support
issues inside an organisation. Employees raise tickets, IT support staff work on
them, and the administrator monitors everything from a live dashboard.

Built with **Python 3 + Flask + Flask-SQLAlchemy + SQLite** on the backend and
**HTML5, CSS3, Vanilla JavaScript, Bootstrap 5 and Chart.js** on the frontend.
The whole application runs locally on a single computer.

---

## Table of Contents

1. [Project Description](#1-project-description)
2. [Problem Statement](#2-problem-statement)
3. [Objectives](#3-objectives)
4. [Technologies Used](#4-technologies-used)
5. [Features](#5-features)
6. [User Roles](#6-user-roles)
7. [Demo Login Credentials](#7-demo-login-credentials)
8. [System Requirements](#8-system-requirements)
9. [Installation (Windows)](#9-installation-windows)
10. [How to Run](#10-how-to-run)
11. [Running the Automated Tests](#11-running-the-automated-tests)
12. [Resetting the Database](#12-resetting-the-database)
13. [Project Folder Structure](#13-project-folder-structure)
14. [Database Description](#14-database-description)
15. [Automated Workflow](#15-automated-workflow)
16. [Security and Validation](#16-security-and-validation)
17. [Application Screenshots](#17-application-screenshots)
18. [Examiner Demonstration Scenario](#18-examiner-demonstration-scenario)
19. [Documentation Folder](#19-documentation-folder)
20. [Troubleshooting](#20-troubleshooting)
21. [Future Enhancements](#21-future-enhancements)

---

## 1. Project Description

The **Smart IT Help Desk Management System** is a web-based application that
manages technical complaints reported by employees or students. A user submits a
ticket describing the problem; the system generates a unique ticket number and
notifies the administrator. The administrator assigns the ticket to an IT support
staff member, who updates the status, adds comments, records resolution notes and
finally marks the ticket as resolved. Everyone involved receives in-app
notifications, and every change is stored in a ticket history table.

## 2. Problem Statement

Most small organisations still collect IT complaints through phone calls, emails,
walk-ins or paper registers. This causes:

* lost or forgotten complaints,
* no record of who is responsible for a problem,
* no way to measure how many issues were resolved or how quickly,
* employees repeatedly asking for status updates.

A centralised help desk solves these problems by giving every complaint a unique
number, an owner and a visible status.

## 3. Objectives

1. Provide a single place for employees to report IT problems.
2. Automatically generate a unique, readable ticket ID for every report.
3. Allow the administrator to assign tickets to support staff and set priorities.
4. Allow support staff to record progress, comments and resolution notes.
5. Keep a complete activity history for every ticket.
6. Show live statistics and charts built from real database records.
7. Notify users about every important change to their tickets.
8. Generate reports and export them as CSV.
9. Enforce role-based access control so each role only sees what it should.

## 4. Technologies Used

| Layer | Technology |
|---|---|
| Frontend structure | HTML5, Jinja2 templates |
| Frontend styling | CSS3 (custom theme), Bootstrap 5 |
| Frontend logic | Vanilla JavaScript |
| Charts | Chart.js 4 |
| Icons | Bootstrap Icons (served locally) |
| Backend language | Python 3.10+ |
| Web framework | Flask 3 |
| ORM | Flask-SQLAlchemy 3 |
| Forms / CSRF | Flask-WTF (CSRFProtect) |
| Password hashing | Werkzeug security |
| Database | SQLite |
| Testing | pytest |
| Editor | Visual Studio Code |

All frontend libraries are stored in `static/vendor/`, so the application
**works completely offline** — no internet connection is needed during the
demonstration.

## 5. Features

**Authentication**
* Register (employees), login (all roles), logout.
* Passwords hashed with Werkzeug (never stored in plain text).
* Session-based login, role-based redirects, protected pages.

**Tickets**
* Create ticket with auto-generated ID (`TKT-1001`, `TKT-1002`, ...).
* Title, description, category, priority, optional attachment, timestamps.
* Categories: Hardware, Software, Network, Printer, Login/Password, Email, Other.
* Priorities: Low, Medium, High, Critical.
* Statuses: Open, Assigned, In Progress, Resolved, Closed.
* Search (ID/title/description), filter (status, priority, category, date range)
  and sort (newest, oldest, priority, status).
* Comment thread on every ticket.
* Full activity history (who changed what and when).
* Resolution notes recorded when a ticket is resolved.

**Knowledge Base & Instant Ticket Deflection (Smart Self-Service)**
* Live solution search: suggestions appear in real-time as users type ticket titles.
* Instant ticket deflection: "This Solved My Problem!" resolves issues on the spot without raising redundant tickets.
* Browse and search library of IT solution guides with upvotes and topic filters.
* Solution authoring: support staff and admins can publish new solution articles.

**SLA (Service Level Agreement) Management & Live Countdown**
* Automated resolution deadlines per priority: Critical (4h), High (8h), Medium (24h), Low (48h).
* Dynamic color-coded SLA badges: On-Track (Green), Warning (Amber), Breached (Red), Met (Teal).
* Real-time ticking countdown timer on active ticket pages.
* Administrator dashboard escalation banner for breached tickets.

**Dashboards (all statistics read from the database)**
* Admin: 8 statistic cards + 4 Chart.js charts (status doughnut, priority bar,
  category pie, monthly line) + recent tickets table.
* Employee: personal ticket counters, status overview, recent tickets,
  notifications.
* Support staff: assigned workload, pending/in-progress/resolved counters,
  assigned ticket table, recent updates timeline.

**Administration**
* View all accounts, add support staff accounts, activate/deactivate accounts.
* Manage categories (add, edit, delete when unused).
* Assign tickets, change priority, change status, delete test tickets.
* Reports page with date filters, per-staff workload and CSV export.

**Notifications**
* Bell icon with unread count and latest five notifications.
* Notifications page with "mark as read" and "mark all as read".
* Created on: ticket creation (admin), assignment (staff + employee),
  status change (employee), resolution (employee), new comments (participants).

## 6. User Roles

### A. Employee (`user`)
Register, log in, view personal dashboard, create tickets, view own tickets and
their status, see the assigned staff member, read/post comments, view history,
receive notifications, update profile and password.

### B. IT Support Staff (`support`)
Log in, view only the tickets assigned to them, open ticket details, change
status to In Progress / Resolved / Closed, add comments, write resolution notes,
mark tickets resolved, view previously resolved tickets and their workload.

Support staff accounts are created by the administrator — there is no public
registration for this role.

### C. Administrator (`admin`)
Everything above plus: view all tickets and users, add support staff, assign
tickets, change priority and status of any ticket, manage categories, delete
inappropriate/test tickets, view reports and system statistics, deactivate
accounts, export CSV.

## 7. Demo Login Credentials

These accounts are created automatically the first time the application starts
(only if they do not already exist):

| Role | Email | Password |
|---|---|---|
| Administrator | `admin@helpdesk.com` | `Admin@123` |
| IT Support Staff | `support@helpdesk.com` | `Support@123` |
| Employee (User) | `user@helpdesk.com` | `User@123` |

Additional sample accounts (all use the password `Demo@123`):

| Role | Name | Email |
|---|---|---|
| Employee | Ayesha Khan | `ayesha@helpdesk.com` |
| Employee | Daniel Reed | `daniel@helpdesk.com` |
| Employee | Priya Sharma | `priya@helpdesk.com` |
| Support | Maria Lopez | `maria@helpdesk.com` |
| Support | David Chen | `david@helpdesk.com` |

> ⚠️ **These are demonstration credentials for academic evaluation only.**
> Change or delete them before using the system in a real organisation.

### Sample demonstration data

On the first start (when the tickets table is empty) the application also loads
`seed_data.py`, which creates a realistic six-month service history:

* **24 tickets** — 3 Open, 3 Assigned, 3 In Progress, 11 Resolved, 4 Closed,
  spread over the last six months so every chart has data.
* **21 comments** and **82 activity-history entries** on those tickets.
* **4 unread notifications** for the demo administrator, support staff and employee.
* Resolution notes and resolved dates on every resolved/closed ticket.

This data loads only once. To start from a completely empty help desk, set
`SEED_SAMPLE_DATA = False` in `config.py`, delete `instance/helpdesk.db` and
restart the server.

## 8. System Requirements

* Windows 10 / 11 (also works on macOS and Linux)
* Python 3.10 or newer — check with `python --version`
* pip (installed with Python)
* Visual Studio Code (recommended editor)
* Any modern browser (Chrome, Edge, Firefox)

## 9. Installation (Windows)

Open **Command Prompt** or the **VS Code terminal** in the project folder
(the folder that contains `app.py`) and run the commands one by one.

### Step 1 — Create a virtual environment

```bat
python -m venv venv
```

### Step 2 — Activate the virtual environment

```bat
venv\Scripts\activate
```

You should now see `(venv)` at the start of the command prompt.

> PowerShell users, if activation is blocked by an execution policy error, run:
> `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` and try again.

### Step 3 — Install the dependencies

```bat
pip install -r requirements.txt
```

## 10. How to Run

```bat
python app.py
```

Then open your browser and go to:

```
http://127.0.0.1:5000/
```

The SQLite database (`instance/helpdesk.db`), the default categories and the
three demo accounts are created automatically on the first start. No separate
"init database" command is required.

Stop the server with `Ctrl + C`.

## 11. Running the Automated Tests

The tests use their own temporary SQLite database, so your demo data is never
modified.

```bat
python -m pytest -v
```

Expected result: **15 passed**. The suite covers registration, login, invalid
login, ticket creation, assignment, status updates, resolution, unauthorized
access, dashboard statistics, CSV export and comments.

## 12. Resetting the Database

To start from a clean database during preparation:

1. Stop the server (`Ctrl + C`).
2. Delete the file `instance/helpdesk.db`.
3. Run `python app.py` again.

The database, categories, demo accounts and the 24-ticket sample dataset are
recreated automatically. Any tickets you created during practice will be gone,
which is usually what you want before a fresh demonstration.

## 13. Project Folder Structure

```
smart_it_helpdesk/
│
├── app.py                     # application factory, routes registration, demo data
├── config.py                  # configuration (database path, uploads, limits, sample-data flag)
├── seed_data.py               # sample users, 24 tickets, comments, history, notifications
├── extensions.py              # SQLAlchemy + CSRF instances
├── models.py                  # User, Category, Ticket, Comment, Notification, TicketHistory
├── utils.py                   # helpers: login_required, notifications, ticket numbers, uploads
├── requirements.txt           # Python dependencies
├── pytest.ini                 # test configuration
├── README.md
├── .gitignore
│
├── routes/
│   ├── __init__.py
│   ├── auth.py                # login / register / logout
│   ├── user.py                # employee dashboard + profile
│   ├── support.py             # support staff dashboard
│   ├── tickets.py             # ticket creation, list, details, workflow actions
│   ├── admin.py               # admin dashboard, users, categories, reports, CSV
│   └── notifications.py       # notification list and read actions
│
├── templates/
│   ├── base.html              # sidebar + topbar layout for all pages
│   ├── login.html
│   ├── register.html
│   ├── admin_dashboard.html
│   ├── user_dashboard.html
│   ├── support_dashboard.html
│   ├── create_ticket.html
│   ├── ticket_list.html
│   ├── ticket_details.html
│   ├── manage_users.html
│   ├── categories.html
│   ├── reports.html
│   ├── notifications.html
│   ├── profile.html
│   ├── 403.html
│   └── 404.html
│
├── static/
│   ├── css/style.css          # navy / white / light blue theme
│   ├── js/main.js             # validation, confirm dialogs, sidebar, alerts
│   ├── uploads/               # uploaded ticket attachments
│   └── vendor/                # Bootstrap, Bootstrap Icons, Chart.js (offline copies)
│
├── tests/
│   └── test_app.py            # 15 automated tests
│
├── docs/
│   ├── CAPSTONE_DOCUMENTATION.md
│   ├── PRESENTATION_OUTLINE.md
│   ├── VIVA_QUESTIONS.md
│   ├── DEMO_SCRIPT.md
│   └── screenshots/           # add your own screenshots here
│
└── instance/
    └── helpdesk.db            # created automatically on first run
```

## 14. Database Description

SQLite database with six tables and foreign-key relationships:

### `users`
| Column | Type | Notes |
|---|---|---|
| id | Integer | Primary key |
| name | String(100) | Full name |
| email | String(120) | Unique, used to log in |
| password_hash | String(255) | Werkzeug hash |
| role | String(20) | `user`, `support` or `admin` |
| department | String(100) | Optional |
| phone | String(30) | Optional |
| is_active | Boolean | Deactivated accounts cannot log in |
| created_at | DateTime | Registration time |

### `categories`
`id`, `name` (unique), `description`.

### `tickets`
`id`, `ticket_number` (unique, e.g. `TKT-1001`), `title`, `description`,
`category_id` → categories.id, `priority`, `status`, `created_by` → users.id,
`assigned_to` → users.id (nullable), `attachment`, `resolution_notes`,
`created_at`, `updated_at`, `resolved_at`.

### `comments`
`id`, `ticket_id` → tickets.id, `user_id` → users.id, `comment_text`, `created_at`.

### `notifications`
`id`, `user_id` → users.id, `message`, `link`, `is_read`, `created_at`.

### `ticket_history`
`id`, `ticket_id` → tickets.id, `changed_by` → users.id, `old_status`,
`new_status`, `activity_description`, `created_at`.

Relationships:

* A user creates many tickets (`created_by`) and can be assigned many tickets
  (`assigned_to`).
* A ticket belongs to one category, one creator and optionally one assignee.
* A ticket has many comments and many history entries (both deleted with it).
* A user has many notifications.

## 15. Automated Workflow

| Trigger | Automated behaviour |
|---|---|
| Employee submits a ticket | Unique `TKT-xxxx` ID, status set to **Open**, timestamp recorded, history entry, notification to every admin and a confirmation to the employee |
| Admin assigns a ticket | Assignee saved, status becomes **Assigned**, history entry, notification to the staff member and to the employee |
| Support starts work | Status becomes **In Progress**, `updated_at` saved, employee notified, history entry |
| Support resolves a ticket | Resolution notes required, status becomes **Resolved**, `resolved_at` recorded, employee notified, history entry |
| Any dashboard refresh | All cards, tables and charts are recalculated from the database with live queries |

Everything above is implemented in `routes/tickets.py` with real database writes —
no simulated or hard-coded data.

## 16. Security and Validation

* Passwords hashed with `werkzeug.security.generate_password_hash`.
* Session authentication; protected routes use the `@login_required(...)` decorator.
* Role-based authorization on every admin/support route (wrong role → HTTP 403).
* Employees can only open their own tickets; support staff only their assigned
  tickets (checked in `utils.get_ticket_or_403`).
* Support staff cannot change ticket priority (admin-only route).
* CSRF protection on every POST form (Flask-WTF `CSRFProtect` + `csrf_token()`).
* Server-side validation for registration, login, profile, tickets, assignment,
  status changes, categories and staff accounts.
* Client-side validation with Bootstrap's `needs-validation` classes.
* SQLAlchemy parameterised queries (no string-built SQL).
* Uploads: extension allow-list, 5 MB limit, `secure_filename`, random prefix.
  Attachments are served through an authenticated route, not the static folder.
* `SECRET_KEY` can be supplied through an environment variable.
* Password hashes are never sent to templates or API responses.
* Deactivated accounts are logged out immediately.

## 17. Application Screenshots

Add your own screenshots to `docs/screenshots/` before submitting the report.
Suggested set:

| File | Screen |
|---|---|
| `01-login.png` | Login page with demo credentials |
| `02-register.png` | Employee registration |
| `03-admin-dashboard.png` | Admin dashboard with 4 charts |
| `04-user-dashboard.png` | Employee dashboard |
| `05-support-dashboard.png` | Support staff dashboard |
| `06-create-ticket.png` | Ticket submission form |
| `07-ticket-list.png` | Ticket table with filters |
| `08-ticket-details.png` | Ticket detail, comments and history |
| `09-reports.png` | Reports and CSV export |
| `10-manage-users.png` | User management |

To capture a screenshot: press `Win + Shift + S` (Windows Snipping Tool), select
the browser area, and save the image with the names above. Then reference them in
your report like this:

```markdown
![Admin dashboard](docs/screenshots/03-admin-dashboard.png)
```

## 18. Examiner Demonstration Scenario

Full script: [`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md). Short version:

1. Log in as `user@helpdesk.com` / `User@123`.
2. Create a ticket: *Computer Not Starting*, Hardware Issue, High priority.
3. Point out the newly generated ID (the next free number, e.g. `TKT-1025`)
   in the success message.
4. Log out, log in as admin. The ticket appears on the dashboard and in All Tickets.
5. Assign it to Sam Support; status becomes **Assigned**.
6. Log out, log in as `support@helpdesk.com`.
7. Open the ticket, set status **In Progress**, add a comment.
8. Set status **Resolved**, enter resolution notes, save.
9. Log back in as the employee: status, resolution notes and notification are visible.
10. Log in as admin: dashboard counters, charts and reports now include the ticket;
    download the CSV export.

## 19. Documentation Folder

| File | Content |
|---|---|
| `docs/CAPSTONE_DOCUMENTATION.md` | Full academic report: abstract, introduction, existing vs proposed system, requirements, architecture, use case, DFD, ER diagram, database design, modules, testing, results, advantages, limitations, future scope, conclusion |
| `docs/PRESENTATION_OUTLINE.md` | 12-slide presentation outline with speaker notes |
| `docs/VIVA_QUESTIONS.md` | 25 examiner questions with simple answers |
| `docs/DEMO_SCRIPT.md` | 3–5 minute demonstration script |
| `seed_data.py` | Generates the sample demonstration dataset on first start |

## 20. Troubleshooting

| Problem | Solution |
|---|---|
| `'python' is not recognized` | Install Python from python.org and tick "Add Python to PATH" |
| `venv\Scripts\activate` blocked | Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` |
| `ModuleNotFoundError: flask` | The virtual environment is not active, or dependencies are not installed: `venv\Scripts\activate` then `pip install -r requirements.txt` |
| Port 5000 already in use | Stop the other program, or change the port in `app.py` (`app.run(..., port=5001)`) |
| Styles or icons missing | Make sure `static/vendor/` was not deleted; it contains local copies of Bootstrap, icons and Chart.js |
| Forgot password for a demo account | Delete `instance/helpdesk.db` and restart to recreate the demo accounts |
| Dashboards show no tickets | The sample dataset loads only when the tickets table is empty: delete `instance/helpdesk.db` and restart |

## 21. Future Enhancements

* Email or SMS notifications when a ticket changes.
* SLA timers and automatic escalation for overdue tickets.
* File preview and multiple attachments per ticket.
* Pagination for very large ticket tables.
* Knowledge base of common solutions.
* Asset/inventory management (which device belongs to whom).
* Two-factor authentication and password reset by email.
* PDF report export and scheduled reports.
* REST API for a future mobile app.
