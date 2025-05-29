from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def build_pdf_report(output_path: str, metadata: dict):
    """
    Generates a one-page PDF summary of metadata.
    """
    doc = SimpleDocTemplate(output_path)
    styles = getSampleStyleSheet()
    story = []
    story.append(Paragraph("Forensic PDF Metadata Report", styles["Title"]))
    story.append(Spacer(1, 12))
    for k, v in metadata.items():
        story.append(Paragraph(f"<b>{k}:</b> {v}", styles["Normal"]))
    doc.build(story)