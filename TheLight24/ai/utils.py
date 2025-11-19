import os
from dotenv import load_dotenv

def load_env():
    if os.path.exists(".env"):
        load_dotenv(".env")
    return {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
        "PICOVOICE_ACCESS_KEY": os.getenv("PICOVOICE_ACCESS_KEY", ""),
        "MIC_DEVICE_INDEX": os.getenv("MIC_DEVICE_INDEX", ""),
        "CAM_INDEX": os.getenv("CAM_INDEX", "0"),
    }

def ensure_dirs():
    os.makedirs("data/models", exist_ok=True)
    os.makedirs("data/profiles", exist_ok=True)
    os.makedirs("data/runtime", exist_ok=True)
