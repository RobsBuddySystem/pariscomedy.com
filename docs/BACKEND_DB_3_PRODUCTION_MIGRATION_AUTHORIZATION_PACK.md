# BACKEND.DB.3 — Production DB Migration Authorization Pack

**For: Robert (operator)**  
**Status: AWAITING ROBERT AUTHORIZATION**  
**Scope: Approval docs only. No migration executed.**

---

## Plain-English Summary for Robert

### What migrations 002–007 add

These migrations add **17 new tables** to your production SQLite database.
Each table corresponds to a V2 backend system that is currently disabled:

| Migration | Tables added |
|---|---|
| 002_auth_v2 | users_v2, sessions_v2, magic_links_v2, audit_events_v2, rate_limits_v2 |
| 003_submissions_v2 | show_submissions_v2 |
| 004_claims_v2 | claims_v2 |
| 005_payments_v2 | payment_customers_v2, payment_subscriptions_v2, payment_invoices_v2, payment_checkout_sessions_v2, payment_webhook_idempotency_v2 |
| 006_messaging_v2 | message_threads_v2, messages_v2, message_blocks_v2, message_reports_v2 |
| 007_tickets_v2 | adapter_discoveries_v2 |

### What they do NOT do

- **No existing data is changed.** Your 119 shows, 45 venues, 275 comics, 179 listings, and all other rows remain exactly as they are.
- **No feature is turned on.** All feature flags remain false. Running migrations alone does nothing visible to users.
- **No email is sent.** `EMAIL_SEND_REAL=false` unchanged.
- **No login changes.** `AUTH_V2_ENABLED=false` unchanged. Legacy login continues to work.
- **No payments.** `PAYMENTS_ENABLED=false` unchanged.
- **No public submissions, claims, messaging, or imports.**

### Why migrations alone don't turn on features

Each backend system has a feature flag that defaults to `false`. The V2 routes return
503 when the flag is off. Running migrations only adds empty tables — nothing reads or
writes them until a flag is explicitly enabled in a separate step that requires another
ChatGPT authorization.

### What risks remain

- **If you interrupt the migration halfway**, a partial state could occur. This is
  extremely unlikely with SQLite (atomic transactions), but a backup beforehand is the
  correct safety net.
- **Rollback drops V2 data.** If you later run rollback scripts, any V2 rows written
  after enablement would be lost. This only matters after a feature is turned on.

---

## Production DB Confirmation

```
Production DB path: ${DB_PATH:-data/paris.db}
  → Confirm actual path on your server before running.
  → Default convention: /var/www/pariscomedy/data/paris.db or $DB_PATH env var.
  → BLOCKED_NEEDS_OPERATOR_CONFIRMATION until you confirm the exact server path.

Backup path convention:
  ${DB_PATH}.backup-$(date -u +%Y%m%dT%H%M%SZ)

Maintenance window recommendation:
  Run during off-peak hours (e.g. 04:00–06:00 CET). Expected duration: < 10 seconds.

Who must approve: Robert only.
```

---

## Pre-Execution Checklist

Before running any migration on production:

- [ ] Confirm exact DB path: `echo $DB_PATH` on the server
- [ ] Stop or put backend in maintenance mode (optional but safer)
- [ ] Create backup: `cp "$DB_PATH" "$DB_PATH.backup-$(date -u +%Y%m%dT%H%M%SZ)"`
- [ ] Verify backup opens: `sqlite3 backup-file.db ".tables"`
- [ ] Capture checksum: `md5sum $DB_PATH` (or `md5 $DB_PATH` on Mac)
- [ ] Capture current row counts for: shows, venues, comics, show_listings
- [ ] Confirm all feature flags false: check `.env` or environment variables
- [ ] Confirm rollback files exist: `ls backend/migrations/*.rollback.sql`

---

## Execution Command Block

```bash
# Set path — confirm this matches your actual production DB
DB_PATH="${DB_PATH:-data/paris.db}"
MIGRATIONS_DIR="backend/migrations"

# Create backup first
cp "$DB_PATH" "$DB_PATH.backup-$(date -u +%Y%m%dT%H%M%SZ)"

# Apply migrations in order
set -e
sqlite3 "$DB_PATH" < "$MIGRATIONS_DIR/002_auth_v2.sql"
sqlite3 "$DB_PATH" < "$MIGRATIONS_DIR/003_submissions_v2.sql"
sqlite3 "$DB_PATH" < "$MIGRATIONS_DIR/004_claims_v2.sql"
sqlite3 "$DB_PATH" < "$MIGRATIONS_DIR/005_payments_v2.sql"
sqlite3 "$DB_PATH" < "$MIGRATIONS_DIR/006_messaging_v2.sql"
sqlite3 "$DB_PATH" < "$MIGRATIONS_DIR/007_tickets_v2.sql"
echo "All migrations applied."
```

**DO NOT add any feature flag enable commands to this block.**

---

## Verification Command Block

After running migrations:

```bash
# Verify V2 tables present (expect 17)
sqlite3 "$DB_PATH" "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%_v2' ORDER BY name;"

# Verify existing data preserved
sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM shows;"      # expect 119
sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM venues;"     # expect 45
sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM comics;"     # expect 275
sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM show_listings;" # expect 179

# Verify backend health
curl https://api.pariscomedy.com/health

# Verify all V2 features still disabled
curl https://api.pariscomedy.com/api/auth_v2/status
curl https://api.pariscomedy.com/api/submissions_v2/status
curl https://api.pariscomedy.com/api/claims_v2/status
curl https://api.pariscomedy.com/api/payments_v2/status
curl https://api.pariscomedy.com/api/messaging_v2/status
curl https://api.pariscomedy.com/api/tickets_v2/status
# All above should return {"enabled": false, ...} or 503
```

---

## Rollback Command Block

**Preferred rollback: restore from backup**

```bash
# Restore from backup (preferred — instant, no data loss)
cp "$DB_PATH.backup-TIMESTAMP" "$DB_PATH"
```

**Secondary rollback: run rollback SQL (use only if backup unavailable)**

```bash
# Warning: this drops all V2 data written since migration
set -e
sqlite3 "$DB_PATH" < "$MIGRATIONS_DIR/007_tickets_v2.rollback.sql"
sqlite3 "$DB_PATH" < "$MIGRATIONS_DIR/006_messaging_v2.rollback.sql"
sqlite3 "$DB_PATH" < "$MIGRATIONS_DIR/005_payments_v2.rollback.sql"
sqlite3 "$DB_PATH" < "$MIGRATIONS_DIR/004_claims_v2.rollback.sql"
sqlite3 "$DB_PATH" < "$MIGRATIONS_DIR/003_submissions_v2.rollback.sql"
sqlite3 "$DB_PATH" < "$MIGRATIONS_DIR/002_auth_v2.rollback.sql"
```

---

## Go / No-Go Decision

| Action | Authorized by this pack? |
|---|---|
| Run DB migrations 002–007 | **YES — after Robert types approval text below** |
| Enable any feature flag | **NO** |
| Send real email | **NO** |
| Switch login.html to Auth V2 | **NO** |
| Enable public submissions/claims/payments/messaging/imports | **NO** |

---

## Robert Approval Text

When you are ready to authorize production migration execution, type exactly:

> **"I authorize production DB migration 002–007 only, with backup first, no feature flags enabled."**

This statement will be recorded as the operator authorization before execution.
Do not type this until you have:
- Confirmed the exact production DB path
- Scheduled a maintenance window
- Ensured a backup strategy is in place
