import streamlit as st
import tempfile
import os
from metadata import analyze_batch

st.set_page_config(page_title="PDF Metadata & Tampering Risk Audit", layout="wide")

def main():
    st.title("📄 PDF Metadata & Tampering Risk Audit")
    uploaded_files = st.file_uploader("Upload one or more PDF files", type=["pdf"], accept_multiple_files=True)

    if uploaded_files:
        with tempfile.TemporaryDirectory() as temp_dir:
            paths = []
            for f in uploaded_files:
                path = os.path.join(temp_dir, f.name)
                with open(path, "wb") as out:
                    out.write(f.read())
                paths.append(path)

            results = analyze_batch(paths)

            for r in results:
                st.divider()
                st.subheader(f"📘 File: `{r['filename']}`")
                st.markdown(f"**SHA-256:** `{r['sha256']}`")
                st.markdown("### Metadata Summary:")
                st.markdown(f"- **Title:** {r.get('title')}")
                st.markdown(f"- **Author:** {r.get('author')}")
                st.markdown(f"- **Producer:** {r.get('producer')}")
                st.markdown(f"- **Creator:** {r.get('creator')}")
                st.markdown(f"- **Creation Date:** {r.get('creation_date')}")
                st.markdown(f"- **Modification Date:** {r.get('mod_date')}")
                st.markdown(f"- **Document ID:** {r.get('doc_id')}")
                st.markdown(f"- **Custom UUID:** {r.get('custom_uuid')}")
                st.markdown(f"- **CID Fonts Detected:** {'Yes' if r['cid_font'] else 'No'}")

                st.markdown("### Entities Found:")
                grantors = ", ".join(r["entities"]["grantors"]) or "*None detected*"
                grantees = ", ".join(r["entities"]["grantees"]) or "*None detected*"
                st.markdown(f"- **Grantors:** {grantors}")
                st.markdown(f"- **Grantees:** {grantees}")

                if r["fraud_flags"]:
                    st.markdown("### 🚨 Fraud Flags:")
                    for flag in r["fraud_flags"]:
                        st.error(f"• {flag}")
                else:
                    st.success("✅ No cross-file or CID-based fraud detected.")

if __name__ == "__main__":
    main()