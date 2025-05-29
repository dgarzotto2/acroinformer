from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
import os

def generate_affidavit_pdf(metadata: dict, output_dir: str) -> str:
    filename = metadata.get("filename", "document")
    outfile = os.path.join(output_dir, f"{filename.replace('.pdf', '')}_affidavit.pdf")
    c = canvas.Canvas(outfile, pagesize=LETTER)

    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, 750, "Forensic Affidavit – Document Analysis")
    c.setFont("Helvetica", 11)

    y = 720
    fields = {
        "Filename": metadata.get("filename", ""),
        "SHA-256 Hash": metadata.get("sha256", ""),
        "Producer": metadata.get("producer", "—"),
        "Creator": metadata.get("creator", "—"),
        "PDF Toolkit": metadata.get("toolkit", "—"),
        "XMP Toolkit": metadata.get("xmp_toolkit", "—"),
        "Creation Date": metadata.get("creation_date", "—"),
        "Modification Date": metadata.get("mod_date", "—"),
        "AcroForm Present": str(metadata.get("has_acroform", False)),
        "Signature Field": str(metadata.get("has_signature_field", False)),
        "Tamper Risk": metadata.get("tamper_risk", "None"),
    }

    for label, value in fields.items():
        c.drawString(72, y, f"{label}: {value}")
        y -= 18

    c.setFont("Helvetica-Oblique", 10)
    c.drawString(72, 120, "Certified forensic review conducted using Swigdoc protocol and PDF metadata extraction best practices.")
    c.drawString(72, 105, "Certified by Forensix, LLC")

    c.showPage()
    c.save()
    return outfile