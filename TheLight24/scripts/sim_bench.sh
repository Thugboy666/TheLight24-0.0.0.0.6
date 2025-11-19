#!/bin/bash
# Headless runner: carica scenario, integra per N step, salva snapshot periodici
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
source .venv/bin/activate

PY=$(cat <<'PYCODE'
import json, time
from src.sim.universe import Universe

U=Universe()
U.load_from_json("src/sim/scenarios/solar_system_min.json")

for i in range(300):
    dt=U.step()
    if i%10==0:
        snap=U.snapshot(2000)
        with open("data/runtime/last_snapshot.json","w",encoding="utf-8") as f:
            json.dump(snap,f)
print("OK")
PYCODE
)
python3 -c "$PY"
