"""BilletRéduc adapter — SCAFFOLD ONLY.

AUDIT-ONLY: this module does NOT perform any HTTP fetch, scrape, or import.
All public methods raise NotImplementedError so accidental invocation fails safe.

Activation requires:
  1. Operator (Robert) explicit authorization
  2. ChatGPT scope review + approval
  3. Rename `search` → `_search_impl`, add an operator wrapper that checks
     a config flag (e.g. data/source-adapters.json -> billetreduc.enabled)
  4. Dry-run test against a single fixture HTML (no network)
  5. Rate-limited live test gated behind same config flag

Until then: every entry point raises NotImplementedError with a clear message.
"""

from __future__ import annotations

BASE = "https://www.billetreduc.com"
SEARCH = BASE + "/recherche/?qry={query}"
USER_AGENT = "ParisComedyAdapter/1.0 (+https://pariscomedy.com/about.html)"
RATE_LIMIT_SECONDS = 5

_GATE_MSG = "BilletReduc adapter — pending operator authorization"


class BilletReducAdapter:
    """Scaffolded adapter. All methods are gated stubs."""

    def search(self, query):  # noqa: ARG002
        raise NotImplementedError(_GATE_MSG)

    def parse_listing(self, html):  # noqa: ARG002
        raise NotImplementedError(_GATE_MSG)

    def to_internal_record(self, listing):  # noqa: ARG002
        raise NotImplementedError(_GATE_MSG)
