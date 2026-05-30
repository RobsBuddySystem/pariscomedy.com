-- Rollback for 002_auth_v2.sql. Drops v2 auth tables in reverse FK order.
-- Safe to run multiple times.
DROP TABLE IF EXISTS rate_limits_v2;
DROP TABLE IF EXISTS audit_events_v2;
DROP TABLE IF EXISTS magic_links_v2;
DROP TABLE IF EXISTS sessions_v2;
DROP TABLE IF EXISTS users_v2;
