# utils/decode_controller.py

from utils.decode_streams import decode_streams
from utils.suppression_detector import detect_suppression_patterns

def decode_pdf(file_bytes: bytes, use_fitz: bool = True) -> list:
    """
    Full decoding pipeline:
    - Decodes PDF content using either PyMuPDF (fitz) or static byte parsing.
    - Applies suppression pattern analysis to each block.
    Returns a list of decoded blocks with suppression flags.
    """
    blocks = decode_streams(file_bytes, use_fitz=use_fitz)

    for block in blocks:
        text = block.get("text", "")
        flags = detect_suppression_patterns(text)
        block["suppression_flags"] = flags

    return blocks