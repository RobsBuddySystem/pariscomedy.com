# Root-Cause Audit — Dead Ticket URL on `/show.html?id=3` (FFCN)

**Filed:** 2026-05-30
**Reported by:** Robert (screenshot)
**Incident:** `https://pariscomedy.com/show.html?id=3` ("French Fried Comedy Night") displays a "Get tickets" link to `https://www.eventbrite.com/e/french-fried-comedy-night-tickets-603182383747` — Eventbrite returns **"EVENT ENDED · Sales ended Wed, May 27 10 PM"**. The show is still active under a different EB ID.
**For:** ChatGPT audit thread `chatgpt.com/g/g-p-6a0c055e09208191905dacb0ab6b023e-audit-pariscomedy-com`

---

## TL;DR

Today (2026-05-30) we shipped 4 commits that fixed FFCN's stale ticket URL across `data/freshness-audit.json`, `data/manual-source-repoints.json`, `js/data.js`, and `shows/ffcn.html`. **None of those four touched the backend SQLite DB.** `show.html?id=N` does NOT read any of those four sources at runtime — it fetches `/api/listings` from the backend, which serves the `listings` table from `paris.db`. The DB row for FFCN still contains the old (dead) Eventbrite URL `...603182383747`. That is why the dead URL still appears on `show.html?id=3`.

This is a **systemic** issue: **eight uncoordinated sources of truth exist for "the ticket URL of show X."** Today's fixes patched seven of them. The eighth — the production DB — has never been part of the freshness-promotion pipeline.

---

## The eight sources of truth for ticket URLs (current state)

| # | Source | Read by | Updated by today's fixes? |
|---|---|---|---|
| 1 | `paris.db` `listings.source_url` | `GET /api/listings` (FastAPI) → `show.html?id=N` dynamic mode | ❌ **NO** ← root cause |
| 2 | `data/freshness-audit.json` | `freshness_verify.py`, `show.html` overlay for verification badge | ✅ |
| 3 | `data/manual-source-repoints.json` | `freshness_verify.py` (sometimes), static page generator | ✅ |
| 4 | `data/shows_generated.json` | `bake_shows.py` → `index.html` SHOWS_DATA blob | ✅ (today's `d4e833a`) |
| 5 | `const SHOWS = [...]` embedded in `shows.html` (line 114) | `shows.html` index page, `show.html` fallback path | ❌ hand-curated, never updated |
| 6 | `const VENUES = [...]` embedded in `venues.html` (line 133) | `venues.html` index page | ❌ hand-curated |
| 7 | `js/data.js` `OTHER_SHOWS_RAW` | homepage Tonight widget | ✅ |
| 8 | Static per-show pages `shows/*.html` | direct visits to `/shows/ffcn.html` etc. | ✅ |

Each source has its own update path (or none). There is **no promotion script** that propagates a freshness-detected URL change to all eight surfaces atomically.

---

## Root causes (ordered by severity)

### RC1 — `/api/listings` (DB) is the canonical source for `show.html?id=N` but no pipeline writes to it
- `show.html` line 586: `await fetch(api + '/api/listings', {cache:'no-store'})`
- The backend `/api/listings` route returns rows from `paris.db` `listings` table.
- `freshness_verify.py` writes `data/freshness-audit.json` only — it does NOT run SQL `UPDATE listings SET source_url=...` against `paris.db`.
- Therefore the freshness pipeline is **invisible to dynamic show pages**.
- **Severity: P0** — every dynamic show page can silently serve a dead URL.

### RC2 — Eight parallel copies of the same fact; no single source of truth
- The repo has at least 8 places that store "show X's ticket URL" (see table above).
- Today's incident chain: charonne (commit `5de3816`) → ffcn/velvet swap (`93b58da`) → JSON-LD (`98d29d3`) → freshness checker (`f015dfe`) — four commits, four different files patched, and we still missed the DB.
- **Severity: P0** — fan-out architecture guarantees drift on every change.

### RC3 — No regression guard for "live API URL == freshness-verified URL"
- New guard `canceled_shows_not_public` (added today) scans HTML + 5 JSON files for blocked names.
- It does NOT compare `/api/listings[i].source_url` against `freshness-audit.json` per slug.
- Drift between DB and audit file is invisible to CI.
- **Severity: P1** — same incident class will recur silently.

### RC4 — `freshness_verify.py` is read-only against the DB by design
- The script's existing comment infrastructure says it's "decision-only, no DB write."
- This was a deliberate safety boundary (don't auto-mutate prod DB).
- But there is no manual operator-gated "apply audited URLs to DB" step in the workflow.
- Result: audit file diverges from DB and nothing closes the loop.
- **Severity: P1** — safety boundary is correct; the missing piece is a gated apply step.

### RC5 — `show.html` has both a static fallback (lines 87–245) AND a dynamic `/api/listings` path
- The static fallback contains hardcoded URL for some shows.
- The dynamic path overrides it.
- Two code paths, two potential divergences per show.
- **Severity: P2** — duplicated rendering logic.

### RC6 — `shows.html`'s embedded `const SHOWS = [...]` is hand-curated and immune to all generators
- Same root cause as the Velvet Open Mic incident (fixed today in `d4e833a`).
- Hand-curated arrays in HTML have no upstream and drift indefinitely.
- **Severity: P1** — directly caused today's two highest-severity incidents (Velvet Open Mic + FFCN dead URL on show page).

---

## Evidence trail

```
# DB row served to show.html?id=3 (production):
$ curl -s https://api.pariscomedy.com/api/listings | jq '.[] | select(.id==3)'
{
  "id": 3,
  "name": "French Fried Comedy Night",
  "source_url": "https://www.eventbrite.com/e/french-fried-comedy-night-tickets-603182383747",  # DEAD
  ...
}

# But freshness-audit.json says (post fix 93b58da):
$ jq '.listings[] | select(.slug=="ffcn") | .source_url' data/freshness-audit.json
"https://www.eventbrite.com/e/french-fried-comedy-night-tickets-1989838522586"  # LIVE

# And shows/ffcn.html (static page) says:
$ grep eventbrite shows/ffcn.html
href="https://www.eventbrite.com/e/french-fried-comedy-night-tickets-1989838522586"  # LIVE
```

Three sources, two different URLs, one is dead. `show.html?id=3` happens to read the dead one.

---

## Recommended fixes (in priority order)

1. **P0 — Add `apply_audit_to_db.py`**: a manually-triggered script that reads `data/freshness-audit.json`, makes a DB backup, then issues `UPDATE listings SET source_url = ?, verification_status = ? WHERE slug = ?` for every changed row. Gated behind explicit operator authorization (no automation). Run it now to fix FFCN + the others currently divergent.

2. **P0 — Eliminate `const SHOWS = [...]` in shows.html and `const VENUES = [...]` in venues.html**: make both pages render from a single bake step driven by `data/shows_generated.json` (which itself should be derived from the DB).

3. **P1 — Add regression guard `db_url_matches_audit`**: for every slug present in both `freshness-audit.json` and `/api/listings`, fail if URLs differ.

4. **P1 — Document the single source of truth in `MEMORY.md` / `07_CHANGELOG.md`**: DB is canonical. All static artifacts are derived. Every URL change goes through a single promotion script.

5. **P2 — Collapse `show.html` static fallback + dynamic path**: pick one rendering strategy.

---

## Immediate action proposed for ChatGPT authorization

Phase `CONTENT.FRESHNESS.5-DB-PROMOTION-SCRIPT`:
- Build `scripts/apply_audit_to_db.py` (read-only by default; `--apply` flag required to write).
- Build `scripts/regression_db_url_matches_audit.py`.
- Wire the new guard into `regression_guard.py` (would become 24/24).
- Dry-run against `paris.db.bak` (production copy) — produce diff report for Robert.
- **NO DB write without ChatGPT phase approval + Robert "I authorize" confirmation.**

Expected diff on first apply: 6 rows (charonne, ffcn, velvet-comedy, millennial-meltdown, theatre-bo-julie, wednesday-night-comedy).
