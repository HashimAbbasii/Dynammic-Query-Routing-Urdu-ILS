# -*- coding: utf-8 -*-
"""Phase-10b: Option B with Hybrid-tail preservation (no overwrite of H[41:50]).

Only change vs frozen Phase-10 Option B: Hybrid's own ranks 41–50 are kept;
cascade fills only empty slots when |H| < 50.
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
    ra = {int(did): i for i, (did, _s) in enumerate(hits_a, 1)}
    rb = {int(did): i for i, (did, _s) in enumerate(hits_b, 1)}
    rows = []
    for did in set(ra) | set(rb):
        a = ra.get(did)
        b = rb.get(did)
        rows.append((did, rrf_score_one(a, k) + rrf_score_one(b, k), a, b))
    rows.sort(key=lambda t: (-t[1], t[0]))
    return rows


def option_b10b_fuse(
    hybrid_hits: list[tuple[int, float]],
    p9_hits: list[tuple[int, float]] | None,
    ng3_hits: list[tuple[int, float]] | None,
    triggered: bool,
    hybrid_keep: int = HYBRID_KEEP,
    cascade_slots: int = CASCADE_SLOTS,
    top_k: int = TOP_K,
) -> list[tuple[int, float]]:
    """Hybrid-first with no eviction of Hybrid's own ranks 41–50.

    Non-triggered: Hybrid Top-k unchanged.
    Triggered:
      ranks 1–hybrid_keep = H[1:keep] (untouched);
      ranks keep+1 … top_k = H's existing entries at those ranks first;
      only then fill remaining *empty* slots from RRF(P9, NG3) cascade-only
      docs (not already in the output). Never overwrite a Hybrid-occupied
      tail rank.
    """
    h_ids = [int(d) for d, _s in hybrid_hits[:top_k]]
    h_score = {int(d): float(s) for d, s in hybrid_hits[:top_k]}
    if not triggered:
        return [(d, h_score[d]) for d in h_ids[:top_k]]

    head = h_ids[:hybrid_keep]
    # Hybrid's own tail occupants — preserved (the Phase-10b correction)
    hybrid_tail = h_ids[hybrid_keep:top_k]
    out: list[tuple[int, float]] = [(d, h_score[d]) for d in head]
    out.extend((d, h_score[d]) for d in hybrid_tail)
    placed = {d for d, _ in out}

    empty_slots = top_k - len(out)
    if empty_slots > 0:
        cascade = fuse_rrf_two(p9_hits or [], ng3_hits or [], k=RRF_K)
        for did, sc, _a, _b in cascade:
            if did in placed:
                continue
            out.append((did, float(sc)))
            placed.add(did)
            if len(out) >= top_k:
                break

    # Safety pad from Hybrid if still short (should be rare)
    for did in h_ids:
        if len(out) >= top_k:
            break
        if did not in placed:
            out.append((did, h_score[did]))
            placed.add(did)
    return out[:top_k]


def gold_rank(ranked: list[tuple[int, float]], gold_id: int) -> int:
    g = int(gold_id)
    for i, (did, _s) in enumerate(ranked, 1):
        if int(did) == g:
            return i
    return 999
