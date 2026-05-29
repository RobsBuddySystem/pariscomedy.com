# 07_CHANGELOG

## 2026-05-29 | infra | P4.SITEMAP.1
- Regenerated `sitemap.xml` from real public pages + verified shows. Now includes 15 public pages + 13 `/show.html?slug=...` entries (only `verified_24h`/`verified_72h` from `data/freshness-audit.json`) = 28 URLs. Each `<lastmod>` from `git log -1 --format=%cs`. Six legal pages (terms/privacy/disclosure × EN/FR) carry `xhtml:link rel="alternate" hreflang` pairs + `x-default`.
- Excluded (noindex or auth-only): `404.html`, `admin-{events,crm,messages,payments,submit}.html`, `booker-{portal,dashboard}.html`, `performer-portal.html`, `show-runner.html`, `login.html`, `checkout-pending.html`, `r.html`.
- `robots.txt` rewritten: `Disallow` for all admin/portal/login pages + `/api/`; `Sitemap: https://pariscomedy.com/sitemap.xml` retained.
- Generator: `scripts/generate_sitemap.py` (stdlib only). Reads `data/freshness-audit.json` so daily freshness wrapper can keep sitemap fresh.
- Vault: `chuck_vault/10-concepts/projects/pariscomedy-canonical/P4_SITEMAP_1_SITEMAP_GENERATOR.md`.

## 2026-05-29 | infra | PROCESS.ROOT.1
- Added `scripts/regression_guard.py` — stdlib-only Python 3 guard that runs 9 live-production checks against pariscomedy.com: forbidden-strings (bilingual/mixed-language/marketing-claim leakage), internal-CTAs (/venues.html → /show.html, no external bypass), raw-includes (no unprocessed `<!-- include: -->`), stale-homepage-panel (next3-row populated or explicit empty msg), card-render (/comedians.html + /shows.html non-zero), status-sweep (31 named public URLs return 200), nav-consistency (one `nav-shell-*` per page), freshness-sanity (/data/freshness-audit.json parses, zero stale rows), hreflang (3 alternates per legal page × EN+FR).
- Single check via `--check <name>`; optional Playwright DOM probes via `--with-dom`. JSON evidence written to `logs/regression-guard.<ISO>.json` (gitignored).
- CI: `.github/workflows/regression-guard.yml` runs the guard on push + PR to `main`.
- Doc: `chuck_vault/10-concepts/projects/pariscomedy-canonical/PROCESS_ROOT_1_REGRESSION_GUARD.md` (check rationale + add-a-check procedure).
- First live run (2026-05-29): 8/9 PASS. `nav_consistency` legitimately flagged 3 legacy bare-`<nav>` pages (`/disclosure.html`, `/show.html`, `/show-runner.html`) that haven't been migrated to `nav-shell-*` partials — real drift, deferred fix.

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

## 2026-05-29 | frontend | P5.HUD.1
- Added `/status.html` — single-page operator HUD. Robots noindex, admin nav shell, auto-refresh 60s. Renders: (1) freshness summary from `/data/freshness-audit.json` (total + by-status metrics + per-listing color-coded table); (2) source adapter status from `/data/source-adapters.json`; (3) live page-health probe of 27 public URLs with `{cache:'no-store'}` fetch; (4) doctrine forbidden-string scan over `/`, `/shows.html`, `/comedians.html`; (5) phase ledger summary. Zero deps, inline CSS+JS. Added `status.html` to `EXCLUDED_PAGES` in `scripts/generate_sitemap.py` and regenerated `sitemap.xml` (15 URLs, status.html absent). Operator-only — not linked from any public nav; bookmark to access.
