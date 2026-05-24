#!/usr/bin/env python3
"""CRM safety guardrails — no contact data leaks into the public repo,
no API tokens in frontend JS, raw archives outside web root.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CRM_RAW_DIR = Path.home() / ".openclaw" / "crm" / "raw-archives"
CRM_BACKUP_DIR = Path.home() / ".openclaw" / "crm" / "backups"

FORBIDDEN_TOKEN_PATTERNS = [
    re.compile(r"\bsumup_[A-Za-z0-9_]{12,}\b"),
    re.compile(r"\bsup_sk_[A-Za-z0-9]+\b"),
    re.compile(r"\bEVENTBRITE_API_KEY\s*=\s*['\"][A-Za-z0-9]{8,}['\"]"),
    re.compile(r"\beyJ[A-Za-z0-9_.\-]{20,}\b"),  # JWT
]
PUBLIC_GLOBS = ["*.html", "assets/**/*.js", "js/**/*.js"]


def main() -> int:
    failures: list[str] = []

    # 1. Raw archives must be outside the repo
    for path in CRM_RAW_DIR, CRM_BACKUP_DIR:
        if path.exists():
            try:
                path.relative_to(ROOT)
                failures.append(f"CRM archive inside repo: {path}")
            except ValueError:
                pass  # good — outside the repo

    # 2. Public files must not contain CSV-like contact lists
    csv_email_re = re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\s*,\s*[A-Za-z]+,\s*[A-Za-z]+")
    allowed_emails = {"payments@pariscomedy.com", "bio@pariscomedy.com"}
    for pat in PUBLIC_GLOBS:
        for f in ROOT.glob(pat):
            if "scripts/guardrails" in str(f):
                continue
            try:
                text = f.read_text(errors="replace")
            except Exception:
                continue
            for rx in FORBIDDEN_TOKEN_PATTERNS:
                if rx.search(text):
                    failures.append(f"public file {f.relative_to(ROOT)} contains API-token-shaped string")
            if csv_email_re.search(text):
                failures.append(f"public file {f.relative_to(ROOT)} appears to contain a CSV contact list")

    # 3. sitemap must not contain /api/ or /shows/<slug>?email= patterns
    sm = ROOT / "sitemap.xml"
    if sm.exists():
        text = sm.read_text()
        for needle in ("/api/", "/crm/", "@gmail.com", "@example.com"):
            if needle in text:
                failures.append(f"sitemap.xml contains forbidden: {needle!r}")

    # 4. No admin-crm contact dump in published HTML
    for f in (ROOT / "admin-crm.html",):
        if f.exists():
            text = f.read_text()
            # admin-crm.html must declare noindex
            if 'name="robots"' not in text or 'noindex' not in text:
                failures.append("admin-crm.html missing noindex meta tag")

    if failures:
        print(f"❌ {len(failures)} CRM safety failure(s):")
        for x in failures:
            print(f"  - {x}")
        return 1
    print("✅ CRM safety clean — no contact leaks, no tokens in frontend, archives outside repo")
    return 0


if __name__ == "__main__":
    sys.exit(main())
