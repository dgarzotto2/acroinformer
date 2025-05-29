import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime

def generate_pdf_report(output_path, filename, metadata_result):
    filepath = os.path.join(output_path, f"{filename}_forensic_report.pdf")
    c = canvas.Canvas(filepath, pagesize=letter)
    width, height = letter
    line_height = 14
    y = height - 40

    def draw_line(label, value, indent=0):
        nonlocal y
        c.drawString(40 + indent, y, f"{label}: {value}")
        y -= line_height

    def draw_section_title(title):
        nonlocal y
        y -= 10
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, y, title)
        c.setFont("Helvetica", 10)
        y -= line_height

    # Title
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, f"Forensic PDF Metadata Report")
    y -= line_height
    c.setFont("Helvetica", 10)
    c.drawString(40, y, f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    y -= line_height * 2

    draw_section_title("General Metadata")
    meta = metadata_result.get("metadata", {})
    for k, v in meta.items():
        draw_line(k, str(v)[:80])

    draw_section_title("Obfuscation & Tamper Flags")
    draw_line("Obfuscation Libraries", ", ".join(metadata_result.get("obfuscation_libraries", [])) or "None")
    draw_line("Hidden Obfuscator Detected", "Yes" if metadata_result.get("hidden_lib_usage") else "No")
    draw_line("ByteRange Mismatch", "Yes" if metadata_result.get("byte_range_mismatch") else "No")
    draw_line("CID Font Suppression", "Yes" if metadata_result.get("font_warnings") else "No")
    draw_line("XFA Fields Present", "Yes" if metadata_result.get("has_xfa") else "No")
    draw_line("AcroForm Present", "Yes" if metadata_result.get("has_acroform") else "No")
    draw_line("Embedded Files", "Yes" if metadata_result.get("embedded_files") else "No")

    js_snippets = metadata_result.get("js", [])
    draw_section_title("Embedded JavaScript")
    if js_snippets:
        for js in js_snippets:
            draw_line("Script", js[:80], indent=10)
    else:
        draw_line("Script", "None detected")

    notes = metadata_result.get("notes", [])
    draw_section_title("Forensic Notes & Warnings")
    if notes:
        for note in notes:
            draw_line("-", note)
    else:
        draw_line("-", "None")

    c.save()
    return filepath