# Module 1 R-dev ablation results

Candidate interventions on **ROMAN branch only**. M0 baseline from frozen artifacts.

## M0 baseline (frozen)

| Track | Metric | Result |
| --- | --- | --- |
| KI | ExactSource Hit@5 | 19/50 = 38.00% |
| NAT | Success@5 (frozen qrels) | 12/50 = 24.00% |

## M1-A — Conservative normalization

Layer A: NFKC, lowercase, punctuation spacing, whitespace collapse

| | KI Hit@5 | NAT Success@5 |
| --- | --- | --- |
| M0 | 19/50 | 12/50 |
| Candidate | 19/50 | 12/50 |
| Delta | +0 | +0 |

**KI script strata (Hit@5):** {"URDU": {"n": 17, "m0_hits": 11, "cand_hits": 11, "m0_rate": 0.6471, "cand_rate": 0.6471, "delta": 0.0}, "ROMAN": {"n": 5, "m0_hits": 1, "cand_hits": 1, "m0_rate": 0.2, "cand_rate": 0.2, "delta": 0.0}, "MIXED": {"n": 28, "m0_hits": 7, "cand_hits": 7, "m0_rate": 0.25, "cand_rate": 0.25, "delta": 0.0}}

**NAT script strata (Success@5):** {"URDU": {"n": 1, "m0_hits": 1, "cand_hits": 1, "m0_rate": 1.0, "cand_rate": 1.0, "delta": 0.0}, "ROMAN": {"n": 36, "m0_hits": 7, "cand_hits": 7, "m0_rate": 0.1944, "cand_rate": 0.1944, "delta": 0.0}, "MIXED": {"n": 12, "m0_hits": 4, "cand_hits": 4, "m0_rate": 0.3333, "cand_rate": 0.3333, "delta": 0.0}}

KI improved: 0 | worsened: 0 | unchanged: 50

NAT improved: 0 | worsened: 0 | unchanged: 50

## M1-B — Dictionary-assisted normalization

Layer A + closed _VARIANT_TO_DICT_KEY aliases + dict-key canonical forms

| | KI Hit@5 | NAT Success@5 |
| --- | --- | --- |
| M0 | 19/50 | 12/50 |
| Candidate | 19/50 | 12/50 |
| Delta | +0 | +0 |

**KI script strata (Hit@5):** {"URDU": {"n": 17, "m0_hits": 11, "cand_hits": 11, "m0_rate": 0.6471, "cand_rate": 0.6471, "delta": 0.0}, "ROMAN": {"n": 5, "m0_hits": 1, "cand_hits": 1, "m0_rate": 0.2, "cand_rate": 0.2, "delta": 0.0}, "MIXED": {"n": 28, "m0_hits": 7, "cand_hits": 7, "m0_rate": 0.25, "cand_rate": 0.25, "delta": 0.0}}

**NAT script strata (Success@5):** {"URDU": {"n": 1, "m0_hits": 1, "cand_hits": 1, "m0_rate": 1.0, "cand_rate": 1.0, "delta": 0.0}, "ROMAN": {"n": 36, "m0_hits": 7, "cand_hits": 7, "m0_rate": 0.1944, "cand_rate": 0.1944, "delta": 0.0}, "MIXED": {"n": 12, "m0_hits": 4, "cand_hits": 4, "m0_rate": 0.3333, "cand_rate": 0.3333, "delta": 0.0}}

KI improved: 0 | worsened: 0 | unchanged: 50

NAT improved: 0 | worsened: 0 | unchanged: 50

## M1-C — Conservative + dictionary

Same as M1-B (Layer A plus read-only 198-key dictionary aliases)

| | KI Hit@5 | NAT Success@5 |
| --- | --- | --- |
| M0 | 19/50 | 12/50 |
| Candidate | 19/50 | 12/50 |
| Delta | +0 | +0 |

**KI script strata (Hit@5):** {"URDU": {"n": 17, "m0_hits": 11, "cand_hits": 11, "m0_rate": 0.6471, "cand_rate": 0.6471, "delta": 0.0}, "ROMAN": {"n": 5, "m0_hits": 1, "cand_hits": 1, "m0_rate": 0.2, "cand_rate": 0.2, "delta": 0.0}, "MIXED": {"n": 28, "m0_hits": 7, "cand_hits": 7, "m0_rate": 0.25, "cand_rate": 0.25, "delta": 0.0}}

**NAT script strata (Success@5):** {"URDU": {"n": 1, "m0_hits": 1, "cand_hits": 1, "m0_rate": 1.0, "cand_rate": 1.0, "delta": 0.0}, "ROMAN": {"n": 36, "m0_hits": 7, "cand_hits": 7, "m0_rate": 0.1944, "cand_rate": 0.1944, "delta": 0.0}, "MIXED": {"n": 12, "m0_hits": 4, "cand_hits": 4, "m0_rate": 0.3333, "cand_rate": 0.3333, "delta": 0.0}}

KI improved: 0 | worsened: 0 | unchanged: 50

NAT improved: 0 | worsened: 0 | unchanged: 50

No generalization claims. R-dev development only.

## M1-D — Layer A + repeated-character normalization

Layer A plus collapse ASCII letter runs of 3+ to maximum 2 consecutive (`NormalizationConfig.repeated_character_normalization=True`, `min_run_to_collapse=3`, `max_identical_letter_run=2`).

| | KI Hit@5 | NAT Success@5 |
| --- | --- | --- |
| M0 | 19/50 | 12/50 |
| M1-D | 19/50 | 12/50 |
| Delta | +0 | +0 |

**KI script strata (Hit@5):** {"URDU": {"n": 17, "m0_hits": 11, "cand_hits": 11, "m0_rate": 0.6471, "cand_rate": 0.6471, "delta": 0.0}, "ROMAN": {"n": 5, "m0_hits": 1, "cand_hits": 1, "m0_rate": 0.2, "cand_rate": 0.2, "delta": 0.0}, "MIXED": {"n": 28, "m0_hits": 7, "cand_hits": 7, "m0_rate": 0.25, "cand_rate": 0.25, "delta": 0.0}}

**NAT script strata (Success@5):** {"URDU": {"n": 1, "m0_hits": 1, "cand_hits": 1, "m0_rate": 1.0, "cand_rate": 1.0, "delta": 0.0}, "ROMAN": {"n": 36, "m0_hits": 7, "cand_hits": 7, "m0_rate": 0.1944, "cand_rate": 0.1944, "delta": 0.0}, "MIXED": {"n": 12, "m0_hits": 4, "cand_hits": 4, "m0_rate": 0.3333, "cand_rate": 0.3333, "delta": 0.0}}

Roman queries with token change: 0 / 42

Ranking lists changed vs M0: 0 / 100

KI improved: 0 | worsened: 0 | unchanged: 50

NAT improved: 0 | worsened: 0 | unchanged: 50
