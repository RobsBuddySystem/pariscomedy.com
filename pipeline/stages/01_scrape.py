#!/usr/bin/env python3
"""
Stage 01: Scrape comedy events from Eventbrite Paris pages.

Output: pipeline/output/raw_scraped.json
Log:    pipeline/logs/pipeline_*.log (via run_pipeline.sh)

Usage:
  python3 pipeline/stages/01_scrape.py
  python3 pipeline/stages/01_scrape.py --dry-run   # uses fixture cache if present
"""

import sys
import json
import hashlib
import argparse
import re
import time
import logging
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup
import yaml

# ── Paths ─────────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = REPO_ROOT / "pipeline" / "config.yml"
OUTPUT_PATH = REPO_ROOT / "pipeline" / "output" / "raw_scraped.json"
FIXTURE_PATH = REPO_ROOT / "pipeline" / "output" / "_fixture_raw_scraped.json"

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9,fr;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def load_config() -> dict:
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


def fingerprint(name: str, url: str) -> str:
    """Stable ID for dedup across runs."""
    raw = f"{name.lower().strip()}|{url.strip()}"
    return hashlib.md5(raw.encode()).hexdigest()[:12]


def parse_eventbrite_search_page(html: str, source_key: str, source_url: str) -> list[dict]:
    """
    Parse Eventbrite search results page.
    Targets <article> event cards — stable across EB's current layout.
    Falls back to JSON-LD embedded in the page if cards not found.
    """
    soup = BeautifulSoup(html, "html.parser")
    events = []

    # Strategy 1: article cards (Eventbrite's primary listing layout)
    cards = soup.find_all("article", attrs={"data-testid": True})
    if not cards:
        # Try alternative selectors used in some EB locale variants
        cards = soup.find_all("article", class_=re.compile(r"search-event-card|event-card"))

    for card in cards:
        try:
            # Title
            title_el = (
                card.find("h2")
                or card.find("h3")
                or card.find(attrs={"data-testid": re.compile(r"event-title|title")})
            )
            name = title_el.get_text(strip=True) if title_el else None
            if not name:
                continue

            # URL
            link_el = card.find("a", href=True)
            event_url = link_el["href"] if link_el else ""
            if event_url and not event_url.startswith("http"):
                event_url = "https://www.eventbrite.com" + event_url
            # Strip query params, keep clean URL
            event_url = event_url.split("?")[0]

            # Eventbrite event ID from URL
            eb_id_match = re.search(r"tickets-(\d+)$", event_url)
            eb_id = eb_id_match.group(1) if eb_id_match else fingerprint(name, event_url)

            # Date (raw string — normalized in stage 02)
            date_el = card.find("time") or card.find(attrs={"data-testid": re.compile(r"date|time")})
            date_raw = date_el.get_text(strip=True) if date_el else None
            if date_el and date_el.get("datetime"):
                date_raw = date_el["datetime"]

            # Venue
            # EB cards show location as "Venue · City" or just city
            venue_candidates = card.find_all(attrs={"data-testid": re.compile(r"venue|location|address")})
            if venue_candidates:
                venue_raw = venue_candidates[0].get_text(strip=True)
            else:
                # Fallback: look for small/p tags near the bottom of the card
                venue_raw = None
                for el in card.find_all(["p", "small", "span"]):
                    txt = el.get_text(strip=True)
                    if txt and "Paris" in txt and txt != name:
                        venue_raw = txt
                        break

            # Description / snippet
            desc_el = card.find(attrs={"data-testid": re.compile(r"description|summary|snippet")})
            if not desc_el:
                # Try aria-label on the card itself
                desc_el = card.find(attrs={"aria-label": True})
            description_raw = desc_el.get_text(strip=True) if desc_el else ""

            events.append({
                "id": eb_id,
                "name": name,
                "url": event_url,
                "start_date": date_raw,
                "venue_raw": venue_raw or "",
                "description_raw": description_raw,
                "source": source_key,
                "source_url": source_url,
                "scraped_at": datetime.utcnow().isoformat() + "Z",
            })

        except Exception as exc:
            log.warning(f"[SCRAPE] card parse error: {exc}")
            continue

    # Strategy 2: JSON-LD fallback (Eventbrite embeds structured data)
    if not events:
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string or "")
                items = data if isinstance(data, list) else [data]
                for item in items:
                    if item.get("@type") not in ("Event", "SocialEvent", "ComedyEvent"):
                        continue
                    name = item.get("name", "")
                    event_url = item.get("url", "")
                    eb_id_match = re.search(r"tickets-(\d+)$", event_url)
                    eb_id = eb_id_match.group(1) if eb_id_match else fingerprint(name, event_url)
                    location = item.get("location", {})
                    venue_raw = location.get("name", "") if isinstance(location, dict) else str(location)
                    events.append({
                        "id": eb_id,
                        "name": name,
                        "url": event_url.split("?")[0],
                        "start_date": item.get("startDate"),
                        "venue_raw": venue_raw,
                        "description_raw": item.get("description", "")[:500],
                        "source": source_key,
                        "source_url": source_url,
                        "scraped_at": datetime.utcnow().isoformat() + "Z",
                    })
            except Exception:
                continue

    return events


def scrape_source(key: str, cfg: dict, session: requests.Session) -> list[dict]:
    url = cfg["url"]
    log.info(f"[SCRAPE] Fetching {key}: {url}")
    try:
        resp = session.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
    except requests.RequestException as exc:
        log.error(f"[SCRAPE] FAIL {key}: {exc}")
        return []

    events = parse_eventbrite_search_page(resp.text, key, url)
    log.info(f"[SCRAPE] {key}: found {len(events)} events")
    return events


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="Use cached fixture data instead of live fetch")
    args, _ = parser.parse_known_args()

    cfg = load_config()
    sources = cfg.get("sources", {})

    if args.dry_run and FIXTURE_PATH.exists():
        log.info(f"[SCRAPE] --dry-run: loading fixture from {FIXTURE_PATH}")
        with open(FIXTURE_PATH) as f:
            all_events = json.load(f)
        log.info(f"[SCRAPE] dry-run: {len(all_events)} events from fixture")
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_PATH, "w") as f:
            json.dump(all_events, f, indent=2, ensure_ascii=False)
        return

    session = requests.Session()
    all_events: list[dict] = []
    active_sources = {k: v for k, v in sources.items() if v.get("enabled", True)}

    for key, src_cfg in active_sources.items():
        events = scrape_source(key, src_cfg, session)
        all_events.extend(events)
        time.sleep(1.5)  # polite delay between sources

    # Deduplicate by id within this run (same event on multiple EB pages)
    seen_ids: set[str] = set()
    deduped: list[dict] = []
    for ev in all_events:
        if ev["id"] not in seen_ids:
            seen_ids.add(ev["id"])
            deduped.append(ev)

    log.info(f"[SCRAPE] Total: {len(deduped)} unique events from {len(active_sources)} sources "
             f"(removed {len(all_events) - len(deduped)} cross-source dupes)")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(deduped, f, indent=2, ensure_ascii=False)

    # Save as fixture for future --dry-run
    if not args.dry_run:
        with open(FIXTURE_PATH, "w") as f:
            json.dump(deduped, f, indent=2, ensure_ascii=False)

    log.info(f"[SCRAPE] Written to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
