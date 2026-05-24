# Live regression — 2026-05-24

```
$ curl -s https://pariscomedy.com/ | grep -E "instagram|first 100|34\+|27\+|Robert Hoehn|chucklericain"  → (empty)
$ curl -s https://pariscomedy.com/shows.html | grep -E "instagram\.com/pariscomedy|Source check stale"     → (empty)
$ curl -s https://api.pariscomedy.com/api/listings           | grep -Ei "chucklericain|Robert Hoehn|runner_email"  → (empty)
$ curl -s https://api.pariscomedy.com/api/listings?featured=1 | grep -Ei "chucklericain|Robert Hoehn|runner_email"  → (empty)
$ curl -s https://api.pariscomedy.com/api/shows              | grep -Ei "chucklericain|Robert Hoehn|runner_email"  → (empty)
$ python3 scripts/guardrails/check_invariants.py                                                                    → ✅ GREEN
```
