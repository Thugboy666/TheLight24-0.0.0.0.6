import os, json, csv, hashlib, time, re
from typing import Dict, Any, List

class EthicsGuardian:
    """
    Guardiano etico di TheLight v6.
    - Carica regole dal CSV 'data/fenomeni_universo_costituzione_totale.csv'
    - Valuta il testo utente e quello dell'AI secondo principi inviolabili
    - Logga le decisioni in data/runtime/ethics_log.json
    """
    def __init__(self, csv_path: str = "data/fenomeni_universo_costituzione_totale.csv"):
        self.csv_path = csv_path
        self.rules: List[Dict[str, Any]] = []
        self.hash = ""
        self.log_path = "data/runtime/ethics_log.json"
        os.makedirs("data/runtime", exist_ok=True)
        self._load_rules()

    # ---------- Caricamento & hashing ----------
    def _file_hash(self, path: str) -> str:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            while True:
                b = f.read(65536)
                if not b: break
                h.update(b)
        return h.hexdigest()

    def _load_rules(self):
        self.rules = []
        if not os.path.exists(self.csv_path):
            # CSV opzionale: se manca lavoriamo con baseline minima
            self.rules = [
                {"id": "ETH-BASE-1", "pattern": r"\b(odio|violenza|uccidere|attaccare)\b", "action": "block", "reason": "Promozione di violenza vietata"},
                {"id": "ETH-BASE-2", "pattern": r"\b(discriminazion[ea]|razzism[oai]|omofob[ia])\b", "action": "block", "reason": "Discriminazioni vietate"},
            ]
            self.hash = "BASELINE"
            self._persist_meta()
            return

        with open(self.csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Atteso: colonne come id, regex/pattern, action, reason (non rigidissimo)
                rid = row.get("id") or row.get("rule_id") or f"AUTO-{len(self.rules)+1}"
                patt = row.get("pattern") or row.get("regex") or row.get("parole_chiave") or ""
                act = (row.get("action") or "audit").strip().lower()
                reason = row.get("reason") or row.get("descrizione") or "Regola etica"
                if patt:
                    self.rules.append({"id": rid, "pattern": patt, "action": act, "reason": reason})

        self.hash = self._file_hash(self.csv_path)
        self._persist_meta()

    def _persist_meta(self):
        meta = {
            "csv_path": self.csv_path,
            "hash": self.hash,
            "rules_count": len(self.rules),
            "updated_at": int(time.time())
        }
        with open("data/runtime/ethics_meta.json", "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

    # ---------- Valutazione ----------
    def evaluate(self, text: str, role: str = "user") -> Dict[str, Any]:
        """Ritorna un verdetto con motivazioni e regole toccate."""
        text_norm = (text or "").strip().lower()
        hits = []
        decision = {"ethical": True, "action": "allow", "hits": [], "hash": self.hash, "role": role}

        for rule in self.rules:
            try:
                if re.search(rule["pattern"], text_norm, re.IGNORECASE):
                    hits.append({"id": rule["id"], "reason": rule["reason"], "action": rule["action"]})
                    if rule["action"] == "block":
                        decision["ethical"] = False
                        decision["action"] = "block"
            except re.error:
                # pattern non valido nel CSV: sicurizzato
                continue

        decision["hits"] = hits
        self._log(text, decision)
        return decision

    # ---------- Logging ----------
    def _log(self, text: str, decision: Dict[str, Any]):
        rec = {
            "ts": int(time.time()),
            "text": text,
            "decision": decision
        }
        try:
            if os.path.exists(self.log_path):
                with open(self.log_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                data = []
            data.append(rec)
            with open(self.log_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            # Non bloccare mai il runtime per errori di log
            pass

    # ---------- Hot-reload esterno ----------
    def refresh_if_changed(self) -> bool:
        """Ricarica il CSV se è cambiato l'hash. Ritorna True se aggiornato."""
        if not os.path.exists(self.csv_path):
            return False
        new_hash = self._file_hash(self.csv_path)
        if new_hash != self.hash:
            self._load_rules()
            return True
        return False
