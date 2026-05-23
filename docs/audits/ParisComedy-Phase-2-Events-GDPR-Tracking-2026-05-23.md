# ParisComedy — Phase 2: Unified Events + GDPR Tracking (2026-05-23)

## Status: GREEN

---

## Files changed

### New files
| File | Description |
|------|-------------|
| `assets/events.js` | Unified client event tracker: `window.pcTrack()`, consent banner, auto-tracks page views + 13 event types |
| `admin-events.html` | Token-gated events dashboard: metrics grid, top pages, referrers, by-type table, conversion funnel |
| `logs/events-build-2026-05-23.md` | Build log |
| `logs/privacy-gdpr-2026-05-23.md` | GDPR design decisions |
| `logs/forms-tracking-test-2026-05-23.md` | Test checklist |
| `logs/admin-events-dashboard-2026-05-23.md` | Dashboard build log |
| `scripts/prune_events.py` | Retention prune script (18-month default, dry-run by default) |

### Modified files
| File | Change |
|------|--------|
| `~/.openclaw/.../main.py` | +561 lines: events table, track_event(), /api/events, /api/admin/events/summary, /api/admin/events/timeline/{show_id}, /api/dsr/export, /api/dsr/erase |
| All 13 public HTML pages | events.js injected |
| `index.html` | newsletter form fires pcTrack(form_submit_attempt/success/error/newsletter_signup) |
| `booker-dashboard.html` | notifyComics + exportLineup fire pcTrack; show timeline panel added |

---

## Commits
- `748dbcc` — frontend: Phase 2 events.js + admin dashboard + all public pages
- `a5519b2` — backend: events table + endpoints (in paris-comedy repo)

---

## Database migrations added
- `events` table (CREATE TABLE IF NOT EXISTS) — auto-migrates on first request
- INSTALL_SALT added to `.env`

---

## Tests run

| Test | Result |
|------|--------|
| main.py AST parse | PASS |
| pcTrack defined in events.js | PASS |
| Consent banner present | PASS |
| events.js injected in all 13 public pages | PASS |
| POST /api/events: page_view | PASS |
| POST /api/events: ticket_click | PASS |
| POST /api/events: affiliate_click | PASS |
| POST /api/events: pricing_cta_click | PASS |
| POST /api/events: comic_profile_open | PASS |
| POST /api/events: form_submit_success | PASS |
| POST /api/events: notify_booked_comics | PASS |
| POST /api/events: lineup_export | PASS |
| POST /api/events: unknown type rejected | PASS (ok:false) |
| GET /api/admin/events/summary (token) | PASS — returned 8 events across 8 types |
| GET /api/dsr/export (admin-gated) | PASS — returns email data |
| GET /api/dsr/export (no token) | PASS — 401 |
| No raw IP in events table | PASS — actor_hash only (SHA-256 salted) |
| No Instagram/social links reintroduced | PASS |
| No Stripe references | PASS |
| No stale launch banner | PASS |
| No false "every link verified" claim | PASS |

---

## Admin dashboard proof

```
GET /api/admin/events/summary?days=7&token=pc-admin-2026

{
  "total_events": 8,
  "page_views": 1,
  "unique_sessions": 8,
  "by_type": [
    {"event_type": "affiliate_click",   "count": 1},
    {"event_type": "comic_profile_open","count": 1},
    {"event_type": "form_submit_success","count": 1},
    {"event_type": "lineup_export",     "count": 1},
    {"event_type": "notify_booked_comics","count": 1},
    {"event_type": "page_view",         "count": 1},
    {"event_type": "pricing_cta_click", "count": 1},
    {"event_type": "ticket_click",      "count": 1}
  ],
  "funnel": [...]
}
```

---

## Privacy / GDPR decisions

- No cookies used. Session ID in `sessionStorage` only.
- No raw IPs stored. All actor identifiers are `SHA-256(INSTALL_SALT + raw_ip)[:16]`.
- Consent: `essential` (default) | `all`. Stored in `localStorage`.
- Consent banner: small, non-blocking, bottom of screen.
- DSR export + erase: admin-token gated (magic-link verification deferred).
- Retention: 18 months. Prune script at `scripts/prune_events.py`. **Not auto-scheduled** — run manually after dry-run review.
- Affiliate click infrastructure preserved: `/r.html`, `data/affiliates.json`, tracking hooks intact. TODO: insert real affiliate IDs after signing up.

---

## Live site status

- GitHub Pages (static): all public pages clean, no P0 regressions.
- Backend (port 8765): hot-reloaded, new endpoints live.
- Admin dashboard (`/admin-events.html`): token-gated, functional.
- Show timeline in booker-dashboard: loads from `/api/admin/events/timeline/{id}`.

---

## Phase 2: GREEN ✅

---

## Next revenue-positive step

**Register for affiliate programs** to activate the already-built affiliate revenue pipeline:
1. Eventbrite Affiliate Program → replace `"eb_ref": "TODO_REAL_EB_AFFILIATE_ID"` in `data/affiliates.json`
2. GetYourGuide Partner Program → replace `"gyg_ref": "TODO_REAL_GYG_AFFILIATE_ID"`
3. Once IDs are live, every ticket click through `/r.html` generates affiliate commission automatically.
4. Dashboard: `/admin-events.html` already tracks affiliate clicks for ROAS measurement.
