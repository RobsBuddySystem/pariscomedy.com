#!/usr/bin/env python3
"""Re-bake SHOWS_DATA in index.html + shows.html using only active shows."""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHOWS = ROOT / "data" / "shows_generated.json"

def main():
    shows = json.loads(SHOWS.read_text(encoding="utf-8"))
    active = [s for s in shows if s.get("ticket_url_status") == "active"]
    if len(active) < 10:
        print(f"REFUSE: only {len(active)} active shows (<10).", file=sys.stderr)
        sys.exit(2)
    blob = json.dumps(active, ensure_ascii=False, separators=(",", ":"))
    for fname in ("index.html", "shows.html"):
        p = ROOT / fname
        content = p.read_text(encoding="utf-8")
        new = re.sub(r"const SHOWS_DATA = \[.*?\];", f"const SHOWS_DATA = {blob};", content, flags=re.DOTALL)
        if new == content:
            print(f"WARN: no SHOWS_DATA replacement in {fname}", file=sys.stderr)
            sys.exit(3)
        p.write_text(new, encoding="utf-8")
    print(json.dumps({"baked_active": len(active), "total": len(shows)}))

if __name__ == "__main__":
    main()
