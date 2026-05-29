# 07_CHANGELOG

## 2026-05-29 | data | P1.SOURCE.2
- Scaffolded FNAC Spectacles, Fever, and Weezevent adapters under `scripts/adapter_{fnac,fever,weezevent}.py` following the BilletRéduc pattern. All stubs raise `NotImplementedError("<Platform> adapter — pending operator authorization")`; no network, no parsing, no imports of listings. `data/source-adapters.json` updated: `fnac_spectacles`, `weezevent` flipped none→scaffolded; new `fever` entry added scaffolded; all `enabled: false`. Other platforms untouched. Gate-unlock procedure in `chuck_vault/10-concepts/projects/pariscomedy-canonical/P1_SOURCE_2_DRY_RUN_ADAPTERS.md`. Stub-raises proof captured in vault doc.

## 2026-05-29 | frontend | SHOWS.DEFAULT.1
- `/shows.html` now lands on today's shows first (Paris TZ) instead of "All". New "Today" chip prepended to filter row, default-active; "All" chip moved to end of row. Contextual banner above grid: "Showing tonight's shows — {day} {date}" with a "See all shows" link. Fallback: if today has no shows, walks forward up to 7 days to next available day with appropriate banner copy. `.checked-badge` (P1.DATA.4) preserved. shows.html: 20,321 → 22,661 bytes. Commit `2eedcda`. Verified: initial active chip = "Today" → Friday; 6 of 34 cards visible until "All" clicked.

## 2026-05-29 | frontend | P1.COMPLIANCE.3
- Added French-language mirrors of 3 legal pages: `fr/terms.html`, `fr/privacy.html`, `fr/disclosure.html`. Each fully French, `<html lang="fr">`, French title/meta/og, robots index+follow.
- Added `<link rel="alternate" hreflang="en|fr|x-default">` triplet to all 6 pages (3 EN + 3 FR) for proper SEO cross-linking.
- Added small "Français" / "English" toggle link at top of `<main>`/`<div class="wrap">` of each of the 6 pages. No language-toggle widget on any other page.
- Brand "Paris Comedy" preserved; `payments@pariscomedy.com` preserved; EN-only URLs (`/shows.html`, etc.) preserved. No bilingual/bilingue/mixed-language/multilingual wording in any of the 6 pages.

## 2026-05-29 | frontend | P1.COMPLIANCE.2
- Added `partials/consent.banner.html` — self-contained EN+FR minimal-storage consent banner (HTML + scoped CSS + IIFE JS, zero deps, zero network).
- Embedded inline into `index.html`, `shows.html`, `comedians.html` (49 lines each).
- localStorage key `pc-consent-v1` with `accepted` | `declined`. Verified via Playwright: appear → click OK → hide → reload persists.

## 2026-05-29 | doctrine | CSS-LANG-001
- Scrubbed dead `.badge-bilingual{...}` CSS selector from 227 static comedian pages under `c/`.
- Also removed residual "bilingual" body/meta text in 8 comedian bios (julie-coulon, julie-haddad-kan, lorene-cadeau, patti-mansbach, rey-mendes, robert-le-ricain, sebastian-marx, tania-dutel).
- Sitewide grep for `bilingual|mixed-language` under `c/` returns 0. `.badge-en` + `.badge-fr` preserved.
