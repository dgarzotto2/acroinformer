# license_checker.py

def check_pdf_license(metadata):
    flags = []
    producer = metadata.get("/Producer", "").lower()
    creator = metadata.get("/Creator", "").lower()

    agpl_tools = ["itext", "bfo", "ghostscript", "qpdf", "pdfreactor"]

    for tool in agpl_tools:
        if tool in producer or tool in creator:
            flags.append(f"{tool.upper()} (AGPL/GPL) detected")

    return flags