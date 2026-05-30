# BACKEND.MESSAGING.3-CONNECT-MESSAGE-DRAFT

**Status: IN_GIT_UNVERIFIED**
**Scope: Frontend status note only. No V2 POST. No paid messaging. No flag change.**

## What This Phase Delivers

A Messaging V2 status note added to the "Send a message" form on `connect.html`.
The existing manual-review message flow is unchanged. No direct message delivery.
No paid messaging activation. No POST to `/api/messaging_v2/threads`.

## Changes to connect.html

Added above the "Send message →" button:

```html
<div id="messaging-v2-status">
  Direct messaging backend is not live yet. Messages are reviewed manually before delivery.
</div>
```

JS fetches `/api/messaging_v2/status`:

| Response | Status line |
|---|---|
| 503 / enabled=false | "Direct messaging backend is not live yet. Messages are reviewed manually before delivery." |
| Error/unreachable | same |
| enabled=true | "Messaging V2 backend reachable. Paid messaging is not active yet." |

**No V2 message button added. No POST to `/api/messaging_v2/*`.**

## Manual Review Copy Preserved

- "Messages are reviewed before delivery — usually within 24 hours." (existing subhead)
- "Direct messaging backend is not live yet. Messages are reviewed manually before delivery." (new note)
- "Messages are reviewed before delivery to protect inboxes." (existing footer)

## MESSAGING_V2_ENABLED

Still `false` (default). No DB migration. No paid messaging gate. No email notifications.

## Regression Guard

`scripts/regression_guard.py` check `messaging_v2_connect_draft` (check 21/21) fails if:

1. `connect.html` contains "direct messages are live", "dms are active", "paid messaging is active", "message sent directly"
2. A POST to `/api/messaging_v2/*` appears without an enabled guard

## Rollback

Remove `messaging-v2-status` div and `checkMessagingV2Status` JS from `connect.html`.
