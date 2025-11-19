from fastapi import FastAPI
from fastapi.responses import JSONResponse
import sounddevice as sd, numpy as np, time
from openwakeword.model import Model

app=FastAPI(title="OpenWakeWord Satellite")

oww=Model(wakeword_models=["data/models/openwakeword/hey_light.tflite"])
SAMPLE_RATE=16000; HOP=320; THR=0.5

@app.get("/listen")
def listen(seconds:int=2):
    dur=max(1,min(10,seconds))
    buf=sd.rec(int(SAMPLE_RATE*dur),samplerate=SAMPLE_RATE,channels=1,dtype="float32")
    sd.wait()
    arr=buf.flatten()
    pos=0; fired=False; conf=0.0
    while pos+HOP<=len(arr):
        score=oww.predict(arr[pos:pos+HOP])
        if score:
            conf=max(score.values())
            if conf>=THR: fired=True; break
        pos+=HOP
    return {"detected":fired,"confidence":conf}
