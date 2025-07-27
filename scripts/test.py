import sqlite3

# Connect to the database
conn = sqlite3.connect("db/warehouse.db")
cursor = conn.cursor()

# Rename the column: syntax → ALTER TABLE table_name RENAME COLUMN old_name TO new_name
try:
    cursor.execute('select * from asn_header where asn_id like '_5124' ')
    conn.commit() 
    print("Column renamed successfully.")
except sqlite3.OperationalError as e:
    print("Error:", e)

conn.close()
