# generate_key.py
from Crypto.PublicKey import RSA

key = RSA.generate(2048)
with open('issuer_priv.pem','wb') as f:
    f.write(key.export_key())
with open('issuer_pub.pem','wb') as f:
    f.write(key.publickey().export_key())
print("Issuer keys generated: issuer_priv.pem and issuer_pub.pem")
