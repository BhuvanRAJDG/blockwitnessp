import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Text, text
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy.exc import SQLAlchemyError

# -------------------------------------------------------------------
# 1️⃣ POSTGRES CONNECTION (Render)
# -------------------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL")

# Fix SSL for Render PostgreSQL
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")

engine = create_engine(DATABASE_URL, connect_args={"sslmode": "require"})
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

# -------------------------------------------------------------------
# 2️⃣ ORM MODELS (metadata renamed → block_metadata)
# -------------------------------------------------------------------
class Block(Base):
    __tablename__ = "blocks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    block_hash = Column(String(256), unique=True)
    previous_hash = Column(String(256))
    nonce = Column(String(256))
    data = Column(Text)
    block_metadata = Column(Text)   # FIXED: renamed from "metadata"

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

# -------------------------------------------------------------------
# 3️⃣ Create database tables (Auto)
# -------------------------------------------------------------------
Base.metadata.create_all(engine)

# -------------------------------------------------------------------
# 4️⃣ Flask App
# -------------------------------------------------------------------
app = Flask(__name__)
CORS(app)

# -------------------------------------------------------------------
# 5️⃣ API ROUTES
# -------------------------------------------------------------------

# Test endpoint
@app.route("/", methods=["GET"])
def home():
    return {"status": "Backend running with PostgreSQL 🎉"}



@app.route("/db-test", methods=["GET"])
def db_test():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "Database Connected 🎉"}
    except Exception as e:
        return {"status": "Database Error", "message": str(e)}


# Add block
@app.route("/add_block", methods=["POST"])
def add_block():
    try:
        data = request.json

        new_block = Block(
            block_hash=data["block_hash"],
            previous_hash=data["previous_hash"],
            nonce=data.get("nonce"),
            data=data.get("data"),
            block_metadata=data.get("metadata")  # DB column is "block_metadata"
        )
        session.add(new_block)
        session.commit()

        return jsonify({"message": "Block added successfully"}), 201

    except SQLAlchemyError as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500


# Add transaction
@app.route("/add_transaction", methods=["POST"])
def add_transaction():
    try:
        data = request.json

        new_tx = Transaction(
            block_id=data["block_id"],
            sender=data["sender"],
            receiver=data["receiver"],
            amount=data["amount"],
            tx_hash=data["tx_hash"]
        )

        session.add(new_tx)
        session.commit()

        return jsonify({"message": "Transaction added successfully"}), 201

    except SQLAlchemyError as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500


# Get all blocks with transactions
@app.route("/get_blocks", methods=["GET"])
def get_blocks():
    blocks = session.query(Block).all()

    result = []
    for block in blocks:
        result.append({
            "id": block.id,
            "block_hash": block.block_hash,
            "previous_hash": block.previous_hash,
            "nonce": block.nonce,
            "data": block.data,
            "metadata": block.block_metadata,  # send original field name
            "transactions": [
                {
                    "id": tx.id,
                    "sender": tx.sender,
                    "receiver": tx.receiver,
                    "amount": tx.amount,
                    "tx_hash": tx.tx_hash
                }
                for tx in block.transactions
            ]
        })

    return jsonify(result)

# -------------------------------------------------------------------
# 6️⃣ Run app
# -------------------------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
