# license_checker.py

def check_pdf_license(metadata):
    flags = []
    agpl_gpl_tools = {
        "iText": "AGPL",
        "iTextSharp": "AGPL",
        "Ghostscript": "GPL",
        "TCPDF": "LGPL",
        "PdfTk": "GPL",
        "PDFBox": "Apache (watch for misuse)",
        "Apache PDFBox": "Apache (watch for misuse)",
    }

    producer = metadata.get("producer", "") or ""
    creator = metadata.get("creator", "") or ""
    xmp_tool = metadata.get("xmp_toolkit", "") or ""

    for tool, license in agpl_gpl_tools.items():
        if tool.lower() in producer.lower() or tool.lower() in creator.lower() or tool.lower() in xmp_tool.lower():
            flags.append(f"{tool} detected – {license} license may prohibit commercial or legal use.")

    return flags