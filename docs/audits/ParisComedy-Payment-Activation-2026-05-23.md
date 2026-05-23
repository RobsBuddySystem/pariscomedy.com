# ParisComedy — Payment Activation Audit (2026-05-23)

## Status: HOLD ⚠️

Payment infrastructure exists but has gaps that block clean activation.

---

## SumUp integration state

### What works ✅
- SumUp REST sync: `/api/admin/payments/sync-sumup` pulls transactions via `SUMUP_API_KEY`
- Manual import: `/api/admin/payments/import-sumup` accepts CSV
- Pending → paid reconciliation: `/api/admin/payments/{id}/mark-paid`
- Hosted checkout URL pattern: `https://pay.sumup.com/b2c/<PRODUCT_CODE>?utm_source=...&utm_campaign=...`
- Pending-payment matcher: name/email/amount fuzzy-match in `_match_sumup_row()`

### Blocker 1: Both products share one checkout URL 🔴
Lines 1614 + 1622 of main.py:
```
"comic_plus_lifetime":  checkout_url: https://pay.sumup.com/b2c/Q9TM3HKU?utm_campaign=comic_plus
"booker_plus_monthly":  checkout_url: https://pay.sumup.com/b2c/Q9TM3HKU?utm_campaign=booker_plus
```
Same product code `Q9TM3HKU` — a buyer cannot pay a different amount via SumUp hosted page; the page is hard-coded to one price.
**Fix:** create two distinct SumUp products (one €1, one €5) and update each `checkout_url`.

### Blocker 2: SumUp does not support recurring billing in the hosted Payment Link product 🔴
Confirmed via SumUp docs (as of May 2026). Two options:

**Option A (RECOMMENDED): prepaid one-shot periods**
| Plan | Price | Period | SumUp product code | Status |
|------|-------|--------|---------------------|--------|
| Comic Plus monthly | €1 | 30 days | TODO_NEW_PRODUCT_CMP_MONTHLY | ⏳ create |
| Comic Plus annual | €12 | 365 days | TODO_NEW_PRODUCT_CMP_ANNUAL | ⏳ create |
| Booker Plus monthly intro | €1 | 30 days × 6 | TODO_NEW_PRODUCT_BKR_INTRO | ⏳ create |
| Booker Plus monthly | €5 | 30 days | TODO_NEW_PRODUCT_BKR_STD | ⏳ create |
| Featured Show 7d | €5 | 7 days | TODO_NEW_PRODUCT_FEAT_7 | ⏳ create |
| Featured Show 30d | €15 | 30 days | TODO_NEW_PRODUCT_FEAT_30 | ⏳ create |
| Featured Show 90d | €40 | 90 days | TODO_NEW_PRODUCT_FEAT_90 | ⏳ create |

Each prepaid period sets an expiry date in the DB. Renewal = new SumUp payment.

**Option B: integrate a different processor with recurring** (Stripe Billing, Mollie, GoCardless) — adds complexity, conflicts with current SumUp-only rule.

→ **Recommendation: Option A.** Faster, cheaper, no new payment processor.

### Blocker 3: Featured Show Promo schema mismatch 🟡
`/api/featured/book` requires `target_id: int` but show slugs are strings. Pricing CTA cannot submit without a numeric show ID. **Fix:** change schema to accept `target_slug: str` (lookup → int internally), or coerce in handler.

### Blocker 4: DB schema still has Stripe column names 🟢 (cosmetic)
`featured_bookings.stripe_session_id` / `stripe_payment_intent_id` columns exist in the schema but are unused. Renaming requires a migration. **Not user-visible**, but does not match the "no Stripe references" rule. **Fix:** rename in migration to `provider_session_id` / `provider_intent_id`.

---

## Payment flow audit per product

### Comic Plus (€1 lifetime, founding-100)
- Pricing CTA → SumUp hosted page (Q9TM3HKU) → user pays → webhook **NOT configured** → admin runs `/api/admin/payments/sync-sumup` → matches by email → marks paid.
- **Time to paid status: minutes to hours (depends on admin sync cadence).**
- Status: ⚠️ HOLD on shared product code (Blocker 1)

### Booker Plus (€5/mo, intro €1/mo for 6 months)
- Same SumUp product as Comic Plus (Blocker 1).
- No recurring billing in SumUp hosted (Blocker 2). Currently a "one-time €1" landing page.
- Status: ⚠️ HOLD

### Featured Show Promo (€5/7d, €15/30d, €40/90d)
- `/api/featured/book` endpoint exists; intent saved to `featured_bookings` table.
- No SumUp checkout URLs configured yet for these three tiers (Blocker 1 extended).
- `paid_featured_until` not set until admin manually reconciles.
- Status: ⚠️ HOLD — works as a waitlist; not a real payment flow yet.

---

## Payment authorization rule

`mark-paid` requires admin token. No code path sets `payment_status='paid'` without either:
1. SumUp sync match (real transaction in SumUp account)
2. Explicit admin action via `/api/admin/payments/{id}/mark-paid`

✅ **Rule held**: no user is marked paid without verified or admin-approved confirmation.

---

## Final remaining blockers

| # | Blocker | Severity | Effort |
|---|---------|----------|--------|
| 1 | One SumUp product for two prices (Comic Plus + Booker Plus) | 🔴 HIGH | 30min (create 7 products in SumUp dashboard) |
| 2 | Wire 7 distinct SumUp checkout URLs in main.py | 🔴 HIGH | 1h |
| 3 | Featured Show Promo target_id schema | 🟡 MED | 30min |
| 4 | DB legacy Stripe column names | 🟢 LOW | 1h migration |
| 5 | SumUp webhook for instant payment confirmation (optional) | 🟡 MED | 2h |
| 6 | Featured Promo expiry cron (sets paid_featured_until=NULL on expire) | 🟡 MED | 1h |

---

## Phase 3 (Payment activation): HOLD ⚠️

Cannot activate without creating real SumUp products and wiring distinct URLs.
