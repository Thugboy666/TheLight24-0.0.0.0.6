#!/usr/bin/env bash
set -e

echo "[+] Setup TheLight24 v0.0.0.0.5 (audio+video+GUI con avatar)"

# System deps
sudo apt update
sudo apt install -y build-essential cmake git python3 python3-venv python3-pip \
  libasound2-dev portaudio19-dev alsa-utils pulseaudio-utils \
  libsdl2-dev libopenal-dev ffmpeg unzip wget v4l-utils


# Modello Vosk IT
mkdir -p data/models
if [ ! -d "data/models/vosk-model-small-it-0.22" ]; then
  echo "[+] Scarico modello Vosk IT..."
  wget -O /tmp/vosk-it.zip https://alphacephei.com/vosk/models/vosk-model-small-it-0.22.zip
  unzip -o /tmp/vosk-it.zip -d data/models/
fi

# Haar cascades OpenCV per face detection
mkdir -p data/models/haarcascades
if [ ! -f data/models/haarcascades/haarcascade_frontalface_default.xml ]; then
  wget -O data/models/haarcascades/haarcascade_frontalface_default.xml \
    https://raw.githubusercontent.com/opencv/opencv/4.x/data/haarcascades/haarcascade_frontalface_default.xml \
    2>/dev/null || true
fi

# Profili voce
mkdir -p data/profiles

# Build C++ bindings
mkdir -p build
cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
cmake --build . -j
cd ..

# Warmup XTTS (download modello una tantum)
python - <<'PY'
from TTS.api import TTS
print("[+] Warmup XTTS v2 (download & init)...")
TTS("tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=False, gpu=False)
print("[OK] XTTS pronto.")
PY

echo "[OK] Installazione completata."
