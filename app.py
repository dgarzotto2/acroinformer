#!/usr/bin/env python3
import os
import streamlit as st
from metadata import extract_metadata
from scoring_engine import ScoringEngine
from metadata_comparator import compare_metadata
from report_logger import configure_logging

configure_logging("DEBUG")

@st.cache_data(show_spinner=False)
def run_extraction(path: str, data: bytes):
    return extract_metadata(path, data)

def save_tmp(uploaded):
    tmp = "/tmp/acroinformer"
    os.makedirs(tmp, exist_ok=True)
    data = uploaded.read()
    p = os.path.join(tmp, uploaded.name)
    with open(p, "wb") as f:
        f.write(data)
    return p, data

def main():
    st.set_page_config("AcroInformer", layout="wide")
    st.title("AcroInformer – Fraud Comparison")

    files = st.file_uploader("Upload 2+ PDFs", type="pdf", accept_multiple_files=True)
    if not files or len(files) < 2:
        st.warning("Please upload at least two PDFs.")
        return

    # Extract + Score first two
    p1, b1 = save_tmp(files[0]); md1 = run_extraction(p1, b1)
    p2, b2 = save_tmp(files[1]); md2 = run_extraction(p2, b2)

    # Score
    scorer = ScoringEngine()
    s1 = scorer.score(md1); s2 = scorer.score(md2)

    # Display side-by-side table
    comp = compare_metadata({**md1, **s1}, {**md2, **s2})
    st.table(comp)

    # Optionally download a forensic ZIP
    if st.button("Download Full Package"):
        from zip_exporter import build_forensic_package
        zip_bytes = build_forensic_package(files)
        st.download_button("ZIP all PDF+YAML", data=zip_bytes, file_name="package.zip")

if __name__ == "__main__":
    main()