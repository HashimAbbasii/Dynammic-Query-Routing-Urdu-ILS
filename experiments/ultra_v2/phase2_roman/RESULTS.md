# ULTRA v2 Phase 2 results (development only)

**Label:** ULTRA v2 development experiment. **Not a PLOS result.**  
**Date:** 2026-09-09  
**Splits:** TRAIN + DEV KN only. **TEST not used.**  
**NL:** pending official pooled annotation (no qrels).

Seal at run time: `48610601209c3723a7252bb9a197d8fbbece18640e0bf7aef972884816ab46c4` (MATCH).

---

## Configuration (all experiments)

| Item | Value |
| --- | --- |
| System | Frozen M0 imported from `run_phase5.py` (not edited) |
| Routing | Unicode detector; ROMAN → Method D; else Urdu BM25 |
| Dictionary | 198 keys, SHA `30c3f61a64ec641abbb3acdbc7a8bcaf197f0238f1bf9e76c2c7ce8e590f86a3` |
| Corpus SHA | `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231` |
| BM25 | k1=1.5, b=0.75, Top-50 |
| Tokenizer | `[\u0600-\u06FF]+|[A-Za-z0-9]+` |
| KN n | 54 (TRAIN 36, DEV 18) |
| Roman KN n | 51 (TRAIN 33, DEV 18) |
| Urdu KN n | 3 (TRAIN only) |

---

## R2-B0 — frozen Method D / M0

No query rewrite.

| Slice | n | Hit@1 | Hit@5 | Hit@10 | Hit@50 | MRR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| All KN | 54 | 3 | 7 (0.1296) | 7 | 9 (0.1667) | 0.0786 |
| TRAIN | 36 | 3 | 6 | 6 | 7 | 0.1080 |
| DEV | 18 | 0 | 1 | 1 | 2 | 0.0198 |
| Roman | 51 | 1 | 4 (0.0784) | 4 | 6 (0.1176) | 0.0375 |
| Roman TRAIN | 33 | 1 | 3 | 3 | 4 | 0.0472 |
| Roman DEV | 18 | 0 | 1 | 1 | 2 | 0.0198 |
| Urdu | 3 | 2 | 3 | 3 | 3 | 0.7778 |

TRAIN Roman Hit@5 failures (n=30): **29 MISS/VOCAB**, **1 RANK** (KN014 at 44). **0 NORM** (no reverse-dict alias mismatch vs source tokens).

---

## R2-2 — unknown-token preservation

Not run as a retriever. Method D BM25 already skips missing terms and keeps the rest. Drop vs preserve is identical.

---

## R2-1 — reverse-dict canonical fold

`kya→kiya` and other frozen sibling folds. 12/51 Roman queries changed tokens.

| vs B0 Hit@5 | improved | unchanged | degraded | total |
| --- | ---: | ---: | ---: | ---: |
| All KN | 0 | 54 | 0 | 54 |
| Roman | 0 | 51 | 0 | 51 |
| Roman TRAIN | 0 | 33 | 0 | 33 |
| Roman DEV | 0 | 18 | 0 | 18 |

Hit@5 unchanged (7/54). Roman Hit@50 **fell** 6→5 because KN014 left the candidate set (rank 44 → miss50).

---

## R2-3 — bounded sibling expansion

Same Hit@5 as B0 (0/51 Roman improved or degraded). Same Hit@50 regression as R2-1 (KN014).

---

## Decision

**STOP — NEGATIVE RESULT** for Phase 2 Roman lexical strengthening.

Alias folding and bounded expansion did not improve ExactSource Hit@5. The one rank movement was a Hit@50 regression. TRAIN Roman misses are candidate-generation VOCAB gaps, not closed spelling aliases. No further ad-hoc dictionary rows. No character n-grams. No Phase 3 in this step.
