import streamlit as st
import tempfile
import os
import zipfile
import datetime
from metadata import extract_metadata

st.set_page_config(page_title="AcroInformer Forensic Scanner", layout="centered")

st.title("📄 AcroInformer: PDF Forensic Risk Scanner")
st.markdown("Upload a suspected PDF file to extract hidden metadata, CID fonts, JavaScript, and obfuscation techniques.")

uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

def save_result_to_zip(results, output_path):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    zip_path = os.path.join(output_path, f"acroinformer_results_{timestamp}.zip")
    with zipfile.ZipFile(zip_path, "w") as zipf:
        result_file = os.path.join(output_path, "result.txt")
        with open(result_file, "w") as f:
            for k, v in results.items():
                f.write(f"{k}: {v}\n")
        zipf.write(result_file, arcname="result.txt")
    return zip_path

if uploaded_file:
    with tempfile.TemporaryDirectory() as temp_dir:
        pdf_path = os.path.join(temp_dir, uploaded_file.name)
        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.read())

        st.info("⏳ Scanning PDF for hidden metadata...")
        r = extract_metadata(pdf_path)

        st.success("✅ Scan complete.")
        st.markdown("### Results Summary")
        st.markdown(f"- **CID Font Detected:** {'Yes' if r['cid_font_detected'] else 'No'}")
        st.markdown(f"- **XFA Forms Detected:** {'Yes' if r['xfa_found'] else 'No'}")
        st.markdown(f"- **Launch Action Present:** {'Yes' if r['launch_action'] else 'No'}")
        st.markdown(f"- **AcroForm Present:** {'Yes' if r['acroform_detected'] else 'No'}")
        st.markdown(f"- **Hidden Library Usage:** {'Yes' if r['hidden_lib_usage'] else 'No'}")
        st.markdown("### Fonts Used:")
        st.code("\n".join(r["fonts_used"]) if r["fonts_used"] else "None")
        if r["embedded_js"]:
            st.markdown("### Embedded JavaScript:")
            st.code("\n".join(r["embedded_js"]))
        else:
            st.markdown("### Embedded JavaScript: None")

        st.markdown("---")
        st.markdown("### 🔐 Download Full Report")
        zip_file = save_result_to_zip(r, temp_dir)
        with open(zip_file, "rb") as f:
            st.download_button("Download Forensic Report (.zip)", f, file_name=os.path.basename(zip_file))