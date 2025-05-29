# scoring_engine.py

def score_documents(meta_a, meta_b):
    score = 0
    reasons = []

    if meta_a["xmp_document_id"] and meta_b["xmp_document_id"]:
        if meta_a["xmp_document_id"] == meta_b["xmp_document_id"]:
            score += 30
            reasons.append("Matching XMP DocumentID")

    if meta_a["xmp_instance_id"] and meta_b["xmp_instance_id"]:
        if meta_a["xmp_instance_id"] == meta_b["xmp_instance_id"]:
            score += 20
            reasons.append("Matching XMP InstanceID")

    if meta_a["creation_date"] == meta_b["creation_date"]:
        score += 15
        reasons.append("Identical creation timestamp")

    if meta_a["mod_date"] == meta_b["mod_date"]:
        score += 10
        reasons.append("Identical modification timestamp")

    form_names_a = set(f["name"] for f in meta_a["form_fields"])
    form_names_b = set(f["name"] for f in meta_b["form_fields"])
    shared_fields = form_names_a.intersection(form_names_b)
    if shared_fields:
        score += min(10, len(shared_fields) * 2)
        reasons.append(f"Shared AcroForm fields: {', '.join(shared_fields)}")

    return score, reasons