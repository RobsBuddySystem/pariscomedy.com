#!/usr/bin/env python3
"""
Stage 06: Schema validation and date filtering.

For 'high' tier:
  - Verify required fields: name, start_date, url
  - Filter out shows where start_date is in the past (before today Paris time)
  - Flag shows where start_date > lookahead_days from now

For all tiers:
  - Log validation errors

Input:  pipeline/output/classified.json
Output: pipeline/output/validated.json
"""

import sys
import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = REPO_ROOT / "pipeline" / "config.yml"
INPUT_PATH = REPO_ROOT / "pipeline" / "output" / "classified.json"
OUTPUT_PATH = REPO_ROOT / "pipeline" / "output" / "validated.json"

PARIS_TZ = ZoneInfo("Europe/Paris")

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

REQUIRED_HIGH = {"name", "start_date", "url"}


def load_config() -> dict:
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


def parse_dt(iso: str | None) -> datetime | None:
    if not iso:
        return None
    try:
        from dateutil import parser as dp
        dt = dp.parse(iso)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=PARIS_TZ)
        return dt
    except Exception:
        return None


def validate_event(ev: dict, now_paris: datetime, lookahead: datetime) -> tuple[dict, list[str]]:
    """Returns (validated_event, list_of_errors)."""
    errors: list[str] = []
    tier = ev.get("publish_tier", "reject")

    if tier == "high":
        missing = [f for f in REQUIRED_HIGH if not ev.get(f)]
        if missing:
            errors.append(f"missing required fields: {missing}")
            ev["publish_tier"] = "review"  # demote to review

        start_dt = parse_dt(ev.get("start_date"))
        if start_dt:
            if start_dt < now_paris:
                errors.append(f"start_date {ev['start_date']!r} is in the past")
                ev["publish_tier"] = "reject"  # past shows → reject
            elif start_dt > lookahead:
                ev["_future_only"] = True
        else:
            if ev.get("start_date"):
                errors.append(f"start_date unparseable: {ev['start_date']!r}")
                ev["publish_tier"] = "review"

    ev["_validation_errors"] = errors
    return ev, errors


def main():
    if not INPUT_PATH.exists():
        log.error(f"[VALIDATE] Input not found: {INPUT_PATH}. Run stage 05 first.")
        sys.exit(1)

    with open(INPUT_PATH) as f:
        events = json.load(f)

    config = load_config()
    pipeline_cfg = config.get("pipeline", {})
    lookahead_days = pipeline_cfg.get("lookahead_days", 60)

    now_paris = datetime.now(tz=PARIS_TZ)
    lookahead = now_paris + timedelta(days=lookahead_days)

    log.info(f"[VALIDATE] Validating {len(events)} events (now={now_paris.date()}, lookahead={lookahead.date()})")

    validated = []
    error_count = 0
    demoted = 0
    past_rejected = 0

    for ev in events:
        original_tier = ev.get("publish_tier")
        ev_out, errors = validate_event(ev, now_paris, lookahead)

        if errors:
            error_count += len(errors)
            for err in errors:
                log.debug(f"[VALIDATE] '{ev.get('name')}': {err}")

        new_tier = ev_out.get("publish_tier")
        if new_tier != original_tier:
            if new_tier == "reject" and "past" in " ".join(errors):
                past_rejected += 1
            else:
                demoted += 1

        validated.append(ev_out)

    tiers = {"high": 0, "review": 0, "reject": 0}
    for ev in validated:
        tiers[ev.get("publish_tier", "reject")] += 1

    log.info(
        f"[VALIDATE] {error_count} errors found, {past_rejected} past-date rejected, "
        f"{demoted} demoted. Final: high={tiers['high']} review={tiers['review']} reject={tiers['reject']}"
    )

    with open(OUTPUT_PATH, "w") as f:
        json.dump(validated, f, indent=2, ensure_ascii=False)

    log.info(f"[VALIDATE] Written to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
