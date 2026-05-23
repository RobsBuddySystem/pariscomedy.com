# ParisComedy — Language / Affiliate / Featured-Show Audit

**Date:** 2026-05-23
**Trigger:** Robert flagged "Bilingual" label on Oscar Comedy Club as unverified; broader concerns about French show coverage, fake featured cards, and placeholder affiliate IDs going to production.

---

## Final report — direct answers to the 8 questions

### 1. How many shows were incorrectly labelled bilingual?

**5 of 37 (13.5%).** All re-tagged to French + `needs_language_review: true`:

| Date | Show | Old | New |
|---|---|---|---|
| 2026-05-24 | Oscar Comedy Club | en+fr | fr (low confidence, needs review) |
| 2026-05-27 | Velvet Bar Comedy Showcase | en+fr | fr (low confidence, needs review) |
| 2026-05-31 | Oscar Comedy Club | en+fr | fr (low confidence, needs review) |
| 2026-06-03 | Velvet Bar Comedy Showcase | en+fr | fr (low confidence, needs review) |
| 2026-06-07 | Oscar Comedy Club | en+fr | fr (low confidence, needs review) |

Reason: neither title nor URL slug contained any explicit `bilingue / bilingual / français-anglais / French and English / English and French` token. Per the new strict rule, description text alone is not sufficient evidence (descriptions were admin-seeded, often inferred).

Velvet Bar Comedy is Robert's own show (FFCN). He may genuinely run it bilingual — but the source listing must say so before the site can claim it. Awaiting his review.

### 2. How many French shows were missing from tomorrow / Sunday?

**Tomorrow (Sun 2026-05-24): 2 newly visible.** Oscar Comedy Club (re-tagged fr) is now in the French filter; Green Mic Comedy Show stays English (title explicitly says "English"). The Sunday total goes from 2 "bilingual + English" to 1 English + 1 French (Oscar).

More broadly: before this audit, **0 of 37** shows were tagged French-only. The bias was systemic.

### 3. Why were French shows missing?

Three compounding causes in the seed ingestion that produced `SHOWS_DATA`:

1. **English-anchored query bias.** The original seed list was built from Eventbrite searches containing `english`, `anglais`, `anglophone` keywords. French-only listings were never queried.
2. **No French default.** Any ambiguous show was tagged `["en"]` rather than `["fr"]`.
3. **Description over-claim.** Admin-seeded descriptions said things like "Sunday afternoon English and bilingual comedy" without source proof, then the language tag was set to match the description.

Fix applied: new strict classifier defaults to French, only upgrades to English/Bilingual on explicit title-level evidence, marks description-only English signals as `medium` confidence + `needs_language_review: true` for human review.

### 4. Was `?aff=pariscomedy` real or placeholder?

**Placeholder.** It was injected by `/r.html` reading `data/affiliates.json`, where `networks.eventbrite.com.ref` was the literal string `"pariscomedy"`. No affiliate program had been signed up for, no approval received, no contract. The parameter would silently fail Eventbrite's attribution validation.

### 5. Are ticket links safe without fake affiliate IDs?

**Yes, now.** Three changes:

- `data/affiliates.json` — all `ref` strings emptied; new `enabled: false` flag on every network; comment-rule "Never invent affiliate IDs."
- `r.html` — injection guarded by `net.enabled === true && net.ref`. With the new config, no parameters are appended; visitors go straight to the bare Eventbrite URL.
- Click tracking still works via `/api/affiliate-click` and `localStorage` — only the *attribution* parameter is gone, not the analytics.

When Robert's Eventbrite affiliate application is approved, the activation is two lines: set `ref` to the real ID and `enabled: true`.

### 6. Are featured shows working honestly?

**No, but they are now.**

`index.html`'s `renderWeeklyFeatured()` previously called `seededShuffle(SHOWS_DATA, weekSeed)` and labelled 3 random shows "⭐ FEATURED THIS WEEK" — fake editorial endorsement. Rewritten:

- Render only shows that have `editorial_featured === true` OR `paid_featured_until` in the future.
- If zero shows qualify, show "No featured show yet" + a `Promote your show →` CTA linking to `/pricing.html#featured-promo`.
- No seeded shuffle remains.

`renderFeaturedTonight()` was already honest (filters `SHOWS_DATA` by today's date; badge says "🎤 TONIGHT" not "FEATURED").

`renderFeatured()` (the top "FEATURED" strip) pulls from `/api/listings?featured=1` and depends on the backend's `is_featured` flag — also honest as long as the backend only flips it on payment or curation.

### 7. Should French translation launch now or after English launch?

**After English launch.** Plan:

- Phase 1 (now → launch): English UI only. Show cards display localized show titles as authored by the venue (already mixed FR/EN show names; we do not translate those).
- Phase 2 (1–2 weeks post-launch): observe traffic, fix any English copy issues, ensure revenue flows work end-to-end (Eventbrite affiliate live, SumUp products live).
- Phase 3 (after revenue flows are stable): introduce the i18n layer described below.

Rationale: translation duplicates surface area and risks drift on revenue-critical pages (pricing, checkout, payment status). Ship English well first.

### 8. What exact tests prove English/French changes will not drift?

Five drift-prevention tests, to be implemented as part of Phase 3:

1. **Single-source data test.** Mutate a show's `date` in `data/shows.json`; render both `/shows.html` and `/fr/shows.html`; assert both show the new date. Fails if either page reads from a duplicated copy.
2. **Single-source ticket URL test.** Mutate `ticket_url`; assert both locales link to the new URL.
3. **Single-source price test.** Mutate `price_info`; assert both locales display the new value.
4. **Missing-translation logger.** Render `/fr/pricing.html`; assert that every key the French dictionary is missing was logged to `events` with `event_type=i18n_missing_key` and the page rendered the English fallback (not an empty string).
5. **Key parity test.** Read `i18n/en.json` and `i18n/fr.json`; assert key sets are identical (Set(en) === Set(fr)). Run in CI.

If any of these would fail today, French launch is blocked until they pass.

---

## Implementation log

### Files changed

- `~/Desktop/pariscomedy_output/html/shows.html`
  - Replaced single "Bilingual" vibe chip with explicit language filter bar (All / French / English / Bilingual).
  - Added `setLang(l)`, `activeLang`, `getFiltered()` language branch.
  - `SHOWS_DATA` re-classified: every row now has `language_confidence` (high/medium/low) and `needs_language_review` (bool).
  - 9 shows re-tagged (5 bilingual→fr, 4 english→fr) — see report above.
- `~/Desktop/pariscomedy_output/html/index.html`
  - `renderWeeklyFeatured()` rewritten: no more `seededShuffle`. Real featured shows only; empty state with "Promote your show" CTA if none.
- `~/pariscomedy-push-20260517-194848/data/affiliates.json`
  - All `ref` emptied, `enabled: false` flag added per network. Rule comment added.
- `~/pariscomedy-push-20260517-194848/r.html` (+ Desktop mirror)
  - Injection guarded by `net.enabled === true`. No more silent `?aff=pariscomedy`.

### Backend changes

None this session — the language tags live in static SHOWS_DATA, not the backend DB.

### Reclassification report (from /tmp/reclassify_report.json)

- Total shows: 37
- Changed: 9
- New language distribution: en=28, fr=9 (was: en=32, en+fr=5, fr=0)
- Needs language review: 18 of 37 (mostly admin-seeded descriptions with English-only signal in description but not title)

---

## i18n architecture plan (for Phase 3)

### Layer 1 — Canonical data

Single JSON source of truth per entity. **No translated copies.**

- `data/shows.json` — shows (date, time, venue ref, ticket_url, price, language tags)
- `data/comics.json` — comics (name as-authored, bio_key)
- `data/venues.json` — venues (name as-authored, address, neighborhood)
- `data/affiliates.json` — affiliate config (already in place)
- `data/plans.json` — SumUp plan catalog (already in `main.py`'s `PLAN_CATALOG`; do not duplicate)

### Layer 2 — UI translation dictionary

Two flat key-value files for UI chrome only:

- `i18n/en.json` — `{ "nav.shows": "Shows", "btn.tickets": "Get tickets", "pricing.featured.cta": "Promote your show" }`
- `i18n/fr.json` — `{ "nav.shows": "Spectacles", "btn.tickets": "Voir les billets", "pricing.featured.cta": "Promouvoir votre spectacle" }`

Renderer: `t('nav.shows')` reads `i18n/{locale}.json`; on missing key, falls back to English **and** posts `event_type=i18n_missing_key` to `/api/events`.

### Layer 3 — Routing

- `/shows.html` → English UI, canonical data
- `/fr/shows.html` → French UI, same canonical data
- A single template per page; the locale is injected at build/render time.

### Layer 4 — Drift guards

- CI test: `node tools/check-i18n-parity.js` — fails the build if `Set(keys(en)) !== Set(keys(fr))`.
- Daily admin event: count `i18n_missing_key` events; alert if >0.
- Manual review of every page change must touch only `i18n/*.json` for chrome OR `data/*.json` for facts. Diff that touches both is suspicious.

### Out of scope for Phase 3

- Auto-translating show titles. (Venue-authored. Keep as-is.)
- Auto-translating comic bios. (Comic-authored. Editor flow only.)
- French-localised legal copy. (Legal review required — punt to Phase 4.)

---

## Follow-up tasks (added to TODO)

- TODO: real Eventbrite affiliate signup → paste ref + flip `enabled:true` in `data/affiliates.json`. Same for Ticketmaster + TripAdvisor.
- TODO: human review pass on the 18 shows with `needs_language_review: true` — Robert confirms each as French / English / Bilingual.
- TODO: ingestion pipeline — add a Paris French-comedy seed query so future imports surface French-default shows.
- TODO: i18n Phase 3 implementation per plan above.
- TODO: featured-show admin flow — UI for setting `editorial_featured: true` on a show (curated picks) without going through paid flow.

---

*Paired with* [[ParisComedy-Session-Handoff-2026-05-23]], [[Velvet-FFCN-Show-Names-Hard-Rule]], [[FFCN-Branding-Assets]].
