#!/usr/bin/env bash
# Hourly Mac fallback: validate ticket URLs, re-bake HTML, commit/push to a
# dedicated `hourly-data` branch (NOT main). main is reserved for human/Claude
# work; a separate nightly job fast-forwards main from hourly-data.
# Refuses to push if active count < 10 or JSON invalid.
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"

LOG="/tmp/pariscomedy-hourly.log"
ERR="/tmp/pariscomedy-hourly.err"
: >"$LOG"; : >"$ERR"
BRANCH="hourly-data"

{
  echo "=== $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="

  # Remember whichever branch the human was on so we restore it.
  ORIG_BRANCH="$(git rev-parse --abbrev-ref HEAD)"

  # Refuse if working tree is dirty — never trample human work in progress.
  if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "ABORT: working tree dirty on $ORIG_BRANCH — refusing to touch repo"
    exit 1
  fi

  git fetch origin --quiet

  # Ensure local hourly-data tracks origin/hourly-data, creating from origin/main if absent.
  if git show-ref --verify --quiet "refs/remotes/origin/$BRANCH"; then
    git checkout -B "$BRANCH" "origin/$BRANCH"
  else
    git checkout -B "$BRANCH" origin/main
  fi

  # Rebase hourly-data onto latest main so we never diverge.
  git rebase origin/main || { git rebase --abort; echo "rebase failed"; exit 1; }

  # Discovery refresh (read-only w.r.t. published data — merge stays Robert-gated).
  python3 scripts/discover_shows.py || echo "discover_shows.py failed (non-fatal)"
  python3 scripts/comic_actuality.py || echo "comic_actuality.py failed (non-fatal)"
  python3 scripts/validate_tickets.py
  python3 -c "import json; json.load(open('data/shows_generated.json'))"  # JSON sanity
  python3 scripts/bake_shows.py

  TRACKED=(data/shows_generated.json data/review_queue.json data/discovered_shows.json data/scrape_conflicts.json data/organizers.json data/comic_actuality.json data/comic_actuality_unverified.json index.html shows.html)

  if git diff --quiet -- "${TRACKED[@]}"; then
    echo "no-op (no diff)"
    git checkout "$ORIG_BRANCH" --quiet
    exit 0
  fi

  git add "${TRACKED[@]}"
  git commit -m "hourly: revalidate + discovery refresh ($(date -u +%Y-%m-%dT%H:%MZ))"
  git push origin "$BRANCH"
  echo "pushed to $BRANCH"

  git checkout "$ORIG_BRANCH" --quiet
} >>"$LOG" 2>&1
