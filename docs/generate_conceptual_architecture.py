from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen import canvas


OUTPUT_DIR = Path(__file__).resolve().parent
WIDTH, HEIGHT = 1600, 1000


def svg_box(x, y, w, h, title, lines, fill, stroke="#1E293B", title_fill=None):
    title_fill = title_fill or fill
    text = [
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{fill}" stroke="{stroke}" stroke-width="2"/>',
        f'<rect x="{x}" y="{y}" width="{w}" height="46" rx="14" fill="{title_fill}"/>',
        f'<path d="M {x} {y+46} H {x+w}" stroke="{stroke}" stroke-width="2"/>',
        f'<text x="{x+16}" y="{y+30}" font-size="18" font-weight="700" fill="#FFFFFF">{escape(title)}</text>',
    ]
    ty = y + 72
    for line in lines:
        text.append(
            f'<text x="{x+16}" y="{ty}" font-size="15" fill="#334155">{escape(line)}</text>'
        )
        ty += 25
    return "\n".join(text)


def svg_arrow(x1, y1, x2, y2, label="", dashed=False):
    dash = ' stroke-dasharray="7 5"' if dashed else ""
    parts = [
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#64748B" stroke-width="3"{dash} marker-end="url(#arrow)"/>'
    ]
    if label:
        mx, my = (x1 + x2) // 2, (y1 + y2) // 2 - 8
        parts.append(
            f'<rect x="{mx-55}" y="{my-16}" width="110" height="24" rx="8" fill="#FFFFFF" fill-opacity="0.92"/>'
        )
        parts.append(
            f'<text x="{mx}" y="{my+1}" text-anchor="middle" font-size="12" font-weight="700" fill="#475569">{escape(label)}</text>'
        )
    return "\n".join(parts)


svg = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
<defs>
  <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
    <path d="M0,0 L0,6 L9,3 z" fill="#64748B"/>
  </marker>
  <style>
    text {{ font-family: Arial, Helvetica, sans-serif; }}
  </style>
</defs>
<rect width="{WIDTH}" height="{HEIGHT}" fill="#F8FAFC"/>
<text x="800" y="58" text-anchor="middle" font-size="34" font-weight="800" fill="#0F172A">OMSU FindBack - Conceptual Architecture</text>
<text x="800" y="88" text-anchor="middle" font-size="16" fill="#64748B">Lost-and-found reporting, verification, claim, messaging, and administration</text>
''']

svg.append(svg_arrow(185, 520, 280, 520, "HTTPS"))
svg.append(svg_arrow(555, 520, 660, 520, "HTTP/WebSocket"))
svg.append(svg_arrow(980, 520, 1120, 520, "SQLAlchemy"))
svg.append(svg_arrow(1240, 520, 1240, 655, "SMTP", True))
svg.append(svg_arrow(760, 650, 760, 735, "Image + model"))
svg.append(svg_arrow(760, 735, 760, 650, "Results", True))
svg.append(svg_arrow(535, 650, 535, 735, "Read/write"))
svg.append(svg_arrow(535, 735, 535, 650, "Files", True))

svg.append(svg_box(40, 410, 145, 220, "ACTORS", [
    "Student / Reporter",
    "Moderator",
    "Administrator",
], "#E2E8F0", "#334155", "#475569"))

svg.append(svg_box(280, 390, 275, 260, "CLIENT LAYER", [
    "Browser / responsive UI",
    "Jinja2 HTML templates",
    "CSS and JavaScript",
    "Flask-Login session",
    "Socket.IO real-time chat",
], "#DBEAFE", "#2563EB", "#2563EB"))

svg.append(svg_box(660, 330, 320, 360, "FLASK APPLICATION", [
    "Authentication blueprint",
    "Student workflow blueprint",
    "Moderator queue blueprint",
    "Administrator blueprint",
    "Messaging + notifications",
    "CSRF, login, rate limits",
    "Security headers",
], "#DCFCE7", "#16A34A", "#15803D"))

svg.append(svg_box(1120, 390, 240, 260, "DATA PERSISTENCE", [
    "MySQL: omsu_findback",
    "SQLAlchemy / Flask-SQLAlchemy",
    "Users, reports, claims",
    "Transactions, audit logs",
    "Conversations, messages",
    "Notifications, AI events",
], "#F3E8FF", "#9333EA", "#9333EA"))

svg.append(svg_box(660, 735, 320, 170, "LOCAL AI ENGINE", [
    "Ultralytics YOLOv8n",
    "Object label, category, color",
    "Image embeddings",
    "Cosine visual similarity",
    "CPU inference",
], "#FEF3C7", "#D97706", "#D97706"))

svg.append(svg_box(360, 735, 350, 170, "PRIVATE UPLOAD STORAGE", [
    "instance/uploads/",
    "JPG, PNG, WEBP only",
    "Maximum 5 MB / 25 MP",
    "Authenticated report-image route",
], "#FFEDD5", "#EA580C", "#EA580C"))

svg.append(svg_box(1120, 735, 240, 170, "NOTIFICATION CHANNEL", [
    "In-app notifications",
    "Optional SMTP email",
    "Socket.IO message events",
    "Match and claim alerts",
], "#E0F2FE", "#0284C7", "#0284C7"))

svg.append(svg_box(40, 735, 145, 170, "STAFF ACTION", [
    "Verify reports",
    "Review claims",
    "Complete handover",
    "Manage users/catalogs",
], "#FEE2E2", "#DC2626", "#DC2626"))

svg.append(svg_arrow(185, 820, 360, 820, "Moderation"))

svg.append('''<rect x="40" y="160" width="1520" height="150" rx="18" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="2"/>
<text x="70" y="195" font-size="18" font-weight="700" fill="#0F172A">Primary User Journey</text>
<text x="70" y="230" font-size="15" fill="#334155">1. Register/Login</text>
<text x="70" y="260" font-size="15" fill="#334155">2. Submit Lost/Found report + optional photo</text>
<text x="250" y="230" font-size="15" fill="#334155">3. Moderator verifies report</text>
<text x="250" y="260" font-size="15" fill="#334155">4. AI suggests matches; claimant submits claim</text>
<text x="510" y="230" font-size="15" fill="#334155">5. Private conversation and proof review</text>
<text x="510" y="260" font-size="15" fill="#334155">6. SSG Office handover verification</text>
<text x="770" y="230" font-size="15" fill="#334155">7. Create immutable claim transaction</text>
<text x="770" y="260" font-size="15" fill="#334155">8. Report becomes recovered / Already claimed</text>
<text x="1060" y="230" font-size="15" fill="#334155">9. Notifications and audit trail</text>
<text x="1060" y="260" font-size="15" fill="#334155">10. Admin manages accounts and catalogs</text>
''')

svg.append('''<rect x="1368" y="390" width="192" height="260" rx="14" fill="#FFFFFF" stroke="#64748B" stroke-width="2"/>
<text x="1388" y="425" font-size="16" font-weight="700" fill="#0F172A">Cross-cutting Concerns</text>
<text x="1388" y="460" font-size="14" fill="#334155">• Role-based access</text>
<text x="1388" y="490" font-size="14" fill="#334155">• Session security</text>
<text x="1388" y="520" font-size="14" fill="#334155">• CSRF protection</text>
<text x="1388" y="550" font-size="14" fill="#334155">• Rate limiting</text>
<text x="1388" y="580" font-size="14" fill="#334155">• Upload validation</text>
<text x="1388" y="610" font-size="14" fill="#334155">• Audit logging</text>
''')

svg.append('</svg>')
(OUTPUT_DIR / "OMSU_FINDBACK_Conceptual_Architecture.svg").write_text("\n".join(svg), encoding="utf-8")


pdf_path = OUTPUT_DIR / "OMSU_FINDBACK_Conceptual_Architecture.pdf"
c = canvas.Canvas(str(pdf_path), pagesize=landscape(letter))
page_w, page_h = landscape(letter)
c.setFillColor(colors.HexColor("#F8FAFC"))
c.rect(0, 0, page_w, page_h, fill=1, stroke=0)
c.setFillColor(colors.HexColor("#0F172A"))
c.setFont("Helvetica-Bold", 20)
c.drawCentredString(page_w / 2, page_h - 36, "OMSU FindBack - Conceptual Architecture")
c.setFont("Helvetica", 9)
c.drawCentredString(page_w / 2, page_h - 52, "Lost-and-found reporting, verification, claim, messaging, and administration")

def pdf_box(x, y, w, h, title, lines, fill):
    c.setFillColor(colors.HexColor(fill))
    c.roundRect(x, y, w, h, 8, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#1E293B"))
    c.roundRect(x, y + h - 28, w, 28, 8, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(x + 8, y + h - 18, title)
    c.setFillColor(colors.HexColor("#334155"))
    c.setFont("Helvetica", 8)
    ty = y + h - 45
    for line in lines:
        c.drawString(x + 8, ty, line)
        ty -= 14

def pdf_arrow(x1, y1, x2, y2, label=""):
    c.setStrokeColor(colors.HexColor("#64748B"))
    c.setLineWidth(1.5)
    c.line(x1, y1, x2, y2)
    c.setFillColor(colors.HexColor("#64748B"))
    c.circle(x2, y2, 3, fill=1, stroke=0)
    if label:
        c.setFillColor(colors.HexColor("#475569"))
        c.setFont("Helvetica-Bold", 7)
        c.drawCentredString((x1+x2)/2, (y1+y2)/2+5, label)

pdf_box(20, 285, 80, 130, "ACTORS", ["Student / Reporter", "Moderator", "Administrator"], "#E2E8F0")
pdf_box(130, 285, 150, 130, "CLIENT LAYER", ["Browser / responsive UI", "Jinja2 HTML templates", "Session + Socket.IO"], "#DBEAFE")
pdf_box(310, 250, 210, 165, "FLASK APPLICATION", ["Auth, Student, Moderator", "Admin, Messaging, Notifications", "CSRF, login, rate limits", "Security headers"], "#DCFCE7")
pdf_box(550, 285, 150, 130, "DATA PERSISTENCE", ["MySQL: omsu_findback", "Flask-SQLAlchemy", "Users, reports, claims", "Transactions, audit, chat"], "#F3E8FF")
pdf_box(310, 70, 210, 105, "LOCAL AI ENGINE", ["YOLOv8n", "Object, category, color", "Image embeddings", "Cosine matching"], "#FEF3C7")
pdf_box(130, 70, 150, 105, "PRIVATE UPLOAD STORAGE", ["instance/uploads/", "JPG, PNG, WEBP", "5 MB / 25 MP limits"], "#FFEDD5")
pdf_box(550, 70, 150, 105, "NOTIFICATION CHANNEL", ["In-app notifications", "Optional SMTP email", "Socket.IO messages"], "#E0F2FE")
pdf_box(20, 70, 80, 105, "STAFF ACTION", ["Verify and review", "Handover at SSG", "User/catalog control"], "#FEE2E2")

pdf_arrow(100, 350, 130, 350, "HTTPS")
pdf_arrow(280, 350, 310, 350, "HTTP/WebSocket")
pdf_arrow(520, 350, 550, 350, "SQLAlchemy")
pdf_arrow(415, 250, 415, 175, "Image / results")
pdf_arrow(205, 285, 205, 175, "Upload / files")
pdf_arrow(625, 285, 625, 175, "Notifications")

c.setFillColor(colors.HexColor("#FFFFFF"))
c.roundRect(20, 430, 680, 72, 8, fill=1, stroke=1)
c.setFillColor(colors.HexColor("#0F172A"))
c.setFont("Helvetica-Bold", 10)
c.drawString(32, 485, "PRIMARY USER JOURNEY")
c.setFillColor(colors.HexColor("#334155"))
c.setFont("Helvetica", 8)
c.drawString(32, 467, "1 Report Lost/Found + photo  ->  2 Moderator verifies  ->  3 AI matches")
c.drawString(32, 452, "4 Student claims + proof  ->  5 Private chat/review  ->  6 SSG handover verification")
c.drawString(32, 437, "7 Claim transaction/audit  ->  8 Recovered/Already claimed  ->  9 Admin controls")

c.setTitle("OMSU FindBack Conceptual Architecture")
c.setAuthor("OMSU FindBack")
c.save()

print((OUTPUT_DIR / "OMSU_FINDBACK_Conceptual_Architecture.svg"))
print(pdf_path)
