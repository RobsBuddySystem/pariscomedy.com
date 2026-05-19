#!/usr/bin/env python3
"""
Stage 02: Normalize raw scraped events.

- Parse date strings to ISO 8601 with Europe/Paris timezone
- Clean venue names (strip whitespace, fix encoding)
- Fill missing fields with null
- Deduplicate by Eventbrite event ID

Input:  pipeline/output/raw_scraped.json
Output: pipeline/output/normalized.json
"""

import sys
import json
import re
import logging
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml
from dateutil import parser as dateutil_parser

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = REPO_ROOT / "pipeline" / "config.yml"
INPUT_PATH = REPO_ROOT / "pipeline" / "output" / "raw_scraped.json"
OUTPUT_PATH = REPO_ROOT / "pipeline" / "output" / "normalized.json"

PARIS_TZ = ZoneInfo("Europe/Paris")

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)


def load_config() -> dict:
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


def parse_date(raw: str | None) -> str | None:
    """Parse any date string to ISO 8601 with Europe/Paris offset."""
    if not raw:
        return None
    raw = raw.strip()
    # Already ISO 8601 with tz?
    if re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}", raw):
        try:
            dt = dateutil_parser.parse(raw)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=PARIS_TZ)
            return dt.isoformat()
        except Exception:
            pass
    # Try dateutil generic parse
    try:
        dt = dateutil_parser.parse(raw, fuzzy=True)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=PARIS_TZ)
        return dt.isoformat()
    except Exception:
        pass
    return None  # unparseable — stage 06 will filter


def clean_venue(raw: str | None) -> str | None:
    """Strip excess whitespace and fix common encoding artifacts."""
    if not raw:
        return None
    # Normalize whitespace
    v = re.sub(r"\s+", " ", raw).strip()
    # Fix common HTML entities that slip through
    v = v.replace("&amp;", "&").replace("&#39;", "'").replace("&quot;", '"')
    # Trim "· Paris" suffix that Eventbrite appends to venue names
    v = re.sub(r"\s*·\s*Paris\s*$", "", v, flags=re.IGNORECASE)
    v = re.sub(r",?\s*Paris\s*\d*\s*$", "", v, flags=re.IGNORECASE)
    return v or None


def normalize_event(raw: dict) -> dict:
    return {
        "id": raw.get("id"),
        "name": (raw.get("name") or "").strip() or None,
        "url": (raw.get("url") or "").strip() or None,
        "start_date": parse_date(raw.get("start_date")),
        "venue_name": clean_venue(raw.get("venue_raw")),
        "description": (raw.get("description_raw") or "").strip() or None,
        "source": raw.get("source"),
        "source_url": raw.get("source_url"),
        "scraped_at": raw.get("scraped_at"),
        # Fields populated by later stages
        "is_comedy": None,
        "confidence": None,
        "type": None,
        "language": None,
        "is_recurring": None,
        "has_specific_date": raw.get("start_date") is not None,
        "publish_tier": None,
        "is_archived": False,
    }


def main():
    if not INPUT_PATH.exists():
        log.error(f"[NORMALIZE] Input not found: {INPUT_PATH}. Run stage 01 first.")
        sys.exit(1)

    with open(INPUT_PATH) as f:
        raw_events = json.load(f)

    log.info(f"[NORMALIZE] Processing {len(raw_events)} raw events")

    normalized: list[dict] = []
    seen_ids: set[str] = set()
    skipped_dupes = 0
    skipped_no_name = 0

    for raw in raw_events:
        ev_id = raw.get("id")
        if not ev_id:
            skipped_no_name += 1
            continue

        if ev_id in seen_ids:
            skipped_dupes += 1
            continue
        seen_ids.add(ev_id)

        norm = normalize_event(raw)
        if not norm["name"]:
            skipped_no_name += 1
            continue

        normalized.append(norm)

    log.info(
        f"[NORMALIZE] {len(normalized)} normalized "
        f"(removed {skipped_dupes} dupes, {skipped_no_name} nameless)"
    )

    with open(OUTPUT_PATH, "w") as f:
        json.dump(normalized, f, indent=2, ensure_ascii=False)

    log.info(f"[NORMALIZE] Written to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
