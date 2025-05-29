# gpt_fraud_summary.py

import openai
import json
import os

from utils.utils import summarize_entities_for_gpt

def generate_fraud_summary(entities, metadata, filename, suppression_flags=None, license_flags=None, batch_duplicates=None):
    """
    Generates a GPT-based fraud risk summary.
    """

    openai.api_key = os.getenv("OPENAI_API_KEY")

    prompt = build_prompt(entities, metadata, filename, suppression_flags, license_flags, batch_duplicates)

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a forensic PDF fraud analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=700
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"⚠️ GPT Error: {str(e)}"

def build_prompt(entities, metadata, filename, suppression_flags=None, license_flags=None, batch_duplicates=None):
    """
    Constructs the GPT prompt with context-aware flags.
    """

    lines = []
    lines.append(f"Analyze the following decoded PDF evidence from `{filename}`.")

    if suppression_flags:
        lines.append("\n**Suppression flags detected:**")
        for flag in suppression_flags:
            lines.append(f"- {flag}")

    if license_flags:
        lines.append("\n**License risk detected:**")
        for flag in license_flags:
            lines.append(f"- {flag}")

    if batch_duplicates:
        lines.append("\n**Duplicate metadata across documents:**")
        for dup_flag in batch_duplicates:
            lines.append(f"- {dup_flag}")

    lines.append("\n---\n**Entities Extracted:**")
    lines.append(summarize_entities_for_gpt(entities))

    if metadata:
        lines.append("\n---\n**Document Metadata:**")
        lines.append(json.dumps(metadata, indent=2))

    lines.append("\n---\nGenerate a fraud summary highlighting:")
    lines.append("- CID font masking or missing Unicode maps")
    lines.append("- AGPL/GPL licensing implications")
    lines.append("- Signs of synthetic document generation")
    lines.append("- Metadata reuse across documents")
    lines.append("- Final rating of fraud risk (Low, Medium, High)")

    return "\n".join(lines)