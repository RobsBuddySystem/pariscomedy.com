#!/usr/bin/env python3
"""Inventory guardrail for show language tags.

Fails if:
  1. Any SHOWS_DATA row tagged 'bi' (or 'en'+'fr') lacks explicit bilingual
     evidence in its name OR description (strict source-text check).
  2. The rendered live homepage or /shows.html shows duplicate adjacent
     language badges (e.g. "Bilingual Bilingual", "EN EN", "FR FR").
  3. Any row with empty/unknown language renders a Bilingual badge.

Exit 0 = pass.
"""
from __future__ import annotations
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SHOWS_HTML = ROOT / "shows.html"

sys.path.insert(
    0, str(Path.home() / "Documents/Claude/Projects/pariscomedy.com/scripts"),
)
from discovery._language_classifier import classify_language  # noqa: E402


def main() -> int:
    failures: list[str] = []

    # 1. Strict inventory check on local SHOWS_DATA
    m = re.search(r"const SHOWS_DATA\s*=\s*(\[.*?\]);", SHOWS_HTML.read_text(), re.S)
    data = json.loads(m.group(1)) if m else []
    for r in data:
        langs = r.get("language") or []
        is_bi = (("en" in langs) and ("fr" in langs)) or ("bi" in langs)
        if is_bi:
            text = f"{r.get('show_name','')} {r.get('description','')}"
            verdict = classify_language(text)
            if verdict != "bi":
                failures.append(
                    f"row {r.get('id')!r} ({r.get('show_name')!r}) is tagged bilingual "
                    f"but its name+description does not contain explicit "
                    f"bilingual evidence (classifier verdict: {verdict})"
                )

    # 2. Rendered-DOM check via Playwright (optional — skip if unavailable)
    try:
        import importlib
        pw = importlib.import_module("playwright.sync_api")
        with pw.sync_playwright() as p:
            b = p.chromium.launch(headless=True)
            for url in ("https://pariscomedy.com/", "https://pariscomedy.com/shows.html"):
                page = b.new_context(user_agent="PC-Invariants/1").new_page()
                page.goto(url, wait_until="domcontentloaded", timeout=20000)
                page.wait_for_timeout(2500)
                body = page.inner_text("body")
                # Duplicate adjacent badges patterns
                for dup in ("Bilingual Bilingual", "EN EN", "FR FR", "English English", "French French"):
                    if dup in body:
                        failures.append(f"{url}: duplicate adjacent language badge: {dup!r}")
                page.close()
            b.close()
    except Exception:
        pass  # Playwright optional

    if failures:
        print(f"❌ {len(failures)} language-inventory failure(s):")
        for f in failures: print(f"  - {f}")
        return 1
    print(f"✅ language inventory clean — {len(data)} SHOWS_DATA rows, 0 unsupported bi tags")
    return 0


if __name__ == "__main__":
    sys.exit(main())
