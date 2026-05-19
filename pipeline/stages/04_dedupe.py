#!/usr/bin/env python3
"""
Stage 04: Deduplicate events by name+date+venue fingerprint.

Fingerprint: MD5(normalize(name) + "|" + date[:10] + "|" + normalize(venue))
When duplicates exist, keep the highest-confidence record.

Input:  pipeline/output/llm_classified.json
Output: pipeline/output/deduped.json
"""

import sys
import json
import hashlib
import re
import logging
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
INPUT_PATH = REPO_ROOT / "pipeline" / "output" / "llm_classified.json"
OUTPUT_PATH = REPO_ROOT / "pipeline" / "output" / "deduped.json"

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)


def normalize_text(s: str | None) -> str:
    if not s:
        return ""
    # lowercase, collapse whitespace, strip punctuation
    s = s.lower().strip()
    s = re.sub(r"[^\w\s]", "", s)
    s = re.sub(r"\s+", " ", s)
    return s


def fingerprint(ev: dict) -> str:
    name_norm = normalize_text(ev.get("name"))
    date_part = (ev.get("start_date") or "")[:10]
    venue_norm = normalize_text(ev.get("venue_name"))
    raw = f"{name_norm}|{date_part}|{venue_norm}"
    return hashlib.md5(raw.encode()).hexdigest()


def main():
    if not INPUT_PATH.exists():
        log.error(f"[DEDUPE] Input not found: {INPUT_PATH}. Run stage 03 first.")
        sys.exit(1)

    with open(INPUT_PATH) as f:
        events = json.load(f)

    log.info(f"[DEDUPE] Processing {len(events)} events")

    # Group by fingerprint
    groups: dict[str, list[dict]] = {}
    for ev in events:
        fp = fingerprint(ev)
        groups.setdefault(fp, []).append(ev)

    # Also deduplicate by Eventbrite ID (same event scraped from multiple pages)
    eb_id_seen: set[str] = set()
    deduped: list[dict] = []

    for fp, group in groups.items():
        # Pick highest-confidence record from each fingerprint group
        best = max(group, key=lambda e: e.get("confidence") or 0.0)

        # Check EB ID dedup
        eb_id = best.get("id")
        if eb_id and eb_id in eb_id_seen:
            continue
        if eb_id:
            eb_id_seen.add(eb_id)

        # Attach fingerprint for downstream debugging
        best["_fingerprint"] = fp
        best["_dupe_count"] = len(group) - 1
        deduped.append(best)

    removed = len(events) - len(deduped)
    log.info(f"[DEDUPE] Removed {removed} duplicates, {len(deduped)} unique remain")

    with open(OUTPUT_PATH, "w") as f:
        json.dump(deduped, f, indent=2, ensure_ascii=False)

    log.info(f"[DEDUPE] Written to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
