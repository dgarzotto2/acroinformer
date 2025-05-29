# affidavit_writer.py

from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from datetime import datetime
import socket

def write_affidavit(output_path, metadata, filename, sha256, findings, analyst_title="Founder, Forensix, LLC"):
    c = canvas.Canvas(output_path, pagesize=LETTER)
    width, height = LETTER
    margin = 50
    y = height - margin

    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, y, "Forensic Document Affidavit")
    y -= 30

    c.setFont("Helvetica", 10)
    c.drawString(margin, y, f"Date of Analysis: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    y -= 15
    c.drawString(margin, y, f"Analyzed File: {filename}")
    y -= 15
    c.drawString(margin, y, f"SHA-256: {sha256}")
    y -= 15
    c.drawString(margin, y, f"Hostname: {socket.gethostname()}")
    y -= 25

    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Findings:")
    y -= 15

    c.setFont("Helvetica", 10)
    for line in findings:
        for subline in split_line(line, width - 2 * margin, c):
            c.drawString(margin, y, subline)
            y -= 12
            if y < margin:
                c.showPage()
                y = height - margin

    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Certification:")
    y -= 15

    cert_text = (
        f"I hereby certify that the analysis above was conducted using industry-standard forensic methods "
        f"to the best of my ability. All observations are based on technical evidence recovered from the provided file. "
        f"\n\nCertified by Forensix, LLC"
    )
    for subline in split_line(cert_text, width - 2 * margin, c):
        c.drawString(margin, y, subline)
        y -= 12

    y -= 30
    c.drawString(margin, y, "Signature: ____________________________")
    y -= 15
    c.drawString(margin, y, f"Title: {analyst_title}")
    y -= 15
    c.drawString(margin, y, "Date: _________________________________")

    c.showPage()
    c.save()

def split_line(text, max_width, canvas_obj):
    words = text.split()
    lines = []
    line = ""
    for word in words:
        if canvas_obj.stringWidth(line + " " + word) < max_width:
            line += " " + word if line else word
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines