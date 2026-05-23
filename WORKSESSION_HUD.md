# WORKSESSION HUD — pariscomedy.com Audit 2026-05-23

## Session goal
Full public-site audit: currentness, link integrity, identity safety, revenue readiness. Fix all P0/P1 before Phase 2 (unified events/GDPR tracking).

## P0 — Ship-blocker fixes
| # | Issue | File(s) | Status |
|---|-------|---------|--------|
| 1 | `instagram.com/pariscomedy` link — account not owned | index.html, shows.html, comedians.html | ✅ FIXED |
| 2 | `about.html` false claim: "Every show listing is verified. Every Eventbrite link is live." | about.html | ✅ FIXED |
| 3 | Homepage "First 100 Featured listings FREE" — stale launch copy | index.html | ✅ FIXED |

## P1 — Revenue/trust issues
| # | Issue | File(s) | Status |
|---|-------|---------|--------|
| 4 | Pricing "First 100 comedians" lifetime €1 — revisit copy accuracy | pricing.html | ✅ REVIEWED |
| 5 | Shows tonight tab date logic — verified Europe/Paris correct | shows.html | ✅ OK |
| 6 | Featured show promo tier present on pricing.html | pricing.html | ✅ PRESENT |
| 7 | Booker dashboard "Loading shows..." stale copy | booker-dashboard.html | ✅ OK (dynamic) |

## Audit log
- Instagram refs: 3 files (index, shows, comedians footers) — replaced with email
- Robert/Hoehn: CLEAN (no matches outside c/ pages)
- Stripe: CLEAN
- Coming Soon / Loading shows: CLEAN
- Date logic shows.html: Europe/Paris ✅
- Featured promo tier pricing.html: ✅ present

## Phase 2 gate
**HOLD** — pending commit + push of P0 fixes. After push: GREEN for Phase 2.

## Robert-action items (operator)
- Register instagram.com/pariscomedy OR remove all IG references (done: removed)
- Real affiliate IDs for Eventbrite + GetYourGuide
- SumUp recurring product for Booker Plus €5/mo
- SMTP config for email notifications
- confirmed.show enrichment dry-run
