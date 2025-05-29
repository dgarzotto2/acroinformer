import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_fraud_summary(entities, metadata=None, suppression_flags=None):
    """
    Runs GPT to interpret extracted entities and suppression patterns.
    Prioritizes CID, ASCII85, registry key patterns, foreign scripts, and suspicious amounts.
    """

    prompt = f"""
You are a forensic document auditor. A PDF has been decoded using multiple methods including CID font extraction, ASCII85 decoding, and OCR. Here are the decoded entities and indicators:

Entities:
{entities}

Metadata:
{metadata if metadata else 'None'}

Suppression Flags:
{suppression_flags if suppression_flags else 'None'}

Please provide a forensic summary of this document, including:
- Possible obfuscation methods
- Roles of named entities (grantor, grantee, intermediary)
- Potential real transaction value vs symbolic/fake values
- Routing anomalies or foreign involvement
- If registry keys imply suppressed individuals

Output as a structured fraud_summary dict.
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a forensic PDF analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=512
        )

        content = response['choices'][0]['message']['content']
        return {"fraud_summary": content.strip()}

    except Exception as e:
        return {"error": str(e)}