from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image as PdfImage,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)


OUT = Path(__file__).resolve().parent
FIGURE_PATH = OUT / "OMSU_FINDBACK_Technology_Stack_Diagram.png"
DOCX_PATH = OUT / "OMSU_FINDBACK_Technology_Stack_Section.docx"
PDF_PATH = OUT / "OMSU_FINDBACK_Technology_Stack_Section.pdf"

INTRO = (
    "This section summarizes the technologies that implement OMSU FindBack, a campus "
    "lost-and-found web application. It describes the presentation, server, real-time "
    "communication, data, and local image-analysis stack, and explains why each "
    "technology fits the system's workflows. SMTP email and shared Redis rate-limit "
    "storage are optional integration points, not required services for local use."
)

TECHNOLOGIES = [
    (
        "Python",
        "Python is the application's implementation language and has mature web, database, "
        "and computer-vision libraries.",
        "It lets the application, report/claim workflows, and local image-analysis code run "
        "in one maintainable server-side codebase.",
    ),
    (
        "Flask 3.1.0",
        "The project uses Flask's small, extensible web framework and blueprint structure "
        "for authentication, student, moderator, administrator, messaging, and notification routes.",
        "It keeps role-specific workflows modular while serving pages and JSON endpoints "
        "from the same application.",
    ),
    (
        "Jinja2, HTML, CSS, and JavaScript",
        "Flask renders the project's Jinja2 templates, with static CSS and JavaScript for "
        "browser presentation and interaction.",
        "Server-rendered pages provide the dashboards, report and claim forms, queues, and "
        "admin views without requiring a separate single-page application service.",
    ),
    (
        "Flask extensions for identity and request protection",
        "Flask-Login (0.6.3), Flask-WTF / CSRFProtect (1.2.2), and Flask-Limiter (3.12) "
        "are already declared and initialized in the project.",
        "They provide signed-in sessions and role checks, CSRF protection for browser forms, "
        "and rate limits for sensitive endpoints such as login, registration, and AI suggestions.",
    ),
    (
        "Flask-SocketIO 5.5.1 and simple-websocket 1.1.0",
        "The application uses Socket.IO rooms and events for private claim conversations; "
        "simple-websocket is included as a transport dependency.",
        "Messages can be delivered to an authorized conversation in real time, while message "
        "history remains stored in the database.",
    ),
    (
        "Flask-SQLAlchemy 3.1.1, SQLAlchemy, and PyMySQL 1.1.1",
        "Flask-SQLAlchemy integrates SQLAlchemy's ORM with Flask, and PyMySQL is the configured "
        "MySQL driver.",
        "The models express relationships among users, reports, claims, handover transactions, "
        "messages, notifications, and audit records; ORM sessions handle database operations.",
    ),
    (
        "MySQL",
        "The project is configured for a relational MySQL database named omsu_findback "
        "(with an optional DATABASE_URL override).",
        "Relational tables and foreign keys keep accounts, report/claim lifecycles, private "
        "conversations, notifications, and review history connected consistently.",
    ),
    (
        "Ultralytics YOLOv8n (8.3.40) and bundled weights",
        "The project includes a local yolov8n.pt model and uses the Ultralytics API for object "
        "detection and image embeddings; inference is configured for CPU.",
        "It can suggest visible object labels/categories and contribute image similarity to "
        "candidate matches without sending report photos to an AI vendor. The pretrained model "
        "is generic COCO-based, not trained on OMSU items, and does not verify ownership.",
    ),
    (
        "Pillow 11.0.0",
        "Pillow is used to open, validate, and inspect uploaded JPG, PNG, and WEBP photos, "
        "and to estimate a dominant color within a detected object crop.",
        "Image format, dimensions, and size checks reject unsupported or oversized uploads "
        "before they are used by report and suggestion workflows.",
    ),
    (
        "Private local upload storage",
        "Report photographs are saved under instance/uploads by default, outside Flask's "
        "public static directory.",
        "Keeping image files separate from public assets allows the application to serve "
        "report images through an authenticated route instead of exposing an open upload URL.",
    ),
    (
        "python-dotenv 1.0.1",
        "Configuration is loaded from a local .env file, with environment-variable overrides "
        "for database, secret, upload, model, email, and deployment settings.",
        "Operators can configure secrets and environment-specific services without embedding "
        "credentials in application source code.",
    ),
]

OPTIONAL_NOTE = (
    "Optional / deployment integrations: SMTP is used only when mail settings are provided; "
    "in-app notifications still work without it. Production configuration requires a shared "
    "Redis-compatible rate-limit store rather than the in-memory development default. This "
    "workspace does not establish that either service is currently configured or deployed."
)


def load_font(size, bold=False):
    choices = (
        [r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\arialbd.ttf"]
        if bold else
        [r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\arial.ttf"]
    )
    for path in choices:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def draw_diagram():
    image = Image.new("RGB", (1800, 980), "#F8FAFC")
    draw = ImageDraw.Draw(image)
    title_font = load_font(38, True)
    subtitle_font = load_font(20)
    label_font = load_font(22, True)
    body_font = load_font(18)
    small_font = load_font(16)
    draw.text((900, 42), "OMSU FindBack Technology Stack", fill="#0F172A", font=title_font, anchor="mm")
    draw.text((900, 86), "Application components and the main runtime/data paths", fill="#64748B", font=subtitle_font, anchor="mm")

    def card(box, title, lines, fill, border):
        x1, y1, x2, y2 = box
        draw.rounded_rectangle(box, radius=18, fill=fill, outline=border, width=3)
        draw.rounded_rectangle((x1, y1, x2, y1+52), radius=18, fill=border)
        draw.rectangle((x1, y1+34, x2, y1+52), fill=border)
        draw.text((x1+18, y1+25), title, fill="#FFFFFF", font=label_font, anchor="lm")
        y = y1 + 76
        for line in lines:
            draw.text((x1+18, y), line, fill="#334155", font=body_font)
            y += 31

    def arrow(start, end, color="#64748B"):
        draw.line((start, end), fill=color, width=5)
        ex, ey = end
        draw.polygon([(ex, ey), (ex-13, ey-8), (ex-13, ey+8)], fill=color)

    card((70, 145, 430, 315), "END USERS", [
        "Students / reporters",
        "Moderators and administrators",
    ], "#DBEAFE", "#2563EB")
    card((540, 145, 1000, 315), "WEB PRESENTATION", [
        "Flask + Jinja2 templates",
        "HTML / CSS / JavaScript",
    ], "#E0F2FE", "#0284C7")
    card((1110, 145, 1720, 315), "APPLICATION SERVER", [
        "Python + Flask 3.1.0 blueprints",
        "Auth, student, moderator, admin",
        "Messaging and notification routes",
    ], "#DCFCE7", "#16A34A")
    arrow((430, 230), (540, 230))
    arrow((1000, 230), (1110, 230))

    card((150, 405, 650, 595), "CROSS-CUTTING EXTENSIONS", [
        "Flask-Login: sessions / role checks",
        "Flask-WTF: CSRF  |  Flask-Limiter",
    ], "#F1F5F9", "#475569")
    card((740, 405, 1230, 595), "REAL-TIME MESSAGING", [
        "Flask-SocketIO + simple-websocket",
        "Private claim conversation rooms",
    ], "#E0F2FE", "#0284C7")
    card((1320, 405, 1690, 595), "LOCAL AI / IMAGES", [
        "Ultralytics YOLOv8n (CPU)",
        "Pillow validation / color estimate",
    ], "#FEF3C7", "#D97706")
    arrow((1315, 315), (420, 405))
    arrow((1410, 315), (985, 405))
    arrow((1510, 315), (1505, 405))

    card((220, 690, 790, 865), "DATA ACCESS", [
        "Flask-SQLAlchemy / SQLAlchemy ORM",
        "PyMySQL database driver",
    ], "#F3E8FF", "#9333EA")
    card((980, 690, 1370, 865), "RELATIONAL DATABASE", [
        "MySQL: omsu_findback",
        "Users, reports, claims, chat, audit",
    ], "#EDE9FE", "#7C3AED")
    card((1460, 690, 1730, 865), "PRIVATE FILES", [
        "instance/uploads/",
        "Authenticated image access",
    ], "#FFEDD5", "#EA580C")
    draw.line([(1720, 230), (1750, 230), (1750, 640), (520, 640), (520, 690)], fill="#64748B", width=5)
    draw.polygon([(520, 690), (512, 677), (528, 677)], fill="#64748B")
    arrow((790, 780), (980, 780))
    arrow((985, 595), (1130, 690))
    arrow((1505, 595), (1580, 690))

    draw.rounded_rectangle((220, 895, 1730, 955), radius=14, fill="#FFFFFF", outline="#94A3B8", width=2)
    draw.text((245, 925), "OPTIONAL / DEPLOYMENT:", fill="#0F172A", font=small_font, anchor="lm")
    draw.text((535, 925), "SMTP email (if configured)  |  Shared Redis rate-limit storage for production", fill="#475569", font=small_font, anchor="lm")
    image.save(FIGURE_PATH, optimize=True)


def build_docx():
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(0.65)
    section.bottom_margin = Inches(0.65)
    section.left_margin = Inches(0.8)
    section.right_margin = Inches(0.8)

    normal = doc.styles["Normal"]
    normal.font.name = "Arial"
    normal.font.size = Pt(10)
    normal.font.color.rgb = RGBColor(51, 65, 85)
    normal.paragraph_format.space_after = Pt(6)
    for style_name, size, color in [
        ("Title", 24, "0F172A"),
        ("Heading 1", 17, "0F172A"),
        ("Heading 2", 12, "1D4ED8"),
    ]:
        style = doc.styles[style_name]
        style.font.name = "Arial"
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = RGBColor.from_string(color)

    title = doc.add_paragraph(style="Title")
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.add_run("Technology Stack")

    doc.add_heading("1. Introductory Statement", level=1)
    doc.add_paragraph(INTRO)

    doc.add_heading("2. Tech Stack Diagram", level=1)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(FIGURE_PATH), width=Inches(6.7))
    caption = doc.add_paragraph(
        "Figure 1. OMSU FindBack technology stack showing the browser, Flask application, "
        "supporting services, persistence, and optional integrations."
    )
    caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in caption.runs:
        run.italic = True
        run.font.size = Pt(9)
        run.font.color.rgb = RGBColor(100, 116, 139)

    doc.add_heading("3. Technology Breakdown", level=1)
    doc.add_paragraph(
        "The choices below reflect the dependencies, application code, and configuration "
        "present in this project. The benefits describe how each component supports the "
        "implemented lost-and-found workflows."
    )
    for name, why, benefit in TECHNOLOGIES:
        doc.add_heading(name, level=2)
        p = doc.add_paragraph()
        r = p.add_run("Why it was chosen: ")
        r.bold = True
        p.add_run(why)
        p = doc.add_paragraph()
        r = p.add_run("How it benefits the system: ")
        r.bold = True
        p.add_run(benefit)

    doc.add_heading("Optional and deployment-specific integrations", level=2)
    doc.add_paragraph(OPTIONAL_NOTE)
    doc.save(DOCX_PATH)


def build_pdf():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="DocTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=23,
        leading=28,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=12,
    ))
    styles.add(ParagraphStyle(
        name="SectionHead",
        parent=styles["Heading1"],
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=12,
        spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        name="TechHead",
        parent=styles["Heading2"],
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#1D4ED8"),
        spaceBefore=8,
        spaceAfter=3,
    ))
    styles.add(ParagraphStyle(
        name="BodyCopy",
        parent=styles["BodyText"],
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#334155"),
        spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        name="Caption",
        parent=styles["BodyText"],
        fontSize=8,
        leading=11,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#64748B"),
        spaceAfter=8,
    ))
    story = [
        Paragraph("Technology Stack", styles["DocTitle"]),
        Paragraph("1. Introductory Statement", styles["SectionHead"]),
        Paragraph(INTRO, styles["BodyCopy"]),
        Paragraph("2. Tech Stack Diagram", styles["SectionHead"]),
        PdfImage(str(FIGURE_PATH), width=7.15*inch, height=7.15*inch*980/1800),
        Paragraph(
            "Figure 1. OMSU FindBack technology stack showing the browser, Flask application, "
            "supporting services, persistence, and optional integrations.",
            styles["Caption"],
        ),
        Paragraph("3. Technology Breakdown", styles["SectionHead"]),
        Paragraph(
            "The choices below reflect the dependencies, application code, and configuration "
            "present in this project. The benefits describe how each component supports the "
            "implemented lost-and-found workflows.",
            styles["BodyCopy"],
        ),
    ]
    for name, why, benefit in TECHNOLOGIES:
        story.append(Paragraph(name, styles["TechHead"]))
        story.append(Paragraph(f"<b>Why it was chosen:</b> {why}", styles["BodyCopy"]))
        story.append(Paragraph(f"<b>How it benefits the system:</b> {benefit}", styles["BodyCopy"]))
    story.extend([
        Paragraph("Optional and deployment-specific integrations", styles["TechHead"]),
        Paragraph(OPTIONAL_NOTE, styles["BodyCopy"]),
    ])
    pdf = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=letter,
        rightMargin=0.72*inch,
        leftMargin=0.72*inch,
        topMargin=0.62*inch,
        bottomMargin=0.62*inch,
        title="OMSU FindBack Technology Stack",
        author="OMSU FindBack",
    )
    pdf.build(story)


draw_diagram()
build_docx()
build_pdf()
print(DOCX_PATH)
print(PDF_PATH)
print(FIGURE_PATH)
