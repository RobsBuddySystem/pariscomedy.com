"""BACKEND.PAYMENTS.1-SCAFFOLD — payments service module.

INERT BY DEFAULT. No routes. No provider call. No real checkout.

Loads product catalog from data/payment-products.json.
"""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

PAYMENTS_ENABLED = os.environ.get("PAYMENTS_ENABLED", "false").lower() in ("1", "true", "yes", "on")
PAYMENTS_PROVIDER = os.environ.get("PAYMENTS_PROVIDER", "dryrun").lower()
PAYMENT_WEBHOOKS_ENABLED = os.environ.get("PAYMENT_WEBHOOKS_ENABLED", "false").lower() in ("1", "true", "yes", "on")

ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATH = ROOT / "data" / "payment-products.json"

_CATALOG: Optional[dict] = None


class PaymentsError(Exception):
    pass


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _new_id() -> str:
    return uuid.uuid4().hex


def status() -> dict:
    return {
        "enabled": PAYMENTS_ENABLED,
        "provider": PAYMENTS_PROVIDER,
        "webhooks_enabled": PAYMENT_WEBHOOKS_ENABLED,
        "product_count": len(list_products()),
    }


# ── Catalog ──────────────────────────────────────────────────────────────────

def _load_catalog() -> dict:
    global _CATALOG
    if _CATALOG is None:
        _CATALOG = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    return _CATALOG


def list_products() -> list[dict]:
    return list(_load_catalog().get("products", []))


def get_product(product_id: str) -> dict:
    for p in list_products():
        if p["id"] == product_id:
            return p
    raise PaymentsError(f"unknown product: {product_id!r}")


def _audit(conn, *, action: str, target_id: str, metadata: Optional[dict] = None) -> None:
    try:
        conn.execute(
            """INSERT INTO audit_events_v2
               (user_id, actor_role, action, target_type, target_id, metadata_json, created_at, ip)
               VALUES (?,?,?,?,?,?,?,?)""",
            (None, "system", action, "payment", target_id,
             json.dumps(metadata) if metadata else None, _now_iso(), None),
        )
    except sqlite3.OperationalError:
        pass


# ── Checkout ─────────────────────────────────────────────────────────────────

def create_checkout_session_dry_run(conn: sqlite3.Connection, *, user_id: str, product_id: str) -> dict:
    """Always dry-run in this scaffold. Inserts a row + returns a placeholder URL."""
    get_product(product_id)  # raises if unknown
    sid = _new_id()
    conn.execute(
        """INSERT INTO payment_checkout_sessions_v2(id, user_id, product_id, mode, created_at)
           VALUES(?,?,?,?,?)""",
        (sid, user_id, product_id, "dryrun", _now_iso()),
    )
    _audit(conn, action="payments.checkout.dryrun", target_id=sid,
           metadata={"user_id": user_id, "product_id": product_id})
    return {"id": sid, "mode": "dryrun",
            "url": f"https://pariscomedy.com/billing/dryrun?session_id={sid}"}


# ── Webhook idempotency ──────────────────────────────────────────────────────

def record_webhook_event(conn: sqlite3.Connection, *, event_id: str, event_type: str,
                         payload: str, provider: str = "dryrun") -> dict:
    """Returns {"recorded": True, "duplicate": False} the first time an
    event_id is seen; {"recorded": False, "duplicate": True} on replay."""
    h = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    try:
        conn.execute(
            """INSERT INTO payment_webhook_idempotency_v2
               (event_id, provider, event_type, payload_hash, received_at)
               VALUES(?,?,?,?,?)""",
            (event_id, provider, event_type, h, _now_iso()),
        )
    except sqlite3.IntegrityError:
        return {"recorded": False, "duplicate": True}
    _audit(conn, action=f"payments.webhook.{event_type}", target_id=event_id)
    return {"recorded": True, "duplicate": False}


# ── Subscription state ───────────────────────────────────────────────────────

def apply_subscription_created(
    conn: sqlite3.Connection,
    *,
    user_id: str,
    product_id: str,
    provider_subscription_id: str,
    current_period_end: Optional[str] = None,
    provider: str = "dryrun",
) -> dict:
    get_product(product_id)
    sid = _new_id()
    conn.execute(
        """INSERT INTO payment_subscriptions_v2
           (id, provider, provider_subscription_id, user_id, product_id,
            status, current_period_end, created_at)
           VALUES (?,?,?,?,?,?,?,?)""",
        (sid, provider, provider_subscription_id, user_id, product_id,
         "active", current_period_end, _now_iso()),
    )
    _audit(conn, action="payments.subscription.created", target_id=sid,
           metadata={"user_id": user_id, "product_id": product_id})
    return {"id": sid, "status": "active"}


def apply_subscription_cancelled(conn: sqlite3.Connection,
                                 *, provider_subscription_id: str) -> bool:
    cur = conn.execute(
        """UPDATE payment_subscriptions_v2
           SET status='cancelled', cancelled_at=?
           WHERE provider_subscription_id=? AND status='active'""",
        (_now_iso(), provider_subscription_id),
    )
    return cur.rowcount > 0


def subscription_status_for_user(conn: sqlite3.Connection, *, user_id: str) -> list[dict]:
    rows = conn.execute(
        """SELECT product_id, status, current_period_end
           FROM payment_subscriptions_v2 WHERE user_id=?""",
        (user_id,),
    ).fetchall()
    return [{"product_id": r[0], "status": r[1], "current_period_end": r[2]} for r in rows]


# ── Feature gate ─────────────────────────────────────────────────────────────

def is_feature_unlocked(conn: sqlite3.Connection, *, user_id: str, feature: str) -> bool:
    """Returns True only if user has an active subscription whose product
    unlocks the named feature."""
    subs = subscription_status_for_user(conn, user_id=user_id)
    active_products = {s["product_id"] for s in subs if s["status"] == "active"}
    for pid in active_products:
        try:
            p = get_product(pid)
        except PaymentsError:
            continue
        if feature in (p.get("unlocks") or []):
            return True
    return False
