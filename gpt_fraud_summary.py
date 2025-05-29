# gpt_fraud_summary.py

import openai
from utils.utils import summarize_entities_for_gpt

def generate_fraud_summary(entities, metadata, filename, suppression_flags, license_flags, batch_duplicates=None):
    gpt_input = f"""
Filename: {filename}
Metadata Summary: {metadata}
Suppression Flags: {suppression_flags}
License Flags: {license_flags}
Batch Duplication Flags: {batch_duplicates or []}
Entities: {summarize_entities_for_gpt(entities)}

What are the potential fraud indicators? Focus on document generation method, CID or license risks, entity anomalies, metadata reuse.
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": gpt_input}],
            temperature=0.4,
            max_tokens=400
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        return f"GPT Error: {str(e)}"