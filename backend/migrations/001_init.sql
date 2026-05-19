-- ParisComedy backend schema — v1
-- Idempotent: safe to run on each startup.

CREATE TABLE IF NOT EXISTS messages_review_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_name    TEXT NOT NULL,
    sender_email   TEXT NOT NULL,
    sender_type    TEXT NOT NULL,        -- comic|booker|venue|fan
    recipient_type TEXT NOT NULL,        -- booker|comic|venue
    recipient_id   TEXT,                 -- slug or show id (no email)
    subject        TEXT,
    message        TEXT NOT NULL,
    source_page    TEXT,
    client_ip      TEXT,
    status         TEXT NOT NULL DEFAULT 'pending_review',
                                         -- pending_review|approved|rejected|delivered|booker_invite_pending
    created_at     TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_msg_status   ON messages_review_queue(status, id DESC);
CREATE INDEX IF NOT EXISTS idx_msg_email    ON messages_review_queue(sender_email, created_at);
CREATE INDEX IF NOT EXISTS idx_msg_ip       ON messages_review_queue(client_ip, created_at);

CREATE TABLE IF NOT EXISTS booker_sessions (
    token         TEXT PRIMARY KEY,
    booker_email  TEXT NOT NULL,
    created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_booker_email ON booker_sessions(booker_email);

CREATE TABLE IF NOT EXISTS booker_shows (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    booker_email  TEXT NOT NULL,
    title         TEXT NOT NULL,
    venue         TEXT,
    show_date     TEXT,
    show_time     TEXT,
    slots         INTEGER NOT NULL DEFAULT 5,
    notes         TEXT,
    created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_booker_shows_email ON booker_shows(booker_email, show_date DESC);

CREATE TABLE IF NOT EXISTS booker_lineup (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    show_id      INTEGER NOT NULL REFERENCES booker_shows(id) ON DELETE CASCADE,
    comic_slug   TEXT NOT NULL,
    comic_name   TEXT,
    note         TEXT,
    status       TEXT NOT NULL DEFAULT 'invited',  -- invited|booked|declined|confirmed
    notified_at  TEXT,
    response_at  TEXT,
    created_at   TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(show_id, comic_slug)
);
CREATE INDEX IF NOT EXISTS idx_lineup_show ON booker_lineup(show_id);
