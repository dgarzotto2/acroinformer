# scoring_engine.py

def score_documents(meta1, meta2):
    score = 0
    reasons = []

    # SHA-256 match (very suspicious)
    if meta1.get("sha256") == meta2.get("sha256"):
        score += 50
        reasons.append("Exact SHA-256 hash match — files may be duplicates or have identical content.")

    # Creation time match
    if meta1.get("creation_time") == meta2.get("creation_time"):
        score += 15
        reasons.append("Matching creation timestamps.")

    # Modification time match
    if meta1.get("modification_time") == meta2.get("modification_time"):
        score += 10
        reasons.append("Matching modification timestamps.")

    # XMP Document ID match
    if meta1.get("xmp_document_id") and meta1.get("xmp_document_id") == meta2.get("xmp_document_id"):
        score += 20
        reasons.append("Matching XMP Document ID (suggests shared origin or reuse).")

    # XMP Instance ID match
    if meta1.get("xmp_instance_id") and meta1.get("xmp_instance_id") == meta2.get("xmp_instance_id"):
        score += 15
        reasons.append("Matching XMP Instance ID.")

    # AcroForm structure overlap
    fields1 = set(meta1.get("acroform_fields", []))
    fields2 = set(meta2.get("acroform_fields", []))
    if fields1 and fields2:
        intersection = fields1 & fields2
        if intersection:
            score += 20
            reasons.append(f"{len(intersection)} overlapping AcroForm field definitions.")

    # Same producer string
    if meta1.get("producer") and meta1.get("producer") == meta2.get("producer"):
        score += 5
        reasons.append("Same PDF producer metadata string.")

    return score, reasons