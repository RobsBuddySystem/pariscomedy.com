#!/usr/bin/env python3
import json, sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / 'data' / 'intake' / 'submissions.sqlite3'
JSONL_PATH = ROOT / 'data' / 'intake' / 'submissions.jsonl'

conn = sqlite3.connect(DB_PATH)
try:
    count = conn.execute('SELECT COUNT(*) FROM submissions').fetchone()[0]
    forward_failures = conn.execute('SELECT COUNT(*) FROM submissions WHERE forwarded = 0').fetchone()[0]
except sqlite3.OperationalError:
    count = 0
    forward_failures = 0
conn.close()
jsonl_count = 0
if JSONL_PATH.exists():
    with JSONL_PATH.open() as fh:
        for line in fh:
            if line.strip():
                json.loads(line)
                jsonl_count += 1
print(json.dumps({'db_submissions': count, 'jsonl_submissions': jsonl_count, 'forward_failures': forward_failures}, indent=2))
