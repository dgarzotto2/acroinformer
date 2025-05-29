# pdf_license_fingerprint.py

import re
from typing import Dict, Optional

KNOWN_AGPL_CREATORS = {
    "iText": "AGPL",
    "iTextSharp": "AGPL",
    "BFO": "AGPL",
    "Big Faceless": "AGPL",
    "Ghostscript": "GPL",
    "GPL Ghostscript": "GPL",
    "TCPDF": "LGPL",
    "Apache PDFBox": "Apache 2.0",
    "pdfTeX": "GPL",
    "PdfLatex": "GPL",
    "PDFreactor": "AGPL",
    "DocRaptor": "AGPL",
    "wkhtmltopdf": "LGPL",
    "PrinceXML": "Proprietary"
}

# These keywords will trigger detection in the metadata fields
CREATOR_PATTERNS = [re.escape(k) for k in KNOWN_AGPL_CREATORS.keys()]
CREATOR_REGEX = re.compile(r"|".join(CREATOR_PATTERNS), re.IGNORECASE)

def detect_pdf_license_fingerprint(metadata: Dict[str, str]) -> Dict[str, Optional[str]]:
    """
    Scans PDF metadata for known AGPL/GPL/Proprietary tools.
    Returns a dict with any matched library and associated license.
    """
    fields_to_check = [
        metadata.get("/Producer", ""),
        metadata.get("/Creator", ""),
        metadata.get("xmp:CreatorTool", "")
    ]

    for field in fields_to_check:
        match = CREATOR_REGEX.search(field)
        if match:
            matched_tool = match.group(0)
            license_type = KNOWN_AGPL_CREATORS.get(matched_tool, "Unknown")
            return {
                "matched_tool": matched_tool,
                "license_type": license_type,
                "licensing_flag": f"Document generated using {matched_tool} ({license_type})"
            }

    return {
        "matched_tool": None,
        "license_type": None,
        "licensing_flag": None
    }