"""Substring + score search across canon lore."""
import re
from typing import List, Dict, Any

from .loader import load_canon


def _score(query: str, text: str) -> float:
    """Simple TF-IDF-ish score: occurrences / length."""
    if not text:
        return 0.0
    text_lower = text.lower()
    query_lower = query.lower().strip()
    if not query_lower:
        return 0.0
    # word match
    words = [w for w in re.split(r"\W+", query_lower) if w]
    if not words:
        return 0.0
    matches = sum(text_lower.count(w) for w in words)
    if matches == 0:
        # substring match (only if query is short)
        if len(query_lower) <= 30 and query_lower in text_lower:
            return 0.5
        return 0.0
    # normalize by length
    score = matches / max(1, len(text_lower) / 1000)
    return min(1.0, score)


def search_canon(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Return top-k canon pieces matching query, with score."""
    pieces = load_canon()
    scored = []
    for p in pieces:
        text = p.title + " " + " ".join(p.tags) + " " + p.body
        s = _score(query, text)
        if s > 0:
            scored.append({
                "name": p.name,
                "title": p.title,
                "score": round(s, 4),
                "doctrines_hit": p.doctrines_hit,
            })
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]
