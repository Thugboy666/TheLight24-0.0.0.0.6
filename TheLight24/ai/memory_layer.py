import os, json, time, hashlib
from typing import Dict, Any, List

class MemoryLayer:
    """
    Memoria persistente e ponderata (ricorda emozioni, contesti e risultati).
    """
    def __init__(self, path="data/runtime/memory.json"):
        self.path = path
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        if not os.path.exists(self.path):
            with open(self.path,"w",encoding="utf-8") as f: json.dump([],f)
        self.mem = self._load()

    def _load(self) -> List[Dict[str,Any]]:
        try:
            with open(self.path,encoding="utf-8") as f: return json.load(f)
        except Exception: return []

    def _save(self):
        with open(self.path,"w",encoding="utf-8") as f: json.dump(self.mem,f,indent=2)

    def add(self, text:str, mood:float=0.5, importance:float=0.5, tags:List[str]=None):
        h=hashlib.sha1((text+str(time.time())).encode()).hexdigest()
        rec={"id":h,"text":text,"mood":mood,"importance":importance,
             "tags":tags or [],"ts":int(time.time())}
        self.mem.append(rec)
        self._save()
        return rec

    def recall(self, keyword:str) -> List[str]:
        out=[m["text"] for m in self.mem if keyword.lower() in m["text"].lower()]
        return out[-5:]

    def summarize(self) -> str:
        if not self.mem: return "(vuoto)"
        latest=[m["text"] for m in self.mem[-3:]]
        return " | ".join(latest)
