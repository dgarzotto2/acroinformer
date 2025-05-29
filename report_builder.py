import os
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from datetime import datetime

def generate_forensic_report(output_path, evidence_bundle):
    """
    Generate a forensic audit report as a PDF using ReportLab.
    Args:
        output_path: full path to save the PDF
        evidence_bundle: dict with keys:
            - metadata
            - xmp_findings
            - acroform_audit
            - signature_results
            - gpt_summary
            - hash_results
    """
    c = canvas.Canvas(output_path, pagesize=LETTER)
    width, height = LETTER

    def write_line(text, y_offset, bold=False):
        if bold:
            c.setFont("Helvetica-Bold", 10)
        else:
            c.setFont("Helvetica", 10)
        c.drawString(1 * inch, y_offset, text)

    y = height - inch
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1 * inch, y, "Forensic Document Audit Report")
    y -= 20
    c.setFont("Helvetica", 10)
    c.drawString(1 * inch, y, f"Generated: {datetime.utcnow().isoformat()} UTC")
    y -= 30

    def section(title, items):
        nonlocal y
        c.setFont("Helvetica-Bold", 12)
        c.drawString(1 * inch, y, title)
        y -= 20
        c.setFont("Helvetica", 10)
        if not items:
            c.drawString(1 * inch, y, "No findings.")
            y -= 15
        else:
            for item in items:
                if y < inch:
                    c.showPage()
                    y = height - inch
                c.drawString(1 * inch, y, f"- {item}")
                y -= 15
        y -= 10

    # Sections
    section("📁 Metadata Findings", evidence_bundle.get("metadata", []))
    section("🧬 XMP Consistency Issues", evidence_bundle.get("xmp_findings", []))
    section("🧪 AcroForm/XFA Audit", evidence_bundle.get("acroform_audit", []))
    section("🔏 Signature Validation", evidence_bundle.get("signature_results", []))
    section("🧠 GPT Observations", evidence_bundle.get("gpt_summary", []))
    section("🔐 Hash/Integrity", evidence_bundle.get("hash_results", []))

    c.setFont("Helvetica-Oblique", 8)
    c.drawString(1 * inch, inch / 2, "Prepared by Forensix, LLC | Certified by Mile2 Investigations")

    c.save()