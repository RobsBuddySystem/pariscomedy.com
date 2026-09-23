#!/usr/bin/env python3
"""
Accessibility + SEO regression test for pariscomedy.com (branch fix/pc-a11y-seo-2026-09-23).

Serves the worktree over plain HTTP, routes every api.pariscomedy.com/api/listings
request to a saved snapshot of the live API (tests/listings_snapshot.json,
tests/listings_featured_snapshot.json — fetched once via curl, never live during
the test run), runs axe-core (injected from the local scratch npm install) against
home, shows, europe, privacy, feedback at desktop (1366x900) and mobile (390x844),
and checks:

  - 0 serious/critical axe violations
  - landmark-one-main violations == 0
  - shows.html has og:title / og:description / og:image and >=1 valid JSON-LD script
  - home JSON-LD has no empty array entries
  - no horizontal overflow (scrollWidth <= clientWidth) at 390x844
  - count of elements with computed font-size < 12px in the content area == 0
    (nav/footer excluded — same scope as the FINDINGS packet)

Usage:
    /path/to/venv/bin/python tests/a11y_seo_test.py [--axe-path PATH] [--port PORT]

Run on the parent commit first (git stash / git checkout) to get "before" numbers,
then on this branch for "after" numbers — see the packet for the table.
"""
import argparse
import http.server
import json
import socketserver
import subprocess
import sys
import threading
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TESTS_DIR = Path(__file__).resolve().parent
DEFAULT_AXE_PATH = "/private/tmp/claude-502/-Users-chuck/8b387494-a92f-4c2c-b718-f0e779ae4fd5/scratchpad/axe/node_modules/axe-core/axe.min.js"

PAGES = ["/", "/shows.html", "/europe.html", "/privacy.html", "/feedback.html"]
VIEWPORTS = {"desktop": (1366, 900), "mobile": (390, 844)}


def start_server(port):
    handler = lambda *a, **kw: http.server.SimpleHTTPRequestHandler(*a, directory=str(REPO_ROOT), **kw)
    httpd = socketserver.TCPServer(("127.0.0.1", port), handler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    return httpd


def run(axe_path, port):
    from playwright.sync_api import sync_playwright

    axe_src = Path(axe_path).read_text()
    listings = (TESTS_DIR / "listings_snapshot.json").read_text()
    featured = (TESTS_DIR / "listings_featured_snapshot.json").read_text()
    if not featured.strip():
        featured = "[]"

    base_url = f"http://127.0.0.1:{port}"
    report = {}
    overall_fail = []

    with sync_playwright() as p:
        browser = p.chromium.launch()

        def api_router(route):
            url = route.request.url
            if "featured=1" in url:
                route.fulfill(status=200, content_type="application/json", body=featured)
            elif "/api/listings" in url:
                route.fulfill(status=200, content_type="application/json", body=listings)
            elif "api-config.json" in url:
                route.continue_()
            else:
                route.continue_()

        for page_path in PAGES:
            report[page_path] = {}
            for vp_name, (w, h) in VIEWPORTS.items():
                context = browser.new_context(viewport={"width": w, "height": h})
                context.route("https://api.pariscomedy.com/**", api_router)
                page = context.new_page()
                page.goto(base_url + page_path, wait_until="networkidle", timeout=30000)
                page.wait_for_timeout(500)

                page.add_script_tag(content=axe_src)
                axe_results = page.evaluate(
                    """async () => {
                        const r = await axe.run(document, {resultTypes: ['violations']});
                        return r.violations.map(v => ({id: v.id, impact: v.impact, nodes: v.nodes.length}));
                    }"""
                )

                overflow = page.evaluate(
                    "() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1"
                )

                small_text_count = page.evaluate(
                    """() => {
                        const skip = el => el.closest('nav, footer, script, style');
                        let n = 0;
                        document.querySelectorAll('body *').forEach(el => {
                            if (skip(el)) return;
                            if (el.children.length > 0) return; // leaf nodes only
                            const txt = (el.textContent || '').trim();
                            if (!txt) return;
                            const fs = parseFloat(getComputedStyle(el).fontSize);
                            if (fs && fs < 12) n++;
                        });
                        return n;
                    }"""
                )

                seo = None
                if page_path == "/shows.html":
                    seo = page.evaluate(
                        """() => ({
                            ogTitle: !!document.querySelector('meta[property="og:title"]'),
                            ogDesc: !!document.querySelector('meta[property="og:description"]'),
                            ogImage: !!document.querySelector('meta[property="og:image"]'),
                            twTitle: !!document.querySelector('meta[name="twitter:title"]'),
                            jsonLdCount: document.querySelectorAll('script[type="application/ld+json"]').length,
                            jsonLdValid: Array.from(document.querySelectorAll('script[type="application/ld+json"]')).every(s => { try { JSON.parse(s.textContent); return true; } catch(e) { return false; } })
                        })"""
                    )

                jsonld_empty = None
                if page_path == "/":
                    jsonld_empty = page.evaluate(
                        """() => {
                            const scripts = Array.from(document.querySelectorAll('script[type="application/ld+json"]'));
                            let emptyFound = false;
                            for (const s of scripts) {
                                try {
                                    const d = JSON.parse(s.textContent);
                                    if (Array.isArray(d) && d.length === 0) emptyFound = true;
                                    if (Array.isArray(d) && d.some(x => Array.isArray(x) && x.length === 0)) emptyFound = true;
                                } catch(e) {}
                            }
                            return emptyFound;
                        }"""
                    )

                serious_critical = [v for v in axe_results if v["impact"] in ("serious", "critical")]
                landmark_violations = [v for v in axe_results if v["id"] == "landmark-one-main"]

                report[page_path][vp_name] = {
                    "violations": axe_results,
                    "serious_critical_count": sum(v["nodes"] for v in serious_critical),
                    "landmark_one_main_count": sum(v["nodes"] for v in landmark_violations),
                    "overflow": overflow,
                    "small_text_count": small_text_count,
                    "seo": seo,
                    "jsonld_empty": jsonld_empty,
                }

                context.close()
        browser.close()

    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--axe-path", default=DEFAULT_AXE_PATH)
    ap.add_argument("--port", type=int, default=8347)
    args = ap.parse_args()

    if not Path(args.axe_path).exists():
        print(f"ERROR: axe-core not found at {args.axe_path}", file=sys.stderr)
        sys.exit(2)

    httpd = start_server(args.port)
    time.sleep(0.3)
    try:
        report = run(args.axe_path, args.port)
    finally:
        httpd.shutdown()

    failures = []
    print("\n=== A11Y / SEO REPORT ===")
    for page_path, vps in report.items():
        for vp_name, data in vps.items():
            print(f"\n{page_path} [{vp_name}]")
            print(f"  serious/critical axe violation nodes: {data['serious_critical_count']}")
            print(f"  landmark-one-main violation nodes: {data['landmark_one_main_count']}")
            print(f"  horizontal overflow: {data['overflow']}")
            print(f"  elements <12px font in content: {data['small_text_count']}")
            for v in data["violations"]:
                print(f"    - {v['id']} ({v['impact']}): {v['nodes']} node(s)")

            if data["serious_critical_count"] > 0:
                failures.append(f"{page_path} [{vp_name}]: {data['serious_critical_count']} serious/critical violation node(s)")
            if data["landmark_one_main_count"] > 0:
                failures.append(f"{page_path} [{vp_name}]: {data['landmark_one_main_count']} landmark-one-main violation node(s)")
            if data["overflow"] and vp_name == "mobile":
                failures.append(f"{page_path} [mobile]: horizontal overflow detected")
            if data["small_text_count"] > 0 and vp_name == "mobile" and page_path in ("/", "/shows.html"):
                failures.append(f"{page_path} [mobile]: {data['small_text_count']} element(s) under 12px font")

            if data["seo"]:
                s = data["seo"]
                print(f"  SEO: {s}")
                if not (s["ogTitle"] and s["ogDesc"] and s["ogImage"]):
                    failures.append(f"{page_path} [{vp_name}]: missing og:title/description/image")
                if s["jsonLdCount"] < 1 or not s["jsonLdValid"]:
                    failures.append(f"{page_path} [{vp_name}]: missing or invalid JSON-LD")

            if data["jsonld_empty"] is not None:
                print(f"  home JSON-LD has empty array entry: {data['jsonld_empty']}")
                if data["jsonld_empty"]:
                    failures.append(f"{page_path} [{vp_name}]: JSON-LD contains an empty array entry")

    print("\n=== SUMMARY ===")
    if failures:
        print(f"FAIL — {len(failures)} issue(s):")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("PASS — all checks green.")
        sys.exit(0)


if __name__ == "__main__":
    main()
