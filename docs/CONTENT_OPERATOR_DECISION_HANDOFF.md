# CONTENT.OPERATOR-DECISION-HANDOFF

**For: Robert (operator)**  
**Status: DECISION HANDOFF — NO DATA CHANGES**  
**Date: 2026-05-30**

> ⚠️ **Robert decisions do not auto-publish.** Claude must create a separate implementation phase and ChatGPT must verify proof before any listing, URL, or public change happens.

---

## Current Active Inventory

| Metric | Count |
|---|---|
| Total active listings | 14 |
| Verified (freshness OK) | 11 |
| Needs human review (stale source) | 3 |
| Seeded missing candidates awaiting your decision | 9 |

---

## Part 1 — Seeded Missing Listings (9 candidates)

These are Paris comedy shows not yet in the database. Each requires your decision.

| Seed | Show name | Venue | Lang | Conf | Source URL | Recommended | Your decision | Notes |
|---|---|---|---|---|---|---|---|---|
| S001 | Coucou Comedy — Tuesday | Le Noddi, 75005 | en | 90 | [Eventbrite](https://www.eventbrite.com/o/coucou-comedy-43230488853) | approve_for_manual_import | | |
| S002 | Coucou Comedy — Friday | Broadway Comedy Club, 75002 | en | 85 | [Eventbrite](https://www.eventbrite.com/o/coucou-comedy-43230488853) | approve_for_manual_import | | |
| S003 | Sebastian Marx NY Comedy Night | La Scène Barbès, 75018 | en | 80 | [sebmarx.com](https://www.sebmarx.com/en/) | approve_for_manual_import | | |
| S004 | Paname Comedy Club | Paname Art Cafe | fr | 88 | [FNAC](https://www.fnacspectacles.com/artist/paname-comedy-club/paname-comedy-club-paris-3410304/) | approve_for_manual_import | | |
| S005 | Golden Comedy Club | Golden Comedy Spot, 75002 | fr | 92 | [Fever](https://feverup.com/m/111045/en) | approve_for_manual_import | | |
| S006 | Oscar Comedy Club | Café Oscar, 75002 | fr | 88 | [Eventbrite](https://www.eventbrite.fr/e/oscar-comedy-club-tickets-1672589683769) | approve_for_manual_import | | |
| S007 | The Joke Comedy Club | The Joke, 75004 | fr | 82 | [Fever](https://feverup.com/en/paris/venue/the-joke) | approve_for_manual_import | | |
| S008 | Le Plateau Comedy Club | Monsieur le Zinc, 75010 | fr | 78 | [Fever](https://feverup.com/m/474472/en) | approve_for_manual_import | | |
| S009 | Le Fridge Comedy Night | Le Fridge Comedy, 75002 | fr | 75 | [BilletRéduc](https://www.billetreduc.com/263384/evt.htm) | approve_for_manual_import | | |

**Allowed decisions**: `approve_for_manual_import` / `reject` / `needs_more_research` / `future_watch`

---

## Part 2 — Stale Source Fixes (3 listings)

These are current active listings whose source URLs returned past-event signals. Decisions here determine what happens to each.

| Slug | Show name | Stale signal | Recommended action | Replacement URL | Risk note | Your decision | Notes |
|---|---|---|---|---|---|---|---|
| millennial-meltdown | Millennial Meltdown | "ventes terminées" | keep_needs_human_review | None confirmed — find Kuhl Productions EB organizer page | Do not repoint until current EB ID found | | |
| theatre-bo-julie | Oh My God She's Parisian! | "event ended" | approve_repoint → julie-collas.com | [julie-collas.com](https://www.julie-collas.com/) or [Viator 2026](https://www.viator.com/tours/Paris/Oh-my-god-shes-Parisian-The-brand-new-comedy-show-in-English-language-in-Paris/d479-67244P1) | ⚠️ Verify performer name: DB says "Coulon", official site says **Collas** | | |
| wednesday-night-comedy | Wednesday Night Comedy | "event ended" | hide_until_current_source_found | None found | May have ended; showing broken link harms credibility | | |

**Allowed decisions**: `approve_repoint` / `keep_needs_human_review` / `hide_until_current_source_found` / `needs_more_research`

### Special Note — Oh My God She's Parisian

The existing DB entry uses the name "Julie Coulon". All public sources — official website, Viator, GetYourGuide, theatreinparis.com — use "**Julie Collas**". This may be a typo or an old stage name. Do not change until you confirm which is correct.

---

## Next Implementation Phases (based on your decisions)

| If Robert decides... | Phase that follows |
|---|---|
| Any candidate `approve_for_manual_import` | `CONTENT.SOURCE-COVERAGE.5-MANUAL-IMPORT-APPROVED` |
| `approve_repoint` for theatre-bo-julie | `CONTENT.FRESHNESS.4-REPOINT-APPROVED-SOURCES` |
| `hide_until_current_source_found` for wednesday-night-comedy | `CONTENT.FRESHNESS.4B-HIDE-APPROVED-STALE-LISTINGS` |
| `needs_more_research` for any | `CONTENT.SOURCE-COVERAGE.5B-MORE-RESEARCH` |
