# Stale Show Quarantine — 2026-05-24

164 rows quarantined this session. Public surfaces stripped of:
- `source` field (was leaking 'archive-2026-04-13')
- All admin/audit fields (cancellation_reason, quarantine_*, previous_status, verified_by, blocked_from_auto_regeneration, public_visible, verification_source)

Quarantined rows retain full audit trail in the DB:
- `status='stale_hidden'`
- `previous_status=` original value
- `featured=0`
- `public_visible=0`
- `quarantine_reason=` one of: "HTTP 200 but no future date and no recurrence text — insufficient proof" / "URL HTTP NNN" / "empty body returned"
- `quarantined_at=2026-05-24`
- `quarantined_by='audit_archive_rows.py'`

No row was deleted.
