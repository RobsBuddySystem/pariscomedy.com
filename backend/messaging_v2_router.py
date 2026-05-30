"""messaging_v2_router.py — BACKEND.MESSAGING.2-ROUTER-DISABLED.

All routes return 503 when MESSAGING_V2_ENABLED=false (default).
GET /api/messaging_v2/status is always-on.
No paid messaging activation. No email notifications. No UI cutover.
"""
from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager

from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel

import messaging_v2

router = APIRouter(prefix="/api/messaging_v2")

DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "..", "data", "pariscomedy.db"))


@contextmanager
def _conn_factory():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def _disabled():
    return HTTPException(
        status_code=503,
        detail={"error": {"code": "messaging/disabled", "message": "Messaging V2 is not enabled."}},
    )


# ---------------------------------------------------------------------------
# Always-on
# ---------------------------------------------------------------------------

@router.get("/status")
def get_status():
    return messaging_v2.status()


# ---------------------------------------------------------------------------
# Thread listing
# ---------------------------------------------------------------------------

@router.get("/threads")
def list_threads(user_id: str):
    if not messaging_v2.MESSAGING_V2_ENABLED:
        raise _disabled()
    with _conn_factory() as conn:
        return {"threads": messaging_v2.list_threads_for_user(conn, user_id)}


# ---------------------------------------------------------------------------
# Thread creation
# ---------------------------------------------------------------------------

class CreateThreadRequest(BaseModel):
    sender_user_id: str
    sender_role: str
    recipient_user_id: str
    recipient_role: str
    subject: str
    body: str


@router.post("/threads")
def create_thread(req: CreateThreadRequest):
    if not messaging_v2.MESSAGING_V2_ENABLED:
        raise _disabled()
    if not req.sender_user_id or not req.recipient_user_id or not req.body:
        raise HTTPException(status_code=400, detail={"error": {"code": "messaging/missing_fields"}})
    try:
        with _conn_factory() as conn:
            result = messaging_v2.create_thread(
                conn,
                sender_user_id=req.sender_user_id,
                sender_role=req.sender_role,
                recipient_user_id=req.recipient_user_id,
                recipient_role=req.recipient_role,
                subject=req.subject,
                body=req.body,
            )
        return result
    except messaging_v2.MessagingError as e:
        msg = str(e)
        if "blocked" in msg:
            raise HTTPException(status_code=403, detail={"error": {"code": "messaging/blocked", "message": msg}})
        if "daily_recipient_cap" in msg:
            raise HTTPException(status_code=429, detail={"error": {"code": "messaging/daily_cap", "message": msg}})
        raise HTTPException(status_code=400, detail={"error": {"code": "messaging/error", "message": msg}})


# ---------------------------------------------------------------------------
# Thread detail
# ---------------------------------------------------------------------------

@router.get("/threads/{thread_id}")
def get_thread(thread_id: str, viewer_user_id: str):
    if not messaging_v2.MESSAGING_V2_ENABLED:
        raise _disabled()
    try:
        with _conn_factory() as conn:
            return messaging_v2.get_thread(conn, thread_id, viewer_user_id)
    except messaging_v2.MessagingError as e:
        raise HTTPException(status_code=404, detail={"error": {"code": "messaging/not_found", "message": str(e)}})


# ---------------------------------------------------------------------------
# Reply
# ---------------------------------------------------------------------------

class ReplyRequest(BaseModel):
    sender_user_id: str
    body: str


@router.post("/threads/{thread_id}/reply")
def reply_to_thread(thread_id: str, req: ReplyRequest):
    if not messaging_v2.MESSAGING_V2_ENABLED:
        raise _disabled()
    if not req.body:
        raise HTTPException(status_code=400, detail={"error": {"code": "messaging/missing_fields"}})
    try:
        with _conn_factory() as conn:
            return messaging_v2.reply_to_thread(conn, thread_id, req.sender_user_id, req.body)
    except messaging_v2.MessagingError as e:
        msg = str(e)
        if "not_found" in msg:
            raise HTTPException(status_code=404, detail={"error": {"code": "messaging/not_found", "message": msg}})
        if "blocked" in msg:
            raise HTTPException(status_code=403, detail={"error": {"code": "messaging/blocked", "message": msg}})
        raise HTTPException(status_code=400, detail={"error": {"code": "messaging/error", "message": msg}})


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

class ReportRequest(BaseModel):
    reporter_user_id: str
    reason: str


@router.post("/threads/{thread_id}/report")
def report_thread(thread_id: str, req: ReportRequest):
    if not messaging_v2.MESSAGING_V2_ENABLED:
        raise _disabled()
    try:
        with _conn_factory() as conn:
            return messaging_v2.report_thread(conn, thread_id, req.reporter_user_id, req.reason)
    except messaging_v2.MessagingError as e:
        msg = str(e)
        if "not_found" in msg:
            raise HTTPException(status_code=404, detail={"error": {"code": "messaging/not_found", "message": msg}})
        raise HTTPException(status_code=403, detail={"error": {"code": "messaging/not_participant", "message": msg}})


# ---------------------------------------------------------------------------
# Block
# ---------------------------------------------------------------------------

class BlockRequest(BaseModel):
    blocker_user_id: str
    reason: str | None = None


@router.post("/users/{blocked_user_id}/block")
def block_user(blocked_user_id: str, req: BlockRequest):
    if not messaging_v2.MESSAGING_V2_ENABLED:
        raise _disabled()
    with _conn_factory() as conn:
        return messaging_v2.block_user(conn, req.blocker_user_id, blocked_user_id, req.reason)
