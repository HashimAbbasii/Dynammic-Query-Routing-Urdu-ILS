# -*- coding: utf-8 -*-
"""
Decision layer that replaces ULTRA's static character threshold (θ=150).

This module only *chooses* HEADLINE vs FULL_CONTENT. It does not search.
The deployed V2 SVM (models/svm_classifier.pkl + scaler.pkl) is the
learned router. Word-count and θ=150 are comparison baselines that
drive the *same* two indexes.
"""
from __future__ import annotations

import os
import pickle
import sys

import numpy as np

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "validate", "phase3"))
from phase3a_extractor import extract_features_phase3a, load_roman_dict  # noqa: E402

WORDCOUNT_LONG_MIN = 6  # frozen Phase 3B rule: >= 6 words -> LONG
THETA_CHAR = 150  # ULTRA static character threshold
HEADLINE = "HEADLINE"
FULL_CONTENT = "FULL_CONTENT"
HYBRID = "HYBRID"

# Thesis confidence bands (Section 3.5): not fitted on eval data.
HIGH_MIN = 85.0
MEDIUM_MIN = 60.0


def confidence_tier(confidence) -> str | None:
    """GREEN / YELLOW / RED lights. None if the system has no confidence."""
    if confidence is None:
        return None
    c = float(confidence)
    if c >= HIGH_MIN:
        return "HIGH"
    if c >= MEDIUM_MIN:
        return "MEDIUM"
    return "LOW"

_svm = None
_scaler = None
_roman_dict = None


def _load_v2():
    global _svm, _scaler, _roman_dict
    if _svm is not None:
        return _svm, _scaler, _roman_dict
    scaler_path = os.path.join(REPO_ROOT, "models", "scaler.pkl")
    svm_path = os.path.join(REPO_ROOT, "models", "svm_classifier.pkl")
    with open(scaler_path, "rb") as f:
        _scaler = pickle.load(f)
    with open(svm_path, "rb") as f:
        _svm = pickle.load(f)
    _roman_dict = load_roman_dict()
    return _svm, _scaler, _roman_dict


def word_count_label(query: str) -> str:
    n = len(query.split())
    return "LONG" if n >= WORDCOUNT_LONG_MIN else "SHORT"


def theta150_label(query: str) -> str:
    return "LONG" if len(query) >= THETA_CHAR else "SHORT"


def svm_v2_label(query: str) -> tuple[str, float]:
    svm, scaler, roman = _load_v2()
    feats = extract_features_phase3a(query, roman)
    Xt = scaler.transform(np.array([feats]))
    pred = str(svm.predict(Xt)[0]).upper()
    if pred not in ("SHORT", "LONG"):
        pred = "LONG" if pred in ("1", "LONG") else "SHORT"
    conf = float(np.max(svm.predict_proba(Xt)[0])) * 100.0
    return pred, conf


def label_to_mode(label: str) -> str:
    return FULL_CONTENT if str(label).upper() == "LONG" else HEADLINE


def decide(query: str, system: str) -> dict:
    """
    system: svm_v2 | wordcount | theta150 | always_headline | always_full
    """
    system = system.lower()
    if system == "always_headline":
        label, conf = "SHORT", None
    elif system == "always_full":
        label, conf = "LONG", None
    elif system == "wordcount":
        label, conf = word_count_label(query), None
    elif system == "theta150":
        label, conf = theta150_label(query), None
    elif system == "svm_v2":
        label, conf = svm_v2_label(query)
    else:
        raise ValueError(f"unknown system: {system}")
    tier = confidence_tier(conf)
    return {
        "system": system,
        "label": label,
        "mode": label_to_mode(label),
        "confidence": conf,
        "tier": tier,
        "word_count": len(query.split()),
        "char_len": len(query),
    }
