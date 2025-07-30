
                insert_pallets_from_excel(df, po_id=po or df.iloc[0]["po_id"], asn_id=asn or df.iloc[0]["asn_id"])
                if check_pallet_exists(po_id=po, asn_id=asn, pallet_id=pallet_id):
                    html = generate_html_snippet(df[df["pallet_id"] == pallet_id])
                    send_email(user_email, "Pallet Resolved", f"Pallet {pallet_id} added and interfaced successfully.<br><br>{html}", html_format=True)
                else:
                    send_email(user_email, "Pallet Missing", f"Pallet {pallet_id} not found even after SAP file received.")
            else:
                send_email(user_email, "Pallet Info Missing", "No SAP file received for missing pallet. Timeout occurred.")

    elif scenario == "quantity_mismatch":
        po = params.get("po")
        pallet_id = params.get("pallet_id")
        asn = params.get("asn")

        identifiers = ", ".join([f"{k.upper()}: {v}" for k, v in params.items() if v])
        send_email("warehouse.sap.123@gmail.com", "Quantity Mismatch", f"Please share file for mismatch: {identifiers}")

        path = wait_for_excel_from_sap("mismatch")
        if path:
            df = parse_excel_to_df(path)
            insert_pallets_from_excel(df, po_id=po or df.iloc[0]["po_id"], asn_id=asn or df.iloc[0]["asn_id"])
            summary = get_po_vs_asn_qty_summary(po)
            if summary["po_qty"] == summary["asn_qty"]:
                html = generate_html_snippet(df)
                send_email(user_email, "Mismatch Resolved", f"Quantities match after update.<br><br>{html}", html_format=True)
            else:
                send_email(user_email, "Mismatch Partially Resolved", f"Quantities still not matching. Please investigate manually.")
        else:
            send_email(user_email, "Mismatch Excel Missing", "SAP didn't respond with Excel for mismatch resolution. Timeout occurred.")
