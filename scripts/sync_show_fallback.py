#!/usr/bin/env python3
"""P1.DATA.3B — sync show.html noscript fallback with data/freshness-audit.json.

show.html contains 14 hardcoded <article id="show-{slug}"> blocks inside
<noscript>. Each carries:
  - a `data-verification-status="..."` attribute
  - a `<a href="...">Get tickets / source listing →</a>` whose URL must match
    the verifier's source_url (= manual repoint if any, else API URL)
  - a `<p class="freshness">` line with the audit's last_checked + status + confidence

This script reads data/freshness-audit.json and rewrites those three fields
on each article in-place. Everything else (h2/venue/address/description) is
preserved.

Behavior is idempotent: running it twice with the same audit produces the same
output.
"""
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SHOW_HTML = REPO / "show.html"
AUDIT_PATH = REPO / "data" / "freshness-audit.json"

STATUS_LABEL = {
    "verified_24h": "verified in last 24h",
    "verified_72h": "verified in last 72h",
    "stale": "stale — source not re-verified",
    "needs_human_review": "needs review — confirm directly on source",
    "source_unreachable": "source unreachable — last verified link broken",
    "user_submitted_pending_review": "user-submitted, awaiting review",
}

ARTICLE_RE = re.compile(
    r'(<article id="show-(?P<slug>[a-z0-9-]+)" data-verification-status=")'
    r'(?P<status>[^"]+)'
    r'(">.*?</article>)',
    re.DOTALL,
)

LINK_RE = re.compile(
    r'(<a href=")(?P<url>[^"]+)("[^>]*>Get tickets / source listing[^<]*</a>)'
)

FRESHNESS_RE = re.compile(
    r'(<p class="freshness"><small>)(?P<inner>.*?)(</small></p>)',
    re.DOTALL,
)


def derive_platform_label(url: str) -> str:
    if "eventbrite" in url:
        return "Eventbrite"
    if "fnacspectacles" in url or "francebillet" in url:
        return "FNAC / France Billet"
    if "billetreduc" in url:
        return "BilletRéduc"
    if "feverup" in url:
        return "Fever"
    if "ticketmaster" in url:
        return "Ticketmaster"
    if "seetickets" in url:
        return "See Tickets"
    if "weezevent" in url:
        return "Weezevent"
    if "billetweb" in url:
        return "Billetweb"
    if "shotgun.live" in url:
        return "Shotgun"
    if "dice.fm" in url:
        return "Dice"
    return "External listing"


def build_freshness_inner(audit_entry: dict) -> str:
    # Per Robert (2026-06-03): NEVER expose internal verification status,
    # confidence score, or "last checked" on the public page — anywhere,
    # including this no-JS fallback. Emit only a neutral source disclosure.
    platform = derive_platform_label(audit_entry.get("source_url") or "")
    return (
        f"Tickets are sold on {platform}, not by Paris Comedy. "
        f"Times and prices can change — always confirm on the source before purchase."
    )


def main() -> int:
    audit = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
    by_slug = {l["slug"]: l for l in audit.get("listings", [])}
    if not by_slug:
        print("no listings in audit", file=sys.stderr)
        return 1

    html = SHOW_HTML.read_text(encoding="utf-8")

    rewrites = []

    def replace_article(m: re.Match) -> str:
        slug = m.group("slug")
        entry = by_slug.get(slug)
        if not entry:
            # Slug present in show.html but missing from audit — leave as-is
            return m.group(0)
        new_status = entry.get("verification_status") or "needs_human_review"
        new_url = entry.get("source_url") or ""
        old_status_attr = m.group(0).split('data-verification-status="', 1)[1].split('"', 1)[0]

        block = m.group(0)
        # Replace status attr
        block = re.sub(
            r'(<article id="show-' + re.escape(slug) + r'" data-verification-status=")[^"]+(")',
            lambda mm: f'{mm.group(1)}{new_status}{mm.group(2)}',
            block,
            count=1,
        )
        # Replace ticket link URL
        if new_url:
            block = LINK_RE.sub(
                lambda mm: f'{mm.group(1)}{new_url}{mm.group(3)}',
                block,
                count=1,
            )
        # Replace freshness inner content
        inner = build_freshness_inner(entry)
        block = FRESHNESS_RE.sub(
            lambda mm: f'{mm.group(1)}{inner}{mm.group(3)}',
            block,
            count=1,
        )
        if block != m.group(0):
            rewrites.append({
                "slug": slug,
                "old_status": old_status_attr,
                "new_status": new_status,
                "new_url": new_url,
                "last_checked": (entry.get("last_checked_at") or "")[:10],
                "confidence": entry.get("confidence_score"),
            })
        return block

    new_html = ARTICLE_RE.sub(replace_article, html)
    if new_html == html:
        print("no changes needed", file=sys.stderr)
        return 0
    SHOW_HTML.write_text(new_html, encoding="utf-8")
    print(f"updated {len(rewrites)} articles in show.html", file=sys.stderr)
    for r in rewrites:
        print(
            f"  {r['slug']:25s} {r['old_status']:22s} -> {r['new_status']:22s} "
            f"(checked {r['last_checked']}, conf {r['confidence']})",
            file=sys.stderr,
        )
    print(json.dumps({"rewrites": rewrites}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
