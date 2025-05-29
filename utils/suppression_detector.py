# utils/suppression_detector.py

import re

def detect_suppression_patterns(text: str) -> list:
    """
    Detects known suppression and obfuscation patterns in a text block.
    Returns a list of flags.
    """
    flags = []

    if not text.strip():
        flags.append("empty_block")

    if "Preview" in text and len(text.strip()) < 40:
        flags.append("preview_only")

    if re.search(r"/CID|CIDFont|ToUnicode|CMap", text, re.IGNORECASE):
        flags.append("cid_font_marker")

    if "\u200b" in text:
        flags.append("zero_width_space")

    if re.search(r"\.\.\.\d{4}", text):
        flags.append("masked_account")

    if re.search(r"(Tehran|FATA|Mashreq|Philippines)", text, re.IGNORECASE):
        flags.append("foreign_route")

    if re.search(r"\b(?:Name|Amount|Parcel|Trust)\b", text, re.IGNORECASE) and len(text.strip()) < 50:
        flags.append("placeholder_terms_only")

    return flags