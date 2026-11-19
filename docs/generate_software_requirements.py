from pathlib import Path

from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle


OUT = Path(__file__).resolve().parent
DOCX_PATH = OUT / "OMSU_FINDBACK_Software_Requirements.docx"
PDF_PATH = OUT / "OMSU_FINDBACK_Software_Requirements.pdf"

ROWS = [
    (
        "Operating System (OS)",
        "The documented installation setup uses Windows 10 or Windows 11. Python 3.10 or newer "
        "is specified by the project tutorial. Other server operating systems are not confirmed "
        "by the project's installation documentation.",
    ),
    (
        "Device screen resolution",
        "The interface uses responsive CSS layouts, with breakpoints around 800, 750, 700, 650, "
        "600, and 500 pixels depending on the page. No minimum display resolution is specified. "
        "For comfortable use, a viewport of about 360 CSS pixels wide on mobile or 1280 x 720 "
        "pixels on a computer is recommended; these are usability recommendations, not tested "
        "minimum hardware specifications.",
    ),
    (
        "Web browser",
        "A current browser with HTML5, CSS, JavaScript, cookies, and WebSocket support is needed "
        "to use the web interface and real-time chat. The application is browser-based and does "
        "not require a separately installed OMSU FindBack client.",
    ),
    (
        "Python runtime and packages",
        "Python 3.10 or newer and pip are required to install and run the backend. Install the "
        "project's pinned dependencies from requirements.txt, including Flask 3.1.0, "
        "Flask-SQLAlchemy 3.1.1, Flask-Login 0.6.3, Flask-SocketIO 5.5.1, Flask-WTF 1.2.2, "
        "Flask-Limiter 3.12, PyMySQL 1.1.1, Pillow 11.0.0, and Ultralytics 8.3.40.",
    ),
    (
        "Web application framework",
        "Flask runs the server-side application and serves its pages, routes, and JSON responses. "
        "Jinja2 templates, HTML, CSS, and JavaScript provide the rendered browser interface.",
    ),
    (
        "Database software",
        "A running MySQL server is required, with a database named omsu_findback (or an alternate "
        "database configured through DATABASE_URL). Flask-SQLAlchemy/SQLAlchemy and the PyMySQL "
        "driver connect application models and queries to the database. XAMPP can provide MySQL "
        "for the documented local setup; Apache is optional.",
    ),
    (
        "Application APIs and real-time protocol",
        "The Flask application exposes its own HTTP routes and a JSON endpoint for photo-analysis "
        "suggestions; it does not require credentials for a third-party application API. "
        "Flask-SocketIO provides authenticated real-time chat events and rooms using Socket.IO/"
        "WebSocket-compatible transport.",
    ),
    (
        "AI model and image software",
        "Ultralytics YOLOv8n and the project's yolov8n.pt weights provide local object detection "
        "and image embeddings. Pillow validates and processes uploaded photos. The model runs "
        "on CPU, does not require a GPU, and provides suggestions rather than ownership "
        "verification. The weights file must be present at the configured model path.",
    ),
    (
        "Search engine",
        "No external search-engine software or service (such as Elasticsearch) is required. "
        "Report matching is performed by the application's category, color, name, and optional "
        "image-similarity logic; administrative user lookup uses database queries.",
    ),
    (
        "Development tools",
        "Visual Studio Code is listed in the installation tutorial as the development environment. "
        "XAMPP Control Panel and phpMyAdmin may be used to start and manage the local MySQL "
        "database. These are development/setup tools, not end-user requirements.",
    ),
    (
        "Configuration and secrets",
        "python-dotenv loads local settings from a .env file, including the database connection, "
        "secret key, upload folder, model path, and optional email settings. A strong secret key "
        "and valid database credentials are required for an installation; secrets must not be "
        "committed to source control.",
    ),
    (
        "Optional email service",
        "An SMTP server and its configuration are optional. If configured, the application can "
        "send report, claim, and message email alerts; in-app notifications continue to work "
        "without SMTP.",
    ),
    (
        "Production-only services",
        "A production deployment requires HTTPS and a shared Redis-compatible rate-limit store "
        "configured through RATELIMIT_STORAGE_URI. The production web/Socket.IO server must "
        "support the application's WebSocket connections. These are not needed for a basic "
        "single-process local demonstration.",
    ),
]


def build_docx():
    doc = Document()
    sec = doc.sections[0]
    sec.top_margin = Inches(0.7)
    sec.bottom_margin = Inches(0.7)
    sec.left_margin = Inches(0.75)
    sec.right_margin = Inches(0.75)

    normal = doc.styles["Normal"]
    normal.font.name = "Arial"
    normal.font.size = Pt(10)
    normal.font.color.rgb = RGBColor(51, 65, 85)

    heading = doc.add_paragraph()
    heading.style = doc.styles["Heading 1"]
    heading.add_run("1. SYSTEM REQUIREMENTS")

    subheading = doc.add_paragraph()
    subheading.style = doc.styles["Heading 2"]
    subheading.add_run("3. Software Requirements")

    caption = doc.add_paragraph()
    caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = caption.add_run("Table 2. The software requirements of OMSU FindBack.")
    run.italic = True
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(100, 116, 139)

    table = doc.add_table(rows=1, cols=2)
    table.style = "Table Grid"
    table.autofit = False
    table.columns[0].width = Inches(1.7)
    table.columns[1].width = Inches(5.5)
    for cell, label in zip(table.rows[0].cells, ("Components", "Description")):
        cell.text = label
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        for paragraph in cell.paragraphs:
            for run in paragraph.runs:
                run.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)
                run.font.size = Pt(10)
        shading = cell._tc.get_or_add_tcPr()
        fill = OxmlElement("w:shd")
        fill.set(qn("w:fill"), "1E3A5F")
        shading.append(fill)

    for component, description in ROWS:
        cells = table.add_row().cells
        cells[0].text = component
        cells[1].text = description
        for cell in cells:
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP
        for paragraph in cells[0].paragraphs:
            paragraph.paragraph_format.space_after = Pt(2)
            for run in paragraph.runs:
                run.bold = True
                run.font.size = Pt(9)
                run.font.color.rgb = RGBColor(30, 58, 95)
        for paragraph in cells[1].paragraphs:
            paragraph.paragraph_format.space_after = Pt(2)
            for run in paragraph.runs:
                run.font.size = Pt(9)
    doc.save(DOCX_PATH)


def build_pdf():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="ReqTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=17,
        leading=21,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=8,
    ))
    styles.add(ParagraphStyle(
        name="ReqSubTitle",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#1E3A5F"),
        spaceBefore=4,
        spaceAfter=8,
    ))
    styles.add(ParagraphStyle(
        name="ReqCaption",
        parent=styles["BodyText"],
        fontSize=9,
        leading=12,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#64748B"),
        spaceAfter=8,
    ))
    styles.add(ParagraphStyle(
        name="ReqCell",
        parent=styles["BodyText"],
        fontSize=8,
        leading=10.2,
        textColor=colors.HexColor("#334155"),
    ))
    styles.add(ParagraphStyle(
        name="ReqHeader",
        parent=styles["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
    ))
    styles.add(ParagraphStyle(
        name="ReqComponent",
        parent=styles["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10.2,
        textColor=colors.HexColor("#1E3A5F"),
    ))

    data = [[
        Paragraph("Components", styles["ReqHeader"]),
        Paragraph("Description", styles["ReqHeader"]),
    ]]
    for component, description in ROWS:
        data.append([
            Paragraph(component, styles["ReqComponent"]),
            Paragraph(description, styles["ReqCell"]),
        ])

    table = Table(data, colWidths=[1.55*inch, 5.75*inch], repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A5F")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    story = [
        Paragraph("1. SYSTEM REQUIREMENTS", styles["ReqTitle"]),
        Paragraph("3. Software Requirements", styles["ReqSubTitle"]),
        Paragraph("Table 2. The software requirements of OMSU FindBack.", styles["ReqCaption"]),
        table,
    ]
    pdf = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=letter,
        leftMargin=0.65*inch,
        rightMargin=0.65*inch,
        topMargin=0.65*inch,
        bottomMargin=0.65*inch,
        title="OMSU FindBack System Requirements - Software",
        author="OMSU FindBack",
    )
    pdf.build(story)


build_docx()
build_pdf()
print(DOCX_PATH)
print(PDF_PATH)
