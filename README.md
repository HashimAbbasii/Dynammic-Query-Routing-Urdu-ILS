# ULTRA

**Adaptive Script-Aware Information Retrieval for Urdu and Roman Urdu**

Frozen lexical retrieval for Urdu news search. Queries are routed by script: native-script and mixed queries search an Urdu BM25 index; Roman Urdu queries search a Method D romanized-document BM25 index.

---

## Overview

Urdu users type Perso-Arabic script, informal Roman Urdu, or both. A single native-script index misses Roman queries even when the article exists. ULTRA (this repository) freezes a **script-aware BM25** pipeline over 111,860 news articles and evaluates it under three protocols that must not be mixed: development/validation known-item recovery, new known-item recovery, and naturalistic human usefulness.

The official frozen system is **M0**. It is not an SVM router and not a MiniLM dual-index retriever. Those earlier studies remain in the repository as historical evidence.

## Key contribution

- Unicode script detection (Urdu vs Latin letter counts)
- Urdu BM25 for URDU, MIXED, and OTHER queries
- Method D romanized-document BM25 for ROMAN queries
- One frozen routing rule, one hashed corpus, one hashed dictionary
- Reproducible evaluation: ExactSource Hit@5 for known-item search, human Success@5 for naturalistic queries

## Final frozen system (M0)

| Component | Specification |
| --- | --- |
| Detector | Unicode Urdu vs Latin counts (`detect_script`) |
| URDU / MIXED / OTHER | Urdu BM25 over article text |
| ROMAN | Method D BM25 over romanized documents |
| BM25 | \(k_1 = 1.5\), \(b = 0.75\) |
| Retrieval depth | Top-50 internally; official cutoff Top-5 |
| Corpus | `data/clean_articles.csv` · **n = 111,860** |
| Dictionary | `models/roman_urdu_dict_expanded.json` · **198 keys** |

Query-side expansions **M1–M4** were tested on the development/validation pool. All scored 68/78 ExactSource Hit@5. **M0 was not replaced.**

## Evaluation

These three results answer different questions. They are not interchangeable and must not be averaged.

| Evaluation | Dataset | Metric | Result |
| --- | --- | --- | --- |
| Development / validation known-item | Phase 2, n = 78 | ExactSource Hit@5 | **68/78 (87.18%)** |
| New known-item | K001–K040 | ExactSource Hit@5 | **27/40 (67.50%)** |
| New naturalistic (human) | U001–U040 | Human Success@5 | **23/40 (57.50%)** |

- **87.18%** is title-derived known-item recovery on the freeze pool. It is not human relevance and not unseen naturalistic performance.
- **67.50%** is ExactSource Hit@5 on independently sealed known-item queries (Hit@1 / @10 / @50 = 50.00% / 70.00% / 75.00%).
- **57.50%** is human Success@5: at least one A (relevant) or B (partially relevant) document in the Top-5. Secondary U metrics: conservative P@5 = 0.2050, nDCG@5 = 0.6460, MRR = 0.4542. This is **not** ExactSource Hit@5.

## Human evaluation

U001–U040 are naturalistic information needs with no gold article. Annotators labeled Top-5 documents. Success@5 = 23/40. In this sealed sample, Urdu-script queries succeeded in 17/18 cases, Roman in 6/18, and mixed in 0/4 (n = 4 is descriptive only).

## Repository structure

```
data/                 Corpus (clean_articles.csv)
models/               Frozen Roman Urdu dictionary
experiments/
  phase5_roman_urdu/  Detector, BM25, Method D (M0 implementation)
  phase8_final_freeze/ Frozen configuration and hashes
  phase9_heldout_evaluation/
  phase11_improvement/ M0–M4 ablation (M0 remains official)
  phase12_new_unseen_evaluation/  Sealed K/U queries and retrieval dumps
  phase12_human_relevance/        U qrels and Success@5
Thesis_Paper/
  IEEE_M0/            Official IEEE-style M0 manuscript
  Clause_1_Formate/PLOS_ULTRA_paper/  Official PLOS ONE M0 manuscript
```

Historical SVM / MiniLM (Layer A) code and reports remain under `validate/` and earlier experiment folders. They are not the official retriever.

## Reproducibility

| Artifact | Value |
| --- | --- |
| Corpus SHA-256 | `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231` |
| Dictionary SHA-256 | `30c3f61a64ec641abbb3acdbc7a8bcaf197f0238f1bf9e76c2c7ce8e590f86a3` |
| Freeze manifest | `experiments/phase8_final_freeze/FINAL_SYSTEM_MANIFEST.json` |
| Detector / BM25 | `experiments/phase5_roman_urdu/run_phase5.py` |
| Phase 12 protocol | `experiments/phase12_new_unseen_evaluation/PHASE12_SEALED_PROTOCOL.md` |
| Official interpretation | `experiments/FINAL_EXPERIMENTAL_RESULTS_ANALYSIS.md` |

The scientific freeze is closed. Do not retune M0, the dictionary, routing, or Method D on K, U, or H001–H040.

## Papers

- **PLOS ONE (M0):** `Thesis_Paper/Clause_1_Formate/PLOS_ULTRA_paper/` · package `Thesis_Paper/ULTRA_PLOS_ONE_FINAL_SUBMISSION.zip`
- **IEEE-style (M0):** `Thesis_Paper/IEEE_M0/` · package `Thesis_Paper/ULTRA_IEEE_M0_FINAL_SUBMISSION.zip`

`Thesis_Paper/IEEE/` is a **different** historical study (SVM + MiniLM dual-index). Do not quote it as M0.

## Thesis

Extended documentation of the same freeze, including labeled historical Layer A chapters, is in `Thesis_Paper/Air_Thesis_Formate/`.

## Limitations

- Roman Urdu is weaker than native-script Urdu on sealed tests (U Success@5: 6/18 vs 17/18).
- Unseen naturalistic human Success@5 is **57.50%**, not 87.18%.
- M0 is lexical BM25. It does not rewrite queries.
- 87.18% is development/validation known-item ExactSource Hit@5 only.
- K and U each have n = 40; mixed-script n = 4; one annotator on U.

## Citation

If you use this freeze, cite the manuscripts in `Thesis_Paper/` and report the three official metrics separately.
