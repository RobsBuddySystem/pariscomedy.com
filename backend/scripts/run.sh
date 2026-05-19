#!/usr/bin/env bash
# Run the ParisComedy backend locally.
set -euo pipefail
cd "$(dirname "$0")/.."

if [ ! -d venv ]; then
  python3 -m venv venv
  ./venv/bin/pip install -q -U pip
  ./venv/bin/pip install -q -r requirements.txt
fi

# Load env from ./env if present (do NOT commit env to git)
if [ -f env ]; then set -a; . ./env; set +a; fi

PORT="${PORT:-8765}"
HOST="${HOST:-127.0.0.1}"
exec ./venv/bin/uvicorn main:app --host "$HOST" --port "$PORT" --no-access-log
