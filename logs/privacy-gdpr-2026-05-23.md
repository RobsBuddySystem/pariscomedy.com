# Privacy / GDPR Log — 2026-05-23

## Design decisions
- No raw IPs stored in events table (SHA-256 with INSTALL_SALT)
- Consent modes: essential (default) | all
- Stored in localStorage key: `pc_consent`
- DSR endpoints: /api/dsr/export + /api/dsr/erase (admin-token gated until email verification ready)
- Retention: 18 months default, prune script at scripts/prune_events.py

