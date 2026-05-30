# BACKEND_NEXT_PHASES — recommended sequence after BACKEND.SCAFFOLD.MANIFEST.1

## Immediate next phase (lowest risk)

**BACKEND.AUTH.2-STAGING-ENABLE**
- Apply 002_auth_v2.sql to staging DB
- Set AUTH_V2_ENABLED=true in staging env only
- Run live magic-link round-trip test
- Keep production AUTH_V2_ENABLED=false
- Risk: low — isolated to staging

## Parallel (can run alongside AUTH.2):

**BACKEND.EMAIL.2-DNS-PROVIDER**
- Select provider (Postmark recommended: GDPR-compliant, EU datacenter)
- Add env.example with POSTMARK_API_KEY placeholder
- Document SPF/DKIM records to add in DNS
- Still no real sending until DNS confirmed

## After AUTH.2 staging passes:

**BACKEND.SUBMIT.2-ROUTER-DISABLED**  
Wire submissions_v2_router behind SUBMISSIONS_V2_ENABLED=false. Disabled = 503.

**BACKEND.CLAIM.2-ROUTER-DISABLED**  
Wire claims_v2_router behind CLAIMS_V2_ENABLED=false.

**BACKEND.ADMIN.1-REVIEW-QUEUE-SCAFFOLD**  
Admin UI for reviewing submissions/claims/ticket candidates.

## After legal/compliance cleared:

**P1.COMPLIANCE.1** — EN/FR legal pages, real cookie consent, affiliate/ticket disclosure.

## After compliance:

**BACKEND.AUTH.3-PRODUCTION-ENABLE**  
Apply 002_auth_v2.sql to production. Enable AUTH_V2_ENABLED=true.

## Deferred until post-compliance:

- BACKEND.PAYMENTS.2-PROVIDER (Stripe/SumUp selection + real checkout)
- BACKEND.MESSAGING.2-ROUTER-ENABLE
- BACKEND.TICKETS.2-ADAPTER-RUN (first live per-platform run, human review required)
- Phase 2.4 nav extraction (still BLOCKED pending P0 closure)
