import re
from utils.patterns import (
    phone_pattern, email_pattern, amount_pattern,
    registry_key_pattern, address_pattern, foreign_script_pattern
)

def extract_entities(text, cid_context=None, ascii85_context=None, ocr_context=None):
    """
    Extracts entities such as phone numbers, emails, registry keys, addresses, amounts, and foreign scripts.
    Disambiguates registry keys from misclassified phone numbers using context.
    """

    entities = {
        "phones": [],
        "emails": [],
        "amounts": [],
        "addresses": [],
        "registry_keys": [],
        "foreign_scripts": [],
        "raw_blocks": [],
    }

    # Capture raw text blocks for traceback if needed
    entities["raw_blocks"].append(text)

    # Primary extraction patterns
    phones = re.findall(phone_pattern, text)
    emails = re.findall(email_pattern, text)
    amounts = re.findall(amount_pattern, text)
    registry_keys = re.findall(registry_key_pattern, text)
    addresses = re.findall(address_pattern, text)

    # Disambiguate potential misclassified registry keys as phone numbers
    cleaned_phones = []
    inferred_keys = set(registry_keys)
    for p in phones:
        digits = re.sub(r"[^\d]", "", p)
        if len(digits) == 10 and digits.startswith(("00", "01", "05", "06", "07", "09")):
            if digits not in inferred_keys:
                inferred_keys.add(digits)
        else:
            cleaned_phones.append(p)

    # Capture registry keys from phone-like patterns
    deduped_keys = list(sorted(inferred_keys))

    # Foreign script detection
    foreign_hits = []
    for match in foreign_script_pattern.finditer(text):
        foreign_hits.append({
            "language": match.lastgroup,
            "text": match.group()
        })

    # CID / ASCII85 / OCR contexts
    if cid_context:
        entities["cid_context"] = cid_context
    if ascii85_context:
        entities["ascii85_context"] = ascii85_context
    if ocr_context:
        entities["ocr_context"] = ocr_context

    entities["phones"] = cleaned_phones
    entities["emails"] = list(set(emails))
    entities["amounts"] = list(set(amounts))
    entities["addresses"] = list(set(addresses))
    entities["registry_keys"] = deduped_keys
    entities["foreign_scripts"] = foreign_hits

    return entities