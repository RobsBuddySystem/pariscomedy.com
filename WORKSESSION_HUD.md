# WORKSESSION HUD — pariscomedy.com 2026-05-23 (SESSION SAVED 22:40 CET)

## Session ended cleanly. Resume from here next time.

---

## Status snapshot

| Phase | State |
|-------|-------|
| 1 — Production verification | ✅ GREEN — live site uses new backend |
| 2 — Events / GDPR tracking | ✅ GREEN — 19 event types live, consent banner, DSR |
| 3 — Affiliate revenue | 🟡 INFRA READY (Robert must sign up + paste IDs) |
| 3 — Payment activation | 🟡 INFRA READY (Robert must create 7 SumUp products) |

---

## Today's commits (chronological)

| Commit | Repo | Summary |
|--------|------|---------|
| `5acd236` | push | P0 audit: remove IG links, fix false about claim, stale banner |
| `748dbcc` | push | Phase 2 frontend: events.js + admin-events.html + 13 pages |
| `a5519b2` | backend | Phase 2 backend: events table + endpoints + DSR |
| `7a59b5b` | push | Phase 2 docs |
| `28e72d4` | push | Production verification + affiliate checklist + payment audit |
| `19ec9eb` | backend | Phase 3: 7 prepaid tiers + checkout intent + expire sweep |
| `af68dee` | push | Phase 3 frontend: Featured Promo CTA + checkout-pending |

All pushed to https://github.com/RobsBuddySystem/pariscomedy.com (main).

---

## Next session — start here

Read `~/Documents/chuck_vault/10-concepts/projects/ParisComedy-Session-Handoff-2026-05-23.md`.

**Fastest revenue-positive next step:** Robert signs up for Eventbrite Affiliate Program (24-hour approval), pastes the real ref ID into `data/affiliates.json`. That one action turns ~80% of ticket clicks into 1.5% commission.

---

## Open code TODOs

- `data/affiliates.json` — placeholder refs across 8 programs (full checklist at `docs/revenue/Affiliate-Setup-Checklist.md`)
- `PLAN_CATALOG` in `main.py` — 7 `TODO_*` SumUp product codes

---

## 2026-05-23 (later) — Language / Affiliate / Featured audit + fixes

Triggered by Robert flagging Oscar Comedy Club as wrongly "Bilingual". See `docs/audits/ParisComedy-Language-Affiliate-Featured-Shows-Audit-2026-05-23.md` (also in chuck_vault).

**Findings & fixes (all applied locally — pending push):**
- 5 shows wrongly tagged bilingual → re-tagged French + `needs_language_review:true` (Oscar ×3, Velvet ×2).
- 4 shows tagged English with no title-level evidence → re-tagged French + `needs_language_review:true` (Comedy Crush, Kiss Comedy Club).
- 0 French-only shows in seed data before; 9 now (still ingestion-biased toward English — TODO: fix scraper queries).
- `?aff=pariscomedy` confirmed PLACEHOLDER (not a real affiliate ID). Stripped from `data/affiliates.json`; `r.html` gated on `enabled:true`.
- `renderWeeklyFeatured()` in `index.html` was FAKE (random `seededShuffle` labelled "FEATURED"). Rewritten to honor `editorial_featured` / `paid_featured_until` only; empty state shows "Promote your show" CTA.
- New language filter on `/shows.html`: All / French / English / Bilingual.
- 18 of 37 shows have `needs_language_review:true` — Robert review pass needed.

**Phase 4 already added this session:** Eventbrite live sync (`/api/eb/shows`, 1h cache, 18 FFCN events) — separate from the audit work above.

**i18n decision:** English launch first; French as Phase 3 with strict drift-prevention tests (see audit doc §7-8).
