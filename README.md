# pariscomedy.com — Frontend

Static site for [pariscomedy.com](https://pariscomedy.com), deployed via **GitHub
Pages** from this repo's `main` branch. No build step — plain HTML/CSS/JS.

Backend lives in a separate (private) repo: `RobsBuddySystem/pariscomedy-backend`.
See **[CODE_MAP.md](CODE_MAP.md)** for the whole-app layout.

## Fresh clone setup (< 5 minutes)

```sh
git clone https://github.com/RobsBuddySystem/pariscomedy.com.git
cd pariscomedy.com

# Install the commit-message hook (enforces the dated commit standard)
bash scripts/install-hooks.sh

# Serve locally (point api-config.json at a local backend if testing the API)
python3 -m http.server 8766
```

## Commit message standard (enforced)

```
YYYY-MM-DD HH:MM TZ | area | summary
```

`area` = `frontend | backend | data | infra | docs`. Enforced locally by the
`commit-msg` hook (`scripts/install-hooks.sh`) and remotely by the
`commit-msg-check` GitHub Action.

## Deployment
- Push to `main` → GitHub Pages rebuilds automatically.
- Custom domain via `CNAME` → `pariscomedy.com`.
- API endpoint is read from `api-config.json` (`https://api.pariscomedy.com`).

## Common commands

| Task | Command |
|------|---------|
| Pre-commit checks | `scripts/dev-check.sh` |
| Install git hooks | `scripts/install-hooks.sh` |

## Repo docs
- [CODE_MAP.md](CODE_MAP.md) — exact paths for the whole app
- [CHANGELOG.md](CHANGELOG.md) — dated change history
- [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md) — push-to-production gate

Affiliate/referral ticket integrations are **deferred** and intentionally not implemented.
