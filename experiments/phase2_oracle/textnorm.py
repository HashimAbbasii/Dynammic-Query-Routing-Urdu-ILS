# -*- coding: utf-8 -*-
"""Query normalization for leakage checks. Do not use for retrieval."""
from __future__ import annotations

import re
import unicodedata

_WS = re.compile(r"\s+")
_PUNCT = re.compile(r"[^\w\u0600-\u06FF]+", re.UNICODE)


def normalize_query(text: str) -> str:
    s = unicodedata.normalize("NFKC", str(text or "")).strip().lower()
    s = s.replace("\u200c", " ").replace("\u200d", " ")
    s = _PUNCT.sub(" ", s)
    s = _WS.sub(" ", s).strip()
    return s


def token_set(text: str) -> set[str]:
    n = normalize_query(text)
    return {t for t in n.split(" ") if t}


def jaccard(a: str, b: str) -> float:
    sa, sb = token_set(a), token_set(b)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)
