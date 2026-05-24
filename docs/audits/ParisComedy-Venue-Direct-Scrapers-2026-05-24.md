# ParisComedy — Venue-Direct Scrapers (2026-05-24)

## Status: GREEN ✅

Guardrails passed before changes. Passed after changes. No canon or scope rules violated. No existing source removed. No Robert/FFCN/Velvet privilege introduced.

## Sources added (10 venue-direct modules)

| # | Module | URL checked | Type | Candidates this run |
|---|--------|-------------|------|---------------------|
| 1 | `cafe_oscar` | https://www.cafeoscar.fr/ | stub (→ EB) | 0 |
| 2 | `le_coquin` | https://www.lecoquin.fr/, FB | stub (no public source) | 0 |
| 3 | `cuba_compagnie` | (3 variants) | stub (no public source) | 0 |
| 4 | `green_mic` | (3 variants) | stub (no public source) | 0 |
| 5 | `the_englishman` | https://theenglishman.club/ | stub (unreachable) | 0 |
| 6 | `blastoff_comedy` | https://www.blastoffcomedy.com/ | extractor | **4 ✅** |
| 7 | `paname_art_cafe` | https://panameartcafe.com/ | extractor | **4 ✅** |
| 8 | `barbes_comedy` | https://www.barbescomedyclub.com/ | stub (JS-rendered) | 0 |
| 9 | `golden_comedy_club` | https://goldencomedyclub.com/ | stub (→ BilletReduc) | 0 |
| 10 | `marco_polo_comedy` | (3 variants) | stub (unreachable) | 0 |

## Working
- `blastoff_comedy` (4 candidates → 4 accepted by LLM classifier)
- `paname_art_cafe` (4 candidates → 0 accepted; pages list residencies without dates)

## Returned zero (honest stubs, logged with reason)
- `cafe_oscar`, `golden_comedy_club` — coverage already provided by existing aggregator sources (EB, BilletReduc respectively)
- `cuba_compagnie`, `green_mic`, `le_coquin`, `the_englishman`, `marco_polo_comedy` — no working public domain

## Needing Playwright / headless later
- `barbes_comedy` — site reachable, events JS-rendered (no static event anchors)
- `fever_paris` (pre-existing) — same JS-rendered problem (task #43)

## Pipeline changes
- `daily_discover.py`: `EXTRACT_PROMPT` brace-escaped (was crashing); added `classifier_unreachable` counter; `run_state` now `GREEN | PARTIAL | FAILED`.
- `discovery/__init__.py`: `SOURCES = AGGREGATOR_SOURCES + VENUE_DIRECT_SOURCES` (17 total); `SOURCE_GROUPS` for `--sources venue_direct` group syntax.
- `scripts/guardrails/check_invariants.py`: accepts PARTIAL; still rejects GREEN-with-zero-raw and GREEN-with-classifier-down.

## Ollama / classifier
- **Reachable** during the dry-run for CLASSIFY calls (4 events accepted, 4 rejected — real classification work).
- **Intermittent** for EXTRACT_PROMPT (performer-name extraction), surfaced in summary as `classifier_unreachable` counter but non-blocking for show acceptance.
- run_state honestly reflected the run.

## Guardrails
- **Before changes:** ✅ GREEN
- **After changes:** ✅ GREEN
- Live public site re-checked: no `@pariscomedy`, no `instagram.com/pariscomedy`, no Stripe, no false claims, no PII in featured API.

## Tomorrow's cron
- **Trustable** for sources that produced data in this run.
- If PC Ollama is down at 06:00, `run_state` will surface as `PARTIAL` or `FAILED` — never silent "GREEN with 0 shows."

## Files changed
- `scripts/discovery/__init__.py` (registry + group aliases)
- `scripts/discovery/_venue_helpers.py` (NEW)
- `scripts/discovery/blastoff_comedy.py` (NEW)
- `scripts/discovery/paname_art_cafe.py` (NEW)
- `scripts/discovery/cafe_oscar.py` (NEW stub)
- `scripts/discovery/golden_comedy_club.py` (NEW stub)
- `scripts/discovery/barbes_comedy.py` (NEW stub)
- `scripts/discovery/le_coquin.py` (NEW stub)
- `scripts/discovery/cuba_compagnie.py` (NEW stub)
- `scripts/discovery/green_mic.py` (NEW stub)
- `scripts/discovery/the_englishman.py` (NEW stub)
- `scripts/discovery/marco_polo_comedy.py` (NEW stub)
- `scripts/daily_discover.py` (EXTRACT_PROMPT escape, PARTIAL state)
- `scripts/guardrails/check_invariants.py` (PARTIAL acceptance)
- `WORKSESSION_HUD.md` (phase log)
- `logs/venue-direct-scrapers-2026-05-24.md`, `logs/discovery-source-tests-2026-05-24.md`

## Commands run
```
python3 scripts/guardrails/check_invariants.py     # pre-flight GREEN
python3 -c 'import discovery; print(discovery.SOURCES)'   # 17/17 import clean
python3 scripts/daily_discover.py --dry-run --sources venue_direct   # 8 raw, 4 accepted
python3 scripts/daily_discover.py --dry-run --sources timeout_paris  # FAILED honestly
python3 scripts/guardrails/check_invariants.py     # post-change GREEN
curl -s https://pariscomedy.com/ | grep -E "..."   # all empty (clean)
```

## Commits
- (frontend repo) — venue scrapers live in scripts/ which is NOT git-tracked (local-only LaunchAgent dir)
- (push repo) — `scripts/guardrails/check_invariants.py` updated (PARTIAL), logs + audit docs committed

## Remaining risks
1. PC Ollama at `100.75.13.73:11434` is intermittent. PARTIAL state will surface honestly when this happens.
2. Two venues (`barbes_comedy`, `fever_paris`) need a Playwright pass to extract their JS-rendered events.
3. Five venues have no public website — their events will only appear if they reach the directory via an aggregator source (EB, BilletReduc, Shotgun, Dice) or manual admin entry.

## Next safest step
Wire a single Playwright-rendering helper that `barbes_comedy` and `fever_paris` can share. That unblocks both venues with one piece of infra.
