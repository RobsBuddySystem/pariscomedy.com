# BACKEND.DB.1-MIGRATION-RUNBOOK

**Status: IN_GIT_UNVERIFIED**
**Scope: Operator runbook only. NO production migration executed. No feature flags enabled.**

> ⚠️ GUARD NOTE: Never apply a migration based on phase memory.
> Verify actual `backend/migrations/` filenames and `CREATE TABLE` statements first.

---

## ⚠️ OPERATOR APPROVAL GATE

Robert must explicitly approve before running any production migration.
ChatGPT must verify this runbook before any execution phase.
**Running migrations before approval = BLOCKED.**

---

## Current production DB location

Default path (from `backend/main.py`):
```
data/paris.db  (relative to repo root)
```

`DB_PATH` env var overrides this. If running on a server (Render, Railway, Fly.io, VPS):
- Check deployment environment for `DB_PATH`
- If unknown: **BLOCKED_NEEDS_OPERATOR_CONFIRMATION** — Robert must confirm exact DB path

---

## Actual migration files (from `backend/migrations/`)

```
001_init.sql                    — original schema (legacy tables)
002_auth_v2.sql                 — Auth V2
002_auth_v2.rollback.sql
003_submissions_v2.sql          — Submissions V2
003_submissions_v2.rollback.sql
004_claims_v2.sql               — Claims V2
004_claims_v2.rollback.sql
005_payments_v2.sql             — Payments V2
005_payments_v2.rollback.sql
006_messaging_v2.sql            — Messaging V2
006_messaging_v2.rollback.sql
007_tickets_v2.sql              — Tickets V2
007_tickets_v2.rollback.sql
```

---

## Migrations to apply (in order)

| Order | File | System | Tables created |
|---|---|---|---|
| 1 | `002_auth_v2.sql` | Auth V2 | `users_v2`, `sessions_v2`, `magic_links_v2`, `audit_events_v2`, `rate_limits_v2` |
| 2 | `003_submissions_v2.sql` | Submissions V2 | `show_submissions_v2` |
| 3 | `004_claims_v2.sql` | Claims V2 | `claims_v2` |
| 4 | `005_payments_v2.sql` | Payments V2 | `payment_customers_v2`, `payment_subscriptions_v2`, `payment_invoices_v2`, `payment_checkout_sessions_v2`, `payment_webhook_idempotency_v2` |
| 5 | `006_messaging_v2.sql` | Messaging V2 | `message_threads_v2`, `messages_v2`, `message_blocks_v2`, `message_reports_v2` |
| 6 | `007_tickets_v2.sql` | Tickets V2 | `adapter_discoveries_v2` |

---

## Step 1 — Pre-flight checks

```bash
# 1. Confirm DB path
echo "${DB_PATH:-data/paris.db}"

# 2. Disk space check
df -h "$(dirname "${DB_PATH:-data/paris.db}")"

# 3. Current table list
sqlite3 "${DB_PATH:-data/paris.db}" ".tables"

# 4. Row counts for critical existing tables (must not change after migration)
sqlite3 "${DB_PATH:-data/paris.db}" "
SELECT 'shows' as t, COUNT(*) FROM shows
UNION SELECT 'venues', COUNT(*) FROM venues
UNION SELECT 'comedians', COUNT(*) FROM comedians;"

# 5. App health check
curl -s http://localhost:8000/api/health | python3 -m json.tool
```

---

## Step 2 — Backup plan

```bash
DB="${DB_PATH:-data/paris.db}"
BACKUP_PATH="${DB}.backup-$(date -u +%Y%m%dT%H%M%SZ)"

cp "$DB" "$BACKUP_PATH"
ls -lh "$BACKUP_PATH"
sqlite3 "$BACKUP_PATH" "SELECT COUNT(*) FROM shows;"
sha256sum "$BACKUP_PATH"
```

---

## Step 3 — Apply migrations (in order, stop on error)

```bash
DB="${DB_PATH:-data/paris.db}"
set -e

sqlite3 "$DB" < backend/migrations/002_auth_v2.sql && echo "002 applied"
sqlite3 "$DB" < backend/migrations/003_submissions_v2.sql && echo "003 applied"
sqlite3 "$DB" < backend/migrations/004_claims_v2.sql && echo "004 applied"
sqlite3 "$DB" < backend/migrations/005_payments_v2.sql && echo "005 applied"
sqlite3 "$DB" < backend/migrations/006_messaging_v2.sql && echo "006 applied"
sqlite3 "$DB" < backend/migrations/007_tickets_v2.sql && echo "007 applied"
```

All files use `CREATE TABLE IF NOT EXISTS` — safe to re-run if partially applied.

---

## Step 4 — Post-migration verification

```bash
DB="${DB_PATH:-data/paris.db}"

# Check each new table exists
for t in users_v2 sessions_v2 magic_links_v2 audit_events_v2 rate_limits_v2 \
          show_submissions_v2 claims_v2 \
          payment_customers_v2 payment_subscriptions_v2 payment_invoices_v2 \
          payment_checkout_sessions_v2 payment_webhook_idempotency_v2 \
          message_threads_v2 messages_v2 message_blocks_v2 message_reports_v2 \
          adapter_discoveries_v2; do
  COUNT=$(sqlite3 "$DB" "SELECT COUNT(*) FROM $t;")
  echo "$t: $COUNT rows"
done

# Existing tables unchanged
sqlite3 "$DB" "
SELECT 'shows' as t, COUNT(*) FROM shows
UNION SELECT 'venues', COUNT(*) FROM venues
UNION SELECT 'comedians', COUNT(*) FROM comedians;"

curl -s http://localhost:8000/api/health | python3 -m json.tool
```

---

## Step 5 — Smoke tests (all should report enabled=false)

```bash
for endpoint in auth_v2 submissions_v2 claims_v2 payments_v2 messaging_v2 tickets_v2; do
  echo "=== /api/$endpoint/status ==="
  curl -s "http://localhost:8000/api/$endpoint/status" | python3 -m json.tool
done
```

Expected: each returns `{"enabled": false, ...}`.

---

## Rollback plan

⚠️ Rollback drops all v2 tables and their data. Do not rollback after production data has been written.

Safest: restore from backup:
```bash
cp "$BACKUP_PATH" "$DB"
```

Or reverse-order rollback files (007 → 006 → 005 → 004 → 003 → 002):
```bash
sqlite3 "$DB" < backend/migrations/007_tickets_v2.rollback.sql
sqlite3 "$DB" < backend/migrations/006_messaging_v2.rollback.sql
sqlite3 "$DB" < backend/migrations/005_payments_v2.rollback.sql
sqlite3 "$DB" < backend/migrations/004_claims_v2.rollback.sql
sqlite3 "$DB" < backend/migrations/003_submissions_v2.rollback.sql
sqlite3 "$DB" < backend/migrations/002_auth_v2.rollback.sql
```

---

## Feature flag safety

Applying these migrations **does NOT enable any feature**.
After migration:
- `AUTH_V2_ENABLED` remains `false`
- `SUBMISSIONS_V2_ENABLED` remains `false`
- `CLAIMS_V2_ENABLED` remains `false`
- `PAYMENTS_ENABLED` remains `false`
- `MESSAGING_V2_ENABLED` remains `false`
- `TICKETS_ADAPTERS_ENABLED` remains `false`

Each feature requires a separate explicit enablement phase after migration.

---

## Machine-readable runbook

`data/backend-db-migration-runbook.json`
