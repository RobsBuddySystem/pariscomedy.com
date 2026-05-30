# Bug Registry

## BUG-P0-LIVE-DATA-001 — Source-of-Truth drift between live API, freshness audit, and rendered CTAs

**Status:** code/guard fix shipped (P0.LIVE-DATA-INTEGRITY.1-SOT-FIX). DB
mutations + URL repoints out of scope for this fix and remain for Robert.

**Symptom:** Public `show.html` rendered "Get tickets / source listing →" CTAs
pointing at stale or ended Eventbrite pages even when the freshness audit had
classified those rows as `needs_human_review`. Static fallbacks in `show.html`
also drifted from the live `api.pariscomedy.com/api/listings` booking_url
(e.g. `charonne` static href ended `...202099` while live API returned
`...324429`).

**Root cause:** Three independent sources of truth (live API, freshness audit
JSON, rendered HTML CTA) could diverge silently:

1. Verifier already pointed at live API, but rendered CTAs in `show.html` JS
   and in `index.html` Tonight/Promoted lanes did not gate on
   `verification_status === 'verified_24h'`.
2. Static fallback `<article>` blocks hard-coded full ticket links with no
   gate, so a `needs_human_review` row still rendered a normal external CTA.
3. No regression guard locked live API ↔ freshness audit ↔ rendered href
   parity.

**Fix (code/guard only, no DB writes):**

- `show.html` JS render now gates the `Get tickets / source listing →` CTA
  on `verification_status === 'verified_24h'`. Anything less renders a
  disabled "Tickets need review — check back soon" span.
- Four static `<article>` blocks (`charonne`, `millennial-meltdown`,
  `theatre-bo-julie`, `wednesday-night-comedy`) that already carried
  `data-verification-status="needs_human_review"` had their external "Get
  tickets" anchors replaced with the same disabled review variant.
- `index.html` Tonight and Promoted lanes both gate on `isFreshEnough(slug)`
  before emitting a `Get tickets →` anchor; otherwise render the disabled
  review variant.
- `scripts/regression_guard.py` gains six new guards:
  - `live_api_source_of_truth`
  - `api_freshness_url_parity` (ADVISORY — surfaces drift without blocking
    since DB cannot be mutated in this phase)
  - `rendered_ticket_href_parity` (ADVISORY)
  - `live_ticket_stale_token_check`
  - `no_normal_cta_for_unverified`
  - `api_not_pariscomedy_static_404_guard`

**Out of scope (Robert decision items):**

- DB UPDATE on stale `booking_url`s (e.g. charonne EB id drift).
- Theatre BO Julie repoint.
- Wednesday Night Comedy hide/keep decision.
- Any FFCN venue/address correction.
- Affiliate id enablement.

**Recurrence guard:** The six new guards run on every regression sweep. Any
new code that points at `pariscomedy.com/api/listings` (404) instead of
`api.pariscomedy.com/api/listings`, or any new CTA emit path that bypasses
freshness gating, fails the suite immediately.
