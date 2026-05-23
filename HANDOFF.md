# pariscomedy.com — Backend System Handoff

**Written 2026-05-20.** Exhaustive list of what exists, what is missing, and what
is needed for a complete, self-running backend. Read top to bottom before
touching production.

---

## 1. What exists today (current architecture)

| Layer | What it is | Where |
|---|---|---|
| Frontend | Static HTML/CSS/JS, no build step | `RobsBuddySystem/pariscomedy.com` repo → GitHub Pages |
| Backend | FastAPI (Python) | `~/.openclaw/workspace/apps/paris-comedy/main.py` |
| Backend host | Mac Studio, `uvicorn` on `127.0.0.1:8765` | started manually with `nohup` |
| Public URL for API | Cloudflare **quick tunnel** (ephemeral) | `cloudflared tunnel --url http://localhost:8765` |
| API URL pointer | `api-config.json` in the repo | frontend reads it at runtime |
| Lead storage | `data/leads.jsonl` (new routes) + SQLite `messages_review_queue` (old route) | `~/.openclaw/workspace/apps/paris-comedy/data/` |
| DB | SQLite `paris.db` | same `data/` dir |
| Payments | SumUp hosted links (cards) | `Q9TM3HKU` = €1 fixed; `Q7EXVGM8` = open-amount tip |
| Scrapers | `validate_tickets.py`, `discover_shows.py`, `comic_actuality.py` | `scripts/` in the repo |
| Hourly job | `scripts/hourly_validate.sh` + LaunchAgent | Mac (currently blocked by TCC) |
| Admin | `admin-messages.html` (ADMIN_TOKEN gated) | reads SQLite queue only |

**Working revenue path:** form → `LeadCapture.js` → `/api/leads` (or named route)
→ `leads.jsonl`. Frontend has a localStorage + mailto fallback if the API is down.
SumUp €1 link is wired into Comic Plus (lifetime) and Booker Plus (first month).

---

## 2. CRITICAL — blocks the system from actually working

| # | Missing / broken | Impact | Fix |
|---|---|---|---|
| C1 | **SMTP not configured** — no `env` file with `SMTP_USER`/`SMTP_PASS` | No signup ever emails the operator. Notifications silently skipped. | Create `~/.openclaw/workspace/apps/paris-comedy/env` with Gmail address + app password + `NOTIFY_EMAIL`. Restart backend. |
| C2 | **Ephemeral Cloudflare tunnel** | Tunnel URL changes on every restart → `api-config.json` goes stale → all forms hit a dead URL. | Create a **named** Cloudflare tunnel (`cloudflared tunnel create pariscomedy`) bound to a stable hostname, e.g. `api.pariscomedy.com`. Pin that in `api-config.json` once, forever. |
| C3 | **Backend is a manual `nohup` process** | Dies on reboot / crash, no auto-restart. | LaunchAgent plist with `KeepAlive` for the uvicorn process (template in `backend/README.md`). |
| C4 | **No payment ↔ signup reconciliation** | When someone pays €1 on SumUp, nothing links the payment to their lead. You cannot tell who actually paid vs. who only filled the form. | SumUp webhook → an endpoint that marks the lead `paid`. Requires C2 (stable URL) first. |
| C5 | **No "first 100" counter** | The founding-member cap is not tracked or enforced — the €1 lifetime offer is currently unbounded. | A counter (DB row or file) incremented on each confirmed Comic Plus payment; the pricing page reads it and closes the offer at 100. |

---

## 3. Accounts & membership — the biggest gap

The site sells "Comic Plus" and "Booker Plus" but there is **no account system**.

| # | Missing | Needed |
|---|---|---|
| A1 | No member sign-in / login on the public site | Email-based login (magic link is simplest — the backend already does this for the booker dashboard via `/api/booker/auth`). |
| A2 | No "sign in" button anywhere | Add to nav once A1 exists. |
| A3 | Paid features can't be gated | Messaging, highlighted profile, priority placement — none can actually be delivered without knowing who is logged in + paid. |
| A4 | No membership state | A `members` table: email, plan, status (pending/active/cancelled), paid_at, founding_number. |
| A5 | No activation flow | After SumUp payment → member flipped to `active` → welcome email + Founding Member badge. |
| A6 | Founding Member badge not shown | `founding-member-badge.svg` exists but is never attached to a comic's public profile card. |
| A7 | No member dashboard | Members can't see their status, edit profile, cancel. |
| A8 | Booker dashboard auth is separate | `/api/booker/auth` exists but is not linked to Booker Plus membership. |

---

## 4. Payments & invoicing

| # | Missing | Notes |
|---|---|---|
| P1 | No recurring billing for Booker Plus | "€1/month invoiced by email" is currently just text. SumUp one-off links don't auto-recur. Plan: SumUp subscription product when ready; until then email invoicing each month. SumUp only — no other processor. |
| P2 | No invoice generation/tracking | Nothing creates, numbers, sends or stores invoices. Required for accounting (Pompei). |
| P3 | No payment record | No table of who paid, how much, when, refunds. |
| P4 | SumUp merchant is labelled **"FFC"**, not "Paris Comedy" | Rename in the SumUp dashboard, or confirm FFC is the intended legal payee. |
| P5 | Lightning Address `payments@pariscomedy.com` does not work | 404 — needs `.well-known/lnurlp/payments` + stable public callback → SweetPea LND. Parked. See `project_pariscomedy_lightning_address_todo` in memory. |
| P6 | No refund process | Define + document. |

---

## 5. Data & storage

| # | Missing | Notes |
|---|---|---|
| D1 | Two lead stores | `leads.jsonl` + SQLite `messages_review_queue`. Unify into one. |
| D2 | No admin view of `leads.jsonl` | `admin-messages.html` only shows the SQLite queue. Build a leads view. |
| D3 | `leads.jsonl` unbounded, no dedup | Grows forever; no schema enforcement. |
| D4 | Show/comic/venue data is flat JSON, hand+scrape maintained | No single source of truth; drift risk. |
| D5 | Backups | `scripts/backup_db.sh` covers `paris.db` only, and is **not scheduled**. `leads.jsonl` is not backed up at all. |
| D6 | No GDPR deletion path | EU PII collected; must be able to delete a person on request. |

---

## 6. Email & notifications

| # | Missing |
|---|---|
| E1 | Transactional email: welcome, payment received, invoice, booking confirmation — none exist. |
| E2 | Newsletter: signups are captured but nothing sends a newsletter. |
| E3 | `NOTIFY_EMAIL` defaults to the operator's personal inbox — confirm the right delivery address. |

---

## 7. Scrapers & data quality

| # | State |
|---|---|
| S1 | `discover_shows.py` / `comic_actuality.py` write staging files (`discovered_shows.json`, `comic_actuality.json`); merging into live data is manual / operator-gated. No merge tool. |
| S2 | Hourly job fragile: macOS TCC blocks the LaunchAgent (needs Full Disk Access on `/bin/zsh`); tunnel rot. |
| S3 | No alerting when the scraper finds conflicts (`scrape_conflicts.json`). |
| S4 | Eventbrite events go stale (e.g. "Open Mic Express April 17" — ended). Validator catches these, but only when the hourly job runs. |

---

## 8. Operations & monitoring

| # | Missing |
|---|---|
| O1 | No uptime monitoring / alerting for the backend or the site. |
| O2 | No analytics — visitor count, conversion rate unknown. |
| O3 | No staging environment — every change goes straight to production. |
| O4 | No runbook for: restarting the backend, rotating the tunnel, checking leads. |
| O5 | The automation agent is not taught any of this — cannot run the site independently. |
| O6 | Secrets would sit in a plaintext `env` file — no secrets management. |

---

## 9. Legal & compliance (operator: confirm these)

| # | Missing |
|---|---|
| L1 | No privacy policy — site collects names, emails, takes payments. |
| L2 | No terms of service. |
| L3 | No GDPR basis documented (EU users + PII). |
| L4 | No cookie/localStorage consent notice. |
| L5 | Legal payee unclear — is FFC the registered business, or a Paris Comedy SASU? |

---

## 10. Things not previously raised but needed

- **SumUp webhook** — without it you never programmatically know who paid (see C4).
- **Founding-member counter** must be live or the "first 100" promise is meaningless (C5).
- **The badge** must actually render on the comic's directory card (A6).
- **Backups must include `leads.jsonl`**, not just `paris.db` (D5).
- **Rate limiting on `/api/leads`** — the old `/api/message` is rate-limited; the new lead routes are not (spam risk).
- **Form abuse** — honeypot exists, but no per-IP throttle on the new routes.
- **Mobile QA** — never systematically tested on phones.
- **An owner for the recurring scraper merge** — discovered shows need a human/agent to approve into live data.

---

## 11. Recommended build order

1. **C1 SMTP** (5 min, you) — so you actually get notified.
2. **C2 named tunnel** (~1 h) — stable API URL, stops the rot.
3. **C3 LaunchAgent** (~30 min) — backend survives reboots.
4. **D2 + D5** — admin leads view + scheduled backups incl. `leads.jsonl`.
5. **C4 + C5** — SumUp webhook + founding counter (needs C2 done first).
6. **Section 3 — accounts & membership** — the real product. Magic-link login,
   `members` table, activation, badge. This is the largest piece.
7. **P1/P2 — invoicing + recurring** for Booker Plus.
8. **Section 9 — legal pages** before any real marketing push.

Items 1–5 make the *current* revenue path trustworthy. Item 6 is what turns
"a form that captures a lead" into "a membership someone can actually log into
and use."

---

## 12. Day-to-day runbook (until automated)

```bash
# Check the backend is up
curl -s http://127.0.0.1:8765/api/health

# See all signups
cat ~/.openclaw/workspace/apps/paris-comedy/data/leads.jsonl

# Restart the backend
cd ~/.openclaw/workspace/apps/paris-comedy
kill $(pgrep -f "uvicorn main:app"); sleep 2
nohup venv/bin/uvicorn main:app --host 0.0.0.0 --port 8765 > /tmp/pariscomedy-backend.log 2>&1 &

# Restart the tunnel + repoint api-config.json (until C2 is done)
pkill cloudflared
nohup cloudflared tunnel --url http://localhost:8765 > /tmp/tunnel.log 2>&1 &
grep -o 'https://[a-z-]*\.trycloudflare\.com' /tmp/tunnel.log | head -1
# put that URL into api-config.json, commit, push

# Check / fix links before any deploy
python3 scripts/check_links.py
```
