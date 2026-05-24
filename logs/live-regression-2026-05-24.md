# Live regression — 2026-05-24

```
$ curl -s https://pariscomedy.com/ | grep -E "instagram|first 100|34\+|27\+|Robert Hoehn|chucklericain"  → (empty)
$ curl -s https://pariscomedy.com/shows.html | grep -E "instagram\.com/pariscomedy|Source check stale"     → (empty)
$ curl -s https://api.pariscomedy.com/api/listings           | grep -Ei "chucklericain|Robert Hoehn|runner_email"  → (empty)
$ curl -s https://api.pariscomedy.com/api/listings?featured=1 | grep -Ei "chucklericain|Robert Hoehn|runner_email"  → (empty)
$ curl -s https://api.pariscomedy.com/api/shows              | grep -Ei "chucklericain|Robert Hoehn|runner_email"  → (empty)
$ python3 scripts/guardrails/check_invariants.py                                                                    → ✅ GREEN
```

## Live regression — archive audit (2026-05-24 16:30 CEST)
For each forbidden string × each public endpoint:
- archive-2026-04-13, velvet-openmic, Velvet Bar Comedy — Open Mic, canceled, stale_hidden, runner_email, Robert Hoehn, chucklericain
× /api/listings?featured=1, /api/listings, /api/shows, /shows.html

**0 HITS.** All public surfaces clean.

```
$ for url in <4 endpoints>; do for term in <8 terms>; do grep -c -- "$term"; done; done   → 0 HITS
$ python3 scripts/guardrails/check_invariants.py        → ✅ GREEN
$ python3 scripts/guardrails/audit_public_shows.py      → ✅ GREEN (41/41)
$ python3 scripts/guardrails/audit_archive_rows.py      → ✅ GREEN (14 kept, 164 quarantined, 0 leaks)
```

## Homepage featured widget audit — live regression (2026-05-24 17:40 CEST)
- /api/listings?featured=1 → `[]`
- /shows.html, /index, /api/* — all clean across 11 forbidden strings
- Playwright rendered DOM: featured section shows truthful empty state, no stale phrases visible
