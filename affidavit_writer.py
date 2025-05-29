# affidavit_writer.py

from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from datetime import datetime

def generate_affidavit(meta1, meta2, score, reasons, output_path):
    c = canvas.Canvas(output_path, pagesize=LETTER)
    width, height = LETTER
    margin = 50
    line_height = 14
    y = height - margin

    # Header
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, y, "Forensic PDF Affidavit")
    y -= 2 * line_height

    # Timestamp
    c.setFont("Helvetica", 10)
    c.drawString(margin, y, f"Generated on: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    y -= 2 * line_height

    # Document 1
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Document 1:")
    y -= line_height
    c.setFont("Helvetica", 10)
    for key, val in meta1.items():
        c.drawString(margin + 20, y, f"{key}: {val}")
        y -= line_height

    y -= line_height

    # Document 2
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Document 2:")
    y -= line_height
    c.setFont("Helvetica", 10)
    for key, val in meta2.items():
        c.drawString(margin + 20, y, f"{key}: {val}")
        y -= line_height

    y -= 2 * line_height

    # Score & Reasons
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, f"Suspicion Score: {score}")
    y -= 2 * line_height
    c.setFont("Helvetica", 10)
    c.drawString(margin, y, "Reasons for Flagging:")
    y -= line_height

    for reason in reasons:
        c.drawString(margin + 20, y, f"- {reason}")
        y -= line_height
        if y < margin + 50:
            c.showPage()
            y = height - margin

    y -= 2 * line_height

    # Certification
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(margin, y, "This analysis was conducted using forensic best practices and automation tools designed for evidentiary use.")
    y -= line_height
    c.drawString(margin, y, "Certified by Forensix, LLC")
    c.save()