#!/usr/bin/env python3
"""
Stage 05: Confidence scoring and publish tier classification.

Combines LLM confidence with keyword signals into a final score.

Scoring formula:
  base = llm.confidence (0.0–1.0)
  + 0.10 if name contains comedy signal word
  + 0.05 if has verified Eventbrite URL
  + 0.05 if has specific start_date
  - 0.20 if name contains exclusion word
  - 0.10 if description is empty
  clamped to [0.0, 1.0]

Tiers:
  high   (>= 0.80): is_comedy=True AND confidence >= 0.80 AND has start_date
  review (0.50–0.79): is_comedy=True AND confidence 0.50–0.79
  reject (< 0.50):  everything else

Input:  pipeline/output/deduped.json
Output: pipeline/output/classified.json
"""

import sys
import json
import logging
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = REPO_ROOT / "pipeline" / "config.yml"
INPUT_PATH = REPO_ROOT / "pipeline" / "output" / "deduped.json"
OUTPUT_PATH = REPO_ROOT / "pipeline" / "output" / "classified.json"

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)


def load_config() -> dict:
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


def adjust_confidence(ev: dict, config: dict) -> float:
    """Apply keyword adjustments on top of LLM base confidence."""
    signals = config.get("comedy_signals", {})
    include = [s.lower() for s in signals.get("include", [])]
    exclude = [s.lower() for s in signals.get("exclude", [])]

    thresholds = config.get("confidence", {})
    auto_pub = thresholds.get("auto_publish_threshold", 0.80)
    review = thresholds.get("review_threshold", 0.50)

    base = float(ev.get("confidence") or 0.0)
    name = (ev.get("name") or "").lower()
    description = (ev.get("description") or "").lower()
    url = (ev.get("url") or "")

    score = base

    # Keyword bonuses
    if any(s in name for s in include):
        score += 0.10

    if "eventbrite.com/e/" in url or "eventbrite.fr/e/" in url:
        score += 0.05

    if ev.get("start_date") or ev.get("has_specific_date"):
        score += 0.05

    # Penalties
    if any(s in name for s in exclude):
        score -= 0.20

    if not description:
        score -= 0.10

    return round(min(1.0, max(0.0, score)), 4)


def classify_event(ev: dict, config: dict) -> dict:
    thresholds = config.get("confidence", {})
    auto_pub = thresholds.get("auto_publish_threshold", 0.80)
    review_min = thresholds.get("review_threshold", 0.50)

    final_score = adjust_confidence(ev, config)
    is_comedy = bool(ev.get("is_comedy", False))
    has_date = bool(ev.get("start_date"))

    if is_comedy and final_score >= auto_pub and has_date:
        tier = "high"
    elif is_comedy and final_score >= review_min:
        tier = "review"
    else:
        tier = "reject"

    ev_out = {**ev, "confidence": final_score, "publish_tier": tier}
    return ev_out


def main():
    if not INPUT_PATH.exists():
        log.error(f"[CLASSIFY] Input not found: {INPUT_PATH}. Run stage 04 first.")
        sys.exit(1)

    with open(INPUT_PATH) as f:
        events = json.load(f)

    config = load_config()
    log.info(f"[CLASSIFY] Scoring {len(events)} events")

    classified = [classify_event(ev, config) for ev in events]

    tiers = {"high": 0, "review": 0, "reject": 0}
    for ev in classified:
        tiers[ev["publish_tier"]] += 1

    log.info(
        f"[CLASSIFY] high={tiers['high']} review={tiers['review']} reject={tiers['reject']}"
    )

    with open(OUTPUT_PATH, "w") as f:
        json.dump(classified, f, indent=2, ensure_ascii=False)

    log.info(f"[CLASSIFY] Written to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
