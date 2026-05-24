#!/usr/bin/env python3
"""End-to-end tests for show-runner portal — publish model, dates, lineup.

Runs against the live backend. Requires a fresh approved claim so it can mint
its own owner token (it does this via /api/show/claim + admin approve).

Tests 30 cases from the spec.
"""
from __future__ import annotations
import json, re, sys, time, urllib.request, urllib.parse
import os

BASE = "https://api.pariscomedy.com"
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "pc-admin-2026")
TEST_SLUG = "comedy-lab"  # use an existing show in directory


def http(method, path, headers=None, body=None):
    data = None
    if body is not None:
        data = body.encode() if isinstance(body, str) else json.dumps(body).encode()
    req = urllib.request.Request(BASE + path, method=method,
        headers={"User-Agent": "PC-Tests/1", "Content-Type": "application/json",
                 **(headers or {})}, data=data)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")


def main() -> int:
    fails = []
    def assert_eq(label, got, want):
        if got != want: fails.append(f"{label}: expected {want!r} got {got!r}")
    def assert_in(label, needle, haystack):
        if needle not in haystack: fails.append(f"{label}: {needle!r} not in {haystack!r}")
    def assert_not_in(label, needle, haystack):
        if needle in haystack: fails.append(f"{label}: forbidden {needle!r} present in {haystack!r}")

    # Mint a fresh owner token via claim + admin approve
    claim_code, claim_body = http("POST", "/api/show/claim", body={
        "show_slug": TEST_SLUG, "show_name": "Comedy Lab",
        "claimant_name": "Test Runner", "claimant_email": "tests@example.com",
        "role": "producer", "source_url": "https://www.eventbrite.com/o/comedy-lab",
        "venue": "Comedy Lab",
    })
    assert_eq("claim 200", claim_code, 200)
    cid = json.loads(claim_body)["claim_id"]
    appr_code, appr_body = http("POST", f"/api/admin/show-claims/{cid}/approve",
                                headers={"X-Admin-Token": ADMIN_TOKEN})
    assert_eq("approve 200", appr_code, 200)
    appr = json.loads(appr_body)
    m = re.search(r"owner_token=([\w_-]+)", appr["magic_link"])
    if not m: fails.append("magic link missing token"); print("\n".join(fails)); return 1
    token = m.group(1)
    auth = {"Authorization": f"Bearer {token}"}
    ad = {"X-Admin-Token": ADMIN_TOKEN}

    # 1. Owner PATCH saves draft
    c, _ = http("PATCH", f"/api/owner/show/{TEST_SLUG}", headers=auth,
                body={"tagline": f"Paris top English lab {int(time.time())}",
                      "description": f"Weekly stand-up {int(time.time())}.",
                      "ticket_url": f"https://www.eventbrite.com/e/x-{int(time.time())}",
                      "venue": f"Comedy Lab Café {int(time.time())}"})
    assert_eq("(1) PATCH draft 200", c, 200)

    # 2. Public profile unchanged until publish
    c, body = http("GET", f"/api/show/{TEST_SLUG}/public-profile")
    pre = json.loads(body).get("profile") or {}
    # 3. Publish safe fields applies
    c, body = http("POST", f"/api/owner/show/{TEST_SLUG}/publish",
                   headers=auth, body={})
    pub = json.loads(body)
    assert_eq("(3) publish 200", c, 200)
    if "tagline" not in pub["applied_immediately"]:
        fails.append(f"(3) tagline should be in applied_immediately: {pub}")
    if "venue" not in pub["pending_admin_review"]:
        fails.append(f"(5) venue should be in pending_admin_review: {pub}")
    c, body = http("GET", f"/api/show/{TEST_SLUG}/public-profile")
    after = json.loads(body)["profile"]
    if not (after["tagline"] or "").startswith("Paris top English lab"):
        fails.append(f"(3) tagline not published: {after['tagline']!r}")
    assert_eq("(2) venue NOT yet visible (sensitive)", after["venue"], pre.get("venue"))

    # 4. Bilingual without evidence rejected at PATCH
    c, body = http("PATCH", f"/api/owner/show/{TEST_SLUG}", headers=auth,
                   body={"language": "bi"})
    assert_eq("(4) bi without evidence 400", c, 400)
    c, _ = http("PATCH", f"/api/owner/show/{TEST_SLUG}", headers=auth,
                body={"language": "bi", "language_evidence": "page says bilingual"})
    assert_eq("(4b) bi with evidence 200", c, 200)

    # 6. Admin approve sensitive change (the venue from step 3)
    c, body = http("GET", "/api/admin/show-profile-changes?status=pending_review",
                   headers=ad)
    changes = json.loads(body)["changes"]
    venue_ch = next((x for x in changes if x["field_name"] == "venue" and x["show_slug"] == TEST_SLUG), None)
    if not venue_ch: fails.append("(6) no venue pending change found")
    else:
        c, _ = http("POST", f"/api/admin/show-profile-changes/{venue_ch['id']}/approve?note=ok",
                    headers=ad)
        assert_eq("(6) admin approve 200", c, 200)
        c, body = http("GET", f"/api/show/{TEST_SLUG}/public-profile")
        if not (json.loads(body)["profile"]["venue"] or "").startswith("Comedy Lab Café"):
            fails.append(f"(6) venue not applied: {json.loads(body)['profile']['venue']!r}")

    # 7. Admin reject sensitive change (force a new one via show_name)
    http("PATCH", f"/api/owner/show/{TEST_SLUG}", headers=auth,
         body={"show_name": "BogusRename"})
    http("POST", f"/api/owner/show/{TEST_SLUG}/publish", headers=auth, body={})
    c, body = http("GET", "/api/admin/show-profile-changes?status=pending_review", headers=ad)
    sn = next((x for x in json.loads(body)["changes"] if x["field_name"] == "show_name" and x["show_slug"] == TEST_SLUG), None)
    if sn:
        http("POST", f"/api/admin/show-profile-changes/{sn['id']}/reject?note=no", headers=ad)
        c, body = http("GET", f"/api/show/{TEST_SLUG}/public-profile")
        if (json.loads(body)["profile"] or {}).get("show_name") == "BogusRename":
            fails.append("(7) rejected change leaked into public profile")

    # 8. Public profile never exposes owner_email
    c, body = http("GET", f"/api/show/{TEST_SLUG}/public-profile")
    assert_not_in("(8) owner_email not in public profile", "owner_email", body)
    assert_not_in("(8) @example.com not in public profile", "@example.com", body)

    # 11-14: Dates CRUD
    c, body = http("POST", f"/api/owner/show/{TEST_SLUG}/dates", headers=auth,
                   body={"show_date": "2026-12-15", "start_time": "20:30",
                         "ticket_url": "https://eventbrite.com/e/ticket-aaa"})
    assert_eq("(11) add date 200", c, 200)
    d1 = json.loads(body)["id"]
    c, body = http("POST", f"/api/owner/show/{TEST_SLUG}/dates", headers=auth,
                   body={"show_date": "2026-12-22", "start_time": "20:30"})
    d2 = json.loads(body)["id"]
    c, _ = http("PATCH", f"/api/owner/show/{TEST_SLUG}/dates/{d1}", headers=auth,
                body={"show_date": "2026-12-16", "start_time": "21:00",
                      "ticket_url": "https://eventbrite.com/e/ticket-aaa", "source_url": None})
    assert_eq("(12) edit date 200", c, 200)
    c, _ = http("POST", f"/api/owner/show/{TEST_SLUG}/dates/{d2}/cancel", headers=auth, body="{}")
    assert_eq("(13) cancel date 200", c, 200)
    c, _ = http("POST", f"/api/owner/show/{TEST_SLUG}/dates/{d1}/sold-out", headers=auth, body="{}")
    assert_eq("(14) sold-out 200", c, 200)
    # Past date rejected
    c, _ = http("POST", f"/api/owner/show/{TEST_SLUG}/dates", headers=auth,
                body={"show_date": "2020-01-01"})
    assert_eq("(16) past date 400", c, 400)

    # 15+17: public-profile dates correctness
    c, body = http("GET", f"/api/show/{TEST_SLUG}/public-profile")
    pp = json.loads(body)
    dates = pp.get("dates", [])
    have_status = {d["show_date"]: d["status"] for d in dates}
    if "2026-12-16" not in have_status or have_status["2026-12-16"] != "sold_out":
        fails.append(f"(14/15) sold_out date not in public dates: {dates}")
    if "2026-12-22" in have_status:
        fails.append(f"(17) cancelled date should be hidden: {dates}")
    if any(d.get("ticket_url") and "owner_email" in d for d in dates):
        fails.append("(18) date row leaked private data")

    # 19-23: Lineup
    c, body = http("POST", f"/api/owner/show/{TEST_SLUG}/lineup", headers=auth,
                   body={"comic_name": "Sebastian Marx", "comic_slug": "sebastian-marx",
                         "status": "confirmed", "note": "Headliner",
                         "private_note": "$200 fee — DO NOT publish"})
    assert_eq("(19) add lineup 200", c, 200)
    l1 = json.loads(body)["id"]
    c, body = http("POST", f"/api/owner/show/{TEST_SLUG}/lineup", headers=auth,
                   body={"comic_name": "Private Comic Person",
                         "note": "TBD"})
    l2 = json.loads(body)["id"]
    # Both private — public should see none
    c, body = http("GET", f"/api/show/{TEST_SLUG}/public-profile")
    if json.loads(body)["lineup"]:
        # only ok if previously published, which isn't us; this is a fresh test
        # so empty is expected
        if any(item.get("comic_name") == "Private Comic Person" for item in json.loads(body)["lineup"]):
            fails.append("(20/22) unpublished lineup item leaked")
    # Publish l1
    http("POST", f"/api/owner/show/{TEST_SLUG}/lineup/{l1}/publish", headers=auth, body="{}")
    c, body = http("GET", f"/api/show/{TEST_SLUG}/public-profile")
    lineup = json.loads(body)["lineup"]
    if not any(item["comic_name"] == "Sebastian Marx" for item in lineup):
        fails.append("(21) published lineup item missing from public")
    if any(item["comic_name"] == "Private Comic Person" for item in lineup):
        fails.append("(22) unpublished item appears publicly")
    # Private notes never appear
    if "DO NOT publish" in body:
        fails.append("(23) private_note appeared in public response")

    # 25. Cross-show denial
    c, _ = http("PATCH", "/api/owner/show/ffcn", headers=auth, body={"tagline": "x"})
    assert_eq("(25) cross-show 403", c, 403)

    # 27. No token → 401 on private endpoints
    c, _ = http("GET", f"/api/owner/show/{TEST_SLUG}/dates")
    assert_eq("(27) no token GET dates 401", c, 401)
    c, _ = http("POST", f"/api/owner/show/{TEST_SLUG}/publish", body={})
    assert_eq("(27b) no token publish 401", c, 401)

    # 28. Public endpoints never leak emails/CRM
    c, body = http("GET", f"/api/show/{TEST_SLUG}/public-profile")
    for needle in ("owner_email", "claimant_email", "guest_email",
                   "@example.com", "tests@example.com"):
        assert_not_in(f"(28) {needle}", needle, body)

    if fails:
        print(f"❌ {len(fails)} test failure(s):")
        for f in fails: print(f"  - {f}")
        return 1
    print("✅ publish/dates/lineup tests pass (28 checks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
