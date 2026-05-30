# BACKEND.EMAIL.4-OPERATOR-DNS-RUNBOOK

**Status: IN_GIT_UNVERIFIED**
**Scope: Operator docs only. No code change. No real email. No API key in repo. No production enablement.**

---

## Robert's checklist (do this before email can go live)

### Step 1 — Create a Postmark account

1. Go to https://postmarkapp.com → Sign up
2. Choose "API" account type (not SMTP)
3. Create a server named `pariscomedy-production`
4. Under the server, create a **Transactional** message stream named `outbound`
5. Note your **Server API Token** (looks like `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)
   - **Do NOT paste this into the repository.** Store it as an environment variable:
     `POSTMARK_SERVER_TOKEN=your-token-here`

### Step 2 — Add and verify your sender domain in Postmark

1. In your Postmark account → **Sender Signatures** → **Add Domain**
2. Enter: `pariscomedy.com`
3. Postmark will show you:
   - A **DKIM TXT record** (selector `pm._domainkey`, value is a long public key string)
   - A **return-path CNAME** value (target is `pm.mtasv.net`)
4. Copy these values — you'll need them in Step 3

### Step 3 — Add DNS records in Porkbun

Log in to https://porkbun.com → Domain Management → `pariscomedy.com` → Edit DNS

#### SPF (update existing TXT record on root domain `@`)

Current value (approximate):
```
v=spf1 include:_spf.porkbun.com ~all
```

Target value (add Postmark include):
```
v=spf1 include:_spf.porkbun.com include:spf.protection.postmark.com ~all
```

> If you have multiple TXT records for `@`, merge the includes into ONE SPF record.
> Multiple SPF records will cause failures.

#### DKIM (new TXT record)

- **Host:** `pm._domainkey`
- **Type:** TXT
- **Value:** (paste the long DKIM value from Postmark — do NOT use a placeholder)
- **TTL:** 600

#### DMARC (new TXT record)

- **Host:** `_dmarc`
- **Type:** TXT
- **Value:**
```
v=DMARC1; p=none; rua=mailto:dmarc-reports@pariscomedy.com; sp=none; adkim=r; aspf=r
```
- **TTL:** 600

#### Return-path CNAME (new CNAME record)

- **Host:** `pm-bounces`
- **Type:** CNAME
- **Value:** `pm.mtasv.net`
- **TTL:** 600

#### Preserve existing MX records

Do not remove any existing MX records if you use Porkbun email forwarding or any
other inbound email service for `@pariscomedy.com`.

---

### Step 4 — Wait for DNS propagation

DNS changes can take 5 minutes to 48 hours. You can check propagation at any time:

```bash
dig TXT pariscomedy.com
dig TXT pm._domainkey.pariscomedy.com
dig TXT _dmarc.pariscomedy.com
dig CNAME pm-bounces.pariscomedy.com
```

Expected results after propagation:
- `pariscomedy.com TXT` → includes `include:spf.protection.postmark.com`
- `pm._domainkey.pariscomedy.com TXT` → long DKIM public key
- `_dmarc.pariscomedy.com TXT` → `v=DMARC1;...`
- `pm-bounces.pariscomedy.com CNAME` → `pm.mtasv.net`

### Step 5 — Verify in Postmark

1. Return to Postmark → Sender Signatures → your domain
2. Click **Verify** next to each DNS record
3. All four should show green checkmarks: SPF ✓, DKIM ✓, Return-path ✓, DMARC ✓

### Step 6 — Send one test email from Postmark dashboard (not from code)

1. In Postmark → Messages → Send a test message
2. Send to your own email address
3. Confirm delivery, check headers for DKIM=pass, SPF=pass, DMARC=pass

---

## DNS record summary table

| Record | Host | Type | Value |
|---|---|---|---|
| SPF | `@` (root) | TXT | `v=spf1 include:_spf.porkbun.com include:spf.protection.postmark.com ~all` |
| DKIM | `pm._domainkey` | TXT | *(copy from Postmark — unique to your account)* |
| DMARC | `_dmarc` | TXT | `v=DMARC1; p=none; rua=mailto:dmarc-reports@pariscomedy.com; sp=none; adkim=r; aspf=r` |
| Return-path | `pm-bounces` | CNAME | `pm.mtasv.net` |

---

## Safety rules

- `EMAIL_SEND_REAL` must remain `false` until a separate authorization phase
- `POSTMARK_SERVER_TOKEN` must NEVER be committed to the repository
- `AUTH_V2_ENABLED` must remain `false` until after email is live and tested
- No production DB migration is part of this runbook
- No login.html switch is part of this runbook

## Next technical phase (after Robert completes DNS)

**BACKEND.EMAIL.5-DNS-LIVE-VERIFY**

That phase will: verify DNS from public resolvers, confirm Postmark dashboard shows
all records green, and still NOT send real email until separately authorized.

---

## Machine-readable runbook

`data/email-operator-dns-runbook.json`
