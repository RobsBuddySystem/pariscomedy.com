# pariscomedy.com — Code Map

Single source-of-truth index for the whole application. Last updated: 2026-05-22.

The app is split across **two Git repositories** (the frontend must be its own
repo because GitHub Pages serves from the repo root).

---

## Repositories

| Part | GitHub repo | Local working copy | Visibility |
|------|-------------|--------------------|------------|
| Frontend | `RobsBuddySystem/pariscomedy.com` | `~/pariscomedy-push-20260517-194848/` | public (GitHub Pages) |
| Backend | `RobsBuddySystem/pariscomedy-backend` | `~/.openclaw/workspace/apps/paris-comedy/` | private |

---

## Exact paths

### Frontend source
- Working copy: `~/pariscomedy-push-20260517-194848/`
- Pages (HTML/CSS/JS): `index.html`, `shows.html`, `comedians.html`, `venues.html`,
  `bookers.html`, `book.html`, `pricing.html`, `about.html`, `login.html`,
  `performer-portal.html`, `booker-portal.html`, `booker-dashboard.html`,
  `admin-payments.html`, `admin-messages.html`, `admin-submit.html`, `auth/verify.html`
- API endpoint config: `api-config.json` → `{"api":"https://api.pariscomedy.com"}`
- Shared JS: `js/`

### Backend source
- Working copy: `~/.openclaw/workspace/apps/paris-comedy/`
- App: `main.py` (FastAPI monolith)
- Launcher: `run.sh`
- Env template: `.env.example` (real `.env` is git-ignored)
- Scripts: `scripts/` (freshness worker, scrapers, importers, migrations)

### Runtime database (NOT in version control — user data)
- `~/.openclaw/workspace/apps/paris-comedy/data/paris.db` (SQLite)
- Leads: `~/.openclaw/workspace/apps/paris-comedy/data/leads.jsonl`
- Excluded by `.gitignore` on purpose. Back this up separately (see Risks).

### Deployment / publish paths
- Frontend: GitHub Pages, auto-published from `RobsBuddySystem/pariscomedy.com`
  branch `main`. Custom domain via `CNAME` → `pariscomedy.com`.
- Backend: launchd service `com.pariscomedy.server` runs uvicorn on `:8765`.
  Exposed publicly as `https://api.pariscomedy.com` via Cloudflare tunnel
  (`com.chuck.cloudflared-paris`).

### Refresh / audit scripts
- Daily refresh: `~/Documents/Claude/Projects/pariscomedy.com/refresh_pariscomedy.py`
- Audit scripts: `~/Documents/Claude/Projects/pariscomedy.com/audit_*.py`
- Backend pipeline scripts: `~/.openclaw/workspace/apps/paris-comedy/scripts/`
- Project docs / audit reports (local, not in VCS):
  `~/Documents/Claude/Projects/pariscomedy.com/` (PROJECT_CANON.md, SESSION_LOG.md,
  AUDIT_AND_GAP_REPORT.md, PROJECT_STATUS.md)

---

## How to download the full codebase

Both repos, fresh clone:

```sh
git clone https://github.com/RobsBuddySystem/pariscomedy.com.git
git clone https://github.com/RobsBuddySystem/pariscomedy-backend.git
```

Snapshot archive without git history (point-in-time download):

```sh
gh repo archive RobsBuddySystem/pariscomedy.com   --output frontend.zip
gh repo archive RobsBuddySystem/pariscomedy-backend --output backend.zip
# or, from inside a clone:
git archive --format=zip --output ../pariscomedy-frontend.zip HEAD
```

View dated history of any file:

```sh
git log --follow --date=iso -- <path>
```

---

## Risks / open items
- The runtime SQLite DB (`data/paris.db`) and `leads.jsonl` are intentionally
  NOT in git (user data + privacy). They have no off-machine backup in VCS —
  schedule a separate encrypted backup.
- The app admin secret appears in plaintext in several local project docs —
  rotate it and keep the new value only in the backend `.env` (never in any doc).
