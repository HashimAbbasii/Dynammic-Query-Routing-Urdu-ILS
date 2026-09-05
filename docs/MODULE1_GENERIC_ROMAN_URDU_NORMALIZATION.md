# Module 1: Generic Roman Urdu Normalization

**Status:** Candidate intervention on branch `research/post-phase12`. **Not** part of frozen M0. **No** retrieval scores were computed for this module.

This module is a candidate intervention for testing the hypothesis that generic Roman Urdu normalization can reduce lexical mismatch. It does **not** claim improved Hit@5, Success@5, nDCG, or MRR.

Full usage and rule table: `src/roman_urdu_normalization/README.md`.

## Isolation

| Frozen item | Touched by Module 1? |
| --- | --- |
| M0 (`experiments/phase5_roman_urdu/run_phase5.py`) | No |
| Method D character table (`experiments/phase2_oracle/run_phase2_pipeline.py`) | No |
| `models/roman_urdu_dict_expanded.json` | No |
| Phase 12 queries, qrels, runners | No |
| Official 87.18% / 67.50% / 57.50% | No |

Existing `experiments/phase2_oracle/textnorm.py` remains a **leakage-check** helper for Phase 2 isolation. Module 1 does not replace it and is not imported by it.

## Integration point (identified, not modified)

A future experiment could apply `normalize_roman_urdu` to **ROMAN** queries *before* Method D BM25. That would require a new runner or a clearly marked non-M0 fork. Frozen M0 was **not** modified.

## Future candidate — not implemented

Dictionary expansion (new keys in `roman_urdu_dict_expanded.json`) is out of scope. If pursued, it must use development data that is not U001–U040 or K001–K040.
