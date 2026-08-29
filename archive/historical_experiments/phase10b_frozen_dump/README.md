# Phase 10B — Frozen-system retrieval dump

Diagnostic replay of the **frozen Phase 9 retriever** on H001–H040.  
It persists Top-50 lists that Phase 9 computed in memory and discarded.

**This is not Phase 9.** Phase 9 remains the official known-item evaluation.  
H001–H040 ExactSource Hit@5 stays **undefined**. Do not report it as 0%, 87.18%, or ~80%.

## What this phase does

- Preflight the frozen corpus / dictionary / BM25 constants / code paths
- Search H001–H040 with the frozen router (URDU/MIXED → Urdu BM25; ROMAN → Method D)
- Write complete Top-50 rows (actual hits only; no padding)
- Compare 10B rank-1 `doc_id` to Phase 9 `top1_doc_id`
- Stop. No relevance labels. No IR quality metrics. No architecture change.

## What this phase does not do

- Overwrite `experiments/phase9_heldout_evaluation/`
- Overwrite `artifacts/phase10/HELD_OUT_RETRIEVAL_DETAILS.csv`
- Use `heldout_retrieval_template.csv`
- Invent `source_doc_id`
- Start Phase 10C
- Tune on H001–H040

## How to run

```
python experiments/phase10b_frozen_dump/run_phase10b.py
```

If preflight fails, the script exits without searching.

## Outputs

| File | Contents |
|---|---|
| `artifacts/preflight.json` | Gate results |
| `artifacts/run_manifest.json` | Experiment id, hashes, environment |
| `TOP50_RETRIEVAL.csv` | All returned ranks ≤ 50 |
| `TOP5_FOR_ANNOTATION.csv` | Ranks 1–5 (or fewer) + headline/snippet; `relevance_label` empty |
| `RANK1_VS_PHASE9.csv` | Rank-1 identity check |
| `PHASE10B_RESULTS.md` | Dump report only |

## Data split

- **Development:** `QTRN_*` n=78 — only pool for selecting future improvements
- **Diagnostic held-out:** H001–H040 — dump only (later 10C baseline); do not tune
- **Future unseen:** H041+ / new sample — required for any post-improvement unseen claim

Protocol: `PHASE10B_SEALED_PROTOCOL.md`
