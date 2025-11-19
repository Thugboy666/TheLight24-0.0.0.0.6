import random, json, os, time

class RewardEngine:
    """
    Micro-RL offline: valuta risposte e aggiorna 'intuition_level' del core.
    """
    def __init__(self, path="data/runtime/reward_state.json"):
        self.path=path
        if not os.path.exists(path):
            with open(path,"w",encoding="utf-8") as f: json.dump({"intuition":0.7,"count":0},f)
        self.state=self._load()

    def _load(self):
        with open(self.path,encoding="utf-8") as f: return json.load(f)
    def _save(self):
        with open(self.path,"w",encoding="utf-8") as f: json.dump(self.state,f,indent=2)

    def feedback(self,good:bool):
        delta=0.01 if good else -0.02
        self.state["intuition"]=max(0.1,min(1.0,self.state["intuition"]+delta))
        self.state["count"]+=1
        self._save()
        return self.state["intuition"]

    def auto_adjust(self):
        # leggera fluttuazione casuale (simula apprendimento spontaneo)
        drift=random.uniform(-0.005,0.005)
        self.state["intuition"]=max(0.1,min(1.0,self.state["intuition"]+drift))
        self._save()
        return self.state["intuition"]
