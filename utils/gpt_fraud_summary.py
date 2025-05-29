import openai
import os

def summarize_fraud(report):
    if not report.get("metadata"):
        return "No metadata available for GPT summary."

    prompt = f"""
You are a forensic AI. Analyze the following PDF decoding result and summarize fraud risks:

Metadata:
{report.get("metadata")}

Fraud Flags:
{report.get("fraud_flags")}

Obfuscation Flags:
{report.get("obfuscation_flags")}

Entities:
{report.get("entities")}

Include:
- Signs of document tampering
- CID masked names or amounts
- Known AGPL/GPL library usage
- Risks related to synthetic or remote-edited PDFs

Respond in a formal paragraph.
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=500
    )

    return response.choices[0].message.content.strip()
