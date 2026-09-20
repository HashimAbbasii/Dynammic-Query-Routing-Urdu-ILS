# -*- coding: utf-8 -*-
"""R2-1 document-side fallback romanizer.

Name: hunterian_ascii_positional_v1
Scope: Urdu-script tokens that Method D would send to naive_roman_word.
Not used for reverse-dictionary hits. Not used on queries.

Scheme: ASCII folding of Hunterian / common Urdu romanization conventions
for matres lectionis, applied per token with no lexicon and no benchmark IDs.

و (waw) is both a consonant /w/ (typical token-initially) and a vowel /o~u/
(typical after a consonant). Method D maps every و to 'o', which is the
R2-C0-identified consonant loss. This romanizer uses position:

- token-initial و → w
- non-initial و → o

ی (ye) is both a consonant /j/ (typical token-initially) and a vowel /i/:

- token-initial ی/ئ → y
- non-initial ی/ئ → i

All other letters use the same closed ASCII inventory as Method D's
_CHAR_ROMAN (no diacritics, no short-vowel insertion). Unwritten short
vowels are not invented; that would require a lexicon (forbidden here).

This module must remain query-independent. Do not add benchmark query IDs
or example query strings.
"""
from __future__ import annotations

from typing import Dict

ROMANIZER_NAME = "hunterian_ascii_positional_v1"
ROMANIZER_VERSION = "1.0.0"

# Closed inventory. Identical to Method D except و/ی/ئ are handled in code.
_CHAR: Dict[str, str] = {
    "ا": "a",
    "آ": "aa",
    "ب": "b",
    "پ": "p",
    "ت": "t",
    "ٹ": "t",
    "ث": "s",
    "ج": "j",
    "چ": "ch",
    "ح": "h",
    "خ": "kh",
    "د": "d",
    "ڈ": "d",
    "ذ": "z",
    "ر": "r",
    "ڑ": "r",
    "ز": "z",
    "ژ": "zh",
    "س": "s",
    "ش": "sh",
    "ص": "s",
    "ض": "z",
    "ط": "t",
    "ظ": "z",
    "ع": "a",
    "غ": "gh",
    "ف": "f",
    "ق": "q",
    "ک": "k",
    "گ": "g",
    "ل": "l",
    "م": "m",
    "ن": "n",
    "ں": "n",
    "ہ": "h",
    "ھ": "h",
    "ء": "",
    "ے": "e",
    "ؤ": "o",
    "أ": "a",
    "إ": "i",
    "ة": "h",
}

_WAW = "و"
_YE = {"ی", "ئ"}


def fallback_roman(token: str) -> str:
    """Deterministic ASCII romanization of one Urdu-script token."""
    if not token:
        return ""
    buf: list[str] = []
    for i, ch in enumerate(token):
        if ch == _WAW:
            buf.append("w" if i == 0 else "o")
        elif ch in _YE:
            buf.append("y" if i == 0 else "i")
        elif ch in _CHAR:
            buf.append(_CHAR[ch])
        elif ch.isascii() and ch.isalnum():
            buf.append(ch)
    return "".join(buf).lower()


def romanizer_config() -> dict:
    return {
        "name": ROMANIZER_NAME,
        "version": ROMANIZER_VERSION,
        "scheme": "Hunterian/ASCII positional matres lectionis",
        "waw_initial": "w",
        "waw_non_initial": "o",
        "ye_initial": "y",
        "ye_non_initial": "i",
        "short_vowel_insertion": False,
        "diacritics": False,
        "lexicon": False,
        "query_dependent": False,
    }
