# ULTRA v2 Phase 8 — 3-way RRF (BM25 + Dense + NG3)

Unweighted Reciprocal Rank Fusion, k=60 (same as Phase 4), third input = frozen R2-NG3.
Does **not** edit Phase 2–7, PLOS/M0, or TEST.

Design (frozen before scoring): `PHASE8_PREREGISTRATION.md`

Execution record: `PHASE8_CONTROLLED_EXPERIMENT.md`

**Experiment ID:** PHASE8-3WAY-RRF  
**Decision:** `PHASE8 UNSUPPORTED`

Roman KN TRAIN+DEV n=51: 3-way RRF Hit@5 **8/51** vs 2-way Hybrid **11/51**. McNemar vs 2-way Hybrid Hit@5 p=0.375 (not significant). Remaining four-way misses: **0/23**.
