# Live Demonstration Script — 3 to 5 Minutes

**Before you start**

* Run `python app.py` and open `http://127.0.0.1:5000/`.
* Log out so the login page is showing.
* The database already contains 24 sample tickets over six months, so the
dashboard and charts look like a system in real use from the first second.
* Have this file and `docs/VIVA_QUESTIONS.md` open on a second screen if possible.
* Speak slowly and narrate what you are clicking.

---

## 0:00 — Introduction (20 seconds)

> "This is the Smart IT Help Desk Management System. It has three roles — employee,
> IT support staff and administrator — and everything you will see is stored in a
> real SQLite database. I will now show the complete life cycle of one support
> ticket."

---

## 0:20 — Employee creates a ticket (60 seconds)

1. Point at the demo credentials box.
2. Log in as **user@helpdesk.com / User@123**.
3. Say: *"This is my employee dashboard with my own ticket history and
   notifications."*
4. Click **New Ticket**.
5. Fill in:
   * Title: **Computer Not Starting**
   * Category: **Hardware Issue**
   * Priority: **High**
   * Description: **My computer is not starting after pressing the power button.**
6. Click **Submit Ticket**.
7. Point at the green message: *"The system generated the next unique ticket ID
   automatically — the number continues from TKT-1024 — set the status to Open,
   recorded the time, and notified the administrator."*
8. Point at the ticket page: description, priority badge, status badge, history
   entry, and the notification bell count.

---

## 1:20 — Administrator assigns the ticket (60 seconds)

1. Click the profile menu → **Logout**.
2. Log in as **admin@helpdesk.com / Admin@123**.
3. Say: *"The admin dashboard is built from live database queries — eight cards and
   four charts."* Point at the charts and the open-ticket counter.
4. Point at the ticket you just created at the top of the recent tickets table,
   then open it.
5. In **Assign Ticket**, choose **Sam Support** and click **Save assignment**.
6. Point out: status changed to **Assigned**, and the history now shows who assigned
   it and when.
7. Optionally change the priority in the **Priority** panel to demonstrate that only
   an admin can do this.

---

## 2:20 — Support staff resolves the ticket (80 seconds)

1. Log out and log in as **support@helpdesk.com / Support@123**.
2. Say: *"Support staff only see tickets assigned to them."* Point at the assigned
   ticket table and the workload counters.
3. Open the newly assigned ticket.
4. In **Update Status**, choose **In Progress** and click **Save status**.
5. Scroll to **Comments**, type:
   *"Checked the power cable and PSU. Replacing the faulty power cable and testing."*
   and click **Post comment**.
6. In **Update Status**, choose **Resolved**, type resolution notes:
   *"Replaced the faulty power cable. The computer now starts normally and was
   tested for 15 minutes."* Click **Save status**.
7. Point at the resolution panel and the full **Ticket History** timeline.

---

## 3:40 — Employee sees the update (30 seconds)

1. Log out and log in as **user@helpdesk.com / User@123**.
2. Point at the dashboard counters: In Progress / Resolved have increased.
3. Open the ticket again: status is **Resolved**, the resolution notes and the
   support staff comments are visible.
4. Open **Notifications**: show the messages about assignment, status change and
   resolution, and click **Mark all as read**.

---

## 4:10 — Admin reporting (30 seconds)

1. Log out and log in as **admin@helpdesk.com / Admin@123**.
2. Point at the dashboard: the resolved counter and the status doughnut include
   the ticket you just resolved, and the High column of the priority bar grew.
3. Open **Reports**: show total, resolved, pending, resolution rate, category table,
   per-staff workload and monthly statistics.
4. Click **Export CSV** and point out the downloaded file.

---

## 4:40 — Closing statement (20 seconds)

> "That is the complete workflow: an employee reports a problem, the administrator
> assigns it, support staff resolve it with notes, the employee is notified, and
> management gets live statistics and an exportable report. Every step was saved in
> the database and recorded in the ticket history. Thank you."

---

## Backup actions if something goes wrong

| Situation | Recovery |
|---|---|
| Wrong password / locked out | Use the correct demo credentials; passwords are case-sensitive |
| Ticket page shows 403 | You are logged in as a role that cannot see that ticket — log in as admin |
| Demo data looks messy | Stop the server, delete `instance/helpdesk.db`, start again |
| Charts do not appear | Confirm `static/vendor/chart.umd.min.js` exists and refresh the page |
| Browser shows an old page | Press `Ctrl + F5` |

## Questions the panel may ask during the demo

* "Where is this stored?" → SQLite, `instance/helpdesk.db`, six tables.
* "What if two tickets are created at once?" → ticket numbers are checked for
  uniqueness before saving.
* "Can support staff assign tickets?" → No, that route is admin-only and returns 403.
* "Can an employee see another employee's ticket?" → No, the access check blocks it.
