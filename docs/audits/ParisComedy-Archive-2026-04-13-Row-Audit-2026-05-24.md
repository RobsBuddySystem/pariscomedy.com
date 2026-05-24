# ParisComedy — archive-2026-04-13 Row Audit (2026-05-24)

## Status: GREEN ✅

## Total
- **Archive/import rows found:** 179 in `show_listings` (34 from archive-2026-04-13, 145 from plateaux-liste-26).
- **Archive rows in `shows` table:** 0 (only 2 future rows, neither archive-sourced).

## Outcome
| Action | Count |
|--------|------:|
| Kept public (proven) | **14** |
| Already canceled | 1 (velvet-openmic) |
| Quarantined (status=stale_hidden) | **164** |
| Manual review / no proof yet | 0 |

## Proof for each kept row
| id | slug | proof category | proof |
|----|------|----------------|-------|
| 2 | velvet-comedy | future date | JSON-LD startDate `2026-05-27` |
| 3 | ffcn | future date | JSON-LD startDate `2026-05-27` |
| 5 | green-light | recurrence | "every <weekday>" text |
| 6 | cuba-compagnie | recurrence | recurring text |
| 8 | rocket | recurrence | recurring text |
| 10 | comedy-crush | recurrence | recurring text |
| 11 | millennial-meltdown | recurrence | recurring text |
| 15 | wednesday-night-comedy | recurrence | recurring text |
| 18 | theatre-bo-julie | recurrence | recurring text |
| 23 | comedy-lab-chat-noir | recurrence | recurring text |
| 24 | green-mic-showcase | recurrence | recurring text |
| 25 | coucou-friday | recurrence | recurring text |
| 28 | smash | recurrence | recurring text |
| 31 | charonne | recurrence | recurring text |

All 14 had ticket_url that returned HTTP 200 + at least one of:
- JSON-LD Event.startDate ≥ today, OR
- explicit recurrence text ("every Wednesday", "tous les lundis", "weekly", etc.)

`verified_at` updated to today for all kept rows.

## Quarantined buckets
| Reason | Count |
|--------|------:|
| HTTP 200 but no future date AND no recurrence text | ~33 |
| URL HTTP 0 (no URL set or unreachable) | ~131 |

164 rows total. All carry `previous_status`, `quarantine_reason`, `quarantined_at`, `quarantined_by` for audit.

## Root cause of prior public exposure
- Original 2026-04-13 seed imported `archive-2026-04-13` rows with `status='active'` and `featured=1` on a few; no provenance check existed.
- The `source` field was being exposed publicly in `/api/listings`.
- The `is_past` check incorrectly short-circuited future-date proofs on Eventbrite recurring events.

## Public endpoint verification (after fix)
```
GET /api/listings                    → 14 rows, none with archive- source visible
GET /api/listings?featured=1         → 0 rows (canonically empty until editorial featured assigned)
GET /api/shows                       → no velvet-openmic, no other quarantined titles
GET /shows.html                      → 41 SHOWS_DATA rows (separate canonical, all proven)

Live grep across 8 forbidden terms × 4 endpoints → 0 HITS.
```

## Guardrail updates
- `audit_archive_rows.py` NEW — enumerates archive rows, probes live URL, requires future-date OR recurrence proof OR signed approval.
- `check_invariants.check_archive_rows_clean()` NEW — DB-level check: any active+public archive row must have today's `verified_at`.
- `audit_archive_rows.py` performs rehab pass: stale_hidden rows that newly prove themselves are restored to `previous_status` with `verified_at=today`.
- Public serializer now strips: `source`, `verification_source`, `cancellation_reason`, `quarantine_*`, `previous_status`, `verified_by`, `blocked_from_auto_regeneration`, `public_visible` (in addition to existing PII fields).
- Featured-venue-diversity check skips empty featured list (canonically allowed).

## Files changed
- `~/.openclaw/workspace/apps/paris-comedy/main.py` — expanded `_LISTING_PRIVATE_FIELDS`.
- `~/pariscomedy-push-20260517-194848/scripts/guardrails/audit_archive_rows.py` (NEW)
- `~/pariscomedy-push-20260517-194848/scripts/guardrails/check_invariants.py` — `check_archive_rows_clean()`, empty-featured-list fix.
- DB schema: extended `status` CHECK to include `stale_hidden`; added columns `quarantine_reason`, `quarantined_at`, `quarantined_by`, `previous_status` (and from prior session: `cancellation_reason`, `public_visible`, `blocked_from_auto_regeneration`, `verified_by`).
- DB rows changed: 164 archive/import rows transitioned to `stale_hidden`. 14 archive rows refreshed to `verified_at=today`. 1 canceled row unchanged.

## Commits
- backend repo: serializer fields update + cache-control helper
- push repo: audit script + invariants update + audit doc + logs

## Final status: **GREEN ✅**
