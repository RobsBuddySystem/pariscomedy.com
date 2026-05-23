# ParisComedy — Project TODO

Canonical project status. Updated 2026-05-23.

---

## P0 — Required for revenue activation (one-time, manual)

- [ ] **Eventbrite Affiliate Program** signup ([eventbrite.com/affiliate-program](https://www.eventbrite.com/affiliate-program)). On approval, set `ref` + `enabled:true` in `data/affiliates.json` for both `eventbrite.com` and `eventbrite.fr`.
- [ ] **SumUp products** — create 7 prepaid products in SumUp dashboard, paste codes into `PLAN_CATALOG` in `main.py`, replacing each `TODO_*` placeholder (lifetime €1 / monthly €1 / annual €12 / booker intro €1 / booker std €5 / featured 7d €5 / featured 30d €15 / featured 90d €40).

---

## P1 — Human review (must happen before launch)

- [ ] **Language review pass** — 18 of 37 shows have `needs_language_review:true` in `shows.html` `SHOWS_DATA`. Robert verifies each as French / English / Bilingual against the source listing, sets `language_confidence:high` and clears the review flag. (Audit: `docs/audits/ParisComedy-Language-Affiliate-Featured-Shows-Audit-2026-05-23.md`)
- [ ] **Velvet Bar Comedy Showcase** — Robert confirms whether it's actually English / French / Bilingual. Currently re-tagged French (low confidence) because the title "Le meilleur du stand-up à Paris" is purely French and the description gave no explicit signal.
- [ ] **Oscar Comedy Club** — same: confirm language. Currently French (low confidence).

---

## P2 — Ingestion bias fix (post-launch)

- [ ] Add a Paris **French-language** seed query to whichever scraper / curation tool produced the current `SHOWS_DATA`. The current seed is 100% English-anchored (`english`, `anglais`, `anglophone`) which is why 0 French shows existed before today's audit.
- [ ] Add `language_confidence` + `needs_language_review` to the ingestion schema so future imports inherit the strict default-French rule automatically.

---

## P3 — i18n (after English launch + revenue stable)

See `docs/audits/ParisComedy-Language-Affiliate-Featured-Shows-Audit-2026-05-23.md` §i18n architecture plan.

- [ ] Move all show / venue / comic data to single canonical JSON files (`data/shows.json`, `data/venues.json`, `data/comics.json`).
- [ ] Create `i18n/en.json` + `i18n/fr.json` for UI chrome strings only.
- [ ] Implement `t(key)` helper with English fallback + `i18n_missing_key` event logging.
- [ ] Route `/fr/*` to French-locale template against canonical data.
- [ ] Drift-prevention CI tests (5 tests — see audit §8).

---

## P4 — Polish / nice-to-have

- [ ] **Featured-show admin UI** — flip `editorial_featured:true` on a show without going through the paid flow (curator picks). Currently you'd have to edit `SHOWS_DATA` by hand.
- [ ] **Featured-show backend** — promote `editorial_featured` from a per-show JSON field into a backend table joined at render time, so curated picks survive `SHOWS_DATA` regenerations.
- [ ] **Affiliate Setup Checklist** (`docs/revenue/Affiliate-Setup-Checklist.md`) — 8 programs total; status tracker for each.
- [ ] Legacy `stripe_session_id` / `stripe_payment_intent_id` columns on `featured_bookings` — rename to `provider_session_id` / `provider_intent_id` in a future migration.

---

## Done (this session, 2026-05-23)

- ✅ Phase 1 production verification GREEN (live site verified against new backend)
- ✅ Phase 2 events / GDPR tracking GREEN (19 event types, consent banner, DSR endpoints, admin dashboard)
- ✅ Phase 3 prepaid SumUp infra GREEN (7 tiers, checkout intent, mark-paid, expire sweep, Featured Promo CTA)
- ✅ Phase 4 Eventbrite live sync GREEN (`/api/eb/shows`, 1h cache, 18 FFCN events live)
- ✅ Strict language reclassification (9 shows re-tagged; default French; confidence + review fields added)
- ✅ Language filter UI on `/shows.html` (All / French / English / Bilingual)
- ✅ `?aff=pariscomedy` placeholder stripped; `r.html` gated on `enabled:true`
- ✅ `renderWeeklyFeatured()` rewritten — no fake features; honest empty state + Promote CTA
- ✅ Audit doc + Obsidian copy + HUD update
