"""BACKEND.SUBMIT.2-ROUTER-DISABLED — Submissions V2 FastAPI router.

Registers `/api/submissions_v2/*` and `/api/admin/submissions_v2/*` endpoints.
When SUBMISSIONS_V2_ENABLED=false (default), every endpoint returns 503 with a
clear disabled response and creates no submission, audit, or listing row.

NOT wired to public /connect.html form — that cutover lands in a later phase.
No email sent. No public listings created.
"""
from __future__ import annotations

import os
import sqlite3
from typing import Optional

from fastapi import APIRouter, HTTPException, Request, Response

import submissions_v2

router = APIRouter(tags=["submissions_v2"])

SUBMISSIONS_V2_ENABLED = submissions_v2.SUBMISSIONS_V2_ENABLED


def _disabled() -> HTTPException:
    return HTTPException(
        status_code=503,
        detail={"error": {"code": "submissions/disabled",
                          "message": "Submissions V2 disabled. Set SUBMISSIONS_V2_ENABLED=true to enable."}},
    )


def _conn_factory():
    """Open a SQLite connection. Patched in tests."""
    db_path = os.environ.get(
        "DB_PATH",
        os.path.join(os.path.dirname(__file__), "..", "data", "paris.db"),
    )
    return sqlite3.connect(db_path)


# ── Public endpoints ──────────────────────────────────────────────────────────

@router.get("/api/submissions_v2/status")
def status_endpoint():
    return submissions_v2.status()


@router.post("/api/submissions_v2/show")
async def submit_show(request: Request):
    if not submissions_v2.SUBMISSIONS_V2_ENABLED:
        raise _disabled()
    body = await request.json() if request.headers.get("content-type", "").startswith("application/json") else {}
    ip = request.client.host if request.client else None
    ua = request.headers.get("user-agent")
    try:
        with _conn_factory() as conn:
            result = submissions_v2.create_show_submission(conn, body, ip=ip, user_agent=ua)
    except submissions_v2.SubmissionError as e:
        raise HTTPException(status_code=400, detail={"error": {"code": "submissions/invalid", "message": str(e)}})
    return {"id": result["id"], "status": result["status"]}


# ── Admin endpoints ───────────────────────────────────────────────────────────

@router.get("/api/admin/submissions_v2")
def admin_list_submissions(status: Optional[str] = None):
    if not submissions_v2.SUBMISSIONS_V2_ENABLED:
        raise _disabled()
    with _conn_factory() as conn:
        rows = submissions_v2.list_pending_submissions(conn)
    if status:
        rows = [r for r in rows if r.get("status") == status]
    return {"submissions": rows}


def _admin_transition(submission_id: str, new_status: str) -> Response:
    if not submissions_v2.SUBMISSIONS_V2_ENABLED:
        raise _disabled()
    try:
        with _conn_factory() as conn:
            ok = submissions_v2.mark_submission_status(conn, submission_id, new_status, reviewer="admin")
    except submissions_v2.SubmissionError as e:
        raise HTTPException(status_code=404, detail={"error": {"code": "submissions/invalid_transition", "message": str(e)}})
    if not ok:
        raise HTTPException(status_code=404, detail={"error": {"code": "submissions/not_found", "message": "submission not found"}})
    return Response(status_code=204)


@router.post("/api/admin/submissions_v2/{submission_id}/approve")
def admin_approve(submission_id: str):
    return _admin_transition(submission_id, "approved")


@router.post("/api/admin/submissions_v2/{submission_id}/reject")
def admin_reject(submission_id: str):
    return _admin_transition(submission_id, "rejected")


@router.post("/api/admin/submissions_v2/{submission_id}/mark-duplicate")
def admin_mark_duplicate(submission_id: str):
    return _admin_transition(submission_id, "duplicate")


@router.post("/api/admin/submissions_v2/{submission_id}/mark-spam")
def admin_mark_spam(submission_id: str):
    return _admin_transition(submission_id, "spam")
