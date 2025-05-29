# gpt_fraud_summary.py

import openai
import os
import time

def generate_fraud_summary(blocks, metadata, cid_flags=None, xfa_flags=None, raster_flags=None):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        raise ValueError("OpenAI API key not set. Please set OPENAI_API_KEY environment variable.")

    context = []

    # Aggregate blocks and metadata for context
    for i, block in enumerate(blocks):
        block_text = block.get("text", "").strip()
        source = block.get("source", f"Block {i}")
        if block_text:
            context.append(f"### {source}\n{block_text}")

    if not context:
        return {"summary": "❌ No text content available for GPT analysis."}

    document_context = "\n\n".join(context[:5])  # Limit to first 5 blocks to stay within token bounds
    fraud_clues = []

    # Detection signals
    if cid_flags:
        fraud_clues.append("CID glyph suppression detected")
    if xfa_flags:
        fraud_clues.append("XFA overlays detected")
    if raster_flags:
        fraud_clues.append("Raster-only content")
    if metadata.get("producer") in ["ABCpdf", "iText", "BFO"]:
        fraud_clues.append(f"Generated with obfuscation-prone library: {metadata.get('producer')}")

    # Construct GPT prompt
    prompt = f"""
You are a forensic document auditor reviewing potential document fraud.

Below is content extracted from a suspicious PDF. Analyze the content for signs of fraud, placeholder names, missing Unicode maps, CID font suppression, and suppressed parties or amounts.

Document Forensic Clues:
- {'; '.join(fraud_clues) if fraud_clues else 'None noted'}

Content Sample:
{document_context}

Instructions:
- Identify any placeholders (e.g., "John Sample", missing names, blank fields).
- Mention if CID font mapping appears to mask real names.
- Flag any financial terms, roles, or entities that are unusually vague.
- Include any indicators that the document was auto-generated or flattened post-signature.

Respond in clear bullet points.
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
            temperature=0.2
        )
        return {"summary": response["choices"][0]["message"]["content"]}
    except Exception as e:
        return {"summary": f"⚠️ GPT summary generation failed: {str(e)}"}