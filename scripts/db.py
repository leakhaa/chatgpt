import sqlite3

DB_PATH = "db/warehouse.db"  # Update if different

def connect_db():
    return sqlite3.connect(DB_PATH)

def check_asn_exists(asn_id):
    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM asn_header WHERE asn_id = ?", (asn_id,))
        header_exists = cur.fetchone()
        cur.execute("SELECT 1 FROM asn_line WHERE asn_id = ?", (asn_id,))
        line_exists = cur.fetchone()
    return bool(header_exists and line_exists)

def check_po_exists(po_id):
    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM po_header WHERE po_id = ?", (po_id,))
        header_exists = cur.fetchone()
        cur.execute("SELECT 1 FROM po_line WHERE po_id = ?", (po_id,))
        line_exists = cur.fetchone()
        cur.execute("SELECT 1 FROM asn_line WHERE po_id = ?", (po_id,))
        asn_line_exists = cur.fetchone()
    return bool(header_exists or line_exists or asn_line_exists)

def check_pallet_exists(po_id=None, asn_id=None, pallet_id=None):
    with connect_db() as conn:
        cur = conn.cursor()
        results = []

        if po_id:
            cur.execute("SELECT 1 FROM po_line WHERE po_id = ? AND pallet_id = ?", (po_id, pallet_id))
            results.append(cur.fetchone())

        if asn_id:
            cur.execute("SELECT 1 FROM asn_line WHERE asn_id = ? AND pallet_id = ?", (asn_id, pallet_id))
            results.append(cur.fetchone())

    return any(results)

def get_po_vs_asn_qty_summary(po_id):
    with connect_db() as conn:
        cur = conn.cursor()

        # From ASN line
        cur.execute("SELECT COUNT(DISTINCT pallet_id), SUM(qty) FROM asn_line WHERE po_id = ?", (po_id,))
        asn_pallets, asn_qty = cur.fetchone()

        # From PO line
        cur.execute("SELECT COUNT(DISTINCT pallet_id), SUM(qty) FROM po_line WHERE po_id = ?", (po_id,))
        po_pallets, po_qty = cur.fetchone()

    return {
        "asn_pallets": asn_pallets or 0,
        "asn_qty": asn_qty or 0,
        "po_pallets": po_pallets or 0,
        "po_qty": po_qty or 0
    }

def get_all_rows_from_table(table_name, where_clause="", params=()):
    with connect_db() as conn:
        cur = conn.cursor()
        query = f"SELECT * FROM {table_name} {where_clause}"
        cur.execute(query, params)
        return cur.fetchall()
