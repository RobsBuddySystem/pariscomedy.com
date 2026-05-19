#!/usr/bin/env bash
# Run on Mac Studio after receiving synced data from openclawpc.
# Regenerates public show JSON, commits to git, and pushes to GitHub Pages.
#
# This script is called remotely by sync_to_macstudio.sh via SSH.
# It can also be triggered by the launchd WatchPaths plist.
#
# Usage (manual):
#   bash pipeline/sync/receive_on_mac.sh

set -euo pipefail

REPO="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO"

log() { echo "[$(date +%H:%M:%S)] [RECEIVE] $*"; }

log "Regenerating show instances from shows.json..."
python3 generate_instances.py

log "Validating generated JSON before commit..."
for f in data/shows_generated.json data/shows.json pipeline/output/review_queue.json; do
  if [ -f "$f" ]; then
    if ! python3 -c "import json,sys; json.load(open('$f'))" 2>/dev/null; then
      log "ERROR: $f is invalid JSON — aborting commit/push to prevent site breakage."
      exit 1
    fi
    log "  OK: $f"
  fi
done

# Sanity: shows_generated must have at least 10 entries
COUNT=$(python3 -c "import json; print(len(json.load(open('data/shows_generated.json'))))")
if [ "$COUNT" -lt 10 ]; then
  log "ERROR: shows_generated.json has only $COUNT entries (expected ≥ 10) — aborting push."
  exit 1
fi
log "  shows_generated.json: $COUNT entries — OK"

log "Regenerating admin review queue HTML..."
python3 pipeline/stages/08_review_queue.py

log "Committing updated data files..."
git add \
  data/shows.json \
  data/shows_generated.json \
  pipeline/output/review_queue.json \
  api/review-queue.html

# --allow-empty handles the case where nothing changed (idempotent)
git commit -m "chore: daily pipeline sync $(date +%Y-%m-%d)" --allow-empty

log "Pushing to GitHub Pages (origin main)..."
git push origin main

log "Done — pariscomedy.com updated."
