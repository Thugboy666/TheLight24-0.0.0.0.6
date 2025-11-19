# TheLight24 v6 – Loader fenomeni dal CSV "fenomeni_universo_costituzione_totale.csv"
import os, csv, json

CSV_DEFAULT = "data/knowledge/fenomeni_universo_costituzione_totale.csv"
OUT_JSON    = "data/runtime/phenomena_index.json"

class PhenomenaIndex:
    def __init__(self, csv_path=CSV_DEFAULT):
        self.csv_path = csv_path
        self.index = []

    def build(self):
        if not os.path.exists(self.csv_path):
            print(f"[PhenomenaIndex] CSV non trovato: {self.csv_path}")
            self.index = []
            return
        with open(self.csv_path, encoding="utf-8") as f:
            r = csv.DictReader(f)
            for row in r:
                # normalizza alcune chiavi comuni se presenti
                item = {
                    "id": row.get("id") or row.get("ID") or "",
                    "name": row.get("name") or row.get("nome") or "",
                    "domain": row.get("domain") or row.get("dominio") or "",
                    "rule": row.get("rule") or row.get("regola") or "",
                    "ethic": row.get("ethic") or row.get("etica") or "",
                    "notes": row.get("notes") or row.get("note") or ""
                }
                self.index.append(item)
        os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
        with open(OUT_JSON, "w", encoding="utf-8") as f:
            json.dump(self.index, f, indent=2)
        print(f"[PhenomenaIndex] Indicizzato: {len(self.index)} fenomeni → {OUT_JSON}")
