# PHASE7-LETTERNAME — controlled experiment report

**Experiment ID:** PHASE7-LETTERNAME  
**Status:** complete  
**Decision:** `PHASE7 UNSUPPORTED`  
**Timestamp (UTC, after gated evaluation):** 2026-09-12T14:12:33Z  
**Branch / commit:** `research/ultra-v2-strengthening` / `fd54ac9b65c2db93e7e16fbf0c5a40b6a6025be1`

Protocol was frozen in `PHASE7_PREREGISTRATION.md` **before** treatment scores. SHA-256 of that file immediately before execution, and again after scoring:

`d5937c525b8933a7abfa1adcc4086db605ad58aa5e75be3b3b4b1cbd6168fc43`

The preregistration was **not** rewritten after seeing results.

TEST query content was not opened. Phase 2–5 artifacts, PLOS, and frozen M0 were not modified. Documents were not re-indexed. Results were not fused or reranked. Wikidata was not used.

---

## 1. Question

Can expanding Latin acronym-like query tokens (length 2–4, not in the frozen 198-key dictionary) into Method-D-compatible Urdu **letter-name** romanizations recover ExactSource golds that word-level Method D misses?

---

## 2. Gates

| Gate | Result |
| --- | --- |
| Corpus SHA-256 `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231` | **PASS** |
| Dictionary SHA-256 `30c3f61a64ec641abbb3acdbc7a8bcaf197f0238f1bf9e76c2c7ce8e590f86a3` (198 keys) | **PASS** |
| n=51 query IDs + `source_doc_id` vs Phase 3/4/5 | **PASS** |
| Method-D gold ranks vs `r2_b0_per_query.csv` | **PASS** (51/51) |
| Reproduced Method-D aggregates 1 / 4 / 4 / 6 / 0.0375 | **PASS** |
| Letter-name toy `bbc` → `bi bi si` | **PASS** |
| Expanded-query search second pass identical | **PASS** |

No rank was patched. Official tables were written only after these gates passed.

---

## 3. Official metrics (Roman KN TRAIN+DEV, n=51)

| Method | Hit@1 | Hit@5 | Hit@10 | Hit@50 | MRR |
| --- | ---: | ---: | ---: | ---: | ---: |
| Method-D BM25 (frozen / reproduced) | 1/51 = 1.96% | 4/51 = 7.84% | 4/51 = 7.84% | 6/51 = 11.76% | 0.0375 |
| Dense e5-small (frozen CSV) | 5/51 = 9.80% | 15/51 = 29.41% | 16/51 = 31.37% | 22/51 = 43.14% | 0.1726 |
| Hybrid RRF (frozen CSV) | 3/51 = 5.88% | 11/51 = 21.57% | 19/51 = 37.25% | 25/51 = 49.02% | 0.1422 |
| R2-NG3 (frozen CSV) | 3/51 = 5.88% | 6/51 = 11.76% | 6/51 = 11.76% | 8/51 = 15.69% | 0.0750 |
| **PHASE7-LETTERNAME** | **0/51 = 0.00%** | **0/51 = 0.00%** | **0/51 = 0.00%** | **1/51 = 1.96%** | **0.0007** |

The single Top-50 hit is **KN004 at rank 29**. That gold was already Method-D Hit@1 (rank 1). Letter-name expansion moved it from rank 1 to rank 29; it is not a recovered miss.

Queries with ≥1 expanded token: **49/51**. Unexpanded: KN041, KN046 (no 2–4 letter token outside the 198-key dict).

---

## 4. Overlap (Hit@50, query-level)

**Phase 7 vs Method-D BM25**

|  | BM25 HIT | BM25 MISS |
| --- | ---: | ---: |
| P7 HIT | 1 | 0 |
| P7 MISS | 5 | 45 |

Recovered BM25 misses: **none**.  
Lost BM25 hits: KN012, KN014, KN023, KN038, KN048.

**Phase 7 vs Dense**

|  | Dense HIT | Dense MISS |
| --- | ---: | ---: |
| P7 HIT | 0 | 1 |
| P7 MISS | 22 | 28 |

The P7-hit / dense-miss cell is again **KN004** (already a BM25 success; dense rank 107).

**Phase 7 vs NG3**

|  | NG3 HIT | NG3 MISS |
| --- | ---: | ---: |
| P7 HIT | 1 | 0 |
| P7 MISS | 7 | 43 |

---

## 5. Recovery of the 23 four-way misses

**0/23.** No ID from the frozen Phase-6 list entered Top-50.

Acronym-shaped tokens among those 23 **did** expand under the frozen rule when they were not dictionary keys, including:

| ID | Token | Expanded (`naive_roman_word`) | P7 rank |
| --- | --- | --- | ---: |
| KN006 | `ipl` | `aaii pi ail` | outside Top-50 |
| KN025 | `adb` | `ae di bi` | outside Top-50 |
| KN042 | `sbp` | `ais bi pi` | outside Top-50 |
| KN047 | `fbr` | `aif bi aar` | outside Top-50 |

`cpec` / `psl` were correctly **not** expanded (frozen dict keys). Length-5+ names (`gmail`, `twitter`, `aladdin`, `kangana`) were correctly **not** expanded.

The letter-name channel therefore fired on the hypothesized org-initials cases and still produced **zero** ExactSource Top-50 recoveries.

---

## 6. ROOM Category 1 (frozen n=11)

| System | Hit@50 |
| --- | ---: |
| Method-D BM25 | **0/11** |
| Dense | **3/11** (KN001, KN011, KN045) |
| Hybrid RRF | **3/11** (same three) |
| R2-NG3 | **1/11** (KN050) |
| PHASE7-LETTERNAME | **0/11** |

---

## 7. Recovery / regression vs Method D

- Recovered into Top-50: **0**
- Lost from Top-50: **5** (KN012, KN014, KN023, KN038, KN048), including three former Hit@5 (KN012 rank 5; KN023 and KN038 rank 3)
- Retained but degraded: KN004, rank 1 → 29

Mechanistic note (not a retune): `^[a-z]{2,4}$` also expands ordinary short Roman words (`air`, `zim`, `kab`, `cup`, `tax`, …) into letter-name tokens, so most queries are rewritten rather than receiving a surgical acronym map. That is the frozen rule’s actual behavior, not a second method.

---

## 8. Runtime / hardware

| Step | Seconds |
| --- | ---: |
| Search × 51 (control + treatment + repeat) | 1.1 |
| **Wall** (includes corpus/dict SHA + Method-D cache load) | **12.7** |

CPU only. CUDA: no. Documents: 111,860 (not reprocessed).  
Python 3.13.9, numpy 2.3.5, Windows 11, 12-core Intel CPU.

---

## 9. Decision

`PHASE7 UNSUPPORTED`

Why not `PARTIALLY SUPPORTED`: the preregistration required at least one of the 23, or a clear acronym gold, to enter Top-50. Neither occurred. The only Hit@50 is a pre-existing Method-D success that got worse.

Why not `BLOCKED`: all gates passed.

This closes **Option 1 (letter-name rule only)** as a candidate-generation method on this population. Wikidata / Option 2 is **not** started from this file.

---

## 10. Safety

| Check | Value |
| --- | --- |
| TEST accessed | NO |
| Gazetteer built from the 23 / n=51 / gold docs | NO (26-letter public names only) |
| Wikidata | NO |
| Frozen M0 / PLOS modified | NO |
| Phase 2 / 3 / 4 / 5 modified | NO |
| Documents re-indexed | NO |
| Fusion / reranking | NO |
| Parameter tuning / second table | NO |
| Commit / push | NO |
