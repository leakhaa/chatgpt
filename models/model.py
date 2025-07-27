def classify(text):
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
