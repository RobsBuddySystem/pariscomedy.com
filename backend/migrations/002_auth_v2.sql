-- BACKEND.AUTH.1-SCAFFOLD migration — DRAFT (not auto-applied).
--
-- Adds v2 auth tables alongside the legacy booker_sessions. Live booker
-- auth (POST /api/booker/auth) is unchanged. New tables are inert until
-- AUTH_V2_ENABLED=true at runtime AND code-level cutover lands.
--
-- Apply manually:  sqlite3 data/paris.db < backend/migrations/002_auth_v2.sql
-- Rollback:        sqlite3 data/paris.db < backend/migrations/002_auth_v2.rollback.sql

CREATE TABLE IF NOT EXISTS users_v2 (
    id            TEXT PRIMARY KEY,                  -- ULID
    email         TEXT NOT NULL UNIQUE,
    email_lower   TEXT NOT NULL UNIQUE,
    password_hash TEXT,                                -- nullable; only admin uses this
    role          TEXT NOT NULL CHECK (role IN ('user','comic','booker','admin')),
    plan          TEXT NOT NULL DEFAULT 'free' CHECK (plan IN ('free','comic_plus','booker_plus')),
    created_at    TEXT NOT NULL DEFAULT (datetime('now')),
    last_login_at TEXT,
    deleted_at    TEXT
);
CREATE INDEX IF NOT EXISTS idx_users_v2_email_lower ON users_v2(email_lower);

CREATE TABLE IF NOT EXISTS sessions_v2 (
    id            TEXT PRIMARY KEY,                  -- session token (cookie value)
    user_id       TEXT NOT NULL REFERENCES users_v2(id) ON DELETE CASCADE,
    created_at    TEXT NOT NULL DEFAULT (datetime('now')),
    last_seen_at  TEXT NOT NULL DEFAULT (datetime('now')),
    expires_at    TEXT NOT NULL,
    revoked_at    TEXT,
    ip            TEXT,
    user_agent    TEXT
);
CREATE INDEX IF NOT EXISTS idx_sessions_v2_user_active
    ON sessions_v2(user_id) WHERE revoked_at IS NULL;

CREATE TABLE IF NOT EXISTS magic_links_v2 (
    token_hash    TEXT PRIMARY KEY,                  -- SHA-256 hex of raw token
    email_lower   TEXT NOT NULL,
    role          TEXT NOT NULL,
    created_at    TEXT NOT NULL DEFAULT (datetime('now')),
    expires_at    TEXT NOT NULL,
    consumed_at   TEXT,
    ip            TEXT
);
CREATE INDEX IF NOT EXISTS idx_magic_links_v2_email
    ON magic_links_v2(email_lower, created_at);

CREATE TABLE IF NOT EXISTS audit_events_v2 (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       TEXT REFERENCES users_v2(id) ON DELETE SET NULL,
    actor_role    TEXT NOT NULL,                      -- 'user' | 'admin' | 'system'
    action        TEXT NOT NULL,
    target_type   TEXT,
    target_id     TEXT,
    metadata_json TEXT,
    created_at    TEXT NOT NULL DEFAULT (datetime('now')),
    ip            TEXT
);
CREATE INDEX IF NOT EXISTS idx_audit_v2_created
    ON audit_events_v2(created_at DESC);

CREATE TABLE IF NOT EXISTS rate_limits_v2 (
    bucket        TEXT NOT NULL,                      -- e.g. 'auth.magic_link.email'
    key           TEXT NOT NULL,
    window_start  TEXT NOT NULL,
    count         INTEGER NOT NULL,
    PRIMARY KEY (bucket, key, window_start)
);
