from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen import canvas


OUTPUT_DIR = Path(__file__).resolve().parent
W, H = 1600, 1050


svg = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
  <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
    <path d="M0,0 L0,6 L9,3 z" fill="#64748B"/>
  </marker>
  <style>text {{ font-family: Arial, Helvetica, sans-serif; }}</style>
</defs>
<rect width="{W}" height="{H}" fill="#F8FAFC"/>
<text x="800" y="48" text-anchor="middle" font-size="34" font-weight="800" fill="#0F172A">OMSU FindBack - Lost Item Recovery Sequence</text>
<text x="800" y="78" text-anchor="middle" font-size="16" fill="#64748B">Report submission, verification, matching, claim, messaging, and handover</text>
''']

participants = [
    (125, "Student\nReporter"),
    (340, "Student\nClaimant"),
    (575, "Flask\nApplication"),
    (810, "AI Matching\nEngine"),
    (1045, "MySQL\nDatabase"),
    (1280, "Moderator /\nAdministrator"),
]

for x, label in participants:
    svg.append(f'<rect x="{x-85}" y="110" width="170" height="70" rx="12" fill="#FFFFFF" stroke="#475569" stroke-width="2"/>')
    lines = label.split("\n")
    for i, line in enumerate(lines):
        svg.append(f'<text x="{x}" y="{140+i*20}" text-anchor="middle" font-size="15" font-weight="700" fill="#0F172A">{escape(line)}</text>')
    svg.append(f'<line x1="{x}" y1="180" x2="{x}" y2="930" stroke="#94A3B8" stroke-width="2" stroke-dasharray="8 6"/>')


def message(y, x1, x2, label, dashed=False):
    dash = ' stroke-dasharray="8 5"' if dashed else ""
    parts = [
        f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="#475569" stroke-width="2.5"{dash} marker-end="url(#arrow)"/>',
        f'<rect x="{(x1+x2)//2-90}" y="{y-18}" width="180" height="24" rx="7" fill="#F8FAFC"/>',
        f'<text x="{(x1+x2)//2}" y="{y-2}" text-anchor="middle" font-size="12" font-weight="700" fill="#334155">{escape(label)}</text>',
    ]
    svg.extend(parts)


# Activation bars
for x in [575, 1045, 1280, 340, 125, 810]:
    svg.append(f'<rect x="{x-5}" y="205" width="10" height="700" rx="4" fill="#DBEAFE" fill-opacity="0.45" stroke="#93C5FD" stroke-width="1"/>')

message(220, 125, 575, "Submit Lost report + photo")
message(250, 575, 1045, "Save report (Awaiting review)")
message(280, 1045, 575, "Report stored", True)
message(310, 575, 125, "Notify report submitted")

message(350, 1280, 575, "Approve report")
message(380, 575, 1045, "Update status = Verified")
message(410, 575, 810, "Request Lost/Found matching")
message(440, 810, 1045, "Read verified candidates")
message(470, 1045, 810, "Candidate reports + photos")
message(500, 810, 810-215, "Calculate attribute score")
message(530, 810, 1045, "Load YOLO image embeddings")
message(560, 1045, 810, "Image data", True)
message(590, 810, 575, "Ranked match suggestions")
message(620, 575, 1045, "Save match notifications")
message(650, 575, 340, "Notify claimant of possible match")

message(690, 340, 575, "Submit claim + identity details")
message(720, 575, 1045, "Save Claim + create Conversation")
message(750, 575, 1280, "Notify ownership claim")
message(780, 575, 125, "Notify owner / meeting")

# Messaging alt frame
svg.append('<rect x="260" y="805" width="1110" height="95" rx="10" fill="#FFFFFF" stroke="#94A3B8" stroke-width="2"/>')
svg.append('<path d="M260 805 H370 L390 825 H260 Z" fill="#E2E8F0" stroke="#94A3B8" stroke-width="2"/>')
svg.append('<text x="275" y="825" font-size="12" font-weight="800" fill="#334155">alt</text>')
message(845, 340, 575, "Send private message")
message(872, 575, 1045, "Save Message")
message(899, 575, 1280, "Socket.IO / notification")

# Reset this isn't overlapping due to final handover
# Handover and transaction block
svg.append('<rect x="40" y="920" width="1520" height="100" rx="12" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="2"/>')
svg.append('<text x="65" y="948" font-size="15" font-weight="800" fill="#0F172A">Physical handover at SSG Office -  Moderator/Administrator verifies the claimant</text>')

svg.append('</svg>')

(OUTPUT_DIR / "OMSU_FINDBACK_Sequence_Diagram.svg").write_text("\n".join(svg), encoding="utf-8")


pdf_path = OUTPUT_DIR / "OMSU_FINDBACK_Sequence_Diagram.pdf"
c = canvas.Canvas(str(pdf_path), pagesize=landscape(letter))
pw, ph = landscape(letter)
c.setFillColor(colors.HexColor("#F8FAFC"))
c.rect(0, 0, pw, ph, fill=1, stroke=0)
c.setFillColor(colors.HexColor("#0F172A"))
c.setFont("Helvetica-Bold", 20)
c.drawCentredString(pw/2, ph-34, "OMSU FindBack - Lost Item Recovery Sequence")
c.setFont("Helvetica", 9)
c.drawCentredString(pw/2, ph-50, "Report submission, verification, matching, claim, messaging, and handover")

part_x = [48, 150, 260, 370, 480, 690]
part_names = ["Reporter", "Claimant", "Flask App", "AI Engine", "MySQL", "Staff"]
for x, name in zip(part_x, part_names):
    c.setFillColor(colors.white)
    c.roundRect(x, 490, 96, 42, 7, fill=1, stroke=1)
    c.setFillColor(colors.HexColor("#0F172A"))
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(x+48, 515, name)
    c.setStrokeColor(colors.HexColor("#94A3B8"))
    c.setDash(4, 3)
    c.line(x+48, 490, x+48, 65)
    c.setDash()


def pdf_message(y, x1, x2, label):
    c.setStrokeColor(colors.HexColor("#475569"))
    c.setLineWidth(1.2)
    c.line(x1, y, x2, y)
    c.setFillColor(colors.HexColor("#475569"))
    c.circle(x2, y, 2.2, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#334155"))
    c.setFont("Helvetica-Bold", 6)
    c.drawCentredString((x1+x2)/2, y+4, label)


pdf_message(470, 96, 308, "Submit Lost report + photo")
pdf_message(445, 308, 528, "Save Awaiting-review report")
pdf_message(420, 738, 308, "Approve report")
pdf_message(395, 308, 418, "Update Verified + request match")
pdf_message(370, 418, 528, "Read candidates")
pdf_message(345, 418, 308, "Ranked suggestions")
pdf_message(320, 308, 198, "Notify possible match")
pdf_message(295, 198, 308, "Submit claim + proof")
pdf_message(270, 308, 528, "Save Claim + Conversation")
pdf_message(245, 308, 738, "Notify staff and owner")
pdf_message(220, 198, 308, "Send private message")
pdf_message(195, 308, 528, "Save Message")
pdf_message(170, 308, 738, "Deliver Socket.IO / notification")

c.setFillColor(colors.HexColor("#FFFFFF"))
c.roundRect(18, 78, 774, 62, 8, fill=1, stroke=1)
c.setFillColor(colors.HexColor("#0F172A"))
c.setFont("Helvetica-Bold", 9)
c.drawString(30, 122, "Handover step")
c.setFont("Helvetica", 7)
c.drawString(30, 108, "Staff verifies physical handover at SSG Office.")
c.drawString(30, 96, "Create immutable ClaimTransaction, mark Report Recovered, record AuditLog.")
c.drawString(30, 84, "Notifications and optional email are sent to owner and claimant.")

c.setTitle("OMSU FindBack Lost Item Recovery Sequence")
c.setAuthor("OMSU FindBack")
c.save()

print(OUTPUT_DIR / "OMSU_FINDBACK_Sequence_Diagram.svg")
print(pdf_path)
