#!/usr/bin/env python3
"""
Stage 03: LLM-based comedy/venue/language classification.

Uses local Ollama (qwen2.5:32b on PC-LAPTOP via Tailscale, mirroring
brain-daemon-local-llm.py endpoint fall-through).

Falls back to keyword-based scoring if all Ollama endpoints fail.

Input:  pipeline/output/normalized.json
Output: pipeline/output/llm_classified.json
"""

import sys
import json
import re
import time
import logging
from pathlib import Path

import requests
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = REPO_ROOT / "pipeline" / "config.yml"
INPUT_PATH = REPO_ROOT / "pipeline" / "output" / "normalized.json"
OUTPUT_PATH = REPO_ROOT / "pipeline" / "output" / "llm_classified.json"

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

PROMPT_TEMPLATE = """\
Is this a comedy event in Paris? Reply JSON only, no markdown:
{{"is_comedy": bool, "confidence": 0.0-1.0, "type": "standup|openmic|improv|other", "language": "en|fr|unknown", "is_recurring": bool, "has_specific_date": bool}}

Event: {name}
Description: {description}"""


def load_config() -> dict:
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


def keyword_score(name: str, description: str, config: dict) -> dict:
    """
    Fallback scoring when Ollama is unavailable.
    Uses comedy_signals from config.yml.
    """
    signals = config.get("comedy_signals", {})
    include = [s.lower() for s in signals.get("include", [])]
    exclude = [s.lower() for s in signals.get("exclude", [])]

    text = f"{name} {description}".lower()

    include_hits = [s for s in include if s in text]
    exclude_hits = [s for s in exclude if s in text]

    if exclude_hits:
        return {
            "is_comedy": False,
            "confidence": 0.10,
            "type": "other",
            "language": "unknown",
            "is_recurring": False,
            "has_specific_date": False,
            "_method": "keyword_fallback",
            "_exclude_hits": exclude_hits,
        }

    if not include_hits:
        return {
            "is_comedy": False,
            "confidence": 0.20,
            "type": "other",
            "language": "unknown",
            "is_recurring": False,
            "has_specific_date": False,
            "_method": "keyword_fallback",
        }

    confidence = min(0.75, 0.40 + len(include_hits) * 0.08)

    # Detect type
    ev_type = "standup"
    if any(s in text for s in ["open mic", "openmic", "open-mic"]):
        ev_type = "openmic"
    elif "improv" in text:
        ev_type = "improv"

    # Language detection
    fr_signals = ["rire", "comédie", "comique", "humour", "billet", "soirée"]
    en_signals = ["standup", "stand-up", "comedy", "comedian", "open mic", "showcase"]
    has_fr = any(s in text for s in fr_signals)
    has_en = any(s in text for s in en_signals)
    # Every Paris show is EITHER French OR English — there is no "bilingual" (Robert, hard rule).
    # Ambiguous (both signals) => "unknown"; the API serializer collapses unknown -> fr (default).
    if has_fr and has_en:
        language = "unknown"
    elif has_fr:
        language = "fr"
    elif has_en:
        language = "en"
    else:
        language = "unknown"

    return {
        "is_comedy": True,
        "confidence": round(confidence, 3),
        "type": ev_type,
        "language": language,
        "is_recurring": False,
        "has_specific_date": False,
        "_method": "keyword_fallback",
        "_include_hits": include_hits,
    }


def call_ollama(endpoint: str, model: str, prompt: str, timeout: int) -> dict | None:
    """Call Ollama /api/generate. Returns parsed JSON dict or None."""
    try:
        resp = requests.post(
            f"{endpoint}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=timeout,
        )
        resp.raise_for_status()
        raw_response = resp.json().get("response", "")
        # Strip markdown code fences if model wraps in ```json
        raw_response = re.sub(r"^```(?:json)?\s*", "", raw_response.strip())
        raw_response = re.sub(r"```\s*$", "", raw_response)
        return json.loads(raw_response)
    except Exception as exc:
        log.debug(f"[LLM] {endpoint} failed: {exc}")
        return None


def classify_event(ev: dict, config: dict) -> dict:
    """Run LLM classification for a single event. Falls back to keywords."""
    llm_cfg = config.get("llm", {})
    model = llm_cfg.get("model", "qwen2.5:32b")
    fallback_model = llm_cfg.get("fallback_model", "mistral:7b")
    endpoints = llm_cfg.get("endpoints", ["http://localhost:11434"])
    timeout = llm_cfg.get("timeout_seconds", 30)

    name = ev.get("name") or ""
    description = (ev.get("description") or "")[:300]
    prompt = PROMPT_TEMPLATE.format(name=name, description=description)

    # Try each endpoint, then fallback model
    for endpoint in endpoints:
        result = call_ollama(endpoint, model, prompt, timeout)
        if result:
            result["_method"] = f"ollama:{model}@{endpoint}"
            return result

    # Try fallback model on first responsive endpoint
    for endpoint in endpoints:
        result = call_ollama(endpoint, fallback_model, prompt, timeout)
        if result:
            result["_method"] = f"ollama:{fallback_model}@{endpoint}"
            return result

    # All Ollama endpoints failed — keyword fallback
    log.warning(f"[LLM] All endpoints failed for '{name}' — using keyword fallback")
    return keyword_score(name, description, config)


def main():
    if not INPUT_PATH.exists():
        log.error(f"[LLM] Input not found: {INPUT_PATH}. Run stage 02 first.")
        sys.exit(1)

    with open(INPUT_PATH) as f:
        events = json.load(f)

    config = load_config()
    log.info(f"[LLM] Classifying {len(events)} events")

    llm_endpoint_list = config.get("llm", {}).get("endpoints", [])
    log.info(f"[LLM] Endpoints: {llm_endpoint_list}")

    results = []
    ollama_hits = 0
    keyword_hits = 0

    for i, ev in enumerate(events):
        cls = classify_event(ev, config)
        method = cls.get("_method", "unknown")
        if "ollama" in method:
            ollama_hits += 1
        else:
            keyword_hits += 1

        ev_out = {**ev}
        ev_out["is_comedy"] = cls.get("is_comedy", False)
        ev_out["confidence"] = float(cls.get("confidence", 0.0))
        ev_out["type"] = cls.get("type", "other")
        ev_out["language"] = cls.get("language", "unknown")
        ev_out["is_recurring"] = cls.get("is_recurring", False)
        ev_out["has_specific_date"] = cls.get("has_specific_date", ev.get("has_specific_date", False))
        ev_out["_llm_method"] = method
        results.append(ev_out)

        if (i + 1) % 10 == 0:
            log.info(f"[LLM] Progress: {i+1}/{len(events)}")

        # Small delay to avoid hammering Ollama
        time.sleep(0.1)

    log.info(
        f"[LLM] Done: {ollama_hits} via Ollama, {keyword_hits} via keyword fallback"
    )

    with open(OUTPUT_PATH, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    log.info(f"[LLM] Written to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
