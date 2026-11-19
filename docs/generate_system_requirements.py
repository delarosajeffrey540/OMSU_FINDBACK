from pathlib import Path

from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


OUT = Path(__file__).resolve().parent
DOCX_PATH = OUT / "OMSU_FINDBACK_System_Requirements.docx"
PDF_PATH = OUT / "OMSU_FINDBACK_System_Requirements.pdf"

ROWS = [
    (
        "Mobile",
        "Optional client device. Students and staff can access OMSU FindBack through a modern "
        "mobile web browser to browse reports, submit reports and claims, view notifications, "
        "and message users. A mobile application is not required.",
    ),
    (
        "Laptop",
        "Client device for students, moderators, and administrators to use the web interface. "
        "A laptop can also host the application and MySQL database for local development or a "
        "demonstration when the required software is installed.",
    ),
    (
        "Desktop",
        "Alternative client device for using the web interface. A desktop computer can host "
        "the Flask application, MySQL database, and private report-photo storage for a local "
        "installation or campus deployment.",
    ),
    (
        "Camera",
        "Optional. A built-in or external camera can capture item photos for report submissions "
        "and AI-assisted suggestions. Users may instead upload an existing image, so a separate "
        "camera is not required.",
    ),
    (
        "Printer",
        "Not required. OMSU FindBack provides its workflows through the web interface and does "
        "not require printed forms or receipts. Users may use browser printing if needed, but "
        "printing is outside the system's core functions.",
    ),
    (
        "Application / database host",
        "Required to run the system: a computer or server that can run the Python/Flask "
        "application and MySQL database. For a local demonstration, one computer may host both; "
        "a dedicated GPU is not required because the configured YOLOv8n image analysis runs on CPU.",
    ),
    (
        "Persistent storage",
        "Required on the host for the MySQL database and private uploaded report photos "
        "(instance/uploads by default). Capacity should be selected according to expected "
        "accounts, records, and image uploads; this project does not define a tested minimum.",
    ),
    (
        "Network connection",
        "Required for browser clients to reach the application host. A local demonstration may "
        "use the same computer or a local network; multi-user campus access requires a suitable "
        "LAN or internet connection. Real-time messaging also requires connectivity to the "
        "Socket.IO-enabled application server.",
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
    subheading.add_run("2. Hardware Requirements")

    caption = doc.add_paragraph()
    caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = caption.add_run("Table 1. The hardware requirements of OMSU FindBack.")
    run.italic = True
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(100, 116, 139)

    table = doc.add_table(rows=1, cols=2)
    table.style = "Table Grid"
    table.autofit = False
    table.columns[0].width = Inches(1.55)
    table.columns[1].width = Inches(5.65)
    header = table.rows[0].cells
    header[0].text = "Components"
    header[1].text = "Description"
    for cell in header:
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        for paragraph in cell.paragraphs:
            for run in paragraph.runs:
                run.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)
                run.font.size = Pt(10)
        shading = cell._tc.get_or_add_tcPr()
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        fill = OxmlElement("w:shd")
        fill.set(qn("w:fill"), "1E3A5F")
        shading.append(fill)

    for component, description in ROWS:
        cells = table.add_row().cells
        cells[0].text = component
        cells[1].text = description
        cells[0].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP
        cells[1].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP
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

    note = doc.add_paragraph()
    note.paragraph_format.space_before = Pt(8)
    run = note.add_run(
        "Note: The project documentation specifies operating-system and software prerequisites "
        "but does not state tested minimum CPU, RAM, or disk-capacity values. Actual host sizing "
        "should be determined from deployment scale and expected photo volume."
    )
    run.italic = True
    run.font.size = Pt(8.5)
    run.font.color.rgb = RGBColor(100, 116, 139)
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
        fontSize=8.5,
        leading=11,
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
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#1E3A5F"),
    ))
    styles.add(ParagraphStyle(
        name="ReqNote",
        parent=styles["BodyText"],
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#64748B"),
        spaceBefore=8,
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

    table = Table(data, colWidths=[1.45*inch, 5.85*inch], repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A5F")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))

    story = [
        Paragraph("1. SYSTEM REQUIREMENTS", styles["ReqTitle"]),
        Paragraph("2. Hardware Requirements", styles["ReqSubTitle"]),
        Paragraph("Table 1. The hardware requirements of OMSU FindBack.", styles["ReqCaption"]),
        table,
        Paragraph(
            "Note: The project documentation specifies operating-system and software "
            "prerequisites but does not state tested minimum CPU, RAM, or disk-capacity values. "
            "Actual host sizing should be determined from deployment scale and expected photo volume.",
            styles["ReqNote"],
        ),
    ]
    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=letter,
        leftMargin=0.65*inch,
        rightMargin=0.65*inch,
        topMargin=0.65*inch,
        bottomMargin=0.65*inch,
        title="OMSU FindBack System Requirements - Hardware",
        author="OMSU FindBack",
    )
    doc.build(story)


build_docx()
build_pdf()
print(DOCX_PATH)
print(PDF_PATH)
