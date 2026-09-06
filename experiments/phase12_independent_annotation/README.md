# Independent annotation package

This folder is for a **second human annotator** of the frozen Phase 12 U Top-5 lists.

It does not rerun retrieval. It does not change the retriever.

## Files

| File | Role |
| --- | --- |
| `INSTRUCTIONS.md` | How to assign A / B / C / D / E |
| `U_TOP5_FOR_INDEPENDENT_ANNOTATION.csv` | 200 rows to label (`relevance_label` empty) |
| `SOURCE_LOCK.json` | SHA-256 lock of the original dump |

The original dump is `experiments/phase12_new_unseen_evaluation/U_TOP5_FOR_ANNOTATION.csv`. That file was not modified.

## Annotator task

Fill `relevance_label` only. See `INSTRUCTIONS.md`.
