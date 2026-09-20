# PHASE9-WPTITLES — controlled experiment report

**Experiment ID:** PHASE9-WPTITLES  
**Status:** complete  
**Decision:** `PHASE9 PARTIALLY SUPPORTED`  
**Timestamp (UTC, after gated evaluation):** `2026-09-17T12:16:41Z`  
**Branch / commit:** `research/ultra-v2-strengthening` / `fd54ac9b65c2db93e7e16fbf0c5a40b6a6025be1`  
**Match rule:** v2 NO-GO correction (§3.2a), frozen before scoring

Preregistration SHA-256 (unchanged through scoring):

`3a3956cbc0749f2f8189a19698a05bc1e3a854d7a164a70a66ff972e947f0372`

TEST was not opened. Phase 2–8, PLOS, and M0 were not modified. Documents were not re-indexed. No fusion, rerank, or second matching procedure after scores.

---

## 1. Question

Can a query-independent Urdu↔English Wikipedia title/redirect table, under the frozen v2 match rule, recover ExactSource golds that Method-D BM25 / dense / NG3 / 2-way hybrid all miss, by expanding matched Urdu titles into Method-D roman tokens on the frozen Method-D BM25 index?

---

## 2. Gates

| Gate | Result |
| --- | --- |
| Corpus SHA-256 `8992a6acca…a9f231` | **PASS** |
| Dictionary SHA-256 `30c3f61a64…0f86a3` (198 keys) | **PASS** |
| Title CSV SHA-256 `7686f02d5b…cf55d` | **PASS** |
| Prereg SHA-256 `3a3956cbc0…7f0372` | **PASS** |
| Wordlist SHA-256 `d6b3e04f1a…05ed86` (9,894) | **PASS** |
| n=51 query IDs + golds vs Phase 2–5 | **PASS** |
| Method-D gold ranks vs `r2_b0_per_query.csv` | **PASS** |
| Reproduced Method-D 1 / 4 / 4 / 6 / 0.0375 | **PASS** |
| Expanded-query search second pass identical | **PASS** |

---

## 3. Official metrics (Roman KN TRAIN+DEV, n=51)

| Method | Hit@1 | Hit@5 | Hit@10 | Hit@50 | MRR |
| --- | ---: | ---: | ---: | ---: | ---: |
| Method-D BM25 (frozen / reproduced) | 1/51 = 1.96% | 4/51 = 7.84% | 4/51 = 7.84% | 6/51 = 11.76% | 0.0375 |
| Dense e5-small (frozen CSV) | 5/51 = 9.80% | 15/51 = 29.41% | 16/51 = 31.37% | 22/51 = 43.14% | 0.1726 |
| Hybrid RRF (frozen CSV) | 3/51 = 5.88% | 11/51 = 21.57% | 19/51 = 37.25% | 25/51 = 49.02% | 0.1422 |
| R2-NG3 (frozen CSV) | 3/51 = 5.88% | 6/51 = 11.76% | 6/51 = 11.76% | 8/51 = 15.69% | 0.0750 |
| **PHASE9-WPTITLES (v2)** | **1/51 = 1.96%** | **5/51 = 9.80%** | **6/51 = 11.76%** | **10/51 = 19.61%** | **0.0478** |

Queries with ≥1 title hit under v2: **22/51**.

---

## 4. Overlap (Hit@50, query-level)

**Phase 9 vs Method-D BM25**

|  | BM25 HIT | BM25 MISS |
| --- | ---: | ---: |
| P9 HIT | 5 | 5 |
| P9 MISS | 1 | 40 |

Recovered BM25 misses (Hit@50): **KN027, KN029, KN030, KN033, KN051**.  
Lost BM25 hit: **KN014** (BM25 rank 44 → outside Top-50 after `ghalti` → TV-serial expansion).

**Phase 9 vs Dense**

|  | Dense HIT | Dense MISS |
| --- | ---: | ---: |
| P9 HIT | 4 | 6 |
| P9 MISS | 18 | 23 |

**Phase 9 vs NG3**

|  | NG3 HIT | NG3 MISS |
| --- | ---: | ---: |
| P9 HIT | 4 | 6 |
| P9 MISS | 4 | 37 |

**Phase 9 vs 2-way Hybrid**

|  | Hybrid HIT | Hybrid MISS |
| --- | ---: | ---: |
| P9 HIT | 8 | 2 |
| P9 MISS | 17 | 24 |

---

## 5. Recovery of the 23 four-way misses

**2/23** enter Top-50:

| ID | Match | Expansion (abbrev.) | P9 rank | Status |
| --- | --- | --- | ---: | --- |
| KN027 | chameleon → Chameleon → گرگٹ | `… grgt` | **3** | Hit@5 (was BM25 miss) |
| KN051 | gmail → Gmail → جی میل | `… ji mil j ml` | **12** | RANK (Top-50, not Top-5) |

Remaining **21/23** still outside Top-50.

### Focus queries with legitimate-looking v2 expansions

| ID | Expansion fired? | P9 rank | Verdict |
| --- | --- | ---: | --- |
| KN006 | yes (`ipl` → Indian Premier League) | outside Top-50 | MISS |
| KN018 | yes (`mabni`, `fable`) | outside Top-50 | MISS |
| KN037 | yes (`chehre`) | outside Top-50 | MISS |
| KN044 | yes (`facebook`) | outside Top-50 | MISS |
| KN045 | yes (`facebook`) | outside Top-50 | MISS |
| KN047 | yes (`sindh`, `sales tax`); `fbr` still absent | outside Top-50 | MISS |
| KN051 | yes (`gmail`) | **12** | RANK / recovered dual-miss |

So among the seven focus IDs, only **KN051** is recovered into Top-50. IPL matching alone did not put KN006’s gold in Top-50.

---

## 6. ROOM Category 1 (n=11)

| Method | Hit@50 | IDs |
| --- | ---: | --- |
| Method-D BM25 | 0/11 | — |
| Dense | 3/11 | KN001, KN011, KN045 |
| Hybrid | 3/11 | KN001, KN011, KN045 |
| NG3 | 1/11 | KN050 |
| **Phase 9** | **1/11** | **KN051** |

Phase 9’s ROOM hit (KN051) is **disjoint** from dense/hybrid/NG3 ROOM hits.

---

## 7. Regressions vs frozen Method-D BM25

**Hit@50**

- Recovered: KN027 (rank 3), KN029 (4), KN030 (46), KN033 (37), KN051 (12)
- Regressed: **KN014** only (44 → miss), via wrong-sense `Ghalti` (TV serial)

**Hit@5**

- Recovered: KN027, KN029
- Regressed: **KN023** (BM25 rank 3 → P9 rank 6; still Hit@50). `aziz mian` expansion pushed gold from Top-5 to rank 6.

BM25 Top-50 successes retained: **5/6**.

---

## 8. Decision

**`PHASE9 PARTIALLY SUPPORTED`**

Rationale (prereg §5): two of the 23 four-way misses enter Top-50 (KN027, KN051), and net Hit@50 rises 6→10 vs Method D, but most of the 23 remain out; several “legitimate” title matches (IPL, Facebook, Gmail siblings, Sindh/sales tax) do not recover their golds; one BM25 Top-50 success is lost.

No second matching procedure. Artifacts: `PHASE9_PER_QUERY.csv`, `artifacts/phase9_summary.json`, `artifacts/phase9_config.json`.
