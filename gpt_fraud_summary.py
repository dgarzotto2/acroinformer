import openai
import os
import json

def run_gpt_fraud_summary(metadata_list):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY not found in environment or .streamlit/secrets.toml.")

    openai.api_key = api_key

    # Format input into a structured prompt
    summary_prompt = {
        "role": "system",
        "content": (
            "You are a forensic document examiner specializing in PDF metadata, XMP analysis, and signature validation. "
            "Given a list of extracted forensic summaries from multiple PDF documents, identify signs of tampering, "
            "synthetic document generation, flattened overlays, missing signatures, or cloned timestamps. "
            "Return your conclusions in professional bullet points, followed by a brief formal statement that could be used in an affidavit."
        )
    }

    document_evidence = {
        "role": "user",
        "content": "Metadata list:\n\n" + json.dumps(metadata_list, indent=2)
    }

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[summary_prompt, document_evidence],
            temperature=0.3,
            max_tokens=700
        )
        return response["choices"][0]["message"]["content"]

    except Exception as e:
        return f"[GPT error] {str(e)}"