# backend/app.py
import os, time, json, uuid
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from pathlib import Path
from db import init_db, get_conn
from chain_utils import sha256_file, merkle_root, sha256_bytes
from crypto_utils import sign_hex, verify_hex

UPLOAD_DIR = Path(__file__).parent / 'uploads'
ISSUER_PRIV = Path(__file__).parent / 'issuer_priv.pem'
ISSUER_PUB = Path(__file__).parent / 'issuer_pub.pem'

UPLOAD_DIR.mkdir(exist_ok=True)
app = Flask(__name__)
CORS(app)

# initialize DB
init_db()

def get_last_block(conn):
    cur = conn.cursor()
    cur.execute('SELECT * FROM blocks ORDER BY idx DESC LIMIT 1')
    return cur.fetchone()

@app.route('/api/issuer/pubkey', methods=['GET'])
def get_pubkey():
    return send_file(str(ISSUER_PUB), mimetype='application/octet-stream')

@app.route('/api/explorer', methods=['GET'])
def explorer():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT idx, timestamp, block_hash, merkle_root FROM blocks ORDER BY idx DESC LIMIT 50')
    rows = [dict(r) for r in cur.fetchall()]
    return jsonify(rows)

@app.route('/api/block/<int:idx>', methods=['GET'])
def get_block(idx):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT * FROM blocks WHERE idx=?', (idx,))
    blk = cur.fetchone()
    if not blk:
        return jsonify({'error':'not found'}), 404
    cur.execute('SELECT * FROM transactions WHERE block_idx=?', (idx,))
    txs = [dict(r) for r in cur.fetchall()]
    b = dict(blk)
    b['transactions'] = txs
    return jsonify(b)

@app.route('/api/report', methods=['POST'])
def create_report():
    # form fields: title, description, uploader
    title = request.form.get('title', 'Untitled')
    uploader = request.form.get('uploader', 'anonymous')
    metadata = {
        'description': request.form.get('description',''),
        'location': request.form.get('location',''),
        'time': request.form.get('time','')
    }
    files = request.files.getlist('files')
    evidence = []
    for f in files:
        fname = f.filename
        unique = f"{uuid.uuid4().hex}_{fname}"
        path = UPLOAD_DIR / unique
        f.save(path)
        h = sha256_file(path)
        evidence.append({'filename':unique, 'sha256': h, 'type': f.mimetype, 'size': path.stat().st_size})
    # build report JSON and compute report hash
    report = {
        'report_id': uuid.uuid4().hex,
        'title': title,
        'uploader': uploader,
        'metadata': metadata,
        'evidence': evidence
    }
    report_bytes = json.dumps(report, sort_keys=True).encode()
    report_hash = sha256_bytes(report_bytes)
    # create transaction
    tx_id = 'tx_' + uuid.uuid4().hex
    conn = get_conn()
    cur = conn.cursor()
    # determine merkle root from evidence hashes + report_hash
    ev_hashes = [e['sha256'] for e in evidence] + [report_hash]
    merkle = merkle_root(ev_hashes)
    # prepare new block
    last = get_last_block(conn)
    prev_hash = last['block_hash'] if last else '0'*64
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    # create block entry (nonce simulated)
    block_obj = {
        'idx': (last['idx'] + 1) if last else 0,
        'timestamp': timestamp,
        'previous_hash': prev_hash,
        'merkle_root': merkle,
        'transactions': [tx_id],
        'nonce': 0
    }
    # compute block hash
    block_serial = json.dumps(block_obj, sort_keys=True).encode()
    block_hash = sha256_bytes(block_serial)
    # sign block_hash
    signature = sign_hex(str(ISSUER_PRIV), block_hash)
    # store block
    cur.execute('INSERT INTO blocks (idx, timestamp, previous_hash, merkle_root, block_hash, signature, nonce) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (block_obj['idx'], timestamp, prev_hash, merkle, block_hash, signature, 0))
    # store transaction
    cur.execute('INSERT INTO transactions (tx_id, block_idx, report_id, title, uploader, metadata, report_hash) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (tx_id, block_obj['idx'], report['report_id'], title, uploader, json.dumps(metadata), report_hash))
    conn.commit()
    # save report file (optional)
    with open( Path(UPLOAD_DIR) / (report['report_id'] + '.json'), 'wb') as f:
        f.write(report_bytes)
    return jsonify({
        'report_id': report['report_id'],
        'tx_id': tx_id,
        'block_index': block_obj['idx'],
        'block_hash': block_hash
    }), 201

@app.route('/api/verify', methods=['POST'])
def verify_file():
    # accept either file OR report JSON
    file = request.files.get('file')
    if not file:
        return jsonify({'error':'no file'}), 400
    # compute hash for file
    tmp_path = UPLOAD_DIR / ("tmp_" + uuid.uuid4().hex)
    file.save(tmp_path)
    h = sha256_file(tmp_path)
    conn = get_conn()
    cur = conn.cursor()
    # search transactions where evidence has this hash OR report_hash equals this hash
    cur.execute("SELECT t.*, b.signature, b.block_hash, b.merkle_root, b.idx FROM transactions t JOIN blocks b ON t.block_idx=b.idx")
    rows = cur.fetchall()
    matches = []
    for r in rows:
        # load report JSON if exists
        report_id = r['report_id']
        report_path = Path(UPLOAD_DIR) / (report_id + '.json')
        found = False
        if report_path.exists():
            rep = json.loads(report_path.read_bytes())
            for e in rep.get('evidence', []):
                if e['sha256'] == h:
                    found = True
                    break
        if found:
            matches.append({
                'tx_id': r['tx_id'],
                'report_id': report_id,
                'block_idx': r['block_idx'],
                'block_hash': r['block_hash'],
                'signature': r['signature'],
                'merkle_root': r['merkle_root']
            })
    tmp_path.unlink(missing_ok=True)
    return jsonify({'matches': matches})

if __name__ == '__main__':
    app.run(port=5001, debug=True)
