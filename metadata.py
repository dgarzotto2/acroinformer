# metadata.py

import re
import zlib
import logging
from typing import Optional, Dict, Any
from PyPDF2 import PdfReader
from utils.xml_utils import parse_xmp_toolkit

logger = logging.getLogger(__name__)

def _find_known_libs(raw: bytes) -> bool:
    """
    Scan raw PDF bytes (and inside Flate‐decoded streams) for footprints of
    programmatic PDF libraries:
      - iText / Lowagie / AGPL
      - PDFBox / Apache PDFBox
      - BFO (Big Faceless)
      - WebSupergoo / ABCpdf
    """
    patterns = [
        b"itext", b"lowagie", b"agpl",
        b"pdfbox", b"apache pdfbox",
        b"bfo", b"big faceless",
        b"websupergoo", b"abcpdf"
    ]
    for pat in patterns:
        if re.search(pat, raw, re.IGNORECASE):
            return True

    # Also inspect Flate streams
    for m in re.finditer(b"stream(.*?)endstream", raw, re.DOTALL):
        chunk = m.group(1).strip(b"\r\n")
        try:
            dec = zlib.decompress(chunk)
            for pat in patterns:
                if re.search(pat, dec, re.IGNORECASE):
                    return True
        except Exception:
            continue

    return False

def extract_metadata(file_path: str, file_bytes: bytes) -> Dict[str, Any]:
    """
    Extract PDF metadata and forensic flags, including:
      - CreationDate, ModDate, Producer, Creator
      - Adobe XMP Toolkit
      - AcroForm presence & /Sig fields
      - Signature-overlay annotations
      - Hidden PDF-library usage (iText, PDFBox, BFO, ABCpdf, etc.)
    """
    reader = PdfReader(file_path)
    info     = reader.metadata or {}
    raw_xmp  = reader.xmp_metadata or b""

    # DocumentID from trailer /ID array
    docid = None
    try:
        id_arr = reader.trailer.get("/ID")
        if isinstance(id_arr, list) and id_arr:
            docid = id_arr[0]
    except Exception:
        pass

    # Parse XMP Toolkit
    xmp_toolkit = parse_xmp_toolkit(raw_xmp) if raw_xmp else None

    # AcroForm & signature-field detection
    root         = reader.trailer.get("/Root", {})
    has_acroform = "/AcroForm" in root
    has_sigfield = False
    if has_acroform:
        for fld in root["/AcroForm"].get("/Fields", []) or []:
            try:
                if fld.get_object().get("/FT") == "/Sig":
                    has_sigfield = True
                    break
            except Exception:
                continue

    # Signature-overlay detection (/Stamp or appearance streams)
    signature_overlay = False
    for page in reader.pages:
        for annot in page.get("/Annots", []) or []:
            try:
                obj = annot.get_object()
                if obj.get("/Subtype") in ("/Stamp", "/Sig") or obj.get("/AP"):
                    signature_overlay = True
                    break
            except Exception:
                continue
        if signature_overlay:
            break

    # Core metadata
    producer      = info.get("/Producer")
    creator       = info.get("/Creator")
    creation_date = info.get("/CreationDate")
    mod_date      = info.get("/ModDate")

    # Hidden PDF-library usage
    hidden_lib_usage = _find_known_libs(file_bytes)

    return {
        "document_id":                docid,
        "producer":                   producer,
        "creator":                    creator,
        "creation_date":              creation_date,
        "mod_date":                   mod_date,
        "xmp_toolkit":                xmp_toolkit,
        "has_acroform":               has_acroform,
        "has_signature_field":        has_sigfield,
        "signature_overlay_detected": signature_overlay,
        "hidden_lib_usage":           hidden_lib_usage
    }