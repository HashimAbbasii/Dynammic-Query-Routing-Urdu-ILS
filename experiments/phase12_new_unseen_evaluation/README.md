# Phase 12 — new unseen evaluation

**Official system: M0** (frozen). Phase 11 did not replace it.

| Subset | What it measures | This folder now |
|---|---|---|
| K001–K040 | ExactSource known-item | Retrieval + `K_RESULTS.md` |
| U001–U040 | Later human Success@5 | Retrieval dump only; labels empty |

H001–H040 are **not** reused. n=78 ExactSource **0.8718** stays the development/validation known-item result.

## Read first

1. `PHASE12_SEALED_PROTOCOL.md` (design)
2. `PHASE12_RETRIEVAL_PROTOCOL.md`
3. `PREFLIGHT_CHECKLIST.md`
4. `QUERY_GENERATION_REPORT.md`

## Sealed query files (do not edit)

- `queries_k.csv`
- `queries_u.csv`
- `SEAL.json`

## After retrieval (do not annotate yet)

- `K_TOP50_RETRIEVAL.csv`
- `K_RESULTS.md`
- `U_TOP50_RETRIEVAL.csv`
- `U_TOP5_FOR_ANNOTATION.csv`
- `U_RETRIEVAL_STATS.md`
- `artifacts/preflight.json`
- `artifacts/run_manifest.json`
