# -*- coding: utf-8 -*-
"""Isolated generic Roman Urdu surface-form normalization (Module 1).

Does not import or call M0, Method D, BM25, the freeze dictionary, or Phase 12.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

from .config import NormalizationConfig

_WS = re.compile(r"\s+")
# Split punctuation that is not a URL/email-safe connector. Hyphens inside
# tokens (COVID-19) and apostrophes (don't) are kept. Whitespace is excluded
# so Layer A whitespace remains independently switchable.
_PUNCT = re.compile(r"[^\w\s\u0600-\u06FF'-]+", re.UNICODE)
_URL = re.compile(r"https?://[^\s]+|www\.[^\s]+", re.IGNORECASE)
_EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")


@dataclass
class NormalizationResult:
    original: str
    normalized: str
    transformations: list[str] = field(default_factory=list)


def _protect(text: str) -> tuple[str, dict[str, str]]:
    """Replace URLs and emails with placeholders so later layers cannot split them."""
    table: dict[str, str] = {}

    def stash(match: re.Match[str], kind: str) -> str:
        # Alphanumeric-only placeholders with a terminator so shorter ids cannot
        # prefix-match longer ones after lowercase (url0 vs url10).
        key = f"ZXULTRAPROT{kind}{len(table)}ZX"
        table[key] = match.group(0)
        return key

    out = _URL.sub(lambda m: stash(m, "URL"), text)
    out = _EMAIL.sub(lambda m: stash(m, "EMAIL"), out)
    return out, table


def _restore(text: str, table: dict[str, str]) -> str:
    # Placeholders are ASCII letters+digits. If lowercase ran, keys may have
    # been folded; restore both the original key and its lowercased form.
    for key, value in sorted(table.items(), key=lambda kv: len(kv[0]), reverse=True):
        text = text.replace(key, value)
        lowered = key.lower()
        if lowered != key:
            text = text.replace(lowered, value)
    return text


def _collapse_letter_runs(text: str, min_run: int, max_keep: int) -> str:
    """Collapse only ASCII letter runs of length >= min_run down to max_keep.

    Digits, Urdu letters, and punctuation are not collapsed. Tokens containing
    digits are left unchanged so identifiers like 111860 stay intact.
    """
    if min_run < 3 or max_keep < 1 or max_keep >= min_run:
        raise ValueError("repeated-character settings must satisfy 1 <= max_keep < min_run and min_run >= 3")

    pattern = re.compile(rf"([a-z])\1{{{min_run - 1},}}")

    def sub_token(tok: str) -> str:
        if any(c.isdigit() for c in tok):
            return tok
        return pattern.sub(lambda m: m.group(1) * max_keep, tok)

    return " ".join(sub_token(t) for t in text.split()) if text else text


def explain_roman_urdu_normalization(
    text: str | None,
    config: NormalizationConfig | None = None,
) -> NormalizationResult:
    """Return the normalized string plus an ordered list of applied layers."""
    cfg = config or NormalizationConfig()
    original = "" if text is None else str(text)
    current = original
    steps: list[str] = []

    current, protected = _protect(current)

    if cfg.unicode_nfkc:
        nxt = unicodedata.normalize("NFKC", current)
        nxt = nxt.replace("\u200c", " ").replace("\u200d", " ")
        if nxt != current:
            steps.append("unicode_nfkc")
        current = nxt

    if cfg.lowercase:
        nxt = current.lower()
        if nxt != current:
            steps.append("lowercase")
        current = nxt

    if cfg.punctuation_spacing:
        nxt = _PUNCT.sub(" ", current)
        nxt = nxt.replace("_", " ")
        if nxt != current:
            steps.append("punctuation_spacing")
        current = nxt

    if cfg.whitespace:
        nxt = _WS.sub(" ", current).strip()
        if nxt != current:
            steps.append("whitespace")
        current = nxt

    if cfg.repeated_character_normalization:
        nxt = _collapse_letter_runs(
            current,
            min_run=cfg.min_run_to_collapse,
            max_keep=cfg.max_identical_letter_run,
        )
        if nxt != current:
            steps.append("repeated_character_normalization")
        current = nxt

    if cfg.vowel_normalization:
        # Not implemented: arbitrary vowel deletion/mapping is unsafe for mixed
        # English + Roman Urdu + names. Flag reserved for a later justified study.
        steps.append("vowel_normalization_skipped_unimplemented")

    current = _restore(current, protected)
    if cfg.whitespace:
        current = _WS.sub(" ", current).strip()

    return NormalizationResult(original=original, normalized=current, transformations=steps)


def normalize_roman_urdu(
    text: str | None,
    config: NormalizationConfig | None = None,
) -> str:
    """Deterministic generic surface-form normalization. No retrieval."""
    return explain_roman_urdu_normalization(text, config).normalized
