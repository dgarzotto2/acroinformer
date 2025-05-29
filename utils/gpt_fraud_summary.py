# utils/gpt_fraud_summary.py

import streamlit as st
import openai

OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
openai.api_key = OPENAI_API_KEY

def generate_fraud_summary(entities: list, metadata: dict, filename: str) -> str:
    """
    Generate a forensic fraud summary using GPT based on extracted entities and metadata.
    """
    prompt = f"""
You are a digital forensics investigator. A document named '{filename}' has been processed.

Entities:
{entities}

Metadata:
{metadata}

Write a fraud summary covering:
- Document tampering indicators (CID fonts, Unicode suppression, AGPL tools, etc.)
- Foreign routing, concealed amounts or parcels
- Suspicious entity roles or metadata overlaps
Use formal, affidavit-ready language. Be concise and forensic.
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert in PDF fraud analysis."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=800
        )
        return response['choices'][0]['message']['content'].strip()

    except Exception as e:
        return f"⚠️ GPT summary unavailable: {str(e)}"