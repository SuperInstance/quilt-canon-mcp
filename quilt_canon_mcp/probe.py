"""Probe lore via JEV-style oracle (heuristic local, optional cloud).

If DEEPINFRA_TOKEN is set, calls the DeepInfra Llama-3.3-70B model.
Otherwise falls back to a deterministic local heuristic that mimics
the JEV composite scoring.
"""
import hashlib
import os
from typing import Any, Dict

from .loader import DOCTRINES


def _local_probe(lore_text: str) -> Dict[str, Any]:
    """Deterministic local JEV-mimic probe. Same input → same composite."""
    if not lore_text:
        return {"composite": 0.0, "doctrines_hit": [], "distinct_voice": False}

    text_lower = lore_text.lower()
    length = len(lore_text)
    # Doctrines hit
    doctrines_hit = []
    keywords = {
        "cells_are_scars": ["scar", "scars", "cell is", "cells are"],
        "witness_log_is_prediction": ["witness log", "witness-log"],
        "canon_gate_is_chord": ["chord", "canon gate", "consensus"],
        "oracle_is_heard": ["oracle", "heard", "jev"],
        "substrate_quantum": ["quantum", "substrate", "walker"],
    }
    for d in DOCTRINES:
        for kw in keywords.get(d, [d]):
            if kw in text_lower:
                doctrines_hit.append(d)
                break

    # Composite: doctrine anchor + length + diversity
    doctrine_score = len(doctrines_hit) / max(1, len(DOCTRINES))
    length_score = min(1.0, length / 1000.0) if length > 100 else 0.0
    # Distinct voice: long enough + has anchors
    distinct_voice = length > 200 and len(doctrines_hit) >= 2

    composite = 0.4 * doctrine_score + 0.3 * length_score + 0.3 * (1.0 if distinct_voice else 0.0)

    return {
        "composite": round(composite, 3),
        "doctrines_hit": doctrines_hit,
        "distinct_voice": distinct_voice,
        "canon_worthy": composite >= 0.5,
        "probe_source": "local_heuristic",
    }


def _deepinfra_probe(lore_text: str, token: str) -> Dict[str, Any]:
    """Call DeepInfra Llama-3.3-70B for real JEV-style probe.

    Falls back to local if call fails.
    """
    try:
        import urllib.request
        import json as jsonlib

        prompt = f"""Rate the following canon lore on a scale of 0.0 to 1.0.

LORE:
\"\"\"{lore_text[:2000]}\"\"\"

Consider:
1. Does it anchor to canon doctrines (cells_are_scars, witness_log_is_prediction, canon_gate_is_chord, oracle_is_heard, substrate_quantum)?
2. Does it have a distinct voice?
3. Is it canon-worthy?

Respond ONLY with a JSON object: {{"composite": <float>, "doctrines_hit": [<list>], "distinct_voice": <bool>, "canon_worthy": <bool>}}"""

        req = urllib.request.Request(
            "https://api.deepinfra.com/v1/openai/chat/completions",
            data=jsonlib.dumps({
                "model": "meta-llama/Llama-3.3-70B-Instruct",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 200,
            }).encode(),
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = jsonlib.loads(resp.read().decode())
        content = data["choices"][0]["message"]["content"].strip()
        # Try to parse as JSON
        try:
            result = jsonlib.loads(content)
            result["probe_source"] = "deepinfra"
            return result
        except Exception:
            # Fallback
            local = _local_probe(lore_text)
            local["probe_source"] = "deepinfra_fallback_to_local"
            return local
    except Exception:
        return _local_probe(lore_text)


def probe_lore(lore_text: str) -> Dict[str, Any]:
    """Probe lore text. Uses DeepInfra if DEEPINFRA_TOKEN set, else local."""
    token = os.environ.get("DEEPINFRA_TOKEN")
    if token:
        return _deepinfra_probe(lore_text, token)
    return _local_probe(lore_text)
