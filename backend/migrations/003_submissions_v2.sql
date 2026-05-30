-- BACKEND.SUBMIT.1-SCAFFOLD migration — DRAFT (not auto-applied).
-- Adds show_submissions_v2 alongside any v1 submission state. Inert until
-- SUBMISSIONS_V2_ENABLED=true at runtime AND route wiring lands.
--
-- Apply manually:  sqlite3 data/paris.db < backend/migrations/003_submissions_v2.sql
-- Rollback:        sqlite3 data/paris.db < backend/migrations/003_submissions_v2.rollback.sql

CREATE TABLE IF NOT EXISTS show_submissions_v2 (
    id                      TEXT PRIMARY KEY,                  -- ULID/uuid hex
    submitter_name          TEXT,
    submitter_email         TEXT NOT NULL,
    submitter_role          TEXT,                               -- comic|booker|venue|fan|''
    show_name               TEXT NOT NULL,
    venue_name              TEXT NOT NULL,
    venue_address           TEXT,
    city                    TEXT,
    language                TEXT,                               -- EN|FR|MIX|''
    source_url              TEXT NOT NULL,
    ticket_url              TEXT,
    recurrence_text         TEXT,
    next_date_time          TEXT,
    notes                   TEXT,
    honeypot                TEXT,                               -- if non-empty -> spam
    spam_signals            TEXT,                               -- json-encoded list
    status                  TEXT NOT NULL DEFAULT 'received'
                                CHECK (status IN ('received','needs_review','approved','rejected','imported','duplicate','spam')),
    review_notes            TEXT,
    created_at              TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at              TEXT NOT NULL DEFAULT (datetime('now')),
    reviewed_at             TEXT,
    reviewed_by             TEXT,
    freshness_check_status  TEXT,
    duplicate_of            TEXT,                               -- submission_id of original
    ip                      TEXT,
    user_agent              TEXT
);
CREATE INDEX IF NOT EXISTS idx_subs_v2_status      ON show_submissions_v2(status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_subs_v2_email       ON show_submissions_v2(submitter_email, created_at);
CREATE INDEX IF NOT EXISTS idx_subs_v2_source_url  ON show_submissions_v2(source_url);
