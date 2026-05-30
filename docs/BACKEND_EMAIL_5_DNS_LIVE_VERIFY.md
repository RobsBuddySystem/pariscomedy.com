# BACKEND.EMAIL.5-DNS-LIVE-VERIFY

**Status: IN_GIT_UNVERIFIED — BLOCKED_NEEDS_OPERATOR_DNS**
**Scope: DNS verification only. No real email sent. No flags changed.**

## Live DNS State (2026-05-30)

| Record | Status | Details |
|---|---|---|
| SPF | PRESENT_BUT_MISSING_POSTMARK | `v=spf1 include:_spf.porkbun.com ~all` — Postmark include missing |
| DKIM (`pm._domainkey`) | MISSING | No record at Porkbun |
| DMARC (`_dmarc`) | MISSING | No record at Porkbun |
| Return-path CNAME (`pm-bounces`) | MISSING | No CNAME to pm.mtasv.net |
| MX | PRESENT | Porkbun forwarding (unaffected by Postmark DNS) |

## Operator Actions Required (Robert)

1. Create Postmark account (if not done)
2. Add sender signature for `pariscomedy.com` in Postmark dashboard
3. **Update SPF at Porkbun**: add `include:spf.protection.postmark.com`
   - Current: `v=spf1 include:_spf.porkbun.com ~all`
   - Required: `v=spf1 include:_spf.porkbun.com include:spf.protection.postmark.com ~all`
4. **Add DKIM at Porkbun**: get TXT value from Postmark dashboard
   - Host: `pm._domainkey`
   - Value: from Postmark → Sender Signatures → pariscomedy.com → DKIM
5. **Add DMARC at Porkbun**:
   - Host: `_dmarc`
   - Value: `v=DMARC1; p=none; rua=mailto:dmarc@pariscomedy.com`
6. **Add CNAME at Porkbun**:
   - Host: `pm-bounces`
   - Target: `pm.mtasv.net`
7. Wait for DNS propagation (up to 24h)
8. Click "Verify" in Postmark dashboard for each record

## Config Status

- `EMAIL_SEND_REAL=false` (unchanged)
- `AUTH_V2_ENABLED=false` (unchanged)
- `POSTMARK_SERVER_TOKEN` not in repo

## Next Phase

After Robert completes DNS setup and all 4 records verified in Postmark:
**BACKEND.EMAIL.6-DRY-RUN-TO-REAL-SEND-PREFLIGHT**

Until then: **BLOCKED_NEEDS_OPERATOR_DNS**.
