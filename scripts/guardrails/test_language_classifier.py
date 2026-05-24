#!/usr/bin/env python3
"""Tests for the strict language classifier.

Exit 0 = pass.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(
    0, str(Path.home() / "Documents/Claude/Projects/pariscomedy.com/scripts"),
)
from discovery._language_classifier import classify_language  # noqa: E402


CASES = [
    # From the user's spec
    ("English-language headline stand-up",       "en"),
    ("stand-up en anglais",                       "en"),
    ("comedy show in English",                    "en"),
    ("spectacle en français",                     "fr"),
    ("humour en français",                        "fr"),
    ("bilingual comedy night",                    "bi"),
    ("anglais et français",                       "bi"),
    ("français et anglais",                       "bi"),
    ("EN/FR comedy night",                        "bi"),
    ("",                                          "unknown"),
    ("Wednesday at 22:00 at Velvet Bar.",         "unknown"),

    # Real-world phrases from current EB descriptions
    ("English stand-up comedy in Paris every Wednesday at Velvet Bar.", "en"),
    ("Chaque mercredi à 20h30, 5/6 humoristes montent sur scène",        "unknown"),
    ("Poussez la porte du Bar Le Coquin",                                 "unknown"),
    ("International comics in English. Doors 19:30.",                     "en"),
    ("Soirée en français à Paris.",                                       "fr"),
    ("Franglais set",                                                     "bi"),
    ("English + French stand-up",                                         "bi"),

    # Substring traps — must NOT misclassify
    ("Comedy in Englishtown",                     "unknown"),  # ish — actually 'in English' matches if word boundary is loose
]


def main() -> int:
    fails: list[str] = []
    for text, expected in CASES:
        got = classify_language(text)
        if got != expected:
            fails.append(f"{text!r} → {got!r} (expected {expected!r})")
    n = len(CASES)
    if fails:
        print(f"❌ {len(fails)}/{n} failures:")
        for f in fails: print(f"  - {f}")
        return 1
    print(f"✅ {n}/{n} tests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
