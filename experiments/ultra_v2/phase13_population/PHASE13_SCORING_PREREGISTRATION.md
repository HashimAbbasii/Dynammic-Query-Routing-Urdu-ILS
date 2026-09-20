# Phase 13 Scoring — Preregistration

**Status:** PREREGISTERED before any n=80 scoring run.  
**Population:** Frozen Roman KN TRAIN+DEV **n=80** (`PHASE13_FREEZE_MANIFEST.json`).  
**TEST:** not accessed. **Program A / M0:** not modified.  
**Phases 2–12:** frozen — **no retuning**, no parameter changes, no artifact overwrites in those directories.

---

## 1. Purpose

Confirmatory ExactSource scoring of **already-frozen** retrieval methods on the expanded Roman KN population (51 original human-written + 29 Phase-13 LLM-drafted / human-reviewed). Not a method-selection experiment.

---

## 2. Methods scored (exact frozen parameters)

| Method | Frozen identity | Key frozen parameters |
|---|---|---|
| Method-D BM25 | Phase 2 R2-B0 / M0 Roman path | `k1=1.5`, `b=0.75`, Method-D romanization, frozen dict SHA `30c3f61a…`, corpus SHA `8992a6ac…`, Top-50 |
| Dense e5-small | Phase 3 | Frozen `dense_doc_embeddings.npy`; query encode only; cosine; Top-50 |
| NG3 | Phase 5 / R2-NG3 | Char 3-grams token-internal; BM25 `k1=1.5` `b=0.75` on NG3 features; representation stream SHAs as Phase 5 |
| Hybrid RRF | Phase 4 | Unweighted RRF `k=60` of Method-D Top-50 + Dense Top-50 |
| Phase 9 | PHASE9-WPTITLES | Frozen `bilingual_titles.csv` + v2 `match_rule`; Method-D BM25 on expanded tokens |
| Phase 10 cascade | Option B | Trigger = ≥1 Phase-9 EN title hit; `HYBRID_KEEP=40`, `CASCADE_SLOTS=10`, RRF(P9,NG3) fill |
| Phase 10b | Tail-preserve Option B | Same trigger; Hybrid ranks 41–50 preserved (no eviction) |

Implementation: reuse frozen modules under `phase2_roman/`, `phase3_dense/`, `phase4_hybrid/`, `phase5_ng3/`, `phase9_entity_resource/`, `phase10_cascade/` **without editing them**. Outputs write only to `experiments/ultra_v2/phase13_population/artifacts/scoring/`.

---

## 3. Endpoints (ExactSource)

Primary report cutoffs: **Hit@1, Hit@5, Hit@10, Hit@50, MRR** (MRR = 0 if gold not in Top-50).

Reported slices (all pre-registered):

1. **n=80** — full frozen Phase-13 population  
2. **n=51** — original Roman KN subset (ids with `writer_id=W1` / IDs &lt; KN091) — **must match** already-frozen Phase 2–10b aggregates/per-query hits; mismatch = **BLOCK / bug**, not a scientific result  
3. **n=29** — Phase-13-only (`KN091`–`KN119`) — descriptive only

---

## 4. Consistency gate (mandatory)

Before accepting n=80 headlines: for each method, the n=51 subset Hit@1/5/10/50 counts and MRR (to 1e-4) must equal the frozen summary cells:

| Method | Frozen Hit@1/5/10/50_n | Frozen MRR |
|---|---|---|
| BM25 | 1 / 4 / 4 / 6 | 0.0375 |
| Dense | 5 / 15 / 16 / 22 | 0.1726 |
| NG3 | 3 / 6 / 6 / 8 | 0.075 |
| Hybrid | 3 / 11 / 19 / 25 | 0.1422 |
| Phase 9 | 1 / 5 / 6 / 10 | 0.0478 |
| Phase 10 | 3 / 11 / 19 / 24 | 0.1418 |
| Phase 10b | 3 / 11 / 19 / 25 | 0.1422 |

---

## 5. Forbidden

- Retuning BM25/dense/RRF/cascade thresholds  
- Opening TEST  
- Overwriting Phase 2–12 scored CSVs / summaries  
- Averaging KN with NL  
- Treating n=29 as a tuning target  

---

## 6. Authorship disclosure

n=51 rows: human-written (`W1`).  
n=29 rows: LLM-drafted, human naturalness-reviewed (`LLM1`). Do not blur in reporting.
