#!/usr/bin/env bash
# Hourly Mac fallback: validate ticket URLs, re-bake HTML, commit/push if safe.
# Refuses to push if active count < 10 or JSON invalid.
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"

LOG="/tmp/pariscomedy-hourly.log"
ERR="/tmp/pariscomedy-hourly.err"
: >"$LOG"; : >"$ERR"   # truncate at start of each run
{
  echo "=== $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
  python3 scripts/validate_tickets.py
  python3 -c "import json; json.load(open('data/shows_generated.json'))"  # JSON sanity
  python3 scripts/bake_shows.py

  if git diff --quiet -- data/shows_generated.json data/review_queue.json index.html shows.html; then
    echo "no-op (no diff)"
    exit 0
  fi

  git add data/shows_generated.json data/review_queue.json index.html shows.html
  git commit -m "hourly: revalidate ticket statuses ($(date -u +%Y-%m-%dT%H:%MZ))"
  git push
  echo "pushed"
} >>"$LOG" 2>&1
