# PHASE8-3WAY-RRF — controlled experiment report

**Experiment ID:** PHASE8-3WAY-RRF  
**Status:** complete  
**Decision:** `PHASE8 UNSUPPORTED`  
**Timestamp (UTC, after gated evaluation):** 2026-09-13T07:10:43Z  
**Branch / commit:** `research/ultra-v2-strengthening` / `fd54ac9b65c2db93e7e16fbf0c5a40b6a6025be1`

Protocol was frozen in `PHASE8_PREREGISTRATION.md` **before** treatment scores. SHA-256 of that file immediately before execution, and again after scoring:

`fcd93d2fccadd561a994bd3feac12fbcadb301c5665626edb70fcee0cf515532`

The preregistration was **not** rewritten after seeing results.

TEST query content was not opened. Phase 2–7 artifacts were not modified. k was not searched. Lists were not weighted. Document embeddings were not regenerated.

---

## 1. Question

Does unweighted RRF (k=60) of frozen Method-D BM25, dense e5-small, and R2-NG3 Top-50 lists improve ExactSource retrieval — especially Hit@5 — over frozen 2-way Hybrid RRF, as a ranking method rather than a Phase-6 union count?

---

## 2. Gates

| Gate | Result |
| --- | --- |
| Input CSV SHA-256 vs Phase 6 (BM25 / Dense / NG3) | **PASS** |
| Corpus SHA-256 `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231` | **PASS** |
| n=51 query IDs + golds vs Phase 3/4/5 | **PASS** |
| Method-D gold ranks vs `r2_b0_per_query.csv` | **PASS** |
| Dense gold rank + rank-1 vs `DENSE_PER_QUERY.csv` | **PASS** |
| NG3 gold ranks vs `R2NG3_PER_QUERY.csv` + feature-stream SHA | **PASS** |
| 2-way RRF (Phase-4 `fuse_rrf` k=60) vs `HYBRID_PER_QUERY.csv` | **PASS** |
| 3-way RRF second pass identical | **PASS** |

Official tables were written only after these gates passed.

---

## 3. Official metrics (Roman KN TRAIN+DEV, n=51)

| Method | Hit@1 | Hit@5 | Hit@10 | Hit@50 | MRR |
| --- | ---: | ---: | ---: | ---: | ---: |
| Method-D BM25 | 1 | 4 | 4 | 6 | 0.0375 |
| Dense e5-small | **5** | **15** | 16 | 22 | **0.1726** |
| Hybrid RRF 2-way (frozen) | 3 | 11 | **19** | **25** | 0.1422 |
| R2-NG3 | 3 | 6 | 6 | 8 | 0.0750 |
| **PHASE8 3-way RRF k=60** | 4 | **8** | 14 | 24 | 0.1310 |

3-way RRF is worse than 2-way Hybrid on Hit@5, Hit@10, Hit@50, and MRR. Hit@1 rises 3→4 (KN004, KN017, KN038, KN048). Dense remains the strongest single first-stage on Hit@1/5/MRR.

---

## 4. McNemar vs 2-way Hybrid (`exact_mcnemar`, copied verbatim)

n=51 is small. Non-significant p-values are underpowered, not proof of equality.

**Hit@5** (control = 2-way Hybrid, treatment = 3-way)

| Item | Value |
| --- | --- |
| 3-way-only hits (n01) | 1 (KN038) |
| 2-way-only hits (n10) | 4 (KN014, KN034, KN046, KN049) |
| Discordant pairs | 5 |
| p two-sided | **0.375** |
| Significant at p&lt;0.05 | **NO** |

**Hit@50**

| Item | Value |
| --- | --- |
| 3-way-only hits (n01) | 2 (KN035, KN050) |
| 2-way-only hits (n10) | 3 (KN030, KN043, KN045) |
| Discordant pairs | 5 |
| p two-sided | **1.0** |
| Significant at p&lt;0.05 | **NO** |

Phase 6’s **union** Hit@5 advantage vs 2-way Hybrid (p=0.006348) does **not** survive RRF re-ranking. Unweighted RRF of the three lists is not the same object as pool membership.

---

## 5. Recovery of the 23 four-way misses

**0/23.** None of the remaining four-way misses entered the 3-way Top-50.

KN035 and KN050 were already NG3 Top-50 successes (and were excluded from that 23). 3-way RRF keeps them in Top-50 but **dilutes** their NG3 ranks: KN050 1→9; KN035 5→11.

---

## 6. ROOM Category 1 (n=11)

| System | Hit@50 | IDs |
| --- | ---: | --- |
| Method-D BM25 | 0/11 | — |
| Dense | 3/11 | KN001, KN011, KN045 |
| Hybrid 2-way | 3/11 | KN001, KN011, KN045 |
| R2-NG3 | 1/11 | KN050 |
| PHASE8 3-way | 3/11 | KN001, KN011, **KN050** |

Net ROOM count is unchanged. 3-way **loses** dense/hybrid ROOM gold KN045 (hybrid 45 → 3-way 67) and **gains** NG3 ROOM gold KN050 (hybrid miss → rank 9).

---

## 7. Recovery / regression vs 2-way Hybrid

Hit@5: recovered KN038 (hybrid 6 → 1); lost KN014 (3→13), KN034 (5→8), KN046 (4→8), KN049 (2→7).

Hit@50: recovered KN035 (rank 11), KN050 (rank 9); lost KN030 (47→71), KN043 (44→66), KN045 (45→67).

Phase-6 union-only golds:

| ID | 2-way hybrid | 3-way RRF | Note |
| --- | ---: | ---: | --- |
| KN035 | miss | **11** | NG3 rank 5; diluted |
| KN040 | 54 (miss) | **81** (miss) | Dense-only; NG3 noise pushes it further out |
| KN050 | miss | **9** | NG3 rank 1; diluted |

Adding NG3 as a third **unweighted** list injects many non-gold documents. That is why union membership at Hit@5 does not become a better ranked Top-5.

---

## 8. Runtime / hardware

| Step | Seconds |
| --- | ---: |
| Method-D cache load | 22.5 |
| BM25 search × 51 | 0.7 |
| Dense npy load | 0.6 |
| e5-small load (CPU) | 71.9 |
| Query encode n=51 | 2.3 |
| Dense cosine × 51 | 1.8 |
| NG3 tokenize + expand (repro, not a new method) | 245.5 |
| NG3 BM25 build | 131.4 |
| NG3 search × 51 | 2.3 |
| **Wall** | **511.0** |

CPU only. CUDA: no. Document embeddings regenerated: **no**.  
Python 3.13.9, numpy 2.3.5, Windows 11, 12-core Intel CPU.

---

## 9. Decision

`PHASE8 UNSUPPORTED`

Why not `PARTIALLY SUPPORTED`: KN035/KN050 in the 3-way Top-50 are already NG3 successes at **better** ranks. 3-way RRF does not discover them; it only partially preserves them while making 2-way Hybrid worse on Hit@5 (11→8), Hit@10 (19→14), Hit@50 (25→24), and MRR (0.1422→0.1310), including a ROOM Cat1 regression (KN045). McNemar vs 2-way is not significant. The 23 remaining four-way misses stay at 0.

Why not `BLOCKED`: all gates passed.

This closes unweighted 3-way RRF (k=60) as an improvement over frozen 2-way Hybrid on this population. Do **not** search k, add weights, or start reranking from this file.

---

## 10. Safety

| Check | Value |
| --- | --- |
| TEST accessed | NO |
| Frozen M0 / PLOS modified | NO |
| Phase 2–7 modified | NO |
| k searched / weights | NO |
| Dense embeddings regenerated | NO |
| Reranking / Phase 9 | NO |
| Commit / push | NO |
