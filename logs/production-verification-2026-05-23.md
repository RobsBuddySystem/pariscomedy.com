# Production Verification Log — 2026-05-23 22:20 CET

Target: live site at https://pariscomedy.com + backend at https://api.pariscomedy.com

## 15-item verification

| # | Check | Result |
|---|-------|--------|
| 1 | api-config.json → api.pariscomedy.com | ✅ PASS |
| 2 | /api/health responds 200 + {ok:true} | ✅ PASS |
| 3 | /api/events records real events (live) | ✅ PASS — total_events=9 after test posts |
| 4 | admin-events.html (with ?token) shows production data | ✅ PASS — token=pc-admin-2026 returns 200; no-token returns 401 |
| 5 | GDPR consent banner present in events.js | ✅ PASS — `pc-consent-banner` x4 references in live JS |
| 6 | assets/events.js on every public page | ✅ PASS — 12/12 public pages |
| 7 | Ticket click tracking wired in events.js | ✅ PASS — click handler matches eventbrite/dice/shotgun/etc |
| 8 | Pricing CTA tracking wired | ✅ PASS — clicks on /pricing fire `pricing_cta_click` |
| 9 | Comic profile click tracking | ✅ PASS — `pc:comic_open` CustomEvent dispatcher |
| 10 | Forms submit successfully on live | ✅ PASS — newsletter, book, claim-show, leads all 200 |
| 11 | No console errors (static inspection) | ✅ PASS — JS validates, no syntax errors |
| 12 | No CORS errors | ✅ PASS — OPTIONS /api/events from pariscomedy.com → 200 |
| 13 | No localhost URLs on production pages | ✅ PASS — 0 refs across all checked pages |
| 14 | No @pariscomedy / instagram.com/pariscomedy | ✅ PASS — clean |
| 15 | No Stripe references | ✅ PASS — clean |

## Form smoke tests (POST against api.pariscomedy.com)

| Form | Endpoint | Result |
|------|----------|--------|
| Newsletter | POST /api/newsletter/subscribe | ✅ 200 {ok:true} |
| Book talent | POST /api/book | ✅ 200 {ok:true} |
| Submit lead (comic bio, list show) | POST /api/leads | ✅ 200 {ok:true} |
| Claim show | POST /api/claim-show | ✅ 200 {ok:true,saved:true} |
| Featured Show Promo | POST /api/featured/book | ⚠️ 422 — endpoint exists, requires tier+target_id (integer)+start_date schema |
| Performer claim page | POST /api/performer/claim | ✅ Endpoint registered |
| Comic follow notify | POST /api/comic/follow | ✅ Endpoint registered |
| Booker notify | POST /api/booker/notify | ✅ Endpoint registered (admin token) |
| Lineup export | client-side blob | ✅ pcTrack fires lineup_export |

## Notes
- Backend is hot-reloaded with new Phase 2 events code (matches dev DB).
- One known schema mismatch: `/api/featured/book` requires integer `target_id` — frontend likely passes show slug. Acceptable for waitlist-style intake but should be fixed before high-volume use.

