# 07_CHANGELOG

## 2026-05-29 | infra | P5.AGENTS.1
- Added `scripts/agent_write_lock.py` — stdlib-only file lock helper. Atomic create via `os.open(O_CREAT|O_EXCL)` on `.pc-write.lock` at repo root; JSON payload `{agent_name, scope, acquired_at, pid}`. Four commands: `acquire <agent> "<scope>"`, `release`, `read_status`, `enforce_for_commit`. Stale-timeout 15 min — a lock older than that is overridden with a stderr warning, so a crashed agent never locks out the next run.
- Added `.githooks/pre-commit` — calls `enforce_for_commit`. **Soft enforcement**: only blocks when `PC_AGENT_NAME` is set AND mismatches the lock holder. Humans + the main agent (no `PC_AGENT_NAME`) stay free. Activate per-clone with `git config core.hooksPath .githooks`.
- `.gitignore` — `.pc-write.lock` ignored (runtime artifact, never committed).
- `data/source-adapters.json` — added `_write_lock_policy` field documenting that adapter scripts must acquire/release before any write to `data/`.
- Anti-PROCESS-P1-001: codifies single-writer-at-a-time so batched out-of-order writes can't contaminate `data/*.json`, HTML, or partials mid-session.
- Verified locally: `acquire test_agent "demo"` → lock written; `read_status` → holder JSON; `release` → removed. No HTML touched. `regression_guard.py` still 10/10 PASS.
- Vault: `chuck_vault/10-concepts/projects/pariscomedy-canonical/P5_AGENTS_1_WRITE_LOCK.md`.

## 2026-05-29 | ux | P2.UX.2
- Playwright audit at mobile 390x844, tablet 820x1180, desktop 1280x900 against production `https://pariscomedy.com` across 7 pages (`/`, `/shows.html`, `/venues.html`, `/comedians.html`, `/show.html?slug=charonne`, `/pricing.html`, `/book.html`) — 21 page-viewport runs total. Per-run probe: horizontal overflow (`scrollWidth > clientWidth`), elements wider than viewport, nav visibility/scroll, primary CTA widths (`.btn-primary/.btn-secondary/.btn-book/.btn-plan`), footer presence, `pageerror` count. Output: `data/ux-mobile-tablet-audit.json`; screenshots at `/tmp/p2-ux-2/{viewport}-{page}.png`.
- 1 issue found: mobile (390px) homepage horizontal overflow (`sw=558` vs `vw=390`). Root cause: `.hero-left h1` containing the unbreakable hyphenated word "English-Language" forced min-content width ~540px, expanding the single-column grid track past the viewport. Small CSS fix applied inline in `index.html`: `.hero-left{min-width:0}`, `.hero-left h1{...overflow-wrap:anywhere;word-break:break-word}`, plus a `@media(max-width:480px)` h1 size clamp override. Re-verified locally → `sw=390`, `h1.width=354`, no horizontal scroll. No external CSS, no nav/footer/script changes.
- 20 other runs GREEN: no nav overflow, no footer missing, no too-narrow / too-wide CTAs, no `pageerror`s. Zero deferred BUGs.
- Vault: `chuck_vault/10-concepts/projects/pariscomedy-canonical/P2_UX_2_MOBILE_TABLET_AUDIT.md`.

## 2026-05-29 | infra | P2.UX.1
- Added `header_cta_rule` check to `scripts/regression_guard.py` (now 10 checks total). For each public page, extracts the first `<nav class="nav-shell-*">` block, collects every `href`, and diffs against the canonical href set parsed from the matching `partials/nav.shell.<variant>.html`. FAIL on any extra href (page-specific CTA leaking into the global nav) or more than one missing canonical href.
- Canonical sets parsed at runtime: marketing (9), minimal (1), auth (3), portal (6), admin (8). Documented exceptions: `/archive.html` may carry an extra `/archive.html` link; `/disclosure.html` + `/fr/disclosure.html` (minimal shell) may carry curated cross-legal links (`/about`, `/shows`, `/terms`, `/privacy`, `/fr/terms`, `/fr/privacy`).
- Wired into the default-run list. Verified: `python3 scripts/regression_guard.py` → 10/10 PASS; standalone `--check header_cta_rule` → PASS (30 pages inspected). Status sweep still 31/31. No HTML touched.
- Vault: `chuck_vault/10-concepts/projects/pariscomedy-canonical/P2_UX_1_HEADER_CTA_RULE.md`.

## 2026-05-29 | infra | P5.AUTOMATION.1
- Added `scripts/daily_proof_package.py` — single aggregator that runs `freshness_verify.py` + `regression_guard.py` + `generate_sitemap.py`, captures each into a structured JSON, and writes `logs/daily-proof-{ISO}.json` with sections `freshness`, `regression`, `sitemap-size` plus a top-level `failures` array. Exit 0 if all PASS, 1 if any FAIL. stdlib only.
- Extended `scripts/freshness_daily_wrapper.sh` — after the existing freshness commit, invokes the aggregator (output appended to `logs/freshness-daily.log`) and commits/pushes `sitemap.xml` if it changed. `logs/daily-proof-*.json` stays local as the evidence trail.
- Verified: `bash scripts/freshness_daily_wrapper.sh` → exit 0; status sweep 31 pages, 0 bad (≥27 pages 200). No HTML touched.

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
