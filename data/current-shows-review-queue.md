# Current shows review queue

Seed/doc candidates that **should not be published as current until re-verified**.

Last updated: 2026-04-06
Owner: Chuck

## Why this file exists
The comedians page is now a verified public reference. If a show appears in the seed Google Doc or older repo history but we cannot confidently confirm it tonight, it lives here until Chuck verifies it.

## Needs manual verification

### Likely active, but not verified enough for public current layer tonight
- **The Dissident Comedy Show** — The Dissident Club — Wednesday 20:30  
  Was in earlier site data; needs live recurrence check.
- **Friday Night Show** — La Pomme d'Eve — Friday 20:00  
  Previously listed in repo history; not re-added without fresh verification.
- **English Stand-Up Thu & Sat** — 76 Rue Jean-Pierre Timbaud — Thursday / Saturday 18:30  
  Prior listing exists, but recurrence needs reconfirmation.
- **Mic Drop Comedy Club** — Speechless — Wednesday 20:00  
  Previously in repo history; needs fresh live source.
- **Millennial Meltdown** — Le Bikini Bottom — Wednesday 20:00  
  Previously in repo history; needs current-source confirmation.

### Historical / stale unless re-verified
- **Paname English Stand-Up** — Paname Art Café — Tuesday 17:30  
  Kept as archive/history context for now, not current public layer.
- **Broadway Comedy Club Paris** — 25 Bd de Bonne Nouvelle  
  Live Eventbrite page fetched again on **2026-04-06** and clearly shows a multi-date listing at the known address, but the recurrence/day pattern is still not clean enough to promote back into the public current layer without risking a bad schedule claim. Keep archived publicly for now; re-promote only after a cleaner cadence/time confirmation.

## Promotion log
- **2026-04-06:** **Funny Women Paris** promoted from review to public current layer after a direct Eventbrite fetch confirmed: multiple dates, **Le Noddi (16 Rue Bernardins, 75005 Paris)**, **doors 20:00 / show 20:30**, Tuesday recurrence, and a live booking URL.

## Verification standard
Before moving any item from this file into `js/data.js`, confirm:
1. live public listing exists
2. day/time still matches
3. venue still matches
4. source is recent enough to justify `verifiedAt`

## After verification
- Add to `OTHER_SHOWS_RAW` in `js/data.js`
- Include `runner`, `verificationSource`, `verifiedAt`, and `showUrl`
- Remove the item from this review queue
