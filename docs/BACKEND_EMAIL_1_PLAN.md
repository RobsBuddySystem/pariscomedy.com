# BACKEND_EMAIL_1_PLAN — transactional email + domain plan

**Phase:** BACKEND.EMAIL.1-PLAN-SCAFFOLD
**Authorized:** ChatGPT 2026-05-30
**Status:** plan + dry-run scaffold. No real sending. No provider API key. Auth V2 still disabled.

## Architecture

### Inbound

| Path | Choice | Notes |
|---|---|---|
| `chuck@pariscomedy.com`     | Cloudflare Email Routing → Robert's personal inbox | live |
| `payments@pariscomedy.com`  | Cloudflare Email Routing → Robert | Stripe receipt reply-to |
| `support@pariscomedy.com`   | Cloudflare Email Routing → shared mailbox (Postmark inbound webhook later for thread-reply parsing) | new |
| `no-reply@pariscomedy.com`  | Cloudflare Email Routing → drop / bounce | outbound only |

### Outbound transactional

| Provider | Recommendation | Reason |
|---|---|---|
| **Postmark** | RECOMMENDED | best deliverability for transactional; EU residency option; clean templating; bounce/complaint webhooks |
| Resend | fallback | newer; cleaner DX but younger reputation |
| SES | not recommended | requires more deliverability work; no managed templating |
| SMTP (Gmail app password) | dev only | already in main.py; do not promote to magic-link sender |

Magic-link, submission decisions, claim decisions, messaging notifications all flow through the same mailer interface (`backend/mailer.py`).

### DNS plan

```
TYPE    HOST                              VALUE
TXT     pariscomedy.com                   v=spf1 include:_spf.mx.cloudflare.net include:spf.mtasv.net -all
TXT     pm._domainkey.pariscomedy.com     <Postmark-supplied DKIM 2048-bit public key>
TXT     _dmarc.pariscomedy.com            v=DMARC1; p=quarantine; rua=mailto:dmarc-reports@pariscomedy.com; ruf=mailto:dmarc-reports@pariscomedy.com; sp=quarantine; aspf=r; adkim=r
```

Rollout sequence:
1. Add SPF + DKIM + DMARC `p=none` for 7 days (monitor only)
2. Tighten to `p=quarantine` for 30 days (monitor rua reports)
3. Tighten to `p=reject` after clean 30-day window

### Security

- No real API keys committed; `env.example` only documents placeholder variable names (additions deferred until provider integration phase)
- Magic-link tokens never logged in production mode — `mailer.send` only logs `template + recipient + subject` at INFO when sending
- Per-template rate limits: magic-link reuses the auth_v2 10/email/hour gate
- Audit logging: every outbound email recorded into `audit_events_v2` (action `email.send.<template>`)
- Token never appears in stderr when `EMAIL_SEND_REAL=true` AND provider != dryrun

### Deliverability

- `From: no-reply@pariscomedy.com` (EMAIL_FROM env var)
- `Reply-To: support@pariscomedy.com` (EMAIL_REPLY_TO env var)
- Plain text + HTML pair per template
- Unsubscribe link on opt-in templates (messaging notifications) — not needed for transactional auth emails

## Dry-run scaffold (this phase)

`backend/mailer.py`:
- Single `send(OutgoingEmail)` entry point
- `EMAIL_SEND_REAL` env var defaults `false`
- `EMAIL_PROVIDER` defaults `"dryrun"`
- Dry-run path: validates from/to/reply-to addresses, captures payload in-process for tests, writes one stderr line (`[mailer DRY-RUN] template=… to=… subject=…`), returns `{delivered:false, mode:"dryrun"}`
- Real-send path (both env vars must opt in): raises `NotImplementedError` — provider wiring lands in `BACKEND.EMAIL.1-PROVIDER`
- One template: `magic_link_email(to, token, base_url)` — text + HTML pair, link only, token in URL not in subject

`backend/tests/test_mailer.py`:
- 7 tests, all PASS:
  - dry-run captures payload
  - magic-link template includes link, plain-text + HTML, subject does NOT contain token
  - invalid `to` address fails closed
  - invalid `from` address fails closed
  - status reports dry-run state
  - real-send with provider=dryrun stays dry-run
  - real-send with unconfigured provider raises NotImplementedError

## Auth V2 wiring (NOT THIS PHASE)

`auth_v2.py` currently writes magic-link tokens to stderr when `AUTH_V2_DRY_RUN_MAILER=true`. The mailer abstraction in this phase is ready for `auth_v2` to call instead — that swap lands when `BACKEND.EMAIL.1-PROVIDER` enables real sending, NOT before.

## What is still NOT live

- Real outbound email from any address
- Provider API keys (no Postmark / Resend / SES configuration)
- DNS changes (SPF / DKIM / DMARC not yet applied)
- Auth V2 still disabled
- login.html unchanged
- Inbound webhook parsing (Postmark inbound) — deferred to BACKEND.MESSAGING.1 dependency

## Rollback

`git revert <commit-sha>` removes `mailer.py` + tests + this doc. No DNS, no env, no production behavior change.

## Related

- [[PHASE_LEDGER]]
- [[BACKEND_PLAN_1]]
- [[BACKEND_RISK_REGISTER]] — R-10 (DMARC misconfig), R-11 (forwarding loop) addressed by rollout sequence
- [[BACKEND_IMPLEMENTATION_SEQUENCE]] — this is phase #4
- [[BACKEND_AUTH_1_ROUTER_INTEGRATION_DISABLED]] — auth side waiting on this email side
