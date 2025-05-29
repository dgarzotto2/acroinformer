import re

def should_trigger_gpt(summary: dict, decoded_blocks: list) -> bool:
    """
    Decide whether to invoke GPT based on decoded metadata, suppression flags, and anomalies.
    """

    # Shortcut if GPT already triggered by risk score or suppression
    if summary.get("risk_score", 0) >= 30:
        return True

    suppression_flags = summary.get("suppression_flags", [])
    if any(flag in suppression_flags for flag in ["cid_font_used", "raster_overlay", "metadata_error", "xfa_suppression"]):
        return True

    all_entities = summary.get("extracted_entities", [])
    if len(all_entities) > 75:
        return True

    # Detect anomaly: 25+ "Phone" entries or other excessive repetition
    phone_count = sum(1 for ent in all_entities if "Phone" in ent)
    if phone_count >= 25:
        return True

    # Detect placeholder or decoy financial amounts
    suspicious_amounts = [r"\$1\b", r"\$8\b", r"\$79\b"]
    for ent in all_entities:
        if any(re.search(pat, ent) for pat in suspicious_amounts):
            return True

    # Detect obvious registry keys disguised as phones or doc IDs
    for ent in all_entities:
        if "00000" in ent or re.match(r"\b\d{10}\b", ent):
            return True

    # Detect decoded block anomalies: too many CID markers or short/no text
    suspicious_blocks = 0
    for block in decoded_blocks:
        if block.get("cid_font_used") or "/CID" in block.get("raw", ""):
            suspicious_blocks += 1
        if block.get("text") and len(block.get("text")) < 15:
            suspicious_blocks += 1

    if suspicious_blocks >= 3:
        return True

    return False