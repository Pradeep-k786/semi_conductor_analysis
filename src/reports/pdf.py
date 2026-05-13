from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = ROOT / "reports"
REPORT_DIR.mkdir(exist_ok=True)

def create_pdf(kpis, recs):
    path = REPORT_DIR / "accusaga_semiconductor_ai_executive_report.pdf"
    c = canvas.Canvas(str(path), pagesize=A4)
    width, height = A4
    y = height - 50

    c.setFont("Helvetica-Bold", 18)
    c.drawString(45, y, "Accusaga Semiconductor AI Executive Report")
    y -= 35

    c.setFont("Helvetica-Bold", 13)
    c.drawString(45, y, "Executive KPIs")
    y -= 24

    c.setFont("Helvetica", 10)
    for k, v in kpis.items():
        c.drawString(60, y, f"{k.title()}: {v}")
        y -= 16

    y -= 18
    c.setFont("Helvetica-Bold", 13)
    c.drawString(45, y, "AI Recommendations")
    y -= 24

    c.setFont("Helvetica", 10)
    for title, msg in recs:
        c.drawString(60, y, f"{title}: {msg[:90]}")
        y -= 18
        if y < 80:
            c.showPage()
            y = height - 50

    c.save()
    return path
