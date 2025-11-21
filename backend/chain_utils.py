# backend/chain_utils.py
import hashlib
import json

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()

def sha256_bytes(b: bytes):
    return hashlib.sha256(b).hexdigest()

def merkle_root(hex_hashes):
    # hex_hashes: list of hex strings
    if not hex_hashes:
        return ''
    cur = [bytes.fromhex(h) for h in hex_hashes]
    while len(cur) > 1:
        if len(cur) % 2 == 1:
            cur.append(cur[-1])
        nxt = []
        for i in range(0, len(cur), 2):
            nxt.append(hashlib.sha256(cur[i] + cur[i+1]).digest())
        cur = nxt
    return cur[0].hex()
