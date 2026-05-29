# 07_CHANGELOG

## 2026-05-29 | frontend | P1.COMPLIANCE.2
- Added `partials/consent.banner.html` — self-contained EN+FR minimal-storage consent banner (HTML + scoped CSS + IIFE JS, zero deps, zero network).
- Embedded inline into `index.html`, `shows.html`, `comedians.html` (49 lines each).
- localStorage key `pc-consent-v1` with `accepted` | `declined`. Verified via Playwright: appear → click OK → hide → reload persists.
