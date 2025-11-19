import os, json, hashlib, time
from typing import Dict, Any, Optional

class Ledger:
    """
    Blockchain locale "mock" (append-only con hash chaining).
    File: data/ledger/chain.jsonl
    """
    def __init__(self, path: str = "data/ledger/chain.jsonl"):
        self.path = path
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        if not os.path.exists(self.path):
            self._genesis()

    def _genesis(self):
        genesis = {
            "index": 0,
            "ts": int(time.time()),
            "type": "genesis",
            "payload": {"msg": "TheLight24 v6 ledger genesis"},
            "prev_hash": "0"*64,
        }
        genesis["hash"] = self._hash(genesis)
        with open(self.path, "w", encoding="utf-8") as f:
            f.write(json.dumps(genesis)+"\n")

    def _hash(self, block: Dict[str, Any]) -> str:
        b = block.copy()
        b.pop("hash", None)
        s = json.dumps(b, sort_keys=True).encode("utf-8")
        return hashlib.sha256(s).hexdigest()

    def _last(self) -> Dict[str, Any]:
        last = None
        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    last = json.loads(line)
        return last

    def add(self, btype: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        last = self._last()
        block = {
            "index": (last["index"] + 1) if last else 1,
            "ts": int(time.time()),
            "type": btype,
            "payload": payload,
            "prev_hash": last["hash"] if last else "0"*64,
        }
        block["hash"] = self._hash(block)
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(block)+"\n")
        return block

    def verify(self) -> bool:
        prev_hash = "0"*64
        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip(): continue
                b = json.loads(line)
                if b["prev_hash"] != prev_hash: return False
                if self._hash(b) != b["hash"]: return False
                prev_hash = b["hash"]
        return True
