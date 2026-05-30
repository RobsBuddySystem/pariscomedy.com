"""BACKEND.PAYMENTS.2-ROUTER-DISABLED — Payments V2 FastAPI router.

Registers `/api/payments_v2/*` endpoints.
When PAYMENTS_ENABLED=false (default), all action endpoints return 503.
PAYMENTS_PROVIDER=dryrun by default. PAYMENT_WEBHOOKS_ENABLED=false by default.

No real Stripe/SumUp/API call. No provider API key. No live checkout.
No paid feature activation. No pricing copy changes.
"""
from __future__ import annotations

import os
import sqlite3
from typing import Optional

from fastapi import APIRouter, HTTPException, Request, Response

import payments_v2

router = APIRouter(prefix="/api/payments_v2", tags=["payments_v2"])


def _disabled() -> HTTPException:
    return HTTPException(
        status_code=503,
        detail={"error": {"code": "payments/disabled",
                          "message": "Payments disabled. Set PAYMENTS_ENABLED=true to enable."}},
    )


def _conn_factory():
    """Open a SQLite connection. Patched in tests."""
    db_path = os.environ.get(
        "DB_PATH",
        os.path.join(os.path.dirname(__file__), "..", "data", "paris.db"),
    )
    return sqlite3.connect(db_path)


# ── Status ────────────────────────────────────────────────────────────────────

@router.get("/status")
def status_endpoint():
    return payments_v2.status()


# ── Product catalog (safe even when disabled) ─────────────────────────────────

@router.get("/products")
def list_products():
    """Product catalog is safe to expose regardless of PAYMENTS_ENABLED.
    No checkout links are returned; products are read from the static catalog.
    """
    return {"products": payments_v2.list_products(), "checkout_live": False}


# ── Checkout (disabled mode returns 503) ──────────────────────────────────────

@router.post("/checkout-session")
async def create_checkout_session(request: Request):
    if not payments_v2.PAYMENTS_ENABLED:
        raise _disabled()
    body = await request.json() if request.headers.get("content-type", "").startswith("application/json") else {}
    user_id = (body.get("user_id") or "").strip()
    product_id = (body.get("product_id") or "").strip()
    if not user_id or not product_id:
        raise HTTPException(status_code=400, detail={"error": {"code": "payments/missing_fields",
                                                                "message": "user_id and product_id required"}})
    try:
        with _conn_factory() as conn:
            result = payments_v2.create_checkout_session_dry_run(conn, user_id=user_id, product_id=product_id)
    except payments_v2.PaymentsError as e:
        raise HTTPException(status_code=400, detail={"error": {"code": "payments/invalid", "message": str(e)}})
    return result


@router.post("/customer-portal")
def customer_portal():
    if not payments_v2.PAYMENTS_ENABLED:
        raise _disabled()
    raise HTTPException(status_code=503, detail={"error": {"code": "payments/provider_not_live",
                                                            "message": "Customer portal not available until provider is live."}})


@router.get("/subscriptions")
def get_subscriptions(user_id: Optional[str] = None):
    if not payments_v2.PAYMENTS_ENABLED:
        raise _disabled()
    if not user_id:
        raise HTTPException(status_code=400, detail={"error": {"code": "payments/missing_fields",
                                                                "message": "user_id required"}})
    with _conn_factory() as conn:
        subs = payments_v2.subscription_status_for_user(conn, user_id=user_id)
    return {"subscriptions": subs}


# ── Webhook ───────────────────────────────────────────────────────────────────

@router.post("/webhook")
async def webhook(request: Request):
    if not payments_v2.PAYMENT_WEBHOOKS_ENABLED:
        raise HTTPException(
            status_code=503,
            detail={"error": {"code": "payments/webhooks_disabled",
                              "message": "Payment webhooks disabled."}},
        )
    body_bytes = await request.body()
    payload = body_bytes.decode("utf-8", errors="replace")
    event_id = request.headers.get("x-webhook-event-id") or request.headers.get("stripe-signature", "")[:32]
    event_type = request.headers.get("x-webhook-event-type", "unknown")
    if not event_id:
        raise HTTPException(status_code=400, detail={"error": {"code": "payments/missing_event_id",
                                                                "message": "x-webhook-event-id header required"}})
    with _conn_factory() as conn:
        result = payments_v2.record_webhook_event(
            conn, event_id=event_id, event_type=event_type,
            payload=payload, provider=payments_v2.PAYMENTS_PROVIDER,
        )
    return result
