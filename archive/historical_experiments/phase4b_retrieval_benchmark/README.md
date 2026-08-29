# Phase 4B — retrieval architecture benchmark

Eval: Phase 2 `dev` + `internal_val`, **n=78**, known-item. **H001–H040 unused.**

## Result (short)

| System | Hit@5 | nDCG@5 |
| --- | ---: | ---: |
| Headline | 0.4487 | 0.4009 |
| Old Full | 0.2564 | 0.2203 |
| Chunk ANN | 0.2821 | 0.2362 |
| **BM25** | **0.5897** | **0.5509** |
| Long-context e5-small | not indexed (CPU 13.5 h) | — |

Headline+BM25 oracle nDCG@5 = **0.617**. Adding Full/Chunk does not raise it. Roman Urdu BM25 Hit@5 = **0**.

Full write-up: `PHASE4B_FINAL_REPORT.md`.

```text
python run_phase4b.py --stage reproduce
python run_phase4b.py --stage bm25
python run_phase4b.py --stage longctx   # stops if >4h extrapolated
python run_phase4b.py --stage report
```
