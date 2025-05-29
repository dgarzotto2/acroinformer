# utils/entity_extraction.py

import re

def extract_entities(text: str) -> list:
    """
    Extract key forensic entities from text.
    """
    entities = []

    registry_keys = re.findall(r"\b0\d{9}\b", text)
    for key in registry_keys:
        entities.append(f"Registry Key: {key}")

    amounts = re.findall(r"\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?", text)
    for amt in amounts:
        entities.append(f"Amount: {amt}")

    parcels = re.findall(r"\b[39]\d{2}-\d{3}-\d{3}\b", text)
    for parcel in parcels:
        entities.append(f"Parcel: {parcel}")

    emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    for email in emails:
        entities.append(f"Email: {email}")

    phones = re.findall(r"\(?\d{3}\)?[-\s.]?\d{3}[-\s.]?\d{4}", text)
    for phone in phones:
        entities.append(f"Phone: {phone}")

    addresses = re.findall(r"\d{2,5} [A-Za-z0-9 .,-]+(?:St|Ave|Blvd|Rd|Highway|Hwy|Way|Lane|Dr)\b", text)
    for addr in addresses:
        entities.append(f"Address: {addr}")

    return list(set(entities))