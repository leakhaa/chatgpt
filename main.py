from scripts.email_handler import get_unread_emails
from models.model import classify
from scripts.resolver import resolve_issue

import re

# -----------------------
# Map email content to scenario
# -----------------------
def map_to_scenario(text):
    text = text.lower()
    if "asn" in text and "missing" in text:
        return "missing_asn"
    elif "po" in text and "missing" in text:
        return "missing_po"
    elif "pallet" in text and "missing" in text:
        return "missing_pallet"
    elif "quantity" in text or "mismatch" in text or "qty" in text:
        return "quantity_mismatch"
    else:
        return "unknown"

# -----------------------
# Extract ASN, PO, PALLET from email using regex
# -----------------------
def extract_params(text):
    params = {}
    
    # ASN: 5 digits starting with 0
    asn_match = re.search(r'\b0\d{4}\b', text)
    if asn_match:
        params['asn'] = asn_match.group()

    # PO: 10 digits starting with 2
    po_match = re.search(r'\b2\d{9}\b', text)
    if po_match:
        params['po'] = po_match.group()

    # PALLET: 15 digits starting with 5
    pallet_match = re.search(r'\b5\d{14}\b', text)
    if pallet_match:
        params['pallet_id'] = pallet_match.group()
    return params

# -----------------------
# Main entry function
# -----------------------
def main():
    emails = get_unread_emails()
    if not emails:
        print("No new emails to process.")
        return

    for subject, body, sender in emails:
        print(f"\nProcessing email with subject: {subject}")

        # Step 1: Classify the issue
        label = classify(body)
        print(f" AI classification label: {label}")

        # Step 2: Map to your system's scenario
        scenario = map_to_scenario(body)
        print(f" Mapped to scenario: {label}")

        # Step 3: Extract IDs (asn, po, pallet_id) from email text
        params = extract_params(body)
        print(f" Extracted parameters: {params}")

        # Step 4: Call the resolver
        if scenario != "unknown":
            resolve_issue(label, params, user_email=sender)
        else:
            print(" Could not determine scenario. Skipping email.")

if __name__ == "__main__":
     main()
