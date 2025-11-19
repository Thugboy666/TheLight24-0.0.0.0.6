#!/bin/bash
set -e
cd "$(dirname "$0")/.."

STAMP=$(date +"%Y%m%d_%H%M")
VER_JSON="data/runtime/state.json"
VER="v6"
if [ -f "$VER_JSON" ]; then
  V=$(grep -oE "v[0-9]+\.[0-9]+\.[0-9]+" "$VER_JSON" | head -1)
  [ -n "$V" ] && VER="$V"
fi

OUT="TheLight24_${VER}_${STAMP}.zip"

echo "[Backup] Creo backup: $OUT"
# zip completo, esclusi i backup stessi e cache tipiche
zip -rq "$OUT" . \
  -x "*.zip" \
  -x "__pycache__/*" \
  -x ".venv/**/__pycache__/*" \
  -x ".git/*"

echo "[Backup] OK -> $OUT"
