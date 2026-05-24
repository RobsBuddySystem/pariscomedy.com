# Discovery source tests — 2026-05-24

## venue_direct group dry-run

```
$ python3 scripts/daily_discover.py --dry-run --sources venue_direct
[cafe_oscar] STUB — no candidates emitted
  reason: site reachable; delegates ticketing to Eventbrite organizer …
[le_coquin] STUB — no candidates emitted
  reason: no stable public event source …
[cuba_compagnie] STUB — no candidates emitted
[green_mic] STUB — no candidates emitted
[the_englishman] STUB — no candidates emitted
[blastoff_comedy] 4 unique Eventbrite eids extracted
[blastoff_comedy] events: 4
[paname_art_cafe] 4 candidate /programmation/ URLs
[paname_art_cafe] events: 4
[barbes_comedy] STUB — no candidates emitted
[golden_comedy_club] STUB — no candidates emitted
[marco_polo_comedy] STUB — no candidates emitted

multi-source discovery: 8 raw events
after dedupe: 8 unique URLs
summary: {"run_state":"GREEN","raw_events":8,"skipped_classification":4,
          "classifier_unreachable":0,"new_shows":4,...}

WOULD ADD show: 'The Open Mic Express - English Stand-Up Comedy | May 26' on 2026-05-26T19:00
WOULD ADD show: 'The Open Mic Express - English Stand-Up Comedy | May 28' on 2026-05-28T19:00
WOULD ADD show: 'The Open Mic Express - English Stand-Up Comedy | May 29' on 2026-05-29T19:00
WOULD ADD show: 'Improvised PowerPoint Comedy Show in English | May 30' on 2026-05-30T19:30
```

## Existing-source regression check

```
$ python3 scripts/daily_discover.py --dry-run --sources timeout_paris
[timeout_paris] fetch failed: https://www.timeout.com/paris/comedy :: HTTP Error 404
[timeout_paris] events: 0
summary: {"run_state":"FAILED",...}   ← honest, not silent
```

## Per-source candidate / acceptance counts

| Source | Raw candidates | Accepted | Rejected | Rejection reason |
|--------|---------------:|---------:|---------:|------------------|
| cafe_oscar | 0 | 0 | 0 | stub — delegated to EB |
| le_coquin | 0 | 0 | 0 | stub — no public source |
| cuba_compagnie | 0 | 0 | 0 | stub — no public source |
| green_mic | 0 | 0 | 0 | stub — delegated to EB |
| the_englishman | 0 | 0 | 0 | stub — domain unreachable |
| blastoff_comedy | 4 | 4 | 0 | — |
| paname_art_cafe | 4 | 0 | 4 | LLM dropped (no date / not stand-up signal) |
| barbes_comedy | 0 | 0 | 0 | stub — JS-rendered (Playwright needed) |
| golden_comedy_club | 0 | 0 | 0 | stub — delegated to BilletReduc |
| marco_polo_comedy | 0 | 0 | 0 | stub — domain unreachable |

## Ollama / classifier
- Reachable at run time for CLASSIFY calls (some accepted, some rejected = real classification).
- Intermittent for EXTRACT_PROMPT (performer-name extraction) — non-blocking.
- run_state honestly logged.

## Playwright pass added 2026-05-24

| Source | Static URLs | Playwright URLs | Outcome |
|---|---:|---:|---|
| barbes_comedy | 0 | 1 | 1 raw candidate, dropped no-date |
| fever_paris | 0 | 0 | honest STUB (Fever uses opaque internal IDs, not /m/<id>- URLs even after JS) |

Full venue_direct group with Playwright: 9 raw / 4 accepted / run_state GREEN.
