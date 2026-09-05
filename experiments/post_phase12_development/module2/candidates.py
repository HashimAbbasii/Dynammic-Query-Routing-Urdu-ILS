# -*- coding: utf-8 -*-
"""
Module 2 candidate definitions (pre-specified).

M2-A: char_wb 3-gram BM25
M2-B: headline + body word BM25 fused with RRF(k=60)

Does not modify M0, Method D, dictionary, or Module 1.
Does not stack Module 1 transforms.
"""
from __future__ import annotations

from collections import defaultdict

from sklearn.feature_extraction.text import TfidfVectorizer

# Fixed parameters — do not change after seeing results.
BM25_K1 = 1.5
BM25_B = 0.75
TOP_K = 50
RRF_K = 60
CHAR_NGRAM = (3, 3)

_CHAR_ANALYZER = None


def char_wb_3gram_analyzer():
    """Deterministic char_wb 3-gram analyzer (sklearn TfidfVectorizer)."""
    global _CHAR_ANALYZER
    if _CHAR_ANALYZER is None:
        _CHAR_ANALYZER = TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=CHAR_NGRAM,
        ).build_analyzer()
    return _CHAR_ANALYZER


def char_wb_3grams(text: str) -> list[str]:
    return char_wb_3gram_analyzer()(text or "")


def rrf_fuse(ranked_lists, k: int = RRF_K, top_k: int = TOP_K):
    """
    Reciprocal Rank Fusion.

    ranked_lists: iterable of lists of (doc_id, score) already sorted best-first.
    score(d) = sum_c 1/(k + rank_c(d)) for channels containing d.
    Tie-break: higher RRF score first; if equal, lower doc_id.
    """
    scores = defaultdict(float)
    for hits in ranked_lists:
        for rank, (did, _s) in enumerate(hits, 1):
            scores[int(did)] += 1.0 / (k + rank)
    ranked = sorted(scores.items(), key=lambda x: (-x[1], x[0]))
    return [(int(did), float(sc)) for did, sc in ranked[:top_k]]


CANDIDATES = {
    "M2-A": {
        "name": "Character 3-gram BM25",
        "description": (
            "char_wb 3-gram tokens via sklearn TfidfVectorizer analyzer; "
            "BM25 k1=1.5 b=0.75; M0 routing; Method D document romanization unchanged"
        ),
        "params": {
            "analyzer": "char_wb",
            "ngram_range": [3, 3],
            "bm25_k1": BM25_K1,
            "bm25_b": BM25_B,
            "top_k": TOP_K,
        },
    },
    "M2-B": {
        "name": "Headline + body BM25 RRF",
        "description": (
            "Word BM25 on Headline and News Text separately; "
            "RRF k=60; BM25 k1=1.5 b=0.75; M0 routing; Method D unchanged"
        ),
        "params": {
            "headline_field": "Headline",
            "body_field": "News Text",
            "tokenization": "run_phase5.tokenize / romanize_token",
            "bm25_k1": BM25_K1,
            "bm25_b": BM25_B,
            "rrf_k": RRF_K,
            "per_channel_top_k": TOP_K,
            "top_k": TOP_K,
            "tie_break": "higher RRF then lower doc_id",
        },
    },
}
