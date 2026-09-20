# -*- coding: utf-8 -*-
"""3-way Reciprocal Rank Fusion for ULTRA v2 PHASE8-3WAY-RRF.

Frozen: k=60 (same as Phase 4), 1-based ranks, missing list contributes 0.
Tie-break: higher RRF score, then smaller document id.
"""
from __future__ import annotations

RRF_K = 60
TOP_K = 50


def rrf_contrib(rank: int | None, k: int = RRF_K) -> float:
    if rank is None:
        return 0.0
    return 1.0 / (k + int(rank))


def rrf_score(
    rank_bm25: int | None,
    rank_dense: int | None,
    rank_ng3: int | None,
    k: int = RRF_K,
) -> float:
    return rrf_contrib(rank_bm25, k) + rrf_contrib(rank_dense, k) + rrf_contrib(rank_ng3, k)


def fuse_rrf_3(
    bm25_hits: list[tuple[int, float]],
    dense_hits: list[tuple[int, float]],
    ng3_hits: list[tuple[int, float]],
    k: int = RRF_K,
) -> list[tuple[int, float, int | None, int | None, int | None]]:
    """Union of three ranked lists → (doc_id, rrf, bm25_rank, dense_rank, ng3_rank)."""
    bm25_rank = {int(did): i for i, (did, _s) in enumerate(bm25_hits, 1)}
    dense_rank = {int(did): i for i, (did, _s) in enumerate(dense_hits, 1)}
    ng3_rank = {int(did): i for i, (did, _s) in enumerate(ng3_hits, 1)}
    union = set(bm25_rank) | set(dense_rank) | set(ng3_rank)
    rows = []
    for did in union:
        rb = bm25_rank.get(did)
        rd = dense_rank.get(did)
        rn = ng3_rank.get(did)
        rows.append((did, rrf_score(rb, rd, rn, k=k), rb, rd, rn))
    rows.sort(key=lambda t: (-t[1], t[0]))
    return rows


def gold_fused_rank(
    fused: list[tuple[int, float, int | None, int | None, int | None]],
    gold_id: int,
) -> tuple[int, float | None]:
    g = int(gold_id)
    for i, (did, score, _rb, _rd, _rn) in enumerate(fused, 1):
        if did == g:
            return i, float(score)
    return 999, None
