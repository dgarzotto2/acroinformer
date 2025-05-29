# gpt_fraud_summary.py

def generate_fraud_summary(metadata, entities, suppression_flags):
    lines = []

    lines.append("## Forensic Risk Summary")
    if suppression_flags:
        lines.append("**Suppression Flags:**")
        for f in suppression_flags:
            lines.append(f"- {f}")

    if metadata.get("xfa_present"):
        lines.append("- XFA forms detected – potential for runtime injection or dynamic field suppression.")

    if metadata.get("has_javascript"):
        lines.append("- Embedded JavaScript present – investigate for auto-actions or remote routing logic.")

    fonts = metadata.get("fonts", [])
    if any("CID" in f or "Identity" in f for f in fonts):
        lines.append("- CID-masked fonts detected – names or routing info may be obfuscated.")

    if metadata.get("producer") and "ABCpdf" in metadata.get("producer", ""):
        lines.append("- Document generated with ABCpdf – high risk for Unicode and font suppression.")
    elif metadata.get("producer") and "iText" in metadata.get("producer", ""):
        lines.append("- iText PDF engine detected – confirm ToUnicode maps and font coverage.")
    elif metadata.get("producer") and "Ghostscript" in metadata.get("producer", ""):
        lines.append("- Ghostscript used – check for raster or ASCII85 stream flattening.")

    lines.append("\n## Entity Snapshot")
    for k, v in entities.items():
        lines.append(f"- {k}: {v}")

    return "\n".join(lines)