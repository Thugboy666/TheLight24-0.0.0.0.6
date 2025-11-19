import os, json, requests, time, queue, threading
import sounddevice as sd
import numpy as np
from vosk import Model, KaldiRecognizer

SAMPLE_RATE = 16000
BLOCK = 256

class VoiceAssistant:
    """Modulo vocale TheLight v6 con TTS remoto e ASR Vosk locale."""

    def __init__(self):
        self.asr_model = Model("data/models/vosk-model-small-it-0.22")
        self.rec = KaldiRecognizer(self.asr_model, SAMPLE_RATE)
        self.q = queue.Queue()
        self.talking = False
        self.host_bridge = os.getenv("HOST_BRIDGE_URL", "http://10.0.2.2:8123")
        print(f"[VoiceAssistant] Bridge DirectML attivo su {self.host_bridge}")

    def _audio_callback(self, indata, frames, time_info, status):
        if status:
            print("[VoiceAssistant] Audio status:", status)
        self.q.put(bytes(indata))

    def listen(self, duration=5):
        """Registra voce utente e converte in testo (ASR)."""
        print("[VoiceAssistant] Ascolto in corso...")
        sd.default.samplerate = SAMPLE_RATE
        sd.default.channels = 1
        frames = []
        with sd.RawInputStream(
            samplerate=SAMPLE_RATE,
            blocksize=BLOCK,
            dtype="int16",
            channels=1,
            callback=self._audio_callback,
        ):
            start = time.time()
            while time.time() - start < duration:
                data = self.q.get()
                frames.append(data)
                if self.rec.AcceptWaveform(data):
                    res = json.loads(self.rec.Result())
                    if res.get("text"):
                        print("[ASR]", res["text"])
                        return res["text"]
        res = json.loads(self.rec.FinalResult())
        return res.get("text", "")

    def speak(self, text: str):
        """Richiede TTS al bridge Piper."""
        try:
            payload = {"text": text}
            r = requests.post(f"{self.host_bridge}/tts", json=payload, timeout=15)
            if r.status_code == 200:
                path = f"data/runtime/{int(time.time())}_tts.wav"
                with open(path, "wb") as f:
                    f.write(r.content)
                data, sr = sd.read(path)
                self.talking = True
                sd.play(data, sr)
                sd.wait()
                self.talking = False
            else:
                print("[VoiceAssistant][TTS] Errore:", r.text)
        except Exception as e:
            print("[VoiceAssistant][TTS] Bridge non raggiungibile:", e)
