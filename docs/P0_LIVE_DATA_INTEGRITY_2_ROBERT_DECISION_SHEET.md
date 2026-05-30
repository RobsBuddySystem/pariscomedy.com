# P0.LIVE-DATA-INTEGRITY.2 — Robert Decision Sheet

**Phase:** P0.LIVE-DATA-INTEGRITY.2-ROBERT-DECISION-SHEET
**Created:** 2026-05-30
**Status:** awaiting_robert_decision
**Scope:** decision sheet only — NO DB MUTATION, NO URL CHANGES, NO STATUS CHANGES, NO HIDE/UNHIDE, NO IMPORTS, NO FEATURE FLAGS, NO BACKEND CUTOVER.

## Purpose

Phase 1B + 1C shipped a code-only fix that gates rendered CTAs on
`verification_status === 'verified_24h'` and synchronizes the static fallback
articles in `show.html` with the live API response. That fix shields public
visitors from clicking through to dead Eventbrite pages — but it does NOT
correct the underlying data drift in the production DB.

This document presents the 6 listings with known live-data integrity problems
and asks Robert to pick a decision per listing. **Nothing in this document
mutates any system.** Once Robert fills in `robert_decision` per row, a
follow-up phase will apply each decision under strict guardrails.

## Source inputs

- Live API snapshot: `/Users/chuck/Desktop/pariscomedy-live-proof-20260530-1505/api-listings.json`
- Freshness audit:   `/Users/chuck/Desktop/pariscomedy-live-proof-20260530-1505/freshness-audit.json`
- Machine-readable companion: `data/p0-live-data-integrity-2-robert-decision-sheet.json`

## Allowed Robert decisions

- `approve_repoint` — apply a candidate replacement URL
- `approve_demote_to_needs_review` — flip `verified_24h` → `needs_human_review` so CTA shields
- `approve_hide_until_current_source_found` — unpublish / hide until a live source resurfaces
- `approve_venue_correction` — apply a venue / address / name correction
- `keep_as_is` — accept current state as canonical
- `needs_more_research` — pause; require more proof before any change
- `kill_listing` — permanently delist

## Per-listing decision table

| id | slug | freshness | drift signal | rendered CTA after 1C | recommended action | default reason |
|----|------|-----------|--------------|------------------------|---------------------|----------------|
| 31 | charonne | needs_human_review | live EB ...5324429 = EVENT ENDED; audit cites separate stale ID ...1202099 | disabled span (shielded) | `needs_more_research` | no confirmed live URL |
| 11 | millennial-meltdown | needs_human_review | live EB = 'ventes terminées' | disabled span (shielded) | `needs_more_research` | suspected Kuhl Productions URL not yet confirmed |
| 18 | theatre-bo-julie | needs_human_review | live EB = event ended; candidate julie-collas.com; Coulon vs Collas name unresolved | disabled span (shielded) | `needs_more_research` | performer name disambiguation required |
| 15 | wednesday-night-comedy | needs_human_review | live EB = event ended; no replacement found anywhere | disabled span (shielded) | `approve_hide_until_current_source_found` | no surviving source; hide is reversible |
| 3  | ffcn | verified_24h | Robert screenshot says EB ...1989838522586 is DEAD; vault canonical venue = Velvet Bar Paris, 43 Rue Saint-Honoré, 75001 vs DB 39 Rue de Douai, 75009 | **normal anchor (NOT shielded)** | `needs_more_research` | high-risk; needs Robert-confirmed URL AND venue before any write |
| 2  | velvet-comedy | verified_24h | static fallback href drifts from live API booking_url; both EB IDs potentially stale; shares FFCN venue ambiguity | **normal anchor (NOT shielded)** | `needs_more_research` | needs Robert-confirmed live URL + physical venue |

## Per-listing detail

### id 31 — `charonne` — Charonne Comedy Club

- **Current API booking_url:** `https://www.eventbrite.fr/e/charonne-comedy-club-tickets-1697805324429`
- **Current API show_url:** same
- **Current venue:** Le Cafe de la Plage — Paris
- **Freshness status:** needs_human_review
- **Drift:** Live EB ...5324429 returns EVENT ENDED (past Mar 21). Freshness
  audit also references an older ID ...1202099 as `source_url`. Two stale EB
  IDs in circulation.
- **CTA status after 1C:** disabled span ("Tickets need review — check back soon")
- **Candidate replacement URL:** none confirmed
- **Recommended action:** `needs_more_research`
- **Risk note:** Do NOT repoint based only on stale freshness audit IDs.
- **Proof required before any action:** live EB page (HTTP 200, no event-ended
  marker) for the next upcoming Charonne Comedy Club date, plus screenshot.
- **`robert_decision`:** _null_
- **`notes`:** _null_

### id 11 — `millennial-meltdown` — Millennial Meltdown

- **Current API booking_url:** `https://www.eventbrite.fr/e/billets-english-comedy-show-millennial-meltdown-paris-stand-up-night-1984665294321`
- **Current venue:** Le Bikini Bottom — 49 Rue de Lappe, 75011 Paris
- **Freshness status:** needs_human_review
- **Drift:** Live EB returns 'ventes terminées'. No live future-date EB
  instance found.
- **CTA status after 1C:** disabled span
- **Candidate replacement URL:** none confirmed (suspected Kuhl Productions
  page, unverified)
- **Recommended action:** `needs_more_research`
- **Risk note:** Producer is Kuhl Comedy / Kuhl Productions; suspected current
  source may live on a Kuhl-owned page, but unconfirmed.
- **Proof required before any action:** confirmed Kuhl Productions URL for the
  next live Millennial Meltdown date, or a fresh EB event ID with upcoming
  dates and HTTP 200.
- **`robert_decision`:** _null_
- **`notes`:** _null_

### id 18 — `theatre-bo-julie` — Oh My God She's Parisian! — Julie Coulon

- **Current API booking_url:** `https://www.eventbrite.fr/e/the-comedy-in-english-by-a-french-girl-that-will-make-you-love-paris-tickets-1764207685679`
- **Current venue:** Theatre BO Saint-Martin — 19 Boulevard Saint-Martin, 75003 Paris
- **Freshness status:** needs_human_review
- **Drift:** Live EB shows event ended. Candidate repoint `julie-collas.com`
  surfaced. Performer name unresolved: DB renders `Julie Coulon` while
  candidate site is `julie-collas.com` (Coulon vs Collas).
- **CTA status after 1C:** disabled span
- **Candidate replacement URL:** `julie-collas.com` — UNCONFIRMED (name discrepancy)
- **Candidate name correction:** Coulon → Collas — UNCONFIRMED. Do NOT apply
  without Robert confirming the performer's actual legal / stage name.
- **Recommended action:** `needs_more_research`
- **Risk note:** Name disambiguation is load-bearing — a wrong name change
  would defame the performer and break SEO. Do not touch DB name or URL until
  Robert confirms performer identity.
- **Proof required before any action:** Robert-confirmed performer name
  (Coulon vs Collas) AND live ticketing URL with upcoming dates.
- **`robert_decision`:** _null_
- **`notes`:** _null_

### id 15 — `wednesday-night-comedy` — Wednesday Night Comedy

- **Current API booking_url:** `https://www.eventbrite.fr/e/english-standup-wednesday-night-comedy-tickets-1750646975229`
- **Current venue:** La Pomme d'Eve — 1 Rue des Boulangers, 75005 Paris
- **Freshness status:** needs_human_review
- **Drift:** Live EB says event ended. No replacement URL found across
  organizer pages, EB search, or partner platforms.
- **CTA status after 1C:** disabled span
- **Candidate replacement URL:** none
- **Recommended action:** `approve_hide_until_current_source_found`
- **Risk note:** Show may have ended permanently. Hiding is reversible —
  preferred over leaving a permanently disabled CTA in public listings.
- **Proof required before any action:** Robert sign-off to hide. Re-listing
  later requires a live source URL with upcoming dates.
- **`robert_decision`:** _null_
- **`notes`:** _null_

### id 3 — `ffcn` — French Fried Comedy Night

- **Current API booking_url:** `https://www.eventbrite.com/e/french-fried-comedy-night-tickets-1989838522586`
- **Current venue (DB):** Velvet Bar — 39 Rue de Douai, 75009 Paris
- **Current venue (vault canonical):** Velvet Bar Paris — 43 Rue Saint-Honoré, 75001 Paris
- **Freshness status:** **verified_24h**
- **Drift:** DB row still verified_24h but Robert screenshot shows live EB
  ...1989838522586 is DEAD. Additionally, vault canonical lists a different
  Velvet Bar address (75001) than DB (75009). Two independent drifts: (a) URL
  liveness, (b) venue / address.
- **CTA status after 1C:** **normal anchor (NOT shielded)** — public visitor
  right now clicks a live-looking CTA into a dead page.
- **Candidate replacement URL:** none confirmed
- **Candidate venue correction:** vault canonical 43 Rue Saint-Honoré, 75001
  — UNCONFIRMED against current physical venue
- **Recommended action:** `needs_more_research`
- **Risk note:** Highest-risk row in the sheet. Do NOT change URL or venue
  without Robert explicitly confirming BOTH (a) current live EB URL and (b)
  current physical venue name + street address + arrondissement.
- **Proof required before any action:** Robert-confirmed (a) current live FFCN
  ticket URL with upcoming Wednesday dates AND (b) current physical venue
  name + street address. Both required before any DB write. Interim option
  (separate phase, NOT this one): demote to `needs_human_review` to shield the
  CTA in the meantime.
- **`robert_decision`:** _null_
- **`notes`:** _null_

### id 2 — `velvet-comedy` — Velvet Bar Comedy — Le meilleur du stand-up

- **Current API booking_url:** `https://www.eventbrite.com/e/velvet-bar-comedy-le-meilleur-du-stand-up-a-paris-tickets-1989840198599`
- **Current venue (DB):** Velvet Bar — 39 Rue de Douai, 75009 Paris
- **Freshness status:** **verified_24h**
- **Drift:** Static fallback href in `show.html` drifts from live API
  booking_url (audit references EB ID ...1989840111338 while live API returns
  ...1989840198599). Both EB IDs potentially stale even though row is
  verified_24h. Also shares the FFCN venue ambiguity (vault canonical vs DB
  39 Rue de Douai).
- **CTA status after 1C:** **normal anchor (NOT shielded)**. Static fallback
  drift addressed by 1B guard, but underlying EB ID liveness not
  Robert-confirmed.
- **Candidate replacement URL:** none confirmed
- **Candidate venue correction:** same ambiguity as FFCN
- **Recommended action:** `needs_more_research`
- **Risk note:** Do NOT repoint based only on stale freshness audit IDs.
- **Proof required before any action:** Robert-confirmed live Velvet Comedy EB
  URL with upcoming Wednesday dates + confirmed physical venue address.
- **`robert_decision`:** _null_
- **`notes`:** _null_

## Public CTA safety status (as of this phase)

- 4 of 6 listings (`charonne`, `millennial-meltdown`, `theatre-bo-julie`,
  `wednesday-night-comedy`) render a disabled span — visitors cannot click
  through to dead pages.
- 2 of 6 listings (`ffcn`, `velvet-comedy`) render a normal anchor because
  their DB row is still `verified_24h`. These remain unshielded until Robert
  authorizes either a URL repoint or a freshness demotion in a follow-up
  phase.

## Out of scope for this phase

- DB writes
- Source URL changes
- Freshness status changes
- Hide / unhide / unpublish
- Eventbrite imports
- Feature flag flips
- Backend cutover

## Next phase (after Robert fills in decisions)

A successor phase `P0.LIVE-DATA-INTEGRITY.3-APPLY-ROBERT-DECISIONS` will read
the populated `robert_decision` values and apply them under strict per-row
guards (each row gated on the specific proof listed above).
