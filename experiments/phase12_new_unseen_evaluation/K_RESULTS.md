# Phase 12 K results — ExactSource known-item (frozen M0)

New independent known-item evaluation on **K001–K040**.
Does **not** replace Phase 9 development/validation ExactSource Hit@5 = 68/78 = 0.8718.
Does **not** measure human relevance. Do not mix with U.

## Preflight and freeze

| | |
| --- | --- |
| preflight | **PASS** |
| official system | M0 |
| corpus SHA-256 | `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231` |
| n_docs | 111860 |
| dictionary SHA-256 | `30c3f61a64ec641abbb3acdbc7a8bcaf197f0238f1bf9e76c2c7ce8e590f86a3` |
| dictionary keys | 198 |
| BM25 k1 / b | 1.5 / 0.75 |
| top_k | 50 |
| routing | URDU/MIXED → urdu_bm25; ROMAN → roman_bm25_method_D |
| M1–M4 applied | no |
| H001–H040 used | no |

## Queries

| | |
| --- | --- |
| n | 40 |
| detector counts | {"URDU": 28, "ROMAN": 12} |
| retrieval-path counts | {"urdu_bm25": 28, "roman_bm25_method_D": 12} |
| n_hits_returned distribution | {"50": 40} |

## ExactSource metrics (primary = Hit@5)

| Metric | Hits | n | Rate |
| --- | ---: | ---: | ---: |
| ExactSource Hit@1 | 20 | 40 | 0.5000 = 50.00% |
| **ExactSource Hit@5** | **27** | **40** | **0.6750 = 67.50%** |
| ExactSource Hit@10 | 28 | 40 | 0.7000 = 70.00% |
| ExactSource Hit@50 | 30 | 40 | 0.7500 = 75.00% |

Valid claim: “On the sealed known-item set K001–K040, frozen M0 ExactSource Hit@5 = 27/40.”

Invalid: treating this number as human Success@5, as unseen H001–H040 accuracy, or as a replacement for 68/78.

## Per-query source rank

| query_id | detector | path | n_hits | source_doc_id | source_rank | Hit@5 |
| --- | --- | --- | ---: | ---: | ---: | --- |
| K001 | URDU | urdu_bm25 | 50 | 1508 | 1 | yes |
| K002 | URDU | urdu_bm25 | 50 | 2815 | 6 | no |
| K003 | URDU | urdu_bm25 | 50 | 3296 | 1 | yes |
| K004 | ROMAN | roman_bm25_method_D | 50 | 5849 | not_in_top50 | no |
| K005 | ROMAN | roman_bm25_method_D | 50 | 8704 | not_in_top50 | no |
| K006 | ROMAN | roman_bm25_method_D | 50 | 9281 | not_in_top50 | no |
| K007 | ROMAN | roman_bm25_method_D | 50 | 9511 | 4 | yes |
| K008 | URDU | urdu_bm25 | 50 | 11480 | 1 | yes |
| K009 | URDU | urdu_bm25 | 50 | 15825 | 4 | yes |
| K010 | URDU | urdu_bm25 | 50 | 15846 | 49 | no |
| K011 | URDU | urdu_bm25 | 50 | 19383 | 1 | yes |
| K012 | URDU | urdu_bm25 | 50 | 21756 | 1 | yes |
| K013 | ROMAN | roman_bm25_method_D | 50 | 21831 | not_in_top50 | no |
| K014 | URDU | urdu_bm25 | 50 | 23022 | 1 | yes |
| K015 | URDU | urdu_bm25 | 50 | 24538 | 1 | yes |
| K016 | ROMAN | roman_bm25_method_D | 50 | 26705 | not_in_top50 | no |
| K017 | URDU | urdu_bm25 | 50 | 29887 | 2 | yes |
| K018 | ROMAN | roman_bm25_method_D | 50 | 31070 | not_in_top50 | no |
| K019 | URDU | urdu_bm25 | 50 | 36767 | 1 | yes |
| K020 | ROMAN | roman_bm25_method_D | 50 | 38678 | not_in_top50 | no |
| K021 | URDU | urdu_bm25 | 50 | 38961 | 2 | yes |
| K022 | URDU | urdu_bm25 | 50 | 41072 | 1 | yes |
| K023 | URDU | urdu_bm25 | 50 | 41669 | 1 | yes |
| K024 | URDU | urdu_bm25 | 50 | 42765 | 1 | yes |
| K025 | ROMAN | roman_bm25_method_D | 50 | 51108 | not_in_top50 | no |
| K026 | URDU | urdu_bm25 | 50 | 59249 | 1 | yes |
| K027 | URDU | urdu_bm25 | 50 | 64255 | 2 | yes |
| K028 | URDU | urdu_bm25 | 50 | 70845 | 1 | yes |
| K029 | URDU | urdu_bm25 | 50 | 72267 | 1 | yes |
| K030 | URDU | urdu_bm25 | 50 | 74034 | 1 | yes |
| K031 | ROMAN | roman_bm25_method_D | 50 | 75789 | 17 | no |
| K032 | URDU | urdu_bm25 | 50 | 80149 | 1 | yes |
| K033 | ROMAN | roman_bm25_method_D | 50 | 80336 | not_in_top50 | no |
| K034 | URDU | urdu_bm25 | 50 | 82804 | 1 | yes |
| K035 | URDU | urdu_bm25 | 50 | 83115 | 1 | yes |
| K036 | URDU | urdu_bm25 | 50 | 83850 | 2 | yes |
| K037 | ROMAN | roman_bm25_method_D | 50 | 93401 | not_in_top50 | no |
| K038 | URDU | urdu_bm25 | 50 | 99509 | 3 | yes |
| K039 | URDU | urdu_bm25 | 50 | 102279 | 1 | yes |
| K040 | URDU | urdu_bm25 | 50 | 103265 | 1 | yes |

## Misses

Not in Top-5 (Hit@5 misses): K002, K004, K005, K006, K010, K013, K016, K018, K020, K025, K031, K033, K037

Not in Top-50: K004, K005, K006, K013, K016, K018, K020, K025, K033, K037

This list is complete. Successful queries are not singled out.

## Stop

K retrieval scored. Do not tune M0 on these misses. Do not start U annotation in this step.
