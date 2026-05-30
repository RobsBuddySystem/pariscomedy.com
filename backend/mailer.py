"""BACKEND.EMAIL.1-PLAN-SCAFFOLD — dry-run-first email abstraction.

Single mailer interface used by auth_v2 (and later submission/claim/messaging).
In dry-run mode (default) no SMTP/API call is made — outgoing payloads are
captured in-process for tests and written to stderr.

Env vars:
  EMAIL_SEND_REAL       default "false". Must be "true" to actually send.
  EMAIL_PROVIDER        default "dryrun". Future: "postmark" | "resend" | "smtp".
  EMAIL_FROM            default "no-reply@pariscomedy.com".
  EMAIL_REPLY_TO        default "support@pariscomedy.com".
  POSTMARK_TOKEN        NOT consulted in this phase (scaffold-only).

Security:
- Magic-link token NEVER logged at INFO level when EMAIL_SEND_REAL=true
  (stderr-printed only in dry-run mode for developer convenience).
- No external network call from this module unless EMAIL_PROVIDER != "dryrun"
  AND EMAIL_SEND_REAL=true (both must be set). Even then this scaffold returns
  NotImplementedError because the provider integration lands in a future phase.

Templates:
- Minimal text + HTML pair per template name.
- Validate from/reply-to addresses on send.
"""
from __future__ import annotations

import dataclasses
import os
import re
import sys
from typing import Optional

EMAIL_SEND_REAL = os.environ.get("EMAIL_SEND_REAL", "false").lower() in ("1", "true", "yes", "on")
EMAIL_PROVIDER = os.environ.get("EMAIL_PROVIDER", "dryrun").lower()
EMAIL_FROM = os.environ.get("EMAIL_FROM", "no-reply@pariscomedy.com")
EMAIL_REPLY_TO = os.environ.get("EMAIL_REPLY_TO", "support@pariscomedy.com")

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")


class MailerError(Exception):
    pass


@dataclasses.dataclass
class OutgoingEmail:
    to: str
    subject: str
    text: str
    html: str
    template: str
    from_addr: str = EMAIL_FROM
    reply_to: str = EMAIL_REPLY_TO


# In-process capture for tests/dry-run inspection.
_CAPTURED: list[OutgoingEmail] = []


def captured() -> list[OutgoingEmail]:
    return list(_CAPTURED)


def reset_captured() -> None:
    _CAPTURED.clear()


# ── Templates ────────────────────────────────────────────────────────────────

def magic_link_email(to: str, token: str, base_url: str = "https://pariscomedy.com") -> OutgoingEmail:
    link = f"{base_url}/auth_v2/magic-link/consume?token={token}"
    text = (
        f"Click the link below to log in to Paris Comedy.\n\n"
        f"{link}\n\n"
        f"This link expires in 15 minutes. If you did not request it, ignore this email."
    )
    html = (
        f"<p>Click the link below to log in to Paris Comedy.</p>"
        f'<p><a href="{link}">{link}</a></p>'
        f"<p>This link expires in 15 minutes. If you did not request it, ignore this email.</p>"
    )
    return OutgoingEmail(
        to=to, subject="Your Paris Comedy login link", text=text, html=html,
        template="magic_link",
    )


# ── Send ─────────────────────────────────────────────────────────────────────

def _validate_addr(addr: str, label: str) -> None:
    if not addr or not EMAIL_RE.match(addr):
        raise MailerError(f"invalid {label} address: {addr!r}")


def send(email: OutgoingEmail) -> dict:
    """Send (or dry-run) an email.

    Returns: {"delivered": bool, "provider": str, "mode": str, "to": ..., "template": ...}.
    """
    _validate_addr(email.from_addr, "from")
    _validate_addr(email.reply_to, "reply-to")
    _validate_addr(email.to, "to")
    _CAPTURED.append(email)

    if not EMAIL_SEND_REAL or EMAIL_PROVIDER == "dryrun":
        # Dry-run: token appears in text body but we do not log raw text in
        # production; only template name + recipient for ops visibility.
        sys.stderr.write(
            f"[mailer DRY-RUN] template={email.template} to={email.to} "
            f"subject={email.subject!r}\n"
        )
        return {"delivered": False, "provider": "dryrun", "mode": "dryrun",
                "to": email.to, "template": email.template}

    # Real provider integration is intentionally NOT implemented in this
    # scaffold phase. It will land behind explicit BACKEND.EMAIL.1-PROVIDER
    # authorization with Postmark/Resend/SMTP keys.
    raise NotImplementedError(
        f"Real email send not implemented in scaffold; provider={EMAIL_PROVIDER}. "
        f"Add provider integration in BACKEND.EMAIL.1-PROVIDER phase."
    )


def status() -> dict:
    return {
        "send_real": EMAIL_SEND_REAL,
        "provider": EMAIL_PROVIDER,
        "from": EMAIL_FROM,
        "reply_to": EMAIL_REPLY_TO,
    }
