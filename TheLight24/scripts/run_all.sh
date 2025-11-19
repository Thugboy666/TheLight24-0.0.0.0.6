#!/bin/bash
set -e
cd "$(dirname "$0")/.."
source .venv/bin/activate

# 0) indicizza fenomeni (CSV -> JSON) – safe to ignore errors if CSV missing
bash scripts/phenomena_index.sh || true

# 1) avvia API (sim + ecom + core systems)
( uvicorn src.api.server:app --host 127.0.0.1 --port 8000 --log-level warning ) &

sleep 2

# 2) carica scenario base della fisica e avvia integrazione headless periodica
curl -s -X POST "http://127.0.0.1:8000/sim/load?scenario=solar_system_min.json" >/dev/null || true
bash scripts/sim_bench.sh &

# 3) avvia Core AI (parlato, memoria, governance)
python3 ai/core_ai.py &

# 4) bootstrap e-commerce di esempio (facoltativo, una sola volta)
bash scripts/init_ecommerce.sh || true

# 5) avvia GUI 3D UNIVERSE e poi apri GUI GALAXY-COMMERCE (in due istanze separate)
python3 src/gui3d/main_gui3d.py &

# lascia 2 secondi e poi apri il marketplace
sleep 2
python3 src/gui3d/market_gui3d.py
