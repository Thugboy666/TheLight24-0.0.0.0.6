# TheLight24 v6 – ECOM Security (Fernet at-rest encryption + HMAC utility)
import os, base64, hashlib, hmac, json
from cryptography.fernet import Fernet

KEY_DIR = "data/keys"
KEY_PATH = os.path.join(KEY_DIR, "commerce.key")

def _ensure_key():
    os.makedirs(KEY_DIR, exist_ok=True)
    if not os.path.exists(KEY_PATH):
        key = Fernet.generate_key()
        with open(KEY_PATH, "wb") as f:
            f.write(key)
        try:
            os.chmod(KEY_PATH, 0o600)
        except Exception:
            pass
    with open(KEY_PATH, "rb") as f:
        key = f.read()
    return Fernet(key)

FERNET = _ensure_key()

def encrypt_json(obj: dict) -> bytes:
    data = json.dumps(obj).encode("utf-8")
    return FERNET.encrypt(data)

def decrypt_json(blob: bytes) -> dict:
    data = FERNET.decrypt(blob)
    return json.loads(data.decode("utf-8"))

def hmac_sha256(secret: bytes, payload: bytes) -> str:
    return hmac.new(secret, payload, hashlib.sha256).hexdigest()

def file_write_encrypted(path: str, obj: dict):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    blob = encrypt_json(obj)
    with open(path, "wb") as f:
        f.write(blob)

def file_read_encrypted(path: str, default: dict):
    if not os.path.exists(path):
        return default
    with open(path, "rb") as f:
        blob = f.read()
    return decrypt_json(blob)
