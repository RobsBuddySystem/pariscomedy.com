#!/usr/bin/env python3
"""Regression test: prove the provenance guardrail blocks manual SHOWS_DATA edits.

Builds a temporary copy of shows.html with a manually fabricated row that has
no ticket_url health entry, no signed approval, and no recurrence_source_url.
Runs audit_public_shows.py against the temp file and asserts it exits non-zero.

This is the test that explicitly demonstrates "manual SHOWS_DATA edits are
blocked by tests" (criterion #4 of the page-fixed checklist).

Exit 0 = test passed (guardrail blocks bad row).
Exit 1 = test failed (guardrail let a bad row through).
"""
from __future__ import annotations
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SHOWS_HTML = ROOT / "shows.html"
AUDIT = ROOT / "scripts" / "guardrails" / "audit_public_shows.py"

BAD_ROW = {
    "id": "fake-fabricated-20260601",
    "show_name": "Fabricated Show That Does Not Exist",
    "date": "2026-06-01",
    "day": "Monday",
    "start_time": "20:00",
    "venue": "Nowhere",
    "language": ["en"],
    "show_type": "showcase",
    "emoji": "🤥",
    "description": "This row was injected by a unit test to verify the guardrail.",
    # No ticket_url, no source_url, no last_verified_at, no approval,
    # no recurrence_source_url. The audit MUST fail.
}


def main() -> int:
    src = SHOWS_HTML.read_text()
    m = re.search(r"(const SHOWS_DATA\s*=\s*)(\[.*?\])(;)", src, re.S)
    if not m:
        print("test: SHOWS_DATA marker not found — cannot run test")
        return 1
    rows = json.loads(m.group(2))
    rows.append(BAD_ROW)
    bad_arr = json.dumps(rows, ensure_ascii=False, indent=2)
    bad_src = src[:m.start()] + m.group(1) + bad_arr + m.group(3) + src[m.end():]

    with tempfile.TemporaryDirectory() as d:
        # The audit script resolves paths relative to its own location;
        # to mock the file we have to point it at a temp shows.html.
        # Easiest: monkey-patch SHOWS_HTML via env var.
        temp_html = Path(d) / "shows.html"
        temp_html.write_text(bad_src)
        # Invoke the audit with a one-off env override.
        env = {"PYTHONPATH": str(ROOT), "PC_AUDIT_SHOWS_HTML_OVERRIDE": str(temp_html)}
        proc = subprocess.run(
            ["python3", str(AUDIT), "--offline", "--strict=true"],
            capture_output=True, text=True, timeout=20,
            env={**__import__("os").environ, **env},
        )

    expected_failure = proc.returncode != 0
    found_bad_id = "fake-fabricated" in proc.stdout
    if expected_failure and found_bad_id:
        print("✅ TEST PASSED — audit_public_shows correctly rejected the fabricated row")
        return 0
    print("❌ TEST FAILED — guardrail did NOT block the bad row")
    print(f"  exit code: {proc.returncode} (expected non-zero)")
    print(f"  bad id in stdout: {found_bad_id}")
    print("  --- audit stdout ---")
    print(proc.stdout)
    return 1


if __name__ == "__main__":
    sys.exit(main())
