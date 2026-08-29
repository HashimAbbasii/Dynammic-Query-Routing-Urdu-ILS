# Phase 11 M0–M4 ablation

Query-side Roman transforms on the **frozen** retriever.  
Phase 9 remains the official known-item evaluation. This folder does **not** write Phase 9 files.

## Run

```
python experiments/phase11_improvement/run_phase11_ablation.py
```

Preflight must pass before any BM25 search. H001–H040 are not loaded.

## Outputs

`transformations.json`, `M0_RESULTS.json` … `M4_RESULTS.json`, `PHASE11_ABLATION_RESULTS.md`

## Do not

Tune on H001–H040, edit the 198-key dictionary, change Method D documents, or create H041+ in this step.
