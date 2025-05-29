import streamlit as st
import os
import tempfile
from utils.metadata import extract_metadata
from utils.gpt_fraud_summary import generate_fraud_summary

st.set_page_config(
    page_title="AcroInformer – PDF Metadata & Tamper Audit",
    layout="centered",
)

st.title("AcroInformer – PDF Metadata & Tamper Audit")
st.write("Upload one or more PDFs to analyze metadata, obfuscation techniques, and tampering behavior.")

uploaded_files = st.file_uploader("Upload PDF(s)", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    all_results = []
    summary_texts = []
    
    for uploaded_file in uploaded_files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(uploaded_file.read())
            temp_file_path = temp_file.name
        
        with st.spinner(f"Analyzing {uploaded_file.name}..."):
            try:
                result = extract_metadata(temp_file_path)
                result["filename"] = uploaded_file.name
                all_results.append(result)
                
                st.subheader(f"Metadata Report: {uploaded_file.name}")
                
                st.markdown("### Core Metadata:")
                st.json(result.get("core", {}))

                st.markdown("### Forensic Flags:")
                st.json(result.get("flags", {}))

                st.markdown("### Notes & Obfuscation Techniques:")
                notes = result.get("notes", [])
                if notes:
                    for note in notes:
                        st.markdown(f"- {note}")
                else:
                    st.markdown("*No notes extracted*")

                summary = generate_fraud_summary(result)
                summary_texts.append(f"### {uploaded_file.name}\n{summary}")

            except Exception as e:
                st.error(f"Error analyzing {uploaded_file.name}: {str(e)}")

    # Optional combined GPT summary
    if summary_texts:
        st.subheader("AI-Powered Summary")
        for section in summary_texts:
            st.markdown(section)