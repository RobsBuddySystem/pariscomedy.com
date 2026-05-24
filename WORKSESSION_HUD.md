# WORKSESSION HUD — Rollback canceled Velvet Open Mic / provenance audit 2026-05-24

## Phase: DONE
## GO/HOLD: GREEN ✅

## Rollback
- 4 invented Velvet Open Mic rows purged from SHOWS_DATA (canonical + push)
- Backend DB row id=1 status → 'canceled' (audit row preserved)
- Backend API hard-blocks velvet-openmic regardless of any query parameter
- generate_instances.py / js/data.js / shows_generated.json / comedians.html all purged
- Live verified via curl + Playwright DOM

## Guardrails added
- data/canceled_shows.json — canonical blocklist
- check_invariants.check_canceled_blocklist
- check_invariants.check_show_provenance
- scripts/guardrails/audit_public_shows.py — per-row provenance audit

## Wednesday shows re-audited
All 6 named shows (FFCN, Velvet Showcase, Kiss, South, Comedy Crush, The Dissident) have full provenance.

## Commits pushed
- 61a22a4 backend (PUBLIC_BLOCKED_SLUGS + schema)
- a570d10 push (purge + blocklist + audit + extended invariants)

## Final status: GREEN ✅
