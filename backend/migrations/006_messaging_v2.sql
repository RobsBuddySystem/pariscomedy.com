-- 006_messaging_v2.sql
-- Comic↔Booker messaging scaffold. NOT auto-applied.

CREATE TABLE IF NOT EXISTS message_threads_v2 (
    thread_id          TEXT PRIMARY KEY,
    participant_a_user_id TEXT NOT NULL,
    participant_b_user_id TEXT NOT NULL,
    participant_a_role TEXT NOT NULL CHECK (participant_a_role IN ('comic','booker','admin')),
    participant_b_role TEXT NOT NULL CHECK (participant_b_role IN ('comic','booker','admin')),
    subject            TEXT NOT NULL DEFAULT '',
    status             TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active','blocked','reported','archived')),
    created_at         TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
    updated_at         TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
    last_message_at    TEXT
);

CREATE INDEX IF NOT EXISTS idx_threads_participant_a ON message_threads_v2 (participant_a_user_id);
CREATE INDEX IF NOT EXISTS idx_threads_participant_b ON message_threads_v2 (participant_b_user_id);

CREATE TABLE IF NOT EXISTS messages_v2 (
    message_id   TEXT PRIMARY KEY,
    thread_id    TEXT NOT NULL REFERENCES message_threads_v2 (thread_id),
    sender_user_id    TEXT NOT NULL,
    recipient_user_id TEXT NOT NULL,
    body         TEXT NOT NULL,
    status       TEXT NOT NULL DEFAULT 'sent' CHECK (status IN ('sent','hidden','deleted','reported')),
    created_at   TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
    read_at      TEXT,
    hidden_at    TEXT,
    deleted_at   TEXT
);

CREATE INDEX IF NOT EXISTS idx_messages_thread ON messages_v2 (thread_id);

CREATE TABLE IF NOT EXISTS message_blocks_v2 (
    block_id        TEXT PRIMARY KEY,
    blocker_user_id TEXT NOT NULL,
    blocked_user_id TEXT NOT NULL,
    reason          TEXT,
    created_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
    UNIQUE (blocker_user_id, blocked_user_id)
);

CREATE TABLE IF NOT EXISTS message_reports_v2 (
    report_id        TEXT PRIMARY KEY,
    thread_id        TEXT NOT NULL REFERENCES message_threads_v2 (thread_id),
    reporter_user_id TEXT NOT NULL,
    reason           TEXT NOT NULL,
    created_at       TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
);
