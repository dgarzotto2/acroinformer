# entity_extraction.py

import re

def extract_entities_from_text(text):
    entities = {
        "grantor": None,
        "grantee": None,
        "amount": None,
        "registry_key": None,
        "email": [],
        "phone": [],
        "address": [],
    }

    name_pattern = re.compile(r"(Tulsi Gabbard|Science of Identity Foundation|Chris Butler|Gabbard Trust)", re.I)
    amount_pattern = re.compile(r"\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?")
    key_pattern = re.compile(r"\b\d{10}\b")
    email_pattern = re.compile(r"\b[\w\.-]+@[\w\.-]+\.\w+\b")
    phone_pattern = re.compile(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}")
    address_pattern = re.compile(r"\d{2,5}\s[\w\s]+(?:Ave|St|Road|Blvd|Rd|Drive|Dr|Lane|Ln|Way|Court|Ct|Loop|Place|Pl)\b", re.I)

    for match in name_pattern.findall(text):
        if "foundation" in match.lower():
            entities["grantee"] = match
        else:
            entities["grantor"] = match

    if amount_match := amount_pattern.search(text):
        entities["amount"] = amount_match.group()

    if key_match := key_pattern.search(text):
        entities["registry_key"] = key_match.group()

    entities["email"] = email_pattern.findall(text)
    entities["phone"] = phone_pattern.findall(text)
    entities["address"] = address_pattern.findall(text)

    return entities