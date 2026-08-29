# Phase 4A status (23 Aug 2026)

## Finished

**Baseline reproduction (n=78, same as Phase 3):** exact match.

| system | hit@5 | nDCG@5 | P@5 | MRR |
| --- | ---: | ---: | ---: | ---: |
| Headline | 0.4487 | 0.4009 | 0.0897 | 0.3885 |
| Full one-vector | 0.2564 | 0.2203 | 0.0513 | 0.2103 |

Δ vs Phase 3 full: hit@5 **0.000**, nDCG@5 **0.000**. Safe to continue.

**Corpus token stats (all 111,860 articles):**

| | |
| --- | ---: |
| mean tokens | 369 |
| median | 291 |
| p90 / p95 / p99 | 661 / 838 / 1456 |
| max | 9769 |
| share > 128 tokens | **94.42%** |

Pre-registered chunks **96 / overlap 32** (not 192/32: that exceeds MiniLM 128 and would truncate). Estimated **644,100** chunks, ~0.99 GB raw embeddings.

## In progress

Corpus chunk **encode + Chroma HNSW** (`python run_phase4a.py --stage index`).

At 3,500 / 111,860 articles (~28.5 min): ~34k chunks written. **ETA ~14–15 hours remaining** on CPU. Resumable via `artifacts/index_progress.json`.

Full write-up: `PHASE4A_REPORT.md`.

Do not start `--stage eval` until `index_build.json` exists and Chroma count = 644,100.

## Not started (blocked on index)

- Eval vs full/headline on n=78
- Recovery of full-index misses
- Latency / disk of the real chunk ANN
- Oracle ceiling with chunk ANN as the full room
- Phase 4B (not this phase)

H001–H040 unused. SVM untouched. Live `urdu_news` collection not overwritten.
