import yaml
import io

def export_yaml(filename, result):
    entities = result.get("entities", {})
    metadata = result.get("metadata", {})
    suppression_flags = result.get("suppression_flags", [])
    fraud_flags = result.get("fraud_flags", [])
    sha256 = result.get("sha256", "unknown")
    gpt_summary = result.get("gpt_summary", "")
    source_doc = filename

    yaml_dict = {
        "source": source_doc,
        "sha256": sha256,
        "metadata": metadata,
        "suppression_flags": suppression_flags,
        "fraud_flags": fraud_flags,
        "cid_font_usage": result.get("cid_font_usage", False),
        "xfa_fields": result.get("xfa_fields", []),
        "acroform_present": result.get("has_acroform", False),
        "launch_action": result.get("launch_action", None),
        "image_ocr_notes": result.get("image_ocr_notes", ""),
        "entities": {
            "names": entities.get("names", []),
            "amounts": entities.get("amounts", []),
            "registry_keys": entities.get("registry_keys", []),
            "addresses": entities.get("addresses", []),
            "emails": entities.get("emails", []),
            "phone_numbers": entities.get("phone_numbers", []),
            "foreign_scripts": entities.get("foreign_scripts", []),
            "gps": entities.get("gps", []),
            "parcel_ids": entities.get("parcel_ids", []),
            "routing": entities.get("routing", []),
            "roles": entities.get("roles", []),
        },
        "gpt_summary": gpt_summary
    }

    # Include real_grantor_inferred if provided
    if "real_grantor_inferred" in entities:
        yaml_dict["real_grantor_inferred"] = entities["real_grantor_inferred"]

    output = io.StringIO()
    yaml.dump(yaml_dict, output, sort_keys=False, allow_unicode=True)
    return output.getvalue().encode("utf-8")