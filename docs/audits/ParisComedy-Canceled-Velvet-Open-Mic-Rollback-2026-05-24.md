# ParisComedy — Canceled Velvet Open Mic Rollback + Provenance Audit (2026-05-24)

## Status: GREEN ✅

## Incident
On 2026-05-24 12:35 CEST in commit `645cbab`, I added 4 Velvet Bar Comedy — Open Mic Wednesday 19:00 rows to SHOWS_DATA during an unrelated FFCN show-list fix session. The Velvet 19:00 Open Mic was suspended on 2026-05-04 per Robert (vault note `Open-Mic-Suspended-2026-05-04`). I had access to that memory and did not consult it. There was no canceled-show blocklist or provenance gate in place to stop the bad insertion. The Backend DB row id=1 slug=`velvet-openmic` was stale seed data that pre-dated this session.

## Confirmation Velvet Open Mic is removed from public site
- **Live /shows.html SHOWS_DATA**: 0 matches for `velvet-openmic` or `Velvet Bar Comedy — Open Mic`
- **Live /api/listings**: blocked by `_PUBLIC_BLOCKED_SLUGS` (verified empty)
- **Live /api/listings?featured=1**: blocked (verified empty)
- **Rendered DOM (Playwright)**: not visible

## Root cause
- Where added: `shows.html` SHOWS_DATA (canonical at `~/Desktop/pariscomedy_output/html/` + push repo mirror)
- Commit that added it: **645cbab** (2026-05-24 12:35 CEST | frontend)
- How: inline Python `mk(...)` snippet during the FFCN show-list fix session, with no provenance check
- Why tests didn't catch it: no canceled-shows blocklist; no provenance guardrail
- Dates fabricated: 2026-05-27, 2026-06-03, 2026-06-10, 2026-06-17 (Wed 19:00)
- Pre-existing stale: backend DB row id=1 had been active in the seed since before this session (separate issue, also fixed)

## Files / data stores cleaned
| File | Change |
|---|---|
| `data/canceled_shows.json` | NEW — canonical blocklist |
| `shows.html` SHOWS_DATA (both copies) | 4 invented rows removed (45 → 41) |
| `~/.openclaw/.../paris.db` show_listings id=1 | status `active` → `canceled` (schema CHECK extended) |
| `main.py` | `_PUBLIC_BLOCKED_SLUGS` + hard-block in `list_listings()` |
| `generate_instances.py` | velvet-openmic seed line removed |
| `js/data.js` | velvet-openmic JS literal removed |
| `data/shows_generated.json` | 5 entries purged (175 → 170) |
| `comedians.html` (both copies) | velvet-openmic SHOWS entry removed |

## Canceled-show blocklist
`data/canceled_shows.json`:
```json
{
  "canceled": [
    {
      "slug": "velvet-openmic",
      "names": ["Velvet Bar Comedy — Open Mic", "Velvet Bar Comedy Open Mic", "Velvet Open Mic"],
      "status": "canceled",
      "public_visible": false,
      "blocked_from_auto_regeneration": true,
      "verified_at": "2026-05-24",
      "verified_by": "Robert (manual admin)",
      "cancellation_reason": "Robert confirmed Velvet Bar Open Mic canceled on 2026-05-04 (vault: Open-Mic-Suspended-2026-05-04); rolled back 4 invented future rows that were added in commit 645cbab on 2026-05-24"
    }
  ]
}
```

## Process guardrails added
- `scripts/guardrails/check_invariants.py` extended with `check_canceled_blocklist()` and `check_show_provenance()`.
- `scripts/guardrails/audit_public_shows.py` NEW — per-row provenance audit; exit 1 if any row lacks ticket_url, source_url, or verified_at.
- `main.py` backend has `_PUBLIC_BLOCKED_SLUGS` hard-block that overrides every query parameter.

## Remaining Wednesday shows — fully audited
All 6 named (FFCN, Velvet Showcase, Kiss, South, Comedy Crush, The Dissident) have ticket_url + source_url + last_verified_at + explicit time. None quarantined.

## Tests run
```
python3 scripts/guardrails/check_invariants.py        → ✅ GREEN (pre)
python3 scripts/guardrails/check_invariants.py        → ✅ GREEN (post)
python3 scripts/guardrails/audit_public_shows.py      → ✅ GREEN (41/41)
curl + grep velvet-openmic on /shows.html             → 0 matches
curl + grep velvet-openmic on /api/listings (both)    → 0 matches
Playwright DOM scan of /shows.html                    → Velvet Open Mic absent
```

## Commits pushed
- `61a22a4` (backend repo): `_PUBLIC_BLOCKED_SLUGS` + schema CHECK + DB row quarantine
- `a570d10` (push repo): all SHOWS_DATA/mirror purges + blocklist + audit script + extended invariants

## Final status: GREEN ✅
