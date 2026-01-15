# src/fuzzy.py

import difflib
import re


def normalize(name: str) -> str:
    """
    Normalize identifiers:
    - lowercase
    - remove underscores
    - collapse repeated letters
    """
    name = name.lower()
    name = name.replace("_", "")
    name = re.sub(r"(.)\1+", r"\1", name)  # aa → a
    return name


def suggest(bad: str, candidates: list[str], cutoff: float = 0.45, top_k: int = 3):
    """
    Smart fuzzy suggestion engine.
    Returns list of best candidates.
    """

    bad_norm = normalize(bad)
    scored = []

    for cand in candidates:
        cand_norm = normalize(cand)

        # similarity score
        score = difflib.SequenceMatcher(None, bad_norm, cand_norm).ratio()

        # strong prefix bonus (emp → employee)
        if len(bad_norm) >= 3 and bad_norm[:3] == cand_norm[:3]:
            score += 0.15


        if score >= cutoff:
            scored.append((cand, score))

    scored.sort(key=lambda x: x[1], reverse=True)

    return [c for c, _ in scored[:top_k]]

