from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
import hashlib
import os
import datetime

def generate_affidavit(report_data, output_path):
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    flow = []

    now = datetime.datetime.now().strftime("%B %d, %Y %H:%M")

    flow.append(Paragraph("<b>Forensic Audit Report</b>", styles["Title"]))
    flow.append(Paragraph(f"<b>Date:</b> {now}", styles["Normal"]))
    flow.append(Spacer(1, 12))

    for item in report_data:
        flow.append(Paragraph(f"<b>Filename:</b> {item['filename']}", styles["Heading2"]))
        flow.append(Paragraph(f"<b>SHA-256:</b> {item['sha256']}", styles["Code"]))
        flow.append(Spacer(1, 6))

        flow.append(Paragraph("<b>Metadata:</b>", styles["Heading3"]))
        flow.append(Paragraph(f"- Title: {item.get('title', 'N/A')}", styles["Normal"]))
        flow.append(Paragraph(f"- Author: {item.get('author', 'N/A')}", styles["Normal"]))
        flow.append(Paragraph(f"- Producer: {item.get('producer', 'N/A')}", styles["Normal"]))
        flow.append(Paragraph(f"- Creator: {item.get('creator', 'N/A')}", styles["Normal"]))
        flow.append(Paragraph(f"- Creation Date: {item.get('creation_date', 'N/A')}", styles["Normal"]))
        flow.append(Paragraph(f"- Modification Date: {item.get('mod_date', 'N/A')}", styles["Normal"]))
        flow.append(Paragraph(f"- Document ID: {item.get('doc_id', 'N/A')}", styles["Normal"]))
        flow.append(Spacer(1, 6))

        flow.append(Paragraph("<b>Entity Summary:</b>", styles["Heading3"]))
        g_list = ", ".join(item['entities'].get("grantors", [])) or "None"
        gr_list = ", ".join(item['entities'].get("grantees", [])) or "None"
        flow.append(Paragraph(f"- Grantors: {g_list}", styles["Normal"]))
        flow.append(Paragraph(f"- Grantees: {gr_list}", styles["Normal"]))
        flow.append(Spacer(1, 6))

        flow.append(Paragraph("<b>Obfuscation Flags:</b>", styles["Heading3"]))
        flow.append(Paragraph(f"- CID Fonts Detected: {'Yes' if item['cid_font'] else 'No'}", styles["Normal"]))

        if item['fraud_flags']:
            flow.append(Spacer(1, 6))
            flow.append(Paragraph("<b>🚨 Detected Forensic Risk Indicators:</b>", styles["Heading3"]))
            for flag in item['fraud_flags']:
                flow.append(Paragraph(f"• {flag}", styles["Bullet"]))
        else:
            flow.append(Paragraph("✅ No significant obfuscation or tampering found.", styles["Normal"]))

        flow.append(PageBreak())

    doc.build(flow)
    return output_path