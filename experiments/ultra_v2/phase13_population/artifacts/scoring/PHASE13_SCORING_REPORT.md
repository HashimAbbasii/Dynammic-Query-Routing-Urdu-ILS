# Phase 13 Scoring Report

**Decision:** CONFIRMATORY COMPLETE (n=51 consistency PASS)
**TEST accessed:** no
**Retuning:** no

## n=80 (full frozen population)

| Method | Hit@1 | Hit@5 | Hit@10 | Hit@50 | MRR |
|---|---:|---:|---:|---:|---:|
| Method-D BM25 | 1/80 | 5/80 | 5/80 | 13/80 | 0.0336 |
| Dense e5-small | 9/80 | 20/80 | 23/80 | 36/80 | 0.1718 |
| NG3 | 4/80 | 10/80 | 13/80 | 19/80 | 0.0766 |
| Hybrid RRF | 5/80 | 17/80 | 25/80 | 40/80 | 0.1376 |
| Phase 9 | 1/80 | 9/80 | 10/80 | 19/80 | 0.0520 |
| Phase 10 cascade | 5/80 | 17/80 | 25/80 | 39/80 | 0.1373 |
| Phase 10b | 5/80 | 17/80 | 25/80 | 40/80 | 0.1376 |

## n=51 subset (must = frozen)

| Method | Hit@1/5/10/50_n | MRR | vs frozen |
|---|---|---:|---|
| Method-D BM25 | 1/4/4/6 | 0.0375 | MATCH |
| Dense e5-small | 5/15/16/22 | 0.1726 | MATCH |
| NG3 | 3/6/6/8 | 0.0750 | MATCH |
| Hybrid RRF | 3/11/19/25 | 0.1422 | MATCH |
| Phase 9 | 1/5/6/10 | 0.0478 | MATCH |
| Phase 10 cascade | 3/11/19/24 | 0.1418 | MATCH |
| Phase 10b | 3/11/19/25 | 0.1422 | MATCH |

## n=29 Phase-13-only (descriptive)

| Method | Hit@1 | Hit@5 | Hit@10 | Hit@50 | MRR |
|---|---:|---:|---:|---:|---:|
| Method-D BM25 | 0/29 | 1/29 | 1/29 | 7/29 | 0.0268 |
| Dense e5-small | 4/29 | 5/29 | 7/29 | 14/29 | 0.1704 |
| NG3 | 1/29 | 4/29 | 7/29 | 11/29 | 0.0794 |
| Hybrid RRF | 2/29 | 6/29 | 6/29 | 15/29 | 0.1295 |
| Phase 9 | 0/29 | 4/29 | 4/29 | 9/29 | 0.0593 |
| Phase 10 cascade | 2/29 | 6/29 | 6/29 | 15/29 | 0.1295 |
| Phase 10b | 2/29 | 6/29 | 6/29 | 15/29 | 0.1295 |

## SHA-256

- `PHASE13_SCORING_PER_QUERY.csv`: `f59c37102ba5c212e7b2c14600cf3781732eef98757379f51c26f0a250fe5d66`
- `phase13_scoring_summary.json`: `9c619f6a3bf1655e7e17f181bd872cd1fc5dd1c56954f7652dc535b2a2455cf9`
- `PHASE13_SCORING_PREREGISTRATION.md`: `55788660c5d1f6d9d55399d82ed722733ab64097704fb23084fd77b1b39b912a`
