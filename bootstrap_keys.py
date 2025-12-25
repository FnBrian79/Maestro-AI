#!/usr/bin/env python3
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import os

os.makedirs("keys", exist_ok=True)
password = os.getenv("SANCTUM_PASSPHRASE", "sunflower").encode()

for name in ["scribe", "auditor", "conductor"]:
    private = rsa.generate_private_key(public_exponent=65537, key_size=4096)
    public = private.public_key()
    
    pem_priv = private.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(password)
    )
    pem_pub = public.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    with open(f"keys/{name}_private.pem", "wb") as f:
        f.write(pem_priv)
    with open(f"keys/{name}_public.pem", "wb") as f:
        f.write(pem_pub)
    print(f"✓ {name}")

print("\n✅ Keys bootstrapped with passphrase")
