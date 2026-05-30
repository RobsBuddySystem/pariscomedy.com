# BACKEND.MESSAGING.1-SCAFFOLD

**Status:** IN_GIT_UNVERIFIED — pending ChatGPT closure  
**Authorized by:** ChatGPT 2026-05-30 (after BACKEND.PAYMENTS.1-SCAFFOLD closed)

## What this phase delivers

Comic↔Booker messaging scaffold: migration + service module + 15 tests. No routes wired. No public messaging UI. No email sent.

## Files

| File | Description |
|---|---|
| `backend/migrations/006_messaging_v2.sql` | 4 tables: threads, messages, blocks, reports |
| `backend/migrations/006_messaging_v2.rollback.sql` | Rollback script |
| `backend/messaging_v2.py` | Service module (no FastAPI router) |
| `backend/tests/test_messaging_v2.py` | 15 unit tests |

## DB tables

- `message_threads_v2` — thread with participant_a/b, roles, subject, status (active/blocked/reported/archived)
- `messages_v2` — individual messages (sent/hidden/deleted/reported), FK to threads
- `message_blocks_v2` — UNIQUE(blocker, blocked) — idempotent block
- `message_reports_v2` — report per thread per user

## Service functions

| Function | Description |
|---|---|
| `create_thread(...)` | New thread + first message; checks block + daily cap |
| `reply_to_thread(...)` | Reply; checks participant + block + thread status |
| `list_threads_for_user(...)` | Only threads user participates in |
| `get_thread(..., viewer_user_id)` | Fail-closed: non-participants get MessagingError; hidden/deleted messages excluded |
| `block_user(...)` | Idempotent; marks active threads blocked |
| `report_thread(...)` | Marks thread reported; fail-closed on non-participant |
| `soft_hide_message(...)` | Sets status=hidden |
| `can_message(...)` | Returns False if either party blocked the other |
| `enforce_daily_recipient_limit(...)` | Raises after DAILY_RECIPIENT_CAP (default 20) distinct recipients/day |
| `status()` | Returns enabled flag + cap |

## Abuse controls

- Daily distinct-recipient cap (20/day, env-configurable)
- Block: prevents new threads and replies; marks existing threads blocked
- Report: marks thread reported; only participants can report
- Non-participant cannot view thread (MessagingError)
- Hidden/deleted messages excluded from get_thread for normal viewers

## Feature gate

- `is_feature_unlocked(conn, user_id="...", feature="messaging")` from payments_v2 checked in tests
- Fails closed: unpaid user → False
- Active comic_plus subscription → True (test DB only)

## What is NOT live

- No FastAPI router (`APIRouter` not present in module)
- `MESSAGING_V2_ENABLED=false` by default
- No email notification
- No public messaging UI
- Production DB migration NOT auto-applied

## Test results

15/15 PASS. Full suite: 101/101 PASS.

## Rollback

```
git revert <sha> && git push origin main
# optional DB: sqlite3 data/paris.db < backend/migrations/006_messaging_v2.rollback.sql
```
