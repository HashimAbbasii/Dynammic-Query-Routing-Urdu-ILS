# Phase 12 U retrieval statistics (frozen M0 dump)

Naturalistic sealed set **U001–U040**. **No** gold documents. **No** human labels.
Do **not** report Success@5, P@5, nDCG, MRR, or any guessed relevance score.

| | |
| --- | --- |
| queries processed | 40 |
| detector counts | {"URDU": 18, "ROMAN": 18, "MIXED": 4} |
| retrieval-path counts | {"urdu_bm25": 22, "roman_bm25_method_D": 18} |
| n_hits_returned distribution | {"50": 39, "28": 1} |
| Top-50 rows | 1978 |
| Top-5 annotation rows | 200 |
| queries with n_hits_returned < 5 | 0 |
| queries with n_hits_returned = 0 | 0 |

Queries with fewer than 5 hits: none

`relevance_label` is empty on all Top-5 rows. Annotation is a later approved step.
