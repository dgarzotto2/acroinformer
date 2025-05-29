import openai
import streamlit as st
import json

def generate_gpt_summary(pdf_analyses):
    openai.api_key = st.secrets["OPENAI_API_KEY"]

    prompt = build_summary_prompt(pdf_analyses)
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "You are a digital forensics expert."},
                      {"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1000
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"⚠️ GPT analysis failed: {str(e)}"

def build_summary_prompt(analyses):
    summary_prompt = (
        "You are a forensic analyst reviewing multiple arbitration agreements for authenticity. "
        "Determine whether tampering, mass-production, synthetic document generation, or invalid signature reuse has occurred. "
        "Highlight any metadata anomalies, AcroForm patterns, or timestamp cloning. Draw legal conclusions. Use plain language.\n\n"
        "Here are the documents:\n"
    )
    for analysis in analyses:
        summary_prompt += format_single_analysis(analysis)
    return summary_prompt

def format_single_analysis(analysis):
    details = f"\n---\n**Document:** {analysis.get('filename', 'Unknown')}\n"
    details += f"• SHA256: {analysis.get('sha256', 'N/A')}\n"
    details += f"• Creation Date: {analysis.get('metadata', {}).get('CreationDate', 'N/A')}\n"
    details += f"• Mod Date: {analysis.get('metadata', {}).get('ModDate', 'N/A')}\n"
    details += f"• XMP Toolkit: {analysis.get('metadata', {}).get('xmp:Toolkit', 'N/A')}\n"
    details += f"• Creator Tool: {analysis.get('metadata', {}).get('xmp:CreatorTool', 'N/A')}\n"
    details += f"• InstanceID: {analysis.get('metadata', {}).get('xmpMM:InstanceID', 'N/A')}\n"
    details += f"• DocumentID: {analysis.get('metadata', {}).get('xmpMM:DocumentID', 'N/A')}\n"
    details += f"• AcroForms Detected: {analysis.get('acroform_flags', [])}\n"
    details += f"• Signature Fields: {analysis.get('signatures', 'N/A')}\n"
    details += f"• Known Forensic Flags: {analysis.get('forensic_flags', [])}\n"
    return details