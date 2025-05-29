# utils/utility.py

import base64
import streamlit as st

def preview_pdf(pdf_path):
    with open(pdf_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    st.markdown(
        f'<iframe src="data:application/pdf;base64,{encoded}" width="100%" height="600px" type="application/pdf"></iframe>',
        unsafe_allow_html=True
    )