# HYBRID-RRF — controlled experiment report

**Experiment ID:** HYBRID-RRF  
**Status:** complete  
**Decision:** `HYBRID RRF PARTIALLY SUPPORTED`  
**Timestamp (UTC, after evaluation):** 2026-09-12T13:18:32Z  
**Branch / commit:** `research/ultra-v2-strengthening` / `fd54ac9b65c2db93e7e16fbf0c5a40b6a6025be1`

Protocol was frozen in `HYBRID_PREREGISTRATION.md` **before** hybrid scores. That file was not rewritten after seeing results.

TEST query content was not opened.

Phase 3 official numbers and `dense_doc_embeddings.npy` were not rewritten.

---

## 1. Question

Can Reciprocal Rank Fusion (k=60) of frozen Method-D BM25 Top-50 and frozen Phase-3 dense Top-50 improve ExactSource retrieval over **either component alone** on Roman KN TRAIN+DEV (n=51)?

This is not “did we reach 80%.”

---

## 2. Gates (mandatory, before official hybrid scores)

Both gates compared **per-query ranks / candidate identity**, not aggregates only.

| Gate | Artifact | What was matched | Result |
| --- | --- | --- | --- |
| Method-D BM25 Top-50 | `phase2_roman/artifacts/r2_b0_per_query.csv` | gold rank, in_top50, hit@5 for all 51 | **PASS** |
| Dense Top-50 | `phase3_dense/DENSE_PER_QUERY.csv` | gold rank and rank-1 doc id for all 51 | **PASS** |
| RRF second pass | same fused lists | identical gold ranks | **PASS** |

Reproduced aggregates matched the frozen cells:

| System | Hit@1 | Hit@5 | Hit@10 | Hit@50 | MRR |
| --- | ---: | ---: | ---: | ---: | ---: |
| Frozen / reproduced Method-D BM25 | 1 | 4 | 4 | 6 | 0.0375 |
| Frozen / reproduced dense e5-small | 5 | 15 | 16 | 22 | 0.1726 |

No baseline was invented. Document embeddings were **not** regenerated. Encoder: `intfloat/multilingual-e5-small` revision `8d923955b027282ba975c0a4c825486c9ca4c490`. Prefix mode: `manual_concat`.

---

## 3. Official comparison (Roman KN TRAIN+DEV, n=51)

| Method | Hit@1 | Hit@5 | Hit@10 | Hit@50 | MRR |
| --- | ---: | ---: | ---: | ---: | ---: |
| Method-D BM25 | 1/51 = 1.96% | 4/51 = 7.84% | 4/51 = 7.84% | 6/51 = 11.76% | 0.0375 |
| Dense e5-small | **5/51 = 9.80%** | **15/51 = 29.41%** | 16/51 = 31.37% | 22/51 = 43.14% | **0.1726** |
| Hybrid RRF (k=60) | 3/51 = 5.88% | 11/51 = 21.57% | **19/51 = 37.25%** | **25/51 = 49.02%** | 0.1422 |

Bold = best on that metric.

Hybrid beats BM25 on every reported metric. Hybrid beats dense on Hit@10 (+3) and Hit@50 (+3). Hybrid is **worse** than dense on Hit@1 (−2), Hit@5 (−4), and MRR (−0.0304).

---

## 4. Fusion mechanics (observed, not tuned)

Mean |BM25 Top-50 ∩ dense Top-50| = **0.53** documents (min 0, max 12). Mean union size = 98.5 (max 100).

The two retrievers almost do not share candidates. Unweighted RRF therefore interleaves two largely disjoint lists. That can raise Hit@50 (more unique golds in the pool) while lowering early precision (dense’s best ranks are diluted by BM25-only documents).

RRF k=60 was not changed after seeing this.

---

## 5. Case classes (Hit@50, all n=51)

| Class | Count | Meaning |
| ---: | ---: | --- |
| A | 6 | BM25 Top-50 success retained by hybrid |
| B | 21 | Dense Top-50 success retained by hybrid |
| C | 19 | BM25 Top-50 miss recovered by hybrid |
| D | 4 | Dense Top-50 miss recovered by hybrid |
| E | 25 | Both miss (gold in neither Top-50) |
| F | 1 | Hybrid lost a previous single-system Top-50 success |

**Dense misses recovered at Top-50 (D):** KN004, KN012, KN023, KN038 (lexical Method-D hits that dense ranked 107 / 59 / outside 50 / 7228).

**Single-system success lost at Top-50 (F):** KN040 — dense rank 27 → hybrid rank 54. Gold was dense-only; RRF of a disjoint BM25 list pushed it past cutoff 50.

**BM25 Top-50 successes lost:** 0.

**Hit@5 regressions (descriptive, not the decision rule):**

- Hybrid lost 2/4 BM25 Hit@5 (KN012 rank 5→10; KN038 rank 3→6). Both remain in hybrid Top-10/50.
- Hybrid lost 7/15 dense Hit@5 (KN013, KN019, KN031, KN033, KN039, KN052, KN053).
- Hybrid recovered 3 dense Hit@5 misses (KN004, KN014, KN023) and 9 BM25 Hit@5 misses.

Transition vs dense Top-50: recovered 4, regressed 1. Exact McNemar p=0.375 (descriptive).  
Transition vs dense Top-5: recovered 3, regressed 7. Exact McNemar p=0.344.  
Transition vs BM25 Top-50: recovered 19, regressed 0. Exact McNemar p=4e-6 (vs the **weaker** component).

---

## 6. ROOM Category 1 (fixed n=11)

Hybrid ExactSource Hit@50 = **3/11** (dense 3/11, BM25 0/11). Same three IDs as Phase 3: KN001, KN011, KN045. Cross-form candidate generation is not solved. Hybrid did not add ROOM Cat1 recoveries.

VOCAB controls KN017/KN020/KN041: hybrid Hit@50 = 1/3 (same as dense: KN017 only). Not claimed as romanization success.

---

## 7. Candidate generation vs ranking

- Gold outside **both** Top-50s: **25/51**. Reranking cannot create those documents.
- Gold in the fused union but hybrid rank >50: **1** (KN040).
- Gold in hybrid Top-50: **25/51**.

The remaining ceiling after this fusion is still mostly **candidate generation**, not fusion ranking.

---

## 8. Runtime / hardware

| Step | Seconds |
| --- | ---: |
| Method-D pickle load (cache hit, ~316 MB) | 24.284 |
| BM25 Top-50 × 51 | 0.755 |
| Dense npy load (mmap then copy; no regenerate) | 0.702 |
| e5-small load (CPU) | 69.963 |
| Query encode n=51 | 2.191 |
| Dense exact cosine × 51 | 1.856 |
| **Wall** | **99.911** |

CPU only. CUDA: no. Document embeddings regenerated: **no**.  
Python 3.13.9, numpy 2.3.5, torch 2.13.0+cpu, sentence-transformers 5.7.0.  
Windows 11, 12-core Intel CPU.

---

## 9. Decision

`HYBRID RRF PARTIALLY SUPPORTED`

Why not `SUPPORTED`: hybrid is worse than the stronger component (dense) on Hit@1, Hit@5, and MRR. ROOM Cat1 stays 3/11. 25/51 remain outside both lists. McNemar vs dense is not significant.

Why not `UNSUPPORTED`: hybrid improves Hit@10 and Hit@50 over dense; restores all 6 BM25 Top-50 successes (Phase 3 had lost the lexical Hit@5 set); recovers 4 dense Top-50 misses, including KN004 at hybrid rank 1; overlap ≈ 0.5 shows genuine complementary evidence.

H1 is only partly supported. Unweighted RRF is a useful **pool union**, not a uniformly better ranker than dense.

Do **not** retune k, add CombSUM, add a second encoder, or start reranking from this file. Those would be a later, separately pre-registered experiment.

---

## 10. Safety

| Check | Value |
| --- | --- |
| TEST accessed | NO |
| Frozen M0 modified | NO |
| PLOS modified | NO |
| Phase-3 artifacts modified | NO |
| Historical R2 artifacts modified | NO |
| Query tuning | NO |
| Model shopping | NO |
| Parameter tuning (k, weights) | NO |
| Reranking | NO |
| Gold-document injection | NO |
| Document embeddings regenerated | NO |
| MiniLM used | NO |
| Commit / push | NO |
