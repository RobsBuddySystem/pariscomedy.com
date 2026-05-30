"""BACKEND.AUTH.1-CUTOVER-PLAN — Auth V2 FastAPI router.

Registers `/api/auth_v2/*` endpoints. When AUTH_V2_ENABLED=false (default),
every endpoint returns 503 with a clear disabled response and creates no
token, session, or audit row. When AUTH_V2_ENABLED=true (test env only),
endpoints delegate to backend/auth_v2.py.

NOT YET wired into main.py — that lands in a follow-up cutover phase. This
module is importable + testable in isolation.
"""
from __future__ import annotations

import sqlite3
from typing import Optional

from fastapi import APIRouter, Cookie, HTTPException, Request, Response

import auth_v2

router = APIRouter(prefix="/api/auth_v2", tags=["auth_v2"])

SESSION_COOKIE = "pc_session_v2"
CSRF_COOKIE = "pc_csrf_v2"


def _disabled() -> HTTPException:
    return HTTPException(
        status_code=503,
        detail={"error": {"code": "auth/disabled", "message": "Auth V2 disabled. Set AUTH_V2_ENABLED=true to enable."}},
    )


def _conn_factory():
    """Open a SQLite connection at module-import time. Patched in tests."""
    # Default uses same DB_PATH as main.py; production should provide its own factory.
    import os
    db_path = os.environ.get(
        "DB_PATH",
        os.path.join(os.path.dirname(__file__), "..", "data", "paris.db"),
    )
    return sqlite3.connect(db_path)


@router.get("/status")
def status_endpoint():
    return auth_v2.status()


@router.post("/magic-link/request")
async def magic_link_request(request: Request):
    if not auth_v2.AUTH_V2_ENABLED:
        raise _disabled()
    body = await request.json() if request.headers.get("content-type", "").startswith("application/json") else {}
    email = (body.get("email") or "").strip()
    role = body.get("role") or "user"
    ip = request.client.host if request.client else None
    try:
        with _conn_factory() as conn:
            auth_v2.request_magic_link(conn, email=email, role=role, ip=ip)
    except auth_v2.AuthV2Error as e:
        # Per R-01 mitigation: always return 204 to avoid email enumeration.
        # We still propagate hard errors (rate limit) so the client sees 429.
        if isinstance(e, auth_v2.RateLimitedError):
            raise HTTPException(status_code=e.http_status,
                                detail={"error": {"code": e.code, "message": str(e)}})
    return Response(status_code=204)


@router.get("/magic-link/consume")
def magic_link_consume(token: str, request: Request, response: Response):
    if not auth_v2.AUTH_V2_ENABLED:
        raise _disabled()
    ip = request.client.host if request.client else None
    ua = request.headers.get("user-agent")
    try:
        with _conn_factory() as conn:
            result = auth_v2.consume_magic_link(conn, token=token, ip=ip, user_agent=ua)
    except auth_v2.AuthV2Error as e:
        raise HTTPException(status_code=e.http_status,
                            detail={"error": {"code": e.code, "message": str(e)}})
    # Issue HttpOnly + Secure session cookie + readable CSRF cookie pair
    response.set_cookie(SESSION_COOKIE, result["session_id"], httponly=True, secure=True,
                        samesite="lax", max_age=14 * 24 * 3600)
    response.set_cookie(CSRF_COOKIE, auth_v2._new_token(16), httponly=False, secure=True,
                        samesite="lax", max_age=14 * 24 * 3600)
    return {"user_id": result["user_id"], "role": result["role"],
            "expires_at": result["expires_at"]}


@router.post("/logout")
def logout_endpoint(response: Response, session: Optional[str] = Cookie(default=None, alias=SESSION_COOKIE)):
    if not auth_v2.AUTH_V2_ENABLED:
        raise _disabled()
    if session:
        with _conn_factory() as conn:
            auth_v2.logout(conn, session_id=session)
    response.delete_cookie(SESSION_COOKIE)
    response.delete_cookie(CSRF_COOKIE)
    return Response(status_code=204)


@router.get("/me")
def me_endpoint(session: Optional[str] = Cookie(default=None, alias=SESSION_COOKIE)):
    if not auth_v2.AUTH_V2_ENABLED:
        raise _disabled()
    if not session:
        raise HTTPException(status_code=401, detail={"error": {"code": "auth/no_session", "message": "no session"}})
    with _conn_factory() as conn:
        cur = auth_v2.get_current_user(conn, session_token=session)
    if not cur:
        raise HTTPException(status_code=401, detail={"error": {"code": "auth/invalid_session", "message": "session invalid"}})
    return cur


@router.get("/session/expiry")
def session_expiry(session: Optional[str] = Cookie(default=None, alias=SESSION_COOKIE)):
    if not auth_v2.AUTH_V2_ENABLED:
        raise _disabled()
    if not session:
        raise HTTPException(status_code=401, detail={"error": {"code": "auth/no_session", "message": "no session"}})
    with _conn_factory() as conn:
        cur = auth_v2.get_current_user(conn, session_token=session)
    if not cur:
        raise HTTPException(status_code=401, detail={"error": {"code": "auth/invalid_session", "message": "session invalid"}})
    return {"expires_at": cur["expires_at"]}
