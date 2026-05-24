# ACCEPTANCE_TESTS.md — ParisComedy.com

The full canonical test suite. Anything labelled "MUST PASS" blocks release. Run before every push, and after any change that touches public surface area.

---

## How to run

```bash
python3 scripts/guardrails/check_invariants.py
```

Exit code `0` = GREEN. Any non-zero = HOLD.

---

## MUST PASS (invariants)

### Public-text invariants
The following strings MUST NOT appear in any HTML under `~/pariscomedy-push-20260517-194848/` (excluding files under `docs/`, `logs/`, `PROJECT_CANON.md`, `SCOPE_LOCK.md`, `ACCEPTANCE_TESTS.md` themselves where they may appear as quotes of forbidden patterns):
- `@pariscomedy`
- `instagram.com/pariscomedy`
- `chucklericain@gmail.com`
- `Robert Hoehn`
- `First 100 Featured listings FREE`
- `Every show listing is verified`
- `Every Eventbrite link is live`
- `34+ active shows`
- `27+ venues`
- `Stripe` (case-insensitive)

### Live-URL invariants (require network)
- `GET /` and `GET /?lang=en` return identical banner copy.
- `GET /shows.html` contains either embedded `SHOWS_DATA` JSON or a crawlable show list.
- `GET /comedians.html` contains either embedded comedian data or a crawlable comic list.
- `GET /api/listings?featured=1` MUST NOT contain `runner_email` keys with non-null values.
- `GET /api/listings?featured=1` MUST NOT contain personal real names in the `runner` field (no `Robert Hoehn`, etc.).
- `GET /api/listings?featured=1` MUST contain at least two distinct organizations / runners (no single-org dominance).

### Scraper invariants
- `daily_discover.py` exit status: if `accepted_listings == 0` AND `raw_candidates == 0` across ALL sources, the run is FAILED. The summary JSON `run_state` field must be `"FAILED"` in that case (not `"GREEN"`).
- Eventbrite-sourced listings MUST NOT be ranked above other sources.
- Public featured API MUST NOT contain only Velvet Bar + FFCN shows.

---

## SHOULD PASS (warnings, not blockers)
- Every public page has a `<title>` ≤ 60 chars and a meta description.
- Every public page has at least one canonical link.
- Every form has a submit-success and submit-error handler firing `pcTrack()`.
- PC Ollama at `100.75.13.73:11434` is reachable (warn if unreachable — scraper falls back).

---

## Manual checks per release
- `/` and `/?lang=en` rendered side-by-side: identical visible copy.
- `/shows.html`: click each weekday chip while on the Tonight tab — verify auto-switch to All Upcoming.
- `/pricing.html`: each Featured Promo radio button submits and lands on `/checkout-pending.html?plan=...` (until real SumUp products exist).
- `/admin-events.html?token=<ADMIN_TOKEN>`: dashboard loads, all 12 metric tiles populated or zero.

---

## What "GREEN" means
- `check_invariants.py` exits 0.
- All curl checks in the live verification block return empty (or only legitimate emails like `bio@pariscomedy.com`).
- Public featured API contains no personal info and no single-org dominance.
- Daily discovery's most recent summary has `run_state: "GREEN"` (or `"FAILED"` correctly raised).

## What "HOLD" means
- Any MUST PASS fails. Site stays on its previous published commit until fixed.
