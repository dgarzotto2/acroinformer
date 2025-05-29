# utils/entity_extraction.py

import re

def extract_entities(text: str) -> list:
    """
    Extracts key forensic entities from the provided text block.
    Returns a list of labeled items.
    """
    entities = []

    # 10-digit registry keys (starting with 0)
    registry_keys = re.findall(r"\b0\d{9}\b", text)
    for key in registry_keys:
        entities.append(f"Registry Key: {key}")

    # Dollar amounts (e.g. $1,000.00)
    amounts = re.findall(r"\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?", text)
    for amt in amounts:
        entities.append(f"Amount: {amt}")

    # Parcel numbers (Hawaii-style TMKs)
    parcels = re.findall(r"\b[39]\d{2}-\d{3}-\d{3}\b", text)
    for parcel in parcels:
        entities.append(f"Parcel: {parcel}")

    # Emails
    emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    for email in emails:
        entities.append(f"Email: {email}")

    # Phone numbers
    phones = re.findall(r"\(?\d{3}\)?[-\s.]?\d{3}[-\s.]?\d{4}", text)
    for phone in phones:
        entities.append(f"Phone: {phone}")

    # Physical addresses (heuristic)
    addresses = re.findall(r"\d{2,5} [A-Za-z0-9 .,-]+(?:St|Ave|Blvd|Rd|Highway|Hwy|Way|Lane|Dr)\b", text)
    for addr in addresses:
        entities.append(f"Address: {addr}")

    return list(set(entities))  # Deduplicated