# affidavit_writer.py

from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from datetime import datetime
import os

def generate_affidavit(meta1, meta2, score, reasons, output_path):
    """
    Generates a PDF affidavit comparing metadata from two documents and listing suspicious similarities.
    """
    c = canvas.Canvas(output_path, pagesize=LETTER)
    width, height = LETTER

    def draw_header():
        c.setFont("Helvetica-Bold", 14)
        c.drawString(72, height - 72, "Forensic Affidavit of PDF Metadata Comparison")
        c.setFont("Helvetica", 10)
        c.drawString(72, height - 90, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    def draw_section(title, lines, y_start):
        y = y_start
        c.setFont("Helvetica-Bold", 12)
        c.drawString(72, y, title)
        c.setFont("Helvetica", 10)
        y -= 16
        for line in lines:
            c.drawString(80, y, line)
            y -= 14
        return y - 10

    draw_header()
    y = height - 120

    # File 1 summary
    lines1 = [f"{k}: {v}" for k, v in meta1.items() if isinstance(v, str) or isinstance(v, list)]
    y = draw_section("Document 1 Metadata", lines1, y)

    # File 2 summary
    lines2 = [f"{k}: {v}" for k, v in meta2.items() if isinstance(v, str) or isinstance(v, list)]
    y = draw_section("Document 2 Metadata", lines2, y)

    # Suspicion score and reasons
    reason_lines = [f"Score: {score}"]
    reason_lines += [f"Reason: {r}" for r in reasons]
    y = draw_section("Suspicion Score & Justifications", reason_lines, y)

    # Footer certification
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(72, 80, "Certified by Forensix, LLC")
    c.drawString(72, 66, "This affidavit was generated using industry-standard methods and best practices,")
    c.drawString(72, 52, "following the guidelines outlined in the Swigdoc framework for digital forensic evidence.")

    c.save()