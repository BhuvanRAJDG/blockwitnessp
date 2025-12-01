# backend/app.py
"""
BlockWitness backend (Postgres on Render / SQLite for local dev)

Behavior:
- If DATABASE_URL env var is set (Render), the app will use that DB (Postgres recommended).
- Otherwise app uses a local SQLite DB file at ./chain.db for convenience (NOT for production).
"""

import os
import time
import json
import uuid
import hashlib
import base64
from io import BytesIO
from pathlib import Path

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

# SQLAlchemy imports
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    select,
    desc,
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# Optional libs
try:
    import qrcode
except Exception:
    qrcode = Nones

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
except Exception:
    canvas = None
    A4 = None
    ImageReader = None

# ----------------------
# Paths + upload dir
# ----------------------
BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# ----------------------
# Database configuration
# ----------------------
DATABASE_URL = os.getenv("DATABASE_URL")

# NOTE:
# - On Render, set DATABASE_URL to the provided Postgres URL in Environment.
# - Locally (if DATABASE_URL is not set) we fallback to a SQLite file for dev.
if DATABASE_URL:
    engine = create_engine(DATABASE_URL, future=True)
else:
    sqlite_path = BASE_DIR / "chain.db"
    engine = create_engine(f"sqlite:///{sqlite_path}", future=True, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, future=True)

Base = declarative_base()


# ----------------------
# Models
# ----------------------
class Block(Base):
    __tablename__ = "blocks"

    idx = Column(Integer, primary_key=True, autoincrement=False)  # we control idx assignment
    timestamp = Column(String, nullable=False)
    previous_hash = Column(String(128), nullable=False)
    merkle_root = Column(String(128), nullable=False)
    block_hash = Column(String(128), nullable=False)

    # relationship to transactions
    transactions = relationship("Transaction", back_populates="block")


class Transaction(Base):
    __tablename__ = "transactions"

    tx_id = Column(String, primary_key=True, index=True)
    block_idx = Column(Integer, ForeignKey("blocks.idx"), nullable=False, index=True)
    report_id = Column(String, nullable=False, index=True)
    title = Column(String, nullable=True)
    uploader = Column(String, nullable=True)
    metadata = Column(Text, nullable=True)  # store JSON string
    report_hash = Column(String(128), nullable=False)

    block = relationship("Block", back_populates="transactions")


# Create tables
Base.metadata.create_all(bind=engine)


# ----------------------
# Flask app setup
# ----------------------
app = Flask(__name__)

FRONTEND_ORIGIN = os.environ.get("FRONTEND_ORIGIN")
if FRONTEND_ORIGIN:
    CORS(app, origins=[FRONTEND_ORIGIN])
else:
    CORS(app)


# ----------------------
# Utils (same as before)
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
    if not hash_list:
        return ""
    cur = [h for h in hash_list]
    while len(cur) > 1:
        nxt = []
        for i in range(0, len(cur), 2):
            a = cur[i]
            b = cur[i + 1] if i + 1 < len(cur) else cur[i]
            nxt.append(hashlib.sha256((a + b).encode()).hexdigest())
        cur = nxt
    return cur[0]


def merkle_proof(hash_list, leaf):
    if leaf not in hash_list:
        return None
    layer = [h for h in hash_list]
    proof = []
    idx = layer.index(leaf)
    while len(layer) > 1:
        nxt = []
        for i in range(0, len(layer), 2):
            a = layer[i]
            b = layer[i + 1] if i + 1 < len(layer) else layer[i]
            if i == idx or i + 1 == idx:
                if i == idx:
                    sibling = b
                    position = "right"
                else:
                    sibling = a
                    position = "left"
                proof.append({"sibling": sibling, "position": position})
                new_hash = hashlib.sha256((a + b).encode()).hexdigest()
                nxt.append(new_hash)
                idx = len(nxt) - 1
            else:
                new_hash = hashlib.sha256((a + b).encode()).hexdigest()
                nxt.append(new_hash)
        layer = nxt
    return proof


# ----------------------
# Database helpers
# ----------------------
def get_last_block(session):
    """Return the last block row or None (ordered by idx desc)."""
    stmt = select(Block).order_by(desc(Block.idx)).limit(1)
    res = session.execute(stmt).scalars().first()
    return res


# ----------------------
# Routes
# ----------------------
@app.route("/db-test", methods=["GET"])
def test_db():
    try:
        # simple test query
        with SessionLocal() as session:
            session.execute(select(1))
        return {"status": "Database Connected"}
    except Exception as e:
        return {"status": "Database Error", "message": str(e)}


@app.get("/")
def home():
    return {"status": "BlockWitness backend running successfully!"}


@app.route("/api/explorer", methods=["GET"])
def explorer():
    with SessionLocal() as session:
        stmt = select(Block).order_by(desc(Block.idx)).limit(100)
        rows = session.execute(stmt).scalars().all()
        out = [
            {
                "idx": b.idx,
                "timestamp": b.timestamp,
                "block_hash": b.block_hash,
                "merkle_root": b.merkle_root,
            }
            for b in rows
        ]
    return jsonify(out)


@app.route("/api/block/<int:idx>", methods=["GET"])
def get_block(idx):
    with SessionLocal() as session:
        b = session.get(Block, idx)
        if not b:
            return jsonify({"error": "block not found"}), 404
        txs = [
            {
                "tx_id": t.tx_id,
                "report_id": t.report_id,
                "title": t.title,
                "uploader": t.uploader,
                "metadata": json.loads(t.metadata) if t.metadata else {},
                "report_hash": t.report_hash,
            }
            for t in b.transactions
        ]
        out = {
            "idx": b.idx,
            "timestamp": b.timestamp,
            "previous_hash": b.previous_hash,
            "merkle_root": b.merkle_root,
            "block_hash": b.block_hash,
            "transactions": txs,
        }
    return jsonify(out)


@app.route("/api/report", methods=["POST"])
def create_report():
    title = request.form.get("title", "Untitled")
    uploader = request.form.get("uploader", "anonymous")
    description = request.form.get("description", "")
    metadata = {
        "description": description,
        "location": request.form.get("location", ""),
        "time": request.form.get("time", ""),
    }

    files = request.files.getlist("files")
    evidence = []
    for f in files:
        filename = f.filename or ("file_" + uuid.uuid4().hex)
        unique = f"{uuid.uuid4().hex}_{filename}"
        path = UPLOAD_DIR / unique
        f.save(path)
        file_hash = sha256_file(path)
        evidence.append(
            {
                "filename": unique,
                "sha256": file_hash,
                "mimetype": f.mimetype,
                "size": path.stat().st_size,
            }
        )

    report = {
        "report_id": uuid.uuid4().hex,
        "title": title,
        "uploader": uploader,
        "metadata": metadata,
        "evidence": evidence,
    }
    report_bytes = json.dumps(report, sort_keys=True).encode()
    report_hash = sha256_bytes(report_bytes)

    tx_id = "tx_" + uuid.uuid4().hex
    ev_hashes = [e["sha256"] for e in evidence] + [report_hash]
    # dedupe in case duplicates
    ev_hashes = [h for i, h in enumerate(ev_hashes) if h and h not in ev_hashes[:i]]
    root = merkle_root(ev_hashes)

    # create block + transaction inside DB session
    with SessionLocal() as session:
        last = get_last_block(session)
        prev_hash = last.block_hash if last else "0" * 64
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%S%z")
        idx = (last.idx + 1) if last else 0

        block_payload = {
            "idx": idx,
            "timestamp": timestamp,
            "previous_hash": prev_hash,
            "merkle_root": root,
            "transactions": [tx_id],
        }
        block_hash = sha256_bytes(json.dumps(block_payload, sort_keys=True).encode())

        # create ORM objects
        blk = Block(
            idx=idx,
            timestamp=timestamp,
            previous_hash=prev_hash,
            merkle_root=root,
            block_hash=block_hash,
        )
        tx = Transaction(
            tx_id=tx_id,
            block_idx=idx,
            report_id=report["report_id"],
            title=title,
            uploader=uploader,
            metadata=json.dumps(metadata),
            report_hash=report_hash,
        )

        session.add(blk)
        session.add(tx)
        session.commit()

    # persist report JSON to uploads folder (for later verification or certificate)
    with open(UPLOAD_DIR / (report["report_id"] + ".json"), "wb") as fh:
        fh.write(report_bytes)

    return (
        jsonify(
            {
                "report_id": report["report_id"],
                "tx_id": tx_id,
                "block_index": idx,
                "block_hash": block_hash,
            }
        ),
        201,
    )


@app.route("/api/verify", methods=["POST"])
def verify_file():
    f = request.files.get("file")
    if not f:
        return jsonify({"error": "no file provided"}), 400
    tmp = UPLOAD_DIR / ("tmp_" + uuid.uuid4().hex)
    f.save(tmp)
    h = sha256_file(tmp)
    matches = []

    with SessionLocal() as session:
        # join transactions + blocks (via relationship)
        stmt = select(Transaction, Block).join(Block, Transaction.block_idx == Block.idx)
        for tx, blk in session.execute(stmt):
            report_id = tx.report_id
            report_path = UPLOAD_DIR / (report_id + ".json")
            if report_path.exists():
                rep = json.loads(report_path.read_bytes())
                for e in rep.get("evidence", []):
                    if e.get("sha256") == h:
                        matches.append(
                            {
                                "tx_id": tx.tx_id,
                                "report_id": report_id,
                                "block_idx": tx.block_idx,
                                "block_hash": blk.block_hash,
                                "merkle_root": blk.merkle_root,
                            }
                        )

    tmp.unlink(missing_ok=True)
    return jsonify({"matches": matches})


@app.route("/api/block/<int:idx>/qr", methods=["GET"])
def block_qr(idx):
    frontend_origin = os.environ.get("FRONTEND_ORIGIN", FRONTEND_ORIGIN or "http://localhost:5173")
    verification_url = f"{frontend_origin}/explorer?block={idx}"
    if qrcode is None:
        return jsonify({"error": "qrcode not installed", "verification_url": verification_url})
    img = qrcode.make(verification_url)
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode()
    return jsonify({"qr_base64": b64, "verification_url": verification_url})


@app.route("/api/block/<int:idx>/merkle", methods=["GET"])
def block_merkle(idx):
    leaf = request.args.get("leaf", "").strip()
    with SessionLocal() as session:
        b = session.get(Block, idx)
        if not b:
            return jsonify({"error": "block not found"}), 404

        # get all evidence hashes for the block by iterating transactions and reading stored report JSONs
        stmt = select(Transaction).where(Transaction.block_idx == idx)
        rows = session.execute(stmt).scalars().all()
        ev_hashes = []
        for r in rows:
            report_id = r.report_id
            report_path = UPLOAD_DIR / (report_id + ".json")
            if report_path.exists():
                rep = json.loads(report_path.read_bytes())
                for e in rep.get("evidence", []):
                    ev_hashes.append(e.get("sha256"))
                rep_bytes = json.dumps(rep, sort_keys=True).encode()
                rep_hash = sha256_bytes(rep_bytes)
                ev_hashes.append(rep_hash)

        # dedupe preserving order
        ev_hashes = [h for i, h in enumerate(ev_hashes) if h and h not in ev_hashes[:i]]
        root = b.merkle_root
        if not ev_hashes:
            return jsonify({"error": "no evidence hashes for block"}), 400
        if not leaf:
            leaf = ev_hashes[-1]
        proof = merkle_proof(ev_hashes, leaf)
        valid = False
        if proof is not None:
            cur = leaf
            for p in proof:
                sib = p["sibling"]
                if p["position"] == "left":
                    cur = hashlib.sha256((sib + cur).encode()).hexdigest()
                else:
                    cur = hashlib.sha256((cur + sib).encode()).hexdigest()
            valid = (cur == root)
    return jsonify({"root": root, "proof": proof, "leaf": leaf, "valid": valid, "all_leaves": ev_hashes})


@app.route("/api/report/<report_id>/certificate", methods=["GET"])
def report_certificate(report_id):
    report_path = UPLOAD_DIR / (f"{report_id}.json")
    if not report_path.exists():
        return jsonify({"error": "report JSON not found"}), 404
    report = json.loads(report_path.read_bytes())
    with SessionLocal() as session:
        stmt = select(Transaction).where(Transaction.report_id == report_id)
        tx = session.execute(stmt).scalars().first()
        if not tx:
            return jsonify({"error": "transaction not found"}), 404
        block_idx = tx.block_idx
        blk = session.get(Block, block_idx)

    if canvas is None or A4 is None or ImageReader is None:
        return (
            jsonify(
                {
                    "warning": "reportlab not installed; install to generate PDF",
                    "report": report,
                    "transaction": {
                        "tx_id": tx.tx_id,
                        "block_idx": tx.block_idx,
                        "report_id": tx.report_id,
                        "title": tx.title,
                        "uploader": tx.uploader,
                    },
                    "block": {
                        "idx": blk.idx,
                        "block_hash": blk.block_hash,
                        "timestamp": blk.timestamp,
                        "merkle_root": blk.merkle_root,
                    }
                    if blk
                    else None,
                }
            ),
            200,
        )

    buf = BytesIO()
    cpdf = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    cpdf.setFont("Helvetica-Bold", 18)
    cpdf.drawString(40, height - 60, "BlockWitness — Evidence Certificate")
    cpdf.setFont("Helvetica", 12)
    cpdf.drawString(40, height - 90, f"Report ID: {report_id}")
    cpdf.drawString(40, height - 110, f"Title: {report.get('title')}")
    cpdf.drawString(40, height - 130, f"Uploader: {report.get('uploader')}")
    cpdf.drawString(40, height - 150, f"Block Index: {block_idx}")
    if blk:
        cpdf.drawString(40, height - 170, f"Block Hash: {blk.block_hash}")
        cpdf.drawString(40, height - 190, f"Timestamp: {blk.timestamp}")
    thumb_y = height - 320
    try:
        thumb_path = None
        if report.get("evidence"):
            fn = report["evidence"][0].get("filename")
            p = UPLOAD_DIR / fn
            if p.exists():
                thumb_path = p
        if not thumb_path:
            thumb_path = Path("/mnt/data/8c099852-aacd-4177-bd7b-db36ae98c0d2.png")
        if thumb_path.exists():
            img_reader = ImageReader(str(thumb_path))
            cpdf.drawImage(img_reader, 40, thumb_y, width=200, height=120, preserveAspectRatio=True)
    except Exception:
        pass
    desc = report.get("metadata", {}).get("description", "")
    cpdf.setFont("Helvetica", 10)
    text = cpdf.beginText(260, int(thumb_y + 100))
    text.textLines(
        f"Description: {desc}\n\nThis certificate proves the report was recorded in the BlockWitness ledger. Verify at the BlockWitness Explorer using the block hash or the report ID."
    )
    cpdf.drawText(text)
    cpdf.setFont("Helvetica-Oblique", 9)
    cpdf.drawString(40, 50, "Generated by BlockWitness (demo) — not a legal document.")
    cpdf.showPage()
    cpdf.save()
    buf.seek(0)
    return send_file(buf, mimetype="application/pdf", download_name=f"certificate_{report_id}.pdf", as_attachment=True)


@app.route("/api/chain/verify", methods=["GET"])
def chain_verify():
    problems = []
    with SessionLocal() as session:
        stmt = select(Block).order_by(Block.idx.asc())
        blocks = session.execute(stmt).scalars().all()
        prev_hash = None
        for b in blocks:
            # collect tx ids for recompute
            stmt_t = select(Transaction).where(Transaction.block_idx == b.idx).order_by(Transaction.tx_id)
            txs = [t.tx_id for t in session.execute(stmt_t).scalars().all()]
            payload = {"idx": b.idx, "timestamp": b.timestamp, "previous_hash": b.previous_hash, "merkle_root": b.merkle_root, "transactions": txs}
            recomputed = sha256_bytes(json.dumps(payload, sort_keys=True).encode())
            if recomputed != b.block_hash:
                problems.append({"idx": b.idx, "issue": "block_hash_mismatch", "expected": b.block_hash, "recomputed": recomputed})
            if prev_hash is not None and b.previous_hash != prev_hash:
                problems.append({"idx": b.idx, "issue": "previous_hash_mismatch", "expected_prev": prev_hash, "got": b.previous_hash})
            prev_hash = b.block_hash
    return jsonify({"ok": len(problems) == 0, "problems": problems})


@app.route("/api/chain/timeline", methods=["GET"])
def chain_timeline():
    with SessionLocal() as session:
        stmt = select(Block).order_by(desc(Block.idx))
        blocks = session.execute(stmt).scalars().all()
        out = []
        for b in blocks:
            stmt_t = select(Transaction).where(Transaction.block_idx == b.idx).order_by(Transaction.tx_id)
            txs = [
                {
                    "tx_id": t.tx_id,
                    "title": t.title,
                    "uploader": t.uploader,
                    "report_id": t.report_id,
                }
                for t in session.execute(stmt_t).scalars().all()
            ]
            out.append(
                {
                    "idx": b.idx,
                    "timestamp": b.timestamp,
                    "block_hash": b.block_hash,
                    "merkle_root": b.merkle_root,
                    "transactions": txs,
                }
            )
    return jsonify(out)


# ----------------------
# Run
# ----------------------
if __name__ == "__main__":
    # For local testing only; in production (Render) use gunicorn:
    # gunicorn app:app --bind 0.0.0.0:$PORT
    port = int(os.environ.get("PORT", "8000"))
    app.run(host="0.0.0.0", port=port, debug=False)
