# -*- coding: utf-8 -*-
"""
V3 features = frozen V2 8-vector plus four intent flags.

Phase 3A (validate/phase3/phase3a_extractor.py) stays frozen for the
2026-08-10 V2 pickle. This extractor is only for models whose
n_features_in_ is 12.
"""
from __future__ import annotations

import os
import sys

_PHASE3 = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "phase3"))
if _PHASE3 not in sys.path:
    sys.path.insert(0, _PHASE3)
from phase3a_extractor import extract_features_phase3a  # noqa: E402

FEATURE_ORDER_V3 = [
    "urdu_ratio",
    "roman_ratio",
    "has_urdu",
    "has_roman",
    "query_len",
    "char_len",
    "mixed",
    "urdu_chars",
    "has_causal",
    "has_manner",
    "has_synthesis",
    "has_fact_cue",
]

# Why / reason — usually needs the article, even if the query is short.
_CAUSAL = (
    "کیوں",
    "kyun",
    "kyu",
    "why",
    "وجہ",
    "وجوہات",
    "waja",
    "wajohat",
    "reasons",
)

# How / manner — usually needs the story.
_MANNER = (
    "کیسے",
    "kaise",
    "kese",
    "how",
    "کس طرح",
    "kis tarah",
)

# Damage / review / comparison — headline is rarely enough.
_SYNTHESIS = (
    "نقصان",
    "nuksan",
    "nuqsan",
    "جائزہ",
    "jaiza",
    "موازنہ",
    "muwazna",
    "comparison",
    "تفصیل",
    "tafseel",
    "کارکردگی",
    "performance",
)

# One-fact lookup phrasing (score, rate, date, how-much-is).
_FACT = (
    "کیا ہے",
    "kya hai",
    "کتنی ہے",
    "کتنا ہے",
    "kitni hai",
    "kitna hai",
    "کب ہے",
    "kab hai",
    "کب آیا",
    "kab aaya",
    "کب لانچ",
    "kab launch",
    "کب کھیلا",
    "kab khela",
    "ریٹ کیا",
    "rate kya",
    "اسکور کیا",
    "score kya",
)


def _has_any(query: str, needles) -> int:
    q = query.lower()
    return int(any(n.lower() in q for n in needles))


def intent_flags(query: str) -> list[int]:
    return [
        _has_any(query, _CAUSAL),
        _has_any(query, _MANNER),
        _has_any(query, _SYNTHESIS),
        _has_any(query, _FACT),
    ]


def extract_features_v3(query, roman_urdu_dict) -> list:
    base = extract_features_phase3a(query, roman_urdu_dict)
    return list(base) + intent_flags(query)
