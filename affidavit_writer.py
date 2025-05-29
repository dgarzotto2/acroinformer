# affidavit_writer.py

from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
import datetime
import os

def generate_affidavit(output_path, metadata_summary):
    c = canvas.Canvas(output_path, pagesize=LETTER)
    width, height = LETTER

    margin = 50
    y = height - margin

    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin, y, "Forensic PDF Affidavit Report")

    c.setFont("Helvetica", 12)
    y -= 40
    c.drawString(margin, y, f"Date: {datetime.date.today().isoformat()}")

    y -= 30
    c.drawString(margin, y, "The following document analysis was performed using static forensic methods.")
    y -= 20
    c.drawString(margin, y, "No OCR, editing, or external re-encoding was applied to preserve evidentiary integrity.")

    for meta in metadata_summary:
        y -= 40
        if y < 100:
            c.showPage()
            y = height - margin

        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin, y, f"Filename: {meta.get('filename', 'Unknown')}")

        c.setFont("Helvetica", 11)
        y -= 20
        c.drawString(margin, y, f"Risk Class: {meta.get('risk_class', 'Unknown')} | Score: {meta.get('score', 0)}")

        flags = meta.get("flags", [])
        if flags:
            y -= 20
            c.drawString(margin, y, "Flags:")
            for flag in flags:
                y -= 15
                if y < 100:
                    c.showPage()
                    y = height - margin
                c.drawString(margin + 20, y, f"• {flag}")

    # Footer certification
    y -= 60
    if y < 100:
        c.showPage()
        y = height - margin
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(margin, y, "Certified by Forensix, LLC")

    c.save()
    return output_path