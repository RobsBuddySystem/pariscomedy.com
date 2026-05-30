"""tickets_v2_router.py — BACKEND.TICKETS.2-ROUTER-DISABLED.

All admin/action routes return 503 when TICKETS_ADAPTERS_ENABLED=false (default).
GET /api/tickets_v2/status is always-on.
GET /api/tickets_v2/adapters returns registry with imports_enabled=false when disabled.
No live scraping. No public import. No affiliate links. No listing changes.
"""
from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager

from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel

import tickets_v2

router = APIRouter()

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
        detail={"error": {"code": "tickets/disabled", "message": "Tickets adapters are not enabled."}},
    )


# ---------------------------------------------------------------------------
# Always-on
# ---------------------------------------------------------------------------

@router.get("/api/tickets_v2/status")
def get_status():
    return tickets_v2.status()


@router.get("/api/tickets_v2/adapters")
def list_adapters():
    """Adapter registry is safe to read even when disabled.
    Returns imports_enabled=false when TICKETS_ADAPTERS_ENABLED=false."""
    adapters = tickets_v2.list_adapters()
    return {
        "adapters": adapters,
        "imports_enabled": False,
        "affiliate_links_enabled": False,
    }


# ---------------------------------------------------------------------------
# Admin discovery routes — disabled when TICKETS_ADAPTERS_ENABLED=false
# ---------------------------------------------------------------------------

@router.get("/api/admin/tickets_v2/discoveries")
def list_discoveries():
    if not tickets_v2.TICKETS_ADAPTERS_ENABLED:
        raise _disabled()
    with _conn_factory() as conn:
        return {"discoveries": tickets_v2.list_review_queue(conn)}


class DiscoveryCreateRequest(BaseModel):
    source_platform: str
    source_url: str
    title: str | None = None
    venue_name: str | None = None
    venue_address: str | None = None
    city: str = "Paris"
    starts_at: str | None = None
    recurrence_text: str | None = None
    language_guess: str = "fr"
    ticket_url: str | None = None
    confidence_score: float = 0.0
    notes: str | None = None


@router.post("/api/admin/tickets_v2/discoveries")
def create_discovery(req: DiscoveryCreateRequest):
    if not tickets_v2.TICKETS_ADAPTERS_ENABLED:
        raise _disabled()
    try:
        candidate = tickets_v2.normalize_candidate(req.model_dump())
    except tickets_v2.TicketsError as e:
        raise HTTPException(status_code=400, detail={"error": {"code": "tickets/invalid_platform", "message": str(e)}})
    with _conn_factory() as conn:
        result = tickets_v2.save_candidate(conn, candidate)
        dup = tickets_v2.detect_candidate_duplicate(conn, candidate)
    return {**result, "duplicate_check": dup}


@router.post("/api/admin/tickets_v2/discoveries/{candidate_id}/approve")
def approve_discovery(candidate_id: str):
    if not tickets_v2.TICKETS_ADAPTERS_ENABLED:
        raise _disabled()
    with _conn_factory() as conn:
        result = tickets_v2.mark_candidate_status(conn, candidate_id, "approved_for_import", reviewer="admin")
    return result


@router.post("/api/admin/tickets_v2/discoveries/{candidate_id}/reject")
def reject_discovery(candidate_id: str):
    if not tickets_v2.TICKETS_ADAPTERS_ENABLED:
        raise _disabled()
    with _conn_factory() as conn:
        result = tickets_v2.mark_candidate_status(conn, candidate_id, "rejected", reviewer="admin")
    return result


@router.post("/api/admin/tickets_v2/discoveries/{candidate_id}/mark-duplicate")
def mark_duplicate(candidate_id: str):
    if not tickets_v2.TICKETS_ADAPTERS_ENABLED:
        raise _disabled()
    with _conn_factory() as conn:
        result = tickets_v2.mark_candidate_status(conn, candidate_id, "duplicate_existing", reviewer="admin")
    return result


@router.post("/api/admin/tickets_v2/discoveries/{candidate_id}/mark-unreachable")
def mark_unreachable(candidate_id: str):
    if not tickets_v2.TICKETS_ADAPTERS_ENABLED:
        raise _disabled()
    with _conn_factory() as conn:
        result = tickets_v2.mark_candidate_status(conn, candidate_id, "source_unreachable", reviewer="admin")
    return result


@router.post("/api/admin/tickets_v2/discoveries/{candidate_id}/dry-run-import")
def dry_run_import(candidate_id: str):
    if not tickets_v2.TICKETS_ADAPTERS_ENABLED:
        raise _disabled()
    try:
        with _conn_factory() as conn:
            return tickets_v2.import_candidate_dry_run(conn, candidate_id)
    except tickets_v2.TicketsError as e:
        msg = str(e)
        if "not_found" in msg:
            raise HTTPException(status_code=404, detail={"error": {"code": "tickets/not_found", "message": msg}})
        raise HTTPException(status_code=400, detail={"error": {"code": "tickets/import_blocked", "message": msg}})
