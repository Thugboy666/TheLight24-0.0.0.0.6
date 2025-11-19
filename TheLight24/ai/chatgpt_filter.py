import openai
from ai.utils import load_env

class ChatGPTFilter:
    def __init__(self):
        env = load_env()
        self.enabled = False
        if env.get("OPENAI_API_KEY"):
            openai.api_key = env["OPENAI_API_KEY"]
            self.enabled = True

    def ask(self, text: str) -> str:
        if not self.enabled:
            return "[Offline] ChatGPT disabilitato."
        try:
            resp = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role":"system","content":"Assistente tecnico conciso."},
                          {"role":"user","content":text}]
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            return f"[ChatGPT errore] {e}"
