# WORKSESSION HUD — Audit archive-2026-04-13 rows 2026-05-24

## Phase: DONE
## GO/HOLD: GREEN ✅

## Result
- 179 archive/import rows audited
- 14 proven (live URL + future-date or recurrence text)
- 164 quarantined (status=stale_hidden, featured=0, public_visible=0)
- 1 already canceled (velvet-openmic)
- 0 manual review

## Fixes
- Public API was leaking `source: archive-2026-04-13` — now stripped (added to _LISTING_PRIVATE_FIELDS)
- `is_past` check was overriding future-date proofs on Eventbrite recurring events — reordered priority
- Featured-venue-diversity check now skips empty list (canon-allowed)
- DB schema extended: status enum + 8 new audit columns

## Guardrails added
- scripts/guardrails/audit_archive_rows.py (probes URLs, requires proof, rehabs proven rows)
- check_invariants.check_archive_rows_clean() (cheap DB-level check)

## Live verification: 8 forbidden terms × 4 public endpoints = 0 HITS
