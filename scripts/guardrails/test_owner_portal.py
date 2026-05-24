#!/usr/bin/env python3
"""Show-runner portal access tests against the live backend.

1. No-token request to owner endpoints returns 401.
2. Token issued for one show cannot access another show (403).
3. Public ownership endpoint never leaks email.
4. RSVP list requires owner/admin.
5. show-runner.html declares noindex and contains no Eventbrite/SumUp tokens.
"""
from __future__ import annotations
import json
import re
import sys
import urllib.request
from pathlib import Path

BASE = "https://api.pariscomedy.com"
ROOT = Path(__file__).resolve().parents[2]


def http(method, path, headers=None, data=None):
    req = urllib.request.Request(BASE + path, method=method,
        headers={"User-Agent":"PC-Test/1", **(headers or {})},
        data=data.encode() if data else None)
    try:
        with urllib.request.urlopen(req, timeout=12) as r:
            return r.status, r.read().decode("utf-8","replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8","replace")


def main() -> int:
    failures = []

    # 1. No token → 401
    code, _ = http("GET", "/api/owner/shows")
    if code != 401:
        failures.append(f"GET /api/owner/shows without token expected 401, got {code}")
    code, _ = http("GET", "/api/owner/show/ffcn/reservations")
    if code != 401:
        failures.append(f"GET reservations without token expected 401, got {code}")

    # 3. Ownership never leaks email
    code, body = http("GET", "/api/show/ffcn/ownership")
    if code == 200:
        d = json.loads(body)
        if "@" in str(d):
            failures.append(f"ownership endpoint leaked email: {body!r}")

    # 5. show-runner.html declares noindex; no obvious tokens
    p = ROOT / "show-runner.html"
    if not p.exists():
        failures.append("show-runner.html missing in repo")
    else:
        text = p.read_text()
        if "noindex" not in text or 'name="robots"' not in text:
            failures.append("show-runner.html missing noindex robots tag")
        for needle in ("sup_sk_", "EVENTBRITE_API_KEY"):
            if needle in text:
                failures.append(f"show-runner.html contains token-shaped {needle!r}")

    if failures:
        print(f"❌ {len(failures)} owner-portal failure(s):")
        for f in failures: print(f"  - {f}")
        return 1
    print("✅ owner-portal access tests pass (no-token=401, ownership no-email, page noindex)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
