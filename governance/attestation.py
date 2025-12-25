import hashlib, json, time
from dataclasses import dataclass

@dataclass
class Signature:
    key_id: str
    digest: str
    ts: str

def sign_payload(payload: dict, key_id: str = "conductor:v1") -> Signature:
    canon = json.dumps(payload, sort_keys=True).encode()
    digest = hashlib.sha256(canon).hexdigest()
    return Signature(key_id=key_id, digest=digest, ts=time.strftime("%Y-%m-%dT%H:%M:%SZ"))

def attach_signature(payload: dict, sig: Signature) -> dict:
    return {**payload, "Signature": f"{sig.key_id}:{sig.digest}", "Timestamp": sig.ts}
