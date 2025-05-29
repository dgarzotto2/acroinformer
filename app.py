import os
import tempfile
import streamlit as st
from utils.metadata import extract_metadata
from utils.decode_controller import decode_pdf
from utils.entity_extraction import extract_entities
from utils.gpt_trigger_controller import run_gpt_if_triggered, batch_gpt_summary

st.set_page_config(page_title="AcroInformer – PDF Metadata & Tamper Audit", layout="wide")
st.title("AcroInformer – PDF Forensics & Tamper Audit")

uploaded_files = st.file_uploader("Upload PDF(s) for analysis", type=["pdf"], accept_multiple_files=True)
use_fitz = st.radio("Decoding Mode", ["PyMuPDF (fitz)", "Static (no fitz)"]) == "PyMuPDF (fitz)"

results = []
gpt_outputs = {}

if uploaded_files:
    for uploaded_file in uploaded_files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_path = tmp_file.name

        st.subheader(f"📄 Analysis: {uploaded_file.name}")

        try:
            with open(tmp_path, "rb") as f:
                file_bytes = f.read()

            metadata = extract_metadata(file_bytes)
            decoded_blocks = decode_pdf(file_bytes, use_fitz=use_fitz)
            full_text = "\n".join([b.get("text", "") for b in decoded_blocks])
            entities = extract_entities(full_text)

            # Suppression + risk display
            st.markdown("### Suppression Flags & Risk Scores")
            for b in decoded_blocks:
                page = b.get("page", "?")
                flags = b.get("suppression_flags", [])
                score = b.get("risk_score", 0)
                if flags:
                    st.write(f"- Page {page}: {flags} | Risk: {score}")

            # Entity list
            st.markdown("### Extracted Entities")
            if entities:
                for e in entities:
                    st.write(f"- {e}")
            else:
                st.info("No entities extracted.")

            # GPT Summary Trigger
            summary = run_gpt_if_triggered(decoded_blocks, metadata, entities, uploaded_file.name)
            if summary:
                st.markdown("### GPT Fraud Summary")
                st.code(summary, language="markdown")
            else:
                st.info("No GPT summary triggered.")

            # Save results
            results.append({
                "filename": uploaded_file.name,
                "blocks": decoded_blocks,
                "metadata": metadata,
                "entities": entities
            })
            if summary:
                gpt_outputs[uploaded_file.name] = summary

        except Exception as e:
            st.error(f"Error processing {uploaded_file.name}: {e}")

    # Batch Summary Export Section
    if gpt_outputs:
        st.markdown("---")
        st.markdown("### GPT Summaries (All Triggered Files)")
        for fname, summary in gpt_outputs.items():
            st.write(f"**{fname}**")
            st.code(summary, language="markdown")