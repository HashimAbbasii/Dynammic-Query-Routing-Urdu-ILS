# Phase 3 — full-article retrieval forensics

**Status:** complete. Stop here. Do not start Phase 4. Do not unseal H001–H040. Do not retrain the SVM.

## What this folder is

Diagnosis of **why the full-article Chroma index loses to the headline cache** on known-item retrieval, using only Phase 2 **dev + internal_val** (n=78).

The frozen test **H001–H040** was not loaded, not used for chunk size, not used for method selection.

## Rules that were kept

- No SVM retrain
- No new router, no RRF, no confidence lights
- No overwrite of Phase 0 / 1 / 2 artifacts
- Roman Urdu was **not** used to pick a retrieval method
- One chunking configuration, justified by `max_seq_length=128` (96 tokens, overlap 24)
- Chunk experiment is a **re-rank of Chroma top-15**, not a 111k-document chunk ANN

## Files

| File | Role |
| --- | --- |
| `ARCHITECTURE_AUDIT.md` | Code-level map of preprocess → embed → Chroma → query |
| `FULL_INDEX_ERROR_ANALYSIS.md` | Stratified query-level failures |
| `ROMAN_URDU_ANALYSIS.md` | Script-mismatch diagnosis (not a training signal) |
| `PHASE3_RESULTS.md` | Answers to the Phase 3 success questions |
| `BASELINE_RESULTS.csv` | Headline vs current full vs chunk re-rank @5/10/15 |
| `CHUNKING_COMPARISON.csv` | Same comparison, compact |
| `RETRIEVAL_EXPERIMENTS.csv` | E0–E3 controlled experiments |
| `ORACLE_CEILING_COMPARISON.csv` | Oracle nDCG@5 before/after replacing full with chunk re-rank |
| `phase3_statistics.json` | Machine-readable dump |
| `eval_query_forensics.csv` | Per-query ranks, cosines, titles |
| `run_phase3.py` | Reproducible runner |
| `figures/` | hit@k, truncation histogram, self-similarity, hit by language |

## Eval pool

Phase 2 `oracle_all.csv` rows with `split ∈ {dev, internal_val}` → **78** queries (39+39). Train (182) was not used to pick a method. Frozen 40 unused.

## Headline result

Chunk re-rank **does not** raise known-item **nDCG@5** (0.2203 → 0.2203). Source hit@5 rises 0.2564 → 0.2821 at **~27×** query-time cost. Oracle ceiling does **not** increase (0.4327 → 0.4319).

**Selected full index for later phases:** keep `full_one_vector_chroma_111k`.
