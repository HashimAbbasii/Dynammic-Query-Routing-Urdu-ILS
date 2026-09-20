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
