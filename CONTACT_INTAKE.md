# Paris Comedy contact + newsletter intake

## What changed
- Front-end forms now try a **local intake endpoint** first: `POST /api/intake`
- Every submission is:
  1. validated
  2. stored in `data/intake/submissions.sqlite3`
  3. appended to `data/intake/submissions.jsonl`
  4. forwarded to `chucklericain@icloud.com`
- If the local endpoint is unavailable, the browser falls back to FormSubmit so leads are not lost tonight.

## Run locally
```bash
cd /Users/chuck/.openclaw/workspace/pariscomedy.com
python3 api/intake_server.py 8787
```

Then reverse-proxy `/api/intake` and `/api/intake/health` to `http://127.0.0.1:8787`.

## Files
- `api/intake_server.py` — local HTTP endpoint
- `api/validate_intake.py` — quick integrity check
- `data/intake/submissions.sqlite3` — primary store
- `data/intake/submissions.jsonl` — append-only backup log

## Validator workflow
Run after changes or before a deploy:
```bash
python3 api/validate_intake.py
```
You want:
- `db_submissions` = `jsonl_submissions`
- `forward_failures` = 0

If `forward_failures > 0`, nothing is lost — resend from the database/jsonl log.

## Backup workflow
Tonight's practical backup plan:
1. Keep sqlite as the live store.
2. Keep JSONL as append-only recovery log.
3. Include `data/intake/` in the normal machine backup job.
4. Before/after deploys, copy `data/intake/` somewhere safe if there are fresh leads.

## Notes from the audit
- Previous setup sent directly to a third-party inbox relay with no local storage.
- `book.html` contact inputs were missing `name=` attributes, so the old contact form was not reliably sending full contact data.
- Newsletter popup also pointed straight at the third-party endpoint.

This new setup is boring on purpose: local first, recoverable, inspectable, and still backed up by a browser-side fallback.
