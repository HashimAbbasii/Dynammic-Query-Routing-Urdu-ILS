# PHASE 9 FINAL REPORT

One-shot held-out evaluation under the Phase 8 freeze.  
Architecture, BM25, tokenizer, romanizer, dictionary, detector, routing, and metric were **not** changed.  
No second run. No test-set tuning. No queries dropped to raise a score.

---

## 0. Preflight (before scoring)

All checks **passed** (`artifacts/preflight.json`):

| Check | Result |
| --- | --- |
| Corpus SHA-256 | `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231` (matches freeze) |
| Corpus rows | 111,860 |
| Dictionary keys | 198 |
| k1 / b | 1.5 / 0.75 |
| top_k | 50 |
| Python | 3.13.9 (Anaconda) |
| NumPy | 2.3.5 |
| pandas | 2.3.3 |
| Phase 8 freeze intact | yes |
| Test tuning | **no** |

Frozen path executed: URDU/MIXED → Urdu BM25; ROMAN → Method D. Detector: Unicode script counts.

---

## 1. FINAL H001–H040 RESULT

**Official ExactSource Hit@5 cannot be computed.**

| | |
| --- | --- |
| n queries | 40 (H001–H040) |
| **n_scored** | **0** |
| **n_excluded** | **40** |
| Exclude reason | **no `source_doc_id` gold** |
| ExactSource Hit@5 | **not defined** (n_scored = 0) |
| P@5 | not defined |
| nDCG@5 | not defined |
| MRR | not defined |
| Hit@10 | not defined |
| Hit@15 | not defined |

H001–H040 are routing-trap queries (`heldout_traps.py`: SHORT/LONG protocol labels). They have **no known-item `source_doc_id`**. Phase 8 protocol §13 forbids guessing a gold document. Retrieval still ran **once** on all 40 strings (Top-50 lists produced). Rank of the source is empty because there is no source.

This is **not** a Hit@5 of 0.00 (that would mean 40 scored misses). It is **no official known-item score**.

---

## 2. Development result

n = 78 (Phase 2 dev + internal_val), exact-source Hit@5 = **0.8718** (68/78).

That number is **not** the held-out result.

---

## 3. Difference (final − development)

**Not defined.** There is no official held-out Hit@5 to subtract from 0.8718.

Do not treat 0.8718 as if it generalized to H001–H040.

---

## 4. Hits / misses

- Official known-item hits: **not applicable**
- Official known-item misses: **not applicable**
- Queries processed by the frozen retriever: **40 / 40**
- Queries excluded from the metric: **40 / 40**

Detector on the 40 queries (not used as gold): **20 URDU**, **20 ROMAN**, 0 MIXED. Paths: 20 Urdu BM25, 20 Method D. Matches the designer script field; the official router used the frozen Unicode detector, not the trap-file `script` column.

---

## 5. Per-query results

See `HELD_OUT_PER_QUERY.csv`. Summary:

| query_id | detector | path | source_doc_id | rank | Hit@5 | excluded |
| --- | --- | --- | --- | --- | --- | --- |
| H001 | URDU | urdu_bm25 | — | — | — | yes |
| H002 | URDU | urdu_bm25 | — | — | — | yes |
| H003 | URDU | urdu_bm25 | — | — | — | yes |
| H004 | URDU | urdu_bm25 | — | — | — | yes |
| H005 | URDU | urdu_bm25 | — | — | — | yes |
| H006 | URDU | urdu_bm25 | — | — | — | yes |
| H007 | URDU | urdu_bm25 | — | — | — | yes |
| H008 | URDU | urdu_bm25 | — | — | — | yes |
| H009 | ROMAN | roman_bm25_method_D | — | — | — | yes |
| H010 | ROMAN | roman_bm25_method_D | — | — | — | yes |
| H011 | ROMAN | roman_bm25_method_D | — | — | — | yes |
| H012 | ROMAN | roman_bm25_method_D | — | — | — | yes |
| H013 | ROMAN | roman_bm25_method_D | — | — | — | yes |
| H014 | ROMAN | roman_bm25_method_D | — | — | — | yes |
| H015 | ROMAN | roman_bm25_method_D | — | — | — | yes |
| H016 | ROMAN | roman_bm25_method_D | — | — | — | yes |
| H017 | URDU | urdu_bm25 | — | — | — | yes |
| H018 | URDU | urdu_bm25 | — | — | — | yes |
| H019 | URDU | urdu_bm25 | — | — | — | yes |
| H020 | URDU | urdu_bm25 | — | — | — | yes |
| H021 | URDU | urdu_bm25 | — | — | — | yes |
| H022 | URDU | urdu_bm25 | — | — | — | yes |
| H023 | URDU | urdu_bm25 | — | — | — | yes |
| H024 | URDU | urdu_bm25 | — | — | — | yes |
| H025 | ROMAN | roman_bm25_method_D | — | — | — | yes |
| H026 | ROMAN | roman_bm25_method_D | — | — | — | yes |
| H027 | ROMAN | roman_bm25_method_D | — | — | — | yes |
| H028 | ROMAN | roman_bm25_method_D | — | — | — | yes |
| H029 | ROMAN | roman_bm25_method_D | — | — | — | yes |
| H030 | ROMAN | roman_bm25_method_D | — | — | — | yes |
| H031 | ROMAN | roman_bm25_method_D | — | — | — | yes |
| H032 | ROMAN | roman_bm25_method_D | — | — | — | yes |
| H033 | URDU | urdu_bm25 | — | — | — | yes |
| H034 | URDU | urdu_bm25 | — | — | — | yes |
| H035 | ROMAN | roman_bm25_method_D | — | — | — | yes |
| H036 | ROMAN | roman_bm25_method_D | — | — | — | yes |
| H037 | URDU | urdu_bm25 | — | — | — | yes |
| H038 | URDU | urdu_bm25 | — | — | — | yes |
| H039 | ROMAN | roman_bm25_method_D | — | — | — | yes |
| H040 | ROMAN | roman_bm25_method_D | — | — | — | yes |

`top1_doc_id` in the CSV is the BM25 top hit for logging only. It is **not** gold.

---

## 6. Exclusions

**All 40** excluded under frozen protocol §13: missing `source_doc_id` (not in `[0, 111859]` because the field does not exist).

No query was dropped for being difficult. No substitution gold was created from `heldout_retrieval_template.csv` relevance marks (that would be circular and unofficial).

---

## 7. No test-set tuning

- Single run of `experiments/phase9_heldout_evaluation/run_phase9.py`
- k1, b, tokenizer, Method D, 198-key dictionary, detector, routing unchanged
- No RRF, fusion, reranker, dense model, or second attempt after seeing ranks
- Official known-item metrics left **undefined** rather than filled in

---

## Thesis interpretation

The **only** official ExactSource Hit@5 this project currently has is the frozen development/validation score:

**0.8718 on n=78 (QTRN known-item pool).**

H001–H040 cannot confirm or refute that number under the frozen known-item protocol, because they were never assigned a source article. Claiming an 80% or 87.18% **test** Hit@5 would be false.

STOP. No Phase 10.
