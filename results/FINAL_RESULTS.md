# Official ULTRA results (frozen M0)

**System:** M0 (script-aware BM25). These numbers are copied from the sealed Phase 8–12 reports. They were **not** recomputed.

Do **not** average the three headlines. They answer different questions.

| Evaluation | Dataset | Type | Metric | Result |
| --- | --- | --- | --- | --- |
| Development / validation | Phase 2, n = 78 | Known-item | ExactSource Hit@5 | **68/78 = 87.18%** |
| New known-item | K001–K040 | Known-item | ExactSource Hit@5 | **27/40 = 67.50%** |
| New naturalistic | U001–U040 | Human relevance | Success@5 | **23/40 = 57.50%** |

- **87.18%** is title-derived known-item recovery on the freeze pool. It is not human usefulness and not unseen naturalistic performance.
- **67.50%** is ExactSource Hit@5 on independently sealed known-item queries.
- **57.50%** is human Success@5 (at least one A or B in the Top-5). It is **not** ExactSource Hit@5.

See `DEVELOPMENT_VALIDATION.md`, `PHASE12_RESULTS.md`, and `PHASE11_ABLATION.md` in this folder.

Source reports (unchanged):

- `experiments/phase8_final_freeze/DEVELOPMENT_RESULTS.md`
- `experiments/phase12_new_unseen_evaluation/K_RESULTS.md`
- `experiments/phase12_human_relevance/PHASE12_HUMAN_RESULTS.md`
- `docs/FINAL_EXPERIMENTAL_RESULTS_ANALYSIS.md`
