import os
import json
import time
import hashlib
from threading import Lock

LEDGER_PATH = "data/runtime/ledger.json"


class Ledger:
    """
    Ledger append-only con hash a catena.

    Perché esiste:
    - Ogni cosa che l'utente dice alla macchina viene salvata
    - Ogni risposta dell'AI viene salvata
    - Ogni decisione o azione interna viene salvata
    - Tutto in maniera immutabile (catena di hash)
    - Trasparenza: puoi dimostrare che TheLight non mente

    Ogni blocco contiene:
    {
        "ts": <epoch_seconds>,
        "role": "user" | "ai" | "system",
        "text": "contenuto conversazione o decisione",
        "meta": {
            ...informazioni aggiuntive...
            "mode": "supporto_emotivo"/"operativo"/...,
            "inference_device": "gpu-fp16" | "cpu-fallback",
            ...
        },
        "prev_hash": "hash del blocco precedente",
        "hash": "hash SHA256 del blocco"
    }
    """

    def __init__(self, path=LEDGER_PATH):
        self.path = path
        self._lock = Lock()

        # crea cartella se mancante
        d = os.path.dirname(path)
        if d and not os.path.exists(d):
            os.makedirs(d, exist_ok=True)

        # se ledger non esiste, crealo vuoto
        if not os.path.exists(self.path):
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=2)

    def _read_all(self):
        try:
            with open(self.path, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _write_all(self, chain):
        tmp_path = self.path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(chain, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, self.path)

    def _calc_hash(self, block_dict):
        """
        Calcola SHA256 del blocco senza il campo 'hash'.
        Questo rende l'entry verificabile e non alterabile.
        """
        clone = dict(block_dict)
        if "hash" in clone:
            del clone["hash"]
        raw = json.dumps(clone, sort_keys=True, ensure_ascii=False).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    def append(self, role, text, meta=None):
        """
        Aggiunge un nuovo blocco al ledger.
        - role: "user", "ai", "system"
        - text: contenuto testuale
        - meta: dict con info aggiuntive (es. device usato, modalità emotiva)

        Ritorna l'hash del blocco appena scritto.
        """
        if meta is None:
            meta = {}

        with self._lock:
            chain = self._read_all()
            prev_hash = chain[-1]["hash"] if chain else "GENESIS"

            block = {
                "ts": time.time(),
                "role": role,
                "text": text,
                "meta": meta,
                "prev_hash": prev_hash
            }
            block["hash"] = self._calc_hash(block)

            chain.append(block)
            self._write_all(chain)

            return block["hash"]

    def verify_chain(self):
        """
        Controlla l'integrità del ledger:
        - Ogni hash deve combaciare col contenuto del blocco
        - Ogni prev_hash deve puntare al blocco precedente

        True = catena consistente
        False = catena alterata
        """
        chain = self._read_all()
        prev = "GENESIS"
        for block in chain:
            expected_hash = self._calc_hash(block)
            if block["hash"] != expected_hash:
                return False
            if block["prev_hash"] != prev:
                return False
            prev = block["hash"]
        return True
