# suppression_detector.py

import fitz

def detect_suppression_flags(file_path):
    doc = fitz.open(file_path)
    flags = []

    for page in doc:
        fonts = page.get_fonts(full=True)
        for font in fonts:
            if "/CIDFont" in str(font):
                flags.append("CID font masking")
        text = page.get_text()
        if "Preview" in text and len(text.strip()) < 50:
            flags.append("Preview overlay with minimal visible content")

    if not flags:
        flags.append("None")

    return list(set(flags))