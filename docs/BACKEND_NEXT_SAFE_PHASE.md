# BACKEND_NEXT_SAFE_PHASE

**As of BACKEND.PRODUCTION-CUTOVER.BLOCKER-LEDGER (2026-05-30)**

## Recommended: BACKEND.EMAIL.4-OPERATOR-DNS-RUNBOOK

**Why this over the alternatives:**

| Option | Why safe | Why now |
|---|---|---|
| A. BACKEND.ADMIN.1-REVIEW-QUEUE-SHELL | Inert UI — no risk | Useful but requires DB migrations before real value |
| **B. BACKEND.EMAIL.4-OPERATOR-DNS-RUNBOOK** | **Pure docs/runbook — zero code risk** | **Unblocks Auth V2 (magic link emails) which unblocks everything else** |
| C. BACKEND.DB.1-MIGRATION-RUNBOOK | Pure docs/runbook — zero code risk | Also valuable, but email is the longer external dependency |
| D. BACKEND.AUTH.5-LOGIN-V2-DRAFT | Inert UI draft — low risk | Blocked by email anyway |

**Choice: B** — Email DNS is the longest external lead time (Robert must act at Porkbun + Postmark).
Getting the runbook in front of Robert earliest maximizes the chance of having email live
before the first production auth attempt.

## Dependency chain to first live feature

```
BACKEND.EMAIL.4-OPERATOR-DNS-RUNBOOK (Robert acts on DNS)
    └── BACKEND.DB.1-MIGRATION-RUNBOOK (02–07 migration docs)
         └── BACKEND.AUTH.5-LOGIN-V2-DRAFT (inert login UI)
              └── AUTH_V2_ENABLED=true (production cutover)
                   └── EMAIL_SEND_REAL=true (magic links work)
                        └── SUBMISSIONS_V2 / CLAIMS_V2 (admin review queue)
                             └── PAYMENTS_V2 (checkout live)
                                  └── MESSAGING_V2 (paid DMs)
                                       └── TICKETS_V2 (affiliate-enabled imports)
```
