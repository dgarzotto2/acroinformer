# scoring_engine.py

def score_documents(meta1, meta2):
    """
    Compares two metadata dictionaries and returns a score with reasons.
    Score over 50 indicates high similarity or suspicious overlap.
    """
    score = 0
    reasons = []

    # Compare XMP Document IDs
    if meta1.get("xmp:DocumentID") and meta1["xmp:DocumentID"] == meta2.get("xmp:DocumentID"):
        score += 30
        reasons.append("Matching xmp:DocumentID")

    # Compare InstanceIDs
    if meta1.get("xmp:InstanceID") and meta1["xmp:InstanceID"] == meta2.get("xmp:InstanceID"):
        score += 25
        reasons.append("Matching xmp:InstanceID")

    # Compare PDF Producer
    if meta1.get("producer") and meta1["producer"] == meta2.get("producer"):
        score += 10
        reasons.append("Same PDF producer")

    # Compare Creation Dates
    if meta1.get("creation_date") and meta1["creation_date"] == meta2.get("creation_date"):
        score += 10
        reasons.append("Same creation timestamp")

    # Check for matching AcroForm fields
    acro1 = set(meta1.get("acroform_fields", []))
    acro2 = set(meta2.get("acroform_fields", []))
    if acro1 and acro1 == acro2:
        score += 20
        reasons.append("Identical AcroForm structure and fields")

    # Final evaluation
    if score == 0:
        reasons.append("No detectable metadata overlap")

    return score, reasons