# PROJECT_CANON.md — ParisComedy.com

**This file is the source of truth for what the site is and is not.** Any change to a rule here requires a written Scope Change Proposal (see `SCOPE_LOCK.md`).

---

## What ParisComedy.com is

ParisComedy.com is a **neutral directory for every stand-up comedy show in Paris**. English stand-up is the editorial focus. French and bilingual shows are listed when honestly tagged. The site exists to help audiences find shows and to help comics/bookers find each other — not to promote any one organization, venue, or person.

---

## Core rules (enforced by `scripts/guardrails/check_invariants.py`)

### Editorial neutrality
- English stand-up is the focus.
- French and bilingual shows MAY be listed if tagged honestly (`language: en | fr | bi`).
- **No source is privileged.** Eventbrite is one of many. Shotgun, Dice, BilletReduc, Fever, Time Out, direct venue scrapes, manual submissions, and admin overrides are all peers.
- The Eventbrite API key we hold is scoped to **one** organization (French Fried Comedy Night). That feed must never be presented as "the live Paris comedy shows" — it represents one organizer.
- Robert's shows (Velvet Bar, FFCN) must never dominate the directory because of API access. Their rank is identical to any other show that meets the same criteria.

### Featured placement — only these reasons qualify
1. **Natural day-of-week relevance** (show runs tonight matches today's Paris weekday).
2. **Paid Featured Show Promo** (`paid_featured_until` in the future, set by admin after SumUp reconciliation).
3. **Editorial feature** (`editorial_featured: true`) with a written reason in `data/editorial_featured.json` (slug → reason → date).

No other reason creates a Featured card. No random shuffles. No "this week's pick." Empty state = empty section, not faked content.

### Single canonical source of truth for public show instances
- **The canonical source is `shows.html` → `const SHOWS_DATA`**. Every visible card on `/shows.html` renders from this array.
- The backend DB `show_listings` table feeds **only** the homepage Featured cards (via `/api/listings?featured=1`) — never the directory grid. Backend remains the system-of-record for ticketed venues; SHOWS_DATA remains the system-of-record for what the public directory shows.
- Mirror files (`js/data.js`, `data/shows_generated.json`, `generate_instances.py`) are **deprecated for new shows**. They survive only as historical/recurrence-seed references and must not contain any slug that conflicts with the canonical SHOWS_DATA or the canceled blocklist. `check_invariants.py` flags any mirror file that contains a canceled slug.
- Drift between SHOWS_DATA and the backend DB is allowed (different surfaces), but neither may surface a slug listed in `data/canceled_shows.json`.

### No manual SHOWS_DATA patching
- SHOWS_DATA in `shows.html` must never be hand-edited to add a show. New rows enter the directory through one of these paths only:
  1. `daily_discover.py` writes them after passing the LLM classifier + future-date filter, **and** the resulting ticket_url responds HTTP 2xx during the next `audit_public_shows.py --live-check` run, **or**
  2. an operator runs `python3 scripts/guardrails/audit_public_shows.py --live-check` to record HTTP 2xx in `data/url_health.json`, **or**
  3. a written approval entry is added to `data/show_approvals.json` (signed by Robert with a `valid_until` date), **or**
  4. the row carries a `recurrence_source_url` field pointing to a current venue/organizer page documenting the schedule.
- `check_invariants.py` runs the strict provenance audit on every commit; rows without one of the four proofs fail the build.
- Canceled shows are tracked in `data/canceled_shows.json`. Any slug or name listed there is hard-blocked from public APIs and SHOWS_DATA.

### Honesty
- All public claims must be provable. No "34+ shows / 27+ venues" unless the count is real.
- No "every show verified / every link live" — claim only what we can prove.
- No fake affiliate IDs. Affiliate refs stay empty + `enabled:false` until a real network confirms approval.
- Show counts are dynamic. Don't ship hard-coded numbers in public copy.

### Privacy
- Public APIs must never expose: `runner_email`, personal real names (e.g. Robert Hoehn), `chucklericain@gmail.com`, or any operator-identifying info.
- Site operator stays anonymous. Robert may appear ONLY as a rotating comic, same treatment as everyone else.
- No `@pariscomedy` Instagram handle and no `instagram.com/pariscomedy` link — we don't own that account.
- Stripe references must not appear publicly — SumUp only.

### Pricing & money
- Pricing changes require Robert's explicit approval. Current canonical tiers:
  - Comic Plus founding lifetime: €1 one-time
  - Comic Plus monthly: €1 / 30 days
  - Comic Plus annual: €12 / 365 days
  - Booker Plus intro: €1 / 30 days (intro cap)
  - Booker Plus monthly: €5 / 30 days
  - Featured Show 7d: €5
  - Featured Show 30d: €15
  - Featured Show 90d: €40
- No user is marked paid without SumUp confirmation or explicit admin action.
- Payment provider is SumUp. Never Stripe.

### Data ingestion
- Scraper must be multi-source: Eventbrite organizer pages + Eventbrite public search + BilletReduc + Shotgun + Dice + Fever (when wired) + Time Out + direct venue sites + manual submissions + manual admin override.
- If all sources return zero events, the run is **FAILED**, not "successful."
- Every scrape run writes raw candidates, accepted listings, rejected listings + reason, source, timestamp, errors, and a GREEN/FAILED state.

---

## What ParisComedy.com is NOT
- Not a private promotion site for Velvet Bar or FFCN.
- Not a feed of one Eventbrite organization.
- Not a curated "best shows" list — every qualifying show goes in.
- Not a paid placement site where money buys editorial coverage (paid Featured Promos exist but are clearly marked).
