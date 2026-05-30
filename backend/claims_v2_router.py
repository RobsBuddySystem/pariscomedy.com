"""BACKEND.CLAIM.2-ROUTER-DISABLED — Claims V2 FastAPI router.

Registers `/api/claims_v2/*` and `/api/admin/claims_v2/*` endpoints.
When CLAIMS_V2_ENABLED=false (default), every action endpoint returns 503.

No public claim UI cutover. No ownership writeback. No real email. No
production DB migration. No secrets.
"""
from __future__ import annotations

import os
import sqlite3
from typing import Optional

from fastapi import APIRouter, HTTPException, Request, Response

import claims_v2

router = APIRouter(tags=["claims_v2"])


def _disabled() -> HTTPException:
    return HTTPException(
        status_code=503,
        detail={"error": {"code": "claims/disabled",
                          "message": "Claims V2 disabled. Set CLAIMS_V2_ENABLED=true to enable."}},
    )


def _conn_factory():
    """Open a SQLite connection. Patched in tests."""
    db_path = os.environ.get(
        "DB_PATH",
        os.path.join(os.path.dirname(__file__), "..", "data", "paris.db"),
    )
    return sqlite3.connect(db_path)


# ── Status ────────────────────────────────────────────────────────────────────

@router.get("/api/claims_v2/status")
def status_endpoint():
    return claims_v2.status()


# ── Public claim submission endpoints ────────────────────────────────────────

async def _handle_claim_request(request: Request, claim_type: str) -> dict:
    if not claims_v2.CLAIMS_V2_ENABLED:
        raise _disabled()
    body = await request.json() if request.headers.get("content-type", "").startswith("application/json") else {}
    body["claim_type"] = claim_type
    ip = request.client.host if request.client else None
    ua = request.headers.get("user-agent")
    try:
        with _conn_factory() as conn:
            result = claims_v2.create_claim_request(conn, body, ip=ip, user_agent=ua)
    except claims_v2.ClaimError as e:
        raise HTTPException(status_code=400, detail={"error": {"code": "claims/invalid", "message": str(e)}})
    return {"id": result["id"], "status": result["status"]}


@router.post("/api/claims_v2/comic")
async def claim_comic(request: Request):
    return await _handle_claim_request(request, "comic")


@router.post("/api/claims_v2/show-runner")
async def claim_show_runner(request: Request):
    return await _handle_claim_request(request, "show_runner")


@router.post("/api/claims_v2/venue")
async def claim_venue(request: Request):
    return await _handle_claim_request(request, "venue")


# ── Claim status (public, fail-closed) ───────────────────────────────────────

@router.get("/api/claim-status/{claim_type}/{target_id_or_slug}")
def claim_status(claim_type: str, target_id_or_slug: str):
    if not claims_v2.CLAIMS_V2_ENABLED:
        raise _disabled()
    with _conn_factory() as conn:
        result = claims_v2.claim_status_for_target(conn, claim_type, target_id_or_slug)
    return result


# ── Admin endpoints ───────────────────────────────────────────────────────────

@router.get("/api/admin/claims_v2")
def admin_list_claims():
    if not claims_v2.CLAIMS_V2_ENABLED:
        raise _disabled()
    with _conn_factory() as conn:
        rows = claims_v2.list_pending_claims(conn)
    return {"claims": rows}


def _admin_transition(claim_id: str, new_status: str) -> Response:
    if not claims_v2.CLAIMS_V2_ENABLED:
        raise _disabled()
    try:
        with _conn_factory() as conn:
            claims_v2.mark_claim_status(conn, claim_id, new_status, reviewer="admin")
    except claims_v2.ClaimError as e:
        raise HTTPException(status_code=404, detail={"error": {"code": "claims/invalid_transition", "message": str(e)}})
    return Response(status_code=204)


@router.post("/api/admin/claims_v2/{claim_id}/approve")
def admin_approve(claim_id: str):
    return _admin_transition(claim_id, "approved")


@router.post("/api/admin/claims_v2/{claim_id}/reject")
def admin_reject(claim_id: str):
    return _admin_transition(claim_id, "rejected")


@router.post("/api/admin/claims_v2/{claim_id}/mark-duplicate")
def admin_mark_duplicate(claim_id: str):
    return _admin_transition(claim_id, "duplicate")


@router.post("/api/admin/claims_v2/{claim_id}/mark-spam")
def admin_mark_spam(claim_id: str):
    return _admin_transition(claim_id, "spam")
