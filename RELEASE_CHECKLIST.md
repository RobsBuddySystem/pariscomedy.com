# Release Checklist — pariscomedy.com

Gate steps before pushing to production. Frontend deploys to GitHub Pages on push
to `main`; backend runs from the working tree, so an unclean tree = unreleased code.

## Before every push
- [ ] `scripts/dev-check.sh` passes
- [ ] Commit message follows standard: `YYYY-MM-DD HH:MM TZ | area | summary`
- [ ] No secrets/DB/env files staged (`git status`)
- [ ] `CHANGELOG.md` updated with a dated entry for this change

## Backend release (after pushing backend changes)
- [ ] Restart service: `launchctl kickstart -k gui/$(id -u)/com.pariscomedy.server`
- [ ] `curl -s https://api.pariscomedy.com/health` → `{"ok":true,...}`
- [ ] Working tree clean (running code == committed code)

## Frontend release
- [ ] `api-config.json` points to `https://api.pariscomedy.com` (not localhost)
- [ ] Pushed to `main` — GitHub Pages rebuilds automatically
- [ ] Spot-check the changed page on `https://pariscomedy.com`

## Verify parity
- [ ] `scripts/parity_check.sh` → `RESULT: PASS`

## Milestone (stable releases only)
- [ ] Tag: `git tag -a vYYYY.MM.DD-<label> -m "..."` then `git push origin <tag>`

## Standing rules
- Affiliate/referral ticket integrations remain **deferred** — do not implement.
- Never commit secrets. Never push to production with an unclean tree.
