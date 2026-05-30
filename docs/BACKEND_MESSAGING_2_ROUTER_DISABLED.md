# BACKEND.MESSAGING.2-ROUTER-DISABLED

**Status: IN_GIT_UNVERIFIED**
**Feature flag: MESSAGING_V2_ENABLED=false (default)**
**Live messaging: NOT enabled**

## Overview

Messaging V2 router wired to `main.py` in disabled mode, matching the pattern
used by Auth/Submissions/Claims/Payments V2 routers.

## Routes Wired

| Method | Path | Disabled response |
|---|---|---|
| GET | /api/messaging_v2/status | always-on, reports enabled=false |
| GET | /api/messaging_v2/threads | 503 disabled |
| POST | /api/messaging_v2/threads | 503 disabled |
| GET | /api/messaging_v2/threads/{id} | 503 disabled |
| POST | /api/messaging_v2/threads/{id}/reply | 503 disabled |
| POST | /api/messaging_v2/threads/{id}/report | 503 disabled |
| POST | /api/messaging_v2/users/{id}/block | 503 disabled |

## Safety Rules

- MESSAGING_V2_ENABLED=false — all action endpoints return 503
- No email notifications sent
- No paid messaging activation (no is_feature_unlocked check)
- No external network calls
- No UI cutover
- Block/report abuse controls wired but inactive

## Tests (23 total — test_messaging_v2_router.py)

Disabled (8): status always-on, list/create/get/reply/report/block all 503, no state on disabled
Enabled (15): status, create, list, get thread, nonparticipant 404, reply, reply to nonexistent 404, report, block prevents new thread, block idempotent, reply blocked after block, missing body 400, no external network, no email send, no paid feature activation
