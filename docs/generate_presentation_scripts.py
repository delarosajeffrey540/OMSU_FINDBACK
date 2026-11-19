from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


OUT = Path(__file__).resolve().parent
BLUE = colors.HexColor("#163B67")
TEAL = colors.HexColor("#087E8B")
PALE = colors.HexColor("#EAF2F8")
INK = colors.HexColor("#182433")
MUTED = colors.HexColor("#526477")

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name="CoverTitle", parent=styles["Title"], fontName="Helvetica-Bold",
    fontSize=25, leading=30, textColor=BLUE, alignment=1, spaceAfter=12,
))
styles.add(ParagraphStyle(
    name="CoverSub", parent=styles["Normal"], fontSize=11, leading=16,
    textColor=MUTED, alignment=1, spaceAfter=7,
))
styles.add(ParagraphStyle(
    name="Section", parent=styles["Heading1"], fontName="Helvetica-Bold",
    fontSize=16, leading=20, textColor=BLUE, spaceBefore=4, spaceAfter=7,
))
styles.add(ParagraphStyle(
    name="Sub", parent=styles["Heading2"], fontName="Helvetica-Bold",
    fontSize=10.5, leading=13, textColor=TEAL, spaceBefore=7, spaceAfter=3,
))
styles.add(ParagraphStyle(
    name="Body", parent=styles["BodyText"], fontName="Helvetica",
    fontSize=9, leading=12.3, textColor=INK, spaceAfter=4,
))
styles.add(ParagraphStyle(
    name="Small", parent=styles["BodyText"], fontName="Helvetica",
    fontSize=7.8, leading=10, textColor=MUTED, spaceAfter=3,
))
styles.add(ParagraphStyle(
    name="TableHead", parent=styles["BodyText"], fontName="Helvetica-Bold",
    fontSize=7.8, leading=10, textColor=colors.white,
))
styles.add(ParagraphStyle(
    name="Callout", parent=styles["BodyText"], fontName="Helvetica-Bold",
    fontSize=8.8, leading=12, textColor=BLUE, backColor=PALE,
    borderColor=colors.HexColor("#B8CDDF"), borderWidth=.5,
    borderPadding=6, spaceBefore=4, spaceAfter=6,
))
styles.add(ParagraphStyle(
    name="Quote", parent=styles["BodyText"], fontName="Helvetica-Oblique",
    fontSize=9.2, leading=13, leftIndent=8, rightIndent=5, textColor=INK,
    borderColor=TEAL, borderLeftWidth=2, borderPadding=6,
    spaceBefore=2, spaceAfter=6,
))


def para(text, style="Body"):
    return Paragraph(escape(text).replace("\n", "<br/>"), styles[style])


def bullet(text):
    return Paragraph("&bull; " + escape(text), styles["Body"])


def footer(canvas, doc):
    canvas.saveState()
    width, _ = letter
    canvas.setStrokeColor(colors.HexColor("#D6E0E9"))
    canvas.line(.62 * inch, .53 * inch, width - .62 * inch, .53 * inch)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(.65 * inch, .36 * inch, "OMSU FINDBACK  |  PRESENTATION SCRIPT")
    canvas.drawRightString(width - .65 * inch, .36 * inch, str(doc.page))
    canvas.restoreState()


def save_pdf(filename, story):
    doc = SimpleDocTemplate(
        str(OUT / filename), pagesize=letter, leftMargin=.66 * inch,
        rightMargin=.66 * inch, topMargin=.65 * inch, bottomMargin=.68 * inch,
        title=filename.replace("_", " "), author="OMSU FindBack Presentation Team",
    )
    doc.build(story, onFirstPage=footer, onLaterPages=footer)


def segment(number, name, feature, route, purpose, steps, speech, video):
    story = [
        para(f"{number:02d}  |  {name}", "Section"),
        para(f"Assigned feature: {feature}"),
        para("Start at: " + route, "Callout"),
        para("Explain this: " + purpose),
        para("DEMONSTRATION - FOLLOW THESE STEPS", "Sub"),
    ]
    story.extend(para(f"{i}. {step}") for i, step in enumerate(steps, 1))
    story.extend([
        para("SAY THIS", "Sub"),
        para('"' + speech + '"', "Quote"),
        para("VIDEO CUE", "Sub"),
        para(video, "Small"),
        Spacer(1, 7),
    ])
    return story


def backend_chapter(number, title, screen, files, steps, speech, video):
    story = [
        para(f"{number:02d}  |  {title}", "Section"),
        para("On screen: " + screen, "Callout"),
        para("Relevant files: " + ", ".join(files), "Small"),
        para("DEMONSTRATION STEPS", "Sub"),
    ]
    story.extend(para(f"{i}. {step}") for i, step in enumerate(steps, 1))
    story.extend([
        para("SAY THIS", "Sub"),
        para('"' + speech + '"', "Quote"),
        para("VIDEO CUE", "Sub"),
        para(video, "Small"),
        PageBreak(),
    ])
    return story


def make_frontend():
    story = [
        Spacer(1, .45 * inch),
        para("OMSU FINDBACK", "CoverSub"),
        para("Front-End Demonstration Script", "CoverTitle"),
        para("Eight presenter assignments | Interfaces, design, user experience, and features", "CoverSub"),
        para("Purpose", "Sub"),
        para("Use this as a spoken guide and screen-recording checklist. Each presenter demonstrates one real workflow in the current OMSU FindBack application. Follow the actions in order, narrate the visible interaction, and explain what the user gains from the design."),
        para("Recording setup", "Sub"),
    ]
    story.extend([
        bullet("Use the local demo site at http://127.0.0.1:5000 and prepared demo accounts. Never record real passwords, private claim answers, personal IDs, or production records."),
        bullet("Record browser content at 1080p if available; keep the cursor slow and page zoom readable. Begin each clip with a 2-second title card showing presenter name and segment number."),
        bullet("Sign in before recording whenever typing credentials could expose them. Use only a designated demo record for any submit, approve, reject, or status-change action."),
        bullet("If the screen is empty, prepare demo data first. Do not claim a feature worked if the data or optional email setup is unavailable. In-app notifications are the dependable demo path."),
        para("Suggested order and timing", "Sub"),
    ])
    rows = [
        ["Presenter", "Feature area", "Target"],
        ["1 Alisa Gerardino", "Sign-in, registration, role entry", "1-1.5 min"],
        ["2 Gener Meneses", "Student campus board and item detail", "1 min"],
        ["3 Heyl Unson", "Report form and photo suggestions", "1.5 min"],
        ["4 John Mark Payag", "My reports and AI match suggestions", "1.5 min"],
        ["5 Johnlord Ortiz", "Claims, recovery, messages, alerts", "1.5 min"],
        ["6 Lennox Pedraza", "Moderator review and item management", "1.5-2 min"],
        ["7 Neil Suner", "Admin overview, analytics, records", "1.5 min"],
        ["8 Nikko Galendez", "User, role, category, location admin", "1.5 min"],
    ]
    table = Table(
        [[para(cell, "TableHead" if row_index == 0 else "Small") for cell in row]
         for row_index, row in enumerate(rows)],
        colWidths=[1.55 * inch, 3.8 * inch, 1 * inch], repeatRows=1,
    )
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLUE),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), .35, colors.HexColor("#CAD6E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.extend([
        table, Spacer(1, 6),
        para("Show the interface while speaking; do not read code in a front-end segment. AI suggestions are decision-support only. Human staff verify ownership and handover.", "Callout"),
        PageBreak(),
    ])
    story.extend(segment(
        1, "ALISA GERARDINO", "Sign-in, student registration, password visibility, role-based entry",
        "/login then /register",
        "The sign-in page presents OMSU branding and a short recovery story. Registration is for students; moderators and administrators are assigned by an administrator. Successful sign-in opens the correct role workspace.",
        [
            "Open sign-in. Point out the branded introduction, three recovery steps, email/password fields, and create-account link.",
            "Open Create an account. Show registration fields and explain that students register themselves; do not submit real personal data.",
            "Return to sign-in and use the prepared demo student account. Keep the password masked and avoid showing credentials being typed.",
            "Pause on the student workspace and point out role-specific navigation. If time permits, show the password visibility control.",
        ],
        "This is the entry point to OMSU FindBack. The sign-in screen keeps the task clear and provides a visible path for new students to register. Staff roles are assigned by an administrator. After successful sign-in, the system routes each account to the correct workspace, so users see the tools relevant to their role.",
        "Capture the sign-in screen, registration form, then student landing page. Blur or cut away from account details. Do not show actual credentials or a staff password. Use pre-created demo accounts to show role redirects.",
    ))
    story.append(PageBreak())
    story.extend(segment(
        2, "GENER MENESES", "Student campus board, navigation, and item details",
        "/student/dashboard",
        "The shared layout provides role-aware navigation. Student cards show recent item type, status, name, location, date, and category, then link to the report details.",
        [
            "Sign in as a prepared demo student and show the left navigation and campus board heading.",
            "Point to Report lost item and Report found item, then the recently reported cards.",
            "Open a demo item. Show its report code, description, location, date, current status, and photo if available.",
            "Explain the safety note about keeping unique ownership details private. Return and point out My reports, AI matches, and Recovery tracker.",
        ],
        "The student workspace is organized around the campus board. The visual cards make it easy to scan what was reported and where, while each card opens details before the student takes action. The side navigation keeps reporting, matches, and recovery tracking close at hand. The design also reminds users not to publish hidden ownership details.",
        "Keep the whole card visible before opening it. Use safe demo text with no personal identifiers; record the click into detail and the return to the board.",
    ))
    story.append(PageBreak())
    story.extend(segment(
        3, "HEYL UNSON", "Lost/found report submission and local photo suggestions",
        "/student/report/lost or /student/report/found",
        "The report form separates photo, item details, date, location, and description. Categories and locations come from active controlled lists. Photo suggestions are optional and must be checked by the person reporting.",
        [
            "From the student board, choose Report lost item or Report found item and show the photo/details/submit steps.",
            "Choose a safe demo image and click Suggest details from photo. Explain that guesses can be corrected or ignored.",
            "Complete item name, category, date, campus location, and description. Keep unique identifying facts out of the public description.",
            "Submit only a prepared demo report. Show confirmation and My reports status; explain that new reports wait for moderator review.",
        ],
        "This form guides a student through reporting without unnecessary steps. A photo can be analyzed locally to suggest common object details, but those suggestions are not guaranteed and the user remains in control. Required fields and campus lists keep the report useful, while the privacy note protects ownership evidence. A new report goes to human moderation.",
        "Frame the photo result and fields it suggests. Do not call AI a custom OMSU-trained model or a guarantee. Keep a demo image ready and submit only a record intended for the presentation.",
    ))
    story.append(PageBreak())
    story.extend(segment(
        4, "JOHN MARK PAYAG", "My reports, statuses, and AI-suggested matches",
        "/student/reports then /student/matches",
        "My reports tracks the signed-in student's reports. Matches ranks possible pairs of verified lost/found reports and can show photo similarity when both reports have photos.",
        [
            "Open My reports and identify a report code, item, type, and status.",
            "Open AI matches using a prepared student account with a verified lost report and verified found report in demo data.",
            "Point out the candidate, score, and photo similarity if shown. Open the suggested found item to inspect it.",
            "Explain that a match is not proof of ownership and that the empty state is expected when no suitable verified reports exist.",
        ],
        "This area helps students follow their own reports and notice potentially relevant found items. Matching ranks candidates using report details and, when both photos are present, local image features. The score is a navigation aid, not a decision. A student still reviews the item and submits a private claim, and staff verify ownership.",
        "Prepare a demo student with at least one verified Lost report and verified Found report in the database. Capture the score disclaimer. If no pair appears, show the empty state rather than inventing a match.",
    ))
    story.append(PageBreak())
    story.extend(segment(
        5, "JOHNLORD ORTIZ", "Private claim, recovery tracker, conversation, and notifications",
        "/student/item/<found-report-id> then /student/recovery",
        "A claim is limited to an eligible verified found report owned by another user. The claimant enters private details; a conversation and notifications support coordination. Staff verify physical handover.",
        [
            "Open a verified found-item detail page as a different demo student, then choose the claim action.",
            "Show the private ownership-check page and its two prompts. Do not expose private answers or submit a claim unless using resettable demo data.",
            "Open Recovery tracker and show claim status and conversation link. Open the conversation without displaying sensitive test text.",
            "Open Notifications and point to claim/status alerts. Explain that in-app alerts work without optional email.",
        ],
        "A student does not prove ownership on the public item card. The claim form asks for identifying details privately and advises against sending a full student ID online. The claim creates a recovery-tracking entry and private conversation. Notifications keep people informed, but authorized staff verify the handover and complete recovery.",
        "Use a fake item and demo claimant/owner accounts. Keep claim evidence out of the recording; blur chat text if needed. Do not imply that a student can approve a claim.",
    ))
    story.append(PageBreak())
    story.extend(segment(
        6, "LENNOX PEDRAZA", "Moderator review queue, claim verification, and item management",
        "/moderator/queue and /moderator/items",
        "Moderators review reports and claims separately. They can approve/reject reports, request more claim proof, and verify completed handovers. Item management supports authorized staff workflows.",
        [
            "Sign in with a prepared moderator account and open Review queue. Point to report review and ownership claim lists.",
            "Show a demo report and explain approve/reject. Submit an action only on a designated test record.",
            "Show a demo claim, private evidence area, and SSG Office reminder; explain that proof is reviewed by a person.",
            "Demonstrate Request proof or an explicitly designated demo approval. Explain that completion updates status, records handover, and notifies parties.",
            "Open Manage lost & found and show staff-created reports or claim/status controls. State that mutations are for test data only.",
        ],
        "Moderators are the human review layer between a public report and a recovered item. This queue puts pending reports and claims in one place. Approving a report makes it eligible for matching; approving a claim is a separate step that records a verified handover. These controls are role-protected and intended for authorized staff.",
        "Record the queue, then item management. Use labeled demo records. Avoid real claimant details. If you click an approval or rejection, state the expected status change and use a resettable record only.",
    ))
    story.append(PageBreak())
    story.extend(segment(
        7, "NEIL SUNER", "Administrator overview, records, analytics, handover history, audit trail",
        "/admin/overview then /admin/analytics",
        "The overview summarizes reports, recoveries, active users, and AI analyses. Admin analytics aggregate activity by selected period; records, handover history, and audit pages support oversight.",
        [
            "Sign in as a demo administrator and show overview metrics and recent records.",
            "Open analytics. Set a date range and show totals, recovery count, category/location breakdown, monthly activity, and AI activity if available.",
            "Open Lost & found records and Claim handover history. Explain that a transaction snapshot preserves completed handover information.",
            "Open Audit trail and point to logged administrative actions. Do not reveal private claim answers.",
        ],
        "The administrator dashboard gives a high-level view of platform activity and links to the records behind that summary. Date filters help analyze the selected period, and analytics group report and local AI activity. Claim handover history preserves completed transaction details, while the audit trail records administrative changes for accountability.",
        "Use demo data so charts are meaningful. Record one page at a time; avoid reading personal fields from claim-history snapshots. If there are no analytics events, describe the zero value accurately.",
    ))
    story.append(PageBreak())
    story.extend(segment(
        8, "NIKKO GALENDEZ", "Administrator user, role, category, and campus-location management",
        "/admin/users and /admin/catalogs",
        "Account role/status changes are administrator controls; student registration cannot create staff access. Campus lists can be added, renamed, and activated/deactivated without rewriting existing report text.",
        [
            "Open User accounts and show search, role, and status fields. Explain that student, moderator, and admin roles are assigned through this workflow.",
            "Open a demo account edit screen and explain controls. Do not change a real account; use a test account if demonstrating a save.",
            "Open Categories & locations. Show the separate campus lists and how staff can add, rename, or deactivate/reactivate entries.",
            "Explain that inactive entries stop appearing as new report choices while existing report text remains. Changes are recorded in the audit trail.",
        ],
        "Account and campus-list management are reserved for administrators. That separation prevents a self-registered student from assigning themselves staff privileges. Campus lists keep report forms consistent, and deactivation preserves older records. Changes are validated and recorded so the system remains manageable and accountable.",
        "Use a non-privileged demo account and test category/location. Avoid deleting or deactivating active users in a recorded demo. Show the controls or save only a reversible test change.",
    ))
    story.extend([
        PageBreak(), para("Final video assembly checklist", "Section"),
        bullet("Place clips in presenter order and add a chapter title with each presenter name and feature."),
        bullet('Use labels such as "Student - Campus board", "Moderator - Review queue", and "Admin - Analytics".'),
        bullet("Keep narration synchronized with the visible screen. Retake failed actions rather than narrating an outcome that did not happen."),
        bullet("Close with the group handoff: student reports and claims feed a human-reviewed workflow; administrators support access, records, and oversight."),
    ])
    save_pdf("OMSU_FINDBACK_Front_End_Presentation_Script.pdf", story)


def make_backend():
    story = [
        Spacer(1, .45 * inch),
        para("OMSU FINDBACK", "CoverSub"),
        para("Back-End Demonstration Script", "CoverTitle"),
        para("Presenter: JEFFREY DELA ROSA | Server-side workflow and recording guide", "CoverSub"),
        para("Presentation objective", "Sub"),
        para("Explain how browser actions travel through Flask routes, authentication and role checks, SQLAlchemy/MySQL operations, optional local AI processing, messaging, and notifications. Show code and confirm the visible result in the running application. This project primarily renders HTML pages and processes form submissions; it is not a REST-only JSON application."),
        para("Before recording", "Sub"),
        bullet("Use local demo accounts and records. Keep database passwords, SECRET_KEY, SMTP credentials, .env, private claim details, and real user records off-screen. Do not run destructive SQL or change production data."),
        bullet("Record at 1080p if possible. Capture browser behavior and VS Code code walkthroughs. Add a title overlay for each chapter: Jeffrey Dela Rosa - Backend - 01 ..."),
        bullet("Prepare a demo student, moderator, administrator, verified report, eligible claim, and sample image. If a dependency or dataset is unavailable, state that plainly and show the code without pretending to execute it."),
        bullet("Suggested length: about 6-8 minutes. Pause briefly after each action so the instructor can read the screen."),
        para("Sequence at a glance", "Sub"),
    ]
    rows = [
        ["Chapter", "Show / explain"],
        ["1 Architecture", "app.py, factory, blueprint registration"],
        ["2 Authentication", "auth/routes.py, User model, role redirects"],
        ["3 Database", "models.py, MySQL config, SQLAlchemy tables"],
        ["4 Report flow", "student/routes.py, validation, upload, notification"],
        ["5 AI / matching", "JSON suggestion route and ai_engine modules"],
        ["6 Moderation", "moderator/routes.py, transactions, audit"],
        ["7 Messaging", "Socket.IO events, authorization, stored messages"],
        ["8 Security / admin", "CSRF, rate limits, sessions, private uploads, analytics"],
    ]
    table = Table(
        [[para(cell, "TableHead" if row_index == 0 else "Small") for cell in row]
         for row_index, row in enumerate(rows)],
        colWidths=[1.4 * inch, 4.95 * inch], repeatRows=1,
    )
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLUE),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), .35, colors.HexColor("#CAD6E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.extend([table, PageBreak()])
    chapters = [
        (1, "System architecture and request path", "VS Code project tree, app.py, then browser at http://127.0.0.1:5000",
         ["app.py", "extensions.py", "auth/", "student/", "moderator/", "admin/"],
         ["Show folders for auth, student, moderator, admin, ai_engine, templates, and static.",
          "Open create_app() in app.py. Point out configuration loading, extension setup, blueprint registration, and database initialization.",
          "Switch to the browser. Trace browser request -> Flask route/blueprint -> model or service -> template or JSON response."],
         "OMSU FindBack is a Flask application organized into blueprints for authentication, student, moderator, and administrator tasks. The app factory loads configuration and initializes database, login, CSRF, rate limiting, and Socket.IO extensions. Most workflows return rendered HTML pages; selected functions use JSON or real-time Socket.IO events.",
         "Start with a chapter title, show the folder tree briefly, zoom into app.py, and finish on the browser. Keep environment files and terminal secrets off-screen."),
        (2, "Authentication and role-based authorization", "auth/routes.py, models.py, then role-specific browser landing page",
         ["auth/routes.py", "models.py", "app.py"],
         ["Show register(): student registration creates role=user and hashes a password through User.set_password().",
          "Show login(): normalized email lookup, password hash check, active-status check, login_user(), and redirect_for_role().",
          "Point out blueprint before_request guards in student, moderator, and admin routes.",
          "Sign into prepared student/moderator/admin accounts separately and show each landing page without exposing credentials."],
         "Authentication uses Flask-Login. Passwords are stored as hashes through Werkzeug, not as plain text. Inactive accounts cannot load through the user loader, and successful sign-in routes according to the stored role. Blueprint guards restrict student, moderator, and administrator routes. Public registration creates a student-level user only; staff privileges are managed by an administrator.",
         "Keep passwords masked. Show code without secret values, then cut to pre-authenticated demo roles and label each role."),
        (3, "Database models and persistence", "models.py, config.py, database/schema.sql; optionally show safe read-only database view",
         ["models.py", "config.py", "database/schema.sql", "app.py"],
         ["Show the SQLAlchemy URI assembled from environment settings and the MySQL/PyMySQL driver, without revealing values.",
          "Walk through User, Report, Claim, Conversation, Message, Notification, AuditLog, and ClaimTransaction relationships.",
          "Explain that app startup calls db.create_all() and seeds empty category/location lists. schema.sql creates/selects the database; it does not define every ORM table.",
          "Show a demo record in the UI or a safe read-only query; describe status lifecycle instead of editing data."],
         "The application uses Flask-SQLAlchemy with MySQL. Models define users, reports, claims, conversations and messages, notifications, audit entries, and handover snapshots. Foreign keys and relationships connect the workflow. On startup, create_all creates missing tables and the app adds starter campus choices when needed. This is not a general migration system, so schema changes need backups and deliberate migrations.",
         "Show model names and selected relationships. If using a database client, use a read-only demo database and avoid contact details or claim evidence."),
        (4, "Student report request and database write", "student/routes.py create_report(), report form, and My reports result",
         ["student/routes.py", "models.py", "config.py", "notification_service.py"],
         ["Show create_report() POST validation: required fields, date parsing, active category/location checks, and error flashes.",
          "Explain photo validation: JPG/PNG/WEBP, image format and dimension checks, UUID filename, and private upload folder.",
          "Show the Report ORM object and database commit; explain staff in-app notifications and optional email after storage.",
          "In the browser, submit a prepared safe demo report, then show its code and Awaiting review status in My reports."],
         "When a student submits a report, the server validates required fields, dates, and active campus choices rather than trusting browser input. If there is a photo, the server verifies its format and dimensions and saves it under a generated filename in private upload storage. SQLAlchemy stores the report and creates staff notifications. The student sees confirmation and a report awaiting human review.",
         "Record the form, relevant route, and resulting status. Use an expendable demo report, no private details, and never open .env."),
        (5, "JSON photo suggestions and AI match ranking", "student/routes.py /student/ai/suggest, ai_engine/image_detection.py and ai_engine/matching.py",
         ["student/routes.py", "ai_engine/image_detection.py", "ai_engine/matching.py", "models.py"],
         ["Explain that /student/ai/suggest is a POST JSON endpoint used by the report form; it validates an uploaded image and rate-limits requests.",
          "Show local YOLO inference on CPU, object labels/confidence/category/color suggestions, and AIRecognitionEvent logging.",
          "Explain the 45% threshold: below it, name/type/category are not auto-filled. Suggestions and matching scores are not ownership verification.",
          "Click Suggest details from photo in a demo form and show the result and UI warning."],
         "Photo analysis runs locally on the application server with the bundled pretrained YOLOv8 Nano model. It detects common object classes and may suggest category and approximate color. Lower-confidence results leave key fields blank. The server records an analysis event, not another copy of the image. Matching compares report details and can use local image embeddings; neither score proves identity or ownership. Moderators still verify claims.",
         "Label the chapter Local AI suggestion - not ownership proof. Show the route and inference code, then the actual form result. Do not imply a custom OMSU-trained model or public REST API."),
        (6, "Moderator decisions, handover transaction, admin analytics", "moderator/routes.py review_report()/review_claim(); admin/routes.py analytics(); moderator queue",
         ["moderator/routes.py", "admin/routes.py", "models.py", "notification_service.py"],
         ["Show report review: approve changes status to Verified report, runs possible-match notifications, and writes an audit entry; reject marks Rejected.",
          "Show claim review: request proof/reject, or approve after verified physical handover. Approval changes report status to Recovered and creates a ClaimTransaction snapshot.",
          "Explain notifications, optional email, audit trail, and administrator claim history.",
          "Show analytics date range, totals, category/location/month grouping, and AI event statistics."],
         "Report approval is separate from claim approval. A moderator first reviews a report; only verified reports are included in matching. A claim is a separate human ownership check. On verified handover, the report is marked Recovered and a transaction snapshot captures the parties, report, evidence, location, and reviewer, while audit and notification records support accountability. Admin analytics aggregate activity for the selected period.",
         "Use only a test claim for any approval. Do not display private evidence fields. End on claim history or analytics with safe demo values; do not edit production records."),
        (7, "Private messaging and notification delivery", "messaging.py Socket.IO handlers, messages/thread.html, notifications.py",
         ["messaging.py", "notifications.py", "models.py", "notification_service.py"],
         ["Explain that an eligible claim creates one Conversation and associated Claim.",
          "Show can_access_conversation(): active user requirement, claimant/report-owner access, and staff access for authorized moderation.",
          "Show join_conversation and send_message: validation, 2,000-character limit, per-minute cap, database persistence, and emission to authorized room.",
          "Show message history JSON route and notification open route; email is optional and in-app notifications persist."],
         "Private chat uses Socket.IO for real-time updates, but each message is also saved to the database. Before joining or sending, the server verifies the active account and conversation access. Messages are length-checked and rate-limited, then delivered to the conversation room and generate notifications. The history endpoint returns JSON, while normal page navigation uses rendered templates. Email is optional; in-app notifications remain available.",
         "Capture code, then a short demo chat between prepared accounts using harmless messages. The project does not use a third-party chat vendor or an unauthenticated public room."),
        (8, "Security configuration and wrap-up", "config.py, app.py security setup, extensions.py, report image route, then browser",
         ["config.py", "app.py", "extensions.py", "templates/base.html"],
         ["Show CSRF setup and POST forms, login/register/AI rate limits, session-cookie flags, and security headers.",
          "Show upload-folder safety check and /report-images/<id>: login required and controlled photo route.",
          "Explain production requirements: strong SECRET_KEY, ALLOWED_HOSTS, shared Redis rate-limit storage, HTTPS, and trusted proxy only when correctly deployed.",
          "Close in browser by showing different role navigation and summarize request -> validation/authorization -> persistence -> response/notification."],
         "Security controls are applied at several layers: CSRF tokens on browser forms, rate limits on sensitive endpoints, hashed passwords, role checks, secure session settings, response headers, and private report-photo storage. Production requires deployment-specific secrets, hosts, and shared rate-limit storage. The workflow is server-validated, persisted, and reflected in the correct role-specific interface.",
         "Never reveal .env, SECRET_KEY, database credentials, SMTP credentials, or real user data. Finish with a clean chapter card."),
    ]
    for chapter in chapters:
        story.extend(backend_chapter(*chapter))
    story.extend([
        para("Final explanation / video close", "Section"),
        para('"In summary, OMSU FindBack combines role-aware Flask pages, MySQL-backed records, optional local image assistance, and authorized human review. Reports and claims are validated on the server, status changes are stored, and the right users receive notifications. AI and match scores support discovery; they never replace ownership verification."', "Quote"),
        para("Accuracy checks before submitting", "Sub"),
        bullet("Call this a Flask web application with server-rendered pages, form POSTs, selected JSON routes, and Socket.IO messaging - not a REST-only backend."),
        bullet("Describe AI as local pretrained object detection and embedding-based matching support, not a custom university-trained model, ownership proof, or guaranteed match."),
        bullet("Describe email as optional and in-app notifications as the persistent feature."),
        bullet("If a route or service cannot be run locally, identify the segment as a code walkthrough rather than a live demonstration."),
    ])
    save_pdf("OMSU_FINDBACK_Back_End_Presentation_Script.pdf", story)


if __name__ == "__main__":
    make_frontend()
    make_backend()
    for name in (
        "OMSU_FINDBACK_Front_End_Presentation_Script.pdf",
        "OMSU_FINDBACK_Back_End_Presentation_Script.pdf",
    ):
        path = OUT / name
        print(f"Created {path} ({path.stat().st_size} bytes)")
