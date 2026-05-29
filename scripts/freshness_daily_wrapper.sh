#!/usr/bin/env bash
# P1.DATA.6 — daily freshness verification wrapper.
# Runs freshness_verify.py, then commits + pushes the refreshed data/freshness-audit.json
# only if the by_status snapshot changed. Logs to logs/freshness-daily.log.
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
cd "$REPO"
mkdir -p logs
LOG="logs/freshness-daily.log"
TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
{
  echo ""
  echo "==== $TS ===="
  if ! python3 scripts/freshness_verify.py 2>&1 ; then
    echo "FAIL: freshness_verify.py exited non-zero" >&2
    exit 1
  fi
  if ! git diff --quiet data/freshness-audit.json ; then
    echo "freshness-audit.json changed — committing"
    git add data/freshness-audit.json
    git commit -m "data | freshness daily run ${TS}" --no-verify
    git push origin main || echo "push failed; will retry next run"
  else
    echo "no change in audit JSON"
  fi

  # P5.AUTOMATION.1 — daily proof package (regression guard + sitemap regen + freshness)
  echo "---- daily_proof_package ----"
  if python3 scripts/daily_proof_package.py ; then
    echo "daily-proof: ok"
  else
    echo "daily-proof: one or more checks FAILED (see logs/daily-proof-*.json)"
  fi
  if ! git diff --quiet sitemap.xml ; then
    echo "sitemap.xml changed — committing"
    git add sitemap.xml
    git commit -m "infra | daily sitemap regen ${TS}" --no-verify
    git push origin main || echo "sitemap push failed; will retry next run"
  else
    echo "no change in sitemap.xml"
  fi
} >> "$LOG" 2>&1
