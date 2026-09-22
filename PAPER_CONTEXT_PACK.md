# PAPER_CONTEXT_PACK — ULTRA PLOS / v2 drafting inventory

**Generated (UTC):** 2026-09-20T14:57:48Z
**Purpose:** Read-only consolidation for writing/updating a PLOS ONE paper. Does **not** edit original drafts or frozen phase files.
**Current git HEAD (at inventory):** `research/ultra-v2-strengthening` @ `fd54ac9b65c2db93e7e16fbf0c5a40b6a6025be1` (same tip as `publication/plos-one-final` at inventory time; working tree may contain uncommitted Program B files).

---

# BRANCH 1: `publication/plos-one-final` (Program A / M0)

## 1. PLOS ONE manuscript — paths and SHA-256

| Role | Path | SHA-256 | bytes |
|---|---|---|---:|
| Working-tree TeX | `Papers/PLOS_ONE/Adaptive_dynamic_query_routing_for_Urdu_information_retrieval.tex` | `21611d5bfa1c355103c329003edee5f8cbe9e4343b5fd1ef0e0297d9e9ecfd6e` | 61629 |
| Submission-package TeX | `Papers/PLOS_ONE/SUBMISSION_PACKAGE_FINAL/manuscript/Adaptive_dynamic_query_routing_for_Urdu_information_retrieval.tex` | `21611d5bfa1c355103c329003edee5f8cbe9e4343b5fd1ef0e0297d9e9ecfd6e` | 61629 |
| Submission PDF (EM initial) | `Papers/PLOS_ONE/SUBMISSION_PACKAGE_FINAL/manuscript/Adaptive_dynamic_query_routing_for_Urdu_information_retrieval.pdf` | `4a1fe11481c0409e66db1537957910306df1e307ca19599c6cf311f2c7aa0824` | 113777 |
| Package manifest | `Papers/PLOS_ONE/SUBMISSION_PACKAGE_FINAL/MANIFEST.txt` | `d71e3b3d0615d0ccbc402edcb39df0214f17144db18c23ba7719bf024326c414` | 6193 |
| EM checklist | `Papers/PLOS_ONE/SUBMISSION_PACKAGE_FINAL/EDITORIAL_MANAGER_CHECKLIST.md` | `e37cb580bdf676f3ec2609836a46b2be5466993a9d766e4f7d1c0b5908cc14f5` | 5568 |

**Printed title (header comment + EM checklist):** Script-aware BM25 retrieval for Urdu and Roman Urdu news search

**Note:** Filename retains historical `Adaptive_dynamic_query_routing_...` stem; content is M0 script-aware BM25 (not SVM/MiniLM).

### 1.1 Authors (from TeX body + EM checklist)

| Author | Role in draft | CRediT (EM checklist / TeX header comments) |
|---|---|---|
| Hashim Shazad | Corresponding author (`1*`) | Conceptualization, Methodology, Software, Formal analysis, Writing – original draft, Writing – review & editing |
| Adnan Aslam | Co-author | Supervision, Writing – review & editing |
| Areena Rahman | Co-author | Validation (independent A2 relevance annotation as reliability only; does **not** replace official A1 Success@5 23/40) |
| Affiliation (all) | Department of Creative Technologies, Air University, Islamabad, Pakistan | |

Acknowledgments (TeX): "We thank Adnan Aslam for supervision. This work was completed as part of an M.S. thesis at Air University, Islamabad."

### 1.2 Section outline (PLOS TeX)

Abstract; Introduction (+ Research questions); Materials and methods (Research design, Evaluation hierarchy, Corpus, Official frozen system M0, Method D, Roman-method selection Phase 5, Development/validation known-item pool, Query-side expansions Phase 11, Sealed evaluation Phase 12, Human relevance protocol U, Ethics, Metrics, Rejected alternatives, Diagnostic H001–H040, Software environment, Data availability); Results (Development/validation, Phase 11 ablation, New known-item K, Naturalistic U, Diagnostic H); Discussion (+ Limitations); Conclusion; Supporting information; Acknowledgments.

**Full verbatim TeX** is reproduced in Appendix A of this pack (working-tree copy).

## 2. IEEE companion — path, SHA, differences vs PLOS

| Path | SHA-256 | bytes |
|---|---|---:|
| `Papers/IEEE/FINAL/main.tex` | `b91daaafb7d07dfa8b72899499046c8fde7f5c8c2391c1c1c156429f674c3d18` | 11192 |

**IEEE title:** Script-Aware BM25 for Urdu News Search: Known-Item Recovery, Sealed Generalization, and Human Usefulness

**Authors:** Hashim Shazad, Adnan Aslam only (Areena Rahman **not** on IEEE author list).

**How IEEE differs from PLOS (factual):**
- Shorter conference-style framing (~11 KB vs ~61 KB PLOS TeX).
- Explicit **Related Work** and **Error Analysis** sections (PLOS folds literature into Introduction / Discussion).
- Same three official M0 metrics (87.18% / 67.50% / 57.50%); same "do not average / do not claim 80%" stance.
- Mentions companion IEEE draft with **negative** dense P@5 for SHORT/LONG SVM routing (historical Layer A), clarifying this paper is BM25/M0 only.
- Full verbatim IEEE TeX in Appendix B.

## 3. Submission status (in-repo only)

| Finding | Evidence |
|---|---|
| Submission **package prepared** 6 September 2026 | `SUBMISSION_PACKAGE_FINAL/MANIFEST.txt`, `EDITORIAL_MANAGER_CHECKLIST.md` |
| Branch named | `publication/plos-one-final` @ commit `fd54ac9b…` |
| DOI in repo | **None found** |
| Acceptance letter / reviewer correspondence | **None found** |
| Claim of "published" | **Forbidden** by `docs/MASTER_PROMPT_FOR_CLAUDE.md` rule 6: "Repo shows a PLOS/IEEE **submission snapshot**… No DOI / acceptance letter in-repo." |
| Editorial status outside repo | Explicitly listed as **unknown / waiting** in Master Prompt §"What we are waiting for" item 2 |

## 4. Official frozen M0 metrics (three numbers — do not average)

| Metric | Value | Primary source file | Supporting SHA / freeze |
|---|---|---|---|
| Dev/val ExactSource Hit@5 | **68/78 = 87.18%** | `experiments/phase8_final_freeze/DEVELOPMENT_RESULTS.md`; also `results/FINAL_RESULTS.md` | S1 freeze manifest `development_eval.exact_source_hit@5: 0.8718`; corpus SHA `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231` (`Papers/PLOS_ONE/SUBMISSION_PACKAGE_FINAL/supporting_information/S1_file.json`; `experiments/phase8_final_freeze/FINAL_SYSTEM_MANIFEST.json` SHA prefix `e3cde5df…`) |
| Sealed K ExactSource Hit@5 | **27/40 = 67.50%** | `experiments/phase12_new_unseen_evaluation/K_RESULTS.md` | Queries K SHA `124e452693f98baedf510618240c154df68d56b6b7a37ed085a6512c13d13ff6` (`SEAL.json` / `artifacts/run_manifest.json`); corpus/dict same as freeze |
| Sealed U Success@5 (A1) | **23/40 = 57.50%** | `experiments/phase12_human_relevance/PHASE12_HUMAN_RESULTS.md`; SI `S2_table.csv` | U queries SHA `684fd1e19eddb717f5897d869ef0ca0ed586316c5a7e1d2d23006e0748fc53b9`; A2 reliability 26/40 does **not** replace 23/40 |

**Match to draft:** PLOS Abstract/Results and IEEE Abstract state the same three figures. `results/FINAL_RESULTS.md` restates them as the official non-averaged headlines.

---

# BRANCH 2: `research/ultra-v2-strengthening` (Program B)

## 6. Phase preregistrations + reports (ordered) with SHA-256

| Phase | Preregistration path | SHA-256 | Report path | SHA-256 |
|---|---|---|---|---|
| 2 R2-1 | `experiments/ultra_v2/phase2_roman/R2_1_CONTROLLED_FALLBACK_ROMANIZATION.md` | `82affdefc8588a86e257ea2e902d636392af597b5aa4a529dbd47060e84801a4` | `experiments/ultra_v2/phase2_roman/R2_1_CONTROLLED_FALLBACK_ROMANIZATION.md` | `82affdefc8588a86e257ea2e902d636392af597b5aa4a529dbd47060e84801a4` |
| 2 NG3 prereg | `experiments/ultra_v2/phase2_roman/R2_NG3_PREREGISTRATION.md` | `019a0f63bec03a7b5091a013854c94dce7f2c9688fbc0ac5344d0a93cac1f888` | `experiments/ultra_v2/phase2_roman/R2_NG3_CONTROLLED_EXPERIMENT.md` | `8bb04dc2cfe1c478ddf143df96f758a55cba693c4d6df89ba17c5fcde5361b6d` |
| 3 Dense | `experiments/ultra_v2/phase3_dense/DENSE_PREREGISTRATION.md` | `83fcd3c1aca2e9489621b41484d89d074df5e5b8bcd0c01112044677fc48cf9d` | `experiments/ultra_v2/phase3_dense/DENSE_CONTROLLED_EXPERIMENT.md` | `4a03e9e397b2dc43f5b216d3b841e88b5883686f3c6d722bf0266a3fcab4d12f` |
| 4 Hybrid | `experiments/ultra_v2/phase4_hybrid/HYBRID_PREREGISTRATION.md` | `0e345b86af37440f3fe5c51ca0814f22aea72eb564a3e529619c4e6cd757c551` | `experiments/ultra_v2/phase4_hybrid/HYBRID_CONTROLLED_EXPERIMENT.md` | `fd3444f8db37314f1c2c859014b412c8705590642e7198ce49a29b06c9daef97` |
| 5 NG3 | `experiments/ultra_v2/phase5_ng3/R2NG3_PREREGISTRATION.md` | `b67d152f54117c755c5190f33a6f92b6d526581f76220dde77c83b7908b19157` | `experiments/ultra_v2/phase5_ng3/R2NG3_CONTROLLED_EXPERIMENT.md` | `c93e41a1af35698f6856522d5a6fb731788cd5e1f6c5a9df3dbb91ecd75434bc` |
| 6 Diagnostics | `(no separate *PREREGISTRATION*; diagnostics)` | `—` | `experiments/ultra_v2/phase6_diagnostics/PHASE6_DIAGNOSTICS_REPORT.md` | `d7dca835bea91cfc92422d706efa6c7db395a51898dfbdfec3eee0b45e15946f` |
| 7 Letter-name | `experiments/ultra_v2/phase7_entity_norm/PHASE7_PREREGISTRATION.md` | `d5937c525b8933a7abfa1adcc4086db605ad58aa5e75be3b3b4b1cbd6168fc43` | `experiments/ultra_v2/phase7_entity_norm/PHASE7_CONTROLLED_EXPERIMENT.md` | `b5e6ef0d22c8d015fec65d0276eeb33ed7c36e5a5ffe794d7587c9ff3fb5b277` |
| 8 3-way RRF | `experiments/ultra_v2/phase8_3way_fusion/PHASE8_PREREGISTRATION.md` | `fcd93d2fccadd561a994bd3feac12fbcadb301c5665626edb70fcee0cf515532` | `experiments/ultra_v2/phase8_3way_fusion/PHASE8_CONTROLLED_EXPERIMENT.md` | `9d59c0c0be001618c1153b685d9e18b64c1366ce8808079383029bf7362a5b49` |
| 9 Titles | `experiments/ultra_v2/phase9_entity_resource/PHASE9_PREREGISTRATION.md` | `3a3956cbc0749f2f8189a19698a05bc1e3a854d7a164a70a66ff972e947f0372` | `experiments/ultra_v2/phase9_entity_resource/PHASE9_CONTROLLED_EXPERIMENT.md` | `df9c4934672a2a5bf1ceaecdcce5c233176817070089f7ac8a93db58a44407dd` |
| 10 Cascade | `experiments/ultra_v2/phase10_cascade/PHASE10_PREREGISTRATION.md` | `c85eeb3509423d98fb40eb5ff8e9d44d5e6ee76e2239dc162a9c4ef710369eee` | `experiments/ultra_v2/phase10_cascade/PHASE10_CONTROLLED_EXPERIMENT.md` | `1a6eda2e5d6c0a48cb1d0a66da8c44219bcae73e9d2546131fcbf16643463439` |
| 10b Tail | `experiments/ultra_v2/phase10_cascade/PHASE10B_PREREGISTRATION.md` | `60f691c38e4b3d8a6f26f9c435cf4c0fa55ddafaa73dd7da1093bddfaa49e60e` | `experiments/ultra_v2/phase10_cascade/PHASE10B_CONTROLLED_EXPERIMENT.md` | `65d413d09c8a59c8d55e43d34058b5ae5d0349f79892e180d064ed1e04ffc815` |
| 11 Investigate | `(inspection + Option-1 probe; no Hit@k prereg)` | `—` | `(see PHASE14 §1.1; Phase 11 skipped for injection)` | `—` |
| 12 Rerank | `**SKIPPED** (gating; PHASE14 §1.1)` | `—` | `**SKIPPED**` | `—` |
| 13 Population+score | `experiments/ultra_v2/phase13_population/PHASE13_SCORING_PREREGISTRATION.md` | `55788660c5d1f6d9d55399d82ed722733ab64097704fb23084fd77b1b39b912a` | `experiments/ultra_v2/phase13_population/artifacts/scoring/PHASE13_SCORING_REPORT.md` | `92b4f50ccabca27b118981d0255ba7e67aecfb54b0d0eb168fc67caa892e8218` |
| 14 Final | `n/a (consolidation)` | `—` | `experiments/ultra_v2/PHASE14_FINAL_REPORT.md` | `0cf7c9a928e9d9e734293d18c1d8fbab8c167775340a880d76c0dcaeea862f7b` |

**Phase 14 consolidated source:** **EXISTS** — `experiments/ultra_v2/PHASE14_FINAL_REPORT.md`
- SHA-256: `0cf7c9a928e9d9e734293d18c1d8fbab8c167775340a880d76c0dcaeea862f7b` (also `PHASE14_FINAL_REPORT.sha256`)
- Cite PHASE14 for all Program B Hit@k claims (not scattered per-phase docs).

## 7. Full text of PHASE14_FINAL_REPORT.md

```markdown
# ULTRA v2 Program B — Phase 14 Final Report

**Status:** FROZEN — single source of truth for Program B citation  
**Branch:** `research/ultra-v2-strengthening`  
**Date (UTC):** 2026-09-20  
**Population:** Roman KN TRAIN+DEV ExactSource — original **n=51** (human-written, `writer_id=W1`) + Phase 13 **n=29** (LLM-drafted / human naturalness-reviewed, `writer_id=LLM1`) → frozen **n=80**  
**TEST:** sealed; **never accessed** in any Program B phase (including this report)  
**Program A / M0 / PLOS:** separate, untouched  

**This document supersedes per-phase write-ups for Program B claims.** Cite this file (and its SHA-256), not scattered Phase 2–13 markdown, when writing the v2 paper/thesis chapter.

---

## 0. Executive headline (plain)

**Best Hit@5 (n=80):** Dense e5-small — **20/80 = 0.2500** (MRR 0.1718).  
**Best Hit@50 (n=80):** Hybrid RRF and Phase 10b (tied) — **40/80 = 0.5000**.  
(Phase 10 Option B is **39/80** Hit@50 — strictly worse than Hybrid/10b.)

Against the supervisor’s **~80% stretch target** (interpreted as ExactSource Hit@5 on the Roman KN development population): the best Hit@5 is **25%**, i.e. **55 percentage points short of 80%**. Hit@50 peaks at **50%**, still **30 points short** of an 80% bar if that bar were applied at depth 50. **Program B did not reach the stretch target.** That shortfall is a result, not a soft failure to be reworded as near-miss.

Method-D BM25 on this Roman KN set remains near floor (n=51 Hit@5 **4/51 = 7.84%**; n=80 **5/80 = 6.25%**). Dense is the strongest single first-stage; Hybrid is the strongest candidate-generation pool among deployable fusions tried.

---

## 1. Consolidated ExactSource table (n=51 vs n=80)

All Hit@k counts and MRR values below are copied from frozen JSON summaries / Phase 13 scoring (n=51 subset gate **PASS**).  
**n/a** = method was never re-scored on the expanded n=80 population (Phases 2–8 artifacts remain n=51-only).

| Method | Decision (frozen) | n=51 Hit@1 | n=51 Hit@5 | n=51 Hit@10 | n=51 Hit@50 | n=51 MRR | n=80 Hit@1 | n=80 Hit@5 | n=80 Hit@10 | n=80 Hit@50 | n=80 MRR | Primary frozen source |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| R2-B0 Method-D BM25 | Baseline established | 1 | 4 | 4 | 6 | 0.0375 | 1 | 5 | 5 | 13 | 0.0336 | `phase2_roman/artifacts/r2_b0_summary.json`; n=80: `phase13_population/artifacts/scoring/phase13_scoring_summary.json` |
| R2-1 fallback romanizer | **NOT SUPPORTED** — close fallback direction | 1 | 3 | 4 | 6 | 0.0358 | n/a | n/a | n/a | n/a | n/a | `phase2_roman/artifacts/r2_1_summary.json` (treatment train+dev) |
| R2-NG3 / Phase 5 NG3 | PARTIALLY SUPPORTED | 3 | 6 | 6 | 8 | 0.0750 | 4 | 10 | 13 | 19 | 0.0766 | `phase5_ng3/artifacts/r2ng3_summary.json`; n=80 Phase 13 scoring |
| Dense e5-small | PARTIALLY SUPPORTED (strongest single) | 5 | 15 | 16 | 22 | 0.1726 | 9 | 20 | 23 | 36 | 0.1718 | `phase3_dense/artifacts/dense_summary.json` (`metrics_roman_kn_traindev`); n=80 Phase 13 |
| Hybrid RRF (BM25+Dense, k=60) | Supported as 2-way fusion baseline | 3 | 11 | 19 | 25 | 0.1422 | 5 | 17 | 25 | 40 | 0.1376 | `phase4_hybrid/artifacts/hybrid_summary.json`; n=80 Phase 13 |
| Phase 7 letter-name | **UNSUPPORTED** | 0 | 0 | 0 | 1 | 0.0007 | n/a | n/a | n/a | n/a | n/a | `phase7_entity_norm/artifacts/phase7_summary.json` |
| Phase 8 3-way RRF | **UNSUPPORTED** | 4 | 8 | 14 | 24 | 0.1310 | n/a | n/a | n/a | n/a | n/a | `phase8_3way_fusion/artifacts/phase8_summary.json` |
| Phase 9 Wikipedia titles | PARTIALLY SUPPORTED | 1 | 5 | 6 | 10 | 0.0478 | 1 | 9 | 10 | 19 | 0.0520 | `phase9_entity_resource/artifacts/phase9_summary.json`; n=80 Phase 13 |
| Phase 10 Option B cascade | PARTIALLY SUPPORTED (net Hit@50 **worse** than Hybrid) | 3 | 11 | 19 | 24 | 0.1418 | 5 | 17 | 25 | 39 | 0.1373 | `phase10_cascade/artifacts/phase10_summary.json`; n=80 Phase 13 |
| Phase 10b tail-preserve | PARTIALLY SUPPORTED (= Hybrid; no further Option B) | 3 | 11 | 19 | 25 | 0.1422 | 5 | 17 | 25 | 40 | 0.1376 | `phase10_cascade/artifacts/phase10b_summary.json`; n=80 Phase 13 |

**R2-1 control** (same as R2-B0): Hit@5 4/51, Hit@50 6/51, MRR 0.0375 — treatment did not improve Hit@50; Hit@5 fell 4→3.

### 1.1 Non-Hit@k phases (required record)

| Phase | Status | Record (not a Hit@k row) | Evidence |
|---|---|---|---|
| **Phase 11** | Investigated → **Option 2 skipped** | Five remaining VOCAB/paraphrase dual-misses where Dense also fails badly: **KN020, KN028, KN036, KN041, KN042** (Dense gold ranks **110, 523, 1674, 11599, 469**). Method-D / NG3 / Phase-9-alone: gold **not in Top-50** for all five. Acronym/PN probe through frozen Phase-9 v2 matcher: **CPEC/SBP → 0 title hits**; only KN028 `external debt` hit returned Wikipedia Urdu `بیرونی قرضہ…` (not in gold; gold uses `غیر ملکی قرضوں…`). Frozen title→candidate-list injection showed **no measurable movement**. Conclusion: **no viable candidate-generation path** from existing frozen resources for these misses; building a new bilingual glossary was **not** authorized after the Option-1 no-go. | Phase 11 Step 1–2 inspection + Option-1 probe (session record); Dense ranks from `phase3_dense/DENSE_PER_QUERY.csv` |
| **Phase 12 (reranking)** | **SKIPPED — gating criterion not met** | Reranking presupposes a pool that already contains gold more often. Phase 9’s gain was small and remained proportionally similar at n=51 and n=80; Phase 10/10b added **no net-positive** candidate-generation story (10 regresses Hit@50; 10b ≡ Hybrid). Same gating logic as Phase 11’s skip: **do not spend a phase on reordering a pool that was not genuinely expanded.** | This report §0–§1; `PHASE10B_CONTROLLED_EXPERIMENT.md`; Phase 13 n=80 Hybrid/P9/P10 table above |
| **Phase 13** | Population growth + confirmatory scoring | Frozen n=80; scoring prereg SHA `55788660…`; n=51 subset consistency **PASS**; no retuning | `PHASE13_FREEZE_MANIFEST.json`; `artifacts/scoring/phase13_scoring_summary.json` |

### 1.2 n=29 Phase-13-only slice (descriptive; from Phase 13 scoring)

| Method | Hit@5 | Hit@50 | MRR |
|---|---:|---:|---:|
| BM25 | 1/29 | 7/29 | 0.0268 |
| Dense | 5/29 | 14/29 | 0.1704 |
| NG3 | 4/29 | 11/29 | 0.0794 |
| Hybrid | 6/29 | 15/29 | 0.1295 |
| Phase 9 | 4/29 | 9/29 | 0.0593 |
| Phase 10 | 6/29 | 15/29 | 0.1295 |
| Phase 10b | 6/29 | 15/29 | 0.1295 |

Not a tuning target. Roughly similar Hit@5 rates to the original 51 for Hybrid (~0.21); Hit@50 rate slightly higher (~0.52 vs ~0.49).

---

## 2. What worked / what didn’t / why

### 2.1 What worked

1. **Dense e5-small** — Largest single-method Hit@5 and MRR on Roman KN (n=51: 15/51 Hit@5, 22/51 Hit@50; n=80: 20/80, 36/80). Recovers paraphrase/entity cases Method D cannot bridge; does not solve all VOCAB dual-misses (see Phase 11).
2. **Hybrid RRF (k=60)** — Best deployable **Hit@50** pool (n=51: 25/51; n=80: 40/80). Restores lexical BM25 recalls that Dense alone drops; still leaves a large dual-miss tail.
3. **Phase 9 Wikipedia title expansion** — Narrow, real ExactSource gains (n=51: Hit@5 4→5, Hit@50 6→10 vs BM25; recovers some entity/title cases). Gain is **small** and **does not** cover FBR/CPEC/ADB/JLO-class acronyms absent as exact Wikipedia title keys. At n=80, Hit@50 19/80 — still far below Hybrid.

### 2.2 What didn’t (mechanism)

| Failure | Mechanism |
|---|---|
| **R2-1 fallback romanizer** | Document-side Latin rewrite did not create a BM25 bridge for ROOM Category 1 (0/11→0/11 Hit@50). Hit@50 unchanged; Hit@5 worsened (KN012 5→9). Closed. |
| **Phase 7 letter-name** | Acronym→Urdu letter-name expansion fired often but produced **0/23** Quad-23 Top-50 recoveries; only Hit@50 was a degraded prior BM25 success. Method-D index still lacks matching letter-named document tokens for the hypothesized orgs. |
| **Phase 8 3-way RRF** | Unweighted third list (NG3) **dilutes** Hybrid ranks: Hit@5 11→8, Hit@50 25→24. Union membership ≠ ranked Top-k. |
| **Phase 10 Option B** | Hybrid-first cascade with cascade fill **evicted** Hybrid tail golds (Hit@50 25→24 at n=51; 40→39 at n=80). Recoveries did not offset losses. |
| **Phase 10b** | Tail-preserve removes regressions → **≡ Hybrid**. No net new recoveries. **Stop further Option-B variants** (frozen stopping rule). |
| **Phase 11 VOCAB dual-misses** | True/mixed cross-lingual paraphrase (e.g. CPEC↔اقتصادی راہداری). Dense ranks hundreds–thousands; frozen Wikipedia title matcher returns empty or wrong-synonym expansions. Not a spelling-normalization problem; not fixable by candidate-list injection from existing resources. |

### 2.3 Standing unresolved gap

1. **Acronym / institutional surface forms** (FBR, CPEC, ADB, JLO-class): absent or non-unique as exact English Wikipedia title keys under the frozen Phase-9 rule; letter-name (Phase 7) failed empirically.  
2. **Cross-lingual paraphrase / vocabulary gap** (Phase 11 five): English/Roman macro and institutional phrasing vs Urdu-script golds with different lexemes — unsolved by BM25, NG3, Dense (deep miss), Hybrid, Phase 9, or cascades.  

These remain open scientific problems for any future work; Program B freezes without claiming them solved.

---

## 3. Research-integrity compliance

| Requirement | Evidence |
|---|---|
| TEST never accessed | Every controlled-experiment / summary JSON in Phases 2–13 records `"test_accessed": false`. Runners hard-refuse `benchmark/test/`. Phase 13 validation and scoring used TRAIN+DEV only. This Phase 14 write-up does not open TEST. |
| Preregistration before scoring | Each scored phase has a `*_PREREGISTRATION.md` (or equivalent) written before run; Phase 13 scoring prereg SHA `55788660c5d1f6d9d55399d82ed722733ab64097704fb23084fd77b1b39b912a` locked before `run_phase13_scoring.py`. |
| No retune after negative result | **Phase 10:** no further Option-B variants after 10b ≡ Hybrid / no net gain. **Phase 11:** Option 2 (new bilingual resource) skipped after Option-1 no-go. **Phase 12:** skipped — pool not expanded. **R2-1 / Phase 7 / Phase 8:** closed as UNSUPPORTED per prereg stop rules. |
| Authorship disclosure (Phase 13) | Original 51: human-written `W1`. New 29 (`KN091`–`KN119`): **LLM-drafted, human-reviewed** `LLM1`. Must not be blurred in papers. Manifest: `phase13_population/artifacts/PHASE13_FREEZE_MANIFEST.json`. |
| Consistency | Phase 13 scoring n=51 subset metrics **exact-match** frozen Phase 2–10b cells (gate PASS). Consolidation cross-check (this report build): no numeric conflicts between cited frozen JSONs. |

**Program A** (n=78 ExactSource 68/78 = 87.18%, Phase 12 K/U, PLOS) is a **separate** program. Program B numbers must not be averaged into or substituted for Program A headlines.

---

## 4. Artifact index (traceability)

| Artifact | Role |
|---|---|
| `phase2_roman/artifacts/r2_b0_summary.json` | Method-D n=51 |
| `phase2_roman/artifacts/r2_1_summary.json` | R2-1 treatment/control |
| `phase3_dense/artifacts/dense_summary.json` | Dense n=51 |
| `phase4_hybrid/artifacts/hybrid_summary.json` | Hybrid n=51 |
| `phase5_ng3/artifacts/r2ng3_summary.json` | NG3 n=51 |
| `phase7_entity_norm/artifacts/phase7_summary.json` | Phase 7 |
| `phase8_3way_fusion/artifacts/phase8_summary.json` | Phase 8 |
| `phase9_entity_resource/artifacts/phase9_summary.json` | Phase 9 |
| `phase10_cascade/artifacts/phase10_summary.json` | Phase 10 |
| `phase10_cascade/artifacts/phase10b_summary.json` | Phase 10b |
| `phase13_population/artifacts/PHASE13_FREEZE_MANIFEST.json` | n=80 population freeze + CSV SHAs |
| `phase13_population/artifacts/scoring/phase13_scoring_summary.json` | n=80 / n=51 / n=29 scoring |
| `phase13_population/artifacts/scoring/PHASE13_SCORING_PER_QUERY.csv` | Per-query ranks (SHA in `phase13_scoring_sha256.json`) |

Corpus SHA (throughout): `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231`  
Dictionary SHA: `30c3f61a64ec641abbb3acdbc7a8bcaf197f0238f1bf9e76c2c7ce8e590f86a3`

---

## 5. Freeze statement

Program B Phases 2–14 are **frozen**. No further method variants, retuning, TEST access, or silent omission of skipped phases. Future text about ULTRA v2 Program B must cite **this file** and its SHA-256.

**End of Phase 14.**

```

## 8. Supervisor / advisor mandate record (14 Sep 2026)

**No separate "advisor decision accepted" file** was found (no dated meeting minutes recording Adnan Aslam's choice among the three PPTX options).

**In-repo record of the 14 Sep context** is `docs/MASTER_PROMPT_FOR_CLAUDE.md` §"What we are doing now (as of 14 Sep 2026)" and §"What we are waiting for". Exact quotes (Unicode apostrophe in “Hashim’s” preserved from source):

> **Recommended ask to the advisor (Hashim’s position, not yet approved)**
> - Finish **MS thesis + PLOS on frozen M0** (three numbers, not averaged).
> - Keep **v2 as a follow-on paper**. Do **not** delay graduation for v2 TEST.
> - Do not open TEST until **one** system is preregistered and frozen on TRAIN/DEV.
> - Frame any next paper as **Roman Urdu first-stage retrieval**, not as beating 87%.

> Be explicit when you mention these. Do not invent that they already happened.
>
> 1. **Advisor decision** (Adnan Aslam) on the three options in the PPTX:
>    - (1) Thesis + PLOS only; park v2
>    - **(2) Recommended:** freeze the degree on M0; continue v2 as follow-on; TEST stays sealed
>    - (3) Delay thesis until v2 TEST — **not recommended** (NL unlabeled, Roman KN still 15/51 Hit@5 on TRAIN/DEV)
> 2. **PLOS ONE editorial status** outside the repo (submitted / under review / revision / accepted). In-repo: submission package dated 6 Sep 2026 only.

Supporting deck path: `docs/ULTRA_Advisor_Presentation.pptx` (rebuild: `docs/build_advisor_presentation.py`). History: `docs/COMPLETE_PROJECT_HISTORY.md`.

## 9. Related-work / citation material for v2

| Location | What it contains |
|---|---|
| `Papers/IEEE/FINAL/main.tex` §Related Work | CURE, Urdu MS MARCO, Roman Urdu classification (QLoRA/Xtreme), BM25, cross-lingual dense caveats |
| `Papers/PLOS_ONE/plos_bibtex_sample.bib` | Audited bibliography used by PLOS M0 paper |
| Phase 3–10 preregs | Cite RRF (k=60), e5-small, Wikipedia title resources, letter-name orthography — **experiment design**, not a curated related-work survey |
| Dedicated v2 related-work notes file | **Not found** as a standalone literature survey |

---

# CROSS-CUTTING

## 10. One PLOS paper vs two papers?

**In-repo explicit recommendation (not recorded as advisor-approved):** treat M0 PLOS as Program A submission; keep **v2 as a follow-on paper** (`docs/MASTER_PROMPT_FOR_CLAUDE.md`).

**Also undecided / waiting:** Master Prompt lists advisor decision among three options as still pending.

**No DOI / acceptance** tying M0 into a "must revise with v2" mandate was found.

**Inventory conclusion:** Decision is **recommended as TWO papers (M0 submitted snapshot + v2 follow-on)** in Hashim's written position, but **advisor ratification is not documented in-repo** → treat as **not finally decided** for editorial strategy.

## 11. Stale / contradicted claims in existing PLOS draft relative to frozen v2

| PLOS draft framing | Status after Program B freeze |
|---|---|
| M0 is the official frozen system for this paper | Still correct **for Program A / this draft** |
| "Later exploratory development on a separate git branch is outside this paper (Limitations)" | Still accurate; v2 is that branch — but **if** revising into one paper, Limitations must cite PHASE14 honestly (Roman KN Hit@5 max 25% at n=80) |
| Ordinary Roman Urdu is the main failure (K 1/12, U 6/18) | **Reinforced** by v2: Method-D 4/51 then 5/80 Hit@5 on new Roman KN |
| Dense/hybrid not claimed as official M0 | Correct for M0 paper; v2 found Dense/Hybrid stronger on **new** Roman KN — different population, must not rewrite 87.18% |
| Any implication that lexical Method D "solves" Roman | Stale if generalized beyond title_roman construction; PHASE14 Hit@5 25% best overall on n=80 |
| Stretch ~80% usefulness | PLOS already refuses 80% claim; v2 landed **55 pp short** of 80% Hit@5 stretch on n=80 |

## 12. TEST set (Program B) — path only, contents not read

| Item | Value |
|---|---|
| Directory (exists) | `experiments/ultra_v2/benchmark/test/` |
| Filenames listed (names only; **query CSVs not opened**) | `queries_kn.csv`, `queries_nl.csv`, `README.md`, `seal.json` |
| Contents of query CSVs / seal body | **Not read** in this inventory |

---

# Appendix A — Full PLOS ONE TeX (working tree)

Source: `Papers/PLOS_ONE/Adaptive_dynamic_query_routing_for_Urdu_information_retrieval.tex`
SHA-256: `21611d5bfa1c355103c329003edee5f8cbe9e4343b5fd1ef0e0297d9e9ecfd6e`

```latex
% Template for PLoS
% Version 3.8 Apr 2026
%
% Printed title: Script-aware BM25 retrieval for Urdu and Roman Urdu news search
% Filename kept for packaging paths. Official frozen system: M0 (script-aware BM25). Not SVM/MiniLM.
%
% PORTAL FIELDS --- fill these in PLOS Editorial Manager (confirmed 6 Sep 2026).
%   Funding: No specific funding was received for this work.
%   Competing interests: The authors have declared that no competing interests exist.
%   Author contributions (CRediT) -- paste into Editorial Manager, not the .tex body:
%     Hashim Shazad: Conceptualization, Methodology, Software, Formal analysis,
%     Writing -- original draft, Writing -- review & editing.
%     Adnan Aslam: Supervision, Writing -- review & editing.
%     Areena Rahman: Validation (independent A2 relevance annotation as a
%     reliability check only; A2 does not replace official A1 Success@5 of 23/40).
%   Data availability: third-party Urdu news compilation (Mendeley
%     10.17632/834vsxnb99.3; Kaggle Shahane Version 1). Frozen file
%     data/clean_articles.csv n=111860 SHA-256 8992a6ac... is NOT in GitHub.
%     Authors do not redistribute the article-text CSV. Redistribution
%     permission for underlying news text has not been independently verified.
%     Obtain the source from Kaggle/Mendeley; verify reconstructions against
%     the Corpus SHA-256. Dictionary, M0 code, queries, qrels, and REPRODUCE.md
%     are in https://github.com/HashimAbbasii/Dynammic-Query-Routing-Urdu-ILS
%     Official metrics were copied from sealed Phase 8--12 reports.
%   Ethics: conservative statement in the manuscript body. Do NOT enter IRB
%     approval, exemption, consent, or human-subjects approval.
%   ORCID: enter in the submission system (not invented in this file).
%   Short title: Script-aware BM25 for Urdu news search
%
% Figure image files are uploaded separately (no \includegraphics in this file).
% PLOS Editorial Manager upload names (TIFF derivatives):
%   Fig1.tif  Fig2.tif  Fig3.tif  Fig4.tif  Fig5.tif
% PNG sources retained in Papers/PLOS_ONE/figures/ (not overwritten):
%   Fig1_m0_routing.png
%   Fig2_development_comparators.png
%   Fig3_script_splits.png
%   Fig4_k_miss_analysis.png
%   Fig5_u_label_distribution.png
%
% % % % % % % % % % % % % % % % % % % % % %
%
% -- IMPORTANT NOTE
%
% This template contains comments intended
% to minimize problems and delays during our production
% process. Please follow the template instructions
% whenever possible.
%
% % % % % % % % % % % % % % % % % % % % % % %
%
% Once your paper is accepted for publication,
% PLEASE REMOVE ALL TRACKED CHANGES in this file
% and leave only the final text of your manuscript.
% PLOS recommends the use of latexdiff to track changes during review, as this will help to maintain a clean tex file.
% Visit https://www.ctan.org/pkg/latexdiff?lang=en for info.
%
%
% IMPORTANT
% Below are a few tips to help format manuscript according to our specifications. For more tips to help reduce the possibility of formatting errors during conversion, please see our LaTeX guidelines at http://journals.plos.org/plosone/s/latex
%
% There are no restrictions on package use within the LaTeX files except that no packages listed in the template may be deleted.
%
% Please do not include colors or graphics in the text.
%
% The manuscript LaTeX source should be contained within a single file (do not use \input, \externaldocument, or similar commands).
%
% % % % % % % % % % % % % % % % % % % % % % %
%
% -- FIGURES AND TABLES
%
% Please include tables/figure captions directly after the paragraph where they are first cited in the text.
%
% DO NOT INCLUDE GRAPHICS IN YOUR MANUSCRIPT
% - Figures should be uploaded separately from your manuscript file.
% - Figures generated using LaTeX should be extracted and removed from the PDF before submission.
% - Figures containing multiple panels/subfigures must be combined into one image file before submission.
% For figure citations, please use "Fig" instead of "Figure".
% See http://journals.plos.org/plosone/s/figures for PLOS figure guidelines.
%
% Tables should be cell-based and may not contain:
% - spacing/line breaks within cells to alter layout or alignment
% - do not nest tabular environments (no tabular environments within tabular environments)
% - no graphics or colored text (cell background color/shading OK)
% See http://journals.plos.org/plosone/s/tables for table guidelines.
%
% For tables that exceed the width of the text column, use the adjustwidth environment as illustrated in the example table in text below.
%
% % % % % % % % % % % % % % % % % % % % % % % %
%
% -- EQUATIONS, MATH SYMBOLS, OTHER SPECIAL FORMATTING
%
% - For bold symbols, use the \boldsymbol command and not \mathbf.
% - For inline equations, please be sure to include all portions of an equation in the math environment.  For example, x$^2$ is incorrect; this should be formatted as $x^2$ (or $\mathrm{x}^2$ if the romanized font is desired).
% - Do not include text that is not math in the math environment. For example, CO2 should be written as CO\textsubscript{2} instead of CO$_2$.
% - Avoid capturing simple text as equations, for example $<$.
% - For inline equations, please do not include punctuation (commas, etc) within the math environment unless this is part of the equation.
% - When adding superscript or subscripts outside of brackets/braces, please group using {}.  For example, change "[U(D,E,\gamma)]^2" to "{[U(D,E,\gamma)]}^2".
% - Do not use \cal for caligraphic font.  Instead, use \mathcal{}.
% - Avoid splitting for fragmenting a single equation into multiple objects/environments, for example $f(x)$ = $g(x)$ + $h(x)$.
% - Use math environment for all equations, do not mimic using text.
% - Avoid using single letters in math mode where possible.
% - Always use matching parentheses and delimiters, avoid mixing math and text brackets.
% - Insert spaces around inline equations to ensure proper display after conversion.
% - Do not use forced numbers for display equation labeling or suppress numbering with \nonumber.
%
% % % % % % % % % % % % % % % % % % % % % % % %
%
% Please contact customercare@plos.org with any questions.
%
% % % % % % % % % % % % % % % % % % % % % % % %

\documentclass[10pt,letterpaper]{article}
\usepackage[top=0.85in,left=2.75in,footskip=0.75in]{geometry}

% amsmath and amssymb packages, useful for mathematical formulas and symbols
\usepackage{amsmath,amssymb}

% Use adjustwidth environment to exceed column width (see example table in text)
\usepackage{changepage}

% textcomp package and marvosym package for additional characters
\usepackage{textcomp,marvosym}

% cite package, to clean up citations in the main text. Do not remove.
\usepackage{cite}

% Use nameref to cite supporting information files (see Supporting Information section for more info)
\usepackage{nameref,hyperref}

% line numbers
\usepackage[right]{lineno}

% ligatures disabled
\usepackage[nopatch=eqnum]{microtype}
% PLOS template command; pdftex-only. Tectonic (XeTeX) cannot DisableLigatures.
\ifdefined\pdftexversion
\DisableLigatures[f]{encoding = *, family = * }
\fi

% color can be used to apply background shading to table cells only
\usepackage[table]{xcolor}

% array package and thick rules for tables
\usepackage{array}

% create "+" rule type for thick vertical lines
\newcolumntype{+}{!{\vrule width 2pt}}
% ragged-right p-columns (template array package; reduces underfull table cells)
\newcolumntype{P}[1]{>{\raggedright\arraybackslash}p{#1}}

% create \thickcline for thick horizontal lines of variable length
\newlength\savedwidth
\newcommand\thickcline[1]{%
  \noalign{\global\savedwidth\arrayrulewidth\global\arrayrulewidth 2pt}%
  \cline{#1}%
  \noalign{\vskip\arrayrulewidth}%
  \noalign{\global\arrayrulewidth\savedwidth}%
}

% \thickhline command for thick horizontal lines that span the table
\newcommand\thickhline{\noalign{\global\savedwidth\arrayrulewidth\global\arrayrulewidth 2pt}%
\hline
\noalign{\global\arrayrulewidth\savedwidth}}


% Remove comment for double spacing
%\usepackage{setspace}
%\doublespacing

% Text layout
\raggedright
\setlength{\parindent}{0.5cm}
\textwidth 5.25in
\textheight 8.75in

% Bold the 'Figure #' in the caption and separate it from the title/caption with a period
% Captions will be left justified
\usepackage[aboveskip=1pt,labelfont=bf,labelsep=period,justification=raggedright,singlelinecheck=off]{caption}
\renewcommand{\figurename}{Fig}

% Please use the included `plos2025.bst` as your BibTeX style
\bibliographystyle{plos2025}

% Remove brackets from numbering in List of References
\makeatletter
\renewcommand{\@biblabel}[1]{\quad#1.}
\makeatother



% Header and Footer with logo
\usepackage{lastpage,fancyhdr,graphicx}
\usepackage{epstopdf}
%\pagestyle{myheadings}
\pagestyle{fancy}
\fancyhf{}
%\setlength{\headheight}{27.023pt}
%\lhead{\includegraphics[width=2.0in]{PLOS-submission.eps}}
\rfoot{\thepage/\pageref{LastPage}}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrule}{\hrule height 2pt \vspace{2mm}}
\fancyheadoffset[L]{2.25in}
\fancyfootoffset[L]{2.25in}
\lfoot{\today}

%% Include all user-defined macros below

%% END MACROS SECTION


\begin{document}
\vspace*{0.2in}

% Title must be 250 characters or less.
\begin{flushleft}
{\Large
\textbf{Script-aware {BM25} retrieval for {Urdu} and {Roman} {Urdu} news search} % Please use "sentence case" for title and headings (capitalize only the first word in a title (or heading), the first word in a subtitle (or subheading), and any proper nouns).
}
\newline
% Short title is a PLOS Editorial Manager field (not in the ZIP title block):
% Script-aware BM25 for Urdu news search
% Insert author names, affiliations and corresponding author email (do not include titles, positions, or degrees).
\\
Hashim Shazad\textsuperscript{1*},
Adnan Aslam\textsuperscript{1},
Areena Rahman\textsuperscript{1}
\\
\bigskip
\textbf{1} Department of Creative Technologies, Air University, Islamabad, Pakistan
\\
\bigskip

% Insert additional author notes using the symbols described below. Insert symbol callouts after author names as necessary.
%
% Remove or comment out the symbols in the byline and the author notes below if they aren't used.
%
% Primary Equal Contribution Note
% \Yinyang These authors contributed equally to this work.

% Additional Equal Contribution Note
% Also use this double-dagger symbol for special authorship notes, such as senior authorship.
% \ddag These authors also contributed equally to this work.

% Current address notes
% \textcurrency Current Address: Dept/Program/Center, Institution Name, City, State, Country % change symbol to "\textcurrency a" if more than one current address note
% \textcurrency b Insert second current address
% \textcurrency c Insert third current address

% Deceased author note
% \dag Deceased

% Group/Consortium Author Note
% \textpilcrow Membership list can be found in the Acknowledgments section.

% Use the asterisk to denote corresponding authorship and provide email address in note below.
* abbasihashim30@gmail.com

\end{flushleft}
% Please keep the abstract below 300 words

% For PLOS Medicine research article authors, please structure your abstract
% with "Background", "Method and Findings" and "Conclusion" sections per
% journal requirements.

% For PLOS Neglected Tropical Diseases research article authors, please
% structure your abstract with "Background", "Methodology", "Findings", and
% "Conclusion" sections per journal requirements.
%
\section*{Abstract}
Urdu news users often type native Perso-Arabic script, informal Roman Urdu, or a mixture of both, while a single native-script index will not match Latin-script queries even when the article exists. This paper reports a frozen lexical retriever, M0, on 111,860 Urdu news articles. A deterministic Unicode count of Perso-Arabic versus ASCII letters selects one of two Okapi BM25 indexes: Urdu, mixed, and other queries search native-script BM25; Roman queries search a second index whose documents were romanized with a closed character table and a 198-key reverse dictionary (Method D). The detector is not a learned classifier. Queries are not rewritten. BM25 uses~$k_1 = 1.5$ and~$b = 0.75$; lists are retrieved to depth 50 and scored at a Top-5 cutoff.

On a development/validation known-item pool of title-derived queries, ExactSource Hit@5 was 68/78 (87.18\%; Clopper--Pearson 95\% interval 77.68--93.68\%). On a newly sealed known-item sample the same frozen system achieved 27/40 (67.50\%; 50.87--81.43\%). On a separate sealed naturalistic set with no gold article, the first author (who also wrote the U queries) judged the Top-5 useful (at least one relevant or partially relevant document) for 23/40 queries (official A1 Success@5 57.50\%; 40.89--72.96\%). An independent second annotation (A2) is a reliability check only and does not replace 23/40. Query-side Roman expansions did not raise the 68/78 development score, so the freeze was not replaced. In the naturalistic sample, Urdu-script queries succeeded in 17/18 cases and Roman queries in 6/18; all four mixed queries failed.

These three percentages answer different questions and must not be averaged. On the freeze pool, 68 of 78 title-derived known items reached the Top-5. Ordinary Roman Urdu remains the main limitation. This is a hashed empirical evaluation of script-aware BM25, not a learned or online index-selection policy.

% Please keep the Author Summary between 150 and 200 words. Use first person.
% PLOS ONE, PLOS Biology, PLOS Global Public Health, PLOS Mental Health, and PLOS Water authors please skip this step. Author Summary is not valid for submissions to these journals.


\clearpage
\newgeometry{top=0.85in,left=1in,right=1in,footskip=0.75in}
\linenumbers

% Use "Eq" instead of "Equation" for equation citations.
\section*{Introduction}
Urdu is written in a cursive Perso-Arabic script, but that is not how everyone searches. A large share of users type Roman Urdu: Urdu words in Latin letters, with spelling that is informal and inconsistent~\cite{bib1,bib2,bib3}. A news collection indexed only in native script will not match those queries even when the article is sitting in the index. That mismatch is a retrieval failure, not a missing document.

Urdu remains thinner in shared information retrieval (IR) evaluation than English~\cite{bib4}. Collections exist. CURE provides an Urdu ranking resource~\cite{bib5}. An Urdu MS MARCO baseline reports MRR@10 of 0.247 in the abstract (0.248 in the results table) for a fine-tuned Urdu mT5-mMARCO configuration, under a passage-ranking protocol that is not the one used here~\cite{bib6}. Those resources do not freeze a script-conditional lexical system and then keep known-item recovery separate from human usefulness. Roman Urdu research is still mostly classification---sentiment, offensive language---rather than news search~\cite{bib1,bib2}. Multilingual dense retrievers can lose effectiveness on languages that sit outside the pretraining head~\cite{bib7}, even when scaled multilingual encoders help related tasks such as Urdu natural language inference~\cite{bib8}. Users of lower-resource varieties are also often pushed toward high-resource query forms~\cite{bib9}. Typing Roman Urdu into an Urdu-script index is a concrete instance of that pressure.

The ULTRA framework of Bashir, Qaiser, and Hussain supplies a dual-embedding Urdu news architecture~\cite{bib10}. Its original switch is a static character-length threshold. Length is easy to implement and easy to fool: a short ``why'' question may need the article body, and a long factoid may be answered by a headline. Length also does not decide which \emph{script index} to open. English work on query routing chooses among sparse and dense retrievers~\cite{bib11} or varies retrieval depth in retrieval-augmented generation~\cite{bib12}. Those systems were not designed for Roman Urdu, and they are not what is evaluated here.

This paper asks a narrower empirical question that can be answered with a freeze and a protocol. Specify a lexical retriever. Hash the corpus and the Roman dictionary. Then measure three things that are easy to mix and should not be mixed. First, how often does the system recover a designated source article from title-derived queries on the development/validation pool used to select the Roman path? Second, does that known-item score hold on a newly sealed sample of title-like queries written after the freeze? Third, how often is the Top-5 useful when there is no gold article and a person judges the hits?

Official retrieval here is Okapi BM25~\cite{bib13} with a deterministic Unicode script detector that selects one of two lexical indexes. We call that frozen configuration M0. In this paper, \emph{script-aware index selection} means only that choice: URDU, MIXED, and OTHER queries open Urdu BM25; ROMAN queries open Method D. It is not online adaptation, not query rewriting, and not a learned SHORT/LONG classifier. Earlier work in the same project trained a SHORT/LONG support vector machine and a MiniLM dual-index using a Sentence-{BERT} encoder~\cite{bib14}. Those experiments are historical development, not the official retriever. We mention them only where they were actual development comparators, so that older classification or dense-index numbers are not mistaken for M0.

The contribution is empirical: a hashed freeze of that script-aware BM25 pipeline on one Urdu news collection, evaluations that keep known-item recovery separate from human usefulness, and a documented limitation on ordinary Roman Urdu. We do not claim a new learned routing algorithm, state of the art against CURE or Urdu MS MARCO, or a general solution to Roman Urdu search.

\subsection*{Research questions}

\begin{itemize}
\item \textbf{RQ1.} Can a script-aware lexical pipeline (Urdu BM25 plus Method D) recover known news articles from title-derived queries on a development/validation pool?
\item \textbf{RQ2.} Does that known-item score transfer to a newly sealed known-item sample written independently of the freeze set?
\item \textbf{RQ3.} How often is frozen M0 useful---at least one relevant or partially relevant document in the Top-5---on new naturalistic queries with no gold article?
\item \textbf{RQ4.} Do query-side Roman expansions improve development/validation ExactSource Hit@5 enough to replace M0?
\end{itemize}

\section*{Materials and methods}
\subsection*{Research design}

The study is an offline IR evaluation of one frozen lexical system. Method selection used a pre-registered development split. The official unseen tests were sealed before retrieval. No test query was used to choose BM25 parameters, the script-to-index rule, the Roman method, or the dictionary. After the freeze, later query-side expansions were accepted only if they improved the development known-item score; they did not, and M0 was left in place.

Two tasks are reported. Known-item search asks whether a pre-assigned source document appears in the Top-5. Naturalistic search has no source identifier; a human labels the retrieved Top-5. Those tasks are not averaged.

Official results are the development/validation known-item pool ($n = 78$), sealed K001--K040, and sealed U001--U040 with Annotator-1 labels. Phase 11 (M1--M4), H001--H040, and dense-index pilots are diagnostic or historical. After those official scores were frozen, later exploratory development on a separate git branch is outside this paper (Limitations).

\subsection*{Evaluation hierarchy}

Four layers must not be mixed.

\begin{itemize}
\item \textbf{A. Freeze-pool known-item} ($n = 78$). Metric: ExactSource Hit@5 (secondary nDCG@5, MRR). Used to select Method D and freeze M0.
\item \textbf{B. Phase 12 K} (K001--K040). Same known-item metric on a sealed sample. Not human usefulness.
\item \textbf{C. Phase 12 U} (U001--U040). Official Annotator-1 human Success@5 (secondary P@5, nDCG@5, MRR). No \texttt{source\_doc\_id}.
\item \textbf{D. A2.} Independent labels on the same 200 U Top-5 documents. Reliability only. Does not replace C.
\end{itemize}

H001--H040 are a historical diagnostic. They are not A--D.

\subsection*{Corpus}

The official collection is \texttt{data/clean\_articles.csv}: 111,860 news articles (540,050,203 bytes). The local precursor is \texttt{data/urdu\_news.csv} (111,861 CSV records). That precursor is schema- and size-consistent with Version 1 of the Kaggle listing ``Urdu News Dataset'' compiled by Shahane (file \texttt{urdu-news-dataset-1M.csv}; displayed size 276.79~MB)~\cite{bib17}. The Kaggle page cites Hussain, Mughal, Ali, Hassan, and Daudpota, ``Urdu News Dataset 1M'', Mendeley Data, V3, doi:10.17632/834vsxnb99.3~\cite{bib16}. A SHA-256 comparison of a fresh Kaggle or Mendeley download to the local precursor was not completed. The compilation title uses ``1M''; the Kaggle Version 1 explorer and the local precursor contain 111,861 records, not one million. Whether that Kaggle file is the complete Mendeley dump was not verified.

The last precursor record is truncated (three CSV fields instead of eight; \texttt{Index} 111860; no trailing newline). \texttt{pandas.DataFrame.dropna()} dropped that incomplete row, leaving 111,860 articles. Headline and body were then concatenated:

\texttt{combined\_text = Headline + ' ' + News Text}

There was no Unicode NFKC folding, no ye/he/kaf canonicalization, no diacritic stripping, no stemming, no stopword removal, and no deduplication at indexing. HTML, punctuation, English tokens, and near-duplicate articles were left as in the source dump. Document identifiers equal the corpus row index after that cleaning step. Article categories in the dump are Sports, Business \& Economics, Entertainment, and Science \& Technology.

Corpus SHA-256: \texttt{8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231} (540,050,203 bytes). The Roman dictionary is \texttt{models/roman\_urdu\_dict\_expanded.json} (198 keys; SHA-256 \texttt{30c3f61a64ec641abbb3acdbc7a8bcaf197f0238f1bf9e76c2c7ce8e590f86a3}). Preprocessing cells are in \texttt{archive/historical\_experiments/notebooks/01\_preprocessing.ipynb}. Reconstruction notes are in \texttt{experiments/publication\_audit/}.

\subsection*{Official frozen system (M0)}

% For figure citations, please use "Fig" instead of "Figure".
Fig~\ref{fig1} summarizes M0. Internally the system retrieves 50 documents; the official cutoff is 5. Queries are not rewritten on the official path.

% Place figure captions after the first paragraph in which they are cited.
\begin{figure}[!h]
\caption{\textbf{Official frozen retriever M0.} A deterministic Unicode script detector sends URDU, MIXED, and OTHER queries to Urdu BM25 and ROMAN queries to Method D romanized-document BM25. Queries are not rewritten. This is not an SVM SHORT/LONG classifier and not a MiniLM dual-index pipeline.}
\label{fig1}
\end{figure}

The detector counts characters in the Arabic/Urdu block U+0600--U+06FF and ASCII letters A--Z/a--z. If both counts are zero the label is OTHER. If both are positive the label is MIXED. If only the Urdu count is positive the label is URDU. Otherwise the label is ROMAN. URDU, MIXED, and OTHER search Urdu BM25 over \texttt{combined\_text}. ROMAN searches Method D BM25 over romanized documents. The detector is not a classifier. On the Phase 2 development/validation pool it agreed with the oracle script tags on 78/78 queries. The nine MIXED items in that pool were mixed by construction (an English template suffix), not detector errors.

Tokenization is the same on both indexes: the regular expression \texttt{[\textbackslash u0600-\textbackslash u06FF]+|[A-Za-z0-9]+}, lowercase, no stemming, no stopword list. BM25 is Okapi with frozen $k_1 = 1.5$ and $b = 0.75$. Inverse document frequency for term $t$ with document frequency $n$ in a collection of $N$ documents is
\begin{eqnarray}
\label{eq:idf}
\mathrm{idf}(t) = \log\left(\frac{N - n + 0.5}{n + 0.5} + 1\right).
\end{eqnarray}

The implementation is the custom \texttt{BM25} class in \texttt{experiments/phase5\_roman\_urdu/run\_phase5.py}. The Urdu index has 371,368 terms and mean document length 279.24 tokens. The Method D index has 358,497 terms and mean document length 279.19 tokens.

\subsection*{Method D}

Method D keeps the typed Roman query and indexes romanized documents. Every article in the 111,860-document collection is romanized; the index is not restricted to evaluation source documents. After tokenization, each token is handled as follows. If it contains Urdu letters and that exact token is a value in the 198-key dictionary, emit the first reverse-mapped Latin key (\texttt{setdefault}; first key wins). Otherwise emit a character-table romanization (\texttt{\_CHAR\_ROMAN} from the Phase 2 pipeline). Tokens that are already Latin or alphanumeric are lowercased and kept. The character table maps, among other pairs, madda alif to \texttt{aa} and che to \texttt{ch}, and collapses several Urdu letters onto the same Latin letter (for example te and tte both map to \texttt{t}). That collision is intentional and lossy.

Method D is the document-side counterpart of Phase 2 \texttt{title\_roman} generation. It is not a mapping fitted to evaluation query strings.

\subsection*{Roman-method selection (Phase 5)}

Four Roman strategies were pre-registered and compared on development Roman known-item queries only ($n = 13$), before internal-validation scores were interpreted. Selection used ExactSource Hit@5, then nDCG@5, then lower mean query latency. BM25 hyperparameters were not retuned. Method comparison counts are in \nameref{S3_Table}.

Method A sends the raw Roman query to the Urdu-script BM25 index. Method B transliterates with the existing 198-key dictionary and then searches that same Urdu index; unmapped tokens stay Latin. Method C applies a closed spelling-variant table, dictionary lookup, and a greedy inverse of the Phase 2 character table, then searches Urdu BM25. Method D is the romanized-document index described above. A fifth analysis, Method E, reported the union of C and D; it was not a selectable system, and reciprocal rank fusion was not built~\cite{bib15}.

The selected method was frozen in \texttt{artifacts/selected\_method.json} before internal validation ($n = 10$ Roman queries) was read. Mixed queries under the deployable rule go to Urdu BM25. Urdu queries always use Urdu BM25. Method D was selected on $n = 13$ development Roman queries.

\subsection*{Development/validation known-item pool}

Phase 2 built 260 title-derived known-item queries from corpus articles that were not used in earlier trap sets. Each query has one \texttt{source\_doc\_id}. Templates include short title, romanized title, why/how/effects, lead excerpt, and mixed Urdu+English. Roman strings in this pool are \texttt{title\_roman}: dictionary reverse lookup plus the character table applied to headlines. They are not chat-style Roman Urdu. The split (seed 42) is train $n = 182$, development $n = 39$, internal validation $n = 39$. Official M0 development/validation reporting uses development plus internal validation ($n = 78$). The train split was not used to select Method D; it was later used only as a diagnostic pool for query-side expansions.

\subsection*{Query-side expansions (Phase 11)}

After M0 was frozen, four query-side Roman transforms were scored on the same $n = 78$ pool. The hard gate was ExactSource Hit@5 not below 68/78. A train-Roman diagnostic ($n = 64$) was used only among candidates that passed the gate. H001--H040 and the later sealed sets were not loaded.

M0 applies no query transform. M1 appends a closed alias list while keeping original tokens. M2 adds four further aliases. M3 applies M1 then drops a nine-token query stoplist. M4 combines M1, M2, and the stoplist. The 198-key dictionary file was not edited. Terms such as \texttt{diesel} and \texttt{iphone} were explicitly forbidden as new keys. The official Phase 12 run did not apply M1--M4.

\subsection*{Sealed evaluation (Phase 12)}

K001--K040 (known-item) and U001--U040 (naturalistic) were written and checksum-sealed before retrieval (seed 120260827). Query-file SHA-256 values are \texttt{124e452693f98baedf510618240c154df68d56b6b7a37ed085a6512c13d13ff6} (K) and \texttt{684fd1e19eddb717f5897d869ef0ca0ed586316c5a7e1d2d23006e0748fc53b9} (U). One retrieval pass of frozen M0 produced Top-50 lists. Queries were not edited after ranks were seen. M1--M4 were not applied.

K queries are shortened or lightly paraphrased headlines from articles that were not Phase 2 QTRN sources (260 source identifiers excluded; eligible population 111,574 headlines of length at least 12 after stripping). The creator could see the source article in order to assign \texttt{source\_doc\_id} and did not run BM25 while writing. The 12 Roman K queries are ordinary Roman Urdu of the selected headline, not \texttt{title\_roman} character-table strings. No mixed-script K query occurred naturally; mixed script was not forced.

U queries follow pre-registered naturalistic quotas: 18 Urdu, 18 Roman, 4 mixed; 12 short ($\leq 5$ whitespace tokens), 16 medium (6--12), 12 long (13+); 14 factoid, 14 explanatory, 12 named-entity. Four temporal factoids use \emph{aaj} / \texttt{aaj} / \texttt{mojooda} forms. U has no \texttt{source\_doc\_id}. Queries were not copied from H001--H040. After retrieval, detector counts were 18 URDU, 18 ROMAN, and 4 MIXED; retrieval-path counts were 22 Urdu BM25 (URDU plus MIXED) and 18 Method D. Thirty-nine queries returned 50 hits; U006 returned 28. No query returned fewer than five hits.

\subsection*{Human relevance protocol (U only)}

After the sealed Top-5 dump existed, the first author labeled 200 documents (40 queries $\times$ 5) from headline and snippet only. The same author had written the sealed U queries under the Phase 12 protocol. Labels follow a five-way rubric: A, relevant (the reader could stop); B, partially relevant (same event or occasion, incomplete answer); C, topically related (same topic or entity, not the asked need); D, not relevant; E, ambiguous if A--D cannot be decided. The annotator preferred B over A unless the need was clearly satisfied, and preferred C over B unless the article helped answer the asked need. Temporal queries were judged as archive type-of-fact for a dated occasion in the article, not against the annotator's calendar day. Recurring wires with no date in the query (gold price, budget date, eclipse, stock close) could be A even if dates differed. Named-entity lookups were A if the article's main subject was that person. The original evaluation labels (A1) were retained as the official evaluation labels. An independent second annotation (A2) was subsequently conducted by Areena Rahman on the same 200 query-document judgments as a reliability check; A2 was not used to replace or recompute the reported A1 results (\nameref{S2_File}; per-query labels in \nameref{S4_Table}). Official Success@5 remains Annotator 1 (23/40). ExactSource Hit@5 was not computed on U. Label definitions are in \nameref{S1_Text}.

\subsection*{Ethics}

Relevance labels for U001--U040 were assigned by annotators to retrieved public news headlines and snippets. No search-user logs, interviews, or other identifiable participant records were collected for this evaluation. No institutional ethics-board determination is recorded in the project repository.

\subsection*{Metrics}

For a known-item query with source identifier $s$, ExactSource Hit@$k$ is 1 if and only if $s$ appears in the retrieved top $k$. The official cutoff is $k = 5$. Secondary K cutoffs are 1, 10, and 50. Known-item nDCG@5 on the development pool uses gain $1/\log_2(\mathrm{rank}+1)$ when the source is in the Top-5, else 0. Known-item P@5 equals 0.2 times Hit@5 because there is a single relevant document.

For naturalistic queries, Success@5 is 1 if and only if at least one Top-5 document is A or B. Conservative P@5 is the mean of (count of A labels)/5. nDCG@5 uses gains A $= 3$, B $= 2$, C $= 1$, D $=$ E $= 0$. MRR is the reciprocal rank of the first A or B, or 0 if none. nDCG@5 is secondary: a Top-5 of only topical C documents can score nDCG@5 $= 1$ with no A or B.

Clopper--Pearson 95\% intervals were computed from the reported binomial counts using SciPy's \texttt{binomtest} (SciPy 1.16.3). They were not part of method selection. No hypothesis test comparing systems on K or U was pre-registered; we do not report $p$-values for those splits.

\subsection*{Rejected alternatives}

Development comparators on the same $n = 78$ pool include headline MiniLM, a truncated full-article Chroma index, a 96/32 chunk approximate nearest-neighbour index, and Urdu-only BM25. A pre-registered long-context \texttt{intfloat/multilingual-e5-small} index was not built: a CPU prototype ran at 2.3 documents/s (about 13.5 hours extrapolated for 111,860 articles) and failed a 4-hour gate. The encoder was not swapped after that failure. Fusion of headline and script-aware lists was not deployed: an oracle union added three known-item hits, which was judged insufficient. A reranker was not built. Historical SHORT/LONG SVM index selection and MiniLM dual-index graded P@5 on H001--H040 are a separate development study. They are not official M0 metrics.

\subsection*{Diagnostic set H001--H040}

H001--H040 are historical trap strings with no source identifier. ExactSource Hit@5 is undefined on that set. A later human pass (Phase 10C) labeled 196 retrieved rows (38 queries $\times$ 5, plus H027 $\times$ 5 and H036 $\times$ 1; H036 returned a single document). Success@5 was 25/40; conservative P@5 was 0.1250; 10/40 lists were all D. On that sample, Success@5 was 14/20 for Urdu-script queries and 11/20 for Roman; eight of the ten all-D lists were Roman. Labels were assigned from headline plus a 500-character snippet. Query text, rank-1, and labels are now known. The set is treated as a historical diagnostic and is not the official unseen usefulness result. It is not combined with U.

\subsection*{Software environment and reproducibility}

M0 retrieval uses Python 3.13.9 (Anaconda, 64-bit Windows). Dense-index pilots in the same project ran on CPU (12 cores reported for the e5-small prototype). Method D index construction on the full corpus took 100.6 s (66.3 s tokenize and romanize, 34.3 s BM25 postings) and occupied 116.1 MB of in-memory postings. Entry points were not relocated: detector and BM25 in \texttt{experiments/phase5\_roman\_urdu/run\_phase5.py}, character table in \texttt{experiments/phase2\_oracle/run\_phase2\_pipeline.py}, sealed runner in \texttt{experiments/phase12\_new\_unseen\_evaluation/run\_phase12.py}. The freeze manifest is \texttt{experiments/phase8\_final\_freeze/FINAL\_SYSTEM\_MANIFEST.json} (\nameref{S1_File}). A SHA-256 check for a local copy of the frozen corpus is \texttt{experiments/publication\_audit/verify\_corpus\_hash.py}. Reproduction steps, environment pins, and data-access limits are in the repository file \texttt{REPRODUCE.md} on branch \texttt{publication/plos-one-final}. Code, the Roman dictionary, sealed queries, qrels, and reconstruction notes are in git. Full retrieval reproduction requires a local copy of the third-party article-text corpus; a git clone does not contain that CSV. This manuscript does not claim that a clean-clone full-corpus rerun was completed for publication.

\subsection*{Data availability}

The retrieval collection is a locally processed copy of a third-party Urdu news compilation titled Urdu News Dataset 1M~\cite{bib16}. The local precursor \texttt{data/urdu\_news.csv} (111,861 records) is schema- and size-consistent with Shahane, Urdu News Dataset, Kaggle Version 1, file \texttt{urdu-news-dataset-1M.csv}~\cite{bib17}. That Kaggle listing cites Hussain, Mughal, Ali, Hassan, and Daudpota, Mendeley Data, V3, doi:10.17632/834vsxnb99.3~\cite{bib16}. A SHA-256 identity check between a fresh provider download and the local precursor was not completed. The compilation title uses ``1M''; the file used here has 111,861 precursor records and 111,860 frozen articles.

The frozen file used for all official M0 scores is \texttt{data/clean\_articles.csv} (111,860 articles; 540,050,203 bytes; SHA-256 \texttt{8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231}). Preprocessing dropped one truncated precursor record with \texttt{dropna()} and concatenated headline and body as described in the Corpus subsection. The authors do not redistribute the full article-text CSV in the project GitHub repository or in Supporting Information. Redistribution permission for the underlying news article text has not been independently verified. Researchers should obtain the source dataset from Kaggle and/or Mendeley under those providers' terms, then verify any reconstructed file against that SHA-256. Reconstruction notes without article text are in \nameref{S3_File}. The Roman Urdu dictionary (\texttt{models/roman\_urdu\_dict\_expanded.json}; 198 keys), M0 code, sealed query files, human qrels, and reconstruction notes are at \url{https://github.com/HashimAbbasii/Dynammic-Query-Routing-Urdu-ILS} (branch \texttt{publication/plos-one-final}; \texttt{REPRODUCE.md}). A git clone of the default branch does not by itself select this submission snapshot. A git clone does not contain the article-text corpus. Official metrics were copied from sealed Phase 8--12 reports and were not recomputed for this manuscript.

% Results and Discussion can be combined.
\section*{Results}
Table~\ref{table1} reports the three official headlines. The rows are different tasks. They are not a single accuracy trajectory.

% Place tables after the first paragraph in which they are cited.
\begin{table}[!ht]
\centering
\caption{\textbf{Official M0 results.} ExactSource Hit@5 and human Success@5 answer different questions. Intervals are Clopper--Pearson 95\% intervals computed from the reported counts. Do not average rows. Do not treat 87.18\% as unseen or as human usefulness.}
\begin{tabular}{|P{3.5cm}|P{2.5cm}|P{2.7cm}|P{4.7cm}|}
\hline
\textbf{Evaluation} & \textbf{Dataset} & \textbf{Metric} & \textbf{Result} \\
\hline
Development\slash validation known-item & Phase 2, $n = 78$ & ExactSource Hit@5 & 68/78 (87.18\%; 77.68--93.68\%) \\
\hline
New known-item & K001--K040 & ExactSource Hit@5 & 27/40 (67.50\%; 50.87--81.43\%) \\
\hline
New naturalistic (human) & U001--U040 & Success@5 & 23/40 (57.50\%; 40.89--72.96\%) \\
\hline
\end{tabular}
\label{table1}
\end{table}

\subsection*{Development/validation known-item}

ExactSource Hit@5 on development plus internal validation was 68/78. Secondary known-item metrics on that pool were nDCG@5 $= 0.8107$ and MRR $= 0.797$. An independent rebuild in a later phase reproduced Hit@5 $= 0.8718$.

Table~\ref{table2} and Fig~\ref{fig2} place M0 against the development comparators that were actually run. Urdu-only BM25 (no Roman path) scored 0.5897. Headline MiniLM scored 0.4487. The truncated full-article dense index scored 0.2564, worse than headlines, consistent with truncation at 128 tokens. Chunk ANN scored 0.2821. Those dense numbers are development evidence that a full MiniLM index was not a substitute for a Roman lexical path. They are not Phase 12 results.

\begin{table}[!ht]
\centering
\caption{\textbf{Development/validation comparators on the same $n = 78$ known-item pool.} Official M0 is the script-aware row. Oracle unions were not deployed.}
\begin{tabular}{|l|r|r|r|}
\hline
\textbf{System} & \textbf{Hit@5} & \textbf{nDCG@5} & \textbf{MRR} \\
\hline
Truncated full MiniLM (Chroma) & 0.2564 & 0.2203 & 0.2103 \\
\hline
Chunk ANN (96/32) & 0.2821 & 0.2362 & 0.2309 \\
\hline
Headline MiniLM & 0.4487 & 0.4009 & 0.3885 \\
\hline
Urdu BM25, no Roman path & 0.5897 & 0.5509 & 0.5425 \\
\hline
Script-aware M0 & 0.8718 & 0.8107 & 0.797 \\
\hline
Headline + M0 oracle (not deployed) & 0.9103 & 0.8703 & 0.8615 \\
\hline
\end{tabular}
\label{table2}
\end{table}

\begin{figure}[!h]
\caption{\textbf{ExactSource Hit@5 on the Phase 2 development/validation pool ($n = 78$).} Values are the frozen development comparators in Table~\ref{table2}. Script-aware M0 is the official system. This figure is not a Phase 12 result.}
\label{fig2}
\end{figure}

On the 46 Urdu-script queries in that pool, Urdu BM25 Hit@5 was 0.913; sending those queries to the same Urdu index left that number unchanged. On the 23 Roman queries, Method A was 0/23 and headline MiniLM was 1/23. Method D recovered 22/23 (development 13/13, internal validation 9/10). The remaining miss, QTRN\_031, was rank 9 with 10 overlapping tokens against the romanized source: Hit@10 succeeded, so the residual was ranking competition rather than a remaining script mismatch. Method B remained 0/13 on development Roman queries: 22 of 23 Roman strings were still mostly Latin after dictionary lookup. Method C tied Method D on development Hit@5 (13/13) but lost on nDCG@5 (0.8004 versus 0.9331) and would have scored 6/10 on internal validation in a post-hoc diagnostic that was not used for selection. Mixed queries ($n = 9$) scored Hit@5 $= 0.4444$ on the Urdu path; a mixed-path union did not raise that figure.

A later rebuild (Phase 6) reproduced 68/78 and listed the ten residual misses: four URDU, one ROMAN (QTRN\_031), and five MIXED. Four of those ten sat in ranks 6--10. Mixed-script items in this pool were generated with an English template suffix, so those misses are not a census of naturally mixed user queries. A qualitative primary label was assigned to each of those ten residuals (query ambiguity, wrong index room, entity collision, topical neighbour, or known-item ambiguity among near-duplicate wires). Those labels describe that freeze-pool remainder. They are not a rate, and they are not the Phase 12 diagnosis: sealed Roman misses are mostly sources that never enter the Top-50.

The 87.18\% result is genuine for title-derived known-item search on this pool, including Roman queries that resemble Method D's own romanization. It is not a forecast of chat-style Roman performance.

\subsection*{Phase 11 ablation}

Table~\ref{table3} reports the query-side expansions. M0 through M4 all scored 68/78. Train-Roman Hit@5 stayed 61/64 (95.31\%). M1--M4 nDCG@5 and MRR on that diagnostic were slightly below M0 (0.8940 and 0.8781 versus 0.8960 and 0.8807). No candidate beat 68/78. M1 passed the gate as the simplest non-destructive candidate and was not installed as the official system.

\begin{table}[!ht]
\centering
\caption{\textbf{Phase 11 query-side Roman expansions.} The official system remains M0. Train Roman $n = 64$ is a selection diagnostic, not an unseen test.}
\begin{tabular}{|l|c|c|c|c|}
\hline
\textbf{Model} & \textbf{$n = 78$ Hit@5} & \textbf{Train Roman Hit@5} & \textbf{Train nDCG@5} & \textbf{Train MRR} \\
\hline
M0 (official) & 68/78 & 0.9531 & 0.8960 & 0.8807 \\
\hline
M1 & 68/78 & 0.9531 & 0.8940 & 0.8781 \\
\hline
M2 & 68/78 & 0.9531 & 0.8940 & 0.8781 \\
\hline
M3 & 68/78 & 0.9531 & 0.8940 & 0.8781 \\
\hline
M4 & 68/78 & 0.9531 & 0.8940 & 0.8781 \\
\hline
\end{tabular}
\label{table3}
\end{table}

\subsection*{New known-item (K001--K040)}

Preflight passed: corpus and dictionary hashes matched the freeze, BM25 parameters were unchanged, and M1--M4 were off. Every query returned 50 hits. Detector counts were 28 URDU and 12 ROMAN, matching the retrieval-path counts.

Table~\ref{table4} reports ExactSource Hit at four cutoffs. The primary metric is Hit@5 $= 27/40$. Hit@1 is 20/40. Two further sources appear between ranks 6 and 50 (Hit@10 $= 28/40$, Hit@50 $= 30/40$). Ten of the 13 Hit@5 misses are absent from the entire Top-50; three are in the list but below rank 5 (K002 rank 6, K010 rank 49, K031 rank 17). Per-query source ranks are in \nameref{S1_Table}.

\begin{table}[!ht]
\centering
\caption{\textbf{Phase 12 K ExactSource results, frozen M0.} Primary metric is Hit@5. This evaluation does not replace 68/78 and is not human Success@5.}
\begin{tabular}{|l|l|}
\hline
\textbf{Metric} & \textbf{Result} \\
\hline
ExactSource Hit@1 & 20/40 (50.00\%) \\
\hline
ExactSource Hit@5 & 27/40 (67.50\%; 50.87--81.43\%) \\
\hline
ExactSource Hit@10 & 28/40 (70.00\%) \\
\hline
ExactSource Hit@50 & 30/40 (75.00\%) \\
\hline
\end{tabular}
\label{table4}
\end{table}

The detector split was not used for tuning. Urdu-script K titles scored 26/28 ExactSource Hit@5 (92.86\%; 76.50--99.12\%). Ordinary Roman titles scored 1/12 (8.33\%; 0.21--38.48\%). Fig~\ref{fig3} shows that split beside the naturalistic script split. Fig~\ref{fig4} separates Hit@5 from ``source present but below rank 5'' and ``source absent from the Top-50.'' Both Urdu misses (K002 rank 6, K010 rank 49) are still in the list. Ten of eleven Roman misses never enter the Top-50; the remaining Roman miss (K031) is rank 17. The drop from 87.18\% to 67.50\% is concentrated on ordinary Roman title queries, and on matching rather than near-miss ranking, not on native-script Urdu BM25.

\begin{figure}[!h]
\caption{\textbf{Descriptive script splits of frozen M0, not used for tuning.} Left: ExactSource Hit@5 on K001--K040. Right: human Success@5 on U001--U040. Mixed $n = 4$ is descriptive only. The two panels are different metrics and must not be averaged.}
\label{fig3}
\end{figure}

\begin{figure}[!h]
\caption{\textbf{Where sealed known-item misses sit.} Counts from the K001--K040 per-query source ranks. Urdu misses remain inside the Top-50. Most Roman misses never appear in the retrieved 50.}
\label{fig4}
\end{figure}

\subsection*{Naturalistic human evaluation (U001--U040)}

Success@5 was 23/40. Conservative P@5 was 0.2050 (variable-denominator P@5 was identical because every query had at least five hits). nDCG@5 was 0.6460. MRR was 0.4542. Among 200 labeled documents the counts were A 41, B 26, C 53, D 80, E 0 (Table~\ref{table5}; Fig~\ref{fig5}). Forty-one fully answering documents across 40 queries is consistent with conservative P@5 $= 0.2050$: many Top-5 lists contain at most one A.

\begin{table}[!ht]
\centering
\caption{\textbf{Phase 12 U human metrics, frozen M0 Top-5.} Success@5 is the usefulness headline. nDCG@5 includes gain 1 for topical C and is not a usefulness claim.}
\begin{tabular}{|l|l|}
\hline
\textbf{Metric} & \textbf{Result} \\
\hline
Success@5 (any A or B) & 23/40 (57.50\%; 40.89--72.96\%) \\
\hline
Conservative P@5 (A-count/5) & 0.2050 \\
\hline
nDCG@5 (A=3, B=2, C=1) & 0.6460 \\
\hline
MRR (first A or B) & 0.4542 \\
\hline
Label counts (200 documents) & A 41, B 26, C 53, D 80, E 0 \\
\hline
All-D queries & 12/40 \\
\hline
\end{tabular}
\label{table5}
\end{table}

\begin{figure}[!h]
\caption{\textbf{Label mass on the 200 judged U Top-5 documents.} A = relevant, B = partially relevant, C = topically related, D = not relevant, E = ambiguous. E did not occur. D is the modal label.}
\label{fig5}
\end{figure}

The gap between Success@5 and conservative P@5 is the shape of many successes: one useful document rather than a Top-5 packed with full answers. nDCG@5 overstates usefulness for the same reason the gain table is generous to C.

Fig~\ref{fig3} and Table~\ref{table6} show descriptive slices. Urdu-script queries succeeded in 17/18 cases (94.44\%; 72.71--99.86\%). Roman queries succeeded in 6/18 (33.33\%; 13.34--59.01\%). Mixed queries were 0/4 (0--60.24\%). Mixed $n = 4$ is too small for a population rate; it is reported because all four failed. These slices describe this sealed sample. They are not a licence to retune Method D on U failures.

\begin{table}[!ht]
\centering
\caption{\textbf{Descriptive U Success@5 slices.} Script uses the detector label at retrieval time. Need type and length follow the sealed query file.}
\begin{tabular}{|l|r|r|r|}
\hline
\textbf{Slice} & \textbf{Successes} & \textbf{$n$} & \textbf{Rate} \\
\hline
URDU & 17 & 18 & 0.9444 \\
\hline
ROMAN & 6 & 18 & 0.3333 \\
\hline
MIXED & 0 & 4 & 0.0000 \\
\hline
Factoid & 9 & 14 & 0.6429 \\
\hline
Explanatory & 9 & 14 & 0.6429 \\
\hline
Named entity & 5 & 12 & 0.4167 \\
\hline
Short ($\leq 5$ tokens) & 9 & 12 & 0.7500 \\
\hline
Medium (6--12) & 6 & 16 & 0.3750 \\
\hline
Long (13+) & 8 & 12 & 0.6667 \\
\hline
Temporal & 3 & 4 & 0.7500 \\
\hline
Non-temporal & 20 & 36 & 0.5556 \\
\hline
\end{tabular}
\label{table6}
\end{table}

Complete Success@5 failures were U004, U006, U008, U010, U014, U016, U018, U020, U026, U028, U032, U034, U035, U037, U038, U039, and U040. Twelve of those lists were all D, including several English-loan or service queries (\texttt{psl points table}, train-ticket price, Netflix charges, 5G, dollar rate) and several chat-style Roman strings. Per-query labels are in \nameref{S2_Table}.

\subsection*{Diagnostic H001--H040}

Phase 10C human Success@5 on H001--H040 was 25/40 (62.50\%; 45.80--77.27\%), with conservative P@5 $= 0.1250$ and 10/40 all-D lists. Urdu-script traps succeeded in 14/20 cases and Roman traps in 11/20; eight of the ten all-D lists were Roman. H036 returned one document, labeled D. The queries are historical trap strings, not the Phase 12 naturalistic sample. The number is recorded so it is not silently dropped; it is not the official unseen usefulness result.

\section*{Discussion}
The three headline percentages look like a system falling apart. They are three measurements.

On the freeze pool, M0 often recovers a known article from a shortened headline, including Roman queries built as \texttt{title\_roman}. Method D was selected on that construction. High Hit@5 is what one should expect when the query is a title fragment and, for Roman, when the spelling family matches the index. RQ1 is answered in that setting: 68 of 78 sources reached the Top-5, well above Urdu-only BM25 on the same pool, because the Roman path repaired a script mismatch that Method A could not (0/23). That comparison is the available evidence that a single Urdu BM25 index is insufficient for this Roman construction. A no-Roman-path ablation was not repeated on sealed K or U; those sets were not used to retune the freeze.

K keeps the known-item question and changes the sample. Roman K queries were written as ordinary Roman Urdu of the headline, not as character-table \texttt{title\_roman}. Urdu K stayed high (26/28), and both Urdu misses were still in the Top-50. Roman K did not (1/12), and ten of those eleven misses never entered the Top-50. That pattern is a matching failure, not a near-miss ranking problem. A reranker of the existing Top-50 cannot recover a source that is absent from the list. The 19.7 point drop from 87.18\% to 67.50\% is therefore largely a Roman query-form shift, plus ordinary binomial variation on $n = 40$. It is not evidence that Urdu BM25 broke. RQ2 is answered in the negative if ``transfer'' means the 87\% figure itself; the honest unseen known-item figure on this sealed K set is 27/40.

U asks a different question. There is no single right article. Factoids, explanations, named entities, underspecified strings, and chat Roman are harder than ``find this headline.'' Success@5 only requires one A or B, and still lands at 23/40. Conservative P@5 of 0.205, with 41 A labels in 200 documents, shows that the Top-5 is rarely full of complete answers; D is the most common label. Named-entity queries in this sample were weaker (5/12) than factoid or explanatory queries (each 9/14). Urdu-script needs were usually met (17/18). Roman needs often were not (6/18). RQ3 is therefore a usefulness rate of 23/40 overall, and 17/18 when the user types Urdu script, on this $n = 40$ set with official Annotator-1 labels. Those slice rates have wide intervals and are not population estimates. Independent second-annotator Success@5 is a reliability statistic (\nameref{S2_File}) and does not replace 23/40. A2 does not show that A1 is unbiased: Annotator 1 still wrote the queries.

Query mix will move any headline number. A Roman-heavy sample will look worse than an Urdu-only test even if the Urdu component is unchanged. Averaging 87.18\% with 57.50\% answers no scientific question: it mixes development with new test, known-item with graded usefulness, and \texttt{title\_roman} with chat Roman.

RQ4 is straightforward. Allowed query-side expansions did not move 68/78. A small spelling table is not a demonstrated fix for the Roman gap on K and U, and those sets were not used to invent a larger table.

The pattern is consistent with how Method D was built. Document romanization plus a 198-key reverse dictionary can match pipeline-romanized titles. It does not enumerate WhatsApp-style spelling, English loanwords that users type in Latin while the article uses Urdu, or mixed-script strings that the freeze sends to the Urdu index. Method B already showed that dictionary lookup on the query is too sparse for naive romanizations. The freeze kept the document-side index. That decision was justified for \texttt{title\_roman}. It was not a solution to open-vocabulary Roman IR.

Relative to prior Urdu resources, these numbers are not a CURE or MS MARCO leaderboard entry~\cite{bib5,bib6}. The protocol is different, the collection is news, and the Roman path is the scientific point. Relative to English routers that choose sparse versus dense retrieval~\cite{bib11}, M0 only chooses which script index to open. That is a smaller engineering rule, implemented by Unicode counts, not a learned retrieval policy.

What remains inspectable is native-script Urdu BM25 on this news collection: it recovers title-like known items and, in this U sample, usually puts something useful in the Top-5. Script-aware index selection repairs the development \texttt{title\_roman} mismatch that a single Urdu BM25 index does not (Method A 0/23). It does not repair ordinary or chat-style Roman Urdu on K and U. The study is still useful as a frozen baseline and as an evaluation protocol that keeps those facts separate. Future work may investigate first-stage Roman matching, mixed-script paths, or denser indexes; those are not claims about M0.

\subsection*{Limitations}

K and U each have $n = 40$. Roman K has $n = 12$. Mixed U has $n = 4$. The intervals in Table~\ref{table1} are wide. Point estimates should not be read as a precise ``58\% in the wild,'' and script slices are descriptive of this sample only.

Official U labels (A1) were assigned by the first author, who had also written the sealed U queries under the Phase 12 protocol. An independent second annotation (A2) was later conducted by Areena Rahman on the same 200 judgments as a reliability check (\nameref{S2_File}); five-way Cohen's $\kappa = 0.5490$ and binary $\kappa = 0.6816$. A2 was not used to replace or recompute 23/40, was not used to tune M0, and does not remove the dual-role bias risk. Preferring B over A reduces over-claiming of full answers; it does not remove subjectivity. Labels were assigned after retrieval, from headline and snippet only, and without searching for a better document.

Development Roman queries are \texttt{title\_roman}. K Roman queries are ordinary Roman titles. U Roman queries are chat-style. Those are three related but distinct input families. Success on the first does not contradict failure on the other two. Method D was selected on $n = 13$ development Roman queries.

The nine MIXED items in the $n = 78$ pool were generated with an English suffix. Phase 12 mixed queries ($n = 4$) are too few to estimate a rate. Both facts limit what can be said about mixed-script search.

The corpus is third-party Urdu news only. Cleaning was a null drop. Near-duplicate wires were not collapsed. Results should not be read as general Urdu IR, other domains, other languages, or operational search logs. M0 does not rewrite queries, does not use dates, and does not generate answers. Temporal ``today'' items were judged as archive type-of-fact.

nDCG@5 with C-gain $= 1$ can look high when Success@5 fails. H001--H040 are diagnostic only. K, U, and H001--H040 are burned if M0 is changed.

Sealed K and U do not include a repeated Urdu-only BM25 or multilingual dense, hybrid, or reranking run. Development Table~\ref{table2} already compares Urdu-only BM25 and MiniLM variants on $n = 78$. A CPU \texttt{multilingual-e5-small} index was not built. Those absences bound claims about this index-selection rule versus modern neural IR; they do not change the frozen M0 numbers.

The methodological novelty is modest: deterministic script detection plus BM25. That is a limitation of the contribution, not a defect in the freeze.

The git branch \texttt{research/post-phase12} contains later exploratory development work conducted after the frozen publication evaluation. Those experiments were not used to tune or replace the official M0, K, U, or A1 results reported in this manuscript and are not treated as official test results. They are not combined with 68/78, 27/40, or 23/40.

We do not claim 80\% unseen usefulness, 87.18\% real-world accuracy, or state-of-the-art ranking against CURE or Urdu MS MARCO.

\section*{Conclusion}

Deterministic script-aware BM25 is a simple, hashed baseline for Urdu news search: Unicode counts select a native-script index or a Method D romanized-document index. On the development/validation known-item set the frozen system recovered the source article in the Top-5 for 68 of 78 title-derived queries. On a newly sealed known-item set it did so for 27 of 40. On a separate naturalistic set, official Annotator-1 labels found at least one useful document in the Top-5 for 23 of 40 queries. Native-script title-like search on this collection often recovered the designated article. Ordinary Roman Urdu did not. The study does not solve Urdu or Roman Urdu retrieval. It provides reproducible evidence, under a freeze, of where this lexical pipeline works and where later first-stage matching work is needed.

\section*{Supporting information}

% Include only the SI item label in the paragraph heading. Use the \nameref{label} command to cite SI items in the text.
% Packaged files: Papers/PLOS_ONE/supporting_information/ (upload S1_table.csv, \ldots).
\paragraph*{S1 Table.}
\label{S1_Table}
\textbf{Per-query ExactSource ranks for K001--K040.} Query text, detector label, retrieval path, source document identifier, source rank, and Hit@5 for each sealed known-item query. File: \texttt{S1\_table.csv}.

\paragraph*{S2 Table.}
\label{S2_Table}
\textbf{Per-query official human labels for U001--U040 (Annotator 1).} Raw query text, five Top-5 labels (A--E), Success@5, rank of first A/B, conservative P@5, nDCG@5, and MRR. Official Success@5 is 23/40. File: \texttt{S2\_table.csv}.

\paragraph*{S3 Table.}
\label{S3_Table}
\textbf{Phase 5 development Roman method comparison.} Methods A--D on DEV Roman queries ($n = 13$) with Hit@5, Hit@10, nDCG@5, MRR, and mean latency, plus internal-validation confirmation of Method D ($n = 10$). File: \texttt{S3\_table.csv}.

\paragraph*{S4 Table.}
\label{S4_Table}
\textbf{Annotator 1 versus Annotator 2 per-query labels for U001--U040.} Five A1 labels, five A2 labels, Success@5 for each annotator, and document-level agreement counts. A2 Success@5 is reliability only and does not replace 23/40. File: \texttt{S4\_table.csv}.

\paragraph*{S1 File.}
\label{S1_File}
\textbf{Freeze manifest.} Corpus SHA-256, document count, BM25 parameters ($k_1 = 1.5$, $b = 0.75$), index statistics, dictionary size, and script-to-index table. Historical freeze JSON; the \texttt{test\_set} field still names H001--H040. Official unseen evaluations are K001--K040 and U001--U040. File: \texttt{S1\_file.json}.

\paragraph*{S2 File.}
\label{S2_File}
\textbf{Independent second annotation (reliability analysis).} A2 was conducted by Areena Rahman. Five-way and binary agreement, Cohen's $\kappa$ (0.5490 and 0.6816), confusion matrices, and the statement that A2 Success@5 $= 26/40$ does not replace official A1 Success@5 $= 23/40$. No article text. File: \texttt{S2\_file.md}.

\paragraph*{S3 File.}
\label{S3_File}
\textbf{Dataset provenance and reconstruction notes.} Third-party Kaggle/Mendeley source, 111,861$\to$111,860 truncated-row drop, frozen SHA-256, and instructions to verify a reconstructed corpus. Does not contain \texttt{clean\_articles.csv} or any full article collection. File: \texttt{S3\_file.md}.

\paragraph*{S1 Text.}
\label{S1_Text}
\textbf{U annotation protocol (Annotator 1).} Label definitions A--E, temporal type-of-fact rule, named-entity rule, and metric formulae for Success@5, P@5, nDCG@5, and MRR. File: \texttt{S1\_text.md}.

\section*{Acknowledgments}

We thank Adnan Aslam for supervision. This work was completed as part of an M.S.\ thesis at Air University, Islamabad.

\nolinenumbers

% Please compile your BiBTeX database using the "plos2025.bst" BibTeX style.
% This file is part of the current package.
% A sample BibTeX file is also included as "plos_bibtex_sample.bib".

\bibliography{plos_bibtex_sample}

\end{document}

```

# Appendix B — Full IEEE TeX

Source: `Papers/IEEE/FINAL/main.tex`
SHA-256: `b91daaafb7d07dfa8b72899499046c8fde7f5c8c2391c1c1c156429f674c3d18`

```latex
\documentclass[conference]{IEEEtran}
\IEEEoverridecommandlockouts
\usepackage{cite}
\usepackage{amsmath,amssymb,amsfonts}
\usepackage{graphicx}
\usepackage{textcomp}
\usepackage{booktabs}
\usepackage{array}
\usepackage{url}
\def\BibTeX{{\rm B\kern-.05em{\sc i\kern-.025em b}\kern-.08em
    T\kern-.1667em\lower.7ex\hbox{E}\kern-.125emX}}

\begin{document}

\title{Script-Aware BM25 for Urdu News Search:\\
Known-Item Recovery, Sealed Generalization, and Human Usefulness}

\author{\IEEEauthorblockN{1\textsuperscript{st} Hashim Shazad}
\IEEEauthorblockA{\textit{Dept.\ of Creative Technologies} \\
\textit{Air University}\\
Islamabad, Pakistan \\
abbasihashim30@gmail.com}
\and
\IEEEauthorblockN{2\textsuperscript{nd} Adnan Aslam}
\IEEEauthorblockA{\textit{Dept.\ of Creative Technologies} \\
\textit{Air University}\\
Islamabad, Pakistan}
}

\maketitle

\begin{abstract}
Urdu news users type both Perso-Arabic script and informal Roman Urdu. We freeze a script-aware lexical retriever (M0): Unicode routing, Urdu BM25 for URDU/MIXED/OTHER queries, and Method~D romanized-document BM25 for ROMAN queries. On a Phase~2 development/validation known-item set the frozen system achieves ExactSource Hit@5 of 87.18\% (68/78). That score is genuine for title-derived known-item search on that pool; it is not real-world accuracy and not human usefulness. Independently sealed Phase~12 tests of the same freeze yield ExactSource Hit@5 of 67.50\% (27/40) on new known-item queries and human Success@5 of 57.50\% (23/40) on naturalistic queries (P@5 $=0.2050$, nDCG@5 $=0.6460$, MRR $=0.4542$). Query-side expansions M1--M4 do not improve 68/78; M0 stays official. Urdu-script U queries succeed in 17/18 cases versus 6/18 Roman and 0/4 mixed. We do not average these metrics and do not claim 80\% unseen usefulness.
\end{abstract}

\begin{IEEEkeywords}
Urdu information retrieval, Roman Urdu, BM25, query routing, known-item search, human relevance
\end{IEEEkeywords}

\section{Introduction}

Urdu search is not English search with another font~\cite{daud2017urdu}. Users mix native script with Roman Urdu~\cite{hussain2025qlora,mehmood2020xtreme,sitaram2019codeswitch}. ULTRA~\cite{bashir2026ultra} is a dual-embedding news architecture whose original switch is a 150-character cutoff. Length does not decide which \emph{script index} to open.

We ask a smaller, measurable question. Freeze a lexical system. How often does it recover a known article on the development/validation pool? How often on a new sealed known-item sample? How often is the Top-5 useful when there is no gold article? English routing work selects sparse versus dense retrieval~\cite{arabzadeh2021predicting} or RAG depth~\cite{jeong2024adaptiverag}. Urdu collections exist~\cite{iqbal2021cure,butt2024urdumsmarco}, but they do not report this freeze protocol.

This paper is not a MiniLM dual-index study. A companion IEEE draft records a \emph{negative} dense P@5 result for SHORT/LONG SVM routing. Official retrieval numbers here are BM25 (M0) only.

\section{Related Work}

Daud et al.~\cite{daud2017urdu} map Urdu NLP obstacles. CURE~\cite{iqbal2021cure} and Urdu MS MARCO~\cite{butt2024urdumsmarco} supply evaluation resources; the latter reports MRR@10 of 0.247 for a fine-tuned configuration under a different protocol than ours. Roman Urdu work is mostly classification~\cite{hussain2025qlora,mehmood2020xtreme}. Multilingual dense retrieval can sag off the pretraining head~\cite{wu2024crosslingual,conneau2020xlmr}. BM25 remains a strong lexical baseline~\cite{robertson2009bm25}. We do not claim state of the art against MS MARCO or CURE.

\section{Problem Formulation}

Let $\mathcal{C}$ be 111{,}860 news documents. A query $q$ is URDU, ROMAN, MIXED, or OTHER by Unicode letter counts. Known-item queries carry a pre-assigned source id $s$. ExactSource Hit@5 is $1$ iff $s$ is in the Top-5. Naturalistic queries have no $s$; Success@5 is $1$ iff at least one Top-5 document is labeled A (relevant) or B (partially relevant). These indicators are not interchangeable and are not averaged.

\section{Proposed ULTRA Framework (M0)}

M0 routes URDU, MIXED, and OTHER queries to Urdu BM25 and ROMAN queries to Method~D BM25 over romanized documents (Phase~2 character table plus a 198-key reverse dictionary). Queries are not rewritten. BM25 uses $k_1=1.5$, $b=0.75$; internally Top-50, official cutoff Top-5. The detector is not an SVM. MIXED and OTHER use the Urdu index by freeze rule. Method~D was selected on development \texttt{title\_roman} strings, not on chat Roman Urdu~\cite{robertson2009bm25}. This paper is the official M0 manuscript; a separate IEEE draft reports historical MiniLM dual-index routing and is not this system.

\section{Experimental Setup}

Corpus SHA-256 \texttt{8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231}. Dictionary SHA-256 \texttt{30c3f61a64ec641abbb3acdbc7a8bcaf197f0238f1bf9e76c2c7ce8e590f86a3}. Development/validation known-item: Phase~2 \texttt{dev}+\texttt{internal\_val}, $n=78$. Phase~11 compares query-side Roman expansions M1--M4 on that pool only. Phase~12 seals K001--K040 and U001--U040 before retrieval (seed 120260827). H001--H040 have no source id; their human Success@5 $=62.5\%$ is diagnostic and is not the official unseen result.

\section{Evaluation Protocol}

Primary known-item metric: ExactSource Hit@5. Secondary K: Hit@1/10/50. Primary U metric: Success@5. Secondary U: conservative P@5 (A-count/5), nDCG@5 with gains A$=3$, B$=2$, C$=1$, D$=$E$=0$, and MRR of the first A/B. nDCG is not usefulness: C-gain can yield nDCG@5 $=1.0$ with no A/B. No test-set tuning. No second retrieval after seeing labels.

\section{Results}

\subsection{Development/validation known-item}

ExactSource Hit@5 $=68/78=87.18\%$. Urdu-only BM25 on the same pool is $0.5897$. Roman subset Method~A is $0/23$; Method~D is $22/23$. The 87.18\% figure is genuine for this protocol and is not unseen human usefulness.

\subsection{Phase~11 ablation}

All of M0--M4 score $68/78$. Roman-train Hit@5 stays $61/64=95.31\%$. M1--M4 nDCG@5 is slightly below M0. M0 remains official. M1 is a gate-pass, not an improvement.

\subsection{New known-item K001--K040}

ExactSource Hit@1 $=20/40=50.00\%$; Hit@5 $=27/40=67.50\%$; Hit@10 $=28/40=70.00\%$; Hit@50 $=30/40=75.00\%$. Detector split (descriptive): URDU $26/28$, ROMAN $1/12$.

\subsection{Naturalistic U001--U040}

Success@5 $=23/40=57.50\%$. P@5 $=0.2050$. nDCG@5 $=0.6460$. MRR $=0.4542$. Script split (descriptive): URDU $17/18=94.44\%$, ROMAN $6/18=33.33\%$, MIXED $0/4$. Mixed $n=4$ is too small for a population rate; it is reported because all four failed.

\begin{table}[t]
\caption{Official M0 metrics. Do not average rows.}
\label{tab:official}
\centering
\begin{tabular}{llcc}
\toprule
\textbf{Set} & \textbf{Type} & \textbf{Metric} & \textbf{Result} \\
\midrule
Phase 2 $n{=}78$ & Known-item (dev/val) & ExactSource Hit@5 & 68/78 \\
K001--K040 & Known-item (new) & ExactSource Hit@5 & 27/40 \\
U001--U040 & Human usefulness & Success@5 & 23/40 \\
H001--H040 & Diagnostic human & Success@5 & 25/40 \\
\bottomrule
\end{tabular}
\end{table}

\section{Error Analysis}

Urdu-script titles and U queries are usually recovered or useful on this news collection. Ordinary Roman titles (K) and chat Roman (U) are not. These results suggest a query-form mismatch between Method~D document romanization and user spelling, not a proof of a single linguistic cause. Temporal ``today'' queries were judged as archive type-of-fact, not live QA. We do not retune on U/K misses.

\section{Discussion}

87.18\% shows strong freeze-set known-item recovery. 67.50\% shows that score is not perfectly stable on new titles, especially Roman ones. 57.50\% shows a further gap to naturalistic usefulness. Query mix matters: a Roman-heavy sample will look worse than an Urdu-only test even if the Urdu component is strong. Known-item evaluation alone cannot support a usefulness claim. We do not claim SOTA.

\section{Limitations}

$n=40$ for K and U; one annotator; news domain only; no IAA; Roman spelling is open-ended; mixed $n=4$; nDCG inflated by C; H001--H040 are not official unseen ExactSource (undefined) or official unseen Success@5; K/U are burned if M0 changes. We do not claim 80\% or 87.18\% unseen usefulness.

\section{Conclusion}

M0 is a frozen script-aware BM25 news retriever with 87.18\% ExactSource Hit@5 on the development/validation known-item protocol, 67.50\% ExactSource Hit@5 on new known-item queries, and 57.50\% human Success@5 on naturalistic queries. The contribution is that measured framework and its Roman/mixed limitation---not 87\% real-world accuracy.

\section*{Acknowledgment}

MS thesis work at Air University, Islamabad, under Dr.\ Adnan Aslam. Not an IEEE Xplore publication.

\begin{thebibliography}{00}
\bibitem{daud2017urdu} A.\ Daud, W.\ Khan, and D.\ Che, ``Urdu language processing: a survey,'' \emph{Artif.\ Intell.\ Rev.}, vol.\ 47, pp.\ 279--311, 2017.
\bibitem{hussain2025qlora} N.\ Hussain \emph{et al.}, ``Fine-tuning large language models with QLoRA for offensive language detection in Roman Urdu-English code-mixed text,'' arXiv:2510.03683, 2025.
\bibitem{sitaram2019codeswitch} S.\ Sitaram, K.\ R.\ Chandu, S.\ K.\ Rallabandi, and A.\ W.\ Black, ``A survey of code-switched speech and language processing,'' arXiv:1904.00784, 2019.
\bibitem{mehmood2020xtreme} F.\ Mehmood \emph{et al.}, ``A precisely Xtreme-multi channel hybrid approach for Roman Urdu sentiment analysis,'' arXiv:2003.05443, 2020.
\bibitem{bashir2026ultra} A.\ Bashir, F.\ Qaiser, and I.\ Hussain, ``ULTRA: Urdu language transformer-based recommendation architecture,'' arXiv:2602.11836, 2026.
\bibitem{arabzadeh2021predicting} N.\ Arabzadeh, X.\ Yan, and C.\ L.\ A.\ Clarke, ``Predicting efficiency/effectiveness trade-offs for dense vs.\ sparse retrieval strategy selection,'' in \emph{Proc.\ CIKM}, 2021, pp.\ 2862--2866.
\bibitem{jeong2024adaptiverag} S.\ Jeong \emph{et al.}, ``Adaptive-RAG: learning to adapt retrieval-augmented large language models through question complexity,'' in \emph{Proc.\ NAACL}, 2024, pp.\ 7036--7050.
\bibitem{iqbal2021cure} M.\ Iqbal, B.\ Tahir, and M.\ A.\ Mehmood, ``CURE: collection for Urdu information retrieval evaluation and ranking,'' arXiv:2011.00565, 2021.
\bibitem{butt2024urdumsmarco} U.\ Butt, S.\ Varanasi, and G.\ Neumann, ``Enabling low-resource language retrieval: establishing baselines for Urdu MS MARCO,'' arXiv:2412.12997, 2024.
\bibitem{wu2024crosslingual} J.\ Wu, Z.\ Ren, and S.\ Verberne, ``What are the limits of cross-lingual dense passage retrieval for low-resource languages?'' arXiv:2408.11942, 2024.
\bibitem{conneau2020xlmr} A.\ Conneau \emph{et al.}, ``Unsupervised cross-lingual representation learning at scale,'' in \emph{Proc.\ ACL}, 2020, pp.\ 8440--8451.
\bibitem{robertson2009bm25} S.\ Robertson and H.\ Zaragoza, ``The probabilistic relevance framework: BM25 and beyond,'' \emph{Found.\ Trends Inf.\ Retr.}, vol.\ 3, no.\ 4, pp.\ 333--389, 2009.
\end{thebibliography}

\end{document}

```

# Pack metadata

| Item | Value |
|---|---|
| This file | `PAPER_CONTEXT_PACK.md` (repo root) |
| Builder | Disposable `_build_paper_context_pack.py` removed after write; not part of the scientific record |
| Inventory policy | TEST query CSVs and `seal.json` body **not read**; directory listing names only |

# End of PAPER_CONTEXT_PACK
