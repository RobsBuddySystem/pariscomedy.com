# FINAL.PROOF.1 — Production Proof Manifest

**Generated:** 2026-05-30T00:30:00Z
**Deploy SHA:** 571aa20
**Machine-readable:** `data/final-proof-manifest.json`
**Companion vault doc:** `chuck_vault/10-concepts/projects/pariscomedy-canonical/HANDOFF-2026-05-30.md`

## Summary
| Status | Count |
|---|---|
| live_verified | 26 |
| source_only | 5 |
| audit_only | 3 |
| scaffold_only | 4 |
| needs_visual_proof | 2 |
| needs_backend | 4 |
| **Total entries** | **42** |

## Final closure blockers
1. **P3.AUTH.3** — backend `expires_at` + verify-error vocabulary (API/DB coordination required)
2. **P3.SUBMIT live wiring** — needs `api.pariscomedy.com/api/submissions` endpoint contract
3. **P3.CLAIM live wiring** — needs `api.pariscomedy.com` claim endpoint + verification step
4. **P3.PAYMENTS.1 live** — needs SumUp/Stripe + VAT/legal entity setup
5. **P3.MESSAGING.1 live** — needs WebSocket/polling backend + DB schema
6. **P3.TICKETS.1 / P1.SOURCE.2 live adapters** — needs per-platform operator authorization
7. **Phase 2.4 visual closure** — needs cross-viewport screenshots uploaded to ChatGPT thread
8. **Rate-limit recovery** — 4 agents (P3.CLAIM.5/6 + LIVE.PROOF gallery + P5.HUD.2 + FINAL.CLOSURE.1 pre-audit) failed mid-run to Anthropic API throttle; partial work in working tree

## Per-phase manifest
See `data/final-proof-manifest.json` for the structured per-phase entries with:
- `phase_id` · `status` · `commit_sha` · `public_urls[]` · `live_proof_method` · `rollback` · `limitations` · `next_required_action`

## Mandatory classification (per ChatGPT spec)
- **P3.AUTH.1** = audit_only (not auth fixed)
- **P3.AUTH.2** = live_verified (frontend only; 7 of 10 P3.AUTH.1 findings closed; backend still required for FIND-4/7/10)
- **P3.SUBMIT.1** = audit_only (not submission live)
- **P3.CLAIM.1** = audit_only (not claim flow live)
- **P3.MESSAGING.1** = scaffold_only (not messaging live)
- **P3.PAYMENTS.1** = scaffold_only (not payment live)
- **P1.TICKETS.1** = scaffold_only (not ticket adapters live)
- **P4.SCHEMA.1** = live_verified (Event JSON-LD captured via Playwright DOM on /show.html?slug=charonne with future startDate + inLanguage='en')
- **P5.AUTOMATION.1** = source_only (scheduler is local-machine; daily-proof logs not public-readable)
- **P5.HUD.1** = live_verified (/status.html 200, content panels present in HTML; ChatGPT reader could not open in last pass — supplementary curl proof exists)
- **P4.SITEMAP.1** = live_verified (sitemap.xml 200, 41 URLs, ChatGPT reader could not open in last pass — supplementary curl proof exists)

## Next recommended phase
**BACKEND.PLAN.1** — write a backend/API/DB implementation plan for auth, submissions, claims, payments, messaging so the deferred P3 work can be unblocked. **Plan-only, no implementation**, per master-prompt forbidden list.

After BACKEND.PLAN.1:
- (A) Coordinate with operator on which P3 backend phase to unblock first
- (B) Or proceed to **FINAL.CLOSURE.1** if ChatGPT decides the manifest is sufficient closure

## Verification commitments
- `regression_guard.py` 10/10 PASS
- 27+ public pages 200
- 0 bilingual / mixed-language sitewide
- All commits pushed to `origin/main`
- All vault docs carry `tags: [pariscomedy, ...]` frontmatter

## Rollback
If full session needs rollback: `git revert <commit_range>` (start point: 2004ff9, end point: 571aa20). Vault docs remain (they're additive, no destructive ops).

## Final line
SEND ME THE PROOF OF THE PREVIOUS CHANGES OR CORRECTIONS.
