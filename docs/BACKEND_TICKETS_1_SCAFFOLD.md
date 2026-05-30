# BACKEND.TICKETS.1-SCAFFOLD

**Status:** IN_GIT_UNVERIFIED — pending ChatGPT closure  
**Authorized by:** ChatGPT 2026-05-30 (after P0.PRICING.COPY.SAFETY-3 closed)

## What this phase delivers

Multi-source ticket/listing adapter scaffold: 1 migration table + service module + 14 tests. No live scraping. No public auto-import. All candidates default `needs_review`.

## Files

| File | Description |
|---|---|
| `backend/migrations/007_tickets_v2.sql` | adapter_discoveries_v2 table |
| `backend/migrations/007_tickets_v2.rollback.sql` | Rollback |
| `backend/tickets_v2.py` | Service module + adapter registry |
| `backend/tests/test_tickets_v2.py` | 14 unit tests |

## Platforms modeled (15)

eventbrite, billetreduc, fnac, fever, weezevent, ticketmaster_fr, see_tickets, billetweb, yurplan, helloasso, shotgun, dice, venue_direct, instagram (signal-only), facebook (signal-only)

## DB table: adapter_discoveries_v2

Fields: candidate_id, source_platform, source_url, title, venue_name, venue_address, city, starts_at, recurrence_text, language_guess, ticket_url, confidence_score, parser_status, duplicate_match_status, review_status, imported_listing_id, notes, affiliate_enabled (default 0), robots_note, created_at, updated_at, reviewed_at, reviewed_by

## Review states

discovered → needs_review → duplicate_existing | rejected | approved_for_import → imported | source_unreachable

## Service functions

| Function | Description |
|---|---|
| `register_adapter(platform, config)` | Register adapter; raises on unknown platform |
| `list_adapters()` | Returns all 15 platforms with metadata |
| `normalize_candidate(raw)` | Normalise raw input; default review=needs_review, affiliate=0 |
| `save_candidate(conn, candidate)` | Upsert to DB |
| `detect_candidate_duplicate(conn, candidate)` | Match by source_url |
| `mark_candidate_status(conn, candidate_id, status, ...)` | Validated status transition + audit |
| `list_review_queue(conn)` | Candidates in needs_review/discovered |
| `import_candidate_dry_run(conn, candidate_id)` | Draft only — no public listing; blocked unless approved_for_import |
| `status()` | Feature flag status |

## Safety rules

- All candidates default `needs_review` — never reach public without `approved_for_import`
- Signal-only platforms (instagram, facebook) cannot import
- Duplicate candidates blocked from import
- Affiliate fields always default disabled; blocked by flag if enabled
- No network calls in module (`requests`, `httpx` etc. not imported)
- No robots bypass

## Feature flags

- `TICKETS_ADAPTERS_ENABLED=false`
- `TICKET_IMPORTS_ENABLED=false`
- `AFFILIATE_LINKS_ENABLED=false`

## Tests: 14/14 PASS. Full suite: 115/115 PASS.

## Rollback

```
git revert <sha> && git push origin main
# optional DB: sqlite3 data/paris.db < backend/migrations/007_tickets_v2.rollback.sql
```
