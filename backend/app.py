# backend/app.py
import os
import time
import json
import uuid
import hashlib
import sqlite3
import base64
from io import BytesIO
from pathlib import Path
from flask import Flask, request, jsonify, send_file, abort
from flask_cors import CORS

try:
    import qrcode
except Exception:
    qrcode = None

BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
DB_PATH = BASE_DIR / "chain.db"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(__name__)
CORS(app)

# ----------------------
# Utilities
# ----------------------
def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def merkle_root(hash_list):
    # simple merkle: if empty -> '', if single -> that hash, else pairwise combine
    if not hash_list:
        return ""
    cur = [h for h in hash_list]
    while len(cur) > 1:
        nxt = []
        for i in range(0, len(cur), 2):
            a = cur[i]
            b = cur[i+1] if i+1 < len(cur) else cur[i]
            nxt.append(hashlib.sha256((a + b).encode()).hexdigest())
        cur = nxt
    return cur[0]

# ----------------------
# DB init
# ----------------------
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    # blocks: idx integer primary key, timestamp, previous_hash, merkle_root, block_hash
    c.execute("""
    CREATE TABLE IF NOT EXISTS blocks (
        idx INTEGER PRIMARY KEY,
        timestamp TEXT,
        previous_hash TEXT,
        merkle_root TEXT,
        block_hash TEXT
    )
    """)
    # transactions: tx_id, block_idx, report_id, title, uploader, metadata (json), report_hash
    c.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        tx_id TEXT PRIMARY KEY,
        block_idx INTEGER,
        report_id TEXT,
        title TEXT,
        uploader TEXT,
        metadata TEXT,
        report_hash TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()

def get_last_block():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM blocks ORDER BY idx DESC LIMIT 1")
    r = c.fetchone()
    conn.close()
    return r

# ----------------------
# Endpoints
# ----------------------

@app.route("/api/explorer", methods=["GET"])
def explorer():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT idx, timestamp, block_hash, merkle_root FROM blocks ORDER BY idx DESC LIMIT 100")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return jsonify(rows)

@app.route("/api/block/<int:idx>", methods=["GET"])
def get_block(idx):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM blocks WHERE idx=?", (idx,))
    b = c.fetchone()
    if not b:
        conn.close()
        return jsonify({"error": "block not found"}), 404
    c.execute("SELECT * FROM transactions WHERE block_idx=?", (idx,))
    txs = [dict(r) for r in c.fetchall()]
    conn.close()
    out = dict(b)
    out["transactions"] = txs
    return jsonify(out)

@app.route("/api/report", methods=["POST"])
def create_report():
    title = request.form.get("title", "Untitled")
    uploader = request.form.get("uploader", "anonymous")
    description = request.form.get("description", "")
    metadata = {
        "description": description,
        "location": request.form.get("location", ""),
        "time": request.form.get("time", "")
    }

    files = request.files.getlist("files")
    evidence = []
    for f in files:
        filename = f.filename or ("file_" + uuid.uuid4().hex)
        unique = f"{uuid.uuid4().hex}_{filename}"
        path = UPLOAD_DIR / unique
        f.save(path)
        file_hash = sha256_file(path)
        evidence.append({
            "filename": unique,
            "sha256": file_hash,
            "mimetype": f.mimetype,
            "size": path.stat().st_size
        })

    report = {
        "report_id": uuid.uuid4().hex,
        "title": title,
        "uploader": uploader,
        "metadata": metadata,
        "evidence": evidence
    }
    report_bytes = json.dumps(report, sort_keys=True).encode()
    report_hash = sha256_bytes(report_bytes)

    # transaction id
    tx_id = "tx_" + uuid.uuid4().hex

    # compute merkle root using evidence hashes + report_hash
    ev_hashes = [e["sha256"] for e in evidence] + [report_hash]
    root = merkle_root(ev_hashes)

    # create block
    last = get_last_block()
    prev_hash = last["block_hash"] if last else "0" * 64
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    conn = get_conn()
    c = conn.cursor()
    # block index
    idx = (last["idx"] + 1) if last else 0
    block_payload = {"idx": idx, "timestamp": timestamp, "previous_hash": prev_hash, "merkle_root": root, "transactions": [tx_id]}
    block_hash = sha256_bytes(json.dumps(block_payload, sort_keys=True).encode())

    c.execute("INSERT INTO blocks (idx, timestamp, previous_hash, merkle_root, block_hash) VALUES (?, ?, ?, ?, ?)",
              (idx, timestamp, prev_hash, root, block_hash))
    c.execute("INSERT INTO transactions (tx_id, block_idx, report_id, title, uploader, metadata, report_hash) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (tx_id, idx, report["report_id"], title, uploader, json.dumps(metadata), report_hash))
    conn.commit()
    conn.close()

    # save report JSON alongside uploads for later reference
    with open(UPLOAD_DIR / (report["report_id"] + ".json"), "wb") as fh:
        fh.write(report_bytes)

    return jsonify({
        "report_id": report["report_id"],
        "tx_id": tx_id,
        "block_index": idx,
        "block_hash": block_hash
    }), 201

@app.route("/api/verify", methods=["POST"])
def verify_file():
    f = request.files.get("file")
    if not f:
        return jsonify({"error": "no file provided"}), 400
    tmp = UPLOAD_DIR / ("tmp_" + uuid.uuid4().hex)
    f.save(tmp)
    h = sha256_file(tmp)
    matches = []
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT t.*, b.block_hash, b.merkle_root, b.idx FROM transactions t JOIN blocks b ON t.block_idx=b.idx")
    for r in c.fetchall():
        report_id = r["report_id"]
        report_path = UPLOAD_DIR / (report_id + ".json")
        if report_path.exists():
            rep = json.loads(report_path.read_bytes())
            for e in rep.get("evidence", []):
                if e.get("sha256") == h:
                    matches.append({
                        "tx_id": r["tx_id"],
                        "report_id": report_id,
                        "block_idx": r["block_idx"],
                        "block_hash": r["block_hash"],
                        "merkle_root": r["merkle_root"]
                    })
    conn.close()
    tmp.unlink(missing_ok=True)
    return jsonify({"matches": matches})

@app.route("/api/block/<int:idx>/qr", methods=["GET"])
def block_qr(idx):
    frontend_origin = os.environ.get("FRONTEND_ORIGIN", "http://localhost:5173")
    verification_url = f"{frontend_origin}/explorer?block={idx}"
    if qrcode is None:
        return jsonify({"error": "qrcode library not installed", "verification_url": verification_url})
    img = qrcode.make(verification_url)
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode()
    return jsonify({"qr_base64": b64, "verification_url": verification_url})

@app.route("/api/search", methods=["GET"])
def search():
    """
    Robust search: checks transactions table and the saved report JSON files.
    Matches if the query appears (case-insensitive) in:
      - transaction.title
      - transaction.uploader
      - transaction.metadata (description)
      - saved report JSON content (anywhere)
      - tx_id, report_id, or block index (text)
    """
    import sqlite3  # local import to be safe if file moved
    q = request.args.get("q", "")
    q = q.strip()
    if not q:
        return jsonify([])

    q_lower = q.lower()
    results = []
    conn = get_conn()
    c = conn.cursor()

    # Get all transactions (we'll filter in Python, this is fine for demo size)
    c.execute("SELECT tx_id, report_id, title, uploader, metadata, block_idx FROM transactions ORDER BY block_idx DESC")
    rows = c.fetchall()

    for r in rows:
        tx_id = r["tx_id"]
        report_id = r["report_id"]
        title = r["title"] or ""
        uploader = r["uploader"] or ""
        metadata_raw = r["metadata"] or ""
        block_idx = r["block_idx"]

        # Assemble searchable text
        combined = " ".join([
            str(title),
            str(uploader),
            str(metadata_raw),
            str(tx_id),
            str(report_id),
            str(block_idx)
        ]).lower()

        # Quick in-DB check: if q is substring of combined, tentatively match
        match = q_lower in combined

        # If not matched yet, also try reading saved report JSON (if exists) to search full report fields
        if not match:
            report_path = UPLOAD_DIR / (f"{report_id}.json")
            if report_path.exists():
                try:
                    txt = report_path.read_text(encoding="utf-8").lower()
                    if q_lower in txt:
                        match = True
                except Exception:
                    # ignore read errors and continue
                    pass

        if match:
            # Parse metadata JSON safely to fetch description if possible
            desc = ""
            try:
                meta_obj = json.loads(metadata_raw) if metadata_raw else {}
                desc = meta_obj.get("description", "") if isinstance(meta_obj, dict) else ""
            except Exception:
                desc = ""

            results.append({
                "tx_id": tx_id,
                "report_id": report_id,
                "title": title,
                "uploader": uploader,
                "description": desc,
                "block_index": block_idx
            })

    conn.close()
    return jsonify(results)



if __name__ == "__main__":
    # listen on all interfaces for LAN testing; change host if you prefer localhost only
    app.run(host="0.0.0.0", port=5001, debug=True)
