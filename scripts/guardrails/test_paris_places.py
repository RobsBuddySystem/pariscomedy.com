#!/usr/bin/env python3
"""Tests for the Paris-places normalizer (scripts/discovery/_paris_places.py).

Exit 0 = pass. Exit 1 = at least one assertion failed.

Positive: every Barbès variant must classify as neighborhood='Barbès',
arrondissement=18, and the metro-bearing variants must populate
metro='Barbès-Rochechouart'.

Negative: nearby places (Pigalle, Montmartre, Anvers, Château Rouge,
La Chapelle, Gare du Nord) must NOT be misclassified as Barbès.

Also: words that contain "barb" as a substring (Barbara, barbershop,
barbecue) must never match.
"""
from __future__ import annotations
import sys
from pathlib import Path

# Allow running standalone — import the normalizer from the project scripts dir.
sys.path.insert(
    0,
    str(Path.home() / "Documents/Claude/Projects/pariscomedy.com/scripts"),
)
from discovery._paris_places import classify, fold, is_barbes  # noqa: E402


POSITIVE_BARBES = [
    ("Barbès",                          "Barbès", None,                  18),
    ("Barbes",                          "Barbès", None,                  18),
    ("BARBÈS",                          "Barbès", None,                  18),
    ("BARBES",                          "Barbès", None,                  18),
    ("Barbès-Rochechouart",             "Barbès", "Barbès-Rochechouart", 18),
    ("Barbes-Rochechouart",             "Barbès", "Barbès-Rochechouart", 18),
    ("Barbès Rochechouart",             "Barbès", "Barbès-Rochechouart", 18),
    ("Barbes Rochechouart",             "Barbès", "Barbès-Rochechouart", 18),
    ("Barbes – Rochechouart",           "Barbès", "Barbès-Rochechouart", 18),  # en dash
    ("Barbes — Rochechouart",           "Barbès", "Barbès-Rochechouart", 18),  # em dash
    ("Boulevard de Barbès",             "Barbès", None,                  18),
    ("Métro Barbès-Rochechouart",       "Barbès", "Barbès-Rochechouart", 18),
    ("Metro Barbes Rochechouart",       "Barbès", "Barbès-Rochechouart", 18),
    ("Barbes Rochechouart station",     "Barbès", "Barbès-Rochechouart", 18),
    ("Show at La Scène Barbès tonight", "Barbès", None,                  18),
]

NEGATIVE_NOT_BARBES = [
    ("Pigalle",                  "Pigalle"),
    ("Pigalle 9e",               "Pigalle"),
    ("Sacré-Cœur Montmartre",    "Montmartre"),
    ("Montmartre",               "Montmartre"),
    ("Anvers",                   "Anvers"),
    ("Métro Anvers",             "Anvers"),
    ("Château Rouge",            "Château Rouge"),
    ("La Chapelle",              "La Chapelle"),
    ("Gare du Nord",             "Gare du Nord"),
]

# Words that must NEVER match Barbès because they only share a substring.
NEGATIVE_NONE = [
    "Barbara Anderson opens for FFCN",
    "Barber shop comedy",
    "The barbershop pole",
    "barbecue food truck",
    "Barbican Centre",
    "Bayard show in Pigalle",
]


def main() -> int:
    failures: list[str] = []

    # Positive: every variant must classify as Barbès with arrondissement=18.
    for src, exp_neigh, exp_metro, exp_arr in POSITIVE_BARBES:
        got = classify(src)
        if got is None:
            failures.append(f"[+] {src!r} → None (expected Barbès)")
            continue
        if got["neighborhood"] != exp_neigh:
            failures.append(
                f"[+] {src!r} → neighborhood={got['neighborhood']!r} "
                f"(expected {exp_neigh!r})"
            )
        if got["metro"] != exp_metro:
            failures.append(
                f"[+] {src!r} → metro={got['metro']!r} (expected {exp_metro!r})"
            )
        if got["arrondissement"] != exp_arr:
            failures.append(
                f"[+] {src!r} → arrondissement={got['arrondissement']} "
                f"(expected {exp_arr})"
            )

    # Negative: nearby places must classify to their own neighborhood, NOT Barbès.
    for src, exp_neigh in NEGATIVE_NOT_BARBES:
        got = classify(src)
        if got is None:
            failures.append(f"[-] {src!r} → None (expected {exp_neigh!r})")
            continue
        if got["neighborhood"] == "Barbès":
            failures.append(
                f"[-] {src!r} → misclassified as Barbès (expected {exp_neigh!r})"
            )
        elif got["neighborhood"] != exp_neigh:
            failures.append(
                f"[-] {src!r} → {got['neighborhood']!r} (expected {exp_neigh!r})"
            )

    # Substring traps: must NEVER match anything Barbès-ish.
    for src in NEGATIVE_NONE:
        if is_barbes(src):
            failures.append(f"[!] substring trap {src!r} matched is_barbes")

    n = len(POSITIVE_BARBES) + len(NEGATIVE_NOT_BARBES) + len(NEGATIVE_NONE)
    if not failures:
        print(f"✅ {n}/{n} tests passed")
        return 0
    print(f"❌ {len(failures)} failure(s) out of {n} tests:")
    for f in failures:
        print(f"  - {f}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
