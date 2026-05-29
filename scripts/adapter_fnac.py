"""AUDIT-ONLY scaffold. NO scrape, NO import. Requires operator + ChatGPT authorization before live use. See chuck_vault/.../P1_SOURCE_2_DRY_RUN_ADAPTERS.md for gate-unlock procedure."""

from __future__ import annotations

BASE = "https://www.fnacspectacles.com"
SEARCH = BASE + "/recherche/?searchtext={query}"
USER_AGENT = "ParisComedyAdapter/1.0 (+https://pariscomedy.com/about.html)"
RATE_LIMIT_SECONDS = 5

_GATE_MSG = "FNAC adapter — pending operator authorization"


class FnacAdapter:
    """Scaffolded adapter. All methods are gated stubs."""

    def search(self, query):  # noqa: ARG002
        raise NotImplementedError(_GATE_MSG)

    def parse_listing(self, html):  # noqa: ARG002
        raise NotImplementedError(_GATE_MSG)

    def to_internal_record(self, listing):  # noqa: ARG002
        raise NotImplementedError(_GATE_MSG)
