# ULTRA Project — Verified Complete Summary + Limitations

**Document type:** documentation only (no runs, no retunes, no edits to frozen artifacts)  
**Built:** 2026-10-01  
**Rule:** every number below was copied from a frozen artifact cited in the Traceability table at the end. Approximate or remembered values are not used. Where a requested breakdown is absent from frozen files, it is marked **NOT VERIFIED — EXCLUDE**.

**Rejected external deck (do not reuse):** a prior slide deck claimed Program B `n=80`, BM25 Hit@5≈5%, Dense Hit@5≈25%, Hybrid Hit@50≈50%, and “31 hard failures (17 Covered / 14 Partial / 0 Uncovered).” Those figures do **not** describe this repo’s frozen **Roman KN TRAIN+DEV n=51** phase summaries for Phases 2–10b. Verified n=51 Method-D Hit@5 is **4/51 = 0.0784**, Dense Hit@5 is **15/51 = 0.2941**, Hybrid Hit@50 is **25/51 = 0.4902**. The “31 / 17 / 14 / 0” package is **not** present in `phase6_diagnostics/` or in the n=51 phase JSONs used here.

---

## 1. Two programs — never averaged

State this explicitly: **Program A and Program B answer different questions on different query populations. Their headline rates must never be averaged with each other, and Program B rates must never be averaged into Program A’s three official numbers.**

### Program A — PLOS / M0 (frozen; separate paper track)

| Metric | Exact fraction | Rate as recorded | Population |
| --- | --- | --- | --- |
| Dev/validation ExactSource Hit@5 | **68/78** | **0.8718** (87.18%) | Phase 2 dev + internal_val known-item |
| Sealed known-item K ExactSource Hit@5 | **27/40** | **0.6750 = 67.50%** | K001–K040 |
| Sealed naturalistic U Success@5 (Annotator 1) | **23/40** | **0.5750 = 57.50%** | U001–U040 human Success@5 |

Sources: `experiments/phase8_final_freeze/DEVELOPMENT_RESULTS.md`; `experiments/phase12_new_unseen_evaluation/K_RESULTS.md`; `experiments/phase12_human_relevance/artifacts/metrics.json` + `experiments/phase12_independent_annotation/AGREEMENT.md` (Annotator-1 Success@5 = 23/40 = 57.50%).

**Do not average** 0.8718, 0.6750, and 0.5750 with each other or with any Program B number. They are different protocols (known-item ExactSource vs human Success@5) and different sealed sets.

### Program B — ULTRA v2 (Roman first-stage; this summary’s phase table)

**Population for every Program B Hit@k row in §2:** Roman KN TRAIN+DEV **n = 51** (human-written). Every Program B rate below is stated with that **n** explicitly.

*(Note on later freezes: `PHASE14_FINAL_REPORT.md` also records a Phase 13 expansion to n=80 and confirmatory scoring. Those n=80 cells are **out of scope** for the §2 phase-by-phase table, which uses the original n=51 frozen JSONs. They are mentioned only in §5 Current Status so this document does not falsely claim Phase 13 was never run.)*

---

## 2. Program B — every scored phase (n = 51), exact metrics and decisions

Official cutoffs Hit@1 / Hit@5 / Hit@10 / Hit@50 and MRR. Counts are integers from frozen summary JSON fields (`hit@*_n` or equivalent). Rates below are the JSON `hit@*` / `mrr` fields where present.

### Summary table (Roman KN TRAIN+DEV, n = 51)

| Method | Decision (exact label from controlled-experiment / summary) | Hit@1 | Hit@5 | Hit@10 | Hit@50 | MRR |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| R2-B0 Method-D BM25 | DEVELOPMENT BASELINE ESTABLISHED (baseline; not a support/unsupported gate) | 1 | 4 | 4 | 6 | 0.0375 |
| R2-NG3 / Phase 5 | `R2-NG3 PARTIALLY SUPPORTED` | 3 | 6 | 6 | 8 | 0.0750 |
| Phase 3 Dense e5-small | `DENSE BASELINE PARTIALLY SUPPORTED` | 5 | 15 | 16 | 22 | 0.1726 |
| Phase 4 Hybrid RRF k=60 | `HYBRID RRF PARTIALLY SUPPORTED` | 3 | 11 | 19 | 25 | 0.1422 |
| Phase 7 letter-name | `PHASE7 UNSUPPORTED` | 0 | 0 | 0 | 1 | 0.0007 |
| Phase 8 3-way RRF | `PHASE8 UNSUPPORTED` | 4 | 8 | 14 | 24 | 0.1310 |
| Phase 9 Wikipedia titles (v2 rule) | `PHASE9 PARTIALLY SUPPORTED` | 1 | 5 | 6 | 10 | 0.0478 |
| Phase 10 cascade Option B | `PHASE10 PARTIALLY SUPPORTED` | 3 | 11 | 19 | 24 | 0.1418 |
| Phase 10b tail-preserve | `PHASE10B PARTIALLY SUPPORTED` | 3 | 11 | 19 | 25 | 0.1422 |

**Rates for the strongest n=51 cells (exact fractions):**

- Method-D Hit@5: **4/51 = 0.0784** (7.84%)  
- Dense Hit@5: **15/51 = 0.2941** (29.41% as stored; exact 15÷51 ≈ 29.4118%)  
- Hybrid Hit@50: **25/51 = 0.4902** (49.02% as stored; exact 25÷51 ≈ 49.0196%)

### Per-phase notes (why that decision — from each controlled-experiment report)

**R2-B0 (Method-D BM25).** Baseline for Program B Roman KN. TRAIN+DEV metrics from `r2_b0_summary.json` (`metrics.train+dev`). Taxonomy on n=51: SUCCESS 4, RANK 2, VOCAB/MISS 45. Status recorded as baseline established (`R2_B0.md`), not a PARTIALLY/UNSUPPORTED gate.

**R2-NG3 / Phase 5.** Decision `R2-NG3 PARTIALLY SUPPORTED` (`R2NG3_CONTROLLED_EXPERIMENT.md`). Why: 2 dual-miss golds (KN035, KN050) enter Top-50 outside BM25∪Dense∪Hybrid, but 23/25 dual misses remain, ROOM Category 1 is 1/11, and NG3 lags Dense on aggregates — not `SUPPORTED`, not `UNSUPPORTED`.

**Phase 3 Dense.** Decision `DENSE BASELINE PARTIALLY SUPPORTED`. Why: large absolute gains (Hit@5 4→15, Hit@50 6→22 on n=51) and ENT recoveries, but ROOM Cat1 only 3/11, 29 remaining Top-50 misses vs baseline, and regression of every Method-D Top-5 success — not full `SUPPORTED`.

**Phase 4 Hybrid.** Decision `HYBRID RRF PARTIALLY SUPPORTED`. Why: improves Hit@10/Hit@50 over Dense and restores BM25 Top-50 recalls, but is worse than Dense on Hit@1/Hit@5/MRR; ROOM Cat1 stays 3/11; 25/51 remain outside both lists.

**Phase 7 letter-name.** Decision `PHASE7 UNSUPPORTED`. Why: prereg required at least one of the 23 four-way misses (or a clear acronym gold) in Top-50; recovered **0/23**; only Hit@50 was a degraded prior Method-D success.

**Phase 8 3-way RRF.** Decision `PHASE8 UNSUPPORTED`. Why: unweighted NG3 list dilutes 2-way Hybrid (Hit@5 11→8, Hit@50 25→24, MRR 0.1422→0.1310); does not discover new golds beyond preserving some NG3 ranks; Quad-23 recoveries **0**.

**Phase 9 Wikipedia titles.** Decision `PHASE9 PARTIALLY SUPPORTED`. Why: real but small ExactSource gains vs Method-D (Hit@5 4→5, Hit@50 6→10); recovers some entity/title cases (e.g. KN027, KN051 in Quad-23); does not clear the residual dual-miss mass.

**Phase 10 Option B.** Decision `PHASE10 PARTIALLY SUPPORTED`. Why: Hit@1/5/10 match Hybrid, two Hybrid-miss recoveries (KN027, KN035), but **three** Hybrid Top-50 successes lost → net Hit@50 **25→24** (regression).

**Phase 10b tail-preserve.** Decision `PHASE10B PARTIALLY SUPPORTED`. Why: equals Hybrid exactly on Hit@1/5/10/50 and MRR (regressions fixed, **no** new recoveries); stop rule: no further Option-B variants because Hit@50 is not net-positive vs Hybrid.

*(Related closed Phase 2 method, not in the user’s required list but frozen: R2-1 fallback romanizer — decision `R2-1 NOT SUPPORTED — CLOSE FALLBACK REPRESENTATION DIRECTION`; Hit@5 3/51, Hit@50 6/51, MRR 0.0358.)*

---

## 3. Phase 6 diagnostics (analysis only — no new retrieval)

**Population:** Roman KN TRAIN+DEV **n = 51**. TEST not accessed. No retrieval rerun.  
Source: `experiments/ultra_v2/phase6_diagnostics/PHASE6_DIAGNOSTICS_REPORT.md` + `artifacts/significance_results.json` + `artifacts/length_distribution.json`.

### 3.1 Exact McNemar p-values (two-sided exact binomial McNemar)

| Pair | Cutoff | n01 (control miss, treatment hit) | n10 (control hit, treatment miss) | Discordant | p (two-sided) | Significant at 0.05? |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| BM25 → Dense | Hit@5 | 15 | 4 | 19 | **0.019211** | YES |
| BM25 → Dense | Hit@50 | 20 | 4 | 24 | **0.001544** | YES |
| Dense → Hybrid | Hit@5 | 3 | 7 | 10 | **0.34375** | NO |
| Dense → Hybrid | Hit@50 | 4 | 1 | 5 | **0.375** | NO |
| BM25 → Hybrid | Hit@5 | 9 | 2 | 11 | **0.06543** | NO |
| BM25 → Hybrid | Hit@50 | 19 | 0 | 19 | **4e-06** | YES |
| Hybrid → NG3 | Hit@5 | 3 | 8 | 11 | **0.226562** | NO |
| Hybrid → NG3 | Hit@50 | 2 | 19 | 21 | **0.000221** | YES |
| Hybrid → BM25∪Dense∪NG3 | Hit@5 | 11 | 1 | 12 | **0.006348** | YES |
| Hybrid → BM25∪Dense∪NG3 | Hit@50 | 3 | 0 | 3 | **0.25** | NO |

Report note (copied): n=51 is small; non-significant results are **underpowered**, not proof of equality.

### 3.2 Script routing check

| Check | Exact result |
| --- | --- |
| Detector-labeled ROMAN among n=51 | **51 / 51** |
| Detector mismatches vs ROMAN KN population | **0** |
| Quad-23 dual-miss misroutes | **0 / 23** |
| Overall | **PASS** |

Failures among the 23 four-way misses are retrieval failures, not routing errors.

### 3.3 Document length distribution

Corpus: `data/clean_articles.csv`, n_docs = **111860**, SHA-256 `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231`.

**Character length percentiles (exact JSON values):** p10=532.0, p25=711.0, p50=1034.0, p75=1581.0, p90=2386.0, p95=3036.0, p99=5276.4100000000035; mean=1320.0307348471304; min=171; max=36265.

**Whitespace-token percentiles:** p10=109.0, p25=147.0, p50=216.0, p75=334.0, p90=506.0, p95=643.0, p99=1130.0; mean=277.75102807080276; min=24; max=7766.

**Documents with >512 whitespace tokens:** **10768 / 111860 = 9.6263%**.

### 3.4 Dual-miss diagnostic — what Phase 6 actually freezes vs requested labels

**Frozen dual-miss definition used in Phase 5/6:** gold absent from Method-D BM25 Top-50 **and** Dense Top-50.

| Quantity | Exact value | Source |
| --- | --- | --- |
| Dual-miss count (BM25∪Dense miss@50) | **25** | `phase5_ng3/artifacts/r2ng3_summary.json` → `dual_miss.n` / `dual_miss.ids` |
| Dual-miss IDs | KN002, KN005, KN006, KN008, KN010, KN018, KN020, KN021, KN022, KN024, KN025, KN026, KN027, KN028, KN032, KN035, KN036, KN037, KN041, KN042, KN044, KN047, KN050, KN051, KN054 | same |
| NG3 recoveries among those 25 | **2** (KN035, KN050) | `dual_miss.ng3_recovered` |
| Remaining four-way misses (Quad-23) | **23** | `dual_miss.ng3_remaining_miss` |

**Primary-category breakdown of the 25 dual-miss IDs** (labels from frozen `r2_primary` / R2-B0 failure primary taxonomy — **not** from a Phase 6 category audit file; Phase 6 does **not** store entity/acronym / paraphrase / neighbor / duplicate tags):

| Frozen primary label | Count among 25 dual-miss | Exact query IDs |
| --- | ---: | --- |
| ROOM | 13 | KN006, KN008, KN010, KN018, KN021, KN024, KN025, KN027, KN037, KN044, KN047, KN050, KN051 |
| ENT | 6 | KN002, KN022, KN026, KN032, KN035, KN054 |
| VOCAB | 5 | KN020, KN028, KN036, KN041, KN042 |
| NEIGH | 1 | KN005 |
| **Total** | **25** | |

**NOT VERIFIED — EXCLUDE:** a dual-miss breakdown literally named **entity/acronym**, **paraphrase**, **neighbor**, **duplicate** with those four strings as controlled codes does **not** appear in `phase6_diagnostics/artifacts/`. Closest frozen codes are **ENT / VOCAB / ROOM / NEIGH / RANK / SUCCESS**. There is **no** frozen `duplicate` category in `R2_B0_FAILURE_ANALYSIS.csv` primary values.

**Also NOT VERIFIED — EXCLUDE for n=51 Program B:** “31 hard failures (17 Covered / 14 Partial / 0 Uncovered).” That triple is not in the n=51 Phase 2–10b or Phase 6 frozen files cited here.

### 3.5 Candidate recall split (Phase 6 Task 2, from frozen CSVs)

| Method | Hit@50 | Of Hit@50 also Hit@5 | MISS (outside Top-50) | RANK (in Top-50, outside Top-5) |
| --- | ---: | ---: | ---: | ---: |
| BM25 | 6/51 = 11.76% | 4/6 | 45/51 = 88.24% | 2/51 = 3.92% |
| Dense | 22/51 = 43.14% | 15/22 | 29/51 = 56.86% | 7/51 = 13.73% |
| Hybrid | 25/51 = 49.02% | 11/25 | 26/51 = 50.98% | 14/51 = 27.45% |
| NG3 | 8/51 = 15.69% | 6/8 | 43/51 = 84.31% | 2/51 = 3.92% |
| Phase7 | 1/51 = 1.96% | 0/1 | 50/51 = 98.04% | 1/51 = 1.96% |

---

## 4. Limitations (explicit, evidence-backed)

1. **Sample size.** Program B’s phase-by-phase Hit@k table in this document is **n = 51**. That is small; McNemar non-significance is underpowered (Phase 6 note). These n=51 rates are not a large independent validation set. *(Phase 13 later froze an expanded n=80 confirmatory population — see §5 — but that does not enlarge the original Phase 2–10b decision experiments themselves.)*

2. **Union candidate-generation ceiling (computed fresh from frozen per-query CSVs, n = 51).**  
   - Union Method-D BM25 ∪ Dense ∪ NG3 Top-50: **28/51** (matches Phase 6 Hybrid vs union Hit@50 hit–hit 25 + treatment-only 3).  
   - Union over **all** frozen scored methods in §2 (BM25, Dense, NG3, Hybrid, Phase 7, Phase 8, Phase 9, Phase 10, Phase 10b) Top-50: **30/51 = 0.588235…** (58.82% if rounded to two decimals; exact fraction **30/51**).  
   - IDs still missing from **every** frozen method’s Top-50: **21** — KN002, KN005, KN006, KN008, KN010, KN018, KN020, KN021, KN022, KN024, KN025, KN026, KN028, KN032, KN036, KN037, KN041, KN042, KN044, KN047, KN054.  
   - Relative to an **80%** Hit@50-style bar on n=51: 0.80 × 51 = **40.8**, so **≥41/51** is required to reach ≥80%. From the all-method union **30/51**, **11** additional unique golds would be needed in some Top-50. Gap in rate terms: **0.80 − 30/51 ≈ 0.2118** (about **21.18 percentage points**).

3. **Largest unresolved failure category (among the 25 BM25∪Dense dual-misses, frozen primary labels).**  
   - Largest cell: **ROOM = 13/25**.  
   - Then **ENT = 6/25**, **VOCAB = 5/25**, **NEIGH = 1/25**.  
   - VOCAB dual-misses that remain hard even for Dense (Phase 11 record in Phase 14): KN020, KN028, KN036, KN041, KN042 — cross-lingual paraphrase / institutional phrasing, not fixed by Phases 7–10b.

4. **Approaches that did not help or made things worse (plain statement).**  
   - **Phase 7 letter-name:** Hit@5 **0/51**, Hit@50 **1/51** (worse than Method-D’s 6/51 Hit@50); **0/23** Quad-23 recoveries → **UNSUPPORTED**.  
   - **Phase 8 3-way RRF:** Hit@5 **11→8**, Hit@50 **25→24** vs Hybrid → **UNSUPPORTED**.  
   - **Phase 10 Option B:** Hit@50 **25→24** vs Hybrid (net regression) → PARTIALLY SUPPORTED only with regression acknowledged.  
   - **Phase 10b:** identical to Hybrid (**no** new recoveries); further Option-B variants **stopped**.  
   - **R2-1 fallback** (related): Hit@5 **4→3**; ROOM Cat1 **0/11→0/11** → **NOT SUPPORTED**.

5. **Program A vs Program B are not the same benchmark.**  
   Program A’s verified headlines (**68/78 = 0.8718**, **27/40 = 0.6750**, **23/40 = 0.5750**) use QTRN/K/U populations and mixed scripts / human Success@5. Program B’s verified n=51 Roman KN ExactSource rates (e.g. Dense **15/51 = 0.2941**, Hybrid Hit@50 **25/51 = 0.4902**) are a **different** protocol. **Do not** say Program B “improved on” or “fell short of” Program A’s 87.18% / 67.50% / 57.50% as if they shared one scoreboard.

---

## 5. Current status (from frozen Program B consolidation)

From `experiments/ultra_v2/PHASE14_FINAL_REPORT.md` (FROZEN Program B citation file):

| Phase | Status |
| --- | --- |
| Phases 2–10b | Scored and decided on **n=51** (table in §2) |
| Phase 6 | Diagnostics complete (analysis only) |
| Phase 11 | Investigated; Option 2 (new bilingual resource) **skipped** after Option-1 no-go |
| Phase 12 (reranking) | **SKIPPED** — gating: candidate pool not expanded enough to justify rerank |
| Phase 13 | **Run and frozen:** population expansion + confirmatory scoring (**n=80** = 51 W1 + 29 LLM1); n=51 subset gate PASS |
| Phase 14 | **FROZEN** consolidation / single source of truth for Program B citation |
| TEST | **Sealed; never accessed** in Program B |

**Correction to an outdated “next = Phase 11” roadmap reading:** on the frozen record, Phase 11–14 are already completed or skipped as above. The live integrity constraint that remains is **TEST sealed**. Any further work would be a **new** authorization beyond Phase 14, not the next numbered phase in the original Phase 2–12 ladder.

---

## 6. Traceability table (spot-checkable)

| Reported number / claim | Exact source path | Field / location |
| --- | --- | --- |
| Program A Hit@5 68/78 = 0.8718 | `experiments/phase8_final_freeze/DEVELOPMENT_RESULTS.md` | Official frozen system table; “Exact-source Hit@5 \| **0.8718** (68/78)” |
| Program A K Hit@5 27/40 = 0.6750 | `experiments/phase12_new_unseen_evaluation/K_RESULTS.md` | ExactSource metrics table primary Hit@5 |
| Program A U Success@5 Annotator 1 = 23/40 = 0.5750 | `experiments/phase12_human_relevance/artifacts/metrics.json` | `success@5.hits=23`, `n=40`, `rate=0.575` |
| Annotator-1 Success@5 wording 23/40 = 57.50% | `experiments/phase12_independent_annotation/AGREEMENT.md` | § opening: “Annotator-1 Success@5 = 23/40 = 57.50%” |
| R2-B0 n=51 Hit@1/5/10/50 = 1/4/4/6, MRR 0.0375 | `experiments/ultra_v2/phase2_roman/artifacts/r2_b0_summary.json` | `metrics.train+dev` |
| Dense n=51 Hit@1/5/10/50 = 5/15/16/22, MRR 0.1726 | `experiments/ultra_v2/phase3_dense/artifacts/dense_summary.json` | `metrics_roman_kn_traindev` |
| Dense decision `DENSE BASELINE PARTIALLY SUPPORTED` | `experiments/ultra_v2/phase3_dense/DENSE_CONTROLLED_EXPERIMENT.md` | header Decision + §15 |
| Hybrid n=51 Hit@1/5/10/50 = 3/11/19/25, MRR 0.1422 | `experiments/ultra_v2/phase4_hybrid/artifacts/hybrid_summary.json` | `hybrid_rrf` |
| Hybrid decision `HYBRID RRF PARTIALLY SUPPORTED` | `experiments/ultra_v2/phase4_hybrid/HYBRID_CONTROLLED_EXPERIMENT.md` | header Decision |
| NG3 n=51 Hit@1/5/10/50 = 3/6/6/8, MRR 0.075 | `experiments/ultra_v2/phase5_ng3/artifacts/r2ng3_summary.json` | `reproduced_ng3` |
| NG3 decision `R2-NG3 PARTIALLY SUPPORTED` | `experiments/ultra_v2/phase5_ng3/R2NG3_CONTROLLED_EXPERIMENT.md` | header Decision |
| Phase 7 Hit@1/5/10/50 = 0/0/0/1, MRR 0.0007 | `experiments/ultra_v2/phase7_entity_norm/artifacts/phase7_summary.json` | `phase7_lettername` |
| Phase 7 decision `PHASE7 UNSUPPORTED` | `experiments/ultra_v2/phase7_entity_norm/PHASE7_CONTROLLED_EXPERIMENT.md` | header + §9 |
| Phase 8 Hit@1/5/10/50 = 4/8/14/24, MRR 0.1310 | `experiments/ultra_v2/phase8_3way_fusion/artifacts/phase8_summary.json` | `phase8_3way_rrf` |
| Phase 8 decision `PHASE8 UNSUPPORTED` | `experiments/ultra_v2/phase8_3way_fusion/PHASE8_CONTROLLED_EXPERIMENT.md` | header Decision |
| Phase 9 Hit@1/5/10/50 = 1/5/6/10, MRR 0.0478 | `experiments/ultra_v2/phase9_entity_resource/artifacts/phase9_summary.json` | `phase9_wptitles` |
| Phase 9 decision `PHASE9 PARTIALLY SUPPORTED` | `experiments/ultra_v2/phase9_entity_resource/PHASE9_CONTROLLED_EXPERIMENT.md` | header Decision |
| Phase 10 Hit@1/5/10/50 = 3/11/19/24, MRR 0.1418 | `experiments/ultra_v2/phase10_cascade/artifacts/phase10_summary.json` | `phase10_cascade_b` |
| Phase 10 decision `PHASE10 PARTIALLY SUPPORTED` | `experiments/ultra_v2/phase10_cascade/PHASE10_CONTROLLED_EXPERIMENT.md` | header + §8 |
| Phase 10b Hit@1/5/10/50 = 3/11/19/25, MRR 0.1422 | `experiments/ultra_v2/phase10_cascade/artifacts/phase10b_summary.json` | `phase10b_tail_preserve` |
| Phase 10b decision `PHASE10B PARTIALLY SUPPORTED` | `experiments/ultra_v2/phase10_cascade/PHASE10B_CONTROLLED_EXPERIMENT.md` | header Decision |
| McNemar p-values (all pairs in §3.1) | `experiments/ultra_v2/phase6_diagnostics/artifacts/significance_results.json` | `pairs[*].hit@5|hit@50.p_two_sided` |
| Routing 51/51 ROMAN, 0 mismatches | `experiments/ultra_v2/phase6_diagnostics/PHASE6_DIAGNOSTICS_REPORT.md` | Task 3 table |
| Length percentiles + 10768/111860 = 9.6263% | `experiments/ultra_v2/phase6_diagnostics/artifacts/length_distribution.json` | `char_len`, `whitespace_tokens`, `exceed_512_whitespace_tokens` |
| Dual-miss n=25 + IDs + NG3 recovered 2 | `experiments/ultra_v2/phase5_ng3/artifacts/r2ng3_summary.json` | `dual_miss` |
| Dual-miss primary ENT/ROOM/VOCAB/NEIGH counts | `experiments/ultra_v2/phase3_dense/DENSE_PER_QUERY.csv` (`r2_primary`) cross-checked with `phase2_roman/R2_B0_FAILURE_ANALYSIS.csv` (`primary`) | per query_id among dual_miss.ids |
| Union BM25∪Dense∪NG3 Top-50 = 28/51 | Recomputed from frozen CSVs; consistent with Phase 6 Hybrid vs union Hit@50 (25 hit–hit + 3 treatment-only) | `DENSE_PER_QUERY.csv`, `R2NG3_PER_QUERY.csv`, `artifacts/r2_b0_per_query.csv`; Phase 6 report Task 1 union Hit@50 |
| Union all frozen methods Top-50 = 30/51; 21 all-miss IDs | Recomputed 2026-10-01 from listed `*_PER_QUERY.csv` Hit@50 columns | Shell verification over phase2–10b per-query CSVs |
| Phase 11/12/13/14 status | `experiments/ultra_v2/PHASE14_FINAL_REPORT.md` | §1.1 Non-Hit@k phases; header Status FROZEN |
| “31 / 17 / 14 / 0” for n=51 Program B | **NOT VERIFIED — EXCLUDE** | Not found in Phase 6 or n=51 phase JSONs used in this document |
| Dual-miss labels literally named entity/acronym, paraphrase, duplicate | **NOT VERIFIED — EXCLUDE** | Not present under those strings in `phase6_diagnostics/artifacts/` |

---

## 7. Spot-check tips for supervisor review

1. Open `phase3_dense/artifacts/dense_summary.json` → `metrics_roman_kn_traindev.hit@5_n` should be **15** (not 20).  
2. Open `phase4_hybrid/artifacts/hybrid_summary.json` → `hybrid_rrf.hit@50_n` should be **25** (not 40).  
3. Open `phase2_roman/artifacts/r2_b0_summary.json` → `metrics.train+dev.hit@5_n` should be **4** (not 5).  
4. Open `phase6_diagnostics/artifacts/significance_results.json` → BM25 vs Dense Hit@5 `p_two_sided` should be **0.019211**.  
5. Confirm this file never averages Program A 0.8718 / 0.6750 / 0.5750 with Program B n=51 rates.
