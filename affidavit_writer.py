# affidavit_writer.py

from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
import io
import datetime

def generate_affidavit_pdf(result):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=LETTER)
    c.setFont("Helvetica", 11)
    width, height = LETTER
    y = height - 50

    def writeln(text, indent=0):
        nonlocal y
        c.drawString(50 + indent, y, text)
        y -= 15

    c.setFont("Helvetica-Bold", 14)
    writeln("Forensic Affidavit Summary")
    c.setFont("Helvetica", 11)
    writeln(f"Document: {result['filename']}")
    writeln(f"Date: {datetime.datetime.utcnow().isoformat()} UTC")
    writeln("")

    writeln("Metadata:", 10)
    for k, v in result["metadata"].items():
        writeln(f"- {k}: {v}", 20)

    writeln("\nSuppression Flags:", 10)
    for f in result["suppression_flags"]:
        writeln(f"- {f}", 20)

    writeln("\nLicense Flags:", 10)
    for f in result["license_flags"]:
        writeln(f"- {f}", 20)

    writeln("\nEntities Extracted:", 10)
    for k, v in result["entities"].items():
        writeln(f"- {k}: {v}", 20)

    writeln("\nSummary:", 10)
    for line in result["summary"].split("\n"):
        writeln(f"{line}", 20)

    writeln("\nCertified by Forensix, LLC", 10)
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()