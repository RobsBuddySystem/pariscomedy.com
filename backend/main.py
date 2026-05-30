"""
ParisComedy Backend — Booker Dashboard + Messaging API
=======================================================

Deployable FastAPI app extracted from the legacy monolith.
Hosts at: localhost:8765 (default), exposed via Cloudflare tunnel.

Endpoints:
  GET  /api/health
  POST /api/message                      — public contact-a-comic/booker/venue form
  POST /api/booker/auth                  — email → token (emailed if SMTP configured)
  GET  /api/booker/comics                — directory (no private emails)
  GET  /api/booker/shows                 — booker's shows + lineups
  POST /api/booker/shows                 — create show
  POST /api/booker/lineup                — invite comic to lineup
  DELETE /api/booker/lineup/{id}
  POST /api/booker/lineup/{id}/status    — accept/decline/confirm
  POST /api/booker/notify                — queue invites for admin review
  GET  /api/admin/messages?token=…       — admin: view pending review queue
  POST /api/admin/messages/{id}/status   — admin: mark approved/rejected

Env vars (all optional except in production):
  DB_PATH         default ./data/paris.db
  ADMIN_TOKEN     required for /api/admin/* — generate with: openssl rand -hex 16
  NOTIFY_EMAIL    default chucklericain@gmail.com
  SMTP_HOST       default smtp.gmail.com
  SMTP_PORT       default 587
  SMTP_USER       (Gmail address)
  SMTP_PASS       (Gmail app password)
  CORS_ORIGIN     default *  (set to https://pariscomedy.com in prod)
  COMICS_JSON     default ./data/comedians.json
"""
import json, os, re, secrets, smtplib, sqlite3, sys
from contextlib import contextmanager
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

# ── Config ───────────────────────────────────────────────────────────────────
DB_PATH      = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "..", "data", "paris.db"))
COMICS_JSON  = os.environ.get("COMICS_JSON", os.path.join(os.path.dirname(__file__), "..", "data", "comedians.json"))
ADMIN_TOKEN  = os.environ.get("ADMIN_TOKEN", "")
NOTIFY_EMAIL = os.environ.get("NOTIFY_EMAIL", "chucklericain@gmail.com")
SMTP_USER    = os.environ.get("SMTP_USER", "")
SMTP_PASS    = os.environ.get("SMTP_PASS", "")
SMTP_HOST    = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT    = int(os.environ.get("SMTP_PORT", "587"))
CORS_ORIGIN  = os.environ.get("CORS_ORIGIN", "*")

app = FastAPI(title="ParisComedy Backend", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[CORS_ORIGIN] if CORS_ORIGIN != "*" else ["*"],
    allow_methods=["*"], allow_headers=["*"], allow_credentials=False,
)

# BACKEND.AUTH.1-ROUTER-INTEGRATION-DISABLED — mount the v2 auth router.
# All endpoints are gated by AUTH_V2_ENABLED (default false) and return 503
# {error:{code:"auth/disabled"}} until the flag is enabled.
try:
    from auth_v2_router import router as auth_v2_router  # noqa: E402
    app.include_router(auth_v2_router)
except Exception as _e:  # noqa: BLE001
    import sys as _sys
    _sys.stderr.write(f"[main] auth_v2_router import failed: {_e}\n")

# BACKEND.SUBMIT.2-ROUTER-DISABLED — mount the v2 submissions router.
try:
    from submissions_v2_router import router as submissions_v2_router  # noqa: E402
    app.include_router(submissions_v2_router)
except Exception as _e:  # noqa: BLE001
    import sys as _sys
    _sys.stderr.write(f"[main] submissions_v2_router import failed: {_e}\n")

# BACKEND.CLAIM.2-ROUTER-DISABLED — mount the v2 claims router.
try:
    from claims_v2_router import router as claims_v2_router  # noqa: E402
    app.include_router(claims_v2_router)
except Exception as _e:  # noqa: BLE001
    import sys as _sys
    _sys.stderr.write(f"[main] claims_v2_router import failed: {_e}\n")

# BACKEND.PAYMENTS.2-ROUTER-DISABLED — mount the v2 payments router.
try:
    from payments_v2_router import router as payments_v2_router  # noqa: E402
    app.include_router(payments_v2_router)
except Exception as _e:  # noqa: BLE001
    import sys as _sys
    _sys.stderr.write(f"[main] payments_v2_router import failed: {_e}\n")

# BACKEND.MESSAGING.2-ROUTER-DISABLED — mount the v2 messaging router.
try:
    from messaging_v2_router import router as messaging_v2_router  # noqa: E402
    app.include_router(messaging_v2_router)
except Exception as _e:  # noqa: BLE001
    import sys as _sys
    _sys.stderr.write(f"[main] messaging_v2_router import failed: {_e}\n")

# BACKEND.TICKETS.2-ROUTER-DISABLED — mount the v2 tickets/adapters router.
try:
    from tickets_v2_router import router as tickets_v2_router  # noqa: E402
    app.include_router(tickets_v2_router)
except Exception as _e:  # noqa: BLE001
    import sys as _sys
    _sys.stderr.write(f"[main] tickets_v2_router import failed: {_e}\n")

# ── DB helper ────────────────────────────────────────────────────────────────
@contextmanager
def db():
    os.makedirs(os.path.dirname(os.path.abspath(DB_PATH)), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_schema():
    schema_path = os.path.join(os.path.dirname(__file__), "migrations", "001_init.sql")
    with db() as conn, open(schema_path) as f:
        conn.executescript(f.read())


def send_email(to_addr: str, subject: str, body: str, reply_to: str = "") -> bool:
    if not SMTP_USER or not SMTP_PASS:
        return False
    try:
        m = MIMEText(body, "plain", "utf-8")
        m["Subject"] = subject; m["From"] = SMTP_USER; m["To"] = to_addr
        if reply_to: m["Reply-To"] = reply_to
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as s:
            s.ehlo(); s.starttls(); s.login(SMTP_USER, SMTP_PASS)
            s.sendmail(SMTP_USER, [to_addr], m.as_string())
        return True
    except Exception as exc:
        print(f"[email] send failed: {exc}", file=sys.stderr)
        return False


# ── Client-side event tracking ───────────────────────────────────────────────
@app.post("/api/events", status_code=204)
async def track_event(request: Request):
    """Accept and discard client-side tracking events (privacy-preserving)."""
    return

@app.get("/api/events", status_code=204)
async def track_event_get():
    """Return 204 on GET probe (silences browser 405 console errors)."""
    return


# ── Health ───────────────────────────────────────────────────────────────────
@app.get("/api/health")
def health():
    try:
        with db() as conn:
            conn.execute("SELECT 1")
        db_ok = True
    except Exception as exc:
        db_ok = False
    return {
        "ok": db_ok,
        "version": app.version,
        "db_path": DB_PATH,
        "smtp_configured": bool(SMTP_USER and SMTP_PASS),
        "admin_token_set": bool(ADMIN_TOKEN),
        "comics_json_exists": os.path.exists(COMICS_JSON),
        "ts": datetime.utcnow().isoformat() + "Z",
    }


# ── Anti-spam: messaging ─────────────────────────────────────────────────────
@app.post("/api/message")
async def send_message(request: Request):
    """Public comic↔booker/venue contact. Queued for admin review."""
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(400, "invalid JSON")

    # Honeypot — silent success
    if str(data.get("website", "")).strip() or str(data.get("hp_field", "")).strip():
        return {"ok": True, "queued": True}

    sender_name    = str(data.get("sender_name", "")).strip()[:120]
    sender_email   = str(data.get("sender_email", "")).strip()[:200]
    sender_type    = str(data.get("sender_type", "")).strip().lower()
    recipient_type = str(data.get("recipient_type", "")).strip().lower()
    recipient_id   = str(data.get("recipient_id", "")).strip()[:120]
    subject        = str(data.get("subject", "")).strip()[:200]
    message        = str(data.get("message", "")).strip()
    source_page    = str(data.get("source_page", "")).strip()[:200]

    if not sender_name or not sender_email:
        raise HTTPException(400, "sender_name and sender_email required")
    if "@" not in sender_email or "." not in sender_email:
        raise HTTPException(400, "invalid sender_email")
    if sender_type not in {"comic", "booker", "venue", "fan"}:
        raise HTTPException(400, "invalid sender_type")
    if recipient_type not in {"booker", "comic", "venue"}:
        raise HTTPException(400, "invalid recipient_type")
    if len(message) < 10 or len(message) > 5000:
        raise HTTPException(400, "message must be 10-5000 characters")
    if len(re.findall(r"https?://", message)) > 3:
        raise HTTPException(400, "too many links")

    client_ip = request.client.host if request.client else ""

    with db() as conn:
        cur = conn.execute(
            "SELECT COUNT(*) FROM messages_review_queue WHERE sender_email=? AND created_at>datetime('now','-1 hour')",
            (sender_email,))
        if cur.fetchone()[0] >= 5: raise HTTPException(429, "rate limit: 5/hour per email")
        cur = conn.execute(
            "SELECT COUNT(*) FROM messages_review_queue WHERE client_ip=? AND created_at>datetime('now','-1 hour')",
            (client_ip,))
        if cur.fetchone()[0] >= 20: raise HTTPException(429, "rate limit: 20/hour per IP")
        conn.execute(
            """INSERT INTO messages_review_queue
               (sender_name, sender_email, sender_type, recipient_type, recipient_id,
                subject, message, source_page, client_ip)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (sender_name, sender_email, sender_type, recipient_type, recipient_id,
             subject, message, source_page, client_ip))

    send_email(NOTIFY_EMAIL,
               f"[ParisComedy msg] {sender_name} → {recipient_type}",
               f"New {sender_type}→{recipient_type} message (pending review)\n\n"
               f"From: {sender_name} <{sender_email}>\nTo: {recipient_type} {recipient_id or '(general)'}\n"
               f"Subject: {subject}\nSource: {source_page}\nIP: {client_ip}\n\n--- Message ---\n{message}\n",
               reply_to=sender_email)

    return {"ok": True, "queued": True, "review_required": True}


# ── Booker auth ──────────────────────────────────────────────────────────────
def booker_auth(request: Request) -> str:
    token = request.headers.get("X-Booker-Token", "")
    if not token: raise HTTPException(401, "missing token")
    with db() as conn:
        row = conn.execute("SELECT booker_email FROM booker_sessions WHERE token=?", (token,)).fetchone()
    if not row: raise HTTPException(401, "invalid token")
    return row["booker_email"]


@app.post("/api/booker/auth")
async def booker_auth_request(request: Request):
    data = await request.json()
    email = str(data.get("email", "")).strip().lower()
    if "@" not in email: raise HTTPException(400, "invalid email")
    token = secrets.token_urlsafe(9)
    with db() as conn:
        conn.execute("INSERT INTO booker_sessions(token, booker_email) VALUES(?,?)", (token, email))
    delivered = send_email(email, "[ParisComedy] Your booker token",
                           f"Your Paris Comedy booker token:\n\n{token}\n\nPaste it into the dashboard to access your lineups.")
    return {"ok": True, "delivered": delivered, "dev_token": (None if delivered else token)}


@app.get("/api/booker/comics")
def booker_comics(request: Request):
    booker_auth(request)
    if not os.path.exists(COMICS_JSON):
        return {"comics": [], "count": 0}
    with open(COMICS_JSON) as f:
        comics = json.load(f)
    today = datetime.now()
    three_mo_ago = (today - timedelta(days=90)).strftime("%Y-%m-%d")
    out = []
    for c in comics:
        upcoming = c.get("upcoming_shows") or []
        last_seen = (c.get("last_seen") or "")[:10]
        # Strip private email — only public surface
        out.append({
            "slug": c.get("slug"), "name": c.get("name"),
            "langs": c.get("langs", []), "photo": c.get("photo", ""),
            "bio": (c.get("bio") or "")[:400],
            "instagram": c.get("instagram", ""),
            "actuality": c.get("actuality", ""),
            "upcoming_count": len(upcoming),
            "next_show": (upcoming[0] if upcoming else None),
            "recent_paris": last_seen >= three_mo_ago,
            "has_upcoming": len(upcoming) > 0,
            "claimed": c.get("claimed", False),
            "touring": bool(c.get("touring") or "one-man" in (c.get("actuality") or "").lower()),
        })
    return {"comics": out, "count": len(out)}


@app.post("/api/booker/shows")
async def booker_create_show(request: Request):
    email = booker_auth(request)
    data = await request.json()
    with db() as conn:
        cur = conn.execute(
            "INSERT INTO booker_shows(booker_email,title,venue,show_date,show_time,slots,notes) VALUES(?,?,?,?,?,?,?)",
            (email, str(data.get("title",""))[:200], str(data.get("venue",""))[:200],
             str(data.get("date",""))[:20], str(data.get("time",""))[:10],
             int(data.get("slots", 5)), str(data.get("notes",""))[:2000]))
        return {"ok": True, "show_id": cur.lastrowid}


@app.get("/api/booker/shows")
def booker_list_shows(request: Request):
    email = booker_auth(request)
    with db() as conn:
        shows = [dict(r) for r in conn.execute(
            "SELECT * FROM booker_shows WHERE booker_email=? ORDER BY show_date DESC, id DESC", (email,)).fetchall()]
        for s in shows:
            s["lineup"] = [dict(r) for r in conn.execute(
                "SELECT id,comic_slug,comic_name,note,status,notified_at FROM booker_lineup WHERE show_id=?",
                (s["id"],)).fetchall()]
    return {"shows": shows}


@app.post("/api/booker/lineup")
async def booker_lineup_add(request: Request):
    booker_auth(request)
    data = await request.json()
    show_id = int(data.get("show_id", 0))
    slug = str(data.get("comic_slug", "")).strip()
    if not show_id or not slug: raise HTTPException(400, "show_id and comic_slug required")
    with db() as conn:
        try:
            cur = conn.execute(
                "INSERT INTO booker_lineup(show_id, comic_slug, comic_name, note) VALUES(?,?,?,?)",
                (show_id, slug, str(data.get("comic_name",""))[:200], str(data.get("note",""))[:1000]))
            return {"ok": True, "lineup_id": cur.lastrowid}
        except sqlite3.IntegrityError:
            raise HTTPException(409, "comic already in this lineup")


@app.delete("/api/booker/lineup/{lineup_id}")
def booker_lineup_remove(lineup_id: int, request: Request):
    booker_auth(request)
    with db() as conn:
        conn.execute("DELETE FROM booker_lineup WHERE id=?", (lineup_id,))
    return {"ok": True}


@app.post("/api/booker/lineup/{lineup_id}/status")
async def booker_lineup_status(lineup_id: int, request: Request):
    booker_auth(request)
    data = await request.json()
    status = str(data.get("status","")).strip()
    if status not in {"invited","booked","declined","confirmed"}:
        raise HTTPException(400, "invalid status")
    with db() as conn:
        conn.execute("UPDATE booker_lineup SET status=?, response_at=datetime('now') WHERE id=?",
                     (status, lineup_id))
    return {"ok": True}


@app.post("/api/booker/notify")
async def booker_notify(request: Request):
    email = booker_auth(request)
    data = await request.json()
    show_id = int(data.get("show_id", 0))
    with db() as conn:
        show = conn.execute("SELECT * FROM booker_shows WHERE id=? AND booker_email=?",
                            (show_id, email)).fetchone()
        if not show: raise HTTPException(404, "show not found")
        lineup = conn.execute(
            "SELECT id,comic_slug,comic_name,note FROM booker_lineup WHERE show_id=? AND notified_at IS NULL",
            (show_id,)).fetchall()
        queued = 0
        for row in lineup:
            body = (f"You've been invited to perform.\n\n"
                    f"Show: {show['title']}\nVenue: {show['venue']}\n"
                    f"Date: {show['show_date']} at {show['show_time']}\nBooker: {email}\n"
                    + (f"\nNote: {row['note']}\n" if row['note'] else "")
                    + (f"\nDetails: {show['notes']}\n" if show['notes'] else "")
                    + "\n[ACCEPT or DECLINE — reply to this email]")
            conn.execute(
                """INSERT INTO messages_review_queue
                   (sender_name,sender_email,sender_type,recipient_type,recipient_id,
                    subject,message,source_page,client_ip,status)
                   VALUES(?,?,?,?,?,?,?,?,?,?)""",
                (f"Booker {email}", email, "booker", "comic", row["comic_slug"],
                 f"Booking invite: {show['title']} on {show['show_date']}", body,
                 "/booker-dashboard.html", "", "booker_invite_pending"))
            conn.execute("UPDATE booker_lineup SET notified_at=datetime('now') WHERE id=?", (row["id"],))
            queued += 1
    return {"ok": True, "notifications_queued": queued, "delivery": "manual_review"}


# ── Admin (token-gated) ──────────────────────────────────────────────────────
def admin_auth(token: str):
    if not ADMIN_TOKEN or token != ADMIN_TOKEN:
        raise HTTPException(403, "forbidden")


@app.get("/api/admin/messages")
def admin_messages(token: str = "", status: str = "pending_review"):
    admin_auth(token)
    with db() as conn:
        rows = conn.execute(
            "SELECT * FROM messages_review_queue WHERE status=? ORDER BY id DESC LIMIT 200",
            (status,)).fetchall()
    return {"queue": [dict(r) for r in rows], "count": len(rows)}


@app.post("/api/admin/messages/{msg_id}/status")
async def admin_message_status(msg_id: int, request: Request):
    data = await request.json()
    admin_auth(str(data.get("token", "")))
    new_status = str(data.get("status", "")).strip()
    if new_status not in {"approved", "rejected", "delivered", "pending_review"}:
        raise HTTPException(400, "invalid status")
    with db() as conn:
        conn.execute("UPDATE messages_review_queue SET status=? WHERE id=?", (new_status, msg_id))
    return {"ok": True}


# Initialize schema on import
init_schema()
