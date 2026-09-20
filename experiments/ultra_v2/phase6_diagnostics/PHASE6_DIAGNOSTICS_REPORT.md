# PHASE6-DIAGNOSTICS — read-only analysis

**Status:** complete  
**Directory:** `experiments/ultra_v2/phase6_diagnostics/`  
**Timestamp (UTC):** 2026-09-13T06:48:36Z  
**Population:** Roman KN TRAIN+DEV n=51  
**TEST:** not accessed  
**Retrieval rerun:** none

Frozen Phase 2/3/4/5/7 scripts, configs, and CSVs were read-only inputs. McNemar logic is `exact_mcnemar` copied verbatim from `experiments/ultra_v2/phase2_roman/run_r2_1_experiment.py`. `detect_script` is copied verbatim from `experiments/phase5_roman_urdu/run_phase5.py` (not imported, to avoid M0 import side effects).

---

## Task 1 — Statistical significance (exact McNemar)

n=51 is small. A non-significant p-value is **underpowered to detect a difference**, not proof that the methods are equal.

Paired binary Hit/Miss outcomes. Control miss / treatment hit = n01; control hit / treatment miss = n10. Test statistic = number of discordant pairs; p-value = two-sided exact binomial McNemar from the frozen function.

### BM25 vs Dense

**hit@5**

| Item | Value |
| --- | --- |
| Control → treatment | BM25 → Dense |
| Hit–hit / miss–miss | 0 / 32 |
| Treatment unique hits (c / n01) | 15 |
| Control unique hits (b / n10) | 4 |
| Discordant pairs (test statistic n_b+c) | 19 |
| p two-sided (exact McNemar) | 0.019211 |
| Significant at p<0.05 | YES |

Dense has more unique hits than BM25 (15 vs 4 discordant). The difference IS statistically significant at p<0.05.

Treatment-only hits: KN011, KN013, KN016, KN017, KN019, KN029, KN031, KN033, KN034, KN039, KN046, KN048, KN049, KN052, KN053

Control-only hits: KN004, KN012, KN023, KN038

**hit@50**

| Item | Value |
| --- | --- |
| Control → treatment | BM25 → Dense |
| Hit–hit / miss–miss | 2 / 25 |
| Treatment unique hits (c / n01) | 20 |
| Control unique hits (b / n10) | 4 |
| Discordant pairs (test statistic n_b+c) | 24 |
| p two-sided (exact McNemar) | 0.001544 |
| Significant at p<0.05 | YES |

Dense has more unique hits than BM25 (20 vs 4 discordant). The difference IS statistically significant at p<0.05.

Treatment-only hits: KN001, KN011, KN013, KN015, KN016, KN017, KN019, KN029, KN030, KN031, KN033, KN034, KN039, KN040, KN043, KN045, KN046, KN049, KN052, KN053

Control-only hits: KN004, KN012, KN023, KN038

### Dense vs Hybrid

**hit@5**

| Item | Value |
| --- | --- |
| Control → treatment | Dense → Hybrid |
| Hit–hit / miss–miss | 8 / 33 |
| Treatment unique hits (c / n01) | 3 |
| Control unique hits (b / n10) | 7 |
| Discordant pairs (test statistic n_b+c) | 10 |
| p two-sided (exact McNemar) | 0.34375 |
| Significant at p<0.05 | NO |

Dense has more unique hits than Hybrid (7 vs 3 discordant). The difference is NOT statistically significant at p<0.05. n=51 is small, so treat this as underpowered to detect a difference, not as proof of no difference.

Treatment-only hits: KN004, KN014, KN023

Control-only hits: KN013, KN019, KN031, KN033, KN039, KN052, KN053

**hit@50**

| Item | Value |
| --- | --- |
| Control → treatment | Dense → Hybrid |
| Hit–hit / miss–miss | 21 / 25 |
| Treatment unique hits (c / n01) | 4 |
| Control unique hits (b / n10) | 1 |
| Discordant pairs (test statistic n_b+c) | 5 |
| p two-sided (exact McNemar) | 0.375 |
| Significant at p<0.05 | NO |

Hybrid has more unique hits than Dense (4 vs 1 discordant). The difference is NOT statistically significant at p<0.05. n=51 is small, so treat this as underpowered to detect a difference, not as proof of no difference.

Treatment-only hits: KN004, KN012, KN023, KN038

Control-only hits: KN040

### BM25 vs Hybrid

**hit@5**

| Item | Value |
| --- | --- |
| Control → treatment | BM25 → Hybrid |
| Hit–hit / miss–miss | 2 / 38 |
| Treatment unique hits (c / n01) | 9 |
| Control unique hits (b / n10) | 2 |
| Discordant pairs (test statistic n_b+c) | 11 |
| p two-sided (exact McNemar) | 0.06543 |
| Significant at p<0.05 | NO |

Hybrid has more unique hits than BM25 (9 vs 2 discordant). The difference is NOT statistically significant at p<0.05. n=51 is small, so treat this as underpowered to detect a difference, not as proof of no difference.

Treatment-only hits: KN011, KN014, KN016, KN017, KN029, KN034, KN046, KN048, KN049

Control-only hits: KN012, KN038

**hit@50**

| Item | Value |
| --- | --- |
| Control → treatment | BM25 → Hybrid |
| Hit–hit / miss–miss | 6 / 26 |
| Treatment unique hits (c / n01) | 19 |
| Control unique hits (b / n10) | 0 |
| Discordant pairs (test statistic n_b+c) | 19 |
| p two-sided (exact McNemar) | 4e-06 |
| Significant at p<0.05 | YES |

Hybrid has more unique hits than BM25 (19 vs 0 discordant). The difference IS statistically significant at p<0.05.

Treatment-only hits: KN001, KN011, KN013, KN015, KN016, KN017, KN019, KN029, KN030, KN031, KN033, KN034, KN039, KN043, KN045, KN046, KN049, KN052, KN053

### Hybrid vs NG3 (NG3 alone)

NG3 is a weak first-stage retriever. This pair is reported because it was requested; it is **not** a fair system-vs-system ranking contest.

**hit@5**

| Item | Value |
| --- | --- |
| Control → treatment | Hybrid → NG3 |
| Hit–hit / miss–miss | 3 / 37 |
| Treatment unique hits (c / n01) | 3 |
| Control unique hits (b / n10) | 8 |
| Discordant pairs (test statistic n_b+c) | 11 |
| p two-sided (exact McNemar) | 0.226562 |
| Significant at p<0.05 | NO |

Hybrid has more unique hits than NG3 (8 vs 3 discordant). The difference is NOT statistically significant at p<0.05. n=51 is small, so treat this as underpowered to detect a difference, not as proof of no difference.

Treatment-only hits: KN035, KN038, KN050

Control-only hits: KN011, KN014, KN016, KN029, KN034, KN046, KN048, KN049

**hit@50**

| Item | Value |
| --- | --- |
| Control → treatment | Hybrid → NG3 |
| Hit–hit / miss–miss | 6 / 24 |
| Treatment unique hits (c / n01) | 2 |
| Control unique hits (b / n10) | 19 |
| Discordant pairs (test statistic n_b+c) | 21 |
| p two-sided (exact McNemar) | 0.000221 |
| Significant at p<0.05 | YES |

Hybrid has more unique hits than NG3 (19 vs 2 discordant). The difference IS statistically significant at p<0.05.

Treatment-only hits: KN035, KN050

Control-only hits: KN001, KN011, KN012, KN013, KN014, KN015, KN016, KN019, KN029, KN030, KN031, KN033, KN034, KN043, KN045, KN046, KN049, KN052, KN053

### Hybrid vs BM25 ∪ Dense ∪ NG3 (Top-k union)

Union Hit@k = gold in at least one of Method-D BM25, dense, or NG3 at cutoff k. Hybrid is RRF of BM25∪Dense only, so NG3-only golds can appear in the union but not in hybrid. This is a **candidate-pool** comparison, not a fused ranker.

**hit@5**

| Item | Value |
| --- | --- |
| Control → treatment | Hybrid → BM25∪Dense∪NG3 |
| Hit–hit / miss–miss | 10 / 29 |
| Treatment unique hits (c / n01) | 11 |
| Control unique hits (b / n10) | 1 |
| Discordant pairs (test statistic n_b+c) | 12 |
| p two-sided (exact McNemar) | 0.006348 |
| Significant at p<0.05 | YES |

BM25∪Dense∪NG3 has more unique hits than Hybrid (11 vs 1 discordant). The difference IS statistically significant at p<0.05.

Treatment-only hits: KN012, KN013, KN019, KN031, KN033, KN035, KN038, KN039, KN050, KN052, KN053

Control-only hits: KN014

**hit@50**

| Item | Value |
| --- | --- |
| Control → treatment | Hybrid → BM25∪Dense∪NG3 |
| Hit–hit / miss–miss | 25 / 23 |
| Treatment unique hits (c / n01) | 3 |
| Control unique hits (b / n10) | 0 |
| Discordant pairs (test statistic n_b+c) | 3 |
| p two-sided (exact McNemar) | 0.25 |
| Significant at p<0.05 | NO |

BM25∪Dense∪NG3 has more unique hits than Hybrid (3 vs 0 discordant). The difference is NOT statistically significant at p<0.05. n=51 is small, so treat this as underpowered to detect a difference, not as proof of no difference.

Treatment-only hits: KN035, KN040, KN050

---

## Task 2 — Candidate Recall@50 vs RANK split

Re-tabulated from the frozen per-query CSVs. No retrieval.

| Method | Hit@50 | Of Hit@50, also Hit@5 | MISS (gold outside Top-50) | RANK (in Top-50, outside Top-5) |
| --- | ---: | ---: | ---: | ---: |
| BM25 | 6/51 = 11.76% | 4/6 | 45/51 = 88.24% | 2/51 = 3.92% |
| Dense | 22/51 = 43.14% | 15/22 | 29/51 = 56.86% | 7/51 = 13.73% |
| Hybrid | 25/51 = 49.02% | 11/25 | 26/51 = 50.98% | 14/51 = 27.45% |
| NG3 | 8/51 = 15.69% | 6/8 | 43/51 = 84.31% | 2/51 = 3.92% |
| Phase7 | 1/51 = 1.96% | 0/1 | 50/51 = 98.04% | 1/51 = 1.96% |

Hit@5 implies Hit@50, so “of Hit@50, also Hit@5” equals the Hit@5 count.

MISS is a candidate-generation failure (gold never entered the Top-50 pool). RANK is a ranking failure (gold was in the pool but not in Top-5).

---

## Task 3 — Script routing check

Frozen Unicode detector (`detect_script`): URDU / ROMAN / MIXED / OTHER.

M0 routing (context only, not re-run): URDU/MIXED → Urdu BM25; ROMAN → Method D.

| Check | Result |
| --- | --- |
| n=51 labeled ROMAN by detector | **51 / 51** |
| Detector mismatches vs ROMAN KN population | **0** |
| Quad-23 dual-miss misroutes | **0 / 23** |
| Overall | **PASS** |

All 51 queries, including all 23 four-way misses (KN002, KN005, KN006, KN008, KN010, KN018, KN020, KN021, KN022, KN024, KN025, KN026, KN027, KN028, KN032, KN036, KN037, KN041, KN042, KN044, KN047, KN051, KN054), are detector-ROMAN. Those 23 failures are **retrieval** failures, not script-routing errors.

Per-query flags: `artifacts/routing_check.csv`.

---

## Task 4 — Document length distribution

Corpus: `data/clean_articles.csv`, SHA-256 `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231`, n=111860, column `combined_text`.  
`experiments/phase4_chunk_ann/corpus_token_lengths.npy` was **not** used.

**Character length**

| Percentile | Value |
| --- | ---: |
| p10 | 532.0 |
| p25 | 711.0 |
| p50 | 1034.0 |
| p75 | 1581.0 |
| p90 | 2386.0 |
| p95 | 3036.0 |
| p99 | 5276.4 |
| mean | 1320.0307 |
| min / max | 171 / 36265 |

**Whitespace-token count**

| Percentile | Value |
| --- | ---: |
| p10 | 109.0 |
| p25 | 147.0 |
| p50 | 216.0 |
| p75 | 334.0 |
| p90 | 506.0 |
| p95 | 643.0 |
| p99 | 1130.0 |
| mean | 277.7510 |
| min / max | 24 / 7766 |

Documents with **>512 whitespace tokens:** **10768 / 111860 = 9.6263%**.

Phase 3 did **not** chunk or average those documents. It truncated each document at encoder `max_seq_length=512` (subword tokens, not whitespace tokens). The count above is a whitespace proxy for articles long enough that tail truncation is likely.

---

## Safety

| Check | Value |
| --- | --- |
| TEST accessed | NO |
| Frozen Phase 2/3/4/5/7 modified | NO |
| New retrieval / candidate generation | NO |
| Commit / push | NO |
