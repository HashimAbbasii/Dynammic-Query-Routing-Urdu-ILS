# ULTRA v2 Phase 4 — Hybrid BM25 + Dense Retrieval

**Document type:** pre-registration / controlled design  
**Experiment ID:** HYBRID-RRF  
**Directory:** `experiments/ultra_v2/phase4_hybrid/`  
**Branch:** `research/ultra-v2-strengthening`  
**Commit at design freeze:** `fd54ac9b65c2db93e7e16fbf0c5a40b6a6025be1`  
**Timestamp (UTC, written before hybrid evaluation):** `2026-09-12T13:05:00Z`

**Phase 4 does not modify Phase 3 results.**  
It does not rewrite R2-B0, R2-C0, R2-1, R2-NG3, frozen M0, or PLOS artifacts.  
It does not regenerate `artifacts/dense_doc_embeddings.npy`.  
It does not access TEST query content.

This file must not be silently rewritten after hybrid scores are observed.

---

## 1. Status

**DESIGN ONLY — NOT EXECUTED.**

Phase 0–3 are closed. This document freezes the Phase-4 protocol before any hybrid retrieval run.

Inspection (2026-09-12) found:

- Phase 3 official encoder is **`intfloat/multilingual-e5-small`** revision `8d923955b027282ba975c0a4c825486c9ca4c490`, **not** `paraphrase-multilingual-MiniLM-L12-v2`. MiniLM is historical thesis infrastructure. Phase 4 reuses the Phase-3 e5-small index. That is not a new model and not model shopping.
- Dense matrix `(111860, 384)` float32, unit-norm, 171,817,088 bytes, cache-complete.
- CSV `Index` equals row number `0 … 111859` with **zero mismatches**. BM25 posting ids, dense rows, and KN `source_doc_id` share that integer.
- Method-D BM25 pickle cache exists (`phase2_roman/artifacts/_index_cache.pkl`, ~316 MB).

---

## 2. Research question

Can a **rank-based hybrid** of frozen Method-D BM25 and the frozen Phase-3 dense retriever combine complementary candidate evidence and improve ExactSource retrieval over **either component alone** on authorized Roman KN TRAIN+DEV (n=51)?

---

## 3. Hypothesis

### H1

BM25 and dense make different errors. Reciprocal Rank Fusion (RRF) of their Top-50 lists will recover some documents that one system misses but the other retrieves, including:

- dense recoveries of Method-D misses (especially ENT / paraphrase), and
- Method-D lexical successes that dense ranked out of Top-50.

### H0

Hybrid RRF does not produce a scientifically useful improvement over the better of the two frozen components on the authorized evaluation.

These hypotheses will not be changed after seeing results.

---

## 4. Scientific motivation

Phase 3 (official, frozen):

| Method | n | Hit@1 | Hit@5 | Hit@10 | Hit@50 | MRR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Frozen Method-D BM25 | 51 | 1 | 4 | 4 | 6 | 0.0375 |
| Dense (e5-small) | 51 | 5 | 15 | 16 | 22 | 0.1726 |

Dense recovered 20 Top-50 BM25 misses and lost all 4 BM25 Hit@5 successes. ROOM Cat1 remained 3/11. 29/51 Roman KN queries stayed outside the dense Top-50.

That is complementary error structure, not a mandate to chase 80%. Hybrid is the next **minimal** test of complementarity. It is not reranking, not a new encoder, and not fusion-method shopping.

---

## 5. Dataset / query set

| Item | Value |
| --- | --- |
| Benchmark | `ultra-v2-benchmark-v0` |
| Files | `benchmark/train/queries_kn.csv`, `benchmark/dev/queries_kn.csv` |
| Primary scored population | Roman KN TRAIN+DEV, **n=51** |
| Gold | `source_doc_id` (ExactSource) |
| Secondary (descriptive) | all KN TRAIN+DEV by script (URDU n=3 is too small for claims) |
| Not scored | NL (no official qrels) |
| Forbidden | `benchmark/test/**` query CSVs |

Why this set is permitted: TRAIN/DEV of the fresh unseen-query benchmark; TEST remains sealed; same population as R2-B0 and Phase 3, so comparisons are paired.

Script labels: CSV `script` cross-checked with frozen `detect_script` (read-only import of `experiments/phase5_roman_urdu/run_phase5.py`).

ROOM Category 1 (frozen n=11): KN001, KN006, KN008, KN010, KN011, KN018, KN037, KN045, KN047, KN050, KN051.

VOCAB controls: KN017, KN020, KN041 (do not claim as romanization success).

---

## 6. BM25 component

Frozen **Method D** as in R2-B0:

- Module: `experiments/phase5_roman_urdu/run_phase5.py` **read-only**
- Index: romanized-document BM25 for ROMAN queries (`romanize_token`: reverse-dict first JSON key else character table)
- Query: tokenize as typed; no dictionary on the query
- k1=1.5, b=0.75, tokenizer `[\u0600-\u06FF]+|[A-Za-z0-9]+`
- Dictionary SHA-256: `30c3f61a64ec641abbb3acdbc7a8bcaf197f0238f1bf9e76c2c7ce8e590f86a3`
- Corpus: `data/clean_articles.csv`, SHA-256 `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231`
- Candidate depth: **Top-50**
- Official comparison cells remain 1/4/4/6 / MRR 0.0375

Reuse `phase2_roman/artifacts/_index_cache.pkl` if its meta matches corpus/dict/k1/b/tokenizer. Rebuild of that cache is allowed only if stale; it must not rewrite `r2_b0_*`.

If independently reproduced BM25 ranks disagree with `r2_b0_per_query.csv`, **STOP** (`BLOCKED`) rather than silently replacing the frozen baseline.

---

## 7. Dense component

Frozen Phase-3 retriever:

- Encoder: `intfloat/multilingual-e5-small` @ `8d923955b027282ba975c0a4c825486c9ca4c490`
- Document matrix: `experiments/ultra_v2/phase3_dense/artifacts/dense_doc_embeddings.npy` (load only; **do not regenerate**)
- Prefixes: `query: ` / `passage: ` (manual concat)
- Similarity: cosine = inner product of L2-normalized vectors
- Candidate depth: **Top-50**
- Official comparison cells remain 5/15/16/22 / MRR 0.1726

Query embeddings (51 Roman KN texts, plus 3 Urdu KN if secondary is computed) may be re-encoded. Document embeddings may not.

If re-search from the npy disagrees with `DENSE_PER_QUERY.csv` gold ranks, **STOP** (`BLOCKED`).

---

## 8. Candidate retrieval

For each authorized query:

1. Method-D BM25 Top-50 `(doc_id, bm25_score)` with 1-based ranks.
2. Dense Top-50 `(doc_id, cosine)` with 1-based ranks.
3. **Union** of the two lists (at most 100 unique ids).
4. Fuse by RRF (next section).
5. Sort fused scores descending; tie-break **smaller doc_id**.
6. Report gold rank in the fused list. If gold is in neither Top-50, fused rank is a miss (outside the candidate pool).

No deeper BM25/dense depth. Depth 50 is inherited from R2/Phase 3, not tuned.

No hybrid of Urdu-raw BM25 with Method D for Roman queries. Roman KN uses Method D only, as in R2-B0.

---

## 9. Fusion method

### Primary (this experiment): Reciprocal Rank Fusion

Cormack, Clarke, and Buettcher, SIGIR 2009:

\[
\mathrm{RRF}(d) = \sum_{s \in \{\mathrm{BM25},\,\mathrm{dense}\}} \frac{1}{k + \mathrm{rank}_s(d)}
\]

If system \(s\) did not retrieve \(d\) in its Top-50, that term is **0**.

**\(k = 60\)** (the conventional constant in that paper). Frozen a priori. Not fit on TRAIN/DEV.

No score calibration. No min-max. No learned weight. No RRF variant search.

### Alternatives considered and rejected for this phase

| Method | Why not primary |
| --- | --- |
| Weighted CombSUM / cosine+BM25 linear mix | Requires a weight; that is DEV tuning or an arbitrary knob. |
| Min-max then equal sum | Still pretends BM25 and cosine are commensurate after a scaling choice. |
| Candidate union without rank fusion (OR) | Does not produce a single ranking for Hit@k / MRR. |
| Multiple k or multiple fusion recipes | Fusion shopping. |

One method. One \(k\). One run.

---

## 10. Fixed parameters

| Parameter | Value | Tuned? |
| --- | --- | --- |
| BM25 k1, b | 1.5, 0.75 | No (frozen M0/R2) |
| BM25 / dense cutoff | 50 | No (inherited) |
| RRF k | 60 | No (literature default) |
| Fusion weights | none (ranks only) | N/A |
| Encoder | Phase-3 e5-small | No |
| Query text | as written | No |
| Top-K eval | 1, 5, 10, 50 | No |

---

## 11. Evaluation metrics

Primary, Roman KN n=51, ExactSource:

- Hit@1, Hit@5, Hit@10, Hit@50, MRR  
  (MRR uses reciprocal rank 0 if gold not in the fused Top-50 pool)

Secondary:

- Transition matrices vs BM25 and vs dense at Top-5 and Top-50
- Recovered / regressed counts
- Frozen R2 taxonomy (ROOM, ENT, VOCAB, NEIGH, RANK, SUCCESS)
- ROOM Cat1 Hit@50 = X/11
- VOCAB controls KN017/020/041
- Candidate-generation (gold outside both Top-50s) vs ranking among fused candidates
- Exact McNemar vs BM25 and vs dense on Hit@5 and Hit@50 (descriptive; n=51)

Do not average KN with NL. Do not replace ExactSource.

---

## 12. Baselines

| System | Source of official numbers | Role |
| --- | --- | --- |
| Method-D BM25 | R2-B0 (1/4/4/6, MRR 0.0375) | Frozen lexical |
| Dense e5-small | Phase 3 (5/15/16/22, MRR 0.1726) | Frozen dense |
| Hybrid RRF | **this experiment only** | Treatment |

Improvement is **not** “hybrid > BM25” alone (dense already beats BM25 on aggregates). The scientific comparison is hybrid vs **each** component, especially:

- vs dense: does fusion restore lexical successes without wiping dense recoveries?
- vs BM25: does fusion keep the 20 dense Top-50 recoveries?

---

## 13. Leakage controls

- No TEST query files opened
- No gold id used until after fused ranking
- No qrel filtering of the corpus
- No query rewrite / expansion / translation
- No training, no fine-tune, no learned fusion
- Historical IDs (QTRN / H / K / U) refused
- Phase-3 and R2 artifacts read-only

---

## 14. TEST exclusion

Code must refuse paths under `experiments/ultra_v2/benchmark/test/`.  
Seal metadata may be inspected. Query CSVs there must not be loaded.  
If TEST query text is loaded: `BLOCKED — DATA SAFETY FAILURE`.

---

## 15. Reproducibility

Record Python and package versions, corpus/dict SHAs, RRF k, candidate depths, hardware, runtime, whether BM25 cache hit, whether dense npy was mmap-loaded.

Run fused ranking twice on the same lists; ranks must be identical.

Do not use FAISS / HNSW (approximate). Dense search remains exact NumPy cosine.

---

## 16. Runtime / hardware plan

| Operation | Hardware | Expected class |
| --- | --- | --- |
| Load dense npy mmap | CPU | seconds |
| Re-encode 51–54 queries | CPU (e5-small) | **short** (seconds–1 min) |
| Load Method-D pickle (~316 MB) | CPU | **short–moderate** (tens of seconds) |
| BM25 Top-50 × 51 | CPU | seconds |
| Dense Top-50 × 51 (full-corpus cosine) | CPU | seconds |
| RRF | CPU | negligible |
| **Regenerate 111,860 doc embeddings** | — | **forbidden** |
| GPU / T4 | **not required** | — |

T4 would only help document embedding, which Phase 4 must not redo. Query encode is tiny.

**Runtime class: short** if the BM25 cache hits; **moderate** only if that pickle is stale and Method D must be retokenized (still far below a dense re-index).

---

## 17. Expected outputs (when later executed)

All new files under `experiments/ultra_v2/phase4_hybrid/` only:

- `HYBRID_PREREGISTRATION.md` (this file)
- `run_hybrid.py`
- `hybrid_fusion.py` (RRF only)
- `HYBRID_PER_QUERY.csv`
- `HYBRID_CONTROLLED_EXPERIMENT.md`
- `artifacts/hybrid_config.json`
- `artifacts/hybrid_summary.json`

Do not overwrite Phase-3 or R2 files.

---

## 18. Stop conditions

Choose exactly one after a valid run:

- `HYBRID RRF SUPPORTED` — meaningful gain over **both** frozen components (recoveries vs regressions, not a lone aggregate bump)
- `HYBRID RRF PARTIALLY SUPPORTED` — some complementarity (e.g. restores BM25 hits or adds recoveries) with important remaining misses/regressions
- `HYBRID RRF UNSUPPORTED` — no scientifically useful improvement over the better component
- `BLOCKED` — data safety, ID-mapping, or rank-reproduction failure

No “≥80% = success” rule. No second fusion method after seeing scores. No reranker in this phase.

If hybrid is unsupported, the next authorized discussion is whether **candidate-depth** or **reranking** is justified — as a **later** experiment, not an automatic continuation.

---

## 19. Relationship to Phase 3

Phase 3 answered: dense can recover some BM25 misses and is not a replacement for Method D.

Phase 4 asks whether **rank fusion** of those two frozen systems is complementary.

Phase 4 does not modify Phase 3 results, embeddings, or decision (`DENSE BASELINE PARTIALLY SUPPORTED`).

---

## 20. Relationship to future reranking

Phase 4 is first-stage fusion only.

No cross-encoder, LLM judge, pairwise scoring, or reordering of a BM25-only or dense-only list by a third model.

If hybrid candidate pools still miss gold outside Top-50, that remains a **candidate-generation** problem. Reranking cannot create a document that is in neither list. That distinction stays frozen.
