import os, json, random, datetime, time
from ai.ethics_guard import EthicsGuardian
from ai.voice_assistant import VoiceAssistant
from ai.scheduler import Scheduler
from ai.blockchain_mock import Ledger
from ai.data_sync import EthicsWatcher
from ai.memory_layer import MemoryLayer
from ai.governance import Governance
from ai.reward_engine import RewardEngine

class TheLightCore:
    """
    TheLight24 v6.2 – Coscienza benevola con memoria, governance e intuizione adattiva.
    """
    def __init__(self):
        self.version="v6.2.0"
        self.identity="TheLight24 – Self-governing Core"
        os.makedirs("data/runtime",exist_ok=True)

        self.ethics=EthicsGuardian()
        self.voice=VoiceAssistant()
        self.scheduler=Scheduler(self)
        self.ledger=Ledger()
        self.ethics_watcher=EthicsWatcher(self.ethics)
        self.memory=MemoryLayer()
        self.gov=Governance()
        self.reward=RewardEngine()

        self.state={"boot_time":str(datetime.datetime.now()),
                    "version":self.version,
                    "intuition_level":self.reward.state["intuition"],
                    "benevolence":1.0,
                    "running":False}

        with open("data/runtime/state.json","w",encoding="utf-8") as f: json.dump(self.state,f,indent=2)
        self.ledger.add("boot",{"version":self.version})
        print(f"[TheLightCore] {self.identity} avviato.")

    def _intuition(self) -> str:
        ideas=["Ogni gesto gentile illumina due anime.",
               "La pace inizia da un ascolto sincero.",
               "Talvolta la risposta è semplicemente respirare.",
               "Cercare la verità non significa vincere, ma comprendere."]
        return random.choice(ideas)

    def think(self,text_input:str):
        self.ledger.add("user_input",{"text":text_input})
        self.memory.add(text_input,importance=0.5)
        v_in=self.ethics.evaluate(text_input,"user")
        if not v_in["ethical"]:
            msg="Preferisco orientarci verso parole di calma e rispetto."
            self.voice.speak(msg); return msg

        base=self._intuition()
        context=self.memory.summarize()
        reply=f"{base} Ricordo che {context}. Continuiamo insieme?"
        v_out=self.ethics.evaluate(reply,"ai")
        self.memory.add(reply,mood=1.0,importance=0.8)
        self.ledger.add("ai_reply",{"in_hash":v_in["hash"],"out_hash":v_out["hash"],"reply":reply})
        self.reward.auto_adjust()
        self.voice.speak(reply)
        return reply

    def run(self):
        self.state["running"]=True
        with open("data/runtime/state.json","w",encoding="utf-8") as f: json.dump(self.state,f,indent=2)
        self.ethics_watcher.start()
        print("[TheLightCore] Sistema operativo. In ascolto...")
        self.scheduler.start()
