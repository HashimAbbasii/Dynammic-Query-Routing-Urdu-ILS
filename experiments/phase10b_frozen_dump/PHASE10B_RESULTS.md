# PHASE 10B RESULTS — frozen-system retrieval dump

Diagnostic dump only. **Not** a Phase 9 rewrite. **Not** an ExactSource Hit@5 evaluation.
No A/B/C/D/E labels. No P@5 / Success@5 / nDCG@5. H001–H040 official Hit@5 remains **undefined**.

## Experiment

| | |
| --- | --- |
| experiment_id | `phase10b_frozen_dump` |
| replaces_phase9 | no |
| queries | H001–H040 (n=40) |
| corpus SHA-256 | `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231` |
| n_docs | 111860 |
| dictionary keys | 198 |
| BM25 k1 / b | 1.5 / 0.75 |
| top_k | 50 |
| Python | 3.13.9 |
| NumPy | 2.3.5 |
| pandas | 2.3.3 |
| git commit | b54ffeb805483aa1419095e28c16e3e38e37d1db |
| timestamp UTC | 2026-08-27T13:24:24Z |

## Preflight

Preflight **PASS**. Retrieval ran only after a pass.

## Detector and path counts

Detector: {"URDU": 20, "ROMAN": 20}

Path: {"urdu_bm25": 20, "roman_bm25_method_D": 20}

## Hits returned

| | |
| --- | --- |
| queries processed | 40 |
| total retrieved rows (Top-50 dump) | 1909 |
| Top-5 annotation rows | 196 |
| queries with n_hits_returned < 5 | 1 |

n_hits_returned distribution: {"1": 1, "8": 1, "50": 38}

Queries with fewer than 5 hits: H036

## Rank-1 vs Phase 9

| | |
| --- | --- |
| match | 40 / 40 |
| mismatch | 0 |

Rank-1 replay identity is **verified** (40/40).

This does **not** prove that ranks 2–50 equal the discarded Phase 9 lists. It confirms that the frozen replay’s first hit matches the only rank Phase 9 saved.

## Artifacts

- `experiments/phase10b_frozen_dump/artifacts/preflight.json`
- `experiments/phase10b_frozen_dump/artifacts/run_manifest.json`
- `experiments/phase10b_frozen_dump/TOP50_RETRIEVAL.csv`
- `experiments/phase10b_frozen_dump/TOP5_FOR_ANNOTATION.csv`
- `experiments/phase10b_frozen_dump/RANK1_VS_PHASE9.csv`

Phase 9 files were not written. Phase 10A `HELD_OUT_RETRIEVAL_DETAILS.csv` was not overwritten.

## Explicitly not reported

H001–H040 Hit@5, P@5, Success@5, nDCG@5, MRR, human relevance, ~80%, A/B/C/D/E labels.

Development ExactSource Hit@5 on n=78 remains **0.8718**. That number is not a held-out H score.

## Stop

Phase 10B complete. Do not start Phase 10C in this run. Do not tune on H001–H040.
