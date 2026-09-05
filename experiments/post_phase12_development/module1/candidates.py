# -*- coding: utf-8 -*-
"""Module 1 query-side transforms for ROMAN-branch retrieval only."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments" / "phase5_roman_urdu"))

from src.roman_urdu_normalization import NormalizationConfig, normalize_roman_urdu  # noqa: E402
import run_phase5 as p5  # noqa: E402

LAYER_A = NormalizationConfig(
    unicode_nfkc=True,
    lowercase=True,
    whitespace=True,
    punctuation_spacing=True,
    repeated_character_normalization=False,
    vowel_normalization=False,
)

# M1-D: Layer A + conservative repeat collapse (runs of 3+ ASCII letters → max 2).
LAYER_A_REPEAT = NormalizationConfig(
    unicode_nfkc=True,
    lowercase=True,
    whitespace=True,
    punctuation_spacing=True,
    repeated_character_normalization=True,
    min_run_to_collapse=3,
    max_identical_letter_run=2,
    vowel_normalization=False,
)

# Read-only closed alias table from frozen Phase 5 (not modified).
_VARIANT = dict(p5._VARIANT_TO_DICT_KEY)


def _layer_a(text: str) -> str:
    return normalize_roman_urdu(text, LAYER_A)


def roman_query_tokens_m1a(query_text: str, _fwd: dict | None = None) -> list[str]:
    """M1-A: conservative Layer A then M0 tokenize."""
    return p5.tokenize(_layer_a(query_text))


def roman_query_tokens_m1b(query_text: str, fwd: dict) -> list[str]:
    """M1-B / M1-C: Layer A + dict-key canonicalization (no grapheme rewrite)."""
    toks = p5.tokenize(_layer_a(query_text))
    out = []
    for tok in toks:
        key = _VARIANT.get(tok, tok)
        if key in fwd:
            out.append(key)
        elif tok in fwd:
            out.append(tok)
        else:
            out.append(tok)
    return out


def roman_query_tokens_m1d(query_text: str, _fwd: dict | None = None) -> list[str]:
    """M1-D: Layer A + repeated-character normalization (max 2 consecutive letters)."""
    return p5.tokenize(normalize_roman_urdu(query_text, LAYER_A_REPEAT))


def urdu_query_tokens(query_text: str, _fwd: dict | None = None) -> list[str]:
    """Unchanged M0 path for URDU/MIXED."""
    return p5.tokenize(query_text)


CANDIDATES: dict[str, dict] = {
    "M1-A": {
        "name": "Conservative normalization",
        "description": "Layer A: NFKC, lowercase, punctuation spacing, whitespace collapse",
        "roman_token_fn": roman_query_tokens_m1a,
        "uses_dictionary": False,
    },
    "M1-B": {
        "name": "Dictionary-assisted normalization",
        "description": "Layer A + closed _VARIANT_TO_DICT_KEY aliases + dict-key canonical forms",
        "roman_token_fn": roman_query_tokens_m1b,
        "uses_dictionary": True,
    },
    "M1-C": {
        "name": "Conservative + dictionary",
        "description": "Same as M1-B (Layer A plus read-only 198-key dictionary aliases)",
        "roman_token_fn": roman_query_tokens_m1b,
        "uses_dictionary": True,
    },
    "M1-D": {
        "name": "Layer A + repeated-character normalization",
        "description": (
            "Layer A plus collapse ASCII letter runs of 3+ to max 2 "
            "(NormalizationConfig repeated_character_normalization=True)"
        ),
        "roman_token_fn": roman_query_tokens_m1d,
        "uses_dictionary": False,
    },
}


def get_roman_token_fn(candidate_id: str) -> Callable[[str, dict | None], list[str]]:
    if candidate_id not in CANDIDATES:
        raise KeyError(candidate_id)
    return CANDIDATES[candidate_id]["roman_token_fn"]
