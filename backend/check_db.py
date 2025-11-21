import sqlite3

conn = sqlite3.connect("chain.db")
c = conn.cursor()

print("\n--- TRANSACTIONS TABLE ---")
for row in c.execute("SELECT tx_id, report_id, title, uploader, metadata, block_idx FROM transactions"):
    print(row)

print("\n--- BLOCKS TABLE ---")
for row in c.execute("SELECT idx, timestamp, previous_hash, merkle_root, block_hash FROM blocks"):
    print(row)

conn.close()
