CREATE TABLE IF NOT EXISTS claims_v2 (
    id                  TEXT PRIMARY KEY,
    claim_type          TEXT NOT NULL CHECK (claim_type IN ('comic','show_runner','venue')),
    claimant_name       TEXT,
    claimant_email      TEXT NOT NULL,
    target_id           TEXT,
    target_slug         TEXT,
    target_name         TEXT,
    instagram_url       TEXT,
    recent_post_url     TEXT,
    domain_email        TEXT,
    website_url         TEXT,
    notes               TEXT,
    honeypot            TEXT,
    spam_signals        TEXT,
    status              TEXT NOT NULL DEFAULT 'received'
        CHECK (status IN ('received','needs_review','approved','rejected','duplicate','spam')),
    review_notes        TEXT,
    reviewed_by         TEXT,
    reviewed_at         TEXT,
    created_at          TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at          TEXT NOT NULL DEFAULT (datetime('now')),
    duplicate_of        TEXT,
    ip                  TEXT,
    user_agent          TEXT
);
CREATE INDEX IF NOT EXISTS idx_claims_v2_status        ON claims_v2(status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_claims_v2_target        ON claims_v2(claim_type, target_id, target_slug);
CREATE INDEX IF NOT EXISTS idx_claims_v2_email         ON claims_v2(claimant_email, created_at);
