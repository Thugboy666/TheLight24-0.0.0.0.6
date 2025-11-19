import os, json, time
from threading import Lock

STATE_PATH = "data/runtime/speech_state.json"

class _Sync:
    def __init__(self, path=STATE_PATH):
        self.path = path
        d = os.path.dirname(self.path)
        if d and not os.path.exists(d):
            os.makedirs(d, exist_ok=True)
        self._lock = Lock()
        self._state = {"talking": False, "vu": 0.0, "ts": 0.0, "interrupted": False}
        self._write()

    def _write(self):
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self._state, f, ensure_ascii=False)
        os.replace(tmp, self.path)

    def set_talking(self, val: bool):
        with self._lock:
            self._state["talking"] = bool(val)
            self._state["ts"] = time.time()
            self._write()

    def set_vu(self, vu: float):
        with self._lock:
            self._state["vu"] = float(max(0.0, min(1.0, vu)))
            self._state["ts"] = time.time()
            self._write()

    def set_interrupted(self, val: bool):
        with self._lock:
            self._state["interrupted"] = bool(val)
            self._state["ts"] = time.time()
            self._write()

sync = _Sync()
