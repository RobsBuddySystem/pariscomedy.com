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
