# backend/db.py
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / 'chain.db'

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS blocks (
      idx INTEGER PRIMARY KEY,
      timestamp TEXT,
      previous_hash TEXT,
      merkle_root TEXT,
      block_hash TEXT,
      signature TEXT,
      nonce INTEGER
    )''')
    cur.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
      tx_id TEXT PRIMARY KEY,
      block_idx INTEGER,
      report_id TEXT,
      title TEXT,
      uploader TEXT,
      metadata TEXT,
      report_hash TEXT
    )''')
    conn.commit()
    conn.close()
