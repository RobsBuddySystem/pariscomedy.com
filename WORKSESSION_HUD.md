# WORKSESSION HUD — pariscomedy.com 2026-05-23

## Three-phase verification session: DONE

| Phase | Status | Blockers |
|-------|--------|----------|
| **1. Production verification** | ✅ GREEN | None |
| **2. Revenue activation (affiliate)** | 🟡 HOLD | Robert must register for 8 programs (Eventbrite first) |
| **3. Payment activation (SumUp)** | 🔴 HOLD | 1 SumUp product covers 2 prices — need 7 distinct products |

---

## Phase 1 — Production verification: GREEN ✅
- 15/15 checks pass against live site (https://pariscomedy.com)
- Backend (https://api.pariscomedy.com): /api/health 200, /api/events 200, /api/admin/events 200 with token
- All 12 public pages load events.js
- CORS OK, no localhost leaks, no Stripe, no @pariscomedy
- All major form endpoints respond OK (newsletter, book, leads, claim-show)

## Phase 2 — Revenue activation: HOLD pending registration
- Infrastructure ready: /r.html + data/affiliates.json + affiliate_click tracking all live
- NO fake IDs in production (placeholder string "pariscomedy")
- Checklist written: docs/revenue/Affiliate-Setup-Checklist.md
- Order of priority: Eventbrite → GetYourGuide → BilletReduc → others

## Phase 3 — Payment activation: HOLD
- Comic Plus + Booker Plus share one SumUp checkout URL (€1 product Q9TM3HKU)
- SumUp does not support recurring; recommend prepaid one-shot periods (7 SKUs)
- Featured Show Promo: endpoint exists, no SumUp URLs yet, target_id schema mismatch
- Authorization rule held: nobody marked paid without verified or admin action

---

## Next fastest revenue-positive step

1. **Robert signs up for Eventbrite Affiliate Program** (24-hour approval) → paste real ref into `data/affiliates.json` → ~80% of ticket clicks earn 1.5% commission immediately.

That single action turns existing infrastructure into recurring revenue.
