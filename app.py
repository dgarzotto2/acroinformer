import streamlit as st
import base64
from utils.decode_controller import decode_pdf
from utils.yaml_exporter import export_yaml
from utils.affidavit_writer import generate_affidavit_pdf
from utils.zip_bundle import bundle_results
import hashlib

st.set_page_config(
    page_title="AcroInformer – PDF Metadata & Tamper Audit",
    layout="wide"
)

st.title("AcroInformer – PDF Metadata & Tamper Audit")
st.markdown("Upload one or more PDF documents for forensic analysis. Output includes decoded entities, metadata, risk scores, YAML, and affidavit generation.")

uploaded_files = st.file_uploader("Upload PDF(s)", type=["pdf"], accept_multiple_files=True)

decoding_mode = st.radio("Decoding Mode", ["PyMuPDF (fitz)", "Static (no fitz)"])
static_mode = decoding_mode == "Static (no fitz)"

results = []
if uploaded_files:
    for uploaded_file in uploaded_files:
        st.subheader(f"Analysis: {uploaded_file.name}")
        file_bytes = uploaded_file.read()
        sha256 = hashlib.sha256(file_bytes).hexdigest()
        result = decode_pdf(file_bytes, static_mode=static_mode)

        st.markdown(f"**SHA-256:** `{sha256}`")
        st.markdown(f"**Error:** {result.get('error', 'None')}")

        st.markdown("### Metadata")
        st.json(result.get("metadata", {}))

        st.markdown("### Suppression Flags")
        st.write(result.get("suppression_flags", []))

        st.markdown("### Fraud Flags")
        st.write(result.get("fraud_flags", []))

        st.markdown("### Extracted Entities")
        st.json(result.get("entities", {}))

        st.markdown("### Decoded Text")
        st.text_area("Decoded Content", result.get("decoded_text", ""), height=200)

        st.markdown("### GPT Fraud Summary")
        st.text(result.get("gpt_summary", ""))

        yaml_data = export_yaml(uploaded_file.name, result)
        st.download_button("Download YAML", yaml_data, file_name=uploaded_file.name.replace(".pdf", "_entities.yaml"))

        affidavit_pdf = generate_affidavit_pdf(uploaded_file.name, result)
        st.download_button("Download Affidavit PDF", affidavit_pdf, file_name=uploaded_file.name.replace(".pdf", "_affidavit.pdf"))

        results.append({
            "filename": uploaded_file.name,
            "sha256": sha256,
            "yaml": yaml_data,
            "affidavit": affidavit_pdf
        })

if results:
    if st.button("Bundle All Results into ZIP"):
        zip_bytes = bundle_results(results)
        st.download_button("Download ZIP Bundle", zip_bytes, file_name="forensic_bundle.zip")