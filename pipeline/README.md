# ParisComedy Pipeline

Daily scraping pipeline that discovers new comedy events from Eventbrite Paris,
classifies them with a local LLM, and merges high-confidence shows into the site.

## Architecture

```
openclawpc (RTX 3090, LAN)          Mac Studio (canonical repo)
────────────────────────────        ────────────────────────────
Eventbrite /d/france--paris/        data/shows.json  ←── merge
comedy/ + english-comedy/ +               ↓
stand-up-comedy/                    data/shows_generated.json
       ↓                                  ↓
  01_scrape.py                      generate_instances.py
       ↓                                  ↓
  02_normalize.py               pipeline/output/review_queue.json
       ↓                                  ↓
  03_llm_extract.py             api/review-queue.html (admin UI)
    ↑ Ollama: qwen2.5:32b                 ↑
    ↑ http://100.75.13.73:11434           │
  04_dedupe.py                   receive_on_mac.sh
       ↓                                  ↑
  05_classify.py ────────────── rsync over SSH (LAN)
       ↓                                  ↑
  06_validate.py             sync_to_macstudio.sh
       ↓                                  ↑
  07_export.py ──────────────────── (runs after pipeline)
       ↓
  08_review_queue.py
       ↓
  pipeline/output/review_queue.json
  pipeline/output/metrics_YYYYMMDD.json
```

**Flow summary:**
1. openclawpc runs the full 8-stage pipeline at 06:00 Paris time
2. At 06:35, `sync_to_macstudio.sh` rsyncs output JSONs over SSH/LAN
3. Mac Studio's launchd plist detects the file change and calls `receive_on_mac.sh`
4. `receive_on_mac.sh` regenerates instances, commits, and pushes to GitHub Pages
5. pariscomedy.com is live within ~5 minutes of the rsync

---

## Quick Start

### openclawpc setup

```bash
# 1. Clone or pull the repo
cd /home/chuck && git clone git@github.com:RobsBuddySystem/pariscomedy.com.git _repo
cd _repo

# 2. Install Python deps
pip3 install requests beautifulsoup4 pyyaml python-dateutil

# 3. Verify Ollama is running with the right model
curl http://100.75.13.73:11434/api/tags | python3 -m json.tool | grep name
# Expected: "qwen2.5:32b" and/or "mistral:7b"

# 4. Test run (uses cached fixture if available, no live fetch)
./pipeline/run_pipeline.sh --dry-run

# 5. Full run
./pipeline/run_pipeline.sh

# 6. Install crontab
crontab pipeline/automation/openclawpc.crontab
```

### Mac Studio setup

```bash
# Install launchd watcher
cp pipeline/automation/macstudio.launchd.plist \
   ~/Library/LaunchAgents/com.pariscomedy.receive.plist
launchctl load ~/Library/LaunchAgents/com.pariscomedy.receive.plist

# Verify it loaded
launchctl list | grep pariscomedy
```

---

## Stage Descriptions

| Stage | File | Input → Output | Purpose |
|-------|------|----------------|---------|
| 01 | `01_scrape.py` | live fetch → `raw_scraped.json` | HTTP scrape Eventbrite comedy pages; parse article cards + JSON-LD |
| 02 | `02_normalize.py` | raw → `normalized.json` | Parse dates to ISO 8601/Paris TZ, clean venue names, dedup by EB ID |
| 03 | `03_llm_extract.py` | normalized → `llm_classified.json` | qwen2.5:32b classifies comedy/type/language; keyword fallback if Ollama down |
| 04 | `04_dedupe.py` | llm → `deduped.json` | MD5 fingerprint on name+date+venue; keep highest-confidence dupe |
| 05 | `05_classify.py` | deduped → `classified.json` | Adjust confidence with keyword signals; assign high/review/reject tier |
| 06 | `06_validate.py` | classified → `validated.json` | Verify required fields; filter past-date shows; flag far-future |
| 07 | `07_export.py` | validated → `data/shows.json` + `review_queue.json` + metrics | Merge high-tier into shows.json; write review queue; call generate_instances.py |
| 08 | `08_review_queue.py` | `review_queue.json` → `api/review-queue.html` | Format HTML admin table for human review |

---

## Confidence Thresholds

```
≥ 0.80  HIGH    → auto-publish to data/shows_generated.json
0.50–0.79 MEDIUM → review_queue.json (human reviews in admin UI)
< 0.50  LOW     → discard (logged in stage 07)

Scoring formula:
  base = llm.confidence (0.0–1.0 from qwen2.5:32b)
  + 0.10 if name contains comedy signal word
  + 0.05 if has verified Eventbrite URL (eventbrite.com/e/ or eventbrite.fr/e/)
  + 0.05 if has specific start_date
  - 0.20 if name contains exclusion word (yoga, boxing, fashion, etc.)
  - 0.10 if description is empty
  clamped to [0.0, 1.0]
```

---

## Recommended Ollama Models

| Model | VRAM | Speed | Notes |
|-------|------|-------|-------|
| `qwen2.5:32b` | ~20GB | medium | **Primary.** Best French/English comedy detection. Already in use on PC-LAPTOP. |
| `mistral:7b` | ~5GB | fast | **Fallback.** Lower accuracy but runs anywhere. |
| `llama3.2:3b` | ~2GB | very fast | Emergency fallback. Minimal accuracy. |
| `qwen2.5:72b` | ~45GB | slow | Upgrade path if 3090 gets more VRAM. |

Endpoint fall-through order (mirrors `brain-daemon-local-llm.py`):
1. `http://localhost:11434` (Mac Ollama, if installed)
2. `http://100.75.13.73:11434` (PC-LAPTOP via Tailscale — live endpoint)
3. `http://openclawpc.tail6669ff.ts.net:11434` (3090 box, if also running ollama serve)

---

## How to Add a New Source

1. Add an entry to `pipeline/config.yml` under `sources:`:
   ```yaml
   sources:
     my_new_source:
       url: "https://example.com/paris-comedy-events"
       enabled: true
   ```
2. If the site uses a non-standard layout, add a parser branch in `01_scrape.py`
   `parse_eventbrite_search_page()` — or add a separate `parse_my_new_source()` function
   and dispatch by source key.
3. Run `./pipeline/run_pipeline.sh --stage 01` to test just the scrape stage.

---

## Review Queue Workflow

1. Pipeline runs at 06:00, writes `pipeline/output/review_queue.json`
2. Stage 08 formats it to `api/review-queue.html`
3. After rsync + push, admin opens `https://pariscomedy.com/api/review-queue.html`
4. Each row shows: event name (linked to EB), date, venue, confidence score, type
5. [Accept] opens a pre-filled email to hello@pariscomedy.com
6. Robert pastes the accepted show ID into `data/shows.json` manually (for now)

**Future:** POST to `/api/review` endpoint → auto-appends to shows.json without email.

---

## Data Preservation Rules

- Shows are **never deleted** from `data/shows.json` — only marked `is_archived: true`
- Comedians in `data/comedians.json` are **never deleted** — only `active: false` added
- `generate_instances.py` already filters `is_archived: false` for public rendering
- The `comedian_history` field on each comedian records past Paris shows

---

## Future Extensions

- **Comic self-submission**: POST to `/api/submit-show` → `pipeline/output/submissions.json`
  → stage 08 picks it up for the same human-review flow. No new code needed in the
  pipeline — submissions just start as `confidence: 0.60` (review tier by default).
- **Venue claims**: venue owners POST to `/api/claim-venue` with proof (IG link, email) →
  admin review → `verified: true` flag in `venues.json`. Pays off in address accuracy.
- **Paid promotion**: `featured: true` + `promoted_until: date` fields already in the
  show schema; `generate_instances.py` respects them. Billing handled externally.
  Pipeline never touches `featured` — it's admin-only.
- **Confidence escalation to Claude API**: if `qwen2.5:32b` returns `confidence < 0.60`
  and all three Ollama endpoints are live (i.e., not a service failure), optionally POST
  to `claude-haiku-4-5` for a second opinion. Cost ~$0.001/show. Gated by a
  `llm.escalate_to_claude` flag in `config.yml` (default: false).
- **Multi-city**: the pipeline is city-agnostic. Change the source URLs and `timezone`
  in `config.yml`. Keep it Paris-only until Robert explicitly says go.
