# Phase 5 — Roman Urdu retrieval experiment

Controlled comparison of **pre-registered** Roman Urdu strategies.  
This is **not** the final ULTRA architecture.

## Protocol

- Eval: Phase 2 `dev` + `internal_val` (`n=78`). IDs from `experiments/phase2_oracle/`.
- **H001–H040 sealed.**
- Select among Methods A–D on **DEV Roman Urdu only**.
- Primary = Hit@5, secondary = nDCG@5, tie-break = lower latency.
- Freeze the winner. Confirm **once** on `internal_val`.
- Method E is union/oracle analysis, not a system.
- Do not modify Phase 0–4B result files.

Method definitions: [`METHODS_PREREGISTERED.md`](METHODS_PREREGISTERED.md).

## Reproduce

From the repository root:

```
python experiments/phase5_roman_urdu/run_phase5.py
```

Requires `data/clean_articles.csv`, `models/roman_urdu_dict_expanded.json`, Phase 2 oracle CSVs, and Phase 4B `QUERY_LEVEL_COMPARISON.csv` (dense ranks reused, not recomputed).

## Outputs

| File | Role |
| --- | --- |
| `ROMAN_QUERY_INVENTORY.csv` | Roman query ids + baseline ranks |
| `TRANSLITERATION_AUDIT.md` | Existing dictionary, as-is |
| `DEV_METHOD_COMPARISON.csv` | A–D (+ E analysis) on DEV |
| `INTERNAL_VAL_CONFIRMATION.csv` | Frozen method on internal_val |
| `ROMAN_QUERY_COMPARISON.csv` | Per-query ranks |
| `URDU_REGRESSION_CHECK.csv` | Urdu BM25 vs script-aware routing |
| `SCRIPT_DETECTION_REPORT.md` | Deterministic URDU/ROMAN/MIXED |
| `SCRIPT_ROUTING_RESULTS.csv` | Combined n=78 |
| `ORACLE_HEADROOM.csv` | Ceilings, not deployable |
| `FAILURE_ANALYSIS.md` | Diagnosis only |
| `PHASE5_RESULTS.md` | Final report |
| `figures/` | Plots |

## Stop

After this phase: do not run H001–H040, retrain SVM, build RRF, add a reranker, retune BM25, or start long-context indexing.
