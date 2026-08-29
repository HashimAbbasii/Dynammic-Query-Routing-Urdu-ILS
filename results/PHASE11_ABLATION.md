# Phase 11 ablation (M0–M4)

Query-side Roman expansions M1–M4 were scored on the **same** Phase 2 n = 78 known-item pool.

| System | ExactSource Hit@5 |
| --- | --- |
| M0 (official) | 68/78 = 87.18% |
| M1 | 68/78 = 87.18% |
| M2 | 68/78 = 87.18% |
| M3 | 68/78 = 87.18% |
| M4 | 68/78 = 87.18% |

Roman-train Hit@5 remained 61/64 = 95.31%. M1–M4 nDCG@5 was slightly below M0.

**M0 was not replaced.** M1 is a gate-passing candidate, not an improved final model.

Evidence: `experiments/phase11_improvement/PHASE11_ABLATION_RESULTS.md`, `M0_RESULTS.json` … `M4_RESULTS.json`
