# Phase 6 — Residual retrieval failure diagnosis

Diagnosis only. **No system change.**

## Frozen policy (Phase 5)

- URDU → Urdu BM25 (`k1=1.5`, `b=0.75`, `combined_text`)
- ROMAN → Method D (romanized-document BM25, full corpus)
- MIXED → Urdu BM25

Eval: Phase 2 `dev` + `internal_val` (`n=78`). **H001–H040 sealed.**

## Reproduce

From the repository root:

```
python experiments/phase6_residual_diagnosis/run_phase6.py
```

Rebuilds the frozen BM25 indexes (does not modify Phase 5 files). Stops if script-aware Hit@5 is not 0.8718.

Headline ranks are recomputed with the same MiniLM headline index as Phase 4B (`search_headlines`, `transliterate_roman` first).

## Outputs

| File | Role |
| --- | --- |
| `RESIDUAL_QUERY_INVENTORY.csv` | All 78 ranks under the frozen policy |
| `RESIDUAL_SPLIT_SUMMARY.csv` | DEV vs INTERNAL_VAL misses |
| `RANK_DEPTH_ANALYSIS.csv` | Top-5 / 6–10 / 11–20 / 21–50 / miss-50 |
| `ROOM_COMPLEMENTARITY.csv` | Headline vs script-aware oracle (not a system) |
| `LEXICAL_OVERLAP_ANALYSIS.csv` | Misses vs hits |
| `TOP_RESULT_ERROR_ANALYSIS.csv` | Top-5 neighbour patterns |
| `KNOWN_ITEM_AUDIT.md` | Qualitative topical labels |
| `FAILURE_TAXONOMY.csv` | One primary label per miss |
| `FAILURE_SUMMARY.csv` | Aggregates |
| `PHASE6_RESULTS.md` | Final report |
| `figures/` | Rank depth, complementarity, overlap, taxonomy |

Qualitative taxonomy does **not** change the official known-item Hit@5.

## Stop

Do not implement RRF, a reranker, a new dense index, SVM, or BM25 retune in this folder.
