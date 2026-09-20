# R2-NG3-P5-REPRO — controlled experiment report

**Experiment ID:** R2-NG3-P5-REPRO  
**Status:** complete  
**Decision:** `R2-NG3 PARTIALLY SUPPORTED`  
**Timestamp (UTC, after gated comparison):** 2026-09-12T13:44:57Z  
**Branch / commit:** `research/ultra-v2-strengthening` / `fd54ac9b65c2db93e7e16fbf0c5a40b6a6025be1`

Protocol was frozen in `R2NG3_PREREGISTRATION.md` **before** this run’s official comparison tables. That file was not rewritten after seeing results.

This does **not** replace the Phase-2 R2-NG3 decision (`R2-NG3 PARTIALLY SUPPORTED`, 2026-09-11). It is a gated reproduction of the same method plus the dual-miss comparison that Phase 2 could not compute.

TEST query content was not opened. Phase 2/3/4 artifacts were not rewritten. n was not changed. Raw-Urdu grams and TF-IDF were not used.

---

## 1. Question

Can frozen R2-NG3 (character 3-grams on Method-D tokens, BM25 k1=1.5 b=0.75, Top-50) recover ExactSource golds that **both** Method-D BM25 **and** dense e5-small miss, on Roman KN TRAIN+DEV (n=51)?

---

## 2. Gates

| Gate | Result |
| --- | --- |
| Corpus SHA-256 `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231` | **PASS** |
| n=51 query IDs + `source_doc_id` vs Phase 3/4 | **PASS** |
| Dual-miss set size 25 and equal to Phase-4 `E_both_miss` | **PASS** |
| Method-D gold ranks vs `r2_b0_per_query.csv` | **PASS** (51/51) |
| NG3 gold ranks + hit flags vs `R2_NG3_PER_QUERY.csv` | **PASS** (51/51) |
| Method-D / NG3 feature-stream SHA vs Phase 2 | **PASS** |
| NG3 search second pass identical | **PASS** |

No rank was patched. Official comparison tables were written only after these gates passed.

---

## 3. Official metrics (Roman KN TRAIN+DEV, n=51)

| Method | Hit@1 | Hit@5 | Hit@10 | Hit@50 | MRR |
| --- | ---: | ---: | ---: | ---: | ---: |
| Method-D BM25 (frozen) | 1/51 = 1.96% | 4/51 = 7.84% | 4/51 = 7.84% | 6/51 = 11.76% | 0.0375 |
| Dense e5-small (frozen) | **5/51 = 9.80%** | **15/51 = 29.41%** | 16/51 = 31.37% | 22/51 = 43.14% | **0.1726** |
| Hybrid RRF (frozen) | 3/51 = 5.88% | 11/51 = 21.57% | **19/51 = 37.25%** | **25/51 = 49.02%** | 0.1422 |
| **R2-NG3 (reproduced)** | 3/51 = 5.88% | 6/51 = 11.76% | 6/51 = 11.76% | 8/51 = 15.69% | 0.0750 |

NG3 is stronger than Method D on every reported metric and much weaker than dense or hybrid as an overall retriever. That is expected: this phase tests a **narrow lexical bridge**, not a replacement first-stage.

Reproduced NG3 cells match the frozen Phase-2 treatment exactly (3 / 6 / 6 / 8 / 0.075).

---

## 4. Overlap (Hit@50, query-level)

**NG3 vs BM25**

|  | BM25 HIT | BM25 MISS |
| --- | ---: | ---: |
| NG3 HIT | 4 | 4 |
| NG3 MISS | 2 | 41 |

NG3 recovered BM25 misses: KN017, KN035, KN039, KN050.  
NG3 lost BM25 hits: KN012, KN014.

**NG3 vs Dense**

|  | Dense HIT | Dense MISS |
| --- | ---: | ---: |
| NG3 HIT | 3 | 5 |
| NG3 MISS | 19 | 24 |

**NG3 vs Hybrid RRF**

|  | Hybrid HIT | Hybrid MISS |
| --- | ---: | ---: |
| NG3 HIT | 6 | 2 |
| NG3 MISS | 19 | 24 |

The two Hybrid misses that NG3 hits are **KN035** and **KN050**. Hybrid cannot retrieve them because it only fuses BM25∪dense, and both systems missed those golds.

Live BM25∩NG3 **candidate-list** overlap (not a success metric): mean |Top-50 ∩ Top-50| = **4.47** (min 0, max 31). Mean union 94.6. Dense candidate IDs were not re-searched.

---

## 5. Dual-miss recovery (primary new comparison)

The 25 BM25∩Dense MISS-MISS queries were taken from frozen CSVs and matched Phase-4 `E_both_miss`.

**R2-NG3 recovers 2/25.**

| ID | NG3 rank | Note |
| --- | ---: | --- |
| KN050 | **1** | ROOM Category 1; `world`/`orld` 3-gram bridge |
| KN035 | **5** | outside ROOM Cat1 |

Remaining dual misses: **23/25**.

NG3-only vs BM25∪Dense (unique candidate generation): **exactly those two IDs**.

---

## 6. ROOM Category 1 (frozen n=11)

| System | Hit@50 |
| --- | ---: |
| Method-D BM25 | **0/11** |
| Dense | **3/11** (KN001, KN011, KN045) |
| Hybrid RRF | **3/11** (same three) |
| R2-NG3 | **1/11** (KN050) |

NG3’s ROOM recovery is **disjoint** from dense/hybrid: KN050 is a dual miss; the three dense ROOM hits are NG3 misses. Cross-form candidate generation is not solved (10/11 still out for NG3; 8/11 still out for dense).

VOCAB controls: KN017 enters NG3 Top-5 (as in Phase 2); KN020 and KN041 remain misses. KN017 is **not** a dual-miss recovery (dense already retrieved it).

---

## 7. Recovery / regression

Vs Method D (same as Phase 2, now confirmed under the gate):

- Recovered into Top-50: 4 (KN017, KN035, KN039, KN050)
- Lost from Top-50: 2 (KN012, KN014) — including a former Hit@5

Vs dense: NG3 is not competitive on coverage (8 vs 22 Hit@50). Its scientific value here is the **2 unique dual-miss golds**, not overall recall.

---

## 8. Runtime / hardware

| Step | Seconds |
| --- | ---: |
| Method D tokenize + 3-gram expand | 111.9 |
| NG3 BM25 build | 67.0 |
| Search × 51 (twice) | 2.9 |
| **Wall** | **200.0** |

CPU only. CUDA: no. Documents: 111,860. NG3 features: 68,929,325. Vocabulary: 9,140 terms.  
Python 3.13.9, numpy 2.3.5, Windows 11, 12-core Intel CPU.

---

## 9. Decision

`R2-NG3 PARTIALLY SUPPORTED`

Why not `SUPPORTED`: 23/25 dual misses remain; ROOM Category 1 is 1/11; NG3 is far behind dense on every aggregate; two Method-D successes are destroyed.

Why not `UNSUPPORTED`: 2 dual-miss golds (KN035, KN050) enter Top-50, including the hypothesized ROOM `orl`/`rld` case at rank 1, and those two are **outside** BM25∪Dense∪Hybrid.

Do **not** search n=4, add TF-IDF, add raw-Urdu grams, fuse NG3 into RRF, or start reranking from this file. Those would be later, separately pre-registered experiments.

---

## 10. Safety

| Check | Value |
| --- | --- |
| TEST accessed | NO |
| Frozen M0 modified | NO |
| PLOS modified | NO |
| Phase-2 R2-NG3 files overwritten | NO |
| Phase-3 / Phase-4 modified | NO |
| n changed / TF-IDF / raw-Urdu grams | NO |
| Fusion / reranking | NO |
| Parameter tuning | NO |
| Commit / push | NO |
