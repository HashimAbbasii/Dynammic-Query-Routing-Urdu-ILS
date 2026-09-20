# DENSE-BASELINE — controlled experiment report

**Experiment ID:** DENSE-BASELINE  
**Status:** complete  
**Decision:** `DENSE BASELINE PARTIALLY SUPPORTED`  
**Timestamp (UTC, after evaluation):** 2026-09-11T19:29:19Z  
**Branch / commit:** `research/ultra-v2-strengthening` / `fd54ac9b65c2db93e7e16fbf0c5a40b6a6025be1`

Protocol was frozen in `DENSE_PREREGISTRATION.md` **before** treatment scores. That file was not rewritten after seeing results.

TEST query content was not opened.

---

## 1. Resume diagnosis

Interruption point: **Stage E — corpus embedding generation (partial, valid checkpoint).**

Evidence:

- `DENSE_PREREGISTRATION.md` already existed (stage B complete).
- Hugging Face snapshot `intfloat/multilingual-e5-small` revision `8d923955b027282ba975c0a4c825486c9ca4c490` was already cached (stage C complete).
- `artifacts/dense_config.json` and `dense_representation_stats.json` existed (stage D complete).
- `artifacts/dense_doc_embeddings.memmap` was a full-size float32 matrix (111,860 × 384) with **4,096 unit-norm committed rows** and zeros thereafter.
- `artifacts/dense_embed_progress.json` recorded `next_index=4096`, matching those rows.
- No `DENSE_PER_QUERY.csv`, `dense_summary.json`, or `DENSE_CONTROLLED_EXPERIMENT.md` (stages G–J not done).
- Python PID **2092** (`run_dense_baseline.py`, started 2026-09-11 15:52 local) was **still alive** after the chat stop. It was the original encoder, not a second job.

The chat stop did **not** kill the encoder. No second model, no restart of completed rows.

---

## 2. Recovery action

| Object | Action |
| --- | --- |
| Preregistration, model, corpus SHA, TRAIN/DEV loaders | Reused |
| Committed embeddings 0–4095 | Reused in-process (same PID 2092) |
| Remaining documents 4096–111859 | Continued by the original process |
| Query embed / search / evaluation | Ran once after the full matrix was written |
| Frozen R2-B0 / M0 / TEST / PLOS | Untouched |

A second encoder was **not** started (that would have corrupted the open memmap).

OpenMP (not an experimental result):

- Conflict: two `libiomp5md.dll` copies loaded by the live process (`anaconda3\Library\bin` from MKL, and `torch\lib` from PyTorch). This is Intel OMP Error #15.
- The completed run had already started with `KMP_DUPLICATE_LIB_OK=TRUE`. Killing it to change the environment would have discarded the in-flight chunk. It was left running.
- Safer alternative, tested in a **separate** subprocess without `KMP_DUPLICATE_LIB_OK`: `MKL_THREADING_LAYER=SEQUENTIAL` (MKL does not load a second Intel OpenMP; Torch keeps OpenMP for encode). Wired into `launch_dense_baseline.py` and the runner for **future** launches only. This completed evaluation used the original process environment.

---

## 3. Model (frozen a priori)

| Field | Value |
| --- | --- |
| ID | `intfloat/multilingual-e5-small` |
| Revision | `8d923955b027282ba975c0a4c825486c9ca4c490` |
| Dim | 384 |
| Max seq | 512 |
| Prefixes | `query: ` / `passage: ` (manual concat; ST prompt strings were empty) |
| Pooling | mean |
| Similarity | cosine (L2-normalized inner product) |
| Fine-tune | none |

Rationale (unchanged): documented multilingual retriever with Urdu in the XLM-R language list; already the thesis Phase-4B designated long-context encoder; MIT; CPU-feasible. Not selected from v2 scores.

---

## 4. Baseline reproduction

Frozen Method-D BM25 on Roman KN TRAIN+DEV, read from `experiments/ultra_v2/phase2_roman/artifacts/r2_b0_per_query.csv` (not rewritten):

| Method | n | Hit@1 | Hit@5 | Hit@10 | Hit@50 | MRR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Frozen Method-D BM25 | 51 | 1 | 4 | 4 | 6 | 0.0375 |

---

## 5. Dense results — primary (Roman KN TRAIN+DEV)

| Method | n | Hit@1 | Hit@5 | Hit@10 | Hit@50 | MRR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Frozen Method-D BM25 | 51 | 1 | 4 | 4 | 6 | 0.0375 |
| Dense baseline | 51 | **5** | **15** | **16** | **22** | **0.1726** |

Raw counts: Hit@1 1→5; Hit@5 4→15; Hit@10 4→16; Hit@50 6→22.  
MRR 0.0375 → 0.1726.

Mechanical split (dense): Hit@5 = 15; in-Top-50 / out-Top-5 (ranking) = 7; outside Top-50 (candidate generation) = 29.

TRAIN n=33: Hit@5 9/33, Hit@50 13/33, MRR 0.171.  
DEV n=18: Hit@5 6/18, Hit@50 9/18, MRR 0.1754. Directionally consistent; n is small.

---

## 6. Transition matrices

**Top-50** (baseline HIT = Method-D gold in Top-50):

|  | Dense HIT | Dense MISS |
| --- | ---: | ---: |
| Baseline HIT | 2 | 4 |
| Baseline MISS | 20 | 25 |

Recovered 20; regressed 4.

**Top-5:**

|  | Dense HIT | Dense MISS |
| --- | ---: | ---: |
| Baseline HIT | 0 | 4 |
| Baseline MISS | 15 | 32 |

Recovered 15; **all 4 baseline Hit@5 successes were lost**.

Exact McNemar (descriptive, n=51): Hit@50 discordant 4 vs 20, p=0.001544; Hit@5 discordant 4 vs 15, p=0.019211. Not the decision rule.

---

## 7. ROOM Category 1 (fixed n=11)

Dense ExactSource Hit@50 = **3/11** (baseline 0/11). Recovered 3; regressed 0.

| ID | Dense rank | Hit@50 |
| --- | ---: | ---: |
| KN001 | 16 | 1 |
| KN006 | 13002 | 0 |
| KN008 | 2036 | 0 |
| KN010 | 466 | 0 |
| KN011 | **1** | 1 |
| KN018 | 11213 | 0 |
| KN037 | 2537 | 0 |
| KN045 | 23 | 1 |
| KN047 | 59 | 0 |
| KN050 | 3531 | 0 |
| KN051 | 616 | 0 |

Cross-form candidate generation is **not solved**. Three recoveries (English/Roman need → Urdu gold) show the mechanism can work; eight remain outside Top-50, including KN047 at 59 (just outside).

---

## 8. Frozen failure-category comparison (Hit@50)

Labels from `R2_B0_FAILURE_ANALYSIS.csv`. SUCCESS = the four R2-B0 Hit@5 hits. Categories were not redefined.

| Category | n | Baseline Hit@50 | Dense Hit@50 | Recovered | Regressed |
| --- | ---: | ---: | ---: | ---: | ---: |
| ROOM Cat1 (slice) | 11 | 0 | 3 | 3 | 0 |
| ROOM (full) | 19 | 0 | 6 | 6 | 0 |
| ENT | 16 | 0 | 10 | 10 | 0 |
| VOCAB | 9 | 0 | 4 | 4 | 0 |
| RANK | 2 | 2 | 2 | 0 | 0 |
| NEIGH | 1 | 0 | 0 | 0 | 0 |
| SUCCESS | 4 | 4 | 0 | 0 | 4 |
| NORM | 0 | — | — | — | — |
| TEMP | 0 | — | — | — | — |

ENT is the strongest dense room (10/16 Top-50; 7/16 Hit@5). ROOM full 6/19. VOCAB 4/9.

---

## 9. VOCAB negative controls

Not claimed as romanization recovery.

| ID | Dense rank | Hit@50 | Note |
| --- | ---: | ---: | ---: |
| KN017 | **1** | 1 | English product paraphrase (`boom supersonic…`) retrieved the Urdu gold. Semantic overlap, not Method-D spelling fold. |
| KN020 | 110 | 0 | Still a miss (CPEC English vs Urdu راہداری). |
| KN041 | 11599 | 0 | Still a miss (caretaker / CPEC paraphrase). |

KN017 supports H1’s paraphrase clause. It does **not** mean Romanization is solved.

---

## 10. Baseline success regressions (important)

All four Method-D Hit@5 successes left the dense Top-50:

| ID | Baseline rank | Dense rank |
| --- | ---: | ---: |
| KN004 | 1 | 107 |
| KN012 | 5 | 59 |
| KN023 | 3 | 47725 |
| KN038 | 3 | 7228 |

Dense and lexical successes are **not the same queries**. A higher aggregate does not preserve the BM25 hits. Hybrid fusion is a later experiment, not this one.

RANK items: KN014 44→16 (still ranking); KN048 42→3 (now Hit@5).

---

## 11. Script secondary (authorized KN TRAIN+DEV)

| Script | n | Hit@5 | Hit@50 | MRR |
| --- | ---: | ---: | ---: | ---: |
| ROMAN | 51 | 15 | 22 | 0.1726 |
| URDU | 3 | 3 | 3 | 0.7778 |
| MIXED | 0 | — | — | — |
| OTHER | 0 | — | — | — |

Urdu n=3 is too small for a statistical claim. Same-script Urdu→Urdu is not the Roman candidate-generation question.

NL TRAIN/DEV were ID-checked only (44+22). No official qrels; not scored.

---

## 12. Candidate generation vs ranking

- 29/51 golds remain outside Top-50 → still a **candidate-generation** problem for a majority of Roman KN queries.
- 7/51 are in Top-50 but not Top-5 → ranking, not “need a reranker to invent candidates.”
- Dense recovered 20/45 previous Top-50 misses. That is real progress on the bottleneck, not a solution.

Duplicates: 4 exact-duplicate extra copies in the frozen corpus; not removed.

---

## 13. Reproducibility

Second query encode + search: **rank identity True**; query vectors allclose atol=1e-6 True.

Python 3.13.9; numpy 2.3.5; torch 2.13.0+cpu; sentence-transformers 5.7.0; transformers 5.15.0; pandas 2.3.3.  
CPU only, 12 cores, no CUDA. Index/embed 30,948 s (~8.6 h). Query embed 0.49 s. Search 0.76 s. RSS ~652 MB after search. Exact NumPy cosine (not FAISS).

Corpus SHA-256 `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231` (111,860 docs, `combined_text`).

---

## 14. Did dense beat BM25? Interpretation

1. **Yes, on the primary aggregates** (5/15/16/22 vs 1/4/4/6; MRR 0.1726 vs 0.0375).
2. **Yes, it recovered Top-50 misses** (20 recovered; 25 original misses remain).
3. **ROOM Cat1: 3/11** — partial, not a solution.
4. **Semantic/paraphrase:** KN017 rank 1; several English/Roman entity queries recovered (ENT 10/16).
5. **All 4 baseline successes lost.**
6. **Ranks identical on a second search.**
7. **Candidate generation is improved, not removed** (29/51 still miss Top-50).
8. **Major failure modes:** remaining cross-form ROOM (incl. 8/11 Cat1); entity misses; VOCAB controls KN020/KN041; wholesale loss of lexical BM25 hits.

H1 is **partially** supported. H0 is rejected for “no improvement,” but dense is not a drop-in replacement for Method D.

---

## 15. Exact decision

`DENSE BASELINE PARTIALLY SUPPORTED`

Absolute gains and 20 Top-50 recoveries (especially ENT) are scientifically useful. ROOM Cat1 3/11, 29 remaining Top-50 misses, and regression of every Method-D success prevent `SUPPORTED`. This is not `UNSUPPORTED`.

Do not start hybrid, RRF, reranking, or a second encoder from this report. That is a separate experiment.

---

## 16. Safety

| Check | Value |
| --- | --- |
| TEST accessed | NO |
| Frozen M0 modified | NO |
| PLOS modified | NO |
| Historical R2 artifacts modified | NO |
| Query tuning | NO |
| Model shopping | NO |
| Parameter tuning | NO |
| Hybrid | NO |
| Reranking | NO |
| Gold-document injection | NO |
| Data leakage detected | NO |
| Commit / push | NO |
