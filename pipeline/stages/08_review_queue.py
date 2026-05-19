#!/usr/bin/env python3
"""
Stage 08: Format review queue as HTML for admin UI.

Reads pipeline/output/review_queue.json and writes api/review-queue.html.
The HTML is static — no server needed. Updated daily by the pipeline.
Accept/Reject currently use mailto: links; future: POST to /api/review.

Input:  pipeline/output/review_queue.json
Output: api/review-queue.html
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

REPO_ROOT = Path(__file__).resolve().parents[2]
REVIEW_QUEUE_PATH = REPO_ROOT / "pipeline" / "output" / "review_queue.json"
OUTPUT_PATH = REPO_ROOT / "api" / "review-queue.html"

PARIS_TZ = ZoneInfo("Europe/Paris")
logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

ADMIN_EMAIL = "hello@pariscomedy.com"


def confidence_badge(score: float) -> str:
    pct = int(score * 100)
    if pct >= 70:
        color = "#2d9954"
    elif pct >= 55:
        color = "#c97d10"
    else:
        color = "#c0392b"
    return f'<span style="color:{color};font-weight:bold">{pct}%</span>'


def format_date(iso: str | None) -> str:
    if not iso:
        return "—"
    try:
        from dateutil import parser as dp
        dt = dp.parse(iso)
        return dt.strftime("%a %d %b %Y %H:%M")
    except Exception:
        return iso[:16] if iso else "—"


def html_escape(s: str | None) -> str:
    if not s:
        return ""
    return (
        s.replace("&", "&amp;")
         .replace("<", "&lt;")
         .replace(">", "&gt;")
         .replace('"', "&quot;")
    )


def build_html(payload: dict) -> str:
    generated = payload.get("generated", "")
    shows = payload.get("shows", [])
    count = len(shows)

    try:
        gen_dt = datetime.fromisoformat(generated).strftime("%Y-%m-%d %H:%M %Z")
    except Exception:
        gen_dt = generated or "unknown"

    rows = ""
    for show in shows:
        name = html_escape(show.get("name") or "")
        date = format_date(show.get("start_date"))
        venue = html_escape(show.get("venue_name") or "")
        conf = show.get("confidence") or 0.0
        ev_type = html_escape(show.get("type") or "")
        language = html_escape(show.get("language") or "")
        url = html_escape(show.get("url") or "")
        ev_id = html_escape(str(show.get("id") or ""))
        description = html_escape((show.get("description") or "")[:120])
        errors = show.get("_validation_errors") or []
        error_html = (
            f'<br><small style="color:#c0392b">⚠ {html_escape(", ".join(errors))}</small>'
            if errors else ""
        )
        method = html_escape(show.get("_llm_method") or "")

        subject_accept = f"[pariscomedy] ACCEPT: {show.get('name', '')}"
        subject_reject = f"[pariscomedy] REJECT: {show.get('name', '')}"
        body_accept = (
            f"Event ID: {show.get('id', '')}\n"
            f"Name: {show.get('name', '')}\n"
            f"Date: {show.get('start_date', '')}\n"
            f"Venue: {show.get('venue_name', '')}\n"
            f"URL: {show.get('url', '')}\n\n"
            f"Action: ACCEPT — add to shows.json"
        )
        body_reject = (
            f"Event ID: {show.get('id', '')}\n"
            f"Name: {show.get('name', '')}\n\n"
            f"Action: REJECT — discard"
        )

        from urllib.parse import quote
        accept_href = (
            f"mailto:{ADMIN_EMAIL}?subject={quote(subject_accept)}&body={quote(body_accept)}"
        )
        reject_href = (
            f"mailto:{ADMIN_EMAIL}?subject={quote(subject_reject)}&body={quote(body_reject)}"
        )

        rows += f"""
        <tr>
          <td>
            {'<a href="' + url + '" target="_blank" rel="noopener">' if url else ''}{name}{'</a>' if url else ''}
            {error_html}
            <br><small style="color:#888">{description}</small>
            <br><small style="color:#aaa">ID: {ev_id} | {method}</small>
          </td>
          <td>{date}</td>
          <td>{venue}</td>
          <td>{confidence_badge(conf)}</td>
          <td><span style="text-transform:capitalize">{ev_type}</span><br><small>{language}</small></td>
          <td>
            <a href="{accept_href}" style="background:#2d9954;color:#fff;padding:4px 10px;border-radius:4px;text-decoration:none;font-size:13px">Accept</a>
            &nbsp;
            <a href="{reject_href}" style="background:#c0392b;color:#fff;padding:4px 10px;border-radius:4px;text-decoration:none;font-size:13px">Reject</a>
          </td>
        </tr>"""

    if not shows:
        rows = """
        <tr>
          <td colspan="6" style="text-align:center;color:#888;padding:32px">
            No shows awaiting review. Pipeline last ran: """ + gen_dt + """
          </td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Review Queue — pariscomedy.com Admin</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
           margin: 0; padding: 24px; background: #f5f5f5; color: #222; }}
    h1 {{ font-size: 1.4rem; margin: 0 0 4px; }}
    .meta {{ font-size: 0.85rem; color: #666; margin-bottom: 20px; }}
    .badge {{ display: inline-block; background: #1a1a2e; color: #fff;
              padding: 2px 8px; border-radius: 20px; font-size: 12px; margin-left: 8px; }}
    table {{ width: 100%; border-collapse: collapse; background: #fff;
             border-radius: 8px; overflow: hidden;
             box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
    thead {{ background: #1a1a2e; color: #fff; }}
    th {{ padding: 12px 14px; text-align: left; font-size: 13px;
          font-weight: 600; letter-spacing: 0.3px; }}
    td {{ padding: 12px 14px; font-size: 13px; vertical-align: top;
          border-bottom: 1px solid #f0f0f0; }}
    tr:last-child td {{ border-bottom: none; }}
    tr:hover td {{ background: #f9f9ff; }}
    a {{ color: #1a1a2e; }}
    .note {{ font-size: 12px; color: #888; margin-top: 16px; }}
  </style>
</head>
<body>
  <h1>pariscomedy.com — Review Queue <span class="badge">{count}</span></h1>
  <div class="meta">
    Auto-generated by daily pipeline. Last updated: <strong>{gen_dt}</strong>
    &nbsp;|&nbsp; Shows classified at 0.50–0.79 confidence require human review before publishing.
    &nbsp;|&nbsp; <a href="/">← Site</a>
  </div>

  <table>
    <thead>
      <tr>
        <th style="width:35%">Event</th>
        <th style="width:16%">Date</th>
        <th style="width:18%">Venue</th>
        <th style="width:8%">Score</th>
        <th style="width:10%">Type</th>
        <th style="width:13%">Action</th>
      </tr>
    </thead>
    <tbody>
      {rows}
    </tbody>
  </table>

  <p class="note">
    Accept/Reject buttons open a pre-filled email to {ADMIN_EMAIL}.
    Future: POST to /api/review endpoint for one-click publishing.
    &nbsp;|&nbsp; Pipeline runs daily at 06:00 Paris time on openclawpc (RTX 3090).
  </p>
</body>
</html>"""


def main():
    if not REVIEW_QUEUE_PATH.exists():
        log.warning(f"[REVIEW_QUEUE] {REVIEW_QUEUE_PATH} not found — writing empty page")
        payload = {"generated": datetime.now(tz=PARIS_TZ).isoformat(), "shows": []}
    else:
        with open(REVIEW_QUEUE_PATH) as f:
            payload = json.load(f)

    html = build_html(payload)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        f.write(html)

    count = len(payload.get("shows", []))
    log.info(f"[REVIEW_QUEUE] Written {count} shows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
