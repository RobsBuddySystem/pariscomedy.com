#!/usr/bin/env python3
"""Paris Comedy email collector — lightweight endpoint for newsletter signups"""
import json, os, time
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

DB = Path.home() / "BitByBit" / "pariscomedy-emails.json"
PORT = 18791

def load_emails():
    if DB.exists():
        return json.loads(DB.read_text())
    return []

def save_email(email):
    emails = load_emails()
    # Deduplicate
    if any(e['email'] == email for e in emails):
        return False
    emails.append({'email': email, 'ts': int(time.time()), 'source': 'newsletter'})
    DB.write_text(json.dumps(emails, indent=2))
    return True

class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = json.loads(self.rfile.read(length)) if length else {}
        email = body.get('email', '').strip()
        if not email or '@' not in email:
            self.send_response(400)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'invalid email'}).encode())
            return
        new = save_email(email)
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'ok': True, 'new': new}).encode())

    def log_message(self, *a): pass  # Silent

if __name__ == '__main__':
    print(f'Email collector running on port {PORT}')
    HTTPServer(('0.0.0.0', PORT), Handler).serve_forever()
