# Current shows workflow

> Internal note: ops-only workflow for maintaining verified show listings. Not public website copy and not a blog brief.

This repo now treats the comedians/current-shows page as a **verified public reference**, not a brainstorm list.

## Source hierarchy
1. **Seed source:** the Google Doc / comedian submissions / Chuck notes
2. **Verification source:** public live listing (usually Eventbrite, sometimes BilletReduc or venue page)
3. **Public output:** `js/data.js` → `OTHER_SHOWS_RAW` / `OTHER_SHOWS` / `CURRENT_SHOWS_BY_VENUE`
4. **Manual review bucket:** `data/current-shows-review-queue.md`

## Rules
- If a show has a live public listing and looks clearly current, add it to `OTHER_SHOWS_RAW` with:
  - `runner`
  - `verificationSource`
  - `verifiedAt`
  - `showUrl`
- If a show is mentioned in the seed doc but **cannot be confidently verified tonight**, do **not** invent or backfill facts.
  - Put it in `data/current-shows-review-queue.md` instead.
- Only shows with recent verification belong in the public current layer.
- Historical venues/shows can stay in `VENUES` or archive notes, but should not be presented as current.

## Nightly maintenance checklist
1. Open the seed source (Google Doc / inbound corrections).
2. Compare against `js/data.js` current entries.
3. For each candidate:
   - Confirm a live listing/source exists
   - Confirm venue + day/time still match
   - Add/update verified entries in `OTHER_SHOWS_RAW`
   - Move uncertain items into `data/current-shows-review-queue.md`
4. Review `comedians.html` and `book.html` copy to make sure corrections still route to Chuck.
5. Commit with a message that says what changed.

## Where corrections go
- Public correction CTA: `comedians.html` → `book.html#contactForm`
- Human owner for corrections: **Chuck**
- Public wording should always make that clear so comics know who is reviewing changes.

## Files to touch most often
- `js/data.js` — verified current-show data
- `js/app.js` — comedians directory rendering
- `comedians.html` — public reference page copy
- `book.html` — correction / add-a-show intake copy
- `data/current-shows-review-queue.md` — uncertain seed candidates waiting on verification

## Tonight's first-pass ingest note
Because the seed doc is broader than the verified public layer, some items may appear in the review queue first. That's intentional: better an explicit review list than fake certainty on the public site.
