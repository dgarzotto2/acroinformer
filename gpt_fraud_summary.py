import openai
import streamlit as st
import json

def run_gpt_fraud_summary(metadata_list):
    if "OPENAI_API_KEY" not in st.secrets:
        return "[Error] OPENAI_API_KEY not found in Streamlit secrets."

    openai.api_key = st.secrets["OPENAI_API_KEY"]

    # Construct the GPT prompt
    system_msg = {
        "role": "system",
        "content": (
            "You are a forensic document examiner specializing in digital PDF analysis. "
            "Review the following extracted metadata from arbitration agreements and other legal PDFs. "
            "Detect tampering, cloned timestamps, synthetic AcroForm usage, or any signs of mass-produced agreements. "
            "Summarize all fraud indicators as professional bullet points, followed by a short formal affidavit-style conclusion."
        )
    }

    user_msg = {
        "role": "user",
        "content": "Metadata input:\n\n" + json.dumps(metadata_list, indent=2)
    }

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[system_msg, user_msg],
            temperature=0.2,
            max_tokens=800
        )
        return response["choices"][0]["message"]["content"]

    except Exception as e:
        return f"[GPT Error] {str(e)}"