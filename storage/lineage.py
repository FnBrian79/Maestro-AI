import json, os, time
from pathlib import Path

LINEAGE = Path("artifacts/lineage.jsonl")
ARTIFACTS = Path("artifacts")

def write_artifact(kind: str, data: dict) -> str:
    ts = int(time.time())
    path = ARTIFACTS / f"{kind}_{ts}.json"
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    with open(LINEAGE, "a") as f:
        f.write(json.dumps({"kind": kind, "path": str(path), "ts": ts}) + "\n")
    return str(path)
