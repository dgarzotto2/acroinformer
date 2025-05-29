import os
import tempfile
import streamlit as st
from utils.metadata import extract_metadata
from utils.gpt_fraud_summary import generate_fraud_summary
from utils.decode_controller import decode_pdf
from utils.entity_extraction import extract_entities

st.set_page_config(
    page_title="AcroInformer – PDF Metadata & Tamper Audit",
    layout="wide"
)

st.title("AcroInformer – PDF Forensics & Tamper Audit")

uploaded_file = st.file_uploader("Upload a PDF for analysis", type=["pdf"])

# Optional: add toggle for static vs. fitz mode
use_fitz = st.radio("Decoding Mode", ["PyMuPDF (fitz)", "Static (no fitz)"]) == "PyMuPDF (fitz)"

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    st.subheader(f"Analysis: {uploaded_file.name}")

    try:
        with open(tmp_path, "rb") as f:
            file_bytes = f.read()

        # Extract metadata
        metadata = extract_metadata(file_bytes)
        st.markdown("### Metadata")
        for k, v in metadata.items():
            st.write(f"- **{k}**: {v}")

        # Decode and analyze
        decoded_blocks = decode_pdf(file_bytes, use_fitz=use_fitz)

        # Show suppression flags
        st.markdown("### Suppression Flags & Risk Scores")
        for b in decoded_blocks:
            page = b.get("page", "?")
            flags = b.get("suppression_flags", [])
            score = b.get("risk_score", 0)
            if flags:
                st.write(f"- Page {page}: Flags: {flags} | Risk Score: {score}")

        # Extract entities
        full_text = "\n".join([b.get("text", "") for b in decoded_blocks])
        entities = extract_entities(full_text)

        st.markdown("### Extracted Entities")
        if entities:
            for e in entities:
                st.write(f"- {e}")
        else:
            st.info("No entities extracted.")

        # Auto-GPT summary if risk flags detected
        high_risk_blocks = [b for b in decoded_blocks if b.get("risk_score", 0) >= 30]

        if high_risk_blocks:
            st.markdown("### GPT Fraud Summary (Triggered by Suppression Flags)")
            summary = generate_fraud_summary(entities, metadata, uploaded_file.name)
            st.code(summary, language="markdown")
        else:
            st.info("No high-risk suppression patterns detected. GPT summary not triggered.")

    except Exception as e:
        st.error(f"Error analyzing {uploaded_file.name}: {e}")