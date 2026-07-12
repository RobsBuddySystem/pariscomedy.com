#!/usr/bin/env python3
"""
fetch_event_images.py — pull a real photo for each Europe event.

data/upcoming_events.json has no image fields, but each event's
canonical_event_url (Eventbrite/Meetup/venue listing pages) embeds an
og:image (or twitter:image) meta tag pointing at the listing's cover photo.
This script fetches each event's page, extracts that image URL, and writes

  data/event_images.json   { "<event id>": "<image url>", ... }

stdlib only (urllib + re) — no third-party deps.

Idempotent / mergeable: existing entries are loaded first and only
overwritten when a fetch for that event succeeds. If an event's fetch fails
(timeout, 403, no og:image found, etc.) the previous entry (if any) is left
untouched — a flaky night never blanks out images that were already found.

Run:
  python3 scripts/fetch_event_images.py

Nightly ordering: this script runs BEFORE scripts/build_europe_pages.py in
the europe-refresh job (see scripts/com.pariscomedy.europe-refresh.plist)
so the page build always has the freshest event_images.json to embed.
"""

from __future__ import annotations

import json
import html as html_lib
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA_FILE = REPO / "data" / "upcoming_events.json"
IMAGES_FILE = REPO / "data" / "event_images.json"

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
TIMEOUT = 10
SLEEP_BETWEEN = 0.5

OG_IMAGE_RE = re.compile(
    r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']',
    re.IGNORECASE,
)
OG_IMAGE_RE_REV = re.compile(
    r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']',
    re.IGNORECASE,
)
TWITTER_IMAGE_RE = re.compile(
    r'<meta[^>]+name=["\']twitter:image(?::src)?["\'][^>]+content=["\']([^"\']+)["\']',
    re.IGNORECASE,
)
TWITTER_IMAGE_RE_REV = re.compile(
    r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']twitter:image(?::src)?["\']',
    re.IGNORECASE,
)


def extract_image_url(html: str) -> str | None:
    for pattern in (OG_IMAGE_RE, OG_IMAGE_RE_REV, TWITTER_IMAGE_RE, TWITTER_IMAGE_RE_REV):
        m = pattern.search(html)
        if m:
            # Meta content is HTML-entity-encoded (&amp;) — unescape or signed
            # URLs (img.evbuc.com ...&s=<sig>) lose their signature and 403.
            url = html_lib.unescape(m.group(1).strip())
            if url:
                return url
    return None


def fetch_image_url(url: str) -> str | None:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            raw = resp.read(400_000)  # og:image tags are always in the <head>; cap the read
            charset = resp.headers.get_content_charset() or "utf-8"
            html = raw.decode(charset, errors="replace")
            final_url = resp.geturl()  # post-redirect base for relative og:image paths
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError, OSError):
        return None
    img = extract_image_url(html)
    if not img:
        return None
    # Eventbrite (and others) emit RELATIVE og:image paths like
    # /e/_next/image?url=... — stored verbatim they resolve against
    # pariscomedy.com in the browser and 404. Always absolutize.
    img = urllib.parse.urljoin(final_url, img)
    # Eventbrite's /_next/image resizer refuses hotlinks; unwrap to the real
    # CDN asset it proxies (the url= param), which serves cross-origin fine.
    parsed = urllib.parse.urlparse(img)
    if parsed.path.endswith("/_next/image") or "/_next/image" in parsed.path:
        # parse_qs already url-decodes ONE layer — exactly right. The evbuc
        # URL's own path stays percent-encoded (https%3A%2F%2Fcdn...): its
        # signature (s=) is computed over that encoded form, so decoding
        # again invalidates it (sig_invalid).
        qs = urllib.parse.parse_qs(parsed.query)
        inner = (qs.get("url") or [None])[0]
        if inner:
            img = inner
    if not img.startswith(("http://", "https://")):
        return None
    return img


def main() -> None:
    if not DATA_FILE.exists():
        raise SystemExit(f"missing {DATA_FILE}")
    events = json.loads(DATA_FILE.read_text())
    if not isinstance(events, list):
        events = events.get("events", [])

    existing: dict[str, str] = {}
    if IMAGES_FILE.exists():
        try:
            prior = json.loads(IMAGES_FILE.read_text())
            if isinstance(prior, dict):
                existing = {str(k): v for k, v in prior.items() if isinstance(v, str)}
        except Exception:
            existing = {}

    results = dict(existing)
    hits = 0
    misses = 0
    total = 0

    for ev in events:
        eid = ev.get("id")
        url = ev.get("canonical_event_url")
        if eid is None or not url:
            continue
        total += 1
        img = fetch_image_url(url)
        key = str(eid)
        if img:
            results[key] = img
            hits += 1
        else:
            misses += 1
            # keep whatever was there before (idempotent merge); do nothing
        time.sleep(SLEEP_BETWEEN)

    IMAGES_FILE.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Processed {total} events: {hits} images found, {misses} fetch/parse failures.")
    print(f"data/event_images.json now has {len(results)} total entries (merged with prior run).")


if __name__ == "__main__":
    main()
