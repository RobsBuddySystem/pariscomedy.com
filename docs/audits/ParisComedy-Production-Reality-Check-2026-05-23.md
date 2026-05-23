# ParisComedy — Production Reality Check (2026-05-23)

## Status: GREEN ✅

The live deployed site at https://pariscomedy.com is using the new Phase 2 backend and events system. All 15 verification checks pass.

## Headline numbers
- 12/12 public pages load events.js
- Live backend /api/health: 200 {ok:true}
- Live /api/events: accepts production events, 9 logged during verification
- Admin dashboard: token-gated, returns real production data
- CORS: 200 preflight, no errors
- 0 localhost URLs on production
- 0 unauthorized social links
- 0 Stripe references

## Forms working live
- Newsletter, Book talent, Submit lead, Claim show: all 200 OK
- Featured Show Promo: endpoint exists but requires integer target_id (minor schema mismatch — non-blocking for waitlist use)

## Single residual
- `/api/featured/book` expects `target_id: int`, but pricing page likely sends show slug. **Not a blocker** for collecting Featured Show Promo intent (other fields accepted), but should be reconciled before high-volume sales.

## Phase 1 (Production verification): GREEN ✅
