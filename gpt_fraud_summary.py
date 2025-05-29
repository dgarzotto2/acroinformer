import openai

def generate_fraud_summary(results, api_key):
    openai.api_key = api_key

    metadata_blocks = []
    for r in results:
        block = f"""
Filename: {r['filename']}
SHA-256: {r['sha256']}
Producer: {r['producer']}
Creator: {r['creator']}
Created: {r['creation_date']}
Modified: {r['mod_date']}
Toolkit: {r['xmp_toolkit']}
Signature: {r['signature_type']}
Form Fields: {', '.join(r['form_fields']) if r['form_fields'] else 'None'}
        """.strip()
        metadata_blocks.append(block)

    prompt = (
        "You are a forensic PDF expert. Analyze the following metadata from multiple PDFs. "
        "Identify anomalies, mass production indicators, signature inconsistencies, toolkit reuse, or signs of document tampering.\n\n"
        + "\n\n---\n\n".join(metadata_blocks)
        + "\n\nGenerate a summary that highlights any evidence of fraud, synthetic generation, or post-filing edits."
    )

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800
    )

    return response['choices'][0]['message']['content']