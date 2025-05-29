# affidavit_writer.py

from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from datetime import datetime

def generate_affidavit(meta1, meta2, score, reasons, output_path):
    """
    Generates a forensic affidavit PDF comparing two documents.
    """

    c = canvas.Canvas(output_path, pagesize=LETTER)
    width, height = LETTER
    margin = 50
    line_height = 14
    y = height - margin

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin, y, "Forensic Document Comparison Affidavit")
    y -= line_height * 2

    # Timestamp
    c.setFont("Helvetica", 10)
    c.drawString(margin, y, f"Date of Analysis: {datetime.utcnow().isoformat()} UTC")
    y -= line_height * 2

    # Score section
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, f"Suspicion Score: {score}")
    y -= line_height
    if score > 50:
        c.setFont("Helvetica", 10)
        c.drawString(margin, y, "This score exceeds the forensic suspicion threshold.")
        y -= line_height * 2

    # Document A metadata
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Document A Metadata")
    y -= line_height
    c.setFont("Helvetica", 10)
    for k, v in meta1.items():
        c.drawString(margin + 10, y, f"{k}: {v}")
        y -= line_height
        if y < margin:
            c.showPage()
            y = height - margin

    y -= line_height
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Document B Metadata")
    y -= line_height
    c.setFont("Helvetica", 10)
    for k, v in meta2.items():
        c.drawString(margin + 10, y, f"{k}: {v}")
        y -= line_height
        if y < margin:
            c.showPage()
            y = height - margin

    # Reasons section
    y -= line_height
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Forensic Indicators")
    y -= line_height
    c.setFont("Helvetica", 10)
    for reason in reasons:
        c.drawString(margin + 10, y, f"- {reason}")
        y -= line_height
        if y < margin:
            c.showPage()
            y = height - margin

    # Footer
    y = margin
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(margin, y, "Certified by Forensix, LLC")
    y -= line_height
    c.drawString(margin, y, "This analysis was performed using best available forensic practices and tools including PDF-XChange Editor, ReportLab, hashlib, and XMPToolkit-compatible metadata parsers.")
    y -= line_height
    c.drawString(margin, y, "Affidavit generated via Acroform Informer PDF Forensics Suite.")

    c.save()