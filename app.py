import streamlit as st
import tempfile
import os
import zipfile
from utils.utility import save_uploaded_file
from utils.zip_bundle import bundle_evidence_outputs
from metadata import extract_metadata
from decode_controller import run_full_decode
from entity_extraction import extract_entities
from signature_validator import validate_signature
from pdf_license_fingerprint import check_pdf_license
from gpt_fraud_summary import generate_gpt_summary
from affidavit_writer import generate_affidavit_pdf

st.set_page_config(page_title="X-Ray PDF Forensics", layout="wide")

def handle_uploaded_file(uploaded_file, temp_dir):
    file_path = os.path.join(temp_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())
    return file_path

def extract_pdfs_from_zip(zip_path, temp_dir):
    extracted_paths = []
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
        for name in zip_ref.namelist():
            if name.lower().endswith(".pdf"):
                extracted_paths.append(os.path.join(temp_dir, name))
    return extracted_paths

def process_file(pdf_path, output_dir):
    filename = os.path.basename(pdf_path)
    result = {
        "pdf_path": pdf_path,
        "filename": filename,
        "yaml": None,
        "affidavit": None,
        "gpt_summary": None,
        "error": None,
    }

    try:
        metadata = extract_metadata(pdf_path)
        decoded = run_full_decode(pdf_path)
        entities = extract_entities(decoded, pdf_path)
        signature = validate_signature(pdf_path)
        license_flags = check_pdf_license(pdf_path)

        combined = {**metadata, **decoded, **entities, **signature, **license_flags}
        base_name = os.path.splitext(filename)[0]

        # Save YAML
        yaml_path = os.path.join(output_dir, f"{base_name}_entities.yaml")
        with open(yaml_path, "w") as f:
            import yaml
            yaml.dump(combined, f, sort_keys=False)
        result["yaml"] = yaml_path

        # Generate affidavit
        affidavit_path = os.path.join(output_dir, f"{base_name}_affidavit.pdf")
        generate_affidavit_pdf(pdf_path, combined, affidavit_path)
        result["affidavit"] = affidavit_path

        # GPT Summary
        try:
            gpt_text = generate_gpt_summary(combined)
            result["gpt_summary"] = gpt_text
        except Exception as e:
            result["gpt_summary"] = f"GPT summary failed: {e}"

    except Exception as e:
        result["error"] = str(e)

    return result

def main():
    st.title("X-Ray PDF Forensic Scanner")
    uploaded_files = st.file_uploader("Upload PDFs or a ZIP archive", type=["pdf", "zip"], accept_multiple_files=True)

    if uploaded_files:
        with tempfile.TemporaryDirectory() as temp_dir:
            st.info("Processing uploaded files...")

            all_pdf_paths = []
            for uf in uploaded_files:
                file_path = handle_uploaded_file(uf, temp_dir)
                if file_path.endswith(".zip"):
                    extracted = extract_pdfs_from_zip(file_path, temp_dir)
                    all_pdf_paths.extend(extracted)
                elif file_path.endswith(".pdf"):
                    all_pdf_paths.append(file_path)

            results = []
            output_dir = os.path.join(temp_dir, "results")
            os.makedirs(output_dir, exist_ok=True)

            for pdf_path in all_pdf_paths:
                with st.spinner(f"Analyzing {os.path.basename(pdf_path)}..."):
                    result = process_file(pdf_path, output_dir)
                    results.append(result)

            st.success("Batch processing complete.")
            for res in results:
                st.markdown(f"### {res['filename']}")
                if res["error"]:
                    st.error(f"Error: {res['error']}")
                else:
                    st.markdown(f"- YAML: `{os.path.basename(res['yaml'])}`")
                    st.markdown(f"- Affidavit: `{os.path.basename(res['affidavit'])}`")
                    st.markdown("- GPT Summary:")
                    st.code(res["gpt_summary"] or "N/A", language="markdown")

            # Bundle ZIP
            zip_path = os.path.join(temp_dir, "evidence_bundle.zip")
            bundle_evidence_outputs(output_dir, zip_path)
            with open(zip_path, "rb") as f:
                st.download_button("Download Full ZIP Bundle", f, file_name="evidence_bundle.zip")

if __name__ == "__main__":
    main()