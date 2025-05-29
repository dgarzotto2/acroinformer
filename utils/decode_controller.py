# utils/decode_controller.py

from utils.decode_streams import decode_streams
from utils.suppression_detector import detect_suppression_patterns

def decode_pdf(file_bytes: bytes, use_fitz: bool = True) -> list:
    """
    Full decoding pipeline:
    - Decodes using fitz or static
    - Applies suppression flag detection
    - Computes risk score (based on flags)
    """
    blocks = decode_streams(file_bytes, use_fitz=use_fitz)

    for block in blocks:
        text = block.get("text", "")
        flags = detect_suppression_patterns(text)
        risk_score = score_risk(flags)

        block["suppression_flags"] = flags
        block["risk_score"] = risk_score

    return blocks

def score_risk(flags: list) -> int:
    """
    Assigns a numeric risk score based on suppression indicators.
    """
    score = 0
    weight = {
        "empty_block": 5,
        "preview_only": 10,
        "cid_font_marker": 25,
        "zero_width_space": 10,
        "masked_account": 20,
        "foreign_route": 30,
        "placeholder_terms_only": 15
    }
    for f in flags:
        score += weight.get(f, 0)
    return score