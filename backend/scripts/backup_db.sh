#!/usr/bin/env bash
# Backup the ParisComedy SQLite DB. Run daily via launchd or cron.
# Keeps last 30 daily backups; older ones rolled off.
set -euo pipefail

DB_PATH="${DB_PATH:-$(cd "$(dirname "$0")/../../data" && pwd)/paris.db}"
BACKUP_DIR="${BACKUP_DIR:-$(cd "$(dirname "$0")/.." && pwd)/backups}"
mkdir -p "$BACKUP_DIR"

STAMP=$(date +%Y%m%d_%H%M%S)
OUT="$BACKUP_DIR/paris-${STAMP}.db"

if [ ! -f "$DB_PATH" ]; then
  echo "DB not found at $DB_PATH" >&2; exit 1
fi

# Use SQLite's online backup (safe while server is writing)
sqlite3 "$DB_PATH" ".backup '$OUT'"
gzip -9 "$OUT"
echo "[backup] $OUT.gz"

# Roll off backups older than 30 days
find "$BACKUP_DIR" -name 'paris-*.db.gz' -mtime +30 -delete
echo "[backup] retention pruned to 30 days"
