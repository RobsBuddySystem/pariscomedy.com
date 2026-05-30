# PHASE_LEDGER

Chronological ledger of pariscomedy.com phases. Newest at top.

| date | phase | status | summary |
|------|-------|--------|---------|
| 2026-05-30 | P0.LIVE-DATA-INTEGRITY.2-ROBERT-DECISION-SHEET | awaiting_robert_decision | Decision-only sheet for 6 listings (charonne, millennial-meltdown, theatre-bo-julie, wednesday-night-comedy, ffcn, velvet-comedy). NO DB write. 4/6 CTAs already shielded; ffcn + velvet-comedy still unshielded (verified_24h). |
| 2026-05-30 | P0.LIVE-DATA-INTEGRITY.1C-STATIC-FALLBACK-CTA-FIX | closed | Hardened `no_normal_cta_for_unverified` guard. |
| 2026-05-30 | P0.LIVE-DATA-INTEGRITY.1B-STATIC-FALLBACK-CTA-FIX | closed | Static fallback CTAs gated on live API freshness. |
| 2026-05-30 | P0.LIVE-DATA-INTEGRITY.1-SOT-FIX | closed | CTAs gated on `verification_status === 'verified_24h'`; 6 SOT guards added. |
| 2026-05-30 | ROOT-CAUSE.AUDIT show.html?id=3 dead URL | closed | 8 SOT mapped; DB never updated. |
| 2026-05-30 | P0.BOOK.NUCLEAR-BYPASS + FINAL.FRONTEND.COPY.GUARD.1 + BACKEND.AUTH.3 | closed | /book.html decommissioned; /connect.html canonical. |

## Open / pending

- **P0.LIVE-DATA-INTEGRITY.2** — awaiting Robert's `robert_decision` values per
  row in `data/p0-live-data-integrity-2-robert-decision-sheet.json`.
- **P0.LIVE-DATA-INTEGRITY.3-APPLY-ROBERT-DECISIONS** (planned) — successor
  phase that reads the populated decisions and applies them under strict
  per-row guardrails. Will only open after Robert has confirmed each row.
