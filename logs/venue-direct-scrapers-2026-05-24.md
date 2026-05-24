# Venue-direct scrapers — build log (2026-05-24)

## Pre-flight
- PROJECT_CANON.md, SCOPE_LOCK.md, ACCEPTANCE_TESTS.md, check_invariants.py: READ
- check_invariants.py before changes: ✅ GREEN
- HUD: updated to Phase 0 → Phase 1 (survey) → Phase 2 (build) → Phase 3 (test) → Phase 4 (verify)

## Probe results (which venues have public sites we can scrape)
| Venue | Primary URL | HTTP | Notes |
|-------|-------------|------|-------|
| cafe_oscar | https://www.cafeoscar.fr/ | 200 | links to cafeoscar.eventbrite.fr — delegate to EB |
| le_coquin | https://www.lecoquin.fr/ | 000 | no domain; FB only |
| cuba_compagnie | (3 variants) | 000 | no domain |
| green_mic | (3 variants) | 000 | no domain; EB only |
| the_englishman | https://theenglishman.club/ | 000 | unreachable |
| blastoff_comedy | https://www.blastoffcomedy.com/ | 200 | EB external links extractable ✅ |
| paname_art_cafe | https://panameartcafe.com/ | 200 | /programmation/<slug> pages ✅ |
| barbes_comedy | https://www.barbescomedyclub.com/ | 200 | JS-rendered, no event anchors |
| golden_comedy_club | https://goldencomedyclub.com/ | 200 | delegates to BilletReduc |
| marco_polo_comedy | (3 variants) | 000 | no domain |

## Modules created
- `_venue_helpers.py` — shared parse_event_jsonld + stub_result + candidate factory
- `blastoff_comedy.py` — 4 candidates surfaced (real EB eids from /calendar)
- `paname_art_cafe.py` — 4 candidates surfaced (/programmation/<slug> URLs)
- `cafe_oscar.py` — stub (delegates to eventbrite_organizer)
- `golden_comedy_club.py` — stub (delegates to billetreduc)
- `barbes_comedy.py` — stub (JS-rendered; needs Playwright)
- `le_coquin.py` — stub (no public site)
- `cuba_compagnie.py` — stub (no public site)
- `green_mic.py` — stub (no public site; EB only)
- `the_englishman.py` — stub (domain unreachable)
- `marco_polo_comedy.py` — stub (domain unreachable)

## Registry changes (scripts/discovery/__init__.py)
- New `AGGREGATOR_SOURCES` list (7 modules — unchanged behaviourally)
- New `VENUE_DIRECT_SOURCES` list (10 modules)
- `SOURCES = AGGREGATOR_SOURCES + VENUE_DIRECT_SOURCES` (17 total)
- `SOURCE_GROUPS = {"aggregators": ..., "venue_direct": ...}` group aliases
- `expand_groups()` so `--sources venue_direct` runs all 10 venue modules
- No existing source removed or downgraded.

## Pipeline hardening
- `daily_discover.py` `EXTRACT_PROMPT` brace-escaped (was crashing on .format())
- New `classifier_unreachable` counter
- `run_state` now: GREEN | PARTIAL | FAILED (PARTIAL = classifier was down on ≥1 event)
- `check_invariants.py` accepts PARTIAL as honest; still fails on GREEN-with-zero
