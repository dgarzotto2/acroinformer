# metadata.py

import fitz

def extract_metadata(file_path):
    doc = fitz.open(file_path)
    meta = doc.metadata
    result = dict(meta)

    # ByteRange tamper check
    b_range = doc.xref_get_key(1, "/ByteRange")
    if b_range and isinstance(b_range[1], str) and len(b_range[1].split()) > 4:
        result["byte_range_mismatch"] = True
        result.setdefault("notes", []).append("Suspicious ByteRange length")

    # CID font marker detection
    cid_font_found = False
    for page in doc:
        fonts = page.get_fonts(full=True)
        for font in fonts:
            if "/CIDFont" in str(font):
                cid_font_found = True
                break
        if cid_font_found:
            break
    if cid_font_found:
        result["cid_fonts_used"] = True
        result.setdefault("notes", []).append("CID fonts detected")

    return result