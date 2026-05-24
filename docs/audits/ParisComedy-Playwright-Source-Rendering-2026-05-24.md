# ParisComedy — Playwright Source Rendering (2026-05-24)

## Status: GREEN ✅

Reusable headless-Chromium helper added. JS-rendered sources (barbes_comedy, fever_paris) no longer return silent zeros. Pipeline is unaffected when Playwright is missing — sources cleanly emit SKIPPED with the exact install command.

---

## Install state
- **Playwright Python package**: was NOT installed. Installed during this session via `pip install playwright` (quietly, into the system Python the scraper uses).
- **Chromium**: was NOT installed. Downloaded during this session via `python3 -m playwright install chromium`. Lives at `~/Library/Caches/ms-playwright/chromium_headless_shell-1223`.
- **Smoke test (example.com)**: ok=True, 1756 ms render — Playwright fully functional.

## Helper API
File: `scripts/discovery/_playwright_helper.py`

```python
render_html(url, *, wait_selector=None, timeout_ms=15000,
            source="", block_heavy=True, log=None) -> dict
# returns: ok, html, final_url, error, elapsed_ms, source, skip_reason

playwright_status() -> dict
# returns: package, chromium, install_cmd
```

Lazy-imported. Blocks images/media/fonts at route level so renders stay quick. Headless Chromium, realistic Mac UA, default 15s timeout, never hangs (Playwright timeout + monotonic clock both enforced).

## barbes_comedy result
- **Raw candidates**: 1 (via Playwright; static fetch returned 0)
- **Accepted**: 0 (dropped for no parseable date — canon forbids guessing)
- **Rejected**: 1 (reason: no future date)
- **Errors**: none
- **Verdict**: scraper works; site shows event card without a structured date in static or rendered DOM. Future work: parse the date from the visible card text via a regex on the rendered text, OR add manual admin override.

## fever_paris result
- **Raw candidates**: 0
- **Accepted**: 0
- **Rejected**: 0 (never reached classifier)
- **Errors**: none — rendering succeeded; the DOM simply does not contain `/m/<id>-` event URLs
- **Verdict**: Fever's category listing genuinely does not expose canonical event URLs in HTML, even after JS. Their listings are loaded via internal JSON API with opaque IDs. Honest STUB emitted; recommended next step is reverse-engineering Fever's internal API (cookie/CSRF requirements unknown) or accepting manual submissions.

## Anti-bot / blocking assessment
- **barbes_comedy**: no blocking observed. Page rendered without challenges.
- **fever_paris**: no blocking observed; the issue is structural (URLs not in DOM), not anti-bot. If we DID reverse-engineer the JSON API, anti-bot may surface then.

## Ollama / classifier
- **Reachable** during the venue_direct dry-run for CLASSIFY calls (4 accepts, 4 rejects = real work).
- **Intermittent** elsewhere; surfaces honestly via the `classifier_unreachable` counter and `run_state: PARTIAL`.

## Guardrails
- **Before changes:** ✅ GREEN
- **After changes:** ✅ GREEN
- Live regression on /, /shows, /comedians, /about, /featured API: all clean

## Daily cron
- **Trustable**. Three honest states:
  - GREEN = sources produced data AND classifier was reachable.
  - PARTIAL = classifier was unreachable for ≥1 candidate.
  - FAILED = zero raw events from every source (including Playwright SKIPPED).
- If Playwright/Chromium ever uninstalls, daily run will surface SKIPPED reasons (not crash).

## Files changed
- `scripts/discovery/_playwright_helper.py` (NEW)
- `scripts/discovery/barbes_comedy.py` (static-then-Playwright with structured stubs)
- `scripts/discovery/fever_paris.py` (static-then-Playwright with detail-page render)
- `logs/playwright-helper-2026-05-24.md` (NEW)
- `logs/discovery-source-tests-2026-05-24.md` (appended)
- `docs/audits/ParisComedy-Playwright-Source-Rendering-2026-05-24.md` (NEW) + Obsidian vault copy
- `WORKSESSION_HUD.md`

## Commands run
```
python3 scripts/guardrails/check_invariants.py                                   # pre-flight ✅ GREEN
python3 -c 'import discovery; [importlib.import_module(...)]'                    # 17/17 modules import (with Playwright absent)
python3 scripts/daily_discover.py --dry-run --sources barbes_comedy,fever_paris  # both SKIPPED cleanly (Playwright missing)
pip install --quiet playwright                                                    # OK
python3 -m playwright install chromium                                            # downloaded
python3 -c 'from playwright.sync_api import sync_playwright; ...'                # example.com smoke OK
python3 scripts/daily_discover.py --dry-run --sources barbes_comedy              # 1 raw / dropped no-date / GREEN
python3 scripts/daily_discover.py --dry-run --sources fever_paris                # 0 raw / honest STUB / FAILED
python3 scripts/daily_discover.py --dry-run --sources venue_direct               # 9 raw / 4 accepted / GREEN
python3 scripts/guardrails/check_invariants.py                                   # post-change ✅ GREEN
curl -s https://pariscomedy.com/{,shows,comedians,about}.html | grep …            # no canon violations
curl -s https://api.pariscomedy.com/api/listings?featured=1 | grep -Eoi …         # no PII leaks
```

## Commits pushed
- (push repo) — helper + audit doc + logs committed (scripts/ scraper modules are local-only; not git-tracked)

## Remaining risks
1. PC Ollama at `100.75.13.73:11434` still intermittent (surfaces as PARTIAL, not silent).
2. Fever's internal JSON API not yet wired — task #43 remains open.
3. Barbès card text needs a date-extraction regex if its dates are only in visible text (no JSON-LD).

## Next safest step
Add a visible-text date-extraction pass for barbes_comedy so its 1 raw candidate can be accepted with a real date. Pattern: scan rendered DOM for `\d{1,2} (Jan|Feb|...)|\d{4}-\d{2}-\d{2}` near the event card title.
