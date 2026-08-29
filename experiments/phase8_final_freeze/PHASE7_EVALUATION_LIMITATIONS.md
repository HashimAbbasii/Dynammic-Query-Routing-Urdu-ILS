# Phase 7 evaluation limitations (carry into the freeze)

Official primary metric stays **exact-source Hit@5**.  
Human labels from Phase 7 are **secondary diagnostics on the 10 n=78 residuals only**. They were **not** computed on H001–H040 and must not be used to rewrite 0.8718.

## What known-item Hit@5 measures

Gold = one `source_doc_id`.  
A Top-5 of highly related articles still scores **0** if that exact row is missing.

Phase 7 (DEV-first rubric, then internal_val, rubric unchanged):

| On the 10 official misses | Count |
| --- | ---: |
| Exact-source Hit@5 | 0 / 10 |
| ≥1 RELEVANT in Top-5 | 3 / 10 |
| ≥1 RELEVANT or PARTIALLY_RELEVANT in Top-5 | **8 / 10** |
| Top-5 all NOT_RELEVANT | 0 / 10 |
| Query marked ambiguous | 8 / 10 |

Typical mechanisms:

- Recurring wires without a date (PSX third-day closes; Sindh CNG openings).
- Truncated mixed titles (`ئی سی سی کا`, genre-only film queries, `Pakistan news update` template).
- Same-event neighbours (snooker semi-final vs final; other SA–NZ series reports).

## What this does not allow

- Converting those 8/10 into official hits.
- Reporting “human P@5” as the system score.
- Tuning retrieval so that a neighbour of the gold counts as success.
- Annotating H001–H040 under the Phase 7 rubric unless a **new** sealed protocol says so after this freeze.

## How to report the held-out number

When H001–H040 are scored once, publish:

1. Exact-source Hit@5 (and secondary rank metrics) **as official**.
2. A pointer to this file so readers know known-item identity can understate topical usefulness.
3. The n=78 development baseline, without mixing pools.
