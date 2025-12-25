#!/usr/bin/env python3
import socket, json, time, os
from pathlib import Path
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

SOCK = "/tmp/sanctum.scribe.sock"
os.makedirs("artifacts", exist_ok=True)
Path("artifacts/lineage.jsonl").touch()

password = os.getenv("SANCTUM_PASSPHRASE", "sunflower").encode()

with open("keys/scribe_private.pem", "rb") as f:
    try:
        private_key = serialization.load_pem_private_key(f.read(), password=password)
    except Exception:
        private_key = None

public_keys = {}
for agent in ["auditor", "conductor"]:
    with open(f"keys/{agent}_public.pem", "rb") as f:
        public_keys[agent] = serialization.load_pem_public_key(f.read())

def verify_sig(pub, msg, sig_hex):
    try:
        pub.verify(bytes.fromhex(sig_hex), msg.encode(), padding.PKCS1v15(), hashes.SHA512())
        return True
    except Exception:
        return False

if os.path.exists(SOCK):
    try:
        os.unlink(SOCK)
    except Exception:
        pass
sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
sock.bind(SOCK)
os.chmod(SOCK, 0o777)

print(f"📜 Scribe listening on {SOCK}")

with open("artifacts/lineage.jsonl", "a") as f:
    f.write(json.dumps({"event": "scribe_started", "ts": time.time()}) + "\n")

while True:
    data, addr = sock.recvfrom(4096)
    msg = json.loads(data.decode())
    sender = msg.get("sender")
    
    if sender in public_keys:
        if not verify_sig(public_keys[sender], msg.get("message", ""), msg.get("signature", "")):
            print(f"❌ REJECTED from {sender}")
            continue
        else:
            print(f"✅ Verified from {sender}")
    
    if "create_artifact" in msg:
        artifact_path = msg["create_artifact"]
        os.makedirs(os.path.dirname(artifact_path), exist_ok=True)
        with open(artifact_path, "w") as f:
            f.write(msg.get("message", ""))
        print(f"📝 Created: {artifact_path}")
    
    with open("artifacts/lineage.jsonl", "a") as f:
        f.write(json.dumps({"from": sender, "data": msg, "ts": time.time()}) + "\n")
