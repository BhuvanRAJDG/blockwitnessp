# backend/crypto_utils.py
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

def sign_hex(priv_pem_path, hex_message):
    key = RSA.import_key(open(priv_pem_path,'rb').read())
    h = SHA256.new(bytes.fromhex(hex_message))
    signature = pkcs1_15.new(key).sign(h)
    return signature.hex()

def verify_hex(pub_pem_path, hex_message, signature_hex):
    key = RSA.import_key(open(pub_pem_path,'rb').read())
    h = SHA256.new(bytes.fromhex(hex_message))
    try:
        pkcs1_15.new(key).verify(h, bytes.fromhex(signature_hex))
        return True
    except (ValueError, TypeError):
        return False
