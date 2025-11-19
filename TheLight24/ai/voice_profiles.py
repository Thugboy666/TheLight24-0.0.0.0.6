import os, json, shutil

DB_DIR = "data/profiles"
DB_FILE = os.path.join(DB_DIR, "profiles.json")

def _ensure():
    os.makedirs(DB_DIR, exist_ok=True)
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump({"profiles": []}, f, ensure_ascii=False, indent=2)

def _load():
    _ensure()
    with open(DB_FILE, encoding="utf-8") as f:
        return json.load(f)

def _save(db):
    tmp = DB_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    os.replace(tmp, DB_FILE)

def list_profiles():
    db = _load()
    return db.get("profiles", [])

def get_profile(name: str):
    for p in list_profiles():
        if p.get("name") == name:
            return p
    return None

def add_profile(name: str, wav_path: str, consent: bool = True):
    os.makedirs(DB_DIR, exist_ok=True)
    # conserva una copia dentro la cartella profili
    safe_name = "".join(c for c in name if c.isalnum() or c in ("-", "_"))
    dst = os.path.join(DB_DIR, f"{safe_name}.wav")
    if os.path.abspath(wav_path) != os.path.abspath(dst):
        shutil.copy2(wav_path, dst)

    db = _load()
    # rimuovi se esiste già
    db["profiles"] = [p for p in db.get("profiles", []) if p.get("name") != name]
    db["profiles"].append({"name": name, "wav_path": dst, "consent": bool(consent)})
    _save(db)
    # aggiorna attivo
    with open(os.path.join(DB_DIR, "active.txt"), "w", encoding="utf-8") as f:
        f.write(name)
    return dst

def remove_profile(name: str):
    db = _load()
    prof = get_profile(name)
    db["profiles"] = [p for p in db.get("profiles", []) if p.get("name") != name]
    _save(db)
    if prof and os.path.exists(prof["wav_path"]):
        try:
            os.remove(prof["wav_path"])
        except Exception:
            pass
    active = os.path.join(DB_DIR, "active.txt")
    if os.path.exists(active):
        with open(active, encoding="utf-8") as f:
            cur = f.read().strip()
        if cur == name:
            os.remove(active)
