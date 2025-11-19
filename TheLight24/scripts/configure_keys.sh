#!/usr/bin/env bash
set -e
touch .env
read -p "PICOVOICE_ACCESS_KEY (o vuoto): " PK
read -p "OPENAI_API_KEY (o vuoto): " OK
read -p "MIC_DEVICE_INDEX (es. 2, vuoto=default): " MIC
read -p "CAM_INDEX (es. 0, vuoto=0): " CAM

grep -q "^PICOVOICE_ACCESS_KEY=" .env && sed -i "s|^PICOVOICE_ACCESS_KEY=.*|PICOVOICE_ACCESS_KEY=$PK|" .env || echo "PICOVOICE_ACCESS_KEY=$PK" >> .env
grep -q "^OPENAI_API_KEY=" .env && sed -i "s|^OPENAI_API_KEY=.*|OPENAI_API_KEY=$OK|" .env || echo "OPENAI_API_KEY=$OK" >> .env
[ -n "$MIC" ] && (grep -q "^MIC_DEVICE_INDEX=" .env && sed -i "s|^MIC_DEVICE_INDEX=.*|MIC_DEVICE_INDEX=$MIC|" .env || echo "MIC_DEVICE_INDEX=$MIC" >> .env)
[ -n "$CAM" ] && (grep -q "^CAM_INDEX=" .env && sed -i "s|^CAM_INDEX=.*|CAM_INDEX=$CAM|" .env || echo "CAM_INDEX=$CAM" >> .env)

echo "[OK] .env aggiornato. Non committare questo file."
