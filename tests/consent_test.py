#!/usr/bin/env python3
"""
Regression test for the GA/analytics consent gate on pariscomedy.com.

Confirmed defect (Codex, 2026-09-23): the live /assets/track.js loaded
Google's gtag.js and fired a GA4 'config' call unconditionally, on every
page load, with no consent gate — contradicting privacy.html's own claim
of consent-gated analytics.

This script drives a real headless Chromium (Playwright) against:
  (a) the local worktree, served over plain HTTP, for the four consent
      states (unset / rejected / accepted / accepted-then-withdrawn), and
  (b) the LIVE production site, read-only, in the unset state only, to
      prove the live defect still exists.

Every tracker request (googletagmanager.com, google-analytics.com, or any
other tracker/pixel host) is intercepted via page.route(...).abort() so
nothing is ever actually sent anywhere — this script counts *attempts*,
it never lets a real request reach a tracker, live or local.

Usage:
    /path/to/venv/bin/python tests/consent_test.py --base-url http://127.0.0.1:PORT
    /path/to/venv/bin/python tests/consent_test.py --live-only
"""
import argparse
import sys
from playwright.sync_api import sync_playwright

TRACKER_HOST_SUBSTRINGS = (
    "googletagmanager.com",
    "google-analytics.com",
    "analytics.google.com",
    "doubleclick.net",
    "facebook.net",
    "connect.facebook.net",
    "hotjar.com",
    "clarity.ms",
    "mixpanel.com",
    "segment.io",
    "segment.com",
)


def is_tracker_request(url: str) -> bool:
    return any(h in url for h in TRACKER_HOST_SUBSTRINGS)


def run_state(page, context, base_url, state):
    """
    state: one of 'unset', 'rejected', 'accepted', 'withdrawn'
    Returns (tracker_request_count, cookies_after, localstorage_after)
    """
    tracker_hits = []

    def route_handler(route):
        if is_tracker_request(route.request.url):
            tracker_hits.append(route.request.url)
            route.abort()
        else:
            route.continue_()

    context.route("**/*", route_handler)

    context.clear_cookies()
    page.goto(base_url + "/", wait_until="networkidle", timeout=30000)

    # Clear any localStorage left from a previous state in this context.
    page.evaluate("() => { try { localStorage.clear(); } catch (e) {} }")
    page.reload(wait_until="networkidle", timeout=30000)

    if state == "unset":
        pass  # do nothing — banner should show, no consent choice made
    elif state == "rejected":
        page.evaluate("() => { if (window.PCConsent) window.PCConsent.deny(); }")
        page.wait_for_timeout(300)
    elif state == "accepted":
        page.evaluate("() => { if (window.PCConsent) window.PCConsent.grant(); }")
        page.wait_for_timeout(500)
    elif state == "withdrawn":
        page.evaluate("() => { if (window.PCConsent) window.PCConsent.grant(); }")
        page.wait_for_timeout(500)
        tracker_hits.clear()  # only count post-withdrawal attempts
        page.evaluate("() => { if (window.PCConsent) window.PCConsent.deny(); }")
        page.wait_for_timeout(300)
        # Reload to prove no GA re-fires on a fresh page load after withdrawal.
        page.reload(wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(300)
    else:
        raise ValueError(state)

    cookies = context.cookies()
    ga_cookies = [c["name"] for c in cookies if c["name"].startswith("_ga")]
    local_storage = page.evaluate(
        "() => { try { return JSON.stringify(localStorage); } catch(e) { return '{}'; } }"
    )

    context.unroute("**/*", route_handler)
    return len(tracker_hits), tracker_hits, ga_cookies, local_storage


def test_local(base_url):
    print(f"\n=== LOCAL worktree: {base_url} ===")
    results = {}
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for state in ("unset", "rejected", "accepted", "withdrawn"):
            context = browser.new_context()
            page = context.new_page()
            count, hits, ga_cookies, ls = run_state(page, context, base_url, state)
            results[state] = count
            print(f"  state={state:10s} tracker_requests={count} ga_cookies={ga_cookies} localStorage={ls}")
            if hits:
                for h in hits:
                    print(f"      blocked attempt: {h}")
            context.close()
        browser.close()

    failures = []
    if results["unset"] != 0:
        failures.append(f"unset state fired {results['unset']} tracker request(s), expected 0")
    if results["rejected"] != 0:
        failures.append(f"rejected state fired {results['rejected']} tracker request(s), expected 0")
    if results["accepted"] < 1:
        failures.append(f"accepted state fired {results['accepted']} tracker request(s), expected >=1 (GA should load)")
    if results["withdrawn"] != 0:
        failures.append(f"withdrawn state fired {results['withdrawn']} tracker request(s) after re-denying, expected 0")

    return results, failures


def test_live(live_url):
    print(f"\n=== LIVE site (read-only, unset state only): {live_url} ===")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()
        page = context.new_page()
        count, hits, ga_cookies, ls = run_state(page, context, live_url, "unset")
        print(f"  state=unset      tracker_requests={count} ga_cookies={ga_cookies} localStorage={ls}")
        for h in hits:
            print(f"      blocked attempt (would have fired live): {h}")
        context.close()
        browser.close()
    return count


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default=None, help="Local worktree base URL, e.g. http://127.0.0.1:8123")
    ap.add_argument("--live-url", default="https://pariscomedy.com", help="Live site base URL")
    ap.add_argument("--live-only", action="store_true", help="Only run the live-site read-only check")
    ap.add_argument("--local-only", action="store_true", help="Only run the local worktree checks")
    args = ap.parse_args()

    exit_code = 0

    if not args.live_only:
        if not args.base_url:
            print("ERROR: --base-url is required unless --live-only is given", file=sys.stderr)
            sys.exit(2)
        results, failures = test_local(args.base_url)
        if failures:
            exit_code = 1
            print("\nLOCAL FAIL:")
            for f in failures:
                print(f"  - {f}")
        else:
            print("\nLOCAL PASS: unset=0, rejected=0, accepted>=1, withdrawn=0 tracker requests, as expected.")

    if not args.local_only:
        live_count = test_live(args.live_url)
        print(f"\nLIVE unset-state tracker attempt count: {live_count}")
        if live_count > 0:
            print("LIVE CONFIRMS DEFECT: tracker fired before any consent choice was made.")
        else:
            print("LIVE: no tracker attempt in unset state (defect not reproduced / already fixed).")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
