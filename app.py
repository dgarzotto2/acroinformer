import os
import streamlit as st
import tempfile
import hashlib
from extract_metadata import extract_metadata
from gpt_fraud_summary import generate_fraud_summary

st.set_page_config(page_title="AcroInformer", layout="wide")
st.title("📄 AcroInformer – PDF Metadata Forensics")

uploaded_files = st.file_uploader("Upload one or more PDF files", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    temp_dir = tempfile.mkdtemp(dir="/tmp")
    file_map = {}

    for uploaded in uploaded_files:
        file_path = os.path.join(temp_dir, uploaded.name)
        with open(file_path, "wb") as f:
            f.write(uploaded.read())
        file_map[uploaded.name] = file_path

    results = []

    for fname, fpath in file_map.items():
        with open(fpath, "rb") as f:
            fbytes = f.read()
        try:
            metadata = extract_metadata(fpath, fbytes)
            results.append(metadata)
        except Exception as e:
            st.error(f"❌ Failed to extract metadata from {fname}: {str(e)}")

    # Display extracted metadata
    for r in results:
        st.subheader(f"{r.get('filename', 'Unnamed')}")
        st.code(f"SHA-256: {r['sha256']}", language="bash")
        st.markdown(f"**Producer:** {r['producer'] or '—'}")
        st.markdown(f"**Creator:** {r['creator'] or '—'}")
        st.markdown(f"**Creation Date:** {r['creation_date'] or '—'}")
        st.markdown(f"**Modification Date:** {r['mod_date'] or '—'}")
        st.markdown(f"**Toolkit:** {r['xmp_toolkit'] or '—'}")
        st.markdown(f"**Signature Type:** {r['signature_type'] or '—'}")
        st.markdown(f"**Fields Present:** {', '.join(r['form_fields']) if r['form_fields'] else '—'}")
        st.markdown("---")

    # GPT summary section
    if "openai_api_key" in st.secrets:
        with st.spinner("🔍 Interpreting metadata for fraud signals..."):
            summary = generate_fraud_summary(results, st.secrets["openai_api_key"])
        st.subheader("🧠 GPT Fraud Summary")
        st.markdown(summary)
    else:
        st.warning("OpenAI API key not found in Streamlit secrets.")