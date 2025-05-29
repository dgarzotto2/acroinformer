# hidden_text.py

import re
from typing import List
from PyPDF2 import PdfReader
from utils.xml_utils import parse_xmp_toolkit

# These imports assume you’ve placed the kukatwo modules under kukatwo/
from kukatwo.ascii85_stream_reconstructor import reconstruct_ascii85
from kukatwo.hidden_layer_scanner import scan_invisible_text
from kukatwo.unicode_mapper import map_zero_width
from kukatwo.hidden_struct_scanner import scan_struct_tree
from kukatwo.suppression_detector import detect_suppression_patterns

def extract_hidden_text(file_path: str, file_bytes: bytes) -> List[str]:
    """
    Recover any hidden text fragments via multiple forensic methods.
    Returns a deduplicated list of strings.
    """
    reader = PdfReader(file_path)
    fragments = []

    # 1) Reconstruct ASCII85 fragments from page streams
    for page in reader.pages:
        try:
            raw = page.get("/Contents").get_object().get_data()
            fragments.extend(reconstruct_ascii85(raw))
        except Exception:
            continue

    # 2) Scan for invisible/off-page text
    fragments.extend(scan_invisible_text(file_bytes))

    # 3) Map zero-width & homoglyph Unicode tricks
    fragments.extend(map_zero_width(file_bytes))

    # 4) Walk StructTreeRoot/XFA for suppressed content
    fragments.extend(scan_struct_tree(reader))

    # 5) Known suppression patterns (ligatures, decoys)
    fragments.extend(detect_suppression_patterns(reader))

    # Deduplicate while preserving order
    seen = set()
    result = []
    for f in fragments:
        if f not in seen:
            seen.add(f)
            result.append(f)
    return result