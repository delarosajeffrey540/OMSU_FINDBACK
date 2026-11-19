from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, legal
from reportlab.pdfgen import canvas


OUTPUT_DIR = Path(__file__).resolve().parent
WIDTH, HEIGHT = 1800, 1150

USE_CASES = [
    (650, 245, "Register account", "Guest"),
    (1080, 245, "Sign in / sign out", "Guest"),
    (510, 365, "Browse campus reports", "Student"),
    (900, 365, "Submit Lost / Found report", "Student"),
    (1290, 365, "Get AI photo suggestions", "Student"),
    (510, 500, "View own reports and status", "Student"),
    (900, 500, "Review possible item matches", "Student"),
    (1290, 500, "Submit claim with ownership details", "Student"),
    (700, 635, "Message report owner / claimant", "Student"),
    (1150, 635, "View and open notifications", "Student"),
    (490, 760, "Review, approve, or reject reports", "Staff"),
    (890, 760, "Review claims and ownership proof", "Staff"),
    (1290, 760, "Verify handover / reverse claim", "Staff"),
    (490, 875, "Create report for a student", "Staff"),
    (890, 875, "Access claim conversations", "Staff"),
    (1290, 875, "Receive report and claim alerts", "Staff"),
    (490, 990, "Manage users, roles, and status", "Admin"),
    (890, 990, "Manage categories and locations", "Admin"),
    (1290, 990, "View analytics, records, and audit", "Admin"),
]


def svg_text(x, y, value, size=14, color="#334155", weight=400, anchor="middle"):
    return (
        f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" '
        f'font-weight="{weight}" fill="{color}">{escape(value)}</text>'
    )


svg = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
<defs>
  <marker id="triangle" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto" markerUnits="strokeWidth">
    <path d="M1,1 L10,6 L1,11 Z" fill="#F8FAFC" stroke="#475569" stroke-width="1.5"/>
  </marker>
  <style>text {{ font-family: Arial, Helvetica, sans-serif; }}</style>
</defs>
<rect width="{WIDTH}" height="{HEIGHT}" fill="#F8FAFC"/>
<text x="900" y="48" text-anchor="middle" font-size="34" font-weight="800" fill="#0F172A">OMSU FindBack - Use Case Diagram</text>
<text x="900" y="78" text-anchor="middle" font-size="16" fill="#64748B">End-user access permissions and available system features</text>
<rect x="250" y="120" width="1300" height="930" rx="18" fill="#FFFFFF" stroke="#334155" stroke-width="3"/>
<rect x="250" y="120" width="1300" height="54" rx="18" fill="#1E293B"/>
<text x="900" y="154" text-anchor="middle" font-size="20" font-weight="800" fill="#FFFFFF">OMSU FindBack System</text>
''']

# Associations are routed along a role-specific bus to keep the actor links clear.
svg.extend([
    '<line x1="158" y1="307" x2="280" y2="307" stroke="#475569" stroke-width="2.2"/>',
    '<line x1="280" y1="190" x2="280" y2="307" stroke="#64748B" stroke-width="2"/>',
    '<line x1="280" y1="190" x2="500" y2="190" stroke="#475569" stroke-width="2.2"/>',
    '<line x1="500" y1="190" x2="500" y2="245" stroke="#475569" stroke-width="2.2"/>',
    '<line x1="280" y1="190" x2="930" y2="190" stroke="#475569" stroke-width="2.2"/>',
    '<line x1="930" y1="190" x2="930" y2="245" stroke="#475569" stroke-width="2.2"/>',
    '<line x1="280" y1="315" x2="280" y2="665" stroke="#64748B" stroke-width="2"/>',
    '<line x1="158" y1="547" x2="280" y2="547" stroke="#475569" stroke-width="2.2"/>',
    '<path d="M280 365 V315 H1140" fill="none" stroke="#475569" stroke-width="2.2"/>',
    '<line x1="360" y1="315" x2="360" y2="365" stroke="#475569" stroke-width="2.2"/>',
    '<line x1="750" y1="315" x2="750" y2="365" stroke="#475569" stroke-width="2.2"/>',
    '<line x1="1140" y1="315" x2="1140" y2="365" stroke="#475569" stroke-width="2.2"/>',
    '<path d="M280 500 V455 H1140" fill="none" stroke="#475569" stroke-width="2.2"/>',
    '<line x1="360" y1="455" x2="360" y2="500" stroke="#475569" stroke-width="2.2"/>',
    '<line x1="750" y1="455" x2="750" y2="500" stroke="#475569" stroke-width="2.2"/>',
    '<line x1="1140" y1="455" x2="1140" y2="500" stroke="#475569" stroke-width="2.2"/>',
    '<path d="M280 635 V590 H1000" fill="none" stroke="#475569" stroke-width="2.2"/>',
    '<line x1="550" y1="590" x2="550" y2="635" stroke="#475569" stroke-width="2.2"/>',
    '<line x1="1000" y1="590" x2="1000" y2="635" stroke="#475569" stroke-width="2.2"/>',
    '<line x1="1505" y1="700" x2="1505" y2="910" stroke="#64748B" stroke-width="2"/>',
    '<line x1="1710" y1="812" x2="1505" y2="812" stroke="#475569" stroke-width="2.2"/>',
    '<path d="M1505 760 V710 H640 M1440 710 V760 M1040 710 V760" fill="none" stroke="#475569" stroke-width="2.2"/>',
    '<path d="M1505 875 V820 H640 M1440 820 V875 M1040 820 V875" fill="none" stroke="#475569" stroke-width="2.2"/>',
    '<line x1="1505" y1="935" x2="1505" y2="1020" stroke="#64748B" stroke-width="2"/>',
    '<line x1="1710" y1="982" x2="1505" y2="982" stroke="#475569" stroke-width="2.2"/>',
    '<path d="M1505 990 V935 H640 M1440 935 V990 M1040 935 V990" fill="none" stroke="#475569" stroke-width="2.2"/>',
    # Admin actor specializes the moderator actor, inheriting staff use cases.
    '<path d="M1690 1026 L1760 1026 L1760 820 L1712 820" fill="none" stroke="#475569" stroke-width="2.2" marker-end="url(#triangle)"/>',
])

# Use cases (ellipses) are grouped by actor permission.
for cx, cy, title, role in USE_CASES:
    if role == "Guest":
        fill, stroke = "#E0F2FE", "#0284C7"
    elif role == "Student":
        fill, stroke = "#DBEAFE", "#2563EB"
    elif role == "Staff":
        fill, stroke = "#DCFCE7", "#16A34A"
    else:
        fill, stroke = "#F3E8FF", "#9333EA"
    svg.append(f'<ellipse cx="{cx}" cy="{cy}" rx="150" ry="43" fill="{fill}" stroke="{stroke}" stroke-width="2.5"/>')
    svg.append(svg_text(cx, cy+5, title, size=14, color="#0F172A", weight=700))

# Actors outside the system boundary.
def svg_actor(x, y, label):
    svg.extend([
        f'<circle cx="{x}" cy="{y-35}" r="12" fill="none" stroke="#0F172A" stroke-width="3"/>',
        f'<line x1="{x}" y1="{y-23}" x2="{x}" y2="{y+14}" stroke="#0F172A" stroke-width="3"/>',
        f'<line x1="{x-18}" y1="{y-8}" x2="{x+18}" y2="{y-8}" stroke="#0F172A" stroke-width="3"/>',
        f'<line x1="{x}" y1="{y+14}" x2="{x-16}" y2="{y+36}" stroke="#0F172A" stroke-width="3"/>',
        f'<line x1="{x}" y1="{y+14}" x2="{x+16}" y2="{y+36}" stroke="#0F172A" stroke-width="3"/>',
        svg_text(x, y+62, label, size=16, color="#0F172A", weight=700),
    ])


svg_actor(140, 315, "Guest")
svg_actor(140, 555, "Student")
svg_actor(1690, 820, "Moderator")
svg_actor(1690, 990, "Administrator")

# Permission group headings and policy note.
svg.extend([
    '<text x="310" y="300" font-size="13" font-weight="800" fill="#2563EB">STUDENT PERMISSIONS</text>',
    '<text x="310" y="690" font-size="13" font-weight="800" fill="#16A34A">MODERATOR PERMISSIONS (ADMIN ALSO HAS THESE)</text>',
    '<text x="310" y="925" font-size="13" font-weight="800" fill="#9333EA">ADMINISTRATOR-ONLY PERMISSIONS</text>',
    '<rect x="285" y="1070" width="1230" height="27" rx="8" fill="#FFF7ED" stroke="#EA580C" stroke-width="1.5"/>',
    '<text x="900" y="1088" text-anchor="middle" font-size="12" font-weight="700" fill="#9A3412">Protected features require an account. AI matches are suggestions only; authorized staff verify ownership and handover.</text>',
    '<text x="1650" y="905" text-anchor="end" font-size="11" fill="#475569">Admin inherits staff access</text>',
    '</svg>',
])

(OUTPUT_DIR / "OMSU_FINDBACK_Use_Case_Diagram.svg").write_text("\n".join(svg), encoding="utf-8")


# PDF version: render the same use cases and actors on a landscape legal page.
pdf_path = OUTPUT_DIR / "OMSU_FINDBACK_Use_Case_Diagram.pdf"
page_size = landscape(legal)
page_w, page_h = page_size
c = canvas.Canvas(str(pdf_path), pagesize=page_size)
c.setTitle("OMSU FindBack Use Case Diagram")
c.setAuthor("OMSU FindBack")
scale = min(page_w / WIDTH, (page_h - 30) / HEIGHT)
offset_x = (page_w - WIDTH * scale) / 2
offset_y = (page_h - HEIGHT * scale) / 2


def px(value):
    return offset_x + value * scale


def py(value):
    return page_h - offset_y - value * scale


def pdf_line(x1, y1, x2, y2, color="#475569", width=2):
    c.setStrokeColor(colors.HexColor(color))
    c.setLineWidth(width * scale)
    c.line(px(x1), py(y1), px(x2), py(y2))


def pdf_text(x, y, value, size, color="#334155", weight=False, align="center"):
    c.setFillColor(colors.HexColor(color))
    c.setFont("Helvetica-Bold" if weight else "Helvetica", size * scale)
    if align == "center":
        c.drawCentredString(px(x), py(y), value)
    elif align == "right":
        c.drawRightString(px(x), py(y), value)
    else:
        c.drawString(px(x), py(y), value)


c.setFillColor(colors.HexColor("#F8FAFC"))
c.rect(0, 0, page_w, page_h, fill=1, stroke=0)
c.setFillColor(colors.HexColor("#FFFFFF"))
c.setStrokeColor(colors.HexColor("#334155"))
c.setLineWidth(3 * scale)
c.roundRect(px(250), py(1050), 1300*scale, 930*scale, 18*scale, fill=1, stroke=1)
c.setFillColor(colors.HexColor("#1E293B"))
c.roundRect(px(250), py(174), 1300*scale, 54*scale, 18*scale, fill=1, stroke=0)
pdf_text(900, 48, "OMSU FindBack - Use Case Diagram", 34, "#0F172A", True)
pdf_text(900, 78, "End-user access permissions and available system features", 16, "#64748B")
pdf_text(900, 154, "OMSU FindBack System", 20, "#FFFFFF", True)

# Association buses route around use cases rather than through them.
segments = [
    ((158,307),(280,307)), ((280,190),(280,307)),
    ((280,190),(500,190)), ((500,190),(500,245)),
    ((280,190),(930,190)), ((930,190),(930,245)),
    ((280,315),(280,665)), ((158,547),(280,547)),
    ((280,365),(280,315)), ((280,315),(1140,315)),
    ((360,315),(360,365)), ((750,315),(750,365)), ((1140,315),(1140,365)),
    ((280,500),(280,455)), ((280,455),(1140,455)),
    ((360,455),(360,500)), ((750,455),(750,500)), ((1140,455),(1140,500)),
    ((280,635),(280,590)), ((280,590),(1000,590)),
    ((550,590),(550,635)), ((1000,590),(1000,635)),
    ((1505,700),(1505,910)), ((1710,812),(1505,812)),
    ((1505,760),(1505,710)), ((1505,710),(640,710)),
    ((1440,710),(1440,760)), ((1040,710),(1040,760)), ((640,710),(640,760)),
    ((1505,875),(1505,820)), ((1505,820),(640,820)),
    ((1440,820),(1440,875)), ((1040,820),(1040,875)), ((640,820),(640,875)),
    ((1505,935),(1505,1020)), ((1710,982),(1505,982)),
    ((1505,990),(1505,935)), ((1505,935),(640,935)),
    ((1440,935),(1440,990)), ((1040,935),(1040,990)), ((640,935),(640,990)),
]
for start, end in segments:
    pdf_line(start[0], start[1], end[0], end[1])
pdf_line(1690,1026,1760,1026)
pdf_line(1760,1026,1760,820)
pdf_line(1760,820,1712,820)
generalization = c.beginPath()
generalization.moveTo(px(1712), py(820))
generalization.lineTo(px(1724), py(814))
generalization.lineTo(px(1724), py(826))
generalization.close()
c.setStrokeColor(colors.HexColor("#475569"))
c.setLineWidth(1.2 * scale)
c.drawPath(generalization, stroke=1, fill=0)

for cx, cy, title, role in USE_CASES:
    if role == "Guest":
        fill, stroke = "#E0F2FE", "#0284C7"
    elif role == "Student":
        fill, stroke = "#DBEAFE", "#2563EB"
    elif role == "Staff":
        fill, stroke = "#DCFCE7", "#16A34A"
    else:
        fill, stroke = "#F3E8FF", "#9333EA"
    c.setFillColor(colors.HexColor(fill))
    c.setStrokeColor(colors.HexColor(stroke))
    c.setLineWidth(2.5 * scale)
    c.ellipse(px(cx-150), py(cy+43), px(cx+150), py(cy-43), fill=1, stroke=1)
    pdf_text(cx, cy+5, title, 14, "#0F172A", True)


def pdf_actor(x, y, label):
    c.setStrokeColor(colors.HexColor("#0F172A"))
    c.setLineWidth(3 * scale)
    c.circle(px(x), py(y-35), 12*scale, fill=0, stroke=1)
    for coords in [
        (x,y-23,x,y+14),(x-18,y-8,x+18,y-8),
        (x,y+14,x-16,y+36),(x,y+14,x+16,y+36),
    ]:
        pdf_line(*coords, color="#0F172A", width=3)
    pdf_text(x, y+62, label, 16, "#0F172A", True)


pdf_actor(140, 315, "Guest")
pdf_actor(140, 555, "Student")
pdf_actor(1690, 820, "Moderator")
pdf_actor(1690, 990, "Administrator")
pdf_text(310, 300, "STUDENT PERMISSIONS", 13, "#2563EB", True, "left")
pdf_text(310, 690, "MODERATOR PERMISSIONS (ADMIN ALSO HAS THESE)", 13, "#16A34A", True, "left")
pdf_text(310, 925, "ADMINISTRATOR-ONLY PERMISSIONS", 13, "#9333EA", True, "left")
c.setFillColor(colors.HexColor("#FFF7ED"))
c.setStrokeColor(colors.HexColor("#EA580C"))
c.roundRect(px(285), py(1097), 1230*scale, 27*scale, 8*scale, fill=1, stroke=1)
pdf_text(900, 1088, "Protected features require an account. AI matches are suggestions; authorized staff verify ownership and handover.", 12, "#9A3412", True)
pdf_text(1650, 905, "Admin inherits staff access", 11, "#475569", False, "right")
c.save()

print(OUTPUT_DIR / "OMSU_FINDBACK_Use_Case_Diagram.svg")
print(pdf_path)
