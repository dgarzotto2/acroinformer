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

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    st.subheader(f"📄 Analysis: {uploaded_file.name}")

    try:
        with open(tmp_path, "rb") as f:
            file_bytes = f.read()

        # Metadata extraction
        metadata = extract_metadata(file_bytes)
        st.markdown("### Metadata")
        for k, v in metadata.items():
            st.write(f"- **{k}**: {v}")

        # Decoding and entity extraction
        decoded_blocks = decode_pdf(file_bytes)
        all_text = "\n".join([block.get("text", "") for block in decoded_blocks])
        entities = extract_entities(all_text)

        st.markdown("### Entities Extracted")
        if entities:
            for e in entities:
                st.write(f"- {e}")
        else:
            st.info("No entities extracted.")

        # Fraud summary using GPT
        st.markdown("### GPT Fraud Summary")
        summary = generate_fraud_summary(entities, metadata, uploaded_file.name)
        st.code(summary, language="markdown")

    except Exception as e:
        st.error(f"Error analyzing {uploaded_file.name}: {e}")