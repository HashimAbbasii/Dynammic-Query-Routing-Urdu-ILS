# -*- coding: utf-8 -*-
"""R2-NG3 character 3-gram features. Query-independent. n is fixed at 3.

Trigrams are generated independently inside each existing token (policy A).
Tokens shorter than 3 characters are kept as a single feature.
"""
from __future__ import annotations

N = 3


def char3_grams(token: str) -> list[str]:
    """Overlapping character 3-grams of one lowercase token."""
    if not token:
        return []
    if len(token) < N:
        return [token]
    return [token[i : i + N] for i in range(0, len(token) - N + 1)]


def expand_tokens(tokens: list[str]) -> list[str]:
    """Bag of 3-gram/short features for a tokenized document or query."""
    out: list[str] = []
    for t in tokens:
        out.extend(char3_grams(t))
    return out


def feature_set(tokens: list[str]) -> set[str]:
    return set(expand_tokens(tokens))
