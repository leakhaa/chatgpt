from scripts.email_handler import send_email, wait_for_excel_from_sap
from scripts.db import (
    check_asn_exists, check_po_exists, check_pallet_exists,
    get_po_vs_asn_qty_summary
)
from scripts.utils import (
    parse_excel_to_df, insert_pallets_from_excel,
    fetch_rows, generate_html_snippet
)

def resolve_issue(scenario, params, user_email):
    print(f"Resolving scenario: {scenario}")

    if scenario == "missing_asn":
        asn = params.get("asn")
        if not asn:
            send_email(user_email, "ASN Error", "ASN ID missing.")
            return

        if check_asn_exists(asn):
            rows = fetch_rows("asn_header", "WHERE asn_id = ?", (asn,))
            html = generate_html_snippet(rows, "asn_id", asn)
            send_email(user_email, "ASN Found", f"ASN {asn} already interfaced.<br><br>{html}", html_format=True)
        else:
            send_email("warehouse.sap.123@gmail.com", "Trigger ASN", f"Please trigger ASN {asn}.")
            # No Excel – wait for SAP to respond and re-check later
            send_email(user_email, "ASN Triggered", f"ASN {asn} has been requested. We’ll notify you once interfaced.")

    elif scenario == "missing_po":
        po = params.get("po")
        if not po:
            send_email(user_email, "PO Error", "PO ID missing.")
            return

        if check_po_exists(po):
            summary = get_po_vs_asn_qty_summary(po)
            if summary["po_pallets"] == summary["asn_pallets"] and summary["po_qty"] == summary["asn_qty"]:
                rows = fetch_rows("po_header", "WHERE po_id = ?", (po,))
                html = generate_html_snippet(rows, "po_id", po)
                send_email(user_email, "PO Found", f"PO {po} interfaced successfully.<br><br>{html}", html_format=True)
            else:
                send_email(user_email, "PO Quantity Mismatch", f"PO {po} found, but mismatch detected. Investigating...")
        else:
            send_email("warehouse.sap.123@gmail.com", "Trigger PO", f"Please trigger PO {po}.")
            # No Excel – wait for SAP to respond and re-check later
            send_email(user_email, "PO Triggered", f"PO {po} has been requested. We’ll notify you once interfaced.")

    elif scenario == "missing_pallet":
        pallet_id = params.get("pallet_id")
        po = params.get("po")
        asn = params.get("asn")
        if not pallet_id:
            send_email(user_email, "Pallet Error", "Pallet ID missing.")
            return

        if check_pallet_exists(po_id=po, asn_id=asn, pallet_id=pallet_id):
            send_email(user_email, "Pallet Found", f"Pallet {pallet_id} already exists in system.")
        else:
            send_email("warehouse.sap.123@gmail.com", "Trigger Pallet", f"Missing pallet {pallet_id} for PO {po} and ASN {asn}. Please provide details.")
            path = wait_for_excel_from_sap("pallet")
            df = parse_excel_to_df(path)
            insert_pallets_from_excel(df, po_id=po or df.iloc[0]["po_id"], asn_id=asn or df.iloc[0]["asn_id"])
            if check_pallet_exists(po_id=po, asn_id=asn, pallet_id=pallet_id):
                html = generate_html_snippet(df[df["pallet_id"] == pallet_id])
                send_email(user_email, "Pallet Resolved", f"Pallet {pallet_id} added and interfaced successfully.<br><br>{html}", html_format=True)

    elif scenario == "quantity_mismatch":
        po = params.get("po")
        pallet_id = params.get("pallet_id")
        asn = params.get("asn")

        identifiers = ", ".join([f"{k.upper()}: {v}" for k, v in params.items() if v])
        send_email("warehouse.sap.123@gmail.com", "Quantity Mismatch", f"Please share file for mismatch: {identifiers}")

        path = wait_for_excel_from_sap("mismatch")
        df = parse_excel_to_df(path)
        insert_pallets_from_excel(df, po_id=po or df.iloc[0]["po_id"], asn_id=asn or df.iloc[0]["asn_id"])

        summary = get_po_vs_asn_qty_summary(po)
        if summary["po_qty"] == summary["asn_qty"]:
            html = generate_html_snippet(df)
            send_email(user_email, "Mismatch Resolved", f"Quantities match after update.<br><br>{html}", html_format=True)
        else:
            send_email(user_email, "Mismatch Partially Resolved", f"Quantities still not matching. Please investigate manually.")
