# Changelog — pariscomedy.com

Whole-app changelog (frontend + backend). This file is kept identical in both
repos so either clone shows the full app history.

**Commit message standard (mandatory):**

```
YYYY-MM-DD HH:MM TZ | area | change summary
```

`area` is one of: `frontend`, `backend`, `data`, `infra`, `docs`.

Tag stable milestones: `vYYYY.MM.DD-<label>` (e.g. `v2026.05.22-core-ready`).

---

## 2026-05-22

- `2026-05-22 | infra | VCS + ops hardening sprint` — portable commit-policy
  enforcement (`scripts/validate-commit-msg.sh`, `scripts/install-hooks.sh`);
  GitHub Actions `commit-msg-check` + `gitleaks` in both repos; encrypted
  off-machine runtime-data backup (`backup_runtime_data.sh` / `restore_runtime_data.sh`,
  daily launchd schedule, `BACKUP_RUNBOOK.md`); `.editorconfig`, `.gitattributes`,
  `dev-check.sh`, `RELEASE_CHECKLIST.md`, `SECRET_ROTATION.md`; machine-readable
  `parity_check.sh --json`. Secret scan: gitleaks clean on both repos' full history.
- `2026-05-22 20:17 CEST | backend | initial version-controlled baseline` — backend
  placed under Git for the first time; pushed to `RobsBuddySystem/pariscomedy-backend`
  (private). `.gitignore` excludes secrets, SQLite DBs, venv, node_modules, logs,
  magic-link/notification outboxes.
- `2026-05-22 | docs | VCS workflow established` — CODE_MAP.md, CHANGELOG.md,
  verify_parity.sh added; dated commit standard adopted.
- `2026-05-22 | backend | Fix Gate features` — `/api/claimed-show-names`; real
  `has_upcoming` future-date join; Comic Plus post-payment publish
  (`comics.claimed`); recurrence instance auto-generation (`booker_shows.parent_id`);
  `DELETE /api/booker/venues/{id}`; `is_placeholder` in `/api/booker/comics`.
- `2026-05-22 | frontend | f8d229b` — booker dashboard visitor badge + venue delete UI.
- `2026-05-22 | frontend | 15e5c2a` — removed identity leaks (`Book Robert`),
  removed stand-up type chips, fixed French Fried claim-state, removed homepage
  stats strip.

## Earlier (pre-VCS baseline for backend)

History before 2026-05-22 is captured in `SESSION_LOG.md` in the project docs
directory. Frontend history is fully in `git log` of `RobsBuddySystem/pariscomedy.com`.

- 2026-05-22 — frontend commits `cb80a4d` unified sign-in, `4ce38c4` portal pages,
  `333d14e` confirm-modal + CORS, `400898c` localStorage key fix.
- 2026-05-21 — backend `members`/`payments`/`payment_events`, `/api/pricing-intent`.
- Affiliate/referral ticket integrations: **deferred — not implemented.**
