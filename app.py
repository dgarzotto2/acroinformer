#!/usr/bin/env python3
import os
import tempfile
import hashlib

import streamlit as st

from metadata import extract_metadata
from scoring_engine import ScoringEngine
from gpt_fraud_summary import generate_gpt_summary
from affidavit_writer import generate_affidavit_pdf

# 1) Configure Streamlit page (must be at top-level)
st.set_page_config(
    page_title="Forensic PDF Analyzer",
    layout="wide"
)

# 2) Pure data function — no st.* calls here!
@st.cache_data(show_spinner=False)
def extract_and_score(path: str, data: bytes) -> dict:
    md = extract_metadata(path, data)
    score = ScoringEngine().score(md)
    return {**md, **score}

def main():
    # 3) All UI code lives inside main()
    st.title("Forensic PDF Analyzer")
    st.markdown(
        "Upload *two or more* PDF documents to analyze metadata, "
        "detect tampering, and generate affidavit-ready summaries."
    )

    # 4) Multi-file uploader
    uploaded_files = st.file_uploader(
        "Choose two or more PDF files",
        type="pdf",
        accept_multiple_files=True
    )

    # 5) Enforce at least two
    if not uploaded_files or len(uploaded_files) < 2:
        st.warning("🚨 Please upload **at least two** PDF documents to analyze.")
        st.stop()

    # 6) Process each file
    metadata_list = []
    with tempfile.TemporaryDirectory() as temp_dir:
        st.success(f"{len(uploaded_files)} files uploaded. Processing…")

        for uploaded in uploaded_files:
            # Write to temp
            file_path = os.path.join(temp_dir, uploaded.name)
            with open(file_path, "wb") as f:
                f.write(uploaded.read())

            # Read bytes & hash
            with open(file_path, "rb") as f:
                file_bytes = f.read()
            sha256 = hashlib.sha256(file_bytes).hexdigest()

            # Extract and score (cached)
            try:
                result = extract_and_score(file_path, file_bytes)
            except Exception as e:
                st.error(f"Error analyzing {uploaded.name}: {e}")
                continue

            result["filename"] = uploaded.name
            result["sha256"]   = sha256
            metadata_list.append(result)

    # 7) Display results
    for r in metadata_list:
        st.subheader(r["filename"])
        st.code(f"SHA-256: {r['sha256']}", language="bash")

        st.markdown(f"- **Producer:** {r.get('producer','—')}")
        st.markdown(f"- **Creator:** {r.get('creator','—')}")
        st.markdown(f"- **Creation Date:** {r.get('creation_date','—')}")
        st.markdown(f"- **Modification Date:** {r.get('mod_date','—')}")
        st.markdown(f"- **XMP Toolkit:** {r.get('xmp_toolkit','—')}")
        st.markdown(f"- **Has Signature Field:** {'Yes' if r.get('has_signature_field') else 'No'}")
        st.markdown(f"- **AcroForm Present:** {'Yes' if r.get('has_acroform') else 'No'}")
        st.markdown(f"- **Signature Overlay Detected:** {'Yes' if r.get('signature_overlay_detected') else 'No'}")
        st.markdown(f"- **Hidden Library Usage:** {'Yes' if r.get('hidden_lib_usage') else 'No'}")
        st.markdown(f"- **Risk Score:** {r.get('risk_score', 0)}")
        flags = r.get("risk_flags", [])
        st.markdown(f"- **Risk Flags:** {', '.join(flags) if flags else 'None'}")
        st.markdown("---")

        # 8) GPT forensic summary
        if "openai_api_key" in st.secrets:
            with st.spinner("Generating GPT summary…"):
                try:
                    summary = generate_gpt_summary(r)
                    st.markdown("#### GPT Forensic Summary")
                    st.markdown(summary)
                except Exception as e:
                    st.warning(f"GPT summary failed: {e}")

        # 9) Affidavit generation
        btn_key = f"affidavit_{r['sha256']}"
        if st.button(f"Generate Affidavit for {r['filename']}", key=btn_key):
            try:
                pdf_path = generate_affidavit_pdf(r, temp_dir)
                with open(pdf_path, "rb") as pdf_file:
                    st.download_button(
                        label="Download Affidavit (PDF)",
                        data=pdf_file.read(),
                        file_name=f"{r['filename'].rsplit('.',1)[0]}_affidavit.pdf",
                        mime="application/pdf"
                    )
            except Exception as e:
                st.error(f"Affidavit generation failed: {e}")

if __name__ == "__main__":
    main()
    