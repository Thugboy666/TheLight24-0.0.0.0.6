import threading, time, json, os
import requests

class Scheduler:
    """
    - Tick AI periodico
    - Salvataggio snapshot simulazione (via API) su file per GUI3D
    """
    def __init__(self, core):
        self.core = core
        self.th = None
        self._stop = False

    def _loop(self):
        while not self._stop:
            # salva snapshot ogni 0.5s (se sim attiva)
            try:
                snap = requests.get("http://127.0.0.1:8000/sim/snapshot?n=5000", timeout=0.2).json()
                os.makedirs("data/runtime",exist_ok=True)
                with open("data/runtime/last_snapshot.json","w",encoding="utf-8") as f:
                    json.dump(snap,f)
            except Exception:
                pass
            time.sleep(0.5)

    def start(self):
        if self.th: return
        self.th = threading.Thread(target=self._loop, daemon=True)
        self.th.start()

    def stop(self):
        self._stop=True
        if self.th: self.th.join(timeout=1.0)
