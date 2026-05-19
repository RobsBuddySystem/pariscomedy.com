#!/usr/bin/env python3
"""
Stage 07: Export validated events to shows.json / review_queue.json.

Rules:
  - Shows are NEVER deleted from data/shows.json, only marked is_archived=true
  - Comedians in data/comedians.json are NEVER deleted, only active=false added
  - 'high' tier → merge into data/shows.json, then regenerate data/shows_generated.json
  - 'review' tier → write to pipeline/output/review_queue.json
  - 'reject' tier → log only (name + reason)

Merge rule: if existing record has same Eventbrite ID, update fields but preserve is_archived.
After merge, call generate_instances.py for recurring shows.

Input:  pipeline/output/validated.json
Output: data/shows.json (updated)
        data/shows_generated.json (regenerated)
        pipeline/output/review_queue.json (written)
        pipeline/output/metrics_YYYYMMDD.json (daily metrics)
"""

import sys
import json
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

REPO_ROOT = Path(__file__).resolve().parents[2]
INPUT_PATH = REPO_ROOT / "pipeline" / "output" / "validated.json"
SHOWS_PATH = REPO_ROOT / "data" / "shows.json"
SHOWS_GENERATED_PATH = REPO_ROOT / "data" / "shows_generated.json"
REVIEW_QUEUE_PATH = REPO_ROOT / "pipeline" / "output" / "review_queue.json"

PARIS_TZ = ZoneInfo("Europe/Paris")

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)


def load_json(path: Path, default) -> any:
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return default


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def pipeline_show_to_data_show(ev: dict) -> dict:
    """
    Convert a pipeline event dict to the shows.json schema
    (matches the format used in data/shows.json).

    NOTE: Shows discovered by the pipeline are one-off events, not recurring.
    They store the Eventbrite ID in 'id' and the booking URL in 'url'.
    """
    return {
        "id": ev.get("id"),
        "name": ev.get("name"),
        "venue": ev.get("venue_name"),  # raw; admin can link to venues.json slug later
        "url": ev.get("url"),
        "langs": [ev.get("language", "en")] if ev.get("language") not in (None, "unknown") else [],
        "start_date": ev.get("start_date"),
        "end_date": None,
        "recurrence": "",
        "description": ev.get("description") or "",
        "cover_image": "",
        "source": ev.get("source", "pipeline"),
        "comics": [],
        "last_seen": datetime.now(tz=PARIS_TZ).isoformat(),
        "is_archived": False,
        "_pipeline_confidence": ev.get("confidence"),
        "_pipeline_type": ev.get("type"),
        "_pipeline_is_recurring": ev.get("is_recurring", False),
        "_freshness_checked": datetime.now(tz=PARIS_TZ).isoformat(),
        "source_url": ev.get("source_url"),
        "verified_at": None,  # not yet manually verified
    }


def merge_into_shows(existing_shows: list[dict], new_shows: list[dict]) -> tuple[list[dict], int, int]:
    """
    Merge new pipeline shows into existing shows list.
    Returns (merged_list, added_count, updated_count).
    """
    # Index existing by ID
    index: dict[str, int] = {}
    for i, show in enumerate(existing_shows):
        if show.get("id"):
            index[str(show["id"])] = i

    added = 0
    updated = 0

    for new_show in new_shows:
        ev_id = str(new_show.get("id", ""))
        if ev_id and ev_id in index:
            # Update existing record, preserve is_archived
            existing = existing_shows[index[ev_id]]
            was_archived = existing.get("is_archived", False)
            existing.update(new_show)
            existing["is_archived"] = was_archived  # preserve archival status
            updated += 1
        else:
            existing_shows.append(new_show)
            if ev_id:
                index[ev_id] = len(existing_shows) - 1
            added += 1

    return existing_shows, added, updated


def regenerate_instances() -> bool:
    """Run generate_instances.py to refresh shows_generated.json."""
    script = REPO_ROOT / "generate_instances.py"
    if not script.exists():
        log.warning(f"[EXPORT] generate_instances.py not found at {script}")
        return False
    try:
        result = subprocess.run(
            [sys.executable, str(script)],
            capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=30
        )
        if result.returncode == 0:
            log.info(f"[EXPORT] generate_instances.py: {result.stdout.strip()}")
            return True
        else:
            log.error(f"[EXPORT] generate_instances.py error: {result.stderr.strip()}")
            return False
    except Exception as exc:
        log.error(f"[EXPORT] generate_instances.py exception: {exc}")
        return False


def main():
    if not INPUT_PATH.exists():
        log.error(f"[EXPORT] Input not found: {INPUT_PATH}. Run stage 06 first.")
        sys.exit(1)

    with open(INPUT_PATH) as f:
        events = json.load(f)

    now_paris = datetime.now(tz=PARIS_TZ)
    today_str = now_paris.strftime("%Y%m%d")

    # Partition by tier
    high = [ev for ev in events if ev.get("publish_tier") == "high"]
    review = [ev for ev in events if ev.get("publish_tier") == "review"]
    rejected = [ev for ev in events if ev.get("publish_tier") == "reject"]

    log.info(f"[EXPORT] Tiers: high={len(high)} review={len(review)} reject={len(rejected)}")

    # ── HIGH tier: merge into shows.json ──────────────────────────────────────
    existing_shows = load_json(SHOWS_PATH, [])
    new_data_shows = [pipeline_show_to_data_show(ev) for ev in high]
    merged, added, updated = merge_into_shows(existing_shows, new_data_shows)
    save_json(SHOWS_PATH, merged)
    log.info(f"[EXPORT] shows.json: +{added} added, ~{updated} updated ({len(merged)} total)")

    # Regenerate shows_generated.json (recurring instances)
    regenerated = regenerate_instances()
    if not regenerated:
        log.warning("[EXPORT] Could not regenerate shows_generated.json — manual run needed")

    # ── REVIEW tier: write review_queue.json ──────────────────────────────────
    review_payload = {
        "generated": now_paris.isoformat(),
        "count": len(review),
        "shows": [
            {
                "id": ev.get("id"),
                "name": ev.get("name"),
                "start_date": ev.get("start_date"),
                "venue_name": ev.get("venue_name"),
                "url": ev.get("url"),
                "confidence": ev.get("confidence"),
                "type": ev.get("type"),
                "language": ev.get("language"),
                "is_recurring": ev.get("is_recurring"),
                "description": (ev.get("description") or "")[:200],
                "source": ev.get("source"),
                "_llm_method": ev.get("_llm_method"),
                "_validation_errors": ev.get("_validation_errors", []),
            }
            for ev in review
        ],
    }
    save_json(REVIEW_QUEUE_PATH, review_payload)
    log.info(f"[EXPORT] review_queue.json: {len(review)} shows queued for review")

    # ── REJECT tier: log only ─────────────────────────────────────────────────
    for ev in rejected:
        reasons = ev.get("_validation_errors") or ["low confidence"]
        log.debug(f"[EXPORT] REJECT: {ev.get('name')!r} — {', '.join(reasons)}")

    # ── Daily metrics ─────────────────────────────────────────────────────────
    metrics = {
        "date": today_str,
        "generated_at": now_paris.isoformat(),
        "input_count": len(events),
        "high_count": len(high),
        "review_count": len(review),
        "reject_count": len(rejected),
        "shows_added": added,
        "shows_updated": updated,
        "shows_total": len(merged),
        "shows_generated_refreshed": regenerated,
        "reject_names": [ev.get("name") for ev in rejected[:20]],  # first 20 for debug
    }
    metrics_path = REPO_ROOT / "pipeline" / "output" / f"metrics_{today_str}.json"
    save_json(metrics_path, metrics)

    # Print metrics summary (captured in run_pipeline.sh log)
    print("\n── Daily Pipeline Metrics ─────────────────────────────────")
    print(f"  Date:         {today_str}")
    print(f"  Input events: {metrics['input_count']}")
    print(f"  HIGH (auto):  {metrics['high_count']}  → shows.json (+{added} new, ~{updated} updated)")
    print(f"  REVIEW:       {metrics['review_count']}  → review_queue.json")
    print(f"  REJECT:       {metrics['reject_count']}  (logged)")
    print(f"  shows.json total: {metrics['shows_total']}")
    print(f"  shows_generated refreshed: {regenerated}")
    print("────────────────────────────────────────────────────────────\n")

    log.info(f"[EXPORT] Metrics written to {metrics_path}")


if __name__ == "__main__":
    main()
