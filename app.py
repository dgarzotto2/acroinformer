# /mount/src/acroinformer/app.py

import streamlit as st
import tempfile
from metadata import extract_metadata

def main():
    st.set_page_config(page_title="AcroInformer – PDF Metadata Analyzer", layout="centered")
    st.title("AcroInformer")
    st.subheader("PDF Metadata & Tampering Risk Audit")

    uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

    if uploaded_file:
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = f"{temp_dir}/{uploaded_file.name}"
            with open(file_path, "wb") as f:
                f.write(uploaded_file.read())

            st.markdown("### 🔍 Analysis Results")
            try:
                r = extract_metadata(file_path)
            except Exception as e:
                st.error(f"Metadata extraction failed: {e}")
                return

            if not isinstance(r, dict):
                st.warning("No metadata returned or unexpected format.")
                return

            st.markdown(f"- **CID Fonts Detected:** {'Yes' if r.get('cid_font_detected') else 'No'}")
            st.markdown(f"- **XFA Forms Present:** {'Yes' if r.get('xfa_found') else 'No'}")
            st.markdown(f"- **AcroForm Structure:** {'Yes' if r.get('acroform_detected') else 'No'}")
            st.markdown(f"- **LaunchAction Trigger:** {'Yes' if r.get('launch_action') else 'No'}")
            st.markdown(f"- **Hidden Library Usage:** {'Yes' if r.get('hidden_lib_usage') else 'No'}")
            st.markdown(f"- **ByteRange Mismatch:** {'Yes' if r.get('byte_range_mismatch') else 'No'}")
            st.markdown(f"- **Overlays Detected:** {'Yes' if r.get('overlay_detected') else 'No'}")
            st.markdown(f"- **Suspicious XMP Toolkit:** {r.get('xmp_toolkit', 'Unknown')}")
            st.markdown(f"- **PDF Producer:** {r.get('pdf_producer', 'Unknown')}")
            st.markdown(f"- **Tamper Risk Score:** {r.get('risk_score', 'N/A')}")

            st.markdown("### Embedded JavaScript:")
            embedded_js = r.get("embedded_js", [])
            if embedded_js:
                for js_snippet in embedded_js:
                    st.code(js_snippet)
            else:
                st.markdown("*None detected*")

            st.markdown("### Notes:")
            if r.get("notes"):
                for note in r["notes"]:
                    st.markdown(f"- {note}")
            else:
                st.markdown("*No additional notes.*")

    else:
        st.info("Please upload a PDF to begin.")

if __name__ == "__main__":
    main()