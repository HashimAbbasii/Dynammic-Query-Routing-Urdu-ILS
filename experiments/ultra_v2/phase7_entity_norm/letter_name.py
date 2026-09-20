# -*- coding: utf-8 -*-
"""Query-side Latin letter-name expansion for PHASE7-LETTERNAME.

26-letter Urdu names are a public orthographic convention, not a
benchmark entity list. Romanization uses frozen Method-D naive_roman_word.
"""
from __future__ import annotations

import re

ACRONYM_RE = re.compile(r"^[a-z]{2,4}$")

# Frozen English-letter Urdu names (primer / Pakistani news style).
LETTER_URDU = {
    "a": "اے",
    "b": "بی",
    "c": "سی",
    "d": "ڈی",
    "e": "ای",
    "f": "ایف",
    "g": "جی",
    "h": "ایچ",
    "i": "آئی",
    "j": "جے",
    "k": "کے",
    "l": "ایل",
    "m": "ایم",
    "n": "این",
    "o": "او",
    "p": "پی",
    "q": "کیو",
    "r": "آر",
    "s": "ایس",
    "t": "ٹی",
    "u": "یو",
    "v": "وی",
    "w": "ڈبلیو",
    "x": "ایکس",
    "y": "وائی",
    "z": "زیڈ",
}


def is_acronym_token(tok: str, dict_keys: set[str]) -> bool:
    return bool(ACRONYM_RE.fullmatch(tok)) and tok not in dict_keys


def expand_token(tok: str, naive_roman_word, dict_keys: set[str]) -> list[str]:
    if not is_acronym_token(tok, dict_keys):
        return [tok]
    out = []
    for ch in tok:
        name = LETTER_URDU[ch]
        roman = naive_roman_word(name)
        if roman:
            out.append(roman)
    return out or [tok]


def expand_tokens(tokens: list[str], naive_roman_word, dict_keys: set[str]) -> tuple[list[str], int]:
    """Return expanded token list and count of source tokens that were expanded."""
    out: list[str] = []
    n_exp = 0
    for tok in tokens:
        parts = expand_token(tok, naive_roman_word, dict_keys)
        if is_acronym_token(tok, dict_keys):
            n_exp += 1
        out.extend(parts)
    return out, n_exp
