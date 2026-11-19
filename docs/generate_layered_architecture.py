from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen import canvas


OUTPUT_DIR = Path(__file__).resolve().parent
W, H = 1600, 1000


def layer(x, y, w, h, title, color, stroke, items):
    parts = [
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="{color}" stroke="{stroke}" stroke-width="3"/>',
        f'<rect x="{x}" y="{y}" width="260" height="{h}" rx="16" fill="{stroke}" opacity="0.96"/>',
        f'<text x="{x+130}" y="{y+h/2-10}" text-anchor="middle" font-size="22" font-weight="800" fill="#FFFFFF">{escape(title)}</text>',
    ]
    start_x = x + 290
    card_w = (w - 320) // len(items)
    for index, (name, detail) in enumerate(items):
        cx = start_x + index * card_w
        parts.extend([
            f'<rect x="{cx}" y="{y+25}" width="{card_w-15}" height="{h-50}" rx="12" fill="#FFFFFF" fill-opacity="0.94" stroke="{stroke}" stroke-width="1.5"/>',
            f'<text x="{cx+12}" y="{y+52}" font-size="16" font-weight="700" fill="#0F172A">{escape(name)}</text>',
        ])
        ty = y + 78
        for line in detail:
            parts.append(
                f'<text x="{cx+12}" y="{ty}" font-size="13" fill="#334155">{escape(line)}</text>'
            )
            ty += 21
    return parts


svg = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
  <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
    <path d="M0,0 L0,6 L9,3 z" fill="#64748B"/>
  </marker>
  <style>text {{ font-family: Arial, Helvetica, sans-serif; }}</style>
</defs>
<rect width="{W}" height="{H}" fill="#F8FAFC"/>
<text x="800" y="52" text-anchor="middle" font-size="34" font-weight="800" fill="#0F172A">OMSU FindBack - Layered Architecture</text>
<text x="800" y="82" text-anchor="middle" font-size="16" fill="#64748B">Five application layers plus shared cross-cutting infrastructure</text>
''']

parts = []
parts += layer(50, 120, 1500, 145, "PRESENTATION LAYER", "#DBEAFE", "#2563EB", [
    ("Actors", ["Student / Reporter", "Moderator", "Administrator"]),
    ("Web Interface", ["Jinja2 HTML templates", "Responsive CSS", "JavaScript interactions"]),
    ("Real-Time UI", ["Socket.IO client", "Inbox and message thread"]),
    ("Forms", ["Login / registration", "Lost / found reports", "Claims / admin controls"]),
])
parts += layer(50, 285, 1500, 145, "APPLICATION / ROUTE LAYER", "#DCFCE7", "#16A34A", [
    ("Auth Blueprint", ["Login and logout", "Registration", "Role redirection"]),
    ("Student Blueprint", ["Dashboard and reports", "AI suggestions", "Matching and claims"]),
    ("Staff Blueprints", ["Moderator queue/items", "Admin users/catalog/analytics"]),
    ("Messaging & Notifications", ["Conversation access", "Socket.IO events", "In-app / SMTP alerts"]),
])
parts += layer(50, 450, 1500, 145, "BUSINESS / DOMAIN LAYER", "#FEF3C7", "#D97706", [
    ("Report Workflow", ["Submission and verification", "Status transitions"]),
    ("Claim Workflow", ["Proof submission", "SSG Office handover", "Transaction recording"]),
    ("AI Services", ["YOLOv8 object detection", "Category / color suggestions"]),
    ("Matching Service", ["Attribute scoring", "Cosine image similarity"]),
])
parts += layer(50, 615, 1500, 145, "DATA ACCESS / MODEL LAYER", "#F3E8FF", "#9333EA", [
    ("ORM Models", ["SQLAlchemy models", "Relationships and constraints"]),
    ("Repositories", ["Flask-SQLAlchemy queries", "Session commits"]),
    ("Domain Records", ["Users, reports, claims", "Transactions, conversations"]),
    ("Audit & Events", ["AuditLog", "AIRecognitionEvent", "Notifications"]),
])
parts += layer(50, 780, 1500, 145, "INFRASTRUCTURE LAYER", "#E0F2FE", "#0284C7", [
    ("MySQL", ["omsu_findback database", "PyMySQL connection"]),
    ("File Storage", ["instance/uploads/", "JPG / PNG / WEBP"]),
    ("External Services", ["SMTP email", "YOLOv8n model"]),
    ("Runtime", ["Flask / Flask-SQLAlchemy", "Socket.IO / Gunicorn-ready"]),
])

svg.extend(parts)
for y1, y2 in [(265, 285), (430, 450), (595, 615), (760, 780)]:
    svg.append(f'<line x1="800" y1="{y1}" x2="800" y2="{y2}" stroke="#64748B" stroke-width="3" marker-end="url(#arrow)"/>')

svg.append('''<rect x="50" y="945" width="1500" height="35" rx="10" fill="#1E293B"/>
<text x="800" y="968" text-anchor="middle" font-size="15" font-weight="700" fill="#FFFFFF">Cross-cutting: CSRF Protection • Flask-Login / Roles • Session Security • Rate Limiting • Upload Validation • Security Headers • Audit Logging</text>
</svg>''')

(OUTPUT_DIR / "OMSU_FINDBACK_Layered_Architecture.svg").write_text("\n".join(svg), encoding="utf-8")


pdf_path = OUTPUT_DIR / "OMSU_FINDBACK_Layered_Architecture.pdf"
c = canvas.Canvas(str(pdf_path), pagesize=landscape(letter))
pw, ph = landscape(letter)
c.setFillColor(colors.HexColor("#F8FAFC"))
c.rect(0, 0, pw, ph, fill=1, stroke=0)
c.setFillColor(colors.HexColor("#0F172A"))
c.setFont("Helvetica-Bold", 20)
c.drawCentredString(pw/2, ph-34, "OMSU FindBack - Layered Architecture")
c.setFont("Helvetica", 9)
c.drawCentredString(pw/2, ph-50, "Five application layers plus shared cross-cutting infrastructure")


def pdf_layer(y, title, fill, stroke, items):
    c.setFillColor(colors.HexColor(fill))
    c.roundRect(18, y, 756, 70, 8, fill=1, stroke=0)
    c.setFillColor(colors.HexColor(stroke))
    c.roundRect(18, y, 155, 70, 8, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(95, y+40, title)
    c.drawCentredString(95, y+28, "LAYER")
    card_w = 146
    for i, (name, detail) in enumerate(items):
        x = 180 + i * card_w
        c.setFillColor(colors.white)
        c.roundRect(x, y+8, 137, 54, 6, fill=1, stroke=0)
        c.setFillColor(colors.HexColor("#0F172A"))
        c.setFont("Helvetica-Bold", 8)
        c.drawString(x+7, y+49, name)
        c.setFillColor(colors.HexColor("#334155"))
        c.setFont("Helvetica", 7)
        ty = y+36
        for line in detail[:3]:
            c.drawString(x+7, ty, line)
            ty -= 9


pdf_layer(430, "PRESENTATION", "#DBEAFE", "#2563EB", [
    ("Actors", ["Student", "Moderator", "Administrator"]),
    ("Web Interface", ["Jinja2 templates", "CSS / JavaScript"]),
    ("Real-Time UI", ["Socket.IO client"]),
    ("Forms", ["Auth / reports / claims"]),
])
pdf_layer(350, "APPLICATION / ROUTE", "#DCFCE7", "#16A34A", [
    ("Auth Blueprint", ["Login / register"]),
    ("Student Blueprint", ["Reports / AI / claims"]),
    ("Staff Blueprints", ["Moderator / admin"]),
    ("Messaging", ["Socket.IO / notifications"]),
])
pdf_layer(270, "BUSINESS / DOMAIN", "#FEF3C7", "#D97706", [
    ("Report Workflow", ["Submit / verify"]),
    ("Claim Workflow", ["Proof / handover"]),
    ("AI Services", ["Detection / suggestion"]),
    ("Matching Service", ["Attribute / image score"]),
])
pdf_layer(190, "DATA ACCESS / MODEL", "#F3E8FF", "#9333EA", [
    ("ORM Models", ["SQLAlchemy"]),
    ("Repositories", ["Flask-SQLAlchemy"]),
    ("Domain Records", ["User to transaction"]),
    ("Audit & Events", ["Logs / AI / notices"]),
])
pdf_layer(110, "INFRASTRUCTURE", "#E0F2FE", "#0284C7", [
    ("MySQL", ["omsu_findback"]),
    ("File Storage", ["instance/uploads"]),
    ("External", ["SMTP / YOLOv8n"]),
    ("Runtime", ["Flask / Socket.IO"]),
])

c.setStrokeColor(colors.HexColor("#64748B"))
c.setLineWidth(1.5)
for y in (421, 341, 261, 181):
    c.line(396, y, 396, y-10)

c.setFillColor(colors.HexColor("#1E293B"))
c.roundRect(18, 65, 756, 28, 7, fill=1, stroke=0)
c.setFillColor(colors.white)
c.setFont("Helvetica-Bold", 7)
c.drawCentredString(396, 76, "CROSS-CUTTING: CSRF • Flask-Login/Roles • Sessions • Rate Limiting • Upload Validation • Security Headers • Audit Logging")
c.setTitle("OMSU FindBack Layered Architecture")
c.setAuthor("OMSU FindBack")
c.save()

print(OUTPUT_DIR / "OMSU_FINDBACK_Layered_Architecture.svg")
print(pdf_path)
