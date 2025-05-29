# affidavit_writer.py

from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
import os
import datetime

def generate_affidavit(output_path: str, metadata_results: dict):
    """
    Generates a PDF affidavit summarizing forensic results.

    Args:
        output_path (str): Path to save the affidavit PDF.
        metadata_results (dict): Dictionary mapping filenames to their metadata dict.
    """
    c = canvas.Canvas(output_path, pagesize=LETTER)
    width, height = LETTER
    margin = 50
    y = height - margin

    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, y, "Forensic Analysis Affidavit")
    y -= 30

    c.setFont("Helvetica", 11)
    c.drawString(margin, y, f"Date of Report: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    y -= 40

    for fname, data in metadata_results.items():
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin, y, f"Document: {fname}")
        y -= 20

        c.setFont("Helvetica", 11)
        c.drawString(margin, y, f"SHA-256: {data.get('sha256', 'N/A')}")
        y -= 15
        c.drawString(margin, y, f"File Size: {data.get('file_size', 'N/A')} bytes")
        y -= 15
        c.drawString(margin, y, f"Page Count: {data.get('page_count', 'N/A')}")
        y -= 15
        c.drawString(margin, y, f"AcroForm Present: {'Yes' if data.get('acroform_present') else 'No'}")
        y -= 15
        c.drawString(margin, y, f"XFA Present: {'Yes' if data.get('xfa_present') else 'No'}")
        y -= 15

        metadata = data.get("metadata", {})
        if metadata:
            c.drawString(margin, y, "Metadata:")
            y -= 15
            for key, value in metadata.items():
                c.drawString(margin + 20, y, f"{key}: {value}")
                y -= 15
                if y < 100:
                    c.showPage()
                    y = height - margin

        errors = data.get("errors", [])
        if errors:
            c.drawString(margin, y, "Errors:")
            y -= 15
            for err in errors:
                c.drawString(margin + 20, y, f"- {err}")
                y -= 15
                if y < 100:
                    c.showPage()
                    y = height - margin

        y -= 25
        if y < 100:
            c.showPage()
            y = height - margin

    c.setFont("Helvetica-Oblique", 10)
    c.drawString(margin, 40, "Certified by Forensix, LLC")
    c.save()