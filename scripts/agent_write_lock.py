#!/usr/bin/env python3
"""
agent_write_lock.py — P5.AGENTS.1

Lightweight file-based write lock for multi-agent runs on this repo.

Contract:
  * Only one writer agent at a time. Other agents must be read-only auditors
    unless they explicitly hold the lock.
  * Lock file: `.pc-write.lock` at repo root.
  * Lock payload: JSON {"agent_name": str, "scope": str, "acquired_at": ISO8601, "pid": int}.
  * Created atomically with os.open(O_CREAT | O_EXCL).
  * Stale-timeout: 15 minutes. A lock older than 15 minutes is considered
    stale and may be overridden with a warning.
  * Soft enforcement: the pre-commit hook only blocks a commit when
    env var PC_AGENT_NAME is set AND does not match the lock holder.
    Humans + the main agent (no PC_AGENT_NAME set) stay free.

CLI:
    python3 scripts/agent_write_lock.py acquire <agent_name> "<scope>"
    python3 scripts/agent_write_lock.py release
    python3 scripts/agent_write_lock.py read_status
    python3 scripts/agent_write_lock.py enforce_for_commit

stdlib only. Python 3.
"""

from __future__ import annotations

import json
import os
import sys
import errno
from datetime import datetime, timezone, timedelta
from pathlib import Path

LOCK_FILENAME = ".pc-write.lock"
STALE_AFTER_MINUTES = 15


def _repo_root() -> Path:
    """Walk up from this file to find repo root (dir containing .git)."""
    here = Path(__file__).resolve().parent
    cur = here
    for _ in range(8):
        if (cur / ".git").exists():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    # Fallback: parent of scripts/
    return here.parent


def _lock_path() -> Path:
    return _repo_root() / LOCK_FILENAME


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_iso(s: str) -> datetime | None:
    try:
        # Accept trailing Z
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        return datetime.fromisoformat(s)
    except Exception:
        return None


def _read_lock_file() -> dict | None:
    p = _lock_path()
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def _is_stale(payload: dict) -> bool:
    acquired = _parse_iso(payload.get("acquired_at", ""))
    if not acquired:
        return True
    age = datetime.now(timezone.utc) - acquired
    return age > timedelta(minutes=STALE_AFTER_MINUTES)


def acquire(agent_name: str, scope: str) -> int:
    """Atomically acquire the write lock.

    Returns 0 on success, 1 on failure (already held by another live agent).
    Overrides stale locks (>15 min old) with a warning to stderr.
    """
    if not agent_name:
        print("ERROR: agent_name required", file=sys.stderr)
        return 2
    p = _lock_path()
    payload = {
        "agent_name": agent_name,
        "scope": scope or "",
        "acquired_at": _now_iso(),
        "pid": os.getpid(),
    }
    data = json.dumps(payload, indent=2).encode("utf-8")

    try:
        fd = os.open(str(p), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
    except OSError as e:
        if e.errno != errno.EEXIST:
            print(f"ERROR: could not create lock: {e}", file=sys.stderr)
            return 2
        # Lock exists — inspect for staleness.
        existing = _read_lock_file()
        if existing and _is_stale(existing):
            print(
                f"WARNING: overriding stale lock (held by "
                f"{existing.get('agent_name')!r}, "
                f"acquired_at={existing.get('acquired_at')!r}, "
                f"stale > {STALE_AFTER_MINUTES} min)",
                file=sys.stderr,
            )
            try:
                p.unlink()
            except OSError as e2:
                print(f"ERROR: could not remove stale lock: {e2}", file=sys.stderr)
                return 2
            try:
                fd = os.open(str(p), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
            except OSError as e3:
                print(f"ERROR: race overriding stale lock: {e3}", file=sys.stderr)
                return 1
        else:
            holder = (existing or {}).get("agent_name", "<unknown>")
            scope_h = (existing or {}).get("scope", "")
            acquired_at = (existing or {}).get("acquired_at", "")
            print(
                f"ERROR: lock held by {holder!r} scope={scope_h!r} "
                f"acquired_at={acquired_at!r}",
                file=sys.stderr,
            )
            return 1

    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
    except Exception as e:
        print(f"ERROR: could not write lock payload: {e}", file=sys.stderr)
        try:
            p.unlink()
        except OSError:
            pass
        return 2

    print(f"ACQUIRED {p}: agent={agent_name!r} scope={scope!r}")
    return 0


def release() -> int:
    p = _lock_path()
    if not p.exists():
        print("RELEASE: no lock held (noop)")
        return 0
    try:
        p.unlink()
        print(f"RELEASED {p}")
        return 0
    except OSError as e:
        print(f"ERROR: could not release lock: {e}", file=sys.stderr)
        return 2


def read_status() -> int:
    payload = _read_lock_file()
    if payload is None:
        print("STATUS: no lock held")
        return 0
    stale = _is_stale(payload)
    print(json.dumps(payload, indent=2))
    print(f"# stale={'yes' if stale else 'no'} (threshold={STALE_AFTER_MINUTES}min)")
    return 0


def enforce_for_commit() -> int:
    """Pre-commit gate.

    Soft enforcement:
      * No lock held -> allow (exit 0).
      * Lock held AND env PC_AGENT_NAME unset -> allow (human / main agent).
      * Lock held, env PC_AGENT_NAME set, matches holder -> allow.
      * Lock held, env PC_AGENT_NAME set, MISMATCH -> block (exit 1).
      * Lock stale -> warn, allow.
    """
    payload = _read_lock_file()
    if payload is None:
        return 0
    if _is_stale(payload):
        print(
            f"agent_write_lock: WARNING stale lock from "
            f"{payload.get('agent_name')!r} ignored",
            file=sys.stderr,
        )
        return 0
    me = os.environ.get("PC_AGENT_NAME", "").strip()
    if not me:
        # Human or unidentified main agent — soft signal only.
        return 0
    holder = payload.get("agent_name", "")
    if me == holder:
        return 0
    print(
        f"agent_write_lock: BLOCKED commit by PC_AGENT_NAME={me!r}; "
        f"write lock held by {holder!r} scope={payload.get('scope','')!r} "
        f"acquired_at={payload.get('acquired_at','')!r}. "
        f"Wait or release the lock.",
        file=sys.stderr,
    )
    return 1


def _usage() -> int:
    print(__doc__ or "", file=sys.stderr)
    return 2


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        return _usage()
    cmd = argv[1]
    if cmd == "acquire":
        if len(argv) < 3:
            print("usage: acquire <agent_name> [scope]", file=sys.stderr)
            return 2
        agent = argv[2]
        scope = argv[3] if len(argv) > 3 else ""
        return acquire(agent, scope)
    if cmd == "release":
        return release()
    if cmd == "read_status":
        return read_status()
    if cmd == "enforce_for_commit":
        return enforce_for_commit()
    return _usage()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
