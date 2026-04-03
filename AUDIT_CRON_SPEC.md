# Paris Comedy Site Auditor — Cron Job Spec

## Name
Paris Comedy Site Auditor

## Schedule
Twice daily: **9:00 AM** and **6:00 PM** (Europe/Paris timezone)

## What It Checks
1. **Eventbrite links** — All booking URLs still return 200 OK (not 404, not redirected to generic page)
2. **Show dates** — No shows with dates in the past still listed as upcoming
3. **Broken pages** — All internal links (HTML pages, CSS, JS) load correctly
4. **Other shows** — Verify `OTHER_SHOWS` entries in `js/data.js` are still active (spot-check Eventbrite/venue pages)
5. **External links** — All `target="_blank"` links resolve (Instagram, Eventbrite org page, Buy Me a Coffee, etc.)
6. **Meta tags** — No stale dates in structured data (JSON-LD `startDate` fields)

## What It Fixes (Automated)
- **Expired shows**: Removes shows from `SHOWS` or `OTHER_SHOWS` arrays where the event is confirmed past/cancelled
- **Dead Eventbrite links**: Removes `bookingUrl` from shows with dead links, flags for manual review
- **Stale JSON-LD dates**: Updates `startDate`/`endDate` to next occurrence based on recurring day-of-week

## What It Flags (Manual Review Required)
- New shows discovered on Eventbrite for known venues
- Venue address changes
- Shows with changed times or days
- Any 5xx errors from external services

## Reports To
`~/.openclaw/agents/hal/workspace/daily/`

### Report Format
- Filename: `pariscomedy-audit-YYYY-MM-DD-HHMM.md`
- Sections: ✅ Passed, ⚠️ Warnings, ❌ Failures, 🔧 Auto-Fixed
- Summary line at top with pass/warn/fail counts

## Implementation Notes
- Use `curl -sL -o /dev/null -w "%{http_code}"` for link checking
- Rate-limit Eventbrite requests (max 1 req/sec) to avoid blocks
- Cache results between 9am and 6pm runs to avoid redundant checks on unchanged URLs
- Git commit any auto-fixes with message: `audit: [description of fix]`
