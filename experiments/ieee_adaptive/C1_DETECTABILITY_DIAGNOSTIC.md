# C1 Detectability Diagnostic

**Status:** complete — scientific feasibility gate (not a method claim)  
**Branch:** `research/roman-urdu-adaptive-retrieval`  
**HEAD:** `3b2e829bf9769d16f9b604ee68d7cc50ce128fa7`  
**Date (local):** 2026-09-22  
**Decision:** **NO-GO**

---

## 1. Research Question

Can **query-only / pre-retrieval** surface characteristics of a Roman Urdu query predict which frozen retrieval expert — **BM25 (Method D)**, **NG3**, or **Dense** — is most likely to succeed at ExactSource Hit@5 for Urdu-script news retrieval?

## 2. Hypothesis

**H1:** Query-only linguistic/surface characteristics of Roman Urdu queries contain enough information to predict which retrieval expert is more likely to succeed.

H1 is allowed to fail. This diagnostic does not implement an adaptive system.

## 3. Data Used

| Item | Value |
| --- | --- |
| Population | Roman KN ExactSource TRAIN+DEV (Phase 13 freeze) |
| n | **80** (original W1 cohort 51 + Phase 13 LLM1/human-reviewed 29) |
| Source artifact | `experiments/ultra_v2/phase13_population/artifacts/scoring/PHASE13_SCORING_PER_QUERY.csv` |
| SHA-256 | `f59c37102ba5c212e7b2c14600cf3781732eef98757379f51c26f0a250fe5d66` |
| Frozen status | Program B Phase 13/14 scoring — **read-only** |
| Experts used | Frozen `bm25_hit@5`, `ng3_hit@5`, `dense_hit@5` columns (no retrieval rerun) |
| Query text | TRAIN/DEV query strings from the same Phase 13 CSV (allowed for query-only features) |
| Roman Urdu vocab resource | `models/roman_urdu_dict_expanded.json` (198 keys; Program A frozen dict) |
| Dict SHA-256 | `30c3f61a64ec641abbb3acdbc7a8bcaf197f0238f1bf9e76c2c7ce8e590f86a3` |

No new retrieval. No parameter changes. No TEST rows.

## 4. TEST Isolation

```text
TEST_CONTENT_ACCESSED = FALSE
```

Only structural TEST metadata was previously known from C0 (seal README / `seal.json`). C1 scripts load **only** Phase 13 TRAIN+DEV scoring CSV and the frozen dictionary. Paths containing `benchmark/test` are refused.

## 5. Frozen Expert Definitions

| Expert | Meaning in Program B | Hit@5 source column |
| --- | --- | --- |
| BM25 | Method-D BM25 over romanized documents | `bm25_hit@5` |
| NG3 | Character 3-gram BM25 on Method-D tokens | `ng3_hit@5` |
| Dense | Multilingual e5-small dense first-stage | `dense_hit@5` |

Hybrid/RRF is **not** a selectable expert in C1 (routing among the three complementary first-stages that define the oracle best-of-3). Hybrid remains a fixed baseline for context only via Phase 14 numbers (not used as a C1 label class).

## 6. Expert Complementarity

Hit@5 patterns on n=80 as `(BM25, NG3, Dense)`:

| Pattern | Count | Interpretation |
| --- | ---: | --- |
| `(0,0,0)` | 52 | All three fail |
| `(0,0,1)` | 17 | Dense only |
| `(0,1,0)` | 4 | NG3 only |
| `(1,1,0)` | 3 | BM25+NG3 tie (Dense miss) |
| `(0,1,1)` | 2 | NG3+Dense tie |
| `(1,0,0)` | 1 | BM25 only |
| `(1,1,1)` | 1 | All three succeed |

### Unique wins / ties / all-fail

| Bucket | n |
| --- | ---: |
| UNIQUE Dense | 17 |
| UNIQUE NG3 | 4 |
| UNIQUE BM25 | 1 |
| TIE BM25+NG3 | 3 |
| TIE NG3+Dense | 2 |
| TIE BM25+NG3+Dense | 1 |
| ALL_FAIL | 52 |
| **Unique-best total** | **22** |
| **At least one success** | **28** |

### Pairwise Hit@5 overlap / discordance (n=80)

| Pair | Both hit | A-only | B-only |
| --- | ---: | ---: | ---: |
| BM25 vs NG3 | 4 | 1 | 6 |
| BM25 vs Dense | 1 | 4 | 19 |
| NG3 vs Dense | 3 | 7 | 17 |

**Interpretation:** Experts remain complementary (Program B). Most of that complementarity is **Dense-dominated** among unique winners. **52/80** queries are unrecoverable by any of the three experts at Hit@5.

## 7. Target Definition

### Policies declared *before* fitting

**Primary analysis (main detectability metric):**  
Keep only queries with a **unique** Hit@5 winner among {BM25, NG3, Dense} → **n=22**.  
Label = that unique expert.

**Secondary sensitivity:**  
All queries with ≥1 Hit@5 success → **n=28**.  
Ties broken by fixed priority **Dense > NG3 > BM25**, declared a priori from frozen Program B aggregate Hit@5 strength on n=80 (Dense 20 > NG3 10 > BM25 5; Phase 14 SoT). Not tuned in C1.

**Not done:** Choosing a tie rule after seeing which maximizes predictor accuracy.

Primary label counts: Dense **17**, NG3 **4**, BM25 **1**.  
Secondary label counts (after tie-break): Dense **20**, NG3 **7**, BM25 **1**.

## 8. Query-Only Features

Transparent deterministic features (full set written to `C1_QUERY_FEATURES.csv`; **no** gold IDs, ranks, scores, or hit flags in that file).

| Feature | Group | Definition |
| --- | --- | --- |
| `char_len` | length | Character length of query |
| `token_count` | length | Count of alphanumeric tokens |
| `mean_tok_len` | length | Mean token length |
| `median_tok_len` | length | Median token length |
| `max_tok_len` | length | Max token length |
| `tok_len_var` | length / ortho | Population variance of token lengths |
| `repeated_char_count` | orthographic | Consecutive repeated letters within tokens |
| `repeated_char_ratio` | orthographic | `repeated_char_count / sum(token lengths)` |
| `vowel_ratio` | orthographic | `aeiou` / letters |
| `consonant_ratio` | orthographic | non-vowel letters / letters |
| `digit_ratio` | script | Digit chars / chars |
| `punct_ratio` | script | Non-alnum non-space / chars |
| `uppercase_ratio` | script | Uppercase / chars |
| `has_digit` | script | Binary any digit |
| `has_alnum_mix` | script | Token with both letters and digits |
| `ru_dict_hit_ratio` | code-mix | Fraction of tokens in frozen RU dict keys |
| `unknown_token_ratio` | code-mix | `1 - ru_dict_hit_ratio` |
| `english_stop_ratio` | code-mix | Fraction in fixed English closed-class list (script-embedded; not query-derived) |
| `code_mix_indicator` | code-mix | Both RU-dict and English-stop hits > 0 |
| `unique_token_ratio` | lexical | Unique tokens / tokens |
| `short_token_ratio` | lexical | Tokens with len ≤ 3 |
| `long_token_ratio` | lexical | Tokens with len ≥ 8 |
| `acronym_like_count` | entity-like | Short α tokens (len 2–4) that are ALLCAPS or consonant-heavy |
| `digit_token_count` | entity-like | Tokens containing a digit |

**Provenance of RU dict:** Program A frozen `models/roman_urdu_dict_expanded.json`, available long before C1; hash above matches repository freeze documentation.

## 9. Leakage Audit

| Predictor receives | Predictor does **not** receive |
| --- | --- |
| Raw TRAIN/DEV query text | Gold `source_doc_id` |
| Deterministic surface features (§8) | Article text / titles |
| Frozen RU dictionary membership | Hit@5 / MRR / ranks / scores |
| Fixed English stop list | Retrieved docs / similarities |
| | Oracle / complementarity labels as features |
| | Hybrid/RRF scores |
| | TEST anything |

**Label construction** uses frozen Hit@5 retrospectively (required for supervised evaluation). Features never include those outcomes.

**Fairness form used:** `query → features → predicted expert → frozen expert Hit@5`  
**Not used:** retrieve-all-then-choose.

## 10. Evaluation Protocol

| Choice | Specification |
| --- | --- |
| Models (pre-declared) | (1) train-fold majority baseline; (2) multinomial logistic regression with `StandardScaler` + `class_weight='balanced'`; (3) `DecisionTreeClassifier(max_depth=3, class_weight='balanced')` |
| CV | **Leave-one-out** on primary (n=22) and secondary (n=28) — stratified K-fold infeasible (BM25 unique wins = 1) |
| Scaling / coefficients | Fit **inside each LOO training fold** |
| Seed | `42` (sklearn RNG where applicable) |
| No hyperparameter search | Fixed solver `lbfgs`, `max_iter=2000`, tree depth 3 |
| Software | Python 3.13.9 (Anaconda); scikit-learn 1.7.2; numpy 2.3.5 |

## 11. Baselines

### Primary unique-winner set (n=22)

| Method | Accuracy | Wilson 95% CI | Macro-F1 | Balanced acc | Correct |
| --- | ---: | --- | ---: | ---: | ---: |
| Majority (always Dense) | **0.773** | [0.566, 0.899] | 0.291 | 0.333 | 17/22 |
| Fixed always-BM25* | 0.045 | — | — | — | 1/22 |
| Fixed always-NG3* | 0.182 | — | — | — | 4/22 |
| Fixed always-Dense* | **0.773** | same as majority | 0.291 | 0.333 | 17/22 |

\*Fixed-expert accuracy on the unique-winner subset equals recall of that class.

### Secondary tie-broken set (n=28)

| Method | Accuracy | Wilson 95% CI | Macro-F1 | Balanced acc | Correct |
| --- | ---: | --- | ---: | ---: | ---: |
| Majority (Dense) | **0.714** | [0.529, 0.847] | 0.278 | 0.333 | 20/28 |

## 12. Query-Only Prediction Results

### Primary (unique best, n=22, LOO)

| Model | Accuracy | Wilson 95% CI | Macro-F1 | Balanced acc | Correct |
| --- | ---: | --- | ---: | ---: | ---: |
| Majority | **0.773** | [0.566, 0.899] | 0.291 | 0.333 | 17/22 |
| LogReg (query-only) | **0.636** | [0.430, 0.803] | 0.383 | 0.402 | 14/22 |
| Tree depth≤3 | **0.636** | [0.430, 0.803] | 0.337 | 0.338 | 14/22 |

**Confusion matrix — LogReg primary** (rows = true, cols = pred; order BM25, NG3, Dense):

```text
[[ 0  0  1]    # true BM25 → all predicted Dense
 [ 0  2  2]    # true NG3  → 2 correct, 2→Dense
 [ 1  4 12]]   # true Dense → 12 correct; 5 misrouted to BM25/NG3
```

**Per-expert (LogReg primary, from classification report):**

| Expert | Precision | Recall | F1 | Support |
| --- | ---: | ---: | ---: | ---: |
| BM25 | 0.000 | 0.000 | 0.000 | 1 |
| NG3 | 0.333 | 0.500 | 0.400 | 4 |
| Dense | 0.800 | 0.706 | 0.750 | 17 |

### Secondary (n=28, LOO)

| Model | Accuracy | Macro-F1 | Balanced acc | Correct |
| --- | ---: | ---: | ---: | ---: |
| Majority | **0.714** | 0.278 | 0.333 | 20/28 |
| LogReg | **0.607** | 0.373 | 0.376 | 17/28 |
| Tree | **0.679** | 0.441 | 0.440 | 19/28 |

**Signal assessment:** Accuracy is **below** majority on both primary and secondary. Macro-F1 / balanced accuracy rise slightly because `class_weight='balanced'` occasionally guesses NG3, but this **trades away Dense hits**. That is not a usable selection signal.

## 13. Offline Routing Simulation

On full **n=80**, select an expert then take that expert’s **frozen** Hit@5:

| Policy | Hit@5 |
| --- | ---: |
| Fixed BM25 | 5/80 = 0.0625 |
| Fixed NG3 | 10/80 = 0.1250 |
| Fixed Dense | **20/80 = 0.2500** |
| Majority routing (= always Dense) | **20/80 = 0.2500** |
| Query-only LogReg routing | **17/80 = 0.2125** |
| Oracle upper bound (≥1 expert hits; tie-break priority) | **28/80 = 0.3500** |

Routing used LOO predictions on the 22 unique-winner queries and a model fit on all unique-winners for the remaining 58 queries (ALL_FAIL + ties). Even with that setup, query-only routing is **worse than always choosing Dense**.

Oracle is an upper bound only — **not achievable** by this predictor.

## 14. Feature-Group Analysis

Pre-declared ablation on primary unique-winners (LogReg LOO):

| Feature group | Accuracy | Macro-F1 | Balanced acc |
| --- | ---: | ---: | ---: |
| Length-only | 0.636 | 0.391 | 0.402 |
| Orthographic-only | 0.682 | 0.429 | 0.422 |
| Script/code-mix-only | 0.455 | 0.357 | 0.451 |
| Lexical-surface-only | 0.455 | 0.302 | 0.324 |
| Combined (all) | 0.636 | 0.383 | 0.402 |

No group beats majority accuracy (0.773). Orthographic-only is the least bad on accuracy among subsets, still below majority. Script/code-mix features (the most “Roman Urdu–specific” group) are among the **weakest** on accuracy.

Full-fit coefficients (interpretability only; not CV-safe claims) associate Dense with longer queries / digits / punctuation and NG3 with higher token-length variance / short-token ratio — unstable anecdotes on n=22, not evidence of a robust Roman Urdu detector.

## 15. Failure Analysis

Why query-only prediction fails here:

1. **Extreme class imbalance / tiny unique-winner n** — 17/22 Dense; BM25 unique wins = 1; LOO cannot learn a stable BM25 rule.  
2. **Most mass is ALL_FAIL (52/80)** — no expert choice helps; routing among current experts cannot create signal.  
3. **Overlapping strengths** — when BM25 or NG3 succeed, they often co-succeed with each other (ties) or the query surface does not uniquely mark the winner.  
4. **Semantic / paraphrase failures** — VOCAB-style misses are not readable from length/orthography alone.  
5. **Entity ambiguity** — entity-like surface counts do not map cleanly to Dense vs NG3 unique wins.  
6. **Spelling variation** — NG3’s niche recoveries (e.g. unique NG3 IDs KN035, KN050, KN099, KN114) are not reliably separated by the declared feature groups under LOO.  
7. **Balanced training ≠ retrieval utility** — raising minority recall by sacrificing Dense majority harm Hit@5 routing.

## 16. Decision

# **NO-GO**

## 17. Scientific Interpretation

### What C1 establishes

- On the frozen n=80 Roman KN population, **query-only features do not provide a scientifically defensible expert-selection signal** above always choosing Dense.  
- Oracle complementarity (28/80) remains real; **predictable** complementarity from the query alone is **not** supported by this diagnostic.  
- Apparent small gains in macro-F1 / balanced accuracy do **not** translate into better offline Hit@5 routing (17 < 20).

### What C1 does **not** establish

- That no future feature set could ever work (only that this pre-declared transparent set failed).  
- That post-retrieval QPP / score-agreement routing is impossible (explicitly out of scope; would be a different hypothesis).  
- Novelty or venue fitness of any adaptive method.

### Limitations

- n=22 primary labels; BM25 support 1.  
- Hit@5 binary ties force exclusion or a priority rule.  
- English-stop list is a coarse Latin-script proxy, not a gold language ID.  
- Single population (ULTRA Roman KN); no external RU IR set used.

### Before any adaptive system implementation

Given **NO-GO**, **do not** proceed to C2 router implementation under the current H1 (query-only expert selection among BM25/NG3/Dense).

If research continues at all on related themes, it would require a **different question** (examples for discussion only — not authorized work): larger labeled unique-winner sets; post-retrieval QPP; expanding the expert set / representation that recovers ALL_FAIL queries; or abandoning per-query expert routing in favor of fixed Dense/Hybrid. Those are **not** C1 follow-ons without a new gate.

## 18. Reproducibility

| Item | Value |
| --- | --- |
| Branch | `research/roman-urdu-adaptive-retrieval` |
| HEAD | `3b2e829bf9769d16f9b604ee68d7cc50ce128fa7` |
| Script | `experiments/ieee_adaptive/run_c1_detectability.py` |
| Features CSV | `experiments/ieee_adaptive/C1_QUERY_FEATURES.csv` |
| Machine summary | `experiments/ieee_adaptive/C1_RESULTS_SUMMARY.json` |
| This report | `experiments/ieee_adaptive/C1_DETECTABILITY_DIAGNOSTIC.md` |
| Files modified | **None** (Program A/B untouched) |
| Random seed | 42 |
| Environment | Python 3.13.9; scikit-learn 1.7.2 |
| Phase 13 CSV SHA-256 | `f59c37102ba5c212e7b2c14600cf3781732eef98757379f51c26f0a250fe5d66` |
| RU dict SHA-256 | `30c3f61a64ec641abbb3acdbc7a8bcaf197f0238f1bf9e76c2c7ce8e590f86a3` |

Reproduce:

```text
python experiments/ieee_adaptive/run_c1_detectability.py
```

---

**End of C1.** Hypothesis H1 is **not supported** on this evidence.
