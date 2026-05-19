# ParisComedy Backend

FastAPI app powering the Booker Dashboard, messaging, and admin review queue.

## Quick start (Mac Studio)

```bash
cd backend
cp env.example env   # then edit env to set ADMIN_TOKEN + SMTP_USER/PASS
./scripts/run.sh
```

Default: listens on `127.0.0.1:8765`. Expose via Cloudflare tunnel (`cloudflared tunnel run …`) and update `_repo/api-config.json` to point to the public URL.

## Environment variables

| Var | Default | Purpose |
|---|---|---|
| `DB_PATH` | `../data/paris.db` | SQLite database path |
| `COMICS_JSON` | `../data/comedians.json` | Public comic directory |
| `ADMIN_TOKEN` | *(unset)* | Required for `/api/admin/*` — generate `openssl rand -hex 16` |
| `NOTIFY_EMAIL` | `chucklericain@gmail.com` | Admin notification recipient |
| `SMTP_HOST` / `SMTP_PORT` | `smtp.gmail.com` / `587` | SMTP server |
| `SMTP_USER` / `SMTP_PASS` | *(unset)* | Gmail address + app password |
| `CORS_ORIGIN` | `*` | Set to `https://pariscomedy.com` in prod |
| `PORT` / `HOST` | `8765` / `127.0.0.1` | Listen address |

## Endpoints

- `GET  /api/health` — health check (DB + SMTP + config flags)
- `POST /api/message` — public contact form (honeypot + rate limit)
- `POST /api/booker/auth` — email → token (delivered by email or returned for dev)
- `GET  /api/booker/comics` — directory (no private emails exposed)
- `GET/POST /api/booker/shows` — list / create shows
- `POST /api/booker/lineup` — add comic to lineup
- `DELETE /api/booker/lineup/{id}` — remove
- `POST /api/booker/lineup/{id}/status` — invited|booked|declined|confirmed
- `POST /api/booker/notify` — queue invites for admin review
- `GET  /api/admin/messages?token=…` — admin review queue
- `POST /api/admin/messages/{id}/status` — approve/reject

## Schema

See `migrations/001_init.sql`. Tables: `messages_review_queue`, `booker_sessions`, `booker_shows`, `booker_lineup`. All `CREATE TABLE IF NOT EXISTS` — re-running is safe.

## Backup

```bash
./scripts/backup_db.sh
```

Writes gzipped snapshot to `backend/backups/paris-YYYYMMDD_HHMMSS.db.gz`. Last 30 days kept; older rolled off. Schedule via launchd or cron (daily, 03:00).

## launchd plist (Mac Studio production)

Create `~/Library/LaunchAgents/com.pariscomedy.server.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.pariscomedy.server</string>
  <key>WorkingDirectory</key><string>/Users/chuck/Documents/Claude/Projects/pariscomedy.com/_repo/backend</string>
  <key>ProgramArguments</key>
  <array><string>/bin/bash</string><string>scripts/run.sh</string></array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>StandardOutPath</key><string>/tmp/pariscomedy-backend.log</string>
  <key>StandardErrorPath</key><string>/tmp/pariscomedy-backend.err</string>
</dict></plist>
```

Then: `launchctl load ~/Library/LaunchAgents/com.pariscomedy.server.plist`

## Privacy

Comic private emails are stored only in upstream `comedians.json` source records and are **never** returned by `/api/booker/comics`. The `messages_review_queue` table holds sender emails but those rows are admin-only via `ADMIN_TOKEN`.
