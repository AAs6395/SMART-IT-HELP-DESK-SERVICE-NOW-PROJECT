# Viva Questions and Answers — Smart IT Help Desk Management System

25 likely external-examiner questions with short, accurate answers based on the
implemented code.

---

**1. What is the main purpose of your project?**
It is a web-based IT help desk. Employees report technical problems as tickets, IT
support staff work on the tickets assigned to them, and the administrator
coordinates assignments, monitors progress and generates reports.

**2. Which technologies did you use and why?**
Python and Flask for the backend because Flask is lightweight and easy to learn;
Flask-SQLAlchemy as the ORM; SQLite as a zero-configuration database; and HTML,
CSS, vanilla JavaScript with Bootstrap 5 and Chart.js for the interface. All are
free and run locally.

**3. Why did you choose SQLite instead of MySQL?**
SQLite needs no server installation and stores the whole database in one file,
which makes the project easy to run on any college computer. The ORM means the
database could be changed to MySQL or PostgreSQL by editing one configuration
value.

**4. Explain the architecture of your application.**
It is a three-tier architecture: the presentation tier is the browser with Jinja2
templates, Bootstrap and Chart.js; the application tier is Flask with blueprints,
authentication, workflow logic and notifications; the data tier is SQLite accessed
through SQLAlchemy.

**5. What are the three user roles and what can each do?**
Employee: register, create and track own tickets, comment, view notifications and
update profile. Support staff: view only assigned tickets, change status, comment,
add resolution notes. Administrator: everything, plus user management, category
management, assignment, priority and status control, reports and CSV export.

**6. How are passwords stored?**
Never in plain text. `werkzeug.security.generate_password_hash` creates a salted
hash, and `check_password_hash` verifies a login. The hash column is never sent to
a template.

**7. How does login and session management work?**
The user submits email and password; the password is verified against the hash. On
success the user id is stored in Flask's signed session cookie. A `before_request`
hook loads the user into `g` on every request. Logout clears the session.

**8. How do you prevent a user from opening someone else's ticket?**
`utils.get_ticket_or_403` checks the role: admins can open any ticket, support staff
only tickets assigned to them, and employees only tickets they created. Otherwise
the request is aborted with HTTP 403.

**9. How do you stop an employee from opening admin pages?**
Routes are protected with the `@login_required("admin")` decorator, which returns
HTTP 403 when the role does not match. The sidebar also hides admin links, but the
server-side check is what actually enforces it.

**10. What is CSRF and how did you protect against it?**
Cross-Site Request Forgery tricks a logged-in user's browser into submitting a
forged request. Flask-WTF's `CSRFProtect` rejects any POST without a valid token,
and every form includes `{{ csrf_token() }}` as a hidden field.

**11. How is a ticket ID generated?**
`utils.next_ticket_number()` reads the highest existing number and adds one,
producing IDs like `TKT-1001`. A uniqueness check protects against gaps caused by
deleted tickets.

**12. Explain the ticket workflow.**
Open → Assigned → In Progress → Resolved → Closed. Creating a ticket sets Open.
Assignment sets Assigned. Support staff can move it to In Progress, Resolved or
Closed. Admins can set any status. Every change writes a history row and a
notification.

**13. What happens when a ticket is resolved?**
The status is set to Resolved, `resolved_at` records the time, resolution notes
are stored (they are mandatory), a history entry is added and the employee gets a
notification.

**14. How does the notification system work?**
Notifications are rows in the `notifications` table tied to a user. A context
processor counts unread notifications for the bell icon on every page. Users can
open the notifications page and mark one or all as read.

**15. Where are the dashboard statistics coming from?**
Live SQL aggregate queries on every page load — for example
`Ticket.query.filter_by(status="Open").count()`. Nothing is hard-coded, so the
numbers always match the database.

**16. Which charts did you implement?**
Four Chart.js charts on the admin dashboard: doughnut for status, bar for priority,
pie for category, and a line chart for tickets created per month over the last six
months.

**17. How is the database created?**
`app.py` calls `db.create_all()` inside the application context on startup, so the
tables are created automatically. It then seeds the seven categories and the three
demo accounts only if they do not already exist.

**18. What is a foreign key? Give an example from your project.**
A foreign key links a row to a row in another table and protects data consistency.
Example: `tickets.created_by` references `users.id`, so a ticket cannot exist
without a valid creator.

**19. How did you implement file uploads securely?**
`utils.save_attachment` validates the extension against an allow-list, the app
enforces a 5 MB limit (`MAX_CONTENT_LENGTH`), `secure_filename` strips dangerous
characters, a random prefix prevents overwrites, and downloads are served through
an authenticated route rather than the public static folder.

**20. How did you test the application?**
With pytest. Fifteen automated tests use a temporary SQLite database and cover
registration, login, invalid login, ticket creation, assignment, status updates,
resolution, unauthorised access, dashboard statistics, CSV export and comments.
Manual testing covered every page and all three roles.

**21. Why is CSRF disabled in the tests?**
The test client posts forms programmatically and has no browser to fetch a token,
so `WTF_CSRF_ENABLED` is turned off only in the test configuration. The real
application always enforces CSRF protection.

**22. What are the limitations of your project?**
SQLite is meant for small-scale use; notifications are in-app only, with no email;
one attachment per ticket; no pagination; no SLA timers; reports export to CSV only;
password reset is manual.

**23. How would you scale this for a whole university?**
Move to PostgreSQL or MySQL, deploy behind a production WSGI server, add
pagination and caching, add email/SMS notifications, and add SLA rules with
escalation. The modular blueprint structure means each of these can be added
without rewriting the application.

**24. What was the most challenging part and how did you solve it?**
Implementing role-based ticket visibility and keeping the workflow consistent.
Every status change is centralised in one route that validates the role, writes the
history row, updates timestamps and creates notifications in a single transaction,
so the rules cannot be bypassed.

**25. What did you learn from this project?**
How to design a normalised relational database, build a Flask application with
blueprints and an application factory, implement secure authentication and
authorisation, connect a database to a responsive front end, and verify the result
with automated tests.

---

### Quick facts to remember

| Question | Answer |
|---|---|
| Backend framework | Flask 3 |
| ORM | Flask-SQLAlchemy 3.1 |
| Database file | `instance/helpdesk.db` |
| Number of tables | 6 |
| Default status for new ticket | Open |
| Ticket ID format | `TKT-1001` |
| Statuses | Open, Assigned, In Progress, Resolved, Closed |
| Priorities | Low, Medium, High, Critical |
| Categories | 7 (seeded automatically) |
| Roles | user, support, admin |
| Password hashing | Werkzeug PBKDF/scrypt hash |
| CSRF library | Flask-WTF |
| Charts library | Chart.js 4 |
| Test command | `python -m pytest -v` |
| Number of automated tests | 15 |
| Port | 5000 |
