#!/usr/bin/env python3
"""P5.AUTOMATION.1 — daily proof package aggregator.

Runs three checks in sequence and writes a combined JSON to
``logs/daily-proof-{ISO}.json``:

  1. freshness_verify.py       — staleness + source reachability
  2. regression_guard.py       — forbidden strings, status sweep, nav, hreflang…
  3. generate_sitemap.py       — sitemap regeneration

Exit 0 if all PASS, 1 if any FAIL. stdlib only.
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "scripts"
LOGS = REPO / "logs"


def _run(cmd: list[str]) -> dict:
    proc = subprocess.run(
        cmd,
        cwd=str(REPO),
        capture_output=True,
        text=True,
    )
    return {
        "cmd": cmd,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def _section_status(result: dict, extra_fail_markers: tuple[str, ...] = ()) -> str:
    if result["returncode"] != 0:
        return "FAIL"
    for marker in extra_fail_markers:
        if marker in result["stdout"]:
            return "FAIL"
    return "PASS"


def main() -> int:
    LOGS.mkdir(parents=True, exist_ok=True)
    iso = _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_path = LOGS / f"daily-proof-{iso}.json"

    package: dict = {
        "iso": iso,
        "generated_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "sections": {},
        "failures": [],
    }

    # 1. freshness
    freshness = _run([sys.executable, str(SCRIPTS / "freshness_verify.py")])
    freshness_status = _section_status(freshness)
    audit_path = REPO / "data" / "freshness-audit.json"
    by_status: dict = {}
    if audit_path.exists():
        try:
            audit = json.loads(audit_path.read_text())
            by_status = audit.get("by_status", {})
        except Exception as e:  # noqa: BLE001
            package["failures"].append(f"freshness: audit unreadable: {e}")
            freshness_status = "FAIL"
    package["sections"]["freshness"] = {
        "status": freshness_status,
        "returncode": freshness["returncode"],
        "by_status": by_status,
        "stderr_tail": freshness["stderr"][-500:],
    }
    if freshness_status == "FAIL":
        package["failures"].append("freshness")

    # 2. regression guard
    regression = _run([sys.executable, str(SCRIPTS / "regression_guard.py")])
    # regression_guard prints `[FAIL]` per-check but may exit 0; treat any [FAIL] as failure
    has_fail = "[FAIL]" in regression["stdout"]
    regression_status = "FAIL" if (regression["returncode"] != 0 or has_fail) else "PASS"
    fail_lines = [
        line for line in regression["stdout"].splitlines() if line.startswith("[FAIL]")
    ]
    pass_lines = [
        line for line in regression["stdout"].splitlines() if line.startswith("[PASS]")
    ]
    package["sections"]["regression"] = {
        "status": regression_status,
        "returncode": regression["returncode"],
        "pass_count": len(pass_lines),
        "fail_count": len(fail_lines),
        "fail_lines": fail_lines,
        "summary_tail": regression["stdout"].splitlines()[-3:],
    }
    if regression_status == "FAIL":
        package["failures"].append("regression")

    # 3. sitemap regen
    sitemap = _run([sys.executable, str(SCRIPTS / "generate_sitemap.py")])
    sitemap_path = REPO / "sitemap.xml"
    sitemap_size = sitemap_path.stat().st_size if sitemap_path.exists() else 0
    url_count = 0
    if sitemap_path.exists():
        try:
            url_count = sitemap_path.read_text().count("<url>")
        except Exception:
            pass
    sitemap_status = _section_status(sitemap)
    package["sections"]["sitemap-size"] = {
        "status": sitemap_status,
        "returncode": sitemap["returncode"],
        "bytes": sitemap_size,
        "url_count": url_count,
        "stdout_tail": sitemap["stdout"].strip().splitlines()[-3:],
    }
    if sitemap_status == "FAIL":
        package["failures"].append("sitemap")

    out_path.write_text(json.dumps(package, indent=2, sort_keys=True))

    print(f"daily-proof: wrote {out_path}")
    for name, sec in package["sections"].items():
        print(f"  [{sec['status']}] {name}")
    if package["failures"]:
        print(f"daily-proof: FAILURES = {package['failures']}")
        return 1
    print("daily-proof: ALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
