# report_builder.py

import os
import json
from datetime import datetime
from typing import List, Dict, Any

def build_markdown_report(
    docs: List[Dict[str, Any]],
    clusters: List[Dict[str, Any]],
    overrides: List[Dict[str, Any]],
    output_path: str
) -> None:
    """
    Generate a forensic-analysis report in Markdown.

    - docs: list of per-document metadata dicts, each including:
        - filename, document_id, creation_date, mod_date, producer, xmp_toolkit,
        - has_acroform, has_signature_field, signature_overlay_detected,
        - hidden_lib_usage, risk_score, risk_flags, hidden_text_fragments (optional)
    - clusters: output of fraud_detector.detect_mass_fraud()
    - overrides: output of fraud_detector.detect_producer_override()
    - output_path: filesystem path to write the .md report
    """
    with open(output_path, "w", encoding="utf-8") as f:
        # Header
        f.write(f"# Forensic PDF Analysis Report\n")
        f.write(f"_Generated on {datetime.utcnow().isoformat()}Z_\n\n")

        # Document Summaries
        f.write("## 1. Document Summaries\n\n")
        for doc in docs:
            title = doc.get("filename") or doc.get("document_id", "Unknown")
            f.write(f"### {title}\n\n")

            # Core metadata table
            f.write("| Field | Value |\n|---|---|\n")
            for key in (
                "document_id", "creation_date", "mod_date",
                "producer", "xmp_toolkit", "has_acroform",
                "has_signature_field", "signature_overlay_detected",
                "hidden_lib_usage"
            ):
                val = doc.get(key, "—")
                f.write(f"| **{key}** | {val} |\n")
            f.write("\n")

            # Risk scoring
            f.write(f"- **Risk Score:** {doc.get('risk_score', 0)}\n")
            flags = doc.get("risk_flags", [])
            f.write(f"- **Risk Flags:** {', '.join(flags) or 'None'}\n\n")

            # Hidden text fragments, if any
            hidden_text = doc.get("hidden_text_fragments", [])
            if hidden_text:
                f.write("**Hidden Text Fragments:**\n")
                for frag in hidden_text:
                    f.write(f"- `{frag}`\n")
                f.write("\n")

        # Fraud clusters
        f.write("## 2. Mass-Fraud Clusters\n\n")
        if clusters:
            for cl in clusters:
                mk = cl["minute_key"]
                ts = f"{mk[:4]}-{mk[4:6]}-{mk[6:8]} {mk[8:10]}:{mk[10:12]}"
                f.write(f"### Cluster @ {ts}\n")
                tk = ", ".join(cl["toolkit_values"])
                f.write(f"- **Distinct XMP Toolkit values:** {tk}\n\n")
                f.write("| Filename | Producer | XMP Toolkit | Risk Score |\n")
                f.write("|---|---|---|---|\n")
                for d in cl["docs"]:
                    f.write(
                        f"| {d.get('filename')} "
                        f"| {d.get('producer')} "
                        f"| {d.get('xmp_toolkit')} "
                        f"| {d.get('risk_score')} |\n"
                    )
                f.write("\n")
        else:
            f.write("No mass-fraud clusters detected.\n\n")

        # Producer overrides
        f.write("## 3. Producer Overrides\n\n")
        if overrides:
            f.write("| Document ID | Original Producer | Overridden Producer |\n")
            f.write("|---|---|---|\n")
            for o in overrides:
                f.write(
                    f"| {o['document_id']} "
                    f"| {o['original_producer']} "
                    f"| {o['override_producer']} |\n"
                )
            f.write("\n")
        else:
            f.write("No producer overrides detected.\n\n")

        # Footer
        f.write("---\n")
        f.write("*End of Report*\n")