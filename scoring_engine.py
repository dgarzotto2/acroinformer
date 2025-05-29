import json, logging
from typing import Dict

logger = logging.getLogger(__name__)

class ScoringEngine:
    def __init__(self, rules_path: str = "config/scoring_rules.json"):
        with open(rules_path, 'r') as f:
            self.rules = json.load(f)

    def score(self, md: Dict) -> Dict:
        """
        Applies each rule to metadata dict md, returns:
          - risk_score: total points
          - risk_flags: list of strings
        """
        score = 0
        flags = []

        # Rule: timestamp mismatch
        if md.get("creation_date") and md.get("mod_date") and md["creation_date"] != md["mod_date"]:
            score += self.rules["timestamp_mismatch"]
            flags.append("Timestamp mismatch")

        # Rule: AcroForm w/o signature
        if md.get("has_acroform") and not md.get("has_signature_field"):
            score += self.rules["acroform_without_signature"]
            flags.append("AcroForm without cryptographic signature")

        # Rule: Signature overlay
        if md.get("signature_overlay_detected"):
            score += self.rules["signature_overlay"]
            flags.append("Signature overlay detected")

        # Rule: Missing XMP
        if not md.get("xmp_toolkit"):
            score += self.rules["missing_xmp_toolkit"]
            flags.append("Missing XMP toolkit")

        return {"risk_score": score, "risk_flags": flags}