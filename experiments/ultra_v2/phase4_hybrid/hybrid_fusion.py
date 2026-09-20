# -*- coding: utf-8 -*-
"""Reciprocal Rank Fusion for ULTRA v2 HYBRID-RRF.

Frozen: k=60, 1-based ranks, missing list contributes 0.
Tie-break: higher RRF score, then smaller document id.
"""
from __future__ import annotations

RRF_K = 60
TOP_K = 50


def rrf_score(rank_bm25: int | None, rank_dense: int | None, k: int = RRF_K) -> float:
    s = 0.0
    if rank_bm25 is not None:
        s += 1.0 / (k + int(rank_bm25))
    if rank_dense is not None:
        s += 1.0 / (k + int(rank_dense))
    return s


def fuse_rrf(
    bm25_hits: list[tuple[int, float]],
    dense_hits: list[tuple[int, float]],
    k: int = RRF_K,
) -> list[tuple[int, float, int | None, int | None]]:
    """Union of two ranked lists → (doc_id, rrf, bm25_rank, dense_rank) sorted."""
    bm25_rank = {int(did): i for i, (did, _s) in enumerate(bm25_hits, 1)}
    dense_rank = {int(did): i for i, (did, _s) in enumerate(dense_hits, 1)}
    union = set(bm25_rank) | set(dense_rank)
    rows = []
    for did in union:
        rb = bm25_rank.get(did)
        rd = dense_rank.get(did)
        rows.append((did, rrf_score(rb, rd, k=k), rb, rd))
    rows.sort(key=lambda t: (-t[1], t[0]))
    return rows


def gold_fused_rank(
    fused: list[tuple[int, float, int | None, int | None]],
    gold_id: int,
) -> tuple[int, float | None]:
    g = int(gold_id)
    for i, (did, score, _rb, _rd) in enumerate(fused, 1):
        if did == g:
            return i, float(score)
    return 999, None
