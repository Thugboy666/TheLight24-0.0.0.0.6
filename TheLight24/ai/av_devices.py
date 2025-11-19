import sounddevice as sd

def list_audio_devices():
    try:
        devs = sd.query_devices()
        return [{"index": i, "name": d["name"], "max_input_channels": d["max_input_channels"]} for i, d in enumerate(devs)]
    except Exception as e:
        return [{"error": str(e)}]
