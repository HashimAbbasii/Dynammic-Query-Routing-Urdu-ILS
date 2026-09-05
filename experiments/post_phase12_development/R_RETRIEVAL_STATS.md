# R-dev M0 retrieval statistics (frozen dump only)

Sealed development set **R001–R100**. **No** performance metrics computed.
Do **not** report Hit@5, ExactSource Hit@5, Success@5, P@5, nDCG, or MRR from this step.

| | |
| --- | --- |
| queries processed | 100 |
| track counts | {"KI": 50, "NAT": 50} |
| detector counts (M0 runtime) | {"URDU": 18, "MIXED": 40, "ROMAN": 42} |
| retrieval-path counts | {"urdu_bm25": 58, "roman_bm25_method_D": 42} |
| n_hits_returned distribution | {"50": 96, "8": 1, "29": 2, "0": 1} |
| Top-50 rows | 4866 |
| Top-5 rows | 495 |
| queries with n_hits_returned < 5 | 1 |
| queries with n_hits_returned = 0 | 1 |

Queries with fewer than 5 hits: R080

`relevance_label` is empty on all Top-5 rows. Annotation is a later approved step.
