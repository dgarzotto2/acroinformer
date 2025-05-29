from PyPDF2 import PdfReader
from typing import Dict
import re

def extract_metadata(pdf_path: str) -> Dict:
    result = {
        "producer": None,
        "creator_tool": None,
        "has_xfa": False,
        "has_launch_action": False,
        "has_javascript": False,
        "contains_cid_fonts": False,
        "unicode_map_missing": False,
        "suspicious_tool_detected": False,
        "byte_range_mismatch": False,
        "agpl_pdf_engine": False,
        "notes": [],
    }

    try:
        reader = PdfReader(pdf_path)

        # Basic fields
        meta = reader.metadata or {}
        result["producer"] = str(meta.get("/Producer", "")).strip()
        result["creator_tool"] = str(meta.get("/Creator", "")).strip()

        # Suspicious producers (for AGPL/GPL flag)
        suspicious_tools = ["iText", "iTextSharp", "ABCpdf", "BFO", "PDFBox", "Prince", "Ghostscript"]
        for tool in suspicious_tools:
            if tool.lower() in result["producer"].lower() or tool.lower() in result["creator_tool"].lower():
                result["suspicious_tool_detected"] = True
                if tool.lower() in ["itext", "ghostscript", "pdfbox"]:
                    result["agpl_pdf_engine"] = True
                result["notes"].append(f"Suspicious PDF producer detected: {tool}")
                break

        # Check for CID Fonts
        for page in reader.pages:
            try:
                resources = page.get("/Resources")
                if resources:
                    fonts = resources.get("/Font")
                    if fonts:
                        for font in fonts.values():
                            font_obj = font.get_object()
                            font_base = str(font_obj.get("/BaseFont", ""))
                            if "/CIDFont" in str(font_obj) or "CID" in font_base:
                                result["contains_cid_fonts"] = True
                                result["notes"].append("CID font structure detected")
                                break
            except Exception:
                continue

        # Check for LaunchAction or embedded JS
        for page in reader.pages:
            try:
                annots = page.get("/Annots")
                if annots:
                    for annot in annots:
                        annot_obj = annot.get_object()
                        a = annot_obj.get("/A")
                        if a:
                            if a.get("/S") == "/Launch":
                                result["has_launch_action"] = True
                                result["notes"].append("LaunchAction detected in annotation")
            except Exception:
                continue

        if "/Names" in reader.trailer.get("/Root", {}):
            names = reader.trailer["/Root"]["/Names"]
            if "/JavaScript" in names:
                result["has_javascript"] = True
                result["notes"].append("Embedded JavaScript found")

        # Check ByteRange formatting
        br = meta.get("/ByteRange")
        if isinstance(br, str) and len(br.split()) > 4:
            result["byte_range_mismatch"] = True
            result["notes"].append("Suspicious ByteRange length")

        # Check for XFA
        if "/AcroForm" in reader.trailer.get("/Root", {}):
            af = reader.trailer["/Root"]["/AcroForm"]
            if "/XFA" in af:
                result["has_xfa"] = True
                result["notes"].append("XFA form structure detected")

        # Unicode map detection (if fonts but no /ToUnicode)
        if result["contains_cid_fonts"]:
            unicode_maps = 0
            for obj in reader.objects.values():
                if isinstance(obj, dict) and "/ToUnicode" in obj:
                    unicode_maps += 1
            if unicode_maps == 0:
                result["unicode_map_missing"] = True
                result["notes"].append("CID fonts used but /ToUnicode maps are missing")

    except Exception as e:
        result["notes"].append(f"Error during metadata extraction: {e}")

    return result