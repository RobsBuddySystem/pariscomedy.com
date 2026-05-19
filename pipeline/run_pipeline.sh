#!/usr/bin/env bash
# ParisComedy pipeline — run all stages in order
# Usage:
#   ./pipeline/run_pipeline.sh
#   ./pipeline/run_pipeline.sh --dry-run        # use cached fixture data
#   ./pipeline/run_pipeline.sh --stage 03       # start from a specific stage
#
# Stages:
#   01_scrape       Fetch Eventbrite comedy events
#   02_normalize    Parse dates, clean venue names, dedup by EB ID
#   03_llm_extract  Local LLM comedy/language/type classification (qwen2.5:32b)
#   04_dedupe       Fingerprint merge of cross-source duplicates
#   05_classify     Confidence scoring → high/review/reject tiers
#   06_validate     Schema check, past-date filter, lookahead flag
#   07_export       Merge into shows.json, write review_queue.json + metrics
#   08_review_queue Format review queue HTML for admin UI

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
LOG_DIR="$REPO_ROOT/pipeline/logs"
LOG="$LOG_DIR/pipeline_${TIMESTAMP}.log"

mkdir -p "$LOG_DIR" "$REPO_ROOT/pipeline/output"
cd "$REPO_ROOT"

# ── Argument parsing ──────────────────────────────────────────────────────────
DRY_RUN=""
START_STAGE=1
PASSTHROUGH_ARGS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      DRY_RUN="--dry-run"
      PASSTHROUGH_ARGS+=("--dry-run")
      shift
      ;;
    --stage)
      START_STAGE="$2"
      shift 2
      ;;
    *)
      shift
      ;;
  esac
done

# ── Helpers ───────────────────────────────────────────────────────────────────
log() {
  echo "[$(date +%H:%M:%S)] $*" | tee -a "$LOG"
}

run_stage() {
  local num="$1"
  local name="$2"
  local script="pipeline/stages/${num}_${name}.py"

  if [[ "10#$num" -lt "10#$START_STAGE" ]]; then
    log "Stage ${num}: ${name} — SKIPPED (--stage ${START_STAGE})"
    return 0
  fi

  log "Stage ${num}: ${name} — starting"

  if python3 "$script" "${PASSTHROUGH_ARGS[@]}" 2>&1 | tee -a "$LOG"; then
    log "Stage ${num}: ${name} — OK"
  else
    local exit_code=$?
    log "Stage ${num}: ${name} — FAILED (exit ${exit_code})"
    log "Pipeline halted. Check log: $LOG"
    exit $exit_code
  fi
}

# ── Pre-flight ────────────────────────────────────────────────────────────────
log "=== ParisComedy pipeline start ==="
log "Repo:    $REPO_ROOT"
log "Log:     $LOG"
log "Options: dry-run=${DRY_RUN:-no} start-stage=${START_STAGE}"
python3 --version 2>&1 | tee -a "$LOG"

# Check Python deps
python3 -c "import requests, bs4, yaml, dateutil" 2>/dev/null || {
  log "ERROR: Missing Python deps. Run: pip3 install requests beautifulsoup4 pyyaml python-dateutil"
  exit 1
}

# ── Stages ────────────────────────────────────────────────────────────────────
run_stage 01 scrape
run_stage 02 normalize
run_stage 03 llm_extract
run_stage 04 dedupe
run_stage 05 classify
run_stage 06 validate
run_stage 07 export
run_stage 08 review_queue

# ── Done ──────────────────────────────────────────────────────────────────────
log "=== Pipeline complete. Log: $LOG ==="
