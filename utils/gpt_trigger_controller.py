# utils/gpt_trigger_controller.py

from utils.gpt_fraud_summary import generate_fraud_summary

# Define suppression flags that are always suspicious
HIGH_PRIORITY_FLAGS = {"cid_font_marker", "preview_only", "foreign_route", "zero_width_space"}

def should_trigger_gpt(blocks: list) -> bool:
    """
    Determine if GPT should be run based on decoded block suppression or risk.
    """
    for block in blocks:
        flags = set(block.get("suppression_flags", []))
        risk_score = block.get("risk_score", 0)

        if risk_score >= 30:
            return True

        if flags.intersection(HIGH_PRIORITY_FLAGS):
            return True

    return False

def run_gpt_if_triggered(blocks: list, metadata: dict, entities: list, filename: str) -> str:
    """
    Run GPT-based fraud summary generation if conditions are met.
    Returns the summary string, or empty string if no trigger fired.
    """
    if should_trigger_gpt(blocks):
        return generate_fraud_summary(entities, metadata, filename)
    return ""

def batch_gpt_summary(documents: list) -> dict:
    """
    Process a batch of documents.
    Each item must be a dict with keys: filename, blocks, metadata, entities.
    Returns a dict: {filename: summary}
    """
    results = {}

    for doc in documents:
        filename = doc.get("filename", "unknown.pdf")
        blocks = doc.get("blocks", [])
        metadata = doc.get("metadata", {})
        entities = doc.get("entities", [])

        if should_trigger_gpt(blocks):
            summary = generate_fraud_summary(entities, metadata, filename)
            results[filename] = summary
        else:
            results[filename] = ""

    return results