# ULTRA v2 Failure Decomposition & Recoverable Headroom Analysis

**Date (local):** 2026-09-22  
**Branch:** `research/roman-urdu-adaptive-retrieval`  
**HEAD:** `3b2e829bf9769d16f9b604ee68d7cc50ce128fa7`  
**Nature:** Diagnostic only — no new retrieval, no method, no TEST access  
**Decision:** **LOW / STRUCTURALLY LIMITED HEADROOM** (for the ~80% Hit@5 target)

`TEST_CONTENT_ACCESSED = FALSE`

---

## 0. Repository & TEST integrity

| Field | Value |
| --- | --- |
| Branch | `research/roman-urdu-adaptive-retrieval` |
| HEAD | `3b2e829bf9769d16f9b604ee68d7cc50ce128fa7` |
| Working tree | Untracked `experiments/ieee_adaptive/` only |
| Program A modified | **No** |
| Program B modified | **No** |
| TEST query CSVs opened | **No** |
| TEST seal metadata inspected | **Yes** (`benchmark/test/seal.json` only) |
| Seal kind | `ultra_v2_test_seal` |
| Seal aggregate SHA-256 | `48610601209c3723a7252bb9a197d8fbbece18640e0bf7aef972884816ab46c4` |
| Sealed files (names only) | `queries_kn.csv`, `queries_nl.csv` |

---

## 1. Audit of existing Program B evidence

| Path | Purpose | Split | n | Gold | Ranks | SHA-256 |
| --- | --- | --- | ---: | --- | --- | --- |
| `experiments/ultra_v2/phase13_population/artifacts/scoring/PHASE13_SCORING_PER_QUERY.csv` | **Primary** n=80 per-query ranks + Hit@k | TRAIN+DEV | 80 | source_doc_id | BM25/NG3/Dense/Hybrid (+P9/P10) | `f59c37102ba5c212e7b2c14600cf3781732eef98757379f51c26f0a250fe5d66` |
| `experiments/ultra_v2/phase13_population/artifacts/scoring/phase13_scoring_summary.json` | Aggregated n=80 / n=51 / n=29 metrics | TRAIN+DEV | 80 | no | aggregates | `9c619f6a3bf1655e7e17f181bd872cd1fc5dd1c56954f7652dc535b2a2455cf9` |
| `experiments/ultra_v2/PHASE14_FINAL_REPORT.md` | Frozen Program B citation source | TRAIN+DEV | 80 | narrative | tables | `0cf7c9a928e9d9e734293d18c1d8fbab8c167775340a880d76c0dcaeea862f7b` |
| `experiments/ultra_v2/phase6_diagnostics/PHASE6_DIAGNOSTICS_REPORT.md` | n=51 MISS/RANK + union McNemar | TRAIN+DEV | 51 | no new | derived | (frozen phase6) |
| `experiments/ieee_adaptive/C2A_CASE_ANNOTATIONS.csv` | Pre-existing labels for 31 BND miss50 | TRAIN+DEV | 31 | mechanism labels | no | `8988da1adbff940ee30aa07fd36d1e788c5d2e919eba66b980beb85ed138e009` |

**Population:** Roman KN ExactSource TRAIN+DEV **n=80** (51 original W1 + 29 Phase-13 LLM1).  
**Gold definition:** ExactSource — gold = `source_doc_id` must appear in Top-k.  
**Not used:** TEST queries, TEST golds, TEST retrieval dumps.

### 1.1 Prompt claim verification (from Phase 13 / Phase 14)

| Claim | Repository value | Match |
| --- | --- | --- |
| Method-D Hit@5 = 5/80 = 6.25% | 5/80 | **Yes** |
| Dense Hit@5 = 20/80 = 25% | 20/80 | **Yes** |
| Hybrid Hit@50 = 40/80 = 50% | 40/80 | **Yes** |
| Oracle among BM25/NG3/Dense Hit@5 = 28/80 = 35% | 28/80 | **Yes** |
| BM25 ∪ NG3 ∪ Dense Top-50 misses = 31/80 | 31/80 | **Yes** |

---

## 2. Annotation protocol (pre-declared)

### 2.1 Primary category (mutually exclusive, structural)

Assigned from frozen Hit@k flags only:

| Category | Rule |
| --- | --- |
| **SUCCESS** | At least one of BM25 / NG3 / Dense has ExactSource Hit@5 |
| **RANKING_FAILURE** | Gold in BM25 ∪ NG3 ∪ Dense Top-50, but no expert Hit@5 |
| **CANDIDATE_GENERATION_FAILURE** | Gold absent from BM25 ∪ NG3 ∪ Dense Top-50 |

Categories D/E/F (representation / ambiguity / benchmark) are **not** used as primary unless separate evidence forces it. Structural location of gold is primary; linguistic mechanism is secondary.

### 2.2 Secondary mechanism (CG failures only)

Reuse **pre-existing** C2A classifications for the 31 BND miss50 queries (no new gold inspection):

| C2A label | Secondary mechanism |
| --- | --- |
| A | acronym_institution |
| B | entity_name |
| C | semantic_paraphrase |
| D | orthographic_variation |
| E | lexical_mismatch |
| G | other |

### 2.3 Recoverability class (heuristic, not a method claim)

| Class | Rule |
| --- | --- |
| plausibly_recoverable | C2A A or D |
| uncertain | C2A B, G, or missing |
| likely_intrinsically_difficult | C2A C or E |
| ranking_headroom | primary = RANKING_FAILURE |

---

## 3. Existing retrieval coverage (n=80)

| System | Hit@1 | Hit@5 | Hit@10 | Hit@20 | Hit@50 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Method-D BM25 | 1 | **5** | 5 | 6 | 13 |
| NG3 | 4 | 10 | 13 | 16 | 19 |
| Dense e5-small | 9 | **20** | 23 | 29 | 36 |
| Hybrid RRF (BM25+Dense) | 5 | 17 | 25 | 29 | **40** |

Percentages: Dense Hit@5 = 25.0%; Hybrid Hit@50 = 50.0%.

---

## 4. Perfect-ranking upper bounds

**Definition (`PERFECT_RANKING_UPPER_BOUND`):**  
If gold appears in the named Top-50 candidate pool, a perfect ranker can place it at rank ≤5.  
This is an **oracle/upper bound**, not an achievable system score.

| Candidate pool | Gold in Top-50 | Ceiling Hit@5 | % |
| --- | ---: | ---: | ---: |
| BM25 Top-50 | 13 | **13** | 16.25% |
| NG3 Top-50 | 19 | **19** | 23.75% |
| Dense Top-50 | 36 | **36** | 45.00% |
| Hybrid Top-50 | 40 | **40** | 50.00% |
| BM25 ∪ NG3 | 23 | **23** | 28.75% |
| BM25 ∪ Dense | 44 | **44** | 55.00% |
| NG3 ∪ Dense | 47 | **47** | 58.75% |
| **BM25 ∪ NG3 ∪ Dense** | **49** | **49** | **61.25%** |

Note: Hybrid Hit@50 = 40 < BM25 ∪ Dense = 44 because RRF’s truncated Top-50 need not retain every union member (4 queries are in BM25 ∪ Dense Top-50 but outside Hybrid’s ranked Top-50).

---

## 5. Failure decomposition (structural, BND experts)

| Stage | Queries | Percentage |
| --- | ---: | ---: |
| SUCCESS (any of BM25/NG3/Dense Hit@5) | 28 | 35.00% |
| RANKING_FAILURE (in BND Top-50, not Top-5) | 21 | 26.25% |
| CANDIDATE_GENERATION_FAILURE (absent from BND Top-50) | 31 | 38.75% |
| **PERFECT_RANKING ceiling (BND union)** | **49** | **61.25%** |
| Current best deployable Hit@5 (Dense) | 20 | 25.00% |
| Hybrid Hit@5 (deployable fusion) | 17 | 21.25% |

**RQ1:** Candidate-generation failures = **31/80 (38.75%)**.  
**RQ2:** Ranking failures (gold already in BND pool) = **21/80 (26.25%)**.  
**RQ3:** Perfect ranking over BND recovers at most **49/80 (61.25%)** Hit@5.  
**RQ4:** Union of existing generators yields the same **49/80** ceiling (membership), of which **28** are already Hit@5 under some expert.

---

## 6. Ranking headroom (rank buckets)

### 6.1 Best rank among BM25 ∪ NG3 ∪ Dense

| Bucket | n | % of 80 |
| --- | ---: | ---: |
| Ranks 1–5 | 28 | 35.00% |
| Ranks 6–10 | 5 | 6.25% |
| Ranks 11–20 | 7 | 8.75% |
| Ranks 21–50 | 9 | 11.25% |
| Miss Top-50 | 31 | 38.75% |

Of the **49** in-pool queries: **28/49 (57%)** already ≤5 under some expert; **21/49 (43%)** are ranking headroom (6–50).

### 6.2 Per-system (for context)

| System | 1–5 | 6–10 | 11–20 | 21–50 | Miss50 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Dense | 20 | 3 | 6 | 7 | 44 |
| Hybrid | 17 | 8 | 4 | 11 | 40 |
| NG3 | 10 | 3 | 3 | 3 | 61 |
| BM25 | 5 | 0 | 1 | 7 | 67 |

Hybrid has **23** Rank failures (Hit@50 ∧ ¬Hit@5). Dense has **16**.

**Interpretation:** Ranking headroom is real but **secondary**. The larger mass is **absence from the pool**.

---

## 7. Cross-system complementarity (Hit@50)

| Pattern | n |
| --- | ---: |
| Dense only | 26 |
| none (all miss50) | 31 |
| BM25+NG3 | 6 |
| NG3 only | 5 |
| NG3+Dense | 5 |
| BM25+NG3+Dense | 3 |
| BM25 only | 2 |
| BM25+Dense | 2 |

**Complementarity exists:** BM25-only and NG3-only recoveries are non-zero; NG3 ∪ Dense (47) > Dense (36); BND (49) > BM25 ∪ Dense (44).

**Complementarity ≠ predictability:** C1 already showed query-only routing cannot exploit this (routed 17/80 < Dense 20/80). This diagnostic **reaffirms complementarity without repeating C1**.

Oracle best-of-3 Hit@5 = **28/80** vs Dense **20/80** vs Hybrid **17/80**.

---

## 8. Dominant failure mechanisms (31 CG failures)

From frozen C2A labels (n=31; counts match C2A probe):

| Mechanism | n | % of CG | % of n=80 |
| --- | ---: | ---: | ---: |
| entity_name (non-institutional) | 18 | 58.1% | 22.5% |
| acronym_institution | 6 | 19.4% | 7.5% |
| orthographic_variation | 3 | 9.7% | 3.75% |
| semantic_paraphrase | 2 | 6.5% | 2.5% |
| lexical_mismatch | 1 | 3.2% | 1.25% |
| other | 1 | 3.2% | 1.25% |

**RQ5–RQ6:** Failures are **not** a single mechanism. Entity/name mismatch dominates the CG tail, but institutional, orthographic, and paraphrase residues remain. The overall bottleneck is **distributed CG + secondary ranking**, not one concentrated bug.

### Recoverability heuristic on the 31

| Class | n |
| --- | ---: |
| uncertain | 19 |
| plausibly_recoverable (A∪D) | 9 |
| likely_intrinsically_difficult (C∪E) | 3 |

Even optimistic counting of A∪D does **not** close the 80% gap (see §10). C2a already closed dedicated institutional-alias pursuit (6 < 8 threshold).

---

## 9. Targeted literature mapping (failure *type*, not novelty hunt)

| Observed structure | Technical problem class | Known literature family |
| --- | --- | --- |
| 31/80 outside all first-stage Top-50 | First-stage / candidate-generation failure | Dense vs lexical first-stage; CLIR recall |
| 21/80 in pool but not Top-5 | Ranking / fusion ordering | Reranking; RRF dilution (Phase 8) |
| Entity-name CG misses | Cross-script / multilingual entity retrieval | JRC-Names; name transliteration IR |
| Acronym ↔ descriptive alias | Acronym expansion / bilingual alias | Institutional CLIR (prevalence low here) |
| Orthographic Roman variation | Spelling / script robustness | FIRE / MSIR; typo-aware retrieval |
| Semantic paraphrase | Cross-lingual semantic mismatch | Multilingual dense retrieval limits |

**What kind of problem is this?**  
A **multilingual known-item candidate-generation ceiling** problem with a **secondary ranking-ordering** problem — not a pure reranking problem, and not a single linguistic mechanism.

---

## 10. 80% target analysis

| Quantity | Value |
| --- | ---: |
| Current best Hit@5 (Dense) | **20/80 = 25%** |
| Target 80% | **64/80** |
| Additional successes required from Dense | **44** |
| Oracle any-expert Hit@5 | **28/80** |
| Additional from oracle to 64 | **36** |
| Ranking headroom (BND in-pool, not expert Top-5) | **21** |
| BND candidate-generation ceiling | **49/80 = 61.25%** |
| Queries outside all BND pools | **31** |
| Gap beyond BND ceiling to 64 | **15** |

### Mandatory compatibility statement

> **80% (64/80) is NOT theoretically compatible with the current BM25 ∪ NG3 ∪ Dense Top-50 candidate pool**, even under perfect ranking.  
> Math: ceiling = 49 < 64.  
> Therefore **a reranker alone cannot reach 80%** on this benchmark using that pool.  
> Reaching 80% would require recovering gold into the candidate pool for **at least 15** currently absent queries **in addition to** perfect ranking of all 49 in-pool golds (and beating Dense’s 20 already-successful cases without regressions).

Hybrid’s perfect-ranking ceiling is even lower (**40/80 = 50%**).

---

## 11. Recoverable headroom summary

### Ranking headroom

**21/80** queries: gold already in BND Top-50 but not in any expert’s Top-5.  
Theoretically, perfect selection/ranking among existing lists could raise Hit@5 from Dense **20** toward oracle **28**, and perfect pool ranking toward **49**.

### Candidate-generation headroom

**31/80** absent from BND Top-50.  
Do **not** assume all are recoverable. Heuristic: **9** plausibly, **19** uncertain, **3** likely hard. Prior Phase 9/10/11 and closed C2a show expanding this pool with existing frozen resources is difficult.

### Headroom vs 80%

| Path | Max Hit@5 | Reaches 64? |
| --- | ---: | --- |
| Perfect rank Dense Top-50 | 36 | No |
| Perfect rank Hybrid Top-50 | 40 | No |
| Perfect rank BND union | 49 | **No** |
| Perfect rank BND + recover all 31 CG | 80 | Yes (vacuous / assumes solved CG) |
| Perfect rank BND + recover only A∪D (9) | 58 | **No** |

---

## 12. Answers to RQs

| RQ | Answer |
| --- | --- |
| RQ1 CG failures | **31/80** |
| RQ2 Ranking failures | **21/80** |
| RQ3 Perfect ranking over existing pool | **≤49/80** |
| RQ4 Union of generators | Same **49/80** membership ceiling |
| RQ5 Dominant mechanisms | Entity-name (18/31) among CG; overall CG dominates misses |
| RQ6 Concentrated vs distributed | **Distributed** across entity / institutional / ortho / paraphrase |
| RQ7 Justify another improvement experiment? | **Modest gains yes; path to ~80% no** (see decision) |
| RQ8 Is ~80% compatible? | **No** with current candidate structure |

---

## 13. Reproduction

```text
python experiments/ieee_adaptive/run_failure_decomposition.py
```

- Inputs: Phase 13 per-query CSV + C2A annotations (TRAIN/DEV only).  
- Outputs:  
  - `FAILURE_DECOMPOSITION_PER_QUERY.csv` (SHA `851081add6c5870b2be825efc11ffa39d736bb90d6b8a16830990bbd99dd0427`)  
  - `FAILURE_MECHANISM_SUMMARY.csv` (SHA `8db95af3af30435c20fecf6001856395bf34bccc36ae32ade41aea7402661a81`)  
  - `FAILURE_DECOMPOSITION_SUMMARY.json` (SHA `c2afa1af7d7e32a8fff951c80af0c81478fcb2490db4506765b4799d1d13aa3b`)  
- Formulas: Hit@k from rank≤k; union membership = min rank among components with rank≤50; ceiling = count(union membership).

---

## 14. FINAL REPORT BLOCK

## Repository State

Branch: `research/roman-urdu-adaptive-retrieval`  
HEAD: `3b2e829bf9769d16f9b604ee68d7cc50ce128fa7`  
Working tree: untracked `experiments/ieee_adaptive/` only  
Program A modified: **No**  
Program B modified: **No**

## TEST Integrity

TEST accessed: **No**  
TEST content inspected: **No**

## Dataset

Population: Roman KN ExactSource TRAIN+DEV **n=80**  
Split: train=52, dev=28 (cohort original=51, phase13=29)  
Gold definition: ExactSource `source_doc_id` in Top-k

## Existing Retrieval Coverage

| System | Hit@5 | Hit@50 |
| --- | ---: | ---: |
| BM25 | 5 | 13 |
| NG3 | 10 | 19 |
| Dense | **20** | 36 |
| Hybrid | 17 | **40** |
| Oracle best-of-3 Hit@5 | **28** | — |
| BND union Hit@50 | — | **49** |

## Perfect-Ranking Upper Bounds

| Pool | Ceiling |
| --- | ---: |
| BM25 | 13/80 |
| NG3 | 19/80 |
| Dense | 36/80 |
| Hybrid | 40/80 |
| BM25∪NG3 | 23/80 |
| BM25∪Dense | 44/80 |
| NG3∪Dense | 47/80 |
| BM25∪NG3∪Dense | **49/80 (61.25%)** |

## Failure Decomposition

| Category | n | % |
| --- | ---: | ---: |
| SUCCESS (any expert Hit@5) | 28 | 35.0% |
| RANKING_FAILURE | 21 | 26.3% |
| CANDIDATE_GENERATION_FAILURE | 31 | 38.8% |

## Ranking Headroom

**21/80** in BND pool but not Top-5; Hybrid Rank failures **23/80**; Dense Rank failures **16/80**.

## Candidate-Generation Headroom

**31/80** outside BND Top-50; mechanisms dominated by entity_name (18), then institutional (6); only **9** heuristically “plausibly recoverable.”

## Cross-System Complementarity

Real (Dense-only 26; NG3-only 5; BM25-only 2 at Hit@50) but **not** query-predictable (C1 closed).

## Dominant Failure Mechanisms

**Candidate generation** is the primary bottleneck; among CG misses, **non-institutional entity/name** is the largest subclass, with a long heterogeneous tail.

## 80% Target Analysis

Current Hit@5: **20/80 (Dense)**  
Target: **64/80**  
Additional successes required: **44**  
Candidate-generation ceiling: **49/80**  
Is 80% theoretically compatible with current candidate pool?: **No**  
Answer: **64 > 49 ⇒ reranking/perfect ranking of existing BND pools cannot reach 80%.**

## Interpretation

The performance bottleneck is **first-stage candidate generation**, not Top-5 ordering. Complementarity among BM25/NG3/Dense is real and yields a **61.25%** theoretical Hit@5 ceiling under perfect ranking — a large lift over Dense’s 25%, but **structurally short of 80%**. The remaining 31 misses are mechanism-heterogeneous; prior Program B phases and closed C2a already stress-tested the most concrete CG interventions available in-repo. Scientifically, expecting ~80% Hit@5 from refinements of the current expert set is **unrealistic**. Modest improvement research (toward the 40–49% band) can still be discussed separately from the 80% stretch target.

## Potential Future Interventions

`POTENTIAL FUTURE INTERVENTION` only — **not implemented**:

1. Stronger first-stage / cross-script entity bridging (addresses largest CG subclass; novelty not claimed).  
2. Better fusion/reranking over BND (addresses ≤21 ranking failures; cannot fix 31 absences).  
3. New candidate generators beyond BM25/NG3/Dense (required for any path past 49/80).  
4. Reassess thesis/publication claims around achievable Hit@5 ranges (25–50% empirical; ≤61% oracle ceiling).

## FINAL DECISION

**LOW / STRUCTURALLY LIMITED HEADROOM**

## NEXT STEP

Do not force another method aimed at ~80% Hit@5 on this benchmark with the current candidate-generation architecture.  
Reassess publication/thesis strategy around honest ceilings (Dense ~25%, Hybrid pool ~50%, perfect-BND ≤61%).  
If any later work proceeds, it must target **new candidate generation** with a pre-declared mechanism and prevalence bar — not reranking alone, and not revival of C1/C2a/C3.

---

**End of failure decomposition.**
