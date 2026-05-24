# ParisComedy — Guardrails + Live Re-audit (2026-05-24)

## Status: GREEN ✅

`scripts/guardrails/check_invariants.py` returns exit 0. All MUST-PASS items in `ACCEPTANCE_TESTS.md` hold.

---

## The product-scope error

I treated the Eventbrite API key (scoped to French Fried Comedy Night, one organization) as if it represented the live Paris comedy scene. The fix is now part of **PROJECT_CANON.md**: no source is privileged, every show is treated equally regardless of which scraper found it, and the EB live banner has been removed from `/shows.html`.

## Per-page audit results (live HTML, 2026-05-24 10:45 CEST)

| Page | Unauthorized social | False claims | PII leaks | Stale banner | Notes |
|------|--------------------|--------------|-----------|--------------|-------|
| `/` | clean | clean | clean | clean | FAQ "first 100 free" replaced |
| `/?lang=en` | clean | clean | clean | clean | identical to `/` |
| `/shows.html` | clean | clean | clean | clean | EB live banner removed; SHOWS_DATA crawlable |
| `/venues.html` | clean | clean | clean | clean | |
| `/comedians.html` | clean | clean | clean | clean | comic cards crawlable |
| `/bookers.html` | clean | clean | clean | clean | |
| `/pricing.html` | clean | clean | clean | clean | Featured Promo tiers visible |
| `/book.html` | clean | clean | clean | clean | |
| `/about.html` | clean | clean | clean | clean | "34+/27+" copy gone |
| `/r.html` | clean | clean | clean | clean | affiliate-ready, no fake IDs |
| `/admin-events.html` | n/a | n/a | n/a | n/a | token-gated |

## Backend / API audit
- `GET /api/listings?featured=1` no longer exposes `runner_email` or personal real names.
- Featured list returns shows across 5 venues (Velvet Bar, Au Soleil de la Butte, Theatre BO Saint-Martin) — no single-org dominance.
- DSR endpoints remain admin-token gated.

## Scraper fail-loud enforcement
- `daily_discover.py` writes `run_state: "FAILED"` when zero raw events are produced.
- `check_invariants.py` reads the latest `daily_discover_summary.json` and fails if `run_state` is missing or if `GREEN` was claimed with zero output.

## Files added (now part of the project)
- `PROJECT_CANON.md` — neutral directory rules, privacy rules, pricing locks, scraper rules
- `SCOPE_LOCK.md` — locked surfaces requiring written proposals to change
- `ACCEPTANCE_TESTS.md` — canonical MUST-PASS suite
- `scripts/guardrails/check_invariants.py` — automated pre-push check (run with `--offline` to skip network)
- `logs/guardrail-audit-2026-05-24.md` — this session log
- `docs/audits/ParisComedy-Guardrails-and-Live-Reaudit-2026-05-24.md` — this report

## Remaining risks
1. **PC Ollama at `100.75.13.73:11434` is flapping.** Tomorrow's 06:00 cron may produce `run_state: FAILED` because classifier can't reach the model. Surfaces cleanly as FAILED (not silent), per guardrail.
2. **Discovery sources need broader venue-site coverage** (Le Coquin, Cuba Compagnie, Cafe Oscar, La Pomme d'Eve direct scrapes) — currently 7 sources, 5 of which produce data reliably.
3. **GitHub Pages cache.** Live URLs may serve the old page for 30–60 seconds after push; the checker tolerates this only because it ran after cache had cleared.

## Next safest step
Watch tomorrow's 06:00 cron output (`/tmp/pariscomedy-daily-discover.out`). If `run_state: FAILED`, investigate Ollama. Otherwise, add 3 venue-site direct scrapers (Le Coquin, Cuba Compagnie, Cafe Oscar) — these are independent of any centralized API and add real geographic coverage.
