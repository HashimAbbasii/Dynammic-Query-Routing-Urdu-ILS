# -*- coding: utf-8 -*-
"""Configuration for generic Roman Urdu surface-form normalization (Module 1).

This module is a candidate intervention. It does not retrieve, and it does not
claim retrieval improvement. Nontrivial layers default to off.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NormalizationConfig:
    """Independently switchable layers for future ablation.

    Defaults keep Layer A (cleanup) on and Layers B–C off. Layer C
    (vowel/surface mapping) is intentionally unimplemented: the flag exists
    so a later experiment can turn it on only after a separate scientific
    justification. Enabling it currently records a skip and leaves text
    unchanged at that layer.
    """

    unicode_nfkc: bool = True
    lowercase: bool = True
    whitespace: bool = True
    punctuation_spacing: bool = True
    repeated_character_normalization: bool = False
    vowel_normalization: bool = False

    # Collapse ASCII letter runs of this length or longer down to
    # (max_identical_letter_run) copies. Only used when
    # repeated_character_normalization is True. 3 → 2 is conservative:
    # "good" / "book" are unchanged; "soooo" becomes "soo".
    min_run_to_collapse: int = 3
    max_identical_letter_run: int = 2
