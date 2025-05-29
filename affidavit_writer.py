# affidavit_writer.py

from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from datetime import datetime
import os

def generate_affidavit(meta1, meta2, score, reasons, output_path):
    try:
        c = canvas.Canvas(output_path, pagesize=LETTER)
        width, height = LETTER

        # Title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(72, height - 72, "Forensic PDF Affidavit")

        # Timestamp
        c.setFont("Helvetica", 10)
        c.drawString(72, height - 90, f"Generated on: {datetime.utcnow().isoformat()} UTC")

        # Section: File Metadata Summary
        c.setFont("Helvetica-Bold", 12)
        c.drawString(72, height - 120, "File Comparison Summary:")

        y = height - 140
        c.setFont("Helvetica", 10)

        c.drawString(72, y, f"File A SHA-256: {meta1.get('sha256')}")
        y -= 15
        c.drawString(72, y, f"File B SHA-256: {meta2.get('sha256')}")
        y -= 30

        c.drawString(72, y, f"Creation A: {meta1.get('creation_time')}")
        y -= 15
        c.drawString(72, y, f"Creation B: {meta2.get('creation_time')}")
        y -= 30

        c.drawString(72, y, f"DocumentID A: {meta1.get('xmp_document_id')}")
        y -= 15
        c.drawString(72, y, f"DocumentID B: {meta2.get('xmp_document_id')}")
        y -= 30

        c.drawString(72, y, f"InstanceID A: {meta1.get('xmp_instance_id')}")
        y -= 15
        c.drawString(72, y, f"InstanceID B: {meta2.get('xmp_instance_id')}")
        y -= 30

        # Suspicion Score
        c.setFont("Helvetica-Bold", 12)
        c.drawString(72, y, f"Suspicion Score: {score}")
        y -= 25

        # Section: Reasons
        c.setFont("Helvetica-Bold", 12)
        c.drawString(72, y, "Reasons for Suspicion:")
        y -= 20
        c.setFont("Helvetica", 10)
        for reason in reasons:
            if y < 100:
                c.showPage()
                y = height - 72
            c.drawString(90, y, f"- {reason}")
            y -= 15

        # Footer: Certification
        y = 100
        c.setFont("Helvetica-Oblique", 9)
        c.drawString(72, y, "This report was generated using best forensic practices and tooling meeting or exceeding")
        c.drawString(72, y - 12, "Swigdoc standards. Certified by Forensix, LLC.")

        c.save()

    except Exception as e:
        print(f"[ERROR] Failed to generate affidavit: {e}")