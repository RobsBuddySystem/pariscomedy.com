# BACKEND.DB.1-MIGRATION-RUNBOOK

**Status: IN_GIT_UNVERIFIED**
**Scope: Operator runbook only. NO production migration executed. No feature flags enabled.**

---

## ⚠️ OPERATOR APPROVAL GATE

Robert must explicitly approve before running any production migration.
ChatGPT must verify this runbook before any execution phase.
**Running migrations before approval = BLOCKED.**

---

## Current production DB location

Default path (from `backend/main.py`):
```
backend/../data/paris.db
→ absolute: /path/to/pariscomedy/data/paris.db
```

The `DB_PATH` env var overrides this. If running on a server (Render, Railway, Fly.io, VPS):
- Check the deployment environment for `DB_PATH`
- If unknown: **BLOCKED_NEEDS_OPERATOR_CONFIRMATION** — Robert must confirm exact DB path before proceeding

---

## Migrations to apply

| Order | File | System | Tables created |
|---|---|---|---|
| 1 | `002_auth_v2.sql` | Auth V2 | `auth_tokens_v2`, `rate_limits_v2`, `audit_events_v2` |
| 2 | `003_claims_v2.sql` | Claims V2 | `claim_requests_v2` |
| 3 | `004_submissions_v2.sql` | Submissions V2 | `submissions_v2` |
| 4 | `005_payments_v2.sql` | Payments V2 | `payment_checkout_sessions_v2`, `payment_subscriptions_v2`, `payment_webhook_events_v2`, `payment_feature_unlocks_v2`, `payment_products_v2` |
| 5 | `006_messaging_v2.sql` | Messaging V2 | `message_threads_v2`, `messages_v2`, `message_blocks_v2`, `message_reports_v2` |
| 6 | `007_tickets_v2.sql` | Tickets V2 | `adapter_discoveries_v2` |

---

## Step 1 — Pre-flight checks

```bash
# 1. Confirm DB path
echo $DB_PATH    # or use default: data/paris.db

# 2. Disk space check
df -h $(dirname $DB_PATH)

# 3. Current table count
sqlite3 $DB_PATH ".tables"

# 4. Row counts for critical existing tables (do not lose these)
sqlite3 $DB_PATH "SELECT 'shows' as t, COUNT(*) FROM shows UNION
                  SELECT 'venues', COUNT(*) FROM venues UNION
                  SELECT 'comedians', COUNT(*) FROM comedians;"

# 5. App health check before migration
curl -s http://localhost:8000/api/health | python3 -m json.tool
```

---

## Step 2 — Backup plan

```bash
# Backup filename convention: paris.db.backup-YYYYMMDDTHHMMSSZ
BACKUP_PATH="${DB_PATH}.backup-$(date -u +%Y%m%dT%H%M%SZ)"

# Create backup
cp "$DB_PATH" "$BACKUP_PATH"

# Verify backup exists and can be opened
ls -lh "$BACKUP_PATH"
sqlite3 "$BACKUP_PATH" "SELECT COUNT(*) FROM shows;"

# Checksum
sha256sum "$BACKUP_PATH"
```

---

## Step 3 — Apply migrations (in order)

```bash
set -e   # stop on any error

sqlite3 "$DB_PATH" < backend/migrations/002_auth_v2.sql
echo "002 applied"

sqlite3 "$DB_PATH" < backend/migrations/003_claims_v2.sql
echo "003 applied"

sqlite3 "$DB_PATH" < backend/migrations/004_submissions_v2.sql
echo "004 applied"

sqlite3 "$DB_PATH" < backend/migrations/005_payments_v2.sql
echo "005 applied"

sqlite3 "$DB_PATH" < backend/migrations/006_messaging_v2.sql
echo "006 applied"

sqlite3 "$DB_PATH" < backend/migrations/007_tickets_v2.sql
echo "007 applied"
```

All migration files use `CREATE TABLE IF NOT EXISTS` — safe to re-run if partially applied.

---

## Step 4 — Verification after migration

```bash
# Tables that must now exist
sqlite3 "$DB_PATH" ".tables" | tr ' ' '\n' | sort

# Required new tables (one per line)
for t in auth_tokens_v2 rate_limits_v2 audit_events_v2 \
          claim_requests_v2 submissions_v2 \
          payment_checkout_sessions_v2 payment_subscriptions_v2 \
          payment_webhook_events_v2 payment_feature_unlocks_v2 payment_products_v2 \
          message_threads_v2 messages_v2 message_blocks_v2 message_reports_v2 \
          adapter_discoveries_v2; do
  COUNT=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM $t;")
  echo "$t: $COUNT rows"
done

# Existing tables must still have same row counts as pre-flight
sqlite3 "$DB_PATH" "SELECT 'shows' as t, COUNT(*) FROM shows UNION
                    SELECT 'venues', COUNT(*) FROM venues UNION
                    SELECT 'comedians', COUNT(*) FROM comedians;"

# App health check after migration
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

Expected: each returns `{"enabled": false, ...}` — feature flags unchanged.

---

## Rollback plan

⚠️ **Rollback drops all v2 tables and their data. Do not rollback after production data has been written.**

```bash
# Rollback order: reverse of apply order
sqlite3 "$DB_PATH" < backend/migrations/007_tickets_v2.rollback.sql
sqlite3 "$DB_PATH" < backend/migrations/006_messaging_v2.rollback.sql  # if exists
sqlite3 "$DB_PATH" < backend/migrations/005_payments_v2.rollback.sql   # if exists
sqlite3 "$DB_PATH" < backend/migrations/004_submissions_v2.rollback.sql # if exists
sqlite3 "$DB_PATH" < backend/migrations/003_claims_v2.rollback.sql      # if exists
sqlite3 "$DB_PATH" < backend/migrations/002_auth_v2.rollback.sql        # if exists
```

Or restore from backup (safer):
```bash
cp "$BACKUP_PATH" "$DB_PATH"
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
