# metadata.py

import re
import zlib
import logging
from typing import Dict, Any, Optional
from PyPDF2 import PdfReader
from utils.xml_utils import parse_xmp_toolkit

logger = logging.getLogger(__name__)

def _find_known_libs(raw: bytes) -> bool:
    patterns = [
        b"itext", b"lowagie", b"agpl",
        b"pdfbox", b"apache pdfbox",
        b"bfo", b"big faceless",
        b"websupergoo", b"abcpdf"
    ]
    for pat in patterns:
        if re.search(pat, raw, re.IGNORECASE):
            return True
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
    Extract PDF metadata and forensic flags, with proper IndirectObject dereferencing.
    """
    reader = PdfReader(file_path)
    info     = reader.metadata or {}
    raw_xmp  = reader.xmp_metadata or b""

    # DocumentID
    docid: Optional[str] = None
    try:
        id_arr = reader.trailer.get("/ID")
        if isinstance(id_arr, list) and id_arr:
            docid = id_arr[0]
    except Exception:
        pass

    # XMP Toolkit
    try:
        xmp_toolkit = parse_xmp_toolkit(raw_xmp)
    except Exception:
        xmp_toolkit = None

    # Dereference /Root
    root_obj = reader.trailer.get("/Root")
    try:
        root = root_obj.get_object() if hasattr(root_obj, "get_object") else root_obj or {}
    except Exception:
        root = {}

    # Detect AcroForm & signature fields
    has_acroform = False
    has_sigfield = False
    acro_dict: Dict = {}
    if "/AcroForm" in root:
        has_acroform = True
        af = root.get("/AcroForm")
        try:
            acro_dict = af.get_object() if hasattr(af, "get_object") else af or {}
        except Exception:
            acro_dict = {}
        for fld in acro_dict.get("/Fields", []) or []:
            try:
                fobj = fld.get_object() if hasattr(fld, "get_object") else fld
                if fobj.get("/FT") == "/Sig":
                    has_sigfield = True
                    break
            except Exception:
                continue

    # Signature-overlay (/Stamp or /AP)
    signature_overlay = False
    for page in reader.pages:
        annots = page.get("/Annots", []) or []
        for annot in annots:
            try:
                aobj = annot.get_object() if hasattr(annot, "get_object") else annot
                if aobj.get("/Subtype") in ("/Stamp", "/Sig") or aobj.get("/AP"):
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