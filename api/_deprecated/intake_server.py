#!/usr/bin/env python3
"""
DEPRECATED — 2026-05-29 (P3.SUBMIT.4)
======================================

This localhost-only HTTP intake server is no longer wired to any frontend form.
It was never reachable from production (bound to 127.0.0.1 only, no public route).

The canonical submit flow is now:
    /book.html  ->  POST https://api.pariscomedy.com/api/submissions

Submissions are inspected via the operator HUD at /status.html (NOT via the
static /api/review-queue.html placeholder, which is also deprecated).

This file is preserved (not deleted) so operators can reference the historical
schema and validation rules if/when a backend review-queue producer is built.

Do not re-enable without re-auditing — depends on:
  - /Users/chuck/.openclaw/workspace/send_email.py (machine-local)
  - sqlite db under <repo>/data/intake/ (not synced)
  - subprocess shell-out to chucklericain@icloud.com forwarder

See: chuck_vault/.../P3_SUBMIT_4_DEPRECATE_INTAKE.md
"""
import json, re, sqlite3, subprocess, sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / 'data' / 'intake'
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / 'submissions.sqlite3'
JSONL_PATH = DATA_DIR / 'submissions.jsonl'
FORWARD_TO = 'chucklericain@icloud.com'
SEND_SCRIPT = Path('/Users/chuck/.openclaw/workspace/send_email.py')
EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''CREATE TABLE IF NOT EXISTS submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT NOT NULL,
        kind TEXT NOT NULL,
        name TEXT,
        email TEXT NOT NULL,
        subject TEXT,
        message TEXT,
        page TEXT,
        url TEXT,
        show_name TEXT,
        venue_name TEXT,
        schedule TEXT,
        ticket_url TEXT,
        tier TEXT,
        forwarded INTEGER NOT NULL DEFAULT 0,
        forward_error TEXT
    )''')
    return conn


def parse_body(handler):
    length = int(handler.headers.get('Content-Length', '0') or '0')
    raw = handler.rfile.read(length) if length else b''
    ctype = handler.headers.get('Content-Type', '')
    if 'application/json' in ctype:
        return json.loads(raw.decode('utf-8') or '{}')
    if 'application/x-www-form-urlencoded' in ctype:
        parsed = parse_qs(raw.decode('utf-8'))
        return {k: v[-1] for k, v in parsed.items()}
    return {}


def validate(payload):
    email = (payload.get('email') or '').strip()
    if not EMAIL_RE.match(email):
        return 'invalid email'
    kind = (payload.get('kind') or '').strip() or 'contact'
    if kind not in {'newsletter', 'contact', 'listing'}:
        return 'invalid kind'
    if kind == 'contact' and not (payload.get('message') or '').strip():
        return 'message required'
    if kind == 'listing':
        if not (payload.get('show_name') or '').strip():
            return 'show name required'
        if not (payload.get('tier') or '').strip():
            return 'tier required'
    return None


def forward_email(rowid, payload):
    kind = payload.get('kind', 'contact')
    if kind == 'listing':
        tier = payload.get('tier', '?')
        show = payload.get('show_name', '?')
        subject = f"NEW LISTING REQUEST #{rowid} — {show} ({tier})"
        lines = [
            f"LISTING REQUEST — #{rowid}",
            f"Show: {payload.get('show_name','')}",
            f"Venue: {payload.get('venue_name','')}",
            f"Schedule: {payload.get('schedule','')}",
            f"Ticket URL: {payload.get('ticket_url','')}",
            f"Tier: {payload.get('tier','')}",
            f"Contact: {payload.get('name','')} <{payload.get('email','')}>",
            f"Notes: {payload.get('message','')}",
        ]
        body = '\n'.join(lines)
    else:
        subject = f"Paris Comedy intake #{rowid} — {kind}"
        body = json.dumps(payload, indent=2, ensure_ascii=False)
    result = subprocess.run([sys.executable, str(SEND_SCRIPT), FORWARD_TO, subject, body], capture_output=True, text=True)
    return result.returncode == 0, (result.stderr or result.stdout).strip()


class Handler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_GET(self):
        if self.path != '/api/intake/health':
            self.send_response(404)
            self._cors()
            self.end_headers()
            return
        conn = db()
        count = conn.execute('SELECT COUNT(*) FROM submissions').fetchone()[0]
        conn.close()
        self.send_response(200)
        self._cors()
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'ok': True, 'submissions': count}).encode())

    def do_POST(self):
        if self.path != '/api/intake':
            self.send_response(404)
            self._cors()
            self.end_headers()
            return
        payload = parse_body(self)
        error = validate(payload)
        if error:
            self.send_response(400)
            self._cors()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'ok': False, 'error': error}).encode())
            return

        now = datetime.now(timezone.utc).isoformat()
        record = {
            'created_at': now,
            'kind': payload.get('kind', 'contact'),
            'name': (payload.get('name') or '').strip(),
            'email': (payload.get('email') or '').strip(),
            'subject': (payload.get('subject') or '').strip(),
            'message': (payload.get('message') or '').strip(),
            'page': payload.get('page') or '',
            'url': payload.get('url') or ''
        }
        conn = db()
        cur = conn.execute('INSERT INTO submissions (created_at, kind, name, email, subject, message, page, url) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                           (record['created_at'], record['kind'], record['name'], record['email'], record['subject'], record['message'], record['page'], record['url']))
        rowid = cur.lastrowid
        JSONL_PATH.write_text(JSONL_PATH.read_text() + json.dumps({'id': rowid, **record}, ensure_ascii=False) + '\n' if JSONL_PATH.exists() else json.dumps({'id': rowid, **record}, ensure_ascii=False) + '\n')
        forwarded, info = forward_email(rowid, record)
        conn.execute('UPDATE submissions SET forwarded = ?, forward_error = ? WHERE id = ?', (1 if forwarded else 0, None if forwarded else info, rowid))
        conn.commit()
        conn.close()

        self.send_response(200)
        self._cors()
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'ok': True, 'id': rowid, 'forwarded': forwarded}).encode())

    def log_message(self, *args):
        pass


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8787
    print(f'Paris Comedy intake listening on http://127.0.0.1:{port}/api/intake')
    ThreadingHTTPServer(('127.0.0.1', port), Handler).serve_forever()
