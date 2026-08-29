# Phase 2 — Retrieval-based oracle labels (new train/dev pool)

## Why this phase exists

Phase 1 showed the SVM beats the protocol gold labels (24/40 vs word count 8/40) but **loses dual-index P@5** (33.0% vs 36.5%). Protocol gold disagreed with the retrieval-optimal index on **20/40** frozen queries.

So the next scientific step is **not** a new classifier. It is a new **routing objective** on a **new query pool**:

> Which index actually ranks the right article higher?

The frozen test **H001–H040** was never used for labels, splits, or thresholds.

## What Phase 1 found (frozen, do not mix)

- Word-count P@5 36.5%, always-headline 35.0%, SVM 33.0%
- Oracle ceiling on those 40 human judgments: 40.8%
- Example H002: protocol/SVM LONG, headline P@5 0.80, full 0.00

## How the new pool was built

- **260** queries derived from unused corpus articles (`data/clean_articles.csv`).
- One source article per query (known-item setup).
- Templates: short title, romanized title, why/how/effects, lead excerpt, mixed Urdu+English.
- Blocked against: H001–H040, T001–T040, Phase 3 eval, Phase 2.5 pilot, and the 409 training strings.
- Exact normalized match and Jaccard ≥ 0.75 vs frozen test are hard failures.

## How labels were generated

This is **known-item** supervision, **not** a new human P@5 pass.

1. Retrieve top-20 from the **headline** index and the **full-article** index with the same encoder (`paraphrase-multilingual-MiniLM-L12-v2`).
2. The only relevant document is the source article the query was written from.
3. Primary metric: **nDCG@5**. Also store P@5, hit@5, rank, margin.
4. Pre-registered rule (not tuned on H001–H040):
   - `MIXED` if both nDCG@5 are 0, or `|nDCG_h - nDCG_f| < 0.05`
   - else `HEADLINE` or `FULL` by higher nDCG@5

Protocol labels on this pool are **template tags** (SHORT for title-like, LONG for why/how/lead). They are not a second human rater.

## Split

| Split | n | Role |
| --- | ---: | --- |
| train | 182 | future router fitting only |
| dev | 39 | thresholds / features later |
| internal_val | 39 | extra holdout inside the new pool |
| frozen test | 40 (H001–H040) | **untouched** |

Seed 42. Stratified by oracle route.

## Leakage

See `leakage_check.json`. SVM pickle was not rewritten. Held-out 400 judgments were not used as training labels. MIXED delta was pre-registered at 0.05.

## Limitations (read these)

1. Known-item ≠ graded news relevance. A document that is on-topic but not the source article scores 0.
2. Known-item P@5 is only 0 or 0.2.
3. Naive character romanization is noisy; most roman queries miss the source article in **both** indexes and become MIXED.
4. Queries come from titles/leads, not search logs.

## Do not do next (until you review this report)

- Retrain the SVM
- Tune on H001–H040
- Add RRF / extra classifiers
