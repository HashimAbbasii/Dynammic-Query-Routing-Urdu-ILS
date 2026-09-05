# M0 source locations (not relocated)

Python entry points were **not** moved, so documented freeze paths still work.

- Detector / BM25 / Method D routing: `experiments/phase5_roman_urdu/run_phase5.py`
- Method D character table: `experiments/phase2_oracle/run_phase2_pipeline.py`
- Phase 12 retrieval runner: `experiments/phase12_new_unseen_evaluation/run_phase12.py`

## Post-Phase-12 research modules

These are isolated from M0. They do not change official retrieval results.

- `src/roman_urdu_normalization/` — Module 1: generic Roman Urdu surface-form normalization (candidate intervention; not wired into retrieval)
