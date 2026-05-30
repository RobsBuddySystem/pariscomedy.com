-- 007_tickets_v2.sql
-- Ticket/source adapter candidate model. NOT auto-applied.

CREATE TABLE IF NOT EXISTS adapter_discoveries_v2 (
    candidate_id         TEXT PRIMARY KEY,
    source_platform      TEXT NOT NULL,
    source_url           TEXT NOT NULL,
    title                TEXT,
    venue_name           TEXT,
    venue_address        TEXT,
    city                 TEXT,
    starts_at            TEXT,
    recurrence_text      TEXT,
    language_guess       TEXT,
    ticket_url           TEXT,
    confidence_score     REAL DEFAULT 0.0,
    parser_status        TEXT NOT NULL DEFAULT 'parsed',
    duplicate_match_status TEXT NOT NULL DEFAULT 'unknown' CHECK (duplicate_match_status IN ('unknown','no_duplicate','duplicate_existing')),
    review_status        TEXT NOT NULL DEFAULT 'discovered'
                         CHECK (review_status IN ('discovered','needs_review','duplicate_existing','rejected','approved_for_import','imported','source_unreachable')),
    imported_listing_id  TEXT,
    notes                TEXT,
    affiliate_enabled    INTEGER NOT NULL DEFAULT 0 CHECK (affiliate_enabled IN (0,1)),
    robots_note          TEXT,
    created_at           TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
    updated_at           TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
    reviewed_at          TEXT,
    reviewed_by          TEXT
);

CREATE INDEX IF NOT EXISTS idx_discoveries_platform ON adapter_discoveries_v2 (source_platform);
CREATE INDEX IF NOT EXISTS idx_discoveries_review ON adapter_discoveries_v2 (review_status);
