# scoring_engine.py

import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ScoringEngine:
    def __init__(self, rules_path: str = "config/scoring_rules.json"):
        with open(rules_path, "r") as f:
            self.rules = json.load(f)

    def score(self, md: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply data-driven rules to metadata dict md.
        Returns:
          - risk_score: int
          - risk_flags: List[str]
        """
        score = 0
        flags = []

        # 1) Timestamp mismatch
        if md.get("creation_date") and md.get("mod_date") and md["creation_date"] != md["mod_date"]:
            score += self.rules.get("timestamp_mismatch", 0)
            flags.append("Timestamp mismatch")

        # 2) AcroForm without cryptographic signature
        if md.get("has_acroform") and not md.get("has_signature_field"):
            score += self.rules.get("acroform_without_signature", 0)
            flags.append("AcroForm without cryptographic signature")

        # 3) Signature-overlay annotation
        if md.get("signature_overlay_detected"):
            score += self.rules.get("signature_overlay", 0)
            flags.append("Signature overlay detected")

        # 4) Missing XMP toolkit
        if not md.get("xmp_toolkit"):
            score += self.rules.get("missing_xmp_toolkit", 0)
            flags.append("Missing XMP toolkit")

        # 5) Hidden PDF-library usage (iText, PDFBox, BFO, ABCpdf, etc.)
        if md.get("hidden_lib_usage"):
            score += self.rules.get("hidden_lib_usage", 0)
            flags.append("Programmatic manipulation detected (hidden PDF library)")

        return {"risk_score": score, "risk_flags": flags}