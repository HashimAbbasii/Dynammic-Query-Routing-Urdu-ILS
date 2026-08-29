# Phase 0 — Frozen baseline (do not modify this system on this record)

**Branch:** `research/phase0-1-routing-diagnosis`  
**Parent freeze:** `feat/dual-index-svm-routing`  
**Source of numbers:** existing frozen files. SVM was **not** retrained. Indexes were **not** rebuilt.

This record is the comparison point for every later experiment.

## What is frozen

| Piece | Location / value |
| --- | --- |
| Router | `validate/dual_index_routing/router.py` |
| Retrieval | `validate/dual_index_routing/retrieve.py` |
| V3 features (deployed 12) | `validate/dual_index_routing/extractor_v3.py` |
| V2 8-feature extractor | `validate/phase3/phase3a_extractor.py` |
| Deployed SVM | `models/svm_classifier.pkl` (12 features) |
| Scaler | `models/scaler.pkl` |
| V2 backup (Phase 3B 86/84) | `models/backup_v2_pre_trap_retrain_2026-08-22/` |
| Roman dictionary | `models/roman_urdu_dict_expanded.json` (198 pairs on disk) |
| Word-count baseline | ≥ 6 tokens → LONG / full-article room |
| θ=150 baseline | `len(query) ≥ 150` → LONG; on this 40-query set it never fires LONG |
| Headline index | `data/headline_embeddings_phase2_5_cache.npy` + `paraphrase-multilingual-MiniLM-L12-v2` |
| Full-article index | Chroma `data/chromadb` collection `urdu_news` (~111,860) |
| Confidence lights | HIGH ≥ 85, MEDIUM 60–85, LOW < 60 |
| Protocol labels | `validate/dual_index_routing/labels/heldout_traps.py` / classification JSON |
| Held-out P@5 judgments | `labels/heldout_retrieval_template.csv` (400 rows) |
| Metric code | `validate/dual_index_routing/evaluate_heldout_routed_p5.py` |

## Frozen headline numbers (do not mix tables)

Copied from `results/CURRENT.txt` / `results/CURRENT.json` (23 Aug 2026):

| Layer | n | SVM | Word count | θ=150 / always-headline | Always-full |
| --- | ---: | --- | --- | --- | --- |
| Phase 3B V2 classification | 50 | **86%** | **84%** | — | — |
| Held-out traps classification | 40 | **60%** | **20%** | **50%** | — |
| Held-out dual-index P@5 | 40 (400 judgments) | **33.00%** | **36.50%** | **35.00%** | **34.25%** |
| Held-out nDCG@5 | 40 | 0.6149 | 0.6476 | **0.6868** | 0.6020 |
| Phase 2.5 P@5 | 33 | 35.76% | 35.15% | 32.73% | — |

McNemar Phase 3B: p = 1.0. McNemar traps vs word count: 16–0, p < 0.001.  
**Do not report 96%.** Cue split (traps): n=18 cue SVM 100% vs WC ~11%; n=22 no cue both 27.27%.

## Integrity rules for this branch

- Do not train on H001–H040.
- Do not change `models/svm_classifier.pkl` until a later phase on this branch, and then only under a new experiment ID.
- Do not retune thresholds on the 40-query P@5 set and then claim it as independent evidence.
- Oracle labels from these 40 judgments are **diagnostic only**, not training labels (leakage).
