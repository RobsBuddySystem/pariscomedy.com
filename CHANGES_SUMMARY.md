# CHANGES_SUMMARY — 2026-07-12

Scope: pariscomedy.com analytics/SEO restoration pass. Nothing committed, nothing
pushed, nothing deployed. No `alembic`, no live DB writes, no services restarted.
All changes are sitting in the working tree of:
- Frontend: `/Users/chuck/pariscomedy-push-20260526-095907`
- Backend: `/Users/chuck/.openclaw/workspace/apps/paris-comedy`

---

## 1. Beacon restoration

**New file:** `scripts/add_beacon.py` (frontend repo) — idempotent. Inserts
`<script src="/assets/track.js" defer></script>` (the exact pattern already used
on `index.html:951`) immediately before `</body>` in any target file that
doesn't already contain `assets/track.js`. Safe to re-run — a second run makes
zero changes.

Ran against: `shows.html`, `whats-on.html`, `show.html`, `blog/index.html`,
`blog/whats-on-*.html` (5), `c/*.html` (237), `shows/*.html` (19, incl. `index.html`).

**Result:** 265 files scanned matched targets, all 265 got the beacon inserted
(0 already had it). Re-running the script afterward reported 0 inserted / 265
already-present, confirming idempotency.

**Verify:**
```
python3 scripts/add_beacon.py        # re-run — should report 0 inserted
grep -c track.js shows.html whats-on.html show.html c/abhi-pamnani.html shows/comedy-lab-chat-noir.html
```

---

## 2. Canonical fix

- `shows.html`: added `<link rel="canonical" href="https://pariscomedy.com/shows.html">`
  (it had no canonical tag before).
- `shows/*.html` (18 of 19 — `shows/index.html` is the directory index, not an
  individual show page, and was left pointing at `/shows.html`): each is a
  thin client-side redirect stub (meta-refresh + `location.replace`) to
  `/show.html?slug=<slug>` or `/shows.html`. Canonical on each now points to
  its own URL, e.g. `https://pariscomedy.com/shows/comedy-lab-chat-noir.html`.
- Meta description added to all 18: these stub pages have NO show-specific
  visible content (only "Redirecting to the live show page... Continue →"),
  so per the "do not invent facts" instruction, the description is built only
  from what's actually on the page: `"Redirecting to the Paris Comedy show
  page for <Show Name>."` (name Title-Cased from the page's own slug/link).

**Verify:**
```
grep -o 'rel="canonical" href="[^"]*"' shows/comedy-lab-chat-noir.html
grep -o 'rel="canonical"' shows.html
grep -c 'meta name="description"' shows/*.html   # 1 for all except index.html (0)
```

---

## 3. whats-on.html past-date filter

Edited `whats-on.html`'s inline `<script>`:
- Added `isPast(ev)` / `parisMidnightUTC()` — computes Europe/Paris local
  midnight as a UTC instant via `toLocaleDateString('en-CA', {timeZone:
  'Europe/Paris'})`, and hides any event whose `starts_at` is before it.
  `render()` now filters `ALL` through `!isPast(e)` before building rows,
  stats, and the city filter list.
- Added an "Updated `<date>`" line in the stats bar, sourced from a new
  optional `generated_at` field. The current `data/upcoming_events.json` is a
  plain array (verified: `python3 -c "import json;print(type(json.load(open('data/upcoming_events.json'))))"` → `list`),
  so the fetch handler now tolerates BOTH shapes: a bare array (today's
  format, no `generated_at`, line stays blank) or `{generated_at, events:[...]}`
  (future format). No error either way.
- Verified the date-cutoff logic with a standalone Node harness extracting the
  inline `<script>` and asserting `isPast()` on a real past event
  (`2026-07-11T15:00:00+02:00`, actually present in the live JSON, id 30) →
  `true`, and a future one → `false`.

**Verify:**
```
grep -n "isPast\|GENERATED_AT\|parisMidnightUTC" whats-on.html
```
Open in a browser with today's date — the Barcelona "Open Writing Workshop"
event (`starts_at: 2026-07-11T15:00...`, already past) should NOT render.

---

## 4. billetreduc date bridge

**New file:** `scripts/br_bridge.py` (backend repo, next to `eb_bridge.py`).
Dry-run by default; `--apply` flag mirrors `eb_bridge.py`'s write pattern
(DB backup, then DELETE+INSERT into `show_dates`). **`--apply` was NEVER run
by me — only the dry-run.**

**Target correction:** the task brief named `choumi-in-english`,
`comedy-lab-chat-noir`, `theatre-bo-julie`, `englishman-night` as billetreduc
listings. A read-only query (`SELECT slug,booking_url FROM show_listings WHERE
booking_url LIKE '%billetreduc.com/spectacle%'`) showed `comedy-lab-chat-noir`
and `englishman-night` are actually **Eventbrite**-backed (already covered by
`eb_bridge.py`). The real 5 billetreduc listings are: `choumi-in-english`,
`theatre-bo-julie`, `rocket`, `charonne`, `oscar`. This is documented at the
top of the script and used instead of the brief's stale names.

**Parsing:** BilletReduc embeds a schema.org `Event` block as
`<script type="application/ld&#x2B;json">` — note the `+` is HTML-entity
-encoded (`&#x2B;`), not literal; a naive search for `"ld+json"` finds
nothing on this site. The script decodes that, reads `startDate`/`endDate`,
and falls back to regex-matching visible French date text only if no such
block is found.

**Choumi is biweekly — real dates replace the old days[]-weekly guess, but
only partially:** the JSON-LD gives exactly ONE `startDate` (next occurrence)
plus an `endDate` for the season — it does NOT enumerate every biweekly
session (that calendar is populated client-side via a JS call this script
doesn't execute). The dry-run output flags this loudly per-row. Documented at
length in the script's docstring so nobody mistakes the one date for a full
calendar.

**Dry-run output (actual, captured 2026-07-12):**
```
choumi-in-english: show_date=2026-07-19 20:30 (+ endDate 2026-08-30, NOT enumerated)
theatre-bo-julie:  show_date=2026-08-28 19:00 (+ endDate 2026-12-19, NOT enumerated)
rocket:            show_date=2026-07-12 21:48
charonne:          show_date=2026-07-18 19:30 (+ endDate 2026-08-01, NOT enumerated)
oscar:             show_date=2026-08-06 20:00 (+ endDate 2026-08-30, NOT enumerated)
```
No DB writes occurred (dry-run only).

**Verify:**
```
cd ~/.openclaw/workspace/apps/paris-comedy
./venv/bin/python scripts/br_bridge.py     # or plain python3 if no venv — dry-run, prints plan
```

---

## 5. SEO loop script

**New file:** `scripts/seo_loop.py` (backend repo). Pure Python, no LLM calls,
no writes to `paris.db` (read-only `SELECT` on `page_views` only). Checks:
- (a) diffs `sitemap.xml` (frontend repo) against actual repo HTML pages
  (top-level, `shows/*`, `c/*`, `blog/*`, admin/portal/backup pages excluded).
- (b) live-curls each `sitemap.xml` URL for HTTP status, `<title>`, meta
  description presence, canonical tag + target, and JSON-LD presence
  (`--no-fetch` / `--limit N` flags for offline/quick runs).
- (c) flags repo pages missing `assets/track.js`.
- (d) top referrers from `paris.db.page_views` in the last 7 days
  (read-only, normalises to hostname).

Writes a markdown report to
`~/Documents/chuck_vault/20-missions/seo_report_<date>.md`.

**Ran once** (`--limit 15` to keep the live-fetch pass short):
```
[written] /Users/chuck/Documents/chuck_vault/20-missions/seo_report_2026-07-12.md
```
Report confirms: 286 repo pages vs 42 sitemap entries (263 missing from
sitemap — expected, most are `c/*.html` comic pages the generator
deliberately excludes, see §6); 19 ghost sitemap entries with no matching
file, incl. FR legal pages (served from a different route) and stale
`show.html?slug=...` query-string URLs; live-fetch of 15 URLs found 0 broken
links, `shows.html` missing a live canonical (expected — that fix is only in
the working tree, not deployed); 12 top-level pages (`book.html`,
`terms.html`, `privacy.html`, etc.) still missing the beacon — these were
**not** in this task's target list and were intentionally left untouched, but
are flagged here for a future pass; top referrer last 7d is `pariscomedy.com`
(102), then direct (50), then `duckduckgo.com` (3).

**New file (not loaded):** `scripts/com.pariscomedy.seo-loop.plist` (backend
repo `scripts/`), modeled on the live `com.pariscomedy.eb-bridge.plist`
pattern, `StartCalendarInterval` Hour=3 Minute=12. **Not copied to
`~/Library/LaunchAgents` and not `launchctl load`ed.**

**Verify:**
```
cd ~/.openclaw/workspace/apps/paris-comedy
python3 scripts/seo_loop.py --limit 15
cat ~/Documents/chuck_vault/20-missions/seo_report_2026-07-12.md
plutil -lint scripts/com.pariscomedy.seo-loop.plist   # validates the plist syntax
```

---

## 6. Sitemap

`scripts/generate_sitemap.py` already existed in the frontend repo (I hadn't
seen it before reading it for this step). Read it first: it only writes
`sitemap.xml` at the repo root, reads local files + `git log` +
`data/freshness-audit.json`, makes no network calls and no DB writes — safe
to run. Ran it:
```
Wrote sitemap.xml with 36 URLs
```
It uses a hand-curated `PUBLIC_PAGES` list (does not include `c/*.html` comic
pages at all) plus verified show slugs from `freshness-audit.json` — so
`c/robert-hoehn.html` was never a candidate for inclusion by construction.

**🔴 FLAG (loud, per instructions): DO NOT DELETE ANYTHING YOURSELF —**
`c/robert-hoehn.html` does **NOT** exist in this repo (`ls c/robert-hoehn.html`
→ no such file), and the regenerated local `sitemap.xml` contains no
`robert-hoehn` entry. **However, the currently-LIVE deployed
`https://pariscomedy.com/sitemap.xml` (fetched via curl during this session,
not from this working tree) still lists
`https://pariscomedy.com/c/robert-hoehn.html`** — Robert's private real name,
in a public sitemap, pointing at a 404. This is a live privacy leak sitting on
the deployed site right now, independent of anything in this working tree,
and needs a deploy of the regenerated `sitemap.xml` (via the normal
`pariscomedy-deploy` gated flow — I did not deploy anything) to clear it.
Also worth noting: the live sitemap only has 9 URLs vs. this repo's freshly
regenerated 36 — the deployed sitemap is stale/out of date generally, not
just on this one entry.

**Verify:**
```
grep -i robert-hoehn sitemap.xml                              # local: no match (exit 1)
ls c/robert-hoehn.html                                        # local: no such file
curl -s https://pariscomedy.com/sitemap.xml | grep -i robert-hoehn   # LIVE: still present — needs deploy
```

---

## File inventory

**Frontend repo** (`/Users/chuck/pariscomedy-push-20260526-095907`):
- `scripts/add_beacon.py` — new
- `shows.html`, `whats-on.html`, `show.html`, `blog/index.html`,
  `blog/whats-on-*.html` (5), `c/*.html` (237), `shows/*.html` (19) — beacon
  inserted
- `shows.html` — canonical added
- `shows/*.html` (18, excl. `index.html`) — canonical fixed + meta description added
- `whats-on.html` — past-date filter + "Updated" line
- `sitemap.xml` — regenerated (36 URLs)
- `CHANGES_SUMMARY.md` — this file

**Backend repo** (`/Users/chuck/.openclaw/workspace/apps/paris-comedy`):
- `scripts/br_bridge.py` — new (dry-run only, never applied)
- `scripts/seo_loop.py` — new (ran once, wrote a report)
- `scripts/com.pariscomedy.seo-loop.plist` — new, NOT loaded

**Vault:**
- `~/Documents/chuck_vault/20-missions/seo_report_2026-07-12.md` — new report

No git commits were made. No `git push`. No `alembic`. No DB `--apply`. No
`launchctl load`. No service restarts.
