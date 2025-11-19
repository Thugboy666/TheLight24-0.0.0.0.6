import threading, time
from ai.ethics_guard import EthicsGuardian

class EthicsWatcher:
    """
    Watcher del CSV etico: ricarica le regole quando il file cambia.
    Non blocca il main thread.
    """
    def __init__(self, guard: EthicsGuardian, interval: int = 10):
        self.guard = guard
        self.interval = interval
        self._active = False

    def _loop(self):
        while self._active:
            try:
                changed = self.guard.refresh_if_changed()
                if changed:
                    print("[EthicsWatcher] CSV etico aggiornato e ricaricato.")
            except Exception as e:
                print("[EthicsWatcher] Warning:", e)
            time.sleep(self.interval)

    def start(self):
        if self._active: return
        self._active = True
        t = threading.Thread(target=self._loop, daemon=True)
        t.start()

    def stop(self):
        self._active = False
