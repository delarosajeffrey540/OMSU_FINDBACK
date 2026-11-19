from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen import canvas


OUTPUT_DIR = Path(__file__).resolve().parent
W, H = 1600, 1000


def ext(x, y, w, h, title, lines, fill="#DBEAFE", stroke="#2563EB"):
    text = [
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{fill}" stroke="{stroke}" stroke-width="3"/>',
        f'<text x="{x+w/2}" y="{y+32}" text-anchor="middle" font-size="17" font-weight="800" fill="#0F172A">{escape(title)}</text>',
    ]
    ty = y + 58
    for line in lines:
        text.append(f'<text x="{x+12}" y="{ty}" font-size="13" fill="#334155">{escape(line)}</text>')
        ty += 20
    return text


def process(x, y, w, h, number, title, lines, fill="#DCFCE7", stroke="#16A34A"):
    text = [
        f'<circle cx="{x+w/2}" cy="{y+h/2}" r="{h/2}" fill="{fill}" stroke="{stroke}" stroke-width="3"/>',
        f'<text x="{x+w/2}" y="{y+30}" text-anchor="middle" font-size="13" font-weight="800" fill="{stroke}">{number}</text>',
        f'<text x="{x+w/2}" y="{y+52}" text-anchor="middle" font-size="15" font-weight="800" fill="#0F172A">{escape(title)}</text>',
    ]
    ty = y + 74
    for line in lines:
        text.append(f'<text x="{x+w/2}" y="{ty}" text-anchor="middle" font-size="12" fill="#334155">{escape(line)}</text>')
        ty += 16
    return text


def store(x, y, w, h, title, lines):
    text = [
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#F3E8FF" stroke="#9333EA" stroke-width="3"/>',
        f'<line x1="{x}" y1="{y+38}" x2="{x+w}" y2="{y+38}" stroke="#9333EA" stroke-width="2"/>',
        f'<text x="{x+12}" y="{y+25}" font-size="15" font-weight="800" fill="#6B21A8">{escape(title)}</text>',
    ]
    ty = y + 58
    for line in lines:
        text.append(f'<text x="{x+12}" y="{ty}" font-size="12" fill="#334155">{escape(line)}</text>')
        ty += 17
    return text


def arrow(x1, y1, x2, y2, label="", dashed=False):
    dash = ' stroke-dasharray="7 5"' if dashed else ""
    parts = [
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#64748B" stroke-width="2.5"{dash} marker-end="url(#arrow)"/>'
    ]
    if label:
        mx, my = (x1+x2)/2, (y1+y2)/2
        parts.append(f'<rect x="{mx-70}" y="{my-14}" width="140" height="22" rx="7" fill="#FFFFFF" fill-opacity="0.95"/>')
        parts.append(f'<text x="{mx}" y="{my+1}" text-anchor="middle" font-size="11" font-weight="700" fill="#475569">{escape(label)}</text>')
    return parts


svg = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
  <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
    <path d="M0,0 L0,6 L9,3 z" fill="#64748B"/>
  </marker>
  <style>text {{ font-family: Arial, Helvetica, sans-serif; }}</style>
</defs>
<rect width="{W}" height="{H}" fill="#F8FAFC"/>
<text x="800" y="50" text-anchor="middle" font-size="34" font-weight="800" fill="#0F172A">OMSU FindBack - Level 1 Data Flow Diagram</text>
<text x="800" y="80" text-anchor="middle" font-size="16" fill="#64748B">External entities, processes, and persistent data flows</text>
''']

# External entities
svg.extend(ext(40, 155, 170, 145, "STUDENT", ["Credentials", "Report details", "Claim proof", "Messages"]))
svg.extend(ext(40, 430, 170, 145, "MODERATOR", ["Review decisions", "Handover details", "Claim reversal"]))
svg.extend(ext(40, 705, 170, 145, "ADMINISTRATOR", ["User management", "Catalog management", "Analytics"]))
svg.extend(ext(1390, 705, 170, 145, "SMTP SERVER", ["Optional email", "Report / claim alerts", "Message alerts"], "#E0F2FE", "#0284C7"))

# Processes
svg.extend(process(290, 155, 210, 145, "1.0", "Authenticate & Authorize", ["Login / registration", "Role-based routing"]))
svg.extend(process(290, 405, 210, 145, "2.0", "Manage Lost / Found Reports", ["Create / upload", "Review status"]))
svg.extend(process(590, 405, 210, 145, "3.0", "Analyze & Match Items", ["YOLO suggestions", "Attribute + image match"]))
svg.extend(process(590, 155, 210, 145, "4.0", "Process Claims", ["Claim submission", "Proof review"]))
svg.extend(process(890, 405, 210, 145, "5.0", "Verify Handover", ["Approve claim", "Record transaction"]))
svg.extend(process(890, 155, 210, 145, "6.0", "Messaging", ["Private threads", "Socket.IO delivery"]))
svg.extend(process(1190, 405, 160, 145, "7.0", "Notifications", ["In-app records", "Optional SMTP"]))
svg.extend(process(1190, 155, 160, 145, "8.0", "Admin Control", ["Users", "Catalogs", "Audit / analytics"]))

# Stores
svg.extend(store(590, 720, 210, 155, "D1 - USERS", ["Credentials", "Role", "Status", "Affiliation"]))
svg.extend(store(850, 720, 210, 155, "D2 - REPORTS", ["Report details", "Photo filename", "Status"]))
svg.extend(store(1110, 720, 210, 155, "D3 - CLAIMS / TRANSACTIONS", ["Ownership proof", "Handover", "Reversals"]))
svg.extend(store(1370, 720, 190, 155, "D4 - CHAT / NOTICES", ["Conversations", "Messages", "Notifications"]))

# Arrows
svg.extend(arrow(210, 225, 290, 225, "Credentials"))
svg.extend(arrow(500, 225, 590, 225, "Authenticated user", True))
svg.extend(arrow(210, 500, 290, 500, "Report / review"))
svg.extend(arrow(500, 478, 590, 478, "Report details"))
svg.extend(arrow(210, 770, 1190, 228, "Account / catalog action"))
svg.extend(arrow(210, 478, 590, 478, "Review request"))
svg.extend(arrow(590, 225, 500, 225, "Authorization"))
svg.extend(arrow(395, 300, 395, 405, "Authorized report"))
svg.extend(arrow(695, 405, 695, 300, "Match suggestions"))
svg.extend(arrow(800, 478, 890, 478, "Verified match"))
svg.extend(arrow(695, 405, 695, 300, "Claim target"))
svg.extend(arrow(800, 228, 890, 228, "Claim / proof"))
svg.extend(arrow(800, 478, 890, 228, "Ownership evidence"))
svg.extend(arrow(800, 228, 890, 478, "Claim status"))
svg.extend(arrow(1100, 478, 1190, 478, "Status / alert"))
svg.extend(arrow(1100, 228, 890, 228, "Message events"))
svg.extend(arrow(890, 228, 1190, 478, "Message / claim alert"))
svg.extend(arrow(1350, 478, 1390, 478, "Notification"))
svg.extend(arrow(1270, 478, 1390, 705, "Email request"))
svg.extend(arrow(1350, 228, 210, 770, "Admin result", True))

# Store flows
svg.extend(arrow(395, 550, 695, 720, "User/report record"))
svg.extend(arrow(695, 550, 695, 720, "Report query"))
svg.extend(arrow(695, 720, 695, 550, "Report/photo data", True))
svg.extend(arrow(800, 228, 695, 720, "Claim query"))
svg.extend(arrow(695, 720, 800, 228, "User details", True))
svg.extend(arrow(955, 550, 955, 720, "Claim / transaction"))
svg.extend(arrow(955, 720, 955, 550, "Claim status", True))
svg.extend(arrow(995, 228, 1370, 720, "Chat / notice write"))
svg.extend(arrow(1370, 720, 995, 228, "Chat history", True))
svg.extend(arrow(1190, 228, 590, 720, "Account data"))
svg.extend(arrow(590, 720, 1190, 228, "User records", True))

svg.append('''<rect x="40" y="895" width="1520" height="70" rx="12" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="2"/>
<text x="65" y="925" font-size="15" font-weight="700" fill="#0F172A">Important data boundaries</text>
<text x="65" y="951" font-size="13" fill="#334155">AI matching uses private images stored in instance/uploads; matching scores are suggestions, not ownership proof.</text>
<text x="800" y="951" font-size="13" fill="#334155">The moderator or administrator must verify handover before a claim transaction completes.</text>
''')
svg.append('</svg>')

(OUTPUT_DIR / "OMSU_FINDBACK_Data_Flow_Diagram.svg").write_text("\n".join(svg), encoding="utf-8")


pdf_path = OUTPUT_DIR / "OMSU_FINDBACK_Data_Flow_Diagram.pdf"
c = canvas.Canvas(str(pdf_path), pagesize=landscape(letter))
pw, ph = landscape(letter)
c.setFillColor(colors.HexColor("#F8FAFC"))
c.rect(0, 0, pw, ph, fill=1, stroke=0)
c.setFillColor(colors.HexColor("#0F172A"))
c.setFont("Helvetica-Bold", 20)
c.drawCentredString(pw/2, ph-34, "OMSU FindBack - Level 1 Data Flow Diagram")
c.setFont("Helvetica", 9)
c.drawCentredString(pw/2, ph-50, "External entities, processes, and persistent data flows")


def pdf_box(x, y, w, h, title, fill, stroke, lines):
    c.setFillColor(colors.HexColor(fill))
    c.roundRect(x, y, w, h, 8, fill=1, stroke=0)
    c.setStrokeColor(colors.HexColor(stroke))
    c.roundRect(x, y, w, h, 8, fill=0, stroke=1)
    c.setFillColor(colors.HexColor("#0F172A"))
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(x+w/2, y+h-18, title)
    c.setFont("Helvetica", 7)
    c.setFillColor(colors.HexColor("#334155"))
    ty = y+h-32
    for line in lines:
        c.drawCentredString(x+w/2, ty, line)
        ty -= 10


# Entities
pdf_box(18, 430, 90, 90, "STUDENT", "#DBEAFE", "#2563EB", ["Credentials", "Reports", "Claims", "Messages"])
pdf_box(18, 300, 90, 90, "MODERATOR", "#DBEAFE", "#2563EB", ["Reviews", "Handover", "Reversal"])
pdf_box(18, 170, 90, 90, "ADMIN", "#DBEAFE", "#2563EB", ["Users", "Catalogs", "Analytics"])
pdf_box(684, 170, 108, 90, "SMTP SERVER", "#E0F2FE", "#0284C7", ["Report alerts", "Claim alerts", "Messages"])

# Processes
pdf_box(130, 430, 110, 90, "1.0 Authenticate", "#DCFCE7", "#16A34A", ["Login / register", "Role routing"])
pdf_box(130, 300, 110, 90, "2.0 Report", "#DCFCE7", "#16A34A", ["Create / upload", "Status"])
pdf_box(270, 300, 110, 90, "3.0 AI Match", "#DCFCE7", "#16A34A", ["YOLOv8", "Attribute / image"])
pdf_box(270, 430, 110, 90, "4.0 Claim", "#DCFCE7", "#16A34A", ["Proof", "Conversation"])
pdf_box(410, 300, 110, 90, "5.0 Handover", "#DCFCE7", "#16A34A", ["Approve", "Transaction"])
pdf_box(410, 430, 110, 90, "6.0 Messaging", "#DCFCE7", "#16A34A", ["Private chat", "Socket.IO"])
pdf_box(550, 300, 100, 90, "7.0 Notify", "#DCFCE7", "#16A34A", ["In-app", "SMTP"])
pdf_box(550, 430, 100, 90, "8.0 Admin", "#DCFCE7", "#16A34A", ["Users", "Catalogs"])

# Stores
pdf_box(130, 105, 145, 70, "D1 USERS", "#F3E8FF", "#9333EA", ["Role / status"])
pdf_box(290, 105, 145, 70, "D2 REPORTS", "#F3E8FF", "#9333EA", ["Details / photo / status"])
pdf_box(450, 105, 145, 70, "D3 CLAIMS", "#F3E8FF", "#9333EA", ["Proof / handover"])
pdf_box(610, 105, 182, 70, "D4 CHAT / NOTICES", "#F3E8FF", "#9333EA", ["Messages / notifications"])

c.setStrokeColor(colors.HexColor("#64748B"))
c.setLineWidth(1.2)
flows = [
    (108,475,130,475), (240,475,270,475), (108,345,130,345),
    (240,345,270,345), (380,345,410,345), (520,345,550,345),
    (520,475,410,475), (650,345,684,215), (650,475,684,215),
    (185,300,185,175), (362,300,362,175), (465,300,465,175),
]
for x1,y1,x2,y2 in flows:
    c.line(x1,y1,x2,y2)
    c.circle(x2,y2,2.5,fill=1,stroke=0)

c.setFillColor(colors.HexColor("#FFFFFF"))
c.roundRect(18, 520, 774, 48, 8, fill=1, stroke=1)
c.setFillColor(colors.HexColor("#0F172A"))
c.setFont("Helvetica-Bold", 9)
c.drawString(30, 554, "DATA FLOWS")
c.setFillColor(colors.HexColor("#334155"))
c.setFont("Helvetica", 7)
c.drawString(30, 540, "Student / staff inputs -> report, claim, chat, and admin processes")
c.drawString(270, 540, "Processes -> D1-D4 data stores")
c.drawString(495, 540, "Processes -> in-app and SMTP notifications")
c.drawString(30, 528, "AI matching is descriptive only; moderator/administrator handover verification determines completion")

c.setTitle("OMSU FindBack Level 1 Data Flow Diagram")
c.setAuthor("OMSU FindBack")
c.save()

print(OUTPUT_DIR / "OMSU_FINDBACK_Data_Flow_Diagram.svg")
print(pdf_path)
