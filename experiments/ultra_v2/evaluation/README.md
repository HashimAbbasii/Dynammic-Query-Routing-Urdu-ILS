# ULTRA v2 evaluation

Metric definitions live in `../PROTOCOL.md` §§12–14.  
Schemas and header-only CSV templates live in `schemas/`.

**Not implemented here:** retrieval, BM25, dense search, pooling execution, or scoring of real runs. Those wait until a benchmark exists and a later phase is authorized.

## Two stages

```text
Candidate generation → Top-50 → Recall@50
Final ranking        → Top-5  → Hit@5 / Success@5
```

## Gains (NL nDCG)

| Label | nDCG_useful@5 | nDCG_topical@5 |
| --- | ---: | ---: |
| A | 3 | 3 |
| B | 1 | 2 |
| C | 0 | 1 |
| D | 0 | 0 |
| E | 0 | 0 |

Primary NL metric is Success@5, not nDCG_topical@5.

## Mixing ban

Do not average KN ExactSource Hit@5 with NL Success@5. Do not report 87.18% as a v2 score. Do not treat 80% as a threshold.
