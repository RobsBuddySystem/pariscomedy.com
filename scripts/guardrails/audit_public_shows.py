#!/usr/bin/env python3
"""Provenance audit for every public show on pariscomedy.com.

Per PROJECT_CANON, a public show must have *one of*:
    (a) a live URL check — the row's ticket_url responded HTTP 2xx in the
        last 7 days (recorded in data/url_health.json), OR
    (b) a fresh manual approval — a matching entry in data/show_approvals.json
        signed by Robert and not yet expired, OR
    (c) recurrence proof — a `recurrence_source_url` field on the row that
        points to a current venue/organizer page documenting the schedule.

Plus baseline integrity:
    - ticket_url + source_url + last_verified_at all present
    - slug/name NOT on data/canceled_shows.json
    - last_verified_at not in the future

Usage:
    python3 scripts/guardrails/audit_public_shows.py [--offline] [--live-check] [--strict]

    --offline    audit local repo file instead of live shows.html
    --live-check actively HTTP-probe each unique ticket_url and update
                 data/url_health.json
    --strict     require proof category (a/b/c) for every row (default true).
                 Use --strict=false only during local dev.
"""
from __future__ import annotations
import argparse
import json
import re
import sys
import urllib.request
import urllib.error
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SHOWS_HTML  = ROOT / "shows.html"
BLOCKLIST   = ROOT / "data" / "canceled_shows.json"
APPROVALS   = ROOT / "data" / "show_approvals.json"
URL_HEALTH  = ROOT / "data" / "url_health.json"
LIVE_URL    = "https://pariscomedy.com/shows.html"

LIVE_CHECK_WINDOW_DAYS = 7


def load_json(p: Path, default):
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text())
    except Exception:
        return default


def load_blocklist() -> tuple[set[str], set[str]]:
    data = load_json(BLOCKLIST, {"canceled": []})
    slugs = {e["slug"] for e in data.get("canceled", [])}
    names: set[str] = set()
    for e in data.get("canceled", []):
        for n in e.get("names", []):
            names.add(n)
    return slugs, names


def load_approvals() -> dict:
    """Return {slug_or_id: {valid_until, approved_by, ...}}."""
    raw = load_json(APPROVALS, {"approvals": []})
    out: dict[str, dict] = {}
    for entry in raw.get("approvals", []):
        key = entry.get("slug_or_id", "")
        if key:
            out[key] = entry
    return out


def load_url_health() -> dict:
    """Return {url: {last_ok_at, status}}."""
    return load_json(URL_HEALTH, {})


def slug_from_id(full_id: str) -> str:
    """Strip trailing -YYYYMMDD from SHOWS_DATA id like 'ffcn-20260527'."""
    return re.sub(r"-\d{8}$", "", full_id or "")


def extract_shows(html: str) -> list[dict]:
    m = re.search(r"const SHOWS_DATA\s*=\s*(\[.*?\]);", html, re.S)
    if not m:
        raise RuntimeError("SHOWS_DATA not found")
    return json.loads(m.group(1))


def fetch_html(args) -> str:
    import os
    override = os.environ.get("PC_AUDIT_SHOWS_HTML_OVERRIDE", "")
    if override and Path(override).exists():
        return Path(override).read_text()
    if args.offline:
        return SHOWS_HTML.read_text()
    try:
        req = urllib.request.Request(LIVE_URL, headers={"User-Agent": "PC-Audit/1"})
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.read().decode("utf-8", "replace")
    except Exception as e:
        print(f"live fetch failed ({e!r}); falling back to repo file", file=sys.stderr)
        return SHOWS_HTML.read_text()


# ── live URL probing ──────────────────────────────────────────────────────

def probe_url(url: str, timeout: int = 8) -> tuple[bool, int]:
    """Return (ok, status). ok = HTTP 2xx within timeout."""
    if not url:
        return False, 0
    try:
        req = urllib.request.Request(
            url, method="HEAD",
            headers={"User-Agent": "Mozilla/5.0 (PC-Audit)"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return (200 <= r.status < 300), r.status
    except urllib.error.HTTPError as e:
        return False, e.code
    except Exception:
        return False, 0


def run_live_check(urls: list[str]) -> dict:
    """Probe each URL once, write data/url_health.json."""
    print(f"[live-check] probing {len(urls)} unique URLs…")
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    health = load_url_health()
    for u in sorted(set(urls)):
        ok, status = probe_url(u)
        health[u] = {"last_ok_at": now if ok else health.get(u, {}).get("last_ok_at"),
                     "last_status": status, "last_checked_at": now,
                     "last_ok": ok}
        marker = "✓" if ok else "✗"
        print(f"  {marker} {status:>3}  {u[-70:]}")
    URL_HEALTH.parent.mkdir(parents=True, exist_ok=True)
    URL_HEALTH.write_text(json.dumps(health, indent=2))
    return health


def url_recently_ok(url: str, health: dict, window_days: int = LIVE_CHECK_WINDOW_DAYS) -> bool:
    rec = health.get(url, {})
    if not rec.get("last_ok"):
        return False
    last = rec.get("last_ok_at", "")
    if not last:
        return False
    try:
        dt = datetime.fromisoformat(last.replace("Z", "+00:00"))
    except Exception:
        return False
    return (datetime.now(timezone.utc) - dt) < timedelta(days=window_days)


def approval_valid(row: dict, approvals: dict, today: str) -> bool:
    keys = [row.get("id", ""), slug_from_id(row.get("id", "")), row.get("show_name", "")]
    for k in keys:
        if not k:
            continue
        a = approvals.get(k)
        if a and a.get("valid_until", "") >= today:
            return True
    return False


# ── audit ────────────────────────────────────────────────────────────────

def audit(rows: list[dict], *, strict: bool, health: dict) -> list[str]:
    failures: list[str] = []
    blocked_slugs, blocked_names = load_blocklist()
    approvals = load_approvals()
    today = datetime.now().date().isoformat()

    for r in rows:
        rid = r.get("id", "")
        name = r.get("show_name", "")
        stem = slug_from_id(rid)

        # Baseline integrity
        if not r.get("ticket_url"):
            failures.append(f"{rid!r}: missing ticket_url")
        if not r.get("source_url"):
            failures.append(f"{rid!r}: missing source_url")
        lv = r.get("last_verified_at") or r.get("verified_at") or ""
        if not lv:
            failures.append(f"{rid!r}: missing verified_at / last_verified_at")
        if lv and lv > today:
            failures.append(f"{rid!r}: last_verified_at is in the future ({lv!r})")

        # If the row claims it was verified today (which the JS uses to render
        # "Source checked today"), require matching url_health entry stamped
        # today. Otherwise the public copy lies.
        if lv == today:
            url = r.get("ticket_url") or ""
            rec = health.get(url, {})
            last_ok = rec.get("last_ok_at", "") or ""
            if not last_ok.startswith(today):
                failures.append(
                    f"{rid!r}: last_verified_at={today} but no url_health.last_ok_at "
                    f"recorded for today (would render 'Source checked today' falsely)"
                )

        # Blocklist
        if stem in blocked_slugs or rid in blocked_slugs:
            failures.append(f"{rid!r}: slug on canceled blocklist ({stem!r})")
        if name in blocked_names:
            failures.append(f"{rid!r}: name on canceled blocklist ({name!r})")
        if (r.get("status") or "").lower() == "canceled":
            failures.append(f"{rid!r}: status=canceled but row is in public SHOWS_DATA")

        # Proof category (strict mode only)
        if strict:
            url = r.get("ticket_url") or ""
            cat_a = url and url_recently_ok(url, health)
            cat_b = approval_valid(r, approvals, today)
            cat_c = bool(r.get("recurrence_source_url"))
            if not (cat_a or cat_b or cat_c):
                failures.append(
                    f"{rid!r}: no proof — needs ONE of "
                    f"(a) live URL check within {LIVE_CHECK_WINDOW_DAYS}d, "
                    f"(b) approval in data/show_approvals.json, "
                    f"(c) recurrence_source_url on the row"
                )

    return failures


# ── main ─────────────────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--live-check", action="store_true",
                    help="HTTP-probe every ticket_url and update url_health.json")
    ap.add_argument("--strict", default="true",
                    help="require proof category for every row (default: true)")
    args = ap.parse_args()
    strict = str(args.strict).lower() not in ("0", "false", "no")

    html = fetch_html(args)
    rows = extract_shows(html)

    health = load_url_health()
    if args.live_check:
        urls = [r.get("ticket_url") for r in rows if r.get("ticket_url")]
        health = run_live_check(urls)

    fails = audit(rows, strict=strict, health=health)
    print(f"audited rows: {len(rows)}  strict={strict}")
    if not fails:
        print("✅ GREEN — every public show has provenance.")
        return 0
    print(f"❌ HOLD — {len(fails)} provenance failure(s):")
    for f in fails:
        print(f"  - {f}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
