import openai
import os

def generate_gpt_summary(metadata: dict) -> str:
    openai.api_key = os.environ.get("OPENAI_API_KEY") or \
                     (st.secrets["openai_api_key"] if "openai_api_key" in st.secrets else None)

    prompt = f"""
Analyze the following PDF metadata and provide a forensic opinion. Determine if the document is likely authentic, modified, or synthetic. Highlight any red flags.

Metadata:
- Producer: {metadata.get('producer')}
- Creator: {metadata.get('creator')}
- PDF Toolkit: {metadata.get('toolkit')}
- XMP Toolkit: {metadata.get('xmp_toolkit')}
- Creation Date: {metadata.get('creation_date')}
- Modification Date: {metadata.get('mod_date')}
- AcroForm Present: {metadata.get('has_acroform')}
- Signature Field Present: {metadata.get('has_signature_field')}
- Tamper Risk: {metadata.get('tamper_risk')}
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a digital document forensic analyst."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        max_tokens=500
    )

    return response['choices'][0]['message']['content'].strip()