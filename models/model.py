import requests
import re

def classify(email_body: str) -> str:
    prompt = f"""
[INST]
You are an AI that classifies warehouse issue emails.
Classify the following email into exactly one of:
missing_asn, missing_po, missing_pallet, quantity_mismatch

Only return that label—no explanation, no punctuation.
Email: {email_body}
[/INST]
""".strip()

    payload = {
        "model": "mistral",
        "prompt": prompt,
        "stream": False
    }

    try:
        # 1. Send request
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=payload,
            timeout=120
        )
        response.raise_for_status()

        # 2. Parse JSON
        result = response.json()

        # 3. DEBUG: show the entire JSON reply
        print("Full API response:", result)

        # 4. Extract the actual text
        raw_output = (
            result.get("response")
            or (result.get("message") or {}).get("content")
            or result.get("message")
            or ""
        ).lower().strip()
        print("LLM raw output:", raw_output)

        # 5. Match one of our labels
        valid_labels = ["missing_asn", "missing_po", "missing_pallet", "quantity_mismatch"]
        # exact match
        if raw_output in valid_labels:
            return raw_output
        # regex match
        pattern = r'\b(' + '|'.join(valid_labels) + r')\b'
        m = re.search(pattern, raw_output)
        if m:
            return m.group(1)
        # substring fallback
        for lbl in valid_labels:
            if lbl in raw_output:
                return lbl

        return "unknown"

    except Exception as e:
        print("Classification error:", e)
        return "unknown"
