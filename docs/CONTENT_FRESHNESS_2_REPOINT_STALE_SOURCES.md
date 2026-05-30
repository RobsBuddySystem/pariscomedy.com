# CONTENT.FRESHNESS.2 — Repoint Stale Sources

**Status: AUDIT / REPOINT PROPOSAL ONLY — NO PUBLIC LISTING CHANGES**  
**Date: 2026-05-30**

---

## Needs-Human-Review Listings (3)

All 3 have `confidence_score: 10` and `stale_risk: high`. Their Eventbrite source URLs returned past-event signals ("ventes terminées" or "event ended").

---

### Listing 1 — Millennial Meltdown

| Field | Value |
|---|---|
| Slug | `millennial-meltdown` |
| Current source URL | https://www.eventbrite.fr/e/billets-english-comedy-show-millennial-meltdown-paris-stand-up-night-1984665294321 |
| Stale signal | "ventes terminées" on Eventbrite page |
| Recommendation | **keep_needs_human_review** |

**What was found**: Show is confirmed still running weekly — Kuhl Productions, every Wednesday at 8pm, Le Bikini Bottom (Bastille). The current Eventbrite URL is a past event page. The organizer likely publishes a new event ID per date or per month.

**Operator action required**: Find the current Eventbrite event ID for Millennial Meltdown by searching the Kuhl Productions organizer page on Eventbrite (`eventbrite.fr/o/kuhl-comedy-...`), then update `booking_url` to the active recurring listing.

---

### Listing 2 — Oh My God She's Parisian! — Julie Coulon

| Field | Value |
|---|---|
| Slug | `theatre-bo-julie` |
| Current source URL | https://www.eventbrite.fr/e/the-comedy-in-english-by-a-french-girl-that-will-make-you-love-paris-tickets-1764207685679 |
| Stale signal | "event ended" on Eventbrite page |
| Recommendation | **repoint_source_url** |

**What was found**: Show is still running in 2026. Active on Viator ([2026 booking link](https://www.viator.com/tours/Paris/Oh-my-god-shes-Parisian-The-brand-new-comedy-show-in-English-language-in-Paris/d479-67244P1)) and GetYourGuide. Official site: [julie-collas.com](https://www.julie-collas.com/). Venue appears to be Théâtre Bo Saint-Martin (per theatreinparis.com).

**Additional note**: Performer's surname may be **Collas** (not Coulon) — the official site is julie-collas.com and all search results use "Collas". The existing DB entry uses "Coulon". This may need a name correction.

**Replacement URL candidates**:
1. [julie-collas.com](https://www.julie-collas.com/) — official performer site, most authoritative (confidence 80)
2. [Viator 2026](https://www.viator.com/tours/Paris/Oh-my-god-shes-Parisian-The-brand-new-comedy-show-in-English-language-in-Paris/d479-67244P1) — active 2026 booking (confidence 75)

**Operator action required**: Confirm current venue address and decide: repoint booking_url to julie-collas.com or Viator. Verify if performer name should be corrected to "Julie Collas".

---

### Listing 3 — Wednesday Night Comedy

| Field | Value |
|---|---|
| Slug | `wednesday-night-comedy` |
| Current source URL | https://www.eventbrite.fr/e/english-standup-wednesday-night-comedy-tickets-1750646975229 |
| Stale signal | "event ended" on Eventbrite page |
| Recommendation | **hide_until_current_source_found** |

**What was found**: No current replacement URL identified. The existing Eventbrite listing ID is a past event. Organizer not identified in search results. Show may have ended or moved to a new event series.

**Operator action required**: Search Eventbrite for "Wednesday Night Comedy Paris" to find if a current event series exists. If not found within 2 weeks, recommend moving to `stale_hidden`.

---

## Operator Decision Table

| Listing | Recommendation | Your decision | Notes |
|---|---|---|---|
| Millennial Meltdown | keep_needs_human_review — find current Kuhl Productions Eventbrite ID | | |
| Oh My God She's Parisian! | repoint_source_url — repoint to julie-collas.com or Viator; verify name Collas vs Coulon | | |
| Wednesday Night Comedy | hide_until_current_source_found — search EB for current series | | |

---

## What Is Not Authorized

- No `booking_url` or `show_url` changes in the DB — those require a separate authorized phase
- No public listing status changes (active → stale_hidden etc.) without a separate authorized phase
- No new listing imports
- No feature flags
