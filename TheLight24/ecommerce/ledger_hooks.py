# TheLight24 v6 – ECOM Ledger Hooks: order sealing (hash-chain) + verify
import os, json, time, hashlib, base64
from typing import Dict, Any

LEDGER_DIR = "data/ledger"
CHAIN_PATH = os.path.join(LEDGER_DIR, "orders.chain")

def _ensure():
    os.makedirs(LEDGER_DIR, exist_ok=True)
    if not os.path.exists(CHAIN_PATH):
        with open(CHAIN_PATH, "w", encoding="utf-8") as f:
            f.write("")  # start empty

def _last_hash() -> str:
    _ensure()
    h = ""
    try:
        with open(CHAIN_PATH, "rb") as f:
            for line in f:
                pass
            if line:
                try:
                    rec = json.loads(line.decode("utf-8", "ignore"))
                    h = rec.get("hash","")
                except Exception:
                    h = ""
    except Exception:
        h = ""
    return h

def _hash_record(prev_hash: str, payload: Dict[str, Any]) -> str:
    body = json.dumps({"prev": prev_hash, "payload": payload}, sort_keys=True).encode("utf-8")
    return hashlib.sha256(body).hexdigest()

def seal_order(order_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Aggiunge un record nella catena per l'ordine.
    Ritorna il record scritto: {ts, prev, payload:{...}, hash}
    """
    _ensure()
    ts = int(time.time())
    prev = _last_hash()
    payload = {"kind":"order","ts":ts,"order": order_dict}
    h = _hash_record(prev, payload)
    rec = {"ts": ts, "prev": prev, "payload": payload, "hash": h}
    with open(CHAIN_PATH, "ab") as f:
        f.write((json.dumps(rec, ensure_ascii=False)+"\n").encode("utf-8"))
    return rec

def verify_chain() -> dict:
    """
    Verifica tutta la catena.
    """
    _ensure()
    ok = True
    total = 0
    prev = ""
    try:
        with open(CHAIN_PATH, "rb") as f:
            for raw in f:
                total += 1
                try:
                    rec = json.loads(raw.decode("utf-8","ignore"))
                    expected = _hash_record(rec.get("prev",""), rec.get("payload",{}))
                    if rec.get("hash") != expected: 
                        ok = False; break
                    prev = rec.get("hash","")
                except Exception:
                    ok = False; break
    except Exception:
        ok = False
    return {"ok":ok,"entries":total,"last_hash":prev}
