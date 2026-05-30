# FINAL.FRONTEND.COPY.GUARD.1

**Status:** IN_GIT_UNVERIFIED — pending ChatGPT closure  
**Authorized by:** ChatGPT 2026-05-30 (after BACKEND.EMAIL.2-DNS-PROVIDER closed)

## Scope

Final public copy audit before any backend cutover. No backend behavior changes,
no feature flags enabled, no payments/auth/messaging work.

## Copy bugs found and fixed

| File | Line | Issue | Fix |
|---|---|---|---|
| book.html | 238 | "€1 lifetime (first 100)" + "Claim my €1 lifetime spot →" | → "founding-member early access" + "See early access →" |
| show.html | 244-245 | "All comedy shows in Paris" / "All comedy venues in Paris" | → "Comedy shows in Paris" / "Comedy venues in Paris" |

## Regression guard updates (scripts/regression_guard.py)

Added to `check_pricing_copy_safety()` forbidden list:
- `checkout is live`
- `messaging is live`
- `direct messages available now`
- `affiliate links active`

Added new `check_public_copy_overclaims()` function scanning 8 public HTML files for:
- Coverage: `every show in paris`, `all shows in paris`, `all comedy shows in paris`, `definitive guide`, `complete list`
- Payment: `claim my`, `lifetime spot`, `continue to payment`, `paid through sumup`, `pay now`, `subscribe now`, `checkout is live`
- Feature: `messaging is live`, `direct messages available now`, `payment active`, `affiliate links active`, `auth v2 live`, etc.

Safe negations excluded (lines containing "checkout is not live", "planned", "coming soon", etc.)

Registered as `"public_copy_overclaims"` in CHECKS dict.

## Verification

- `public_copy_overclaims`: PASS (0 hits)
- `pricing_copy_safety`: PASS (0 hits)
- No backend files changed
- No secrets committed
- No feature flags enabled
