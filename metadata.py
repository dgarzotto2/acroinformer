import logging
from typing import Optional, Dict
from PyPDF2 import PdfReader
from .utils.xml_utils import parse_xmp_toolkit

logger = logging.getLogger(__name__)

def extract_metadata(file_path: str, file_bytes: bytes) -> Dict[str, Optional[str]]:
    """
    Extract PDF metadata and forensic flags.
    Validates PDF header, parses XMP, detects AcroForm/signatures/overlays.
    Returns a dict of:
      - producer, creator, creation_date, mod_date, xmp_toolkit
      - has_acroform, has_signature_field, signature_overlay_detected
    """
    # 10. Security: Validate header
    try:
        with open(file_path, 'rb') as f:
            if not f.read(5) == b"%PDF-":
                logger.warning(f"{file_path} may not be a PDF.")
    except Exception as e:
        logger.error("Header check failed", exc_info=e)

    # Load PDF with error handling (2)
    try:
        reader = PdfReader(file_path)
    except Exception as e:
        logger.error(f"Failed to parse PDF: {e}", exc_info=e)
        return {"error": str(e)}

    info     = reader.metadata or {}
    raw_xmp  = reader.xmp_metadata

    # 6. Shared utility for XMP (refactored)
    xmp_toolkit = parse_xmp_toolkit(raw_xmp) if raw_xmp else None

    # 5. AcroForm & signature‐field detection
    root = reader.trailer.get("/Root", {})
    has_acroform = "/AcroForm" in root
    has_signature_field = False
    if has_acroform:
        for fld in root["/AcroForm"].get("/Fields", []):
            try:
                if fld.get_object().get("/FT") == "/Sig":
                    has_signature_field = True
                    break
            except Exception:
                logger.debug("Field parse error", exc_info=True)

    # 5. Overlay detection (scan /Stamp and /AP)
    signature_overlay_detected = False
    for page in reader.pages:
        for annot in page.get("/Annots", []) or []:
            try:
                obj = annot.get_object()
                subtype = obj.get("/Subtype")
                if subtype in ("/Stamp", "/Sig") or obj.get("/AP"):
                    signature_overlay_detected = True
                    break
            except Exception:
                logger.debug("Annot parse error", exc_info=True)
        if signature_overlay_detected:
            break

    # Core fields
    return {
        "producer":           info.get("/Producer"),
        "creator":            info.get("/Creator"),
        "creation_date":      info.get("/CreationDate"),
        "mod_date":           info.get("/ModDate"),
        "xmp_toolkit":        xmp_toolkit,
        "has_acroform":       has_acroform,
        "has_signature_field":has_signature_field,
        "signature_overlay_detected": signature_overlay_detected
    }