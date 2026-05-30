# DB_SCHEMA_DRAFT — pariscomedy.com backend tables

**Status:** DRAFT. Engine-portable (Postgres / SQLite-Turso compatible). All FKs `ON DELETE CASCADE` unless noted. All timestamps `TIMESTAMPTZ` (Postgres) / ISO-8601 text (SQLite).

## Existing tables (read-only here; live today)

- `listings` — see `data/schema.json` and `/api/listings` response shape
- `venues` — joined into listings
- `comics` — comedian directory entries
- (others as deployed in api.pariscomedy.com today)

This draft adds the NEW tables for BACKEND.AUTH/SUBMIT/CLAIM/MESSAGING/PAYMENTS.

## Auth

```sql
CREATE TABLE users (
  id            TEXT PRIMARY KEY,                     -- ULID
  email         TEXT NOT NULL UNIQUE,
  email_lower   TEXT NOT NULL UNIQUE,                  -- case-insensitive uniqueness
  password_hash TEXT NULL,                              -- Argon2id; only set for admin
  role          TEXT NOT NULL CHECK (role IN ('user','comic','booker','admin')),
  plan          TEXT NOT NULL DEFAULT 'free' CHECK (plan IN ('free','comic_plus','booker_plus')),
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  last_login_at TIMESTAMPTZ NULL,
  deleted_at    TIMESTAMPTZ NULL                       -- soft delete; hard purge after 90d
);

CREATE TABLE sessions (
  id            TEXT PRIMARY KEY,                     -- session token (also cookie value, signed)
  user_id       TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  last_seen_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  expires_at    TIMESTAMPTZ NOT NULL,
  revoked_at    TIMESTAMPTZ NULL,
  ip            TEXT NULL,
  user_agent    TEXT NULL
);
CREATE INDEX sessions_user_active ON sessions(user_id) WHERE revoked_at IS NULL;

CREATE TABLE magic_links (
  token_hash    TEXT PRIMARY KEY,                     -- SHA-256 of the URL token (don't store raw)
  email_lower   TEXT NOT NULL,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  expires_at    TIMESTAMPTZ NOT NULL,
  consumed_at   TIMESTAMPTZ NULL,
  ip            TEXT NULL
);

CREATE TABLE audit_events (
  id            TEXT PRIMARY KEY,                     -- ULID
  user_id       TEXT NULL REFERENCES users(id) ON DELETE SET NULL,
  actor_role    TEXT NOT NULL,                         -- 'user' | 'admin' | 'system'
  action        TEXT NOT NULL,                         -- e.g. 'auth.login', 'submissions.approve'
  target_type   TEXT NULL,
  target_id     TEXT NULL,
  metadata_json TEXT NULL,                             -- JSON blob, free-form
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  ip            TEXT NULL
);
CREATE INDEX audit_events_created ON audit_events(created_at DESC);

CREATE TABLE rate_limits (
  bucket        TEXT NOT NULL,                         -- 'auth.magic_link', 'submissions.create', etc.
  key           TEXT NOT NULL,                         -- email_lower or IP
  window_start  TIMESTAMPTZ NOT NULL,
  count         INTEGER NOT NULL,
  PRIMARY KEY (bucket, key, window_start)
);
```

## Show submissions

```sql
CREATE TABLE show_submissions (
  id                TEXT PRIMARY KEY,                  -- ULID
  submitter_email   TEXT NOT NULL,
  proposed_name     TEXT NOT NULL,
  proposed_venue    TEXT NOT NULL,
  day_of_week       TEXT NOT NULL,
  start_time        TEXT NOT NULL,
  language          TEXT NOT NULL CHECK (language IN ('EN','FR','MIX')),
  source_url        TEXT NOT NULL,
  source_verifier_result_json TEXT NULL,               -- snapshot of inline verifier output
  status            TEXT NOT NULL CHECK (status IN ('pending','approved','rejected','spam','duplicate')),
  created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  reviewed_by       TEXT NULL REFERENCES users(id) ON DELETE SET NULL,
  reviewed_at       TIMESTAMPTZ NULL,
  reviewer_notes    TEXT NULL,
  resulting_listing_id TEXT NULL                       -- FK to listings.id once approved
);
CREATE INDEX show_submissions_status ON show_submissions(status, created_at DESC);
```

## Claims

```sql
CREATE TABLE claims (
  id              TEXT PRIMARY KEY,                    -- ULID
  claim_type      TEXT NOT NULL CHECK (claim_type IN ('comic','show_runner','venue')),
  user_id         TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  target_type     TEXT NOT NULL,                       -- 'comic_profile','listing','venue'
  target_id       TEXT NOT NULL,
  evidence_instagram TEXT NULL,
  evidence_recent_post_url TEXT NULL,
  evidence_domain_email TEXT NULL,
  evidence_freeform TEXT NULL,
  status          TEXT NOT NULL CHECK (status IN ('pending','approved','rejected')),
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  reviewed_by     TEXT NULL REFERENCES users(id) ON DELETE SET NULL,
  reviewed_at     TIMESTAMPTZ NULL,
  reviewer_notes  TEXT NULL,
  UNIQUE (claim_type, target_id, status) DEFERRABLE INITIALLY DEFERRED  -- prevent dup pending
);
CREATE INDEX claims_status ON claims(status, created_at DESC);
```

A successful approval ALSO writes back to the target's own table:
- `UPDATE comic_profiles SET claimed_by_user_id=? WHERE id=?` (or equivalent on listings/venues).

## Messaging

```sql
CREATE TABLE message_threads (
  id            TEXT PRIMARY KEY,                     -- ULID
  participant_a TEXT NOT NULL REFERENCES users(id),
  participant_b TEXT NOT NULL REFERENCES users(id),
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  closed_at     TIMESTAMPTZ NULL,
  UNIQUE (participant_a, participant_b),
  CHECK (participant_a < participant_b)               -- canonical ordering, dedupes threads
);

CREATE TABLE messages (
  id            TEXT PRIMARY KEY,                     -- ULID
  thread_id     TEXT NOT NULL REFERENCES message_threads(id) ON DELETE CASCADE,
  sender_id     TEXT NOT NULL REFERENCES users(id),
  body          TEXT NOT NULL,
  sent_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  read_at       TIMESTAMPTZ NULL,
  hidden_at     TIMESTAMPTZ NULL,                     -- soft-delete >90d
  deleted_at    TIMESTAMPTZ NULL                       -- hard-delete >24mo (RGPD)
);
CREATE INDEX messages_thread_sent ON messages(thread_id, sent_at);

CREATE TABLE message_blocks (
  blocker_id    TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  blocked_id    TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (blocker_id, blocked_id)
);

CREATE TABLE message_reports (
  id            TEXT PRIMARY KEY,
  thread_id     TEXT NOT NULL REFERENCES message_threads(id) ON DELETE CASCADE,
  reporter_id   TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  reason        TEXT NOT NULL,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  resolved_at   TIMESTAMPTZ NULL,
  resolved_by   TEXT NULL REFERENCES users(id) ON DELETE SET NULL
);
```

## Payments

```sql
CREATE TABLE stripe_customers (
  user_id           TEXT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  stripe_customer_id TEXT NOT NULL UNIQUE,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE subscriptions (
  id                 TEXT PRIMARY KEY,                -- our ULID
  stripe_subscription_id TEXT NOT NULL UNIQUE,
  user_id            TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  plan               TEXT NOT NULL CHECK (plan IN ('comic_plus','booker_plus')),
  status             TEXT NOT NULL,                    -- mirror Stripe status enum
  current_period_end TIMESTAMPTZ NOT NULL,
  created_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE invoices (
  id                TEXT PRIMARY KEY,
  stripe_invoice_id TEXT NOT NULL UNIQUE,
  user_id           TEXT NOT NULL REFERENCES users(id),
  amount_cents      INTEGER NOT NULL,
  currency          TEXT NOT NULL,
  status            TEXT NOT NULL,
  hosted_invoice_url TEXT NULL,
  pdf_url           TEXT NULL,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE webhook_events_idempotency (
  event_id    TEXT PRIMARY KEY,                       -- Stripe event.id
  received_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  source      TEXT NOT NULL                            -- 'stripe' | 'postmark' | ...
);
```

## Ticket adapters

```sql
CREATE TABLE adapter_discoveries (
  id              TEXT PRIMARY KEY,
  source_platform TEXT NOT NULL,                      -- 'eventbrite','billetreduc','fnac', ...
  source_url      TEXT NOT NULL,
  parsed_name     TEXT NULL,
  parsed_venue    TEXT NULL,
  parsed_day      TEXT NULL,
  parsed_start_time TEXT NULL,
  parsed_language TEXT NULL,
  raw_json        TEXT NULL,
  status          TEXT NOT NULL CHECK (status IN ('discovered','imported','rejected','duplicate')),
  resulting_listing_id TEXT NULL,
  discovered_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  reviewed_at     TIMESTAMPTZ NULL,
  reviewed_by     TEXT NULL REFERENCES users(id) ON DELETE SET NULL,
  reviewer_notes  TEXT NULL
);
CREATE INDEX adapter_discoveries_status ON adapter_discoveries(status, discovered_at DESC);

CREATE TABLE adapter_affiliate_ids (
  platform        TEXT PRIMARY KEY,                   -- 'billetreduc','fnac', ...
  affiliate_id    TEXT NULL,                           -- null until approved
  enabled         BOOLEAN NOT NULL DEFAULT FALSE,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  enabled_at      TIMESTAMPTZ NULL,
  reviewer_notes  TEXT NULL
);
```

## Indexes summary

- All `*_status` indexes are partial where helpful.
- `users(email_lower)`, `sessions(user_id WHERE revoked_at IS NULL)`, `magic_links(email_lower, created_at)`.
- `messages(thread_id, sent_at)` for thread paginating.

## Migration order

1. users + sessions + magic_links + audit_events + rate_limits
2. show_submissions
3. claims
4. message_threads + messages + message_blocks + message_reports
5. stripe_customers + subscriptions + invoices + webhook_events_idempotency
6. adapter_discoveries + adapter_affiliate_ids

Each migration ships as a single forward-only `.sql` file with a rollback note.

## Related
- [[BACKEND_PLAN_1]]
- [[API_CONTRACT_DRAFT]]
- [[BACKEND_RISK_REGISTER]]
- [[BACKEND_IMPLEMENTATION_SEQUENCE]]
