# backend/crypto_utils.py
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

def sign_hex(private_key_path: str, data_hex: str) -> str:
    """Sign a hex string with RSA private key and return hex signature"""
    with open(private_key_path, 'rb') as f:
        private_key = RSA.import_key(f.read())
    
    data_bytes = bytes.fromhex(data_hex) if isinstance(data_hex, str) else data_hex
    h = SHA256.new(data_bytes)
    signature = pkcs1_15.new(private_key).sign(h)
    return signature.hex()

def verify_hex(public_key_path: str, data_hex: str, signature_hex: str) -> bool:
    """Verify a hex signature with RSA public key"""
    with open(public_key_path, 'rb') as f:
        public_key = RSA.import_key(f.read())
    
    data_bytes = bytes.fromhex(data_hex) if isinstance(data_hex, str) else data_hex
    signature_bytes = bytes.fromhex(signature_hex)
    h = SHA256.new(data_bytes)
    
    try:
        pkcs1_15.new(public_key).verify(h, signature_bytes)
        return True
    except (ValueError, TypeError):
        return False
