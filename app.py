import os
import streamlit as st
import tempfile
from utils.extractor import extract_metadata
from utils.gpt_interpreter import run_gpt_analysis
import openai

# Set up OpenAI from Streamlit secrets
openai.api_key = st.secrets["openai_api_key"]

st.set_page_config(
    page_title="AcroInformer – Forensic PDF Metadata Examiner",
    layout="wide"
)

st.title("AcroInformer – PDF Metadata & Signature Forensics")

st.markdown("""
Upload two or more PDF documents to compare:
- Metadata consistency (creation, modification, XMP IDs)
- AcroForm structure, reuse, and flattening
- Signature validation (digital or static overlays)
- Potential signs of synthetic generation or tampering
""")

uploaded_files = st.file_uploader(
    "Select PDF files", type="pdf", accept_multiple_files=True
)

if not uploaded_files or len(uploaded_files) < 2:
    st.warning("Please upload at least 2 PDF files for comparison.")
    st.stop()

with st.spinner("Processing uploaded PDFs..."):
    temp_dir = tempfile.mkdtemp(dir="/tmp")
    file_map = {}

    for uploaded in uploaded_files:
        file_path = os.path.join(temp_dir, uploaded.name)
        with open(file_path, "wb") as f:
            f.write(uploaded.read())
        file_map[uploaded.name] = file_path

    metadata_list = []
    for fname, fpath in file_map.items():
        with open(fpath, "rb") as f:
            fbytes = f.read()
        try:
            meta = extract_metadata(fpath, fbytes)
            metadata_list.append(meta)
        except Exception as e:
            st.error(f"Failed to extract metadata from {fname}: {str(e)}")
            continue

if not metadata_list:
    st.error("No valid metadata could be extracted from the uploaded PDFs.")
    st.stop()

st.success(f"Successfully extracted metadata from {len(metadata_list)} PDF(s).")

# Display metadata
for meta in metadata_list:
    st.subheader(f"📄 {meta.get('filename', 'Unknown')}")
    st.json(meta)

# GPT Forensic Summary (if available)
if openai.api_key:
    st.markdown("---")
    st.header("🧠 GPT-Powered Forensic Interpretation")
    with st.spinner("Interpreting forensic patterns using GPT..."):
        try:
            gpt_summary = run_gpt_analysis(metadata_list)
            st.markdown(gpt_summary)
        except Exception as e:
            st.error(f"GPT analysis failed: {str(e)}")