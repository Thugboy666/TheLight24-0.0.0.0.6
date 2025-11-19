import os, json, queue, threading, time, requests, io, wave
import numpy as np
import sounddevice as sd
import webrtcvad

from vosk import Model, KaldiRecognizer

# OpenWakeWord
from openwakeword.model import Model as OWWModel

from ai.voice_profiles import get_profile, list_profiles
from ai.utils import load_env, ensure_dirs
from ai.speech_sync import sync

SAMPLE_RATE = 16000
BLOCK = 512                   # più stabile per wakeword+VAD
OWW_FRAME_MS = 20             # 20 ms/frame consigliato
OWW_HOP = int(SAMPLE_RATE * (OWW_FRAME_MS / 1000.0))  # 320 samples @16k

WAKEWORD_THRESHOLD = 0.5      # soglia confidenza "hey light"
WAKEWORD_REFRACTORY = 1.0     # secondi di antirimbalzo

class VoiceAssistant:
    """
    TheLight24 v6 – Assistente vocale:
      - Wake word: OpenWakeWord (modello tflite locale)
      - ASR: Vosk IT
      - TTS: Bridge Piper su Windows via HTTP (env HOST_BRIDGE_URL) -> riproduzione wav in locale
      - Interruzione immediata se l'umano parla sopra
      - Lip sync: ai/speech_sync.py (vu + talking)
    """

    def __init__(self):
        ensure_dirs()
        env = load_env()

        # ==============================
        # Profili vocali (per futuro XTTS cloning; qui non utilizzati)
        # ==============================
        self.active_profile = None
        active_file = "data/profiles/active.txt"
        if os.path.exists(active_file):
            with open(active_file, encoding="utf-8") as f:
                self.active_profile = f.read().strip()
        if not self.active_profile:
            profs = list_profiles()
            if profs:
                self.active_profile = profs[0]["name"]

        # ==============================
        # Wake Word (OpenWakeWord)
        # ==============================
        oww_dir = "data/models/openwakeword"
        model_path = os.path.join(oww_dir, "hey_light.tflite")
        if not os.path.exists(model_path):
            raise RuntimeError(f"[OpenWakeWord] Modello assente: {model_path}")
        self.oww = OWWModel(wakeword_models=[model_path])

        self.last_ww = 0.0
        self.wake_ok = True

        # ==============================
        # ASR (Vosk IT)
        # ==============================
        self.model = Model("data/models/vosk-model-small-it-0.22")
        self.rec = KaldiRecognizer(self.model, SAMPLE_RATE)

        # ==============================
        # TTS Bridge (Windows Piper)
        # ==============================
        # Es. http://10.0.2.2:8123   (host da guest VirtualBox)
        self.bridge_url = env.get("HOST_BRIDGE_URL", "http://10.0.2.2:8123").rstrip("/")
        self.tts_endpoint = f"{self.bridge_url}/say"

        # ==============================
        # Audio In/Out + VAD
        # ==============================
        self.q = queue.Queue()
        self.vad = webrtcvad.Vad(2)  # 0..3 (più alto = più aggressivo)

        mic_idx = env.get("MIC_DEVICE_INDEX", "").strip()
        if mic_idx.isdigit():
            sd.default.device = (int(mic_idx), None)
        sd.default.samplerate = SAMPLE_RATE
        sd.default.channels = 1

        # runtime flags
        self.talking = False
        self.user_interrupt = False


    # ---------------------------------------------------------
    #                 AUDIO INPUT CALLBACK
    # ---------------------------------------------------------
    def _is_speech(self, frame_int16):
        try:
            return self.vad.is_speech(frame_int16.tobytes(), SAMPLE_RATE)
        except Exception:
            return False

    def _audio_in_callback(self, indata, frames, time_info, status):
        if status:  # non bloccare per underrun/overrun
            pass
        self.q.put(bytes(indata))

        # Interrompi TTS se l'umano parla sopra
        if self.talking:
            frame = np.frombuffer(indata, dtype=np.int16)
            if self._is_speech(frame):
                self.user_interrupt = True
                sync.set_interrupted(True)

    # ---------------------------------------------------------
    #                       T T S
    # ---------------------------------------------------------
    def _play_wav_bytes(self, wav_bytes: bytes):
        # decodifica WAV (PCM16 mono) e riproduci
        with wave.open(io.BytesIO(wav_bytes), 'rb') as wf:
            if wf.getframerate() != SAMPLE_RATE:
                # semplice resample nearest
                raw = wf.readframes(wf.getnframes())
                pcm = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
                ratio = SAMPLE_RATE / float(wf.getframerate())
                idx = (np.arange(0, int(len(pcm)*ratio)) / ratio).astype(np.int32)
                idx = np.clip(idx, 0, len(pcm)-1)
                audio = pcm[idx]
            else:
                raw = wf.readframes(wf.getnframes())
                audio = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0

        # streaming + lip sync
        self.talking = True
        self.user_interrupt = False
        sync.set_talking(True)

        chunk = 2048
        stream = sd.OutputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="float32"
        )
        stream.start()
        try:
            for i in range(0, len(audio), chunk):
                if self.user_interrupt:
                    break
                buf = audio[i:i+chunk]
                vu = float(np.sqrt(np.mean(np.square(buf)))) if len(buf) else 0.0
                sync.set_vu(min(vu * 4.0, 1.0))
                stream.write(buf)
        finally:
            stream.stop()
            stream.close()
            self.talking = False
            sync.set_talking(False)
            sync.set_vu(0.0)

    def speak(self, text: str):
        """
        TTS via Piper (Windows host_bridge). Se non disponibile, stampa solo.
        """
        text = (text or "").strip()
        if not text:
            return
        try:
            r = requests.get(self.tts_endpoint, params={"text": text}, timeout=10)
            if r.status_code == 200 and r.content:
                self._play_wav_bytes(r.content)
            else:
                print("[VoiceAssistant][TTS Bridge] Risposta non valida:", r.status_code)
                print(">>", text)
        except Exception as e:
            print("[VoiceAssistant][TTS Bridge] Non raggiungibile:", e)
            print(">>", text)

    # ---------------------------------------------------------
    #                 W A K E   W O R D
    # ---------------------------------------------------------
    def _ww_detect(self, audio_int16: np.ndarray) -> bool:
        """
        Rileva 'hey light' con OpenWakeWord. Usa hop da 20ms.
        """
        now = time.time()
        if (now - self.last_ww) < WAKEWORD_REFRACTORY:
            return False

        # spezzetta in frame 20ms
        arr = audio_int16.astype(np.float32) / 32768.0
        pos = 0
        fired = False
        while pos + OWW_HOP <= len(arr):
            frame = arr[pos:pos+OWW_HOP]
            score = self.oww.predict(frame)
            # score è dict: {"model_name": value}
            if score:
                conf = max(score.values())
                if conf >= WAKEWORD_THRESHOLD:
                    self.last_ww = now
                    fired = True
                    break
            pos += OWW_HOP
        return fired

    # ---------------------------------------------------------
    #                   A S C O L T O   L O O P
    # ---------------------------------------------------------
    def listen_loop(self, on_text_callback=None):
        """
        - Wakeword OWW o fallback (auto-ask) se utente parla
        - Cattura frase con Vosk
        - Passa testo alla callback
        """
        print("[Voce] In ascolto microfono... (wake word: 'hey light')")
        with sd.RawInputStream(
            samplerate=SAMPLE_RATE,
            blocksize=BLOCK,
            dtype="int16",
            channels=1,
            callback=self._audio_in_callback
        ):
            speech_active = False
            last_speech = time.time()

            while True:
                data = self.q.get()
                frame_i16 = np.frombuffer(data, dtype=np.int16)

                # wake word
                try:
                    if self._ww_detect(frame_i16):
                        # interrompi eventuale parlato AI
                        if self.talking:
                            self.user_interrupt = True
                        self.speak("Ciao! Dimmi pure.")
                        speech_active = True
                        last_speech = time.time()
                        self.rec.Reset()
                except Exception as e:
                    # Se OWW dovesse fallire, fallback su speech activity
                    pass

                # fallback: se non stiamo registrando e l'utente inizia a parlare
                if not speech_active and self._is_speech(frame_i16):
                    # soft auto-activate
                    speech_active = True
                    last_speech = time.time()
                    self.rec.Reset()
                    print("[VoiceAssistant] >> ASCOLTO ATTIVO <<<")

                # blocco cattura parlato
                if speech_active:
                    if self.rec.AcceptWaveform(data):
                        res = json.loads(self.rec.Result())
                        text = (res.get("text") or "").strip()
                        if text:
                            print("[ASR]", text)
                            if on_text_callback:
                                on_text_callback(text)
                        speech_active = False
                    else:
                        if self._is_speech(frame_i16):
                            last_speech = time.time()
                        else:
                            # se silenzio >1.4s, chiudiamo la frase
                            if time.time() - last_speech > 1.4:
                                res = json.loads(self.rec.FinalResult())
                                text = (res.get("text") or "").strip()
                                if text:
                                    print("[ASR]", text)
                                    if on_text_callback:
                                        on_text_callback(text)
                                speech_active = False
