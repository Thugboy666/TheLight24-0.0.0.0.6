import os, json, hashlib, time
from ai.blockchain_mock import Ledger

class Governance:
    """
    Layer politico-economico locale:
      - votazioni su decisioni AI
      - reputazione utenti
      - ledger per audit
    """
    def __init__(self, path="data/runtime/governance.json"):
        self.path=path
        os.makedirs(os.path.dirname(self.path),exist_ok=True)
        self.ledger=Ledger()
        if not os.path.exists(path):
            with open(path,"w",encoding="utf-8") as f: json.dump({"votes":{}, "reputation":{}},f,indent=2)
        self.data=self._load()

    def _load(self):
        with open(self.path,encoding="utf-8") as f: return json.load(f)
    def _save(self): 
        with open(self.path,"w",encoding="utf-8") as f: json.dump(self.data,f,indent=2)

    def vote(self, user:str, proposal:str, choice:str):
        h=hashlib.sha1((user+proposal+str(time.time())).encode()).hexdigest()
        self.data["votes"][h]={"user":user,"proposal":proposal,"choice":choice,"ts":int(time.time())}
        self._save()
        self.ledger.add("vote",{"user":user,"proposal":proposal,"choice":choice})
        return h

    def reputation(self,user:str,delta:float):
        r=self.data["reputation"].get(user,0.0)
        r+=delta
        self.data["reputation"][user]=max(min(r,1.0),-1.0)
        self._save()
        self.ledger.add("reputation",{"user":user,"value":r})
        return r

    def summary(self):
        return {"votes":len(self.data["votes"]), "users":len(self.data["reputation"])}
