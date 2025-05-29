# affidavit_writer.py

from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from datetime import datetime
import os

def generate_affidavit(meta_a, meta_b, score, reasons, output_path):
    c = canvas.Canvas(output_path, pagesize=LETTER)
    width, height = LETTER
    line = height - 50
    indent = 50

    def write_line(text, offset=15):
        nonlocal line
        c.drawString(indent, line, text)
        line -= offset

    # Title and cert
    c.setFont("Helvetica-Bold", 14)
    write_line("Forensic Affidavit: PDF Document Comparison")
    c.setFont("Helvetica", 10)
    write_line(f"Generated: {datetime.utcnow().isoformat()} UTC")

    write_line("Certified by Mile2 Investigations")
    write_line("Prepared by David Garzotto, Founder, Forensix, LLC")
    write_line("This report was produced using best forensic practices to the best of my ability.")
    write_line("This report conforms to methods consistent with Swigdoc standards.")

    # Document A
    write_line("")
    c.setFont("Helvetica-Bold", 12)
    write_line("Document A Metadata")
    c.setFont("Helvetica", 10)
    for k in ['filename', 'sha256', 'creation_date', 'xmp_document_id', 'xmp_instance_id']:
        write_line(f"{k}: {meta_a.get(k, 'N/A')}")

    # Document B
    write_line("")
    c.setFont("Helvetica-Bold", 12)
    write_line("Document B Metadata")
    c.setFont("Helvetica", 10)
    for k in ['filename', 'sha256', 'creation_date', 'xmp_document_id', 'xmp_instance_id']:
        write_line(f"{k}: {meta_b.get(k, 'N/A')}")

    # Score and reasoning
    write_line("")
    c.setFont("Helvetica-Bold", 12)
    write_line("Forensic Match Score")
    c.setFont("Helvetica", 10)
    write_line(f"Score: {score} / 100")
    write_line(f"Flagged as suspicious: {'YES' if score > 50 else 'NO'}")

    write_line("")
    c.setFont("Helvetica-Bold", 12)
    write_line("Indicators of Similarity or Tampering")
    c.setFont("Helvetica", 10)
    if reasons:
        for r in reasons:
            write_line(f"- {r}", offset=13)
    else:
        write_line("No overlapping metadata or known match indicators detected.")

    write_line("")
    c.setFont("Helvetica", 8)
    write_line("This affidavit is automatically generated for forensic comparison purposes.")

    c.save()