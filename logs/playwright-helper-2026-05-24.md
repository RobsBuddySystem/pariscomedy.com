# Playwright helper — build log (2026-05-24)

## Pre-flight
- canon read: PROJECT_CANON, SCOPE_LOCK, ACCEPTANCE_TESTS, Venue-Direct audit doc
- check_invariants: ✅ GREEN before changes
- playwright_status before install: {"package": False, "chromium": False}

## Install
- `pip install --quiet playwright`  → OK
- `python3 -m playwright install chromium`  → Chrome Headless Shell 148.0.7778.96 downloaded (92.4 MiB)
- playwright_status after install: {"package": True, "chromium": True}
- example.com render smoke test: ok=True, elapsed_ms=1756

## Helper API
```
render_html(url, *, wait_selector=None, timeout_ms=15000, source="",
            block_heavy=True, log=None) -> dict
    returns {ok, html, final_url, error, elapsed_ms, source, skip_reason}

playwright_status() -> dict
    returns {package: bool, chromium: bool, install_cmd: str}
```

Lazy-imported. Blocks images/media/fonts at the route level so renders stay fast.

## SKIPPED-path verification (Playwright absent)
- All 17 sources imported clean
- venue_direct dry-run with no Playwright: barbes_comedy + fever_paris both returned 0
  with structured "Playwright missing — install: <cmd>" reasons. No crash.
- summary.run_state: FAILED (zero raw events, correctly)

## GREEN-path verification (Playwright present)
- barbes_comedy: 0 static → 1 candidate via Playwright (4.1s render). Dropped for no-date (canon: never guess dates).
- fever_paris: 0 static → rendered DOM ALSO had 0 /m/<id>- URLs. Honest STUB emitted.
- venue_direct group total: 9 raw → 4 accepted, run_state GREEN.

## Post-change
- check_invariants: ✅ GREEN
- Live regression: /, /shows, /comedians, /about, /featured API all clean
