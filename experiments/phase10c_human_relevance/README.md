# Phase 10C — human relevance (frozen 10B Top-5)

Baseline human-relevance evaluation of the **frozen** retriever on H001–H040.

Input: `experiments/phase10b_frozen_dump/TOP5_FOR_ANNOTATION.csv` only.  
No retrieval. No architecture change. Does **not** replace Phase 9 ExactSource Hit@5.

## Outputs

- `ANNOTATION_ADDENDUM.md` — H-query rules (raw query; temporal type-of-fact)
- `HELD_OUT_QRELS.csv` — 196 labeled rows
- `PHASE10C_RESULTS.md` — metrics and limitations

## Metrics (after all labels)

- **Success@5:** query succeeds if any retrieved Top-5 row is A or B; divide by 40
- **Conservative P@5:** (count of A) / 5 per query, then mean
- **Variable-denominator P@5:** (count of A) / min(5, n_hits_returned)

Do not call these ExactSource Hit@5. Do not mix with 0.8718.
