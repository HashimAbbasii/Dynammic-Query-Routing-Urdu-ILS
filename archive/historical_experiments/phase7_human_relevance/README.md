# Phase 7 — Human relevance validation of residual known-item misses

Annotation / evaluation only. **Frozen retrieval is unchanged.**

Official metric remains exact `source_doc_id` Hit@5 on n=78.

## Protocol

1. Freeze `ANNOTATION_RUBRIC.md` on DEV residuals QTRN_168, 170, 189, 225.
2. Annotate those four Top-5 lists.
3. Apply the same rubric once to INTERNAL_VAL residuals.
4. Do not edit the rubric after INTERNAL_VAL.
5. Do not open H001–H040.

Top-5 lists come from Phase 6 `artifacts/miss_details.json` (script-aware room).

## Reproduce units

```
python experiments/phase7_human_relevance/_dump_units.py
```

writes `artifacts/annotation_units.json`. Labels are in the CSVs, not re-derived by code.

## Stop

Do not implement RRF, a reranker, a dense index, or SVM. Do not start Phase 8 from this folder.
