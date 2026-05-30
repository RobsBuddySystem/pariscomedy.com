CREATE TABLE IF NOT EXISTS payment_customers_v2 (
    user_id              TEXT PRIMARY KEY,
    provider             TEXT NOT NULL,
    provider_customer_id TEXT NOT NULL,
    created_at           TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS payment_subscriptions_v2 (
    id                       TEXT PRIMARY KEY,
    provider                 TEXT NOT NULL,
    provider_subscription_id TEXT NOT NULL UNIQUE,
    user_id                  TEXT NOT NULL,
    product_id               TEXT NOT NULL,
    status                   TEXT NOT NULL,  -- active|cancelled|past_due|incomplete|trialing
    current_period_end       TEXT,
    created_at               TEXT NOT NULL DEFAULT (datetime('now')),
    cancelled_at             TEXT
);
CREATE INDEX IF NOT EXISTS idx_pay_subs_user ON payment_subscriptions_v2(user_id, status);

CREATE TABLE IF NOT EXISTS payment_invoices_v2 (
    id                  TEXT PRIMARY KEY,
    provider            TEXT NOT NULL,
    provider_invoice_id TEXT NOT NULL UNIQUE,
    user_id             TEXT NOT NULL,
    amount_cents        INTEGER NOT NULL,
    currency            TEXT NOT NULL DEFAULT 'EUR',
    status              TEXT NOT NULL,
    hosted_invoice_url  TEXT,
    created_at          TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS payment_checkout_sessions_v2 (
    id            TEXT PRIMARY KEY,
    user_id       TEXT NOT NULL,
    product_id    TEXT NOT NULL,
    mode          TEXT NOT NULL,  -- 'dryrun' | 'live'
    created_at    TEXT NOT NULL DEFAULT (datetime('now')),
    redeemed_at   TEXT
);

CREATE TABLE IF NOT EXISTS payment_webhook_idempotency_v2 (
    event_id      TEXT PRIMARY KEY,
    provider      TEXT NOT NULL,
    event_type    TEXT NOT NULL,
    payload_hash  TEXT NOT NULL,
    received_at   TEXT NOT NULL DEFAULT (datetime('now'))
);
