# pdf_utils.py

import fitz
import re

def extract_text_and_entities(file_path):
    doc = fitz.open(file_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    doc.close()

    # Basic entity extraction (names, $ amounts, dates, 10-digit keys)
    names = re.findall(r"[A-Z][a-z]+ [A-Z][a-z]+", full_text)
    amounts = re.findall(r"\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?", full_text)
    registry_keys = re.findall(r"\b\d{10}\b", full_text)
    dates = re.findall(r"\b(?:20\d{2}|19\d{2})[-/]\d{1,2}[-/]\d{1,2}\b", full_text)

    return {
        "raw_text": full_text,
        "names": list(set(names)),
        "amounts": list(set(amounts)),
        "registry_keys": list(set(registry_keys)),
        "dates": list(set(dates))
    }