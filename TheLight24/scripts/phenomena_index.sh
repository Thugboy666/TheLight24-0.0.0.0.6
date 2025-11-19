#!/bin/bash
set -e
cd "$(dirname "$0")/.."
source .venv/bin/activate
python3 - <<'PY'
from ai.phenomena_loader import PhenomenaIndex
idx=PhenomenaIndex("data/knowledge/fenomeni_universo_costituzione_totale.csv")
idx.build()
PY
