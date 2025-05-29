import streamlit as st
import os
import tempfile
import hashlib
from extract_metadata import extract_metadata
from gpt_fraud_summary import generate_gpt_summary
from affidavit_writer import generate_affidavit_pdf

st.set_page_config(page_title="Forensic PDF Analyzer", layout="wide")

st.title("Forensic PDF Analyzer")
st.markdown("Upload PDFs to analyze metadata, detect tampering, and generate affidavit-ready forensic summaries.")

uploaded_files = st.file_uploader("Choose PDF files", type="pdf", accept_multiple_files=True)

if uploaded_files:
    with tempfile.TemporaryDirectory() as temp_dir:
        st.success("Files uploaded. Processing...")

        metadata_list = []
        for uploaded in uploaded_files:
            file_path = os.path.join(temp_dir, uploaded.name)
            with open(file_path, "wb") as f:
                f.write(uploaded.read())

            with open(file_path, "rb") as f:
                file_bytes = f.read()

            try:
                metadata = extract_metadata(file_path, file_bytes)
                metadata["filename"] = uploaded.name
                metadata["sha256"] = hashlib.sha256(file_bytes).hexdigest()
                metadata_list.append(metadata)
            except Exception as e:
                st.error(f"Failed to extract metadata from {uploaded.name}: {str(e)}")

        for r in metadata_list:
            st.subheader(f"{r['filename']}")
            st.code(f"SHA-256: {r['sha256']}", language="bash")
            st.markdown(f"**Producer:** {r.get('producer', '—')}")
            st.markdown(f"**Creator:** {r.get('creator', '—')}")
            st.markdown(f"**Creation Date:** {r.get('creation_date', '—')}")
            st.markdown(f"**Modification Date:** {r.get('mod_date', '—')}")
            st.markdown(f"**PDF Library:** {r.get('toolkit', '—')}")
            st.markdown(f"**XMP Toolkit:** {r.get('xmp_toolkit', '—')}")
            st.markdown(f"**Has Signature Field:** {'Yes' if r.get('has_signature_field') else 'No'}")
            st.markdown(f"**AcroForm Present:** {'Yes' if r.get('has_acroform') else 'No'}")
            st.markdown(f"**Tamper Risk:** {r.get('tamper_risk', '—')}")
            st.markdown("---")

            # GPT summary (if key is available)
            if "openai_api_key" in st.secrets:
                with st.spinner("Generating GPT summary..."):
                    try:
                        gpt_summary = generate_gpt_summary(r)
                        st.markdown("### GPT Forensic Summary")
                        st.markdown(gpt_summary)
                    except Exception as e:
                        st.warning(f"GPT analysis failed: {str(e)}")

            # Affidavit generation
            if st.button(f"Generate Affidavit for {r['filename']}", key=r['sha256']):
                pdf_path = generate_affidavit_pdf(r, temp_dir)
                with open(pdf_path, "rb") as pdf_file:
                    st.download_button(
                        label="Download Affidavit (PDF)",
                        data=pdf_file.read(),
                        file_name=f"{r['filename'].replace('.pdf', '')}_affidavit.pdf",
                        mime="application/pdf"
                    )