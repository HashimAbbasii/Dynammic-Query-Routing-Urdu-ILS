# Final test checklist

All items must be **true** before any H001–H040 query is read for evaluation.

Copy this list into the Phase 9 run log and tick at execution time. During Phase 8 they are declared frozen as follows.

## Freeze status (Phase 8)

- [x] Architecture frozen — URDU/MIXED → Urdu BM25; ROMAN → Method D
- [x] BM25 parameters frozen — k1=1.5, b=0.75
- [x] Romanizer frozen — Phase 2 `_CHAR_ROMAN` + reverse dictionary, full corpus
- [x] Script detector frozen — Unicode counts, not SVM
- [x] Corpus frozen — `data/clean_articles.csv`, 111,860 rows, SHA-256 in the manifest
- [x] Indexes frozen — rebuild only with the same code; no alternate tokenizers
- [x] Evaluation code frozen — protocol in `FINAL_EVALUATION_PROTOCOL.md`; scorer = Phase 5 `BM25.search` + rank-of-source
- [x] Primary metric frozen — exact-source Hit@5
- [x] Secondary metrics frozen — P@5, nDCG@5, MRR, Hit@10, Hit@15
- [x] No test queries inspected — H001–H040 not opened in Phase 8
- [x] No test labels inspected
- [x] No test tuning allowed — written into the protocol
- [x] Random seeds/configuration recorded — retrieval is deterministic; `SEED=42` unused on the official path; k1/b/top_k in `FROZEN_CONFIGURATION.json`
- [x] Development results recorded — `DEVELOPMENT_RESULTS.md` (Hit@5 0.8718)
- [x] Phase 7 limitations documented — `PHASE7_EVALUATION_LIMITATIONS.md`

## Still required at the start of the held-out run (Phase 9, not this phase)

- [x] Confirm corpus SHA-256 still matches the manifest — 2026-08-27T12:44:16Z, `experiments/phase9_heldout_evaluation/artifacts/preflight.json`
- [x] Confirm dictionary still has 198 keys and was not edited
- [x] Confirm no H001–H040 files were opened in the meantime — trap file opened only to load IDs/queries for the single run; no gold `source_doc_id` exists; no tuning
- [x] Run evaluation **once** — `experiments/phase9_heldout_evaluation/run_phase9.py`
- [x] Publish official metrics without a second architecture pass — n_scored=0, n_excluded=40; ExactSource Hit@5 undefined (see `PHASE9_RESULTS.md`)
