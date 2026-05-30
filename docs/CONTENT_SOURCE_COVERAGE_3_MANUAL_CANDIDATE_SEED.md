# CONTENT.SOURCE-COVERAGE.3 — Manual Candidate Seed

**Status: DATA SEED ONLY — NO PUBLIC IMPORT**  
**Date: 2026-05-30**  
**Seed count: 9 | Excluded: 3 (future_watch or below confidence threshold)**

All seeds have `import_allowed=false`, `affiliate_enabled=false`, `proposed_status=needs_human_review`.

---

## Included Seeds

| Seed | Candidate | Show name | Venue | Language | Confidence | Source URL |
|---|---|---|---|---|---|---|
| S001 | C001 | Coucou Comedy — Tuesday | Le Noddi, 75005 | en | 90 | [Eventbrite](https://www.eventbrite.com/o/coucou-comedy-43230488853) |
| S002 | C002 | Coucou Comedy — Friday | Broadway Comedy Club, 75002 | en | 85 | [Eventbrite](https://www.eventbrite.com/o/coucou-comedy-43230488853) |
| S003 | C003 | Sebastian Marx NY Comedy Night | La Scène Barbès, 75018 | en | 80 | [sebmarx.com](https://www.sebmarx.com/en/) |
| S004 | C004 | Paname Comedy Club | Paname Art Cafe | fr | 88 | [FNAC Spectacles](https://www.fnacspectacles.com/artist/paname-comedy-club/paname-comedy-club-paris-3410304/) |
| S005 | C005 | Golden Comedy Club | Golden Comedy Spot, 75002 | fr | 92 | [Fever](https://feverup.com/m/111045/en) |
| S006 | C006 | Oscar Comedy Club | Café Oscar, 75002 | fr | 88 | [Eventbrite](https://www.eventbrite.fr/e/oscar-comedy-club-tickets-1672589683769) |
| S007 | C008 | The Joke Comedy Club | The Joke, 75004 | fr | 82 | [Fever](https://feverup.com/en/paris/venue/the-joke) |
| S008 | C009 | Le Plateau Comedy Club | Monsieur le Zinc, 75010 | fr | 78 | [Fever](https://feverup.com/m/474472/en) |
| S009 | C010 | Le Fridge Comedy Night | Le Fridge Comedy, 75002 | fr | 75 | [BilletRéduc](https://www.billetreduc.com/263384/evt.htm) |

---

## Excluded

| Candidate | Reason |
|---|---|
| C007 — Marco Polo Comedy Club | `future_watch` — schedule data ends April 2026; verify before including |
| C011 — Fridge Open Mic | Confidence 72 < 75 threshold; C010 (main show) already covers same venue |
| C012 — No Name Comedy Club | `future_watch` — confidence 65 < 75; insufficient detail for seeding |

---

## Review Questions (per seed)

Each admin review session must answer for each seed:
1. Is the listing still current? (Check source URL for upcoming dates)
2. Is the venue/address still accurate?
3. Is this a duplicate of an existing ParisComedy active listing?
4. Is the source page primary enough (ticket page > guide page > social signal)?
5. Should this become a public listing after verification?

---

## Seed File Safety

- `import_allowed: false` on all 9 rows
- `affiliate_enabled: false` on all 9 rows
- `proposed_status: needs_human_review` on all 9 rows
- No public listings created
- No DB writes made
- No import routes called
- Public site unchanged
