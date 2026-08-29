# Phase 12 human relevance — U001–U040

Frozen-M0 Top-5 only. **Not** ExactSource Hit@5. **Not** a K evaluation. **Not** a Phase 9 rewrite.

Input: `experiments/phase12_new_unseen_evaluation/U_TOP5_FOR_ANNOTATION.csv` (empty labels; not overwritten).

## Outputs

- `ANNOTATION_PROTOCOL.md`
- `U_QRELS.csv` — 200 labeled rows
- `U_PER_QUERY.csv`
- `PHASE12_HUMAN_RESULTS.md`
- `artifacts/metrics.json`

## Primary metric

**Success@5** = queries with ≥1 A or B in the retrieved Top-5, divided by 40.

Do not mix with 68/78 = 0.8718 or with K ExactSource 27/40.
