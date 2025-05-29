# metadata.py

import re
import zlib
import logging
from typing import Any, Dict, Optional
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

def _resolve(obj: Any) -> Any:
    """
    Recursively dereference a PyPDF2 IndirectObject (or list of them)
    into plain Python dicts/lists. Returns {} for anything missing.
    """
    try:
        # Handle a single IndirectObject
        if hasattr(obj, "get_object"):
            return _resolve(obj.get_object())
    except Exception:
        return {}
    # Handle lists of objects
    if isinstance(obj, list):
        return [_resolve(o) for o in obj]
    # Fallback to obj itself
    return obj or {}

def extract_metadata(file_path: str, file_bytes: bytes) -> Dict[str, Any]:
    """
    Extract forensic PDF metadata with safe dereferencing of all indirect objects.
    """
    reader = PdfReader(file_path)
    info = reader.metadata or {}
    raw_xmp = reader.xmp_metadata or b""

    # 1) DocumentID
    docid: Optional[str] = None
    try:
        ids = reader.trailer.get("/ID")
        if isinstance(ids, list) and ids:
            docid = ids[0]
    except Exception:
        pass

    # 2) XMP toolkit
    try:
        xmp_toolkit = parse_xmp_toolkit(raw_xmp)
    except Exception:
        xmp_toolkit = None

    # 3) Root dictionary
    root = _resolve(reader.trailer.get("/Root"))

    # 4) AcroForm & signature-field
    acro = _resolve(root.get("/AcroForm"))
    has_acroform = bool(acro)
    has_sigfield = False
    for fld in acro.get("/Fields", []) or []:
        fobj = _resolve(fld)
        if fobj.get("/FT") == "/Sig":
            has_sigfield = True
            break

    # 5) Signature-overlay detection
    signature_overlay = False
    for page in reader.pages:
        annots = _resolve(page.get("/Annots")) or []
        for annot in annots:
            aobj = _resolve(annot)
            if aobj.get("/Subtype") in ("/Stamp", "/Sig") or aobj.get("/AP"):
                signature_overlay = True
                break
        if signature_overlay:
            break

    # 6) Core metadata fields
    producer      = info.get("/Producer")
    creator       = info.get("/Creator")
    creation_date = info.get("/CreationDate")
    mod_date      = info.get("/ModDate")

    # 7) Hidden-library usage
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