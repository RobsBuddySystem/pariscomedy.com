# Stale Source Deep Audit — 2026-05-30

Robert flagged a regression: `/shows/charonne.html` Get-Tickets button points to an Eventbrite page that says **EVENT ENDED / Sales ended Sat, Mar 21 7:30 PM**, yet the freshness audit marked the listing `verified_24h` with confidence 98.

**Root cause confirmed.** Listings carry two URL fields — `source_url` (listing-level / recurring parent) and `api_source_url` (specific instance the button actually links to). The freshness verifier only checks `source_url`. When the listing-level page still shows "Multiple dates / future", the verifier passes — even though `api_source_url` points at a dead single-instance page.

Of the 14 active listings, deep-checking BOTH URLs yields:

- **GREEN: 8** (both URLs future-active)
- **YELLOW: 3** (one URL stale, other future — usually `api_source_url` stale)
- **RED: 3** (only `source_url` exists and it is stale)

## RED — listing-level URL itself is stale (button is broken and there is no fallback)

| Slug | URL | Signal | Action |
|---|---|---|---|
| `millennial-meltdown` | eventbrite.fr/...-1984665294321 | "Ventes terminées" | Re-point `source_url` to the organizer's current Eventbrite collection, or de-list. (Already prior `needs_human_review`, confidence 10 — verifier was correct here.) |
| `theatre-bo-julie` | eventbrite.fr/...-1764207685679 | "Event ended" / "Sales ended" | Re-point or de-list. |
| `wednesday-night-comedy` | eventbrite.fr/...-1750646975229 | "Event ended" / "Sales ended" | Re-point or de-list. |

## YELLOW — `source_url` future-active, `api_source_url` stale (button broken, but parent is fine)

| Slug | Stale URL | Signal | Action |
|---|---|---|---|
| `charonne` | api_source_url ...1697805324429 | "Event ended / Sales ended Sat, Mar 21 7:30 PM" | **THIS IS ROBERT'S BUG.** Null out `api_source_url` (button will fall back to `source_url` = the still-live parent listing) OR repoint to next instance. |
| `ffcn` | source_url ...1989838453379 | "Sales ended Wed, May 27 10:00 PM" | The parent listing has rolled; the `api_source_url` (...522586) is the next instance and is live. Swap: promote `api_source_url` to `source_url`, fetch a new `api_source_url`. |
| `velvet-comedy` | api_source_url ...1989840198599 | "Event ended / Sales ended Wed, May 27 8:30 PM" | Null out or repoint `api_source_url`; `source_url` parent is live. |

## Recommended verifier fixes

1. **Check both URL fields.** Today only `source_url` is checked.
2. **Parse for past-event phrases**, not just HTTP 200: `event ended`, `sales ended`, `ventes terminées`, `événement terminé`, `sold out`, `complet`.
3. **Compare any date in title/og:title to today** — flag if all dates < today.
4. **Downgrade confidence to ≤ 30** when any URL on a listing fails — never let confidence 98 ship while a CTA points at a dead page.
5. Add the 3 RED slugs to `freshness-overrides.json` immediately so the UI stops claiming `verified_24h`.

Data file: `data/stale-source-deep-audit-20260530.json`
