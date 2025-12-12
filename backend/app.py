# backend/app.py

import os
import json
import hashlib
import qrcode
from datetime import datetime
from io import BytesIO
import base64
from PIL import Image
from flask import Flask, request, jsonify, send_file, redirect, url_for, session
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Text, DateTime, text
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from fpdf import FPDF
import requests
from oauthlib.oauth2 import WebApplicationClient

# Local imports
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chain_utils import sha256_bytes, sha256_file, merkle_root
from crypto_utils import sign_hex, verify_hex

# Flask app setup
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(24).hex())
CORS(app, supports_credentials=True)

# Login manager
login_manager = LoginManager()
login_manager.init_app(app)

# PostgreSQL connection
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise Exception("DATABASE_URL environment variable not set")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Google OAuth setup
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_OAUTH_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET")
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

if GOOGLE_CLIENT_ID:
    client = WebApplicationClient(GOOGLE_CLIENT_ID)
    REPLIT_DEV_DOMAIN = os.environ.get("REPLIT_DEV_DOMAIN", "")
    if REPLIT_DEV_DOMAIN:
        DEV_REDIRECT_URL = f'https://{REPLIT_DEV_DOMAIN}/api/auth/google/callback'
        print(f"""To make Google authentication work:
1. Go to https://console.cloud.google.com/apis/credentials
2. Create a new OAuth 2.0 Client ID
3. Add {DEV_REDIRECT_URL} to Authorized redirect URIs
""")
else:
    client = None

# Models
class User(Base, UserMixin):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(256), unique=True, nullable=False)
    username = Column(String(256), nullable=False)
    password_hash = Column(String(256), nullable=True)
    google_id = Column(String(256), nullable=True, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    reports = relationship("Report", back_populates="user")


class Report(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(256), nullable=False)
    description = Column(Text)
    file_hash = Column(String(256), nullable=False)
    signature = Column(Text)
    block_index = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="reports")


class Block(Base):
    __tablename__ = "blocks"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    block_hash = Column(String(256), unique=True, nullable=False)
    previous_hash = Column(String(256))
    nonce = Column(String(256))
    data = Column(Text)
    block_metadata = Column(Text)
    merkle_root = Column(String(256))
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    transactions = relationship("Transaction", back_populates="block")


class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    block_id = Column(Integer, ForeignKey("blocks.id"))
    sender = Column(String(256))
    receiver = Column(String(256))
    amount = Column(String(100))
    tx_hash = Column(String(256))
    
    block = relationship("Block", back_populates="transactions")


# Create tables
Base.metadata.create_all(engine)

# Login manager loader
@login_manager.user_loader
def load_user(user_id):
    with SessionLocal() as db_session:
        return db_session.query(User).get(int(user_id))

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Auth Routes
@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.json
    email = data.get("email")
    username = data.get("username")
    password = data.get("password")
    
    if not all([email, username, password]):
        return jsonify({"error": "Email, username, and password are required"}), 400
    
    with SessionLocal() as db_session:
        existing = db_session.query(User).filter_by(email=email).first()
        if existing:
            return jsonify({"error": "Email already registered"}), 400
        
        user = User(
            email=email,
            username=username,
            password_hash=hash_password(password)
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        login_user(user)
        
        return jsonify({
            "message": "Registration successful",
            "user": {"id": user.id, "email": user.email, "username": user.username}
        }), 201


@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    
    if not all([email, password]):
        return jsonify({"error": "Email and password are required"}), 400
    
    with SessionLocal() as db_session:
        user = db_session.query(User).filter_by(email=email).first()
        if not user or user.password_hash != hash_password(password):
            return jsonify({"error": "Invalid credentials"}), 401
        
        login_user(user)
        return jsonify({
            "message": "Login successful",
            "user": {"id": user.id, "email": user.email, "username": user.username}
        })


@app.route("/api/auth/logout", methods=["POST"])
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully"})


@app.route("/api/auth/me", methods=["GET"])
def get_current_user():
    if current_user.is_authenticated:
        return jsonify({
            "authenticated": True,
            "user": {
                "id": current_user.id,
                "email": current_user.email,
                "username": current_user.username
            }
        })
    return jsonify({"authenticated": False})


# Google OAuth routes
@app.route("/api/auth/google")
def google_login():
    if not client:
        return jsonify({"error": "Google OAuth not configured"}), 500
    
    google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.url_root.replace("http://", "https://") + "api/auth/google/callback",
        scope=["openid", "email", "profile"],
    )
    return jsonify({"auth_url": request_uri})


@app.route("/api/auth/google/callback")
def google_callback():
    if not client:
        return redirect("/?error=oauth_not_configured")
    
    code = request.args.get("code")
    google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    token_endpoint = google_provider_cfg["token_endpoint"]
    
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url.replace("http://", "https://"),
        redirect_url=request.base_url.replace("http://", "https://"),
        code=code,
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )
    
    client.parse_request_body_response(json.dumps(token_response.json()))
    
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    
    userinfo = userinfo_response.json()
    if not userinfo.get("email_verified"):
        return redirect("/?error=email_not_verified")
    
    users_email = userinfo["email"]
    users_name = userinfo.get("given_name", userinfo.get("name", "User"))
    google_id = userinfo["sub"]
    
    with SessionLocal() as db_session:
        user = db_session.query(User).filter_by(google_id=google_id).first()
        if not user:
            user = db_session.query(User).filter_by(email=users_email).first()
            if user:
                user.google_id = google_id
                db_session.commit()
            else:
                user = User(username=users_name, email=users_email, google_id=google_id)
                db_session.add(user)
                db_session.commit()
        
        db_session.refresh(user)
        login_user(user)
    
    return redirect("/")


# Report Routes
@app.route("/api/report", methods=["POST"])
def create_report():
    title = request.form.get("title")
    description = request.form.get("description", "")
    file = request.files.get("file")
    
    if not title or not file:
        return jsonify({"error": "Title and file are required"}), 400
    
    file_bytes = file.read()
    file_hash = sha256_bytes(file_bytes)
    
    private_key_path = os.path.join(os.path.dirname(__file__), "keys", "issuer_priv.pem")
    signature = sign_hex(private_key_path, file_hash)
    
    with SessionLocal() as db_session:
        blocks = db_session.query(Block).all()
        block_index = len(blocks) + 1
        
        previous_hash = blocks[-1].block_hash if blocks else "0" * 64
        
        block_data = json.dumps({
            "title": title,
            "description": description,
            "file_hash": file_hash,
            "signature": signature,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        block_hash = hashlib.sha256(f"{previous_hash}{block_data}".encode()).hexdigest()
        
        new_block = Block(
            block_hash=block_hash,
            previous_hash=previous_hash,
            data=block_data,
            merkle_root=file_hash
        )
        db_session.add(new_block)
        db_session.commit()
        db_session.refresh(new_block)
        
        user_id = current_user.id if current_user.is_authenticated else None
        report = Report(
            user_id=user_id,
            title=title,
            description=description,
            file_hash=file_hash,
            signature=signature,
            block_index=new_block.id
        )
        db_session.add(report)
        db_session.commit()
        db_session.refresh(report)
        
        return jsonify({
            "message": "Report created and added to blockchain",
            "report_id": report.id,
            "block_index": new_block.id,
            "hash": file_hash,
            "signature": signature
        }), 201


@app.route("/api/search", methods=["GET"])
def search_reports():
    query = request.args.get("q", "")
    
    with SessionLocal() as db_session:
        reports = db_session.query(Report).filter(
            Report.title.ilike(f"%{query}%") | Report.description.ilike(f"%{query}%")
        ).all()
        
        return jsonify([{
            "id": r.id,
            "title": r.title,
            "description": r.description,
            "file_hash": r.file_hash,
            "block_index": r.block_index,
            "created_at": r.created_at.isoformat() if r.created_at else None
        } for r in reports])


@app.route("/api/report/<int:report_id>/certificate", methods=["GET"])
def download_certificate(report_id):
    with SessionLocal() as db_session:
        report = db_session.query(Report).get(report_id)
        if not report:
            return jsonify({"error": "Report not found"}), 404
        
        os.makedirs("certificates", exist_ok=True)
        cert_path = f"certificates/report_{report_id}_certificate.pdf"
        
        pdf = FPDF(orientation="L", unit="mm", format="A4")
        pdf.add_page()
        pdf.set_fill_color(245, 245, 245)
        pdf.rect(0, 0, 297, 210, style="F")
        pdf.set_line_width(2)
        pdf.rect(5, 5, 287, 200)
        
        pdf.set_font("Helvetica", "B", 28)
        pdf.set_xy(0, 30)
        pdf.cell(0, 10, "BLOCKCHAIN VERIFICATION CERTIFICATE", align="C")
        
        pdf.set_font("Helvetica", size=16)
        pdf.set_xy(0, 60)
        pdf.cell(0, 10, f"Report: {report.title}", align="C")
        
        pdf.set_xy(0, 80)
        pdf.cell(0, 10, f"Block Index: {report.block_index}", align="C")
        
        pdf.set_font("Helvetica", size=12)
        pdf.set_xy(20, 100)
        pdf.multi_cell(257, 8, f"Hash: {report.file_hash}")
        
        pdf.set_xy(0, 130)
        pdf.cell(0, 10, f"Created: {report.created_at.strftime('%Y-%m-%d %H:%M:%S') if report.created_at else 'N/A'}", align="C")
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(f"Hash: {report.file_hash}\nBlock: {report.block_index}")
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_path = f"certificates/qr_{report_id}.png"
        qr_img.save(qr_path)
        pdf.image(qr_path, x=230, y=140, w=50)
        
        pdf.output(cert_path)
        
        return send_file(cert_path, as_attachment=True, download_name=f"certificate_{report_id}.pdf")


# Blockchain Explorer Routes
@app.route("/api/explorer", methods=["GET"])
def explorer():
    with SessionLocal() as db_session:
        blocks = db_session.query(Block).order_by(Block.id.desc()).all()
        return jsonify([{
            "id": b.id,
            "block_hash": b.block_hash,
            "previous_hash": b.previous_hash,
            "merkle_root": b.merkle_root,
            "timestamp": b.timestamp.isoformat() if b.timestamp else None,
            "transaction_count": len(b.transactions)
        } for b in blocks])


@app.route("/api/block/<int:idx>", methods=["GET"])
def get_block(idx):
    with SessionLocal() as db_session:
        block = db_session.query(Block).get(idx)
        if not block:
            return jsonify({"error": "Block not found"}), 404
        
        return jsonify({
            "id": block.id,
            "block_hash": block.block_hash,
            "previous_hash": block.previous_hash,
            "merkle_root": block.merkle_root,
            "data": block.data,
            "metadata": block.block_metadata,
            "timestamp": block.timestamp.isoformat() if block.timestamp else None,
            "transactions": [{
                "id": tx.id,
                "sender": tx.sender,
                "receiver": tx.receiver,
                "amount": tx.amount,
                "tx_hash": tx.tx_hash
            } for tx in block.transactions]
        })


@app.route("/api/block/<int:idx>/qr", methods=["GET"])
def get_block_qr(idx):
    with SessionLocal() as db_session:
        block = db_session.query(Block).get(idx)
        if not block:
            return jsonify({"error": "Block not found"}), 404
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(f"Block #{block.id}\nHash: {block.block_hash}")
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = BytesIO()
        qr_img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return jsonify({
            "qr_base64": base64.b64encode(buffer.getvalue()).decode()
        })


@app.route("/api/block/<int:idx>/merkle", methods=["GET"])
def get_merkle_proof(idx):
    with SessionLocal() as db_session:
        block = db_session.query(Block).get(idx)
        if not block:
            return jsonify({"error": "Block not found"}), 404
        
        return jsonify({
            "block_id": block.id,
            "merkle_root": block.merkle_root,
            "block_hash": block.block_hash
        })


# Verify Route
@app.route("/api/verify", methods=["POST"])
def verify_file():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "File is required"}), 400
    
    file_bytes = file.read()
    file_hash = sha256_bytes(file_bytes)
    
    with SessionLocal() as db_session:
        report = db_session.query(Report).filter_by(file_hash=file_hash).first()
        
        if report:
            block = db_session.query(Block).get(report.block_index) if report.block_index else None
            return jsonify({
                "verified": True,
                "message": "File is verified and exists on the blockchain",
                "report": {
                    "id": report.id,
                    "title": report.title,
                    "block_index": report.block_index,
                    "created_at": report.created_at.isoformat() if report.created_at else None
                },
                "block": {
                    "hash": block.block_hash if block else None,
                    "timestamp": block.timestamp.isoformat() if block and block.timestamp else None
                }
            })
        
        return jsonify({
            "verified": False,
            "message": "File not found in blockchain",
            "hash": file_hash
        })


# Chain Operations
@app.route("/api/chain/timeline", methods=["GET"])
def get_timeline():
    with SessionLocal() as db_session:
        blocks = db_session.query(Block).order_by(Block.timestamp.desc()).limit(20).all()
        return jsonify([{
            "id": b.id,
            "block_hash": b.block_hash[:16] + "...",
            "timestamp": b.timestamp.isoformat() if b.timestamp else None,
            "data_preview": b.data[:100] + "..." if b.data and len(b.data) > 100 else b.data
        } for b in blocks])


@app.route("/api/chain/verify", methods=["GET"])
def verify_chain():
    with SessionLocal() as db_session:
        blocks = db_session.query(Block).order_by(Block.id).all()
        
        if not blocks:
            return jsonify({"valid": True, "message": "Chain is empty"})
        
        for i in range(1, len(blocks)):
            if blocks[i].previous_hash != blocks[i-1].block_hash:
                return jsonify({
                    "valid": False,
                    "message": f"Chain broken at block {blocks[i].id}",
                    "block_index": blocks[i].id
                })
        
        return jsonify({
            "valid": True,
            "message": "Blockchain integrity verified",
            "total_blocks": len(blocks)
        })


# Health check
@app.route("/", methods=["GET"])
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "Backend running"})


@app.route("/api/db-test", methods=["GET"])
def db_test():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return jsonify({"status": "Database Connected"})
    except Exception as e:
        return jsonify({"status": "Database Error", "message": str(e)})


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    app.run(host="localhost", port=port, debug=True)
