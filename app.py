#!/usr/bin/env python3
import os
import streamlit as st
from metadata import extract_metadata
from scoring_engine import ScoringEngine
from fraud_detector import detect_mass_fraud
from report_logger import configure_logging

configure_logging("INFO")

@st.cache_data(show_spinner=False)
def extract_and_score(path: str, data: bytes):
    md = extract_metadata(path, data)
    score = ScoringEngine().score(md)
    return {**md, **score}

def save_tmp(uploaded):
    tmp = "/tmp/acroinformer"
    os.makedirs(tmp, exist_ok=True)
    data = uploaded.read()
    p = os.path.join(tmp, uploaded.name)
    with open(p, "wb") as f:
        f.write(data)
    return p, data

def main():
    st.set_page_config("AcroInformer – Mass Fraud Detection", layout="wide")
    st.title("AcroInformer – Mass PDF Fraud Detection")
    st.write("""
    Upload a batch of PDFs.  
    We’ll flag any groups produced in the *same minute* but carrying *different XMP toolkit* values—  
    a classic indicator of mass-fraud template sprawl.
    """)

    files = st.file_uploader(
        "Select one or more PDF documents",
        type="pdf",
        accept_multiple_files=True
    )
    if not files:
        st.info("Please upload at least two PDFs to analyze.")
        return

    # 1) Extract & score each PDF
    all_md = []
    for uf in files:
        path, data = save_tmp(uf)
        md = extract_and_score(path, data)
        md["filename"] = uf.name
        all_md.append(md)

    # 2) Detect fraud clusters
    clusters = detect_mass_fraud(all_md)
    if not clusters:
        st.success("No mass-fraud clusters detected among the uploaded PDFs.")
        return

    # 3) Display each cluster
    for cluster in clusters:
        key = cluster["minute_key"]
        st.subheader(f"⚠️ Cluster at minute {key[:4]}-{key[4:6]}-{key[6:8]} {key[8:10]}:{key[10:12]}")
        st.markdown(f"**Distinct XMP Toolkit values:** {', '.join(cluster['toolkit_values'])}")

        # Show a table of the docs in this cluster
        rows = []
        for doc in cluster["docs"]:
            rows.append({
                "Filename": doc["filename"],
                "Producer": doc.get("producer"),
                "XMP Toolkit": doc.get("xmp_toolkit"),
                "Risk Score": doc.get("risk_score"),
                "Flags": ", ".join(doc.get("risk_flags", []))
            })
        st.table(rows)

        # Expanders for full metadata per document
        for doc in cluster["docs"]:
            with st.expander(f"Details: {doc['filename']}"):
                for k, v in doc.items():
                    if k in ("filename", "risk_score", "risk_flags"):
                        continue
                    st.markdown(f"- **{k}:** {v}")
        st.markdown("---")

if __name__ == "__main__":
    main()