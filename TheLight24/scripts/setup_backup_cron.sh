#!/bin/bash
set -e
cd "$(dirname "$0")/.."

SCRIPT_PATH="$(pwd)/scripts/backup_system.sh"
LOG_PATH="$(pwd)/data/runtime/backup_cron.log"
mkdir -p data/runtime

LINE="0 3 * * * bash \"$SCRIPT_PATH\" >> \"$LOG_PATH\" 2>&1"

# Installa o aggiorna la voce di cron evitando duplicati
( crontab -l 2>/dev/null | grep -v "$SCRIPT_PATH" ; echo "$LINE" ) | crontab -

echo "[Cron] Backup giornaliero programmato alle 03:00."
echo "[Cron] Log: $LOG_PATH"
