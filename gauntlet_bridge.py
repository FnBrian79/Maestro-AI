
# gauntlet_bridge.py
import socket
import json
import time
import os
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

SCRIBE_SOCK = "/tmp/sanctum.scribe.sock"

# Load the Gauntlet's private key (bootstrapped earlier)
def load_key():
    passphrase_env = os.getenv("SANCTUM_PASSPHRASE")
    passphrase = passphrase_env.encode() if passphrase_env else None
    
    with open("keys/conductor_private.pem", "rb") as f: # Using conductor key for now as 'system' actor
        return serialization.load_pem_private_key(f.read(), password=passphrase)

def sign_payload(data, key):
    return key.sign(
        data.encode(),
        padding.PKCS1v15(),
        hashes.SHA512()
    ).hex()

def submit_run(run_data):
    """Submits a Playwright run to the Sanctum"""
    try:
        key = load_key()
    except Exception as e:
        print(f"❌ Failed to load key: {e}")
        return

    data_str = json.dumps(run_data)
    signature = sign_payload(data_str, key)
    
    payload = json.dumps({
        "message": data_str,
        "signature": signature,
        "sender": "gauntlet", # Recognized sender
        "create_artifact": f"artifacts/gauntlet/run_{int(time.time())}.json"
    }).encode()
    
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    try:
        sock.connect(SCRIBE_SOCK)
        sock.send(payload)
        print(f"✅ Gauntlet Run submitted to Sanctum: {len(payload)} bytes")
    except FileNotFoundError:
        print("❌ Sanctum Scribe not running.")
    except Exception as e:
        print(f"❌ Error submitting to Scribe: {e}")
    finally:
        sock.close()

# Example usage (mocking Playwright output)
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--payload", help="Payload to send")
    parser.add_argument("--type", help="Type of payload")
    args = parser.parse_args()
    
    if args.payload:
        # If payload is provided via CLI, use it (from blind_compiler)
        mock_browser_data = {
            "synthesis": args.payload,
            "type": args.type or "compiled_report",
            "timestamp": int(time.time())
        }
    else:
        mock_browser_data = {
            "url": "https://example.com",
            "title": "Example Domain",
            "screenshot_hash": "a1b2c3d4",
            "status": "success"
        }
    submit_run(mock_browser_data)
