import os
from dotenv import dotenv_values

from ai.core_ai import CoreAI
from ai.voice.voice_assistant_v6 import VoiceAssistantV6


def load_env():
    env = {}
    if os.path.exists(".env"):
        env = dotenv_values(".env")
    # default vuoti
    env.setdefault("PICOVOICE_ACCESS_KEY", "")
    env.setdefault("MIC_DEVICE_INDEX", "")
    return env


def main():
    env = load_env()

    core = CoreAI(inference_device_hint="cpu-fallback")  # verrà aggiornato dal voice
    def on_inference_hint(hint):
        # aggiorna il CoreAI per il ledger
        core.inference_device_hint = hint

    voice = VoiceAssistantV6(env, inference_hint_callback=on_inference_hint)

    def on_text_callback(user_text: str):
        reply = core.generate_reply(user_text)
        voice.speak(reply)

    # loop infinito
    voice.listen_loop(on_text_callback)


if __name__ == "__main__":
    main()
