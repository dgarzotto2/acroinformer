from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
import os
import tempfile
from datetime import datetime

def render_affidavit(metadata_list, acroform_list):
    temp_dir = tempfile.mkdtemp(dir="/tmp")
    affidavit_path = os.path.join(temp_dir, "forensic_affidavit.pdf")

    c = canvas.Canvas(affidavit_path, pagesize=LETTER)
    width, height = LETTER

    c.setFont("Helvetica-Bold", 14)
    c.drawString(72, height - 72, "Forensic Document Analysis Affidavit")

    c.setFont("Helvetica", 10)
    c.drawString(72, height - 90, f"Prepared: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    c.drawString(72, height - 105, f"Analyst Toolset: AcroInformer | Report Format: PDF Affidavit")

    y = height - 130

    for idx, meta in enumerate(metadata_list):
        c.setFont("Helvetica-Bold", 12)
        c.drawString(72, y, f"Document #{idx + 1}: {meta.get('filename', 'Unknown')}")
        y -= 15

        c.setFont("Helvetica", 10)
        c.drawString(80, y, f"Producer: {meta.get('producer', 'N/A')}")
        y -= 12
        c.drawString(80, y, f"Created: {meta.get('created', 'N/A')} | Modified: {meta.get('modified', 'N/A')}")
        y -= 12
        c.drawString(80, y, f"XMP Toolkit: {meta.get('xmp_toolkit', 'N/A')}")
        y -= 12

        if meta.get("flags"):
            for flag in meta["flags"]:
                c.setFillColorRGB(1, 0, 0)
                c.drawString(90, y, f"[Tamper Flag] {flag}")
                c.setFillColorRGB(0, 0, 0)
                y -= 12

        y -= 10

    c.setFont("Helvetica-Bold", 12)
    c.drawString(72, y, "AcroForm Audit Results")
    y -= 15

    for acro in acroform_list:
        c.setFont("Helvetica-Bold", 10)
        c.drawString(80, y, f"File: {acro['filename']}")
        y -= 12

        c.setFont("Helvetica", 10)
        if not acro["has_acroform"]:
            c.drawString(90, y, "No AcroForm present.")
            y -= 12
        else:
            c.drawString(90, y, f"Form Fields: {', '.join(acro['field_names']) or 'None'}")
            y -= 12
            if acro["empty_fields"]:
                c.drawString(90, y, f"Empty Fields: {', '.join(acro['empty_fields'])}")
                y -= 12
            if acro["signature_fields"]:
                c.drawString(90, y, f"Signature Fields: {', '.join(acro['signature_fields'])}")
                y -= 12
            if acro["synthetic_warnings"]:
                for warn in acro["synthetic_warnings"]:
                    c.setFillColorRGB(1, 0, 0)
                    c.drawString(100, y, f"[Synthetic Warning] {warn}")
                    c.setFillColorRGB(0, 0, 0)
                    y -= 12

        y -= 10

        if y < 100:
            c.showPage()
            y = height - 72

    # Certification block
    c.setFont("Helvetica-Bold", 11)
    c.drawString(72, 72, "Certification:")
    c.setFont("Helvetica", 10)
    c.drawString(72, 58, "This affidavit was generated using best forensic practices with automated PDF validation tools.")
    c.drawString(72, 45, "Certified by Forensix, LLC.")

    c.save()
    return affidavit_path