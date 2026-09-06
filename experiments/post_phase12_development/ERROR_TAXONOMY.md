# Stage 0 — mechanical error taxonomy (frozen dumps)

**Status:** FIRST PASS COMPLETE (2026-09-05). No retrieval. M0 unchanged.  
**Script:** `stage0_error_taxonomy.py`  
**Rows:** `stage0_error_taxonomy_rows.csv`  
**Counts:** `stage0_error_taxonomy_counts.json`

These buckets are **rank/label mechanics**, not a new official score. Do not tune M0, K, U, or H on this table.

## Codes

| Code | Meaning |
| --- | --- |
| HIT | Known-item source in Top-5 |
| RANK | Source in ranks 6–50 |
| ABSENT | Source not in Top-50 |
| NAT_OK | ≥1 A or B in Top-5 |
| NAT_FAIL_ALL_D | Top-5 all D |
| NAT_FAIL_ALL_C | Top-5 all C (topical, no A/B) |
| NAT_FAIL_NO_AB | Fail with mixed C/D (no A/B) |
| NAT_ZERO_HITS | No documents returned |

SPELL vs LOAN is **not** assigned here. That would be a second, query-text pass and is easy to overfit. Primary decision uses ABSENT vs RANK vs NAT_FAIL only.

## A. Official K001–K040 (known-item)

Hit@5 remains **27/40**.

| Script | HIT | RANK | ABSENT | n |
| --- | ---: | ---: | ---: | ---: |
| URDU | 26 | 2 | 0 | 28 |
| ROMAN | 1 | 1 | 10 | 12 |

Urdu misses are **RANK only** (K002 rank 6, K010 rank 49). Roman misses are almost all **ABSENT** (10/11). One Roman RANK (K031 rank 17).

**Implication:** a Top-50 reranker cannot fix official Roman K. Matching (query/index mapping) is the Roman KI problem. Rerank could only matter for the two Urdu near-misses and K031.

## B. Official U001–U040 (human)

Success@5 remains **23/40**.

| Script | NAT_OK | ALL_D | ALL_C | NO_AB | n |
| --- | ---: | ---: | ---: | ---: | ---: |
| URDU | 17 | 0 | 0 | 1 | 18 |
| ROMAN | 6 | 11 | 0 | 1 | 18 |
| MIXED | 0 | 1 | 3 | 0 | 4 |

Roman failures are mostly **empty Top-5** (all D), not “almost useful.” Mixed failures are mostly **all C** (wrong identity/topic, not a blank list).

**Implication:** Roman U is a usefulness/matching failure. Mixed U looks like P1 (topical neighbours without A/B). Do not treat them as one problem.

## C. R-dev KI (R001–R050) — M0 19/50

Hit@5 reproduced **19/50**.

| Script | HIT | RANK | ABSENT | n |
| --- | ---: | ---: | ---: | ---: |
| URDU | 11 | 4 | 2 | 17 |
| ROMAN | 1 | 0 | 4 | 5 |
| MIXED | 7 | 8 | 13 | 28 |

Largest KI miss mass is **MIXED ABSENT (13)** then **MIXED RANK (8)**. Roman KI n=5 is small; 4/5 ABSENT, same pattern as K but not a precise rate.

**Implication for Module 3 on R-dev:** mixed-script routing/matching is the biggest KI bin. A ROMAN-only Method C retest would address a small n here. Dual-path MIXED is the R-dev-sized target. That is **not** a licence to change official M0 MIXED routing without a locked protocol.

## D. R-dev NAT (R051–R100) — M0 12/50

Success@5 reproduced **12/50**.

| Script | NAT_OK | ALL_D | NO_AB | ZERO | n |
| --- | ---: | ---: | ---: | ---: | ---: |
| URDU | 1 | 0 | 0 | 0 | 1 |
| ROMAN | 7 | 23 | 6 | 1 | 37 |
| MIXED | 4 | 6 | 2 | 0 | 12 |

R080 is the ZERO_HITS Roman query. NAT is Roman-heavy; **23 all-D Roman** is the largest NAT fail bin.

**Implication:** NAT on R-dev is mostly “nothing useful in Top-5,” same family as U Roman all-D. Any new retriever **must** use union-pool labels before claiming Success@5 (M3-E lesson).

## E. What Module 3 should and should not be

From this pass, **do not** start with identity rerank as the main Roman fix.

| If Module 3 is… | Fits which bin? |
| --- | --- |
| ROMAN matching (query→Urdu or better romanization) | K Roman ABSENT; R-dev Roman ABSENT; U/R-dev Roman ALL_D |
| MIXED dual-path (Urdu BM25 ∪ Method D, fixed fuse) | R-dev MIXED ABSENT+RANK (largest KI mass) |
| Rerank M0 Top-50 | K Urdu RANK (n=2); R-dev MIXED/URDU RANK; U MIXED ALL_C |
| Another normalizer / char-3gram | Already failed Module 1–2 |

**Suggested Module 3 family (to lock in S1, not run yet):**  
Pre-register **one**:

1. **MIXED dual-path** if the thesis extra chapter is about R-dev KI mass, or  
2. **ROMAN matching** if the scientific target is the official Roman limitation (K 10/12 ABSENT, U 11/18 all-D).

Do not run both in one module. Do not stack them after seeing scores.

## F. Stop

S0 first pass is done. Next is **S1: write Module 3 protocol** after you choose (1) or (2). No retrieval until that file is locked.
