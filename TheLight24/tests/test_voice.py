import pytest

def test_lib_imports():
    import pvporcupine, vosk, TTS
    assert pvporcupine and vosk and TTS

@pytest.mark.skip(reason="Test live microfono disabilitato per default")
def test_mic_stream(audio_enabled):
    if not audio_enabled:
        pytest.skip("Avvia con --with-audio per testare il microfono live")
    import sounddevice as sd
    import numpy as np
    import queue, time

    q = queue.Queue()
    def cb(indata, frames, time_info, status):
        q.put(indata.copy())

    with sd.RawInputStream(samplerate=16000, blocksize=256, dtype="int16", channels=1, callback=cb):
        start = time.time()
        got = 0
        while time.time() - start < 1.5:
            while not q.empty():
                buf = q.get()
                got += len(np.frombuffer(buf, dtype=np.int16))
        assert got > 0
