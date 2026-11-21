"""
seed_data.py
------------
Creates a realistic demonstration dataset so the application looks like a
system that has been in use for a few months.

It is only run when the database contains no tickets, so restarting the
application never duplicates data. To regenerate the sample data:

    1. Stop the server.
    2. Delete instance/helpdesk.db
    3. Start the server again (python app.py).

All sample accounts use the password: Demo@123
"""

from datetime import datetime, timedelta

from extensions import db
from models import Category, Comment, KnowledgeArticle, Notification, Ticket, TicketHistory, User
from utils import next_ticket_number

# ---------------------------------------------------------------------------
# Extra demonstration accounts (created on top of the three main demo users)
# ---------------------------------------------------------------------------
SAMPLE_PASSWORD = "Demo@123"

SAMPLE_USERS = [
    {"name": "Ayesha Khan", "email": "ayesha@helpdesk.com", "department": "Accounts", "role": "user"},
    {"name": "Daniel Reed", "email": "daniel@helpdesk.com", "department": "Maintenance", "role": "user"},
    {"name": "Priya Sharma", "email": "priya@helpdesk.com", "department": "Library", "role": "user"},
    {"name": "Maria Lopez", "email": "maria@helpdesk.com", "department": "IT Support", "role": "support"},
    {"name": "David Chen", "email": "david@helpdesk.com", "department": "IT Support", "role": "support"},
]

# ---------------------------------------------------------------------------
# Tickets: (title, category, priority, status, days_ago, creator, assignee,
#           resolution notes, comments)
# comments are (author_email, text, hours_after_creation)
# ---------------------------------------------------------------------------
SAMPLE_TICKETS = [
    {
        "title": "Computer not starting in Computer Lab 2",
        "category": "Hardware Issue",
        "priority": "High",
        "status": "Resolved",
        "days_ago": 152,
        "creator": "user@helpdesk.com",
        "assignee": "support@helpdesk.com",
        "description": "PC number 12 in Computer Lab 2 does not power on. The power button light blinks but nothing appears on the screen.",
        "resolution": "Replaced the faulty power supply unit. The PC boots normally and was tested for 20 minutes.",
        "comments": [
            ("support@helpdesk.com", "Checked the power cable and PSU. The PSU is faulty, arranging a replacement.", 5),
            ("user@helpdesk.com", "Thank you, the computer is working now.", 27),
        ],
    },
    {
        "title": "Projector in Seminar Hall not displaying",
        "category": "Hardware Issue",
        "priority": "Medium",
        "status": "Closed",
        "days_ago": 145,
        "creator": "priya@helpdesk.com",
        "assignee": "maria@helpdesk.com",
        "description": "The projector turns on but shows 'No Signal' when the laptop is connected through the HDMI cable.",
        "resolution": "Replaced the damaged HDMI cable and configured the correct input source. Projector tested with two laptops.",
        "comments": [
            ("maria@helpdesk.com", "The HDMI cable was damaged at the connector. Replacement requested.", 3),
        ],
    },
    {
        "title": "Wi-Fi disconnects every 10 minutes",
        "category": "Network Problem",
        "priority": "High",
        "status": "Resolved",
        "days_ago": 131,
        "creator": "ayesha@helpdesk.com",
        "assignee": "david@helpdesk.com",
        "description": "My laptop keeps disconnecting from the office Wi-Fi every 10 minutes. Other colleagues in the same room do not have this problem.",
        "resolution": "Updated the wireless network adapter driver and removed the old saved network profile. Connection is stable now.",
        "comments": [
            ("david@helpdesk.com", "Please try connecting to the IT-Test network while I check the access point logs.", 2),
            ("ayesha@helpdesk.com", "Connected to IT-Test, no disconnections so far.", 6),
        ],
    },
    {
        "title": "Cannot log in to the student portal",
        "category": "Login and Password Issue",
        "priority": "Critical",
        "status": "Resolved",
        "days_ago": 120,
        "creator": "priya@helpdesk.com",
        "assignee": "support@helpdesk.com",
        "description": "The portal says 'account locked' after three attempts. I need access today to upload examination results.",
        "resolution": "Unlocked the account and reset the password. The user successfully logged in and uploaded the results.",
        "comments": [
            ("support@helpdesk.com", "Account unlocked, temporary password sent to your official email.", 1),
        ],
    },
    {
        "title": "Printer on 2nd floor shows paper jam",
        "category": "Printer Issue",
        "priority": "Medium",
        "status": "Assigned",
        "days_ago": 112,
        "creator": "daniel@helpdesk.com",
        "assignee": "maria@helpdesk.com",
        "description": "The shared printer on the second floor displays a paper jam error even after the tray has been cleared and reloaded.",
        "resolution": "",
        "comments": [
            ("daniel@helpdesk.com", "There is a torn piece of paper visible near the rear roller.", 4),
        ],
    },
    {
        "title": "Microsoft Office activation error",
        "category": "Software Issue",
        "priority": "High",
        "status": "Open",
        "days_ago": 104,
        "creator": "ayesha@helpdesk.com",
        "assignee": None,
        "description": "Office shows 'Product activation failed' and Word opens in read-only mode. This started after the last Windows update.",
        "resolution": "",
        "comments": [],
    },
    {
        "title": "Outlook not receiving new emails",
        "category": "Email Issue",
        "priority": "High",
        "status": "Resolved",
        "days_ago": 96,
        "creator": "user@helpdesk.com",
        "assignee": "david@helpdesk.com",
        "description": "I can send emails but nothing new arrives in my inbox since yesterday morning. Webmail works fine.",
        "resolution": "The Outlook profile was corrupted. Recreated the mail profile and re-synced the mailbox.",
        "comments": [
            ("david@helpdesk.com", "Please use webmail for today while I rebuild the Outlook profile.", 3),
        ],
    },
    {
        "title": "Laptop battery drains very quickly",
        "category": "Hardware Issue",
        "priority": "Low",
        "status": "Closed",
        "days_ago": 88,
        "creator": "priya@helpdesk.com",
        "assignee": "support@helpdesk.com",
        "description": "The laptop battery lasts only about 40 minutes after a full charge, even with only one browser tab open.",
        "resolution": "Battery health was at 54 percent. Battery replaced under warranty and power settings adjusted.",
        "comments": [],
    },
    {
        "title": "Slow internet in the library",
        "category": "Network Problem",
        "priority": "Medium",
        "status": "Resolved",
        "days_ago": 80,
        "creator": "priya@helpdesk.com",
        "assignee": "maria@helpdesk.com",
        "description": "Internet in the library reading area is extremely slow in the afternoon. Pages take over a minute to load.",
        "resolution": "The library access point was overloaded. Added a second access point and balanced the channels.",
        "comments": [
            ("maria@helpdesk.com", "Speed test shows 1 Mbps on the library AP. Investigating the uplink.", 2),
        ],
    },
    {
        "title": "Need SPSS installed for research work",
        "category": "Software Issue",
        "priority": "Medium",
        "status": "Assigned",
        "days_ago": 72,
        "creator": "daniel@helpdesk.com",
        "assignee": "david@helpdesk.com",
        "description": "I need SPSS installed on my office desktop for the departmental research project. The license is held by the statistics department.",
        "resolution": "",
        "comments": [
            ("david@helpdesk.com", "Please share the license confirmation from the statistics department.", 6),
        ],
    },
    {
        "title": "Scanner not detected by computer",
        "category": "Printer Issue",
        "priority": "Low",
        "status": "Open",
        "days_ago": 65,
        "creator": "ayesha@helpdesk.com",
        "assignee": None,
        "description": "The flatbed scanner connected by USB is not detected in Windows. It worked last week on the same computer.",
        "resolution": "",
        "comments": [],
    },
    {
        "title": "Password expired and cannot reset",
        "category": "Login and Password Issue",
        "priority": "High",
        "status": "Resolved",
        "days_ago": 58,
        "creator": "daniel@helpdesk.com",
        "assignee": "support@helpdesk.com",
        "description": "My domain password expired this morning. The self-service reset page gives an error and I cannot log in to my computer.",
        "resolution": "Reset the domain password from the admin console and updated it on the user's laptop.",
        "comments": [
            ("support@helpdesk.com", "Password reset done, please log in and change it again from your desk.", 1),
        ],
    },
    {
        "title": "Shared drive not accessible",
        "category": "Network Problem",
        "priority": "High",
        "status": "In Progress",
        "days_ago": 51,
        "creator": "user@helpdesk.com",
        "assignee": "maria@helpdesk.com",
        "description": "The Accounts shared drive is not opening since this morning. Windows shows the error 'network path not found'.",
        "resolution": "",
        "comments": [
            ("maria@helpdesk.com", "The file server service was restarted. Please try mapping the drive again.", 3),
            ("user@helpdesk.com", "Tried again, still the same error message.", 5),
        ],
    },
    {
        "title": "Teams microphone not working",
        "category": "Hardware Issue",
        "priority": "Medium",
        "status": "Resolved",
        "days_ago": 44,
        "creator": "ayesha@helpdesk.com",
        "assignee": "david@helpdesk.com",
        "description": "Other participants cannot hear me in Teams meetings. The headset works in other applications.",
        "resolution": "Teams was using the wrong input device. Selected the correct microphone and disabled exclusive mode.",
        "comments": [
            ("david@helpdesk.com", "Please test the microphone in Teams settings after the change.", 2),
        ],
    },
    {
        "title": "Spam emails filling the inbox",
        "category": "Email Issue",
        "priority": "Medium",
        "status": "Closed",
        "days_ago": 38,
        "creator": "priya@helpdesk.com",
        "assignee": "support@helpdesk.com",
        "description": "I am receiving around 50 spam messages every day, many pretending to be from the bank. Some contain attachments.",
        "resolution": "Enabled the mail gateway spam filter for the mailbox, blocked the sender domain and trained the filter.",
        "comments": [
            ("support@helpdesk.com", "Do not open any attachments from these senders. Filter rules are now active.", 2),
        ],
    },
    {
        "title": "Attendance software crashes on login",
        "category": "Software Issue",
        "priority": "Critical",
        "status": "Resolved",
        "days_ago": 31,
        "creator": "daniel@helpdesk.com",
        "assignee": "maria@helpdesk.com",
        "description": "The attendance system closes immediately after login. The whole department cannot mark attendance today.",
        "resolution": "A corrupted local database file caused the crash. Rebuilt the local cache and re-imported the staff list.",
        "comments": [
            ("maria@helpdesk.com", "Working on the local database. Please use the manual register for today.", 1),
        ],
    },
    {
        "title": "New employee email account request",
        "category": "Email Issue",
        "priority": "Low",
        "status": "Assigned",
        "days_ago": 26,
        "creator": "user@helpdesk.com",
        "assignee": "david@helpdesk.com",
        "description": "Please create an official email account for a new employee joining the Accounts department next Monday.",
        "resolution": "",
        "comments": [
            ("david@helpdesk.com", "Please share the employee's full name and CNIC for the account form.", 4),
        ],
    },
    {
        "title": "Blue screen after Windows update",
        "category": "Hardware Issue",
        "priority": "Critical",
        "status": "In Progress",
        "days_ago": 21,
        "creator": "ayesha@helpdesk.com",
        "assignee": "support@helpdesk.com",
        "description": "After the latest Windows update the computer restarts with a blue screen and the stop code WHEA_UNCORRECTABLE_ERROR.",
        "resolution": "",
        "comments": [
            ("support@helpdesk.com", "Rolled back the display driver. Monitoring the machine for another day.", 8),
        ],
    },
    {
        "title": "Printer prints blank pages",
        "category": "Printer Issue",
        "priority": "Medium",
        "status": "Resolved",
        "days_ago": 17,
        "creator": "priya@helpdesk.com",
        "assignee": "maria@helpdesk.com",
        "description": "The laser printer pulls paper through but the pages come out completely blank, even after replacing the toner.",
        "resolution": "The drum unit was not seated correctly. Reseated the drum and ran the printer self-test successfully.",
        "comments": [],
    },
    {
        "title": "VPN connection fails from home",
        "category": "Network Problem",
        "priority": "High",
        "status": "Resolved",
        "days_ago": 13,
        "creator": "user@helpdesk.com",
        "assignee": "david@helpdesk.com",
        "description": "The office VPN client reports 'authentication failed' when I try to connect from home. It worked last month.",
        "resolution": "The VPN certificate had expired. Installed the renewed certificate and verified the connection.",
        "comments": [
            ("david@helpdesk.com", "Your certificate expired on the 1st. Installing the new one now.", 2),
        ],
    },
    {
        "title": "Cannot open large Excel file",
        "category": "Software Issue",
        "priority": "Low",
        "status": "Open",
        "days_ago": 9,
        "creator": "daniel@helpdesk.com",
        "assignee": None,
        "description": "Excel stops responding when opening the yearly stock file. The file is about 85 MB and opens on a colleague's computer.",
        "resolution": "",
        "comments": [],
    },
    {
        "title": "Monitor flickering in Accounts office",
        "category": "Hardware Issue",
        "priority": "Medium",
        "status": "Resolved",
        "days_ago": 6,
        "creator": "ayesha@helpdesk.com",
        "assignee": "support@helpdesk.com",
        "description": "The monitor flickers constantly and sometimes goes black for a second. It happens with both VGA and HDMI cables.",
        "resolution": "The monitor power adapter was faulty. Replaced the adapter and the display is stable.",
        "comments": [
            ("support@helpdesk.com", "Tested with another monitor, the fault is in the adapter.", 3),
        ],
    },
    {
        "title": "Email attachments rejected",
        "category": "Email Issue",
        "priority": "Medium",
        "status": "Closed",
        "days_ago": 4,
        "creator": "priya@helpdesk.com",
        "assignee": "maria@helpdesk.com",
        "description": "Emails with PDF attachments larger than 5 MB are rejected with a delivery failure message.",
        "resolution": "The mailbox send limit was 5 MB. Increased it to 25 MB as per the IT policy.",
        "comments": [],
    },
    {
        "title": "Wi-Fi password changed without notice",
        "category": "Network Problem",
        "priority": "Low",
        "status": "In Progress",
        "days_ago": 2,
        "creator": "user@helpdesk.com",
        "assignee": "maria@helpdesk.com",
        "description": "The staff Wi-Fi password no longer works and nobody informed the departments about a change.",
        "resolution": "",
        "comments": [
            ("maria@helpdesk.com", "The password was rotated. Sharing the new one through the department heads.", 1),
        ],
    },
]


def seed_sample_data():
    """
    Insert the demonstration users, tickets, comments, history and notifications.

    Returns the number of tickets created (0 when the database already has data).
    """
    if Ticket.query.count() > 0:
        return 0

    # ---- 1. Additional demonstration accounts -----------------------------
    for data in SAMPLE_USERS:
        if User.query.filter_by(email=data["email"]).first() is None:
            user = User(
                name=data["name"],
                email=data["email"],
                department=data["department"],
                role=data["role"],
            )
            user.set_password(SAMPLE_PASSWORD)
            db.session.add(user)
    db.session.commit()

    users = {user.email: user for user in User.query.all()}
    categories = {category.name: category for category in Category.query.all()}
    admin = User.query.filter_by(role="admin").first()
    now = datetime.now()

    # ---- 2. Tickets with history and comments -----------------------------
    created_count = 0
    for index, spec in enumerate(SAMPLE_TICKETS):
        creator = users[spec["creator"]]
        assignee = users.get(spec["assignee"])
        category = categories[spec["category"]]

        created_at = now - timedelta(days=spec["days_ago"], hours=2 + (index % 6))
        updated_at = created_at

        resolved_at = None
        if spec["status"] in ("Resolved", "Closed"):
            resolved_at = created_at + timedelta(days=1, hours=4)
            if resolved_at > now - timedelta(hours=12):
                resolved_at = now - timedelta(hours=12)
            updated_at = resolved_at

        ticket = Ticket(
            ticket_number=next_ticket_number(),
            title=spec["title"],
            description=spec["description"],
            category_id=category.id,
            priority=spec["priority"],
            status=spec["status"],
            created_by=creator.id,
            assigned_to=assignee.id if assignee else None,
            resolution_notes=spec["resolution"] or None,
            created_at=created_at,
            updated_at=updated_at,
            resolved_at=resolved_at,
        )
        db.session.add(ticket)
        db.session.flush()  # so history rows can use ticket.id
        created_count += 1
        number = ticket.ticket_number

        # History: creation
        db.session.add(
            TicketHistory(
                ticket_id=ticket.id,
                changed_by=creator.id,
                old_status=None,
                new_status="Open",
                activity_description=f"Ticket {number} created with status Open.",
                created_at=created_at,
            )
        )

        # History: assignment
        if assignee is not None:
            assigned_at = created_at + timedelta(hours=3)
            db.session.add(
                TicketHistory(
                    ticket_id=ticket.id,
                    changed_by=admin.id,
                    old_status="Open",
                    new_status="Assigned",
                    activity_description=f"Ticket assigned to {assignee.name} by {admin.name}.",
                    created_at=assigned_at,
                )
            )

        # History: progress
        if spec["status"] in ("In Progress", "Resolved", "Closed"):
            started_at = created_at + timedelta(days=1)
            db.session.add(
                TicketHistory(
                    ticket_id=ticket.id,
                    changed_by=(assignee or admin).id,
                    old_status="Assigned",
                    new_status="In Progress",
                    activity_description=f"Status changed from Assigned to In Progress by {(assignee or admin).name}.",
                    created_at=started_at,
                )
            )

        # History: resolution
        if resolved_at is not None:
            db.session.add(
                TicketHistory(
                    ticket_id=ticket.id,
                    changed_by=(assignee or admin).id,
                    old_status="In Progress",
                    new_status="Resolved",
                    activity_description=f"Status changed from In Progress to Resolved by {(assignee or admin).name}.",
                    created_at=resolved_at,
                )
            )

        # History: closed
        if spec["status"] == "Closed":
            db.session.add(
                TicketHistory(
                    ticket_id=ticket.id,
                    changed_by=admin.id,
                    old_status="Resolved",
                    new_status="Closed",
                    activity_description=f"Ticket closed by {admin.name} after user confirmation.",
                    created_at=min(resolved_at + timedelta(days=1), now - timedelta(hours=2)),
                )
            )

        # Comments from staff and employees
        for author_email, text, hours_after in spec["comments"]:
            author = users.get(author_email)
            if author is None:
                continue
            db.session.add(
                Comment(
                    ticket_id=ticket.id,
                    user_id=author.id,
                    comment_text=text,
                    created_at=created_at + timedelta(hours=hours_after),
                )
            )
        db.session.add(ticket)

    db.session.commit()

    # ---- 3. A few notifications so the bell menu is not empty -------------
    newest = Ticket.query.order_by(Ticket.created_at.desc()).limit(4).all()
    employee = users["user@helpdesk.com"]
    support = users["support@helpdesk.com"]

    for ticket in newest[:2]:
        db.session.add(
            Notification(
                user_id=employee.id,
                message=f"Ticket {ticket.ticket_number} is now {ticket.status}.",
                link=f"/tickets/{ticket.id}",
                is_read=False,
                created_at=now - timedelta(hours=3),
            )
        )

    db.session.add(
        Notification(
            user_id=support.id,
            message=f"New ticket assigned to you: {newest[-1].ticket_number} - {newest[-1].title}",
            link=f"/tickets/{newest[-1].id}",
            is_read=False,
            created_at=now - timedelta(hours=6),
        )
    )
    db.session.add(
        Notification(
            user_id=admin.id,
            message=f"New ticket submitted: {newest[0].ticket_number} - {newest[0].title}",
            link=f"/tickets/{newest[0].id}",
            is_read=False,
            created_at=now - timedelta(hours=8),
        )
    )

    db.session.commit()
    return created_count


DEFAULT_KB_ARTICLES = [
    {
        "title": "How to Connect to Office & Campus Wi-Fi",
        "category_name": "Network Problem",
        "keywords": "wifi, network, internet, wireless, connect, ssid, signal, eduroam",
        "solution": (
            "1. Toggle Wi-Fi ON from your device's network settings.\n"
            "2. Select the network 'Campus-Staff-Secure' or 'Office-Secure' from available connections.\n"
            "3. When prompted, choose WPA2/WPA3 Enterprise authentication.\n"
            "4. Enter your organization email username and password.\n"
            "5. If prompted to trust or accept a server security certificate, click 'Trust' / 'Accept'.\n"
            "6. If you receive an authentication error, right-click the network, click 'Forget', and try again."
        ),
        "views": 42,
        "helpful_count": 18,
    },
    {
        "title": "Fixing Printer Paper Jam or Offline Status",
        "category_name": "Printer Issue",
        "keywords": "printer, print, paper, jam, offline, queue, spooler, stuck, canon, hp",
        "solution": (
            "1. Check the physical paper tray: remove any crumpled paper and ensure the tray is not overloaded.\n"
            "2. Open the printer's front and rear access doors to check for any paper lodged near the rollers. Pull paper out gently in the feed direction.\n"
            "3. Restart the Windows Print Spooler: Press Win + R, type 'services.msc', right-click 'Print Spooler' and select 'Restart'.\n"
            "4. Open Printers & Scanners in Windows Settings, click on the printer, open the print queue, and cancel any stuck pending jobs.\n"
            "5. Make sure 'Use Printer Offline' is unchecked in the printer menu."
        ),
        "views": 65,
        "helpful_count": 29,
    },
    {
        "title": "Self-Service Password Reset & Account Lockout",
        "category_name": "Login and Password Issue",
        "keywords": "password, login, reset, forgot, locked, lockout, account, credentials, access, sign in",
        "solution": (
            "1. If you entered an incorrect password 5 consecutive times, your account enters a 15-minute security lock. Please wait 15 minutes before retrying.\n"
            "2. If you are currently logged in, you can update your password under 'My Profile > Change Password'.\n"
            "3. Password criteria: Minimum 6 characters (recommended 8+), containing at least one uppercase letter, one number, and one symbol.\n"
            "4. If you have completely forgotten your password, contact your IT helpdesk administrator for a one-time credential reset."
        ),
        "views": 88,
        "helpful_count": 35,
    },
    {
        "title": "Outlook & Email Sync or Mailbox Full Issue",
        "category_name": "Email Issue",
        "keywords": "email, outlook, sync, mailbox, full, storage, quota, send, receive, pst, exchange",
        "solution": (
            "1. Mailbox Storage Full: Empty both your 'Deleted Items' and 'Junk Email' folders to instantly reclaim storage.\n"
            "2. Sort by Size: In your Inbox, click the sort dropdown and choose 'Size' (Largest on top). Save large email attachments to local storage or OneDrive and delete the emails.\n"
            "3. Offline Status: Check the bottom-right corner of Outlook. If it displays 'Disconnected' or 'Working Offline', click the 'Send / Receive' tab and uncheck 'Work Offline'.\n"
            "4. Press F9 (or click 'Send/Receive All Folders') to force a complete mailbox sync."
        ),
        "views": 37,
        "helpful_count": 14,
    },
    {
        "title": "Computer Monitor Not Displaying (Black Screen / No Signal)",
        "category_name": "Hardware Issue",
        "keywords": "monitor, screen, display, black, blank, no signal, hdmi, vga, cable, power, dual",
        "solution": (
            "1. Power Check: Ensure the monitor power LED is ON. If not, check the power cable connection and test the wall outlet.\n"
            "2. Reseat Display Cable: Unplug both ends of the HDMI / DisplayPort cable, check for bent pins, and reconnect firmly.\n"
            "3. Display Mode: Press Windows Key + P on your keyboard and select 'Duplicate' or 'Extend'.\n"
            "4. Input Source: Press the 'Source' or 'Input' button on the monitor bezel to ensure it is set to HDMI 1 / DisplayPort instead of Auto."
        ),
        "views": 53,
        "helpful_count": 22,
    },
    {
        "title": "Slow Internet, DNS Errors or Webpages Not Loading",
        "category_name": "Network Problem",
        "keywords": "slow, internet, web, site, dns, connection, loading, speed, buffer, ping, browser",
        "solution": (
            "1. Flush DNS Cache: Open Command Prompt as Administrator and type 'ipconfig /flushdns' then press Enter.\n"
            "2. Renew IP: In Command Prompt, run 'ipconfig /release' followed by 'ipconfig /renew'.\n"
            "3. Clear Browser Cache: Press Ctrl + Shift + Delete in Chrome/Edge, select 'Cached images and files', and click 'Clear data'.\n"
            "4. Incognito Test: Open an Incognito/InPrivate window to see if a faulty browser extension is causing the delay."
        ),
        "views": 49,
        "helpful_count": 21,
    },
    {
        "title": "Requesting Software Installation or Admin Rights",
        "category_name": "Software Issue",
        "keywords": "software, install, download, license, admin, permission, rights, exe, setup",
        "solution": (
            "1. Check Company Portal: Search for 'Company Portal' or 'Software Center' in your Start menu. Standard approved applications (Chrome, VS Code, Slack, Zoom, Acrobat) install directly with one click without admin rights.\n"
            "2. Paid Licenses: For proprietary tools (AutoCAD, Adobe Creative Cloud, SPSS), request departmental manager sign-off first.\n"
            "3. If software is not in the Company Portal, raise a Software Issue ticket and attach the vendor link."
        ),
        "views": 31,
        "helpful_count": 12,
    },
    {
        "title": "Audio, Microphone or Web Camera Not Working",
        "category_name": "Hardware Issue",
        "keywords": "audio, sound, mic, microphone, camera, webcam, zoom, teams, video, meeting, call",
        "solution": (
            "1. Windows Privacy Settings: Open Settings > Privacy & security > Camera (and Microphone). Ensure 'Let apps access your camera/microphone' is set to ON.\n"
            "2. Physical Privacy Shutter: Check the top bezel of your laptop camera. Many modern laptops have a physical sliding switch blocking the lens.\n"
            "3. Audio Output: Click the volume icon on the Windows taskbar and verify that the intended headphones or speakers are selected as Default Device.\n"
            "4. Meeting App Settings: In Zoom / Teams, click Settings > Audio and click 'Test Speaker' and 'Test Mic'."
        ),
        "views": 28,
        "helpful_count": 16,
    },
]


def seed_knowledge_base():
    """Create default self-service solutions if the Knowledge Base is empty."""
    if KnowledgeArticle.query.first() is not None:
        return 0

    categories = {c.name: c for c in Category.query.all()}
    created = 0

    for item in DEFAULT_KB_ARTICLES:
        category = categories.get(item["category_name"])
        if category:
            article = KnowledgeArticle(
                title=item["title"],
                category_id=category.id,
                keywords=item["keywords"],
                solution=item["solution"],
                views=item.get("views", 0),
                helpful_count=item.get("helpful_count", 0),
            )
            db.session.add(article)
            created += 1

    db.session.commit()
    return created

