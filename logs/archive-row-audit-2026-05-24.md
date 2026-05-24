# Archive Row Audit — 2026-05-24

## Inventory
- 179 archive/import rows in `show_listings` (1 was already canceled = velvet-openmic).
- 178 rows audited via `audit_archive_rows.py` (probing live ticket_url + JSON-LD startDate + recurrence-text regex + past-event regex).
- 0 archive rows in `shows` table (different schema; only 2 future rows total, none archive-sourced).

## Outcome
| Bucket | Count |
|--------|------:|
| Kept public (proof: future date or explicit recurrence text) | **14** |
| Already canceled (velvet-openmic) | 1 |
| Quarantined → status=stale_hidden, featured=0, public_visible=0 | **164** |
| Manual-review / approval-pending | 0 |

## Proof captured per kept row
| id | slug | proof |
|----|------|-------|
| 2 | velvet-comedy | JSON-LD startDate 2026-05-27 |
| 3 | ffcn | JSON-LD startDate 2026-05-27 |
| 5 | green-light | recurrence text |
| 6 | cuba-compagnie | recurrence text |
| 8 | rocket | recurrence text |
| 10 | comedy-crush | recurrence text |
| 11 | millennial-meltdown | recurrence text |
| 15 | wednesday-night-comedy | recurrence text |
| 18 | theatre-bo-julie | recurrence text |
| 23 | comedy-lab-chat-noir | recurrence text |
| 24 | green-mic-showcase | recurrence text |
| 25 | coucou-friday | recurrence text |
| 28 | smash | recurrence text |
| 31 | charonne | recurrence text |

## Bugs found and fixed
1. The probe was rate-limited on the first bulk run → added 0.5s gap between requests.
2. The `is_past` check was evaluated **before** `future_dates`, so Eventbrite recurring events (which display "Event ended" on the earliest historical instance while still listing future dates) were wrongly quarantined. Reordered to check future_dates and recurrence FIRST.
3. Public `/api/listings` serializer was leaking `source: "archive-2026-04-13"` in plaintext. Added `source`, `verification_source`, `cancellation_reason`, `quarantine_reason`, `quarantined_at/by`, `previous_status`, `verified_by`, `blocked_from_auto_regeneration`, `public_visible` to `_LISTING_PRIVATE_FIELDS`.
4. The "≥2 distinct venues featured" invariant fired on an empty featured list (canonically allowed). Now only enforces when list is non-empty.

## Why featured count is now 0
Per PROJECT_CANON, featured placement requires one of: day-of-week match / paid promo / editorial. The `featured=1` flag was a stale archive-2026-04-13 artifact — not a canonical signal. All 4 previously-featured rows had their `featured` flag cleared during quarantine; rehab restored them to `active` but did not re-set featured. Empty featured = canon-correct until Robert assigns editorial featured or paid promo. The homepage day-of-week logic still surfaces today's matching shows.

