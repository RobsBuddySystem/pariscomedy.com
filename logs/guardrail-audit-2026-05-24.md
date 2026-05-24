# Guardrail Audit Log — 2026-05-24

## Inputs (ChatGPT live-audit findings)
| # | Finding | State at start of session |
|---|---------|---------------------------|
| 1 | `/` has @pariscomedy IG link | already removed in commit 5acd236; ChatGPT was looking at cached page |
| 2 | `/shows.html` has @pariscomedy IG link | already removed |
| 3 | `/comedians.html` has @pariscomedy IG link | already removed |
| 4 | `/` has stale "First 100 Featured listings FREE" banner | banner was removed; **FAQ block had a different stale claim** |
| 5 | `/` and `/?lang=en` inconsistent | identical (same source HTML) |
| 6 | `/about.html` says "34+ active shows across 27+ venues" | fixed in commit c7e7eef |
| 7 | `/about.html` says "Every show listing is verified..." | fixed in commit c7e7eef |
| 8 | Public featured API exposes Robert Hoehn / chucklericain@gmail.com | **REAL — sealed in commit 5691c51** |
| 9 | Shows page weak crawlable show fallback | embedded SHOWS_DATA present (37 rows) |
| 10 | Comedians page no crawlable directory | comic cards present in HTML |

## Fixes applied this session
1. `_serialize_listing` in main.py strips `runner_email` + `runner` from public response.
2. Homepage FAQ "first 100 show runners get a Featured listing completely free" replaced with paid Featured Promo language.
3. Robert Hoehn → Robert le Ricain across c/*.html + sitemap.xml; old `robert-hoehn.html` left as 0s meta-refresh redirect to new slug.
4. `daily_discover.py` summary now writes `run_state: GREEN | FAILED`. Zero events = FAILED.
5. Guardrail files added: PROJECT_CANON.md, SCOPE_LOCK.md, ACCEPTANCE_TESTS.md, scripts/guardrails/check_invariants.py.

## Live checks paste (post-fix, GH Pages may cache for ~60s)
```
$ curl -s https://pariscomedy.com/ | grep -Ei '@pariscomedy|instagram\.com/pariscomedy|First 100|Every show listing|34\+|27\+'
(only legitimate emails like payments@pariscomedy.com; no IG handle, no false claims)

$ curl -s "https://api.pariscomedy.com/api/listings?featured=1" | grep -Ei 'chucklericain|Robert Hoehn|"runner_email":"[a-z]'
(empty — clean)

$ python3 scripts/guardrails/check_invariants.py
✅ GREEN — all invariants hold.
```

## Commits this session
- `5691c51` (backend): strip runner_email + personal names from public API
- `1a10946` (push): PROJECT_CANON / SCOPE_LOCK / ACCEPTANCE_TESTS / check_invariants.py + FAQ fix
- `06e3cd5` (push): Robert Hoehn → Robert le Ricain + sitemap + refined regex
