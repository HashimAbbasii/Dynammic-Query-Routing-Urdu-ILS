# -*- coding: utf-8 -*-
"""Phase-10 Option B: Hybrid-first cascade fill from P9+NG3 RRF.

HYBRID_KEEP=40, CASCADE_SLOTS=10, cascade combine = RRF k=60 of P9 and NG3 only.
"""
from __future__ import annotations

RRF_K = 60
HYBRID_KEEP = 40
CASCADE_SLOTS = 10
TOP_K = 50


def rrf_score_one(rank: int | None, k: int = RRF_K) -> float:
    if rank is None:
        return 0.0
    return 1.0 / (k + int(rank))


def fuse_rrf_two(
    hits_a: list[tuple[int, float]],
    hits_b: list[tuple[int, float]],
    k: int = RRF_K,
) -> list[tuple[int, float, int | None, int | None]]:
    """Two lists → (doc_id, rrf, rank_a, rank_b) sorted desc score, then doc_id."""
    ra = {int(did): i for i, (did, _s) in enumerate(hits_a, 1)}
    rb = {int(did): i for i, (did, _s) in enumerate(hits_b, 1)}
    rows = []
    for did in set(ra) | set(rb):
        a = ra.get(did)
        b = rb.get(did)
        rows.append((did, rrf_score_one(a, k) + rrf_score_one(b, k), a, b))
    rows.sort(key=lambda t: (-t[1], t[0]))
    return rows


def option_b_fuse(
    hybrid_hits: list[tuple[int, float]],
    p9_hits: list[tuple[int, float]] | None,
    ng3_hits: list[tuple[int, float]] | None,
    triggered: bool,
    hybrid_keep: int = HYBRID_KEEP,
    cascade_slots: int = CASCADE_SLOTS,
    top_k: int = TOP_K,
) -> list[tuple[int, float]]:
    """Return Top-k (doc_id, score).

    Non-triggered: Hybrid unchanged.
    Triggered: Hybrid[1:keep] then cascade-only from RRF(P9,NG3); pad from Hybrid tail.
    """
    h_ids = [int(d) for d, _s in hybrid_hits[:top_k]]
    h_score = {int(d): float(s) for d, s in hybrid_hits[:top_k]}
    if not triggered:
        return [(d, h_score[d]) for d in h_ids[:top_k]]

    head = h_ids[:hybrid_keep]
    head_set = set(head)
    cascade = fuse_rrf_two(p9_hits or [], ng3_hits or [], k=RRF_K)
    fill: list[tuple[int, float]] = []
    placed = set(head_set)
    for did, sc, _a, _b in cascade:
        if did in placed:
            continue
        fill.append((did, float(sc)))
        placed.add(did)
        if len(fill) >= cascade_slots:
            break
    if len(fill) < cascade_slots:
        for did in h_ids[hybrid_keep:top_k]:
            if did in placed:
                continue
            fill.append((did, h_score.get(did, 0.0)))
            placed.add(did)
            if len(fill) >= cascade_slots:
                break
    out = [(d, h_score[d]) for d in head]
    out.extend(fill[:cascade_slots])
    seen = {d for d, _ in out}
    for did in h_ids:
        if len(out) >= top_k:
            break
        if did not in seen:
            out.append((did, h_score[did]))
            seen.add(did)
    return out[:top_k]


def gold_rank(ranked: list[tuple[int, float]], gold_id: int) -> int:
    g = int(gold_id)
    for i, (did, _s) in enumerate(ranked, 1):
        if int(did) == g:
            return i
    return 999
