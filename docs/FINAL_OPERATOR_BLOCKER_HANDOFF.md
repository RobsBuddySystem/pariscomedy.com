# FINAL.OPERATOR-BLOCKER-HANDOFF

**For: Robert (operator)**  
**Status: HANDOFF ONLY — NO PRODUCTION ACTION TAKEN**  
**Date: 2026-05-30**

---

## Current State Summary

| Area | Status |
|---|---|
| Public site | **SAFE** — connects.html canonical, pricing "not yet live" qualifiers, login Auth V2 draft not live, admin shell noindex/read-only |
| Backend systems | **Scaffolded and disabled** — 7 V2 systems (Auth, Email, Submissions, Claims, Payments, Messaging, Tickets) fully implemented, all routes return 503 until flags enabled |
| Feature flags | **All false** (AUTH_V2_ENABLED, EMAIL_SEND_REAL, SUBMISSIONS_V2_ENABLED, CLAIMS_V2_ENABLED, PAYMENTS_ENABLED, MESSAGING_V2_ENABLED, TICKETS_ADAPTERS_ENABLED, TICKET_IMPORTS_ENABLED, AFFILIATE_LINKS_ENABLED) |
| DB migrations | **Not yet applied to production** — dry-run verified on copy, authorization pack ready |
| No production backend feature live | ✓ |

---

## Robert Action List

### A. Postmark / DNS Setup

**What**: Add 4 DNS records to pariscomedy.com to enable real email delivery.

| Record | Type | Host | Value |
|---|---|---|---|
| SPF | TXT | `@` | Add `include:spf.protection.postmark.com` to existing SPF record |
| DKIM | CNAME | `pm._domainkey` | `pm.mtasv.net.` (or Postmark-provided value) |
| DMARC | TXT | `_dmarc` | `v=DMARC1; p=quarantine; rua=mailto:postmaster@pariscomedy.com` |
| Return-path | CNAME | `pm-bounces` | `pm.mtasv.net.` (or Postmark-provided value) |

After adding records, wait 24h for propagation, then paste back:
```
SPF TXT record value: <paste full TXT record>
DKIM TXT record: <paste CNAME target>
DMARC TXT record: <paste full TXT record>
Return-path CNAME: <paste target>
Postmark dashboard status: green / verified
```

---

### B. Production DB Migration Authorization

**What**: Apply migrations 002–007 to production SQLite DB to add 17 new V2 tables. No existing data is changed. All feature flags stay false.

**When you are ready**, type exactly:

> **"I authorize production DB migration 002–007 only, with backup first, no feature flags enabled."**

**Before typing that**, confirm the exact path of your production DB:

```bash
echo $DB_PATH          # on your server
# Default: data/paris.db or /var/www/pariscomedy/data/paris.db
```

After migration, paste back:
```
Backup path: <path>
Before checksum (md5): <checksum>
After checksum (md5): <checksum>
Row counts before: shows=119, venues=45, comics=275, show_listings=179
Row counts after: shows=___, venues=___, comics=___, show_listings=___
V2 tables present (expect 17): <sqlite3 output>
/api/auth_v2/status: disabled (confirm still false)
/api/submissions_v2/status: disabled (confirm still false)
```

---

### C. Payment Provider / VAT Decision

**What**: Decide on payment provider and VAT configuration before PAYMENTS_ENABLED can ever be set true.

Minimum required before payments can go live:
- Stripe account created and `STRIPE_SECRET_KEY` + `STRIPE_WEBHOOK_SECRET` set in server env (never committed)
- 7 SumUp products created (tiers defined in `data/sumup-products-manifest.json`)
- VAT configuration confirmed (French TVA rules for digital services)
- Legal review of checkout flow

**No payment flag will be enabled until all of the above are confirmed.**

---

### D. Confirm Production DB Path (Optional Now)

```bash
# Run on your production server:
echo "DB_PATH is: $DB_PATH"
ls -lh data/paris.db 2>/dev/null || ls -lh /var/www/pariscomedy/data/paris.db 2>/dev/null
sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM shows;"  # expect 119
```

Paste back the exact path so the migration command block can be finalized.

---

## What Is Still Forbidden

Until Robert completes the above actions and ChatGPT re-verifies each step:

- No `AUTH_V2_ENABLED=true`
- No `EMAIL_SEND_REAL=true`
- No login.html switch to Auth V2 as primary
- No `PAYMENTS_ENABLED=true`
- No `MESSAGING_V2_ENABLED=true`
- No `SUBMISSIONS_V2_ENABLED=true`
- No `CLAIMS_V2_ENABLED=true`
- No `TICKETS_ADAPTERS_ENABLED=true`
- No production DB migration without Robert authorization text
- No real email sent to real users
- No secrets committed to repo

---

## Next Path After Each Action

| If Robert completes... | Then next phase is... |
|---|---|
| DNS setup + Postmark verified | Re-run `BACKEND.EMAIL.5-DNS-LIVE-VERIFY` → get EMAIL.6 real-send preflight authorization |
| DB migration authorization text | `BACKEND.DB.4-PRODUCTION-MIGRATION-EXECUTION` |
| Neither | Stop backend cutover work → focus on content/source coverage (show data quality, Eventbrite live sync, show listing freshness) |
| Payment provider decision | `BACKEND.PAYMENTS.6-STRIPE-CONFIGURATION` |

---

## Quick-reference: Phase Unlock Dependencies

```
DNS verified
  └→ EMAIL_SEND_REAL=true (Phase EMAIL.6 preflight)
       └→ AUTH_V2_ENABLED=true (Phase AUTH.8)
            └→ SUBMISSIONS_V2_ENABLED=true
            └→ CLAIMS_V2_ENABLED=true
            └→ MESSAGING_V2_ENABLED=true

DB migration applied (002–007)
  └→ TICKETS_ADAPTERS_ENABLED=true (after Auth V2)

Payment provider + VAT
  └→ PAYMENTS_ENABLED=true (independent of auth chain)
```
