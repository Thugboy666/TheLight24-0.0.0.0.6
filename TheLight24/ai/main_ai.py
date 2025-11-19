import threading, time
from ai.voice_assistant import VoiceAssistant
from ai.chatgpt_filter import ChatGPTFilter
from ai.neural_core import NeuralCore
from ai.scheduler import Scheduler

class TheLightAI:
    def __init__(self):
        self.core = NeuralCore(layers=[256,512,512,256])
        self.voice = VoiceAssistant(wake_keyword="porcupine")
        self.chat = ChatGPTFilter()
        self.scheduler = Scheduler(self)

    def on_voice_text(self, text: str):
        print(f"[ASR] {text}")
        # Esempio di routing locale → simulatore/GUI (da completare in 3/5-4/5)
        if any(k in text.lower() for k in ["simulazione","pendolo","gravità","termica"]):
            self.say("Ok, imposto i parametri della simulazione.")
            return

        score = self.core.reason([0.2,0.1,0.3], [ord(c)%256 for c in text][:32])
        if score > 0.05 and len(text) < 80:
            self.say("Ricevuto. Procedo.")
        else:
            ans = self.chat.ask(text)
            self.say(ans)

    def say(self, text: str):
        self.voice.speak(text)

    def start(self):
        self.scheduler.start()
        threading.Thread(target=self.voice.listen_loop,
                         kwargs={"on_text_callback": self.on_voice_text},
                         daemon=True).start()
        while True:
            time.sleep(1)

if __name__ == "__main__":
    TheLightAI().start()
