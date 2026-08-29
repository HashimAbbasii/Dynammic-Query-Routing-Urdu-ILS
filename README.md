# ULTRA

**Adaptive Script-Aware Information Retrieval for Urdu and Roman Urdu**

Frozen lexical retrieval for Urdu news search. A Unicode detector routes each query to an Urdu BM25 index or a Method D romanized-document BM25 index.

---

## Overview

Urdu users type Perso-Arabic script, informal Roman Urdu, or both. A single native-script index misses Roman queries even when the article exists. This repository freezes a **script-aware BM25** pipeline (**M0**) over 111,860 news articles and reports three evaluations that must not be mixed.

M0 is not an SVM router and not a MiniLM dual-index retriever. Earlier SVM/MiniLM work is in `archive/`.

## Architecture (M0)

| Component | Specification |
| --- | --- |
| Detector | Unicode Urdu vs Latin letter counts |
| URDU / MIXED / OTHER | Urdu BM25 over article text |
| ROMAN | Method D BM25 over romanized documents |
| BM25 | \(k_1 = 1.5\), \(b = 0.75\) |
| Depth | Top-50 retrieved; official cutoff Top-5 |
| Corpus | `data/clean_articles.csv` · n = 111,860 |
| Dictionary | `models/roman_urdu_dict_expanded.json` · 198 keys |

Query-side expansions M1–M4 did not improve n=78 ExactSource Hit@5. **M0 remains official.**

## Evaluation

These metrics answer different questions. Do not average them.

| Evaluation | Dataset | Metric | Result |
| --- | --- | --- | --- |
| Development / validation known-item | Phase 2, n = 78 | ExactSource Hit@5 | **68/78 (87.18%)** |
| New known-item | K001–K040 | ExactSource Hit@5 | **27/40 (67.50%)** |
| New naturalistic (human) | U001–U040 | Human Success@5 | **23/40 (57.50%)** |

- **87.18%** is title-derived known-item recovery on the freeze pool — not human usefulness, not unseen naturalistic performance.
- **67.50%** is ExactSource Hit@5 on sealed known-item queries (Hit@1/@10/@50 = 50.00% / 70.00% / 75.00%).
- **57.50%** is human Success@5 (at least one A or B in the Top-5). Secondary: P@5 = 0.2050, nDCG@5 = 0.6460, MRR = 0.4542. **Not** ExactSource Hit@5.

Full write-up: `results/FINAL_RESULTS.md`.

## Repository structure

```
data/            Official corpus (clean_articles.csv)
models/          Frozen Roman Urdu dictionary
src/             Map to M0 Python entry points (code not relocated)
experiments/     M0 implementation + Phase 8–12 evidence
results/         Official result summaries
Thesis/FINAL/    Final AU thesis (DOCX + markdown)
Papers/PLOS_ONE/ Final M0 PLOS source and submission ZIP
Papers/IEEE/     Final M0 IEEE source and submission ZIP
docs/            Freeze status, reproducibility, interpretation
archive/         Historical SVM/MiniLM papers, backups, notebooks
```

## Papers and thesis

- Thesis: `Thesis/FINAL/Hashim_Shazad_243259_AU_Thesis_ULTRA.docx`
- PLOS ONE (M0): `Papers/PLOS_ONE/FINAL/` · ZIP `Papers/PLOS_ONE/SUBMISSION_PACKAGE/ULTRA_PLOS_ONE_FINAL_SUBMISSION.zip`
- IEEE (M0): `Papers/IEEE/FINAL/` · ZIP `Papers/IEEE/SUBMISSION_PACKAGE/ULTRA_IEEE_M0_FINAL_SUBMISSION.zip`

The MiniLM dual-index IEEE paper is historical: `archive/historical_papers/IEEE_MiniLM/`.

## Reproducibility

| Artifact | Location |
| --- | --- |
| Corpus SHA-256 | `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231` |
| Dictionary SHA-256 | `30c3f61a64ec641abbb3acdbc7a8bcaf197f0238f1bf9e76c2c7ce8e590f86a3` |
| Freeze manifest | `experiments/phase8_final_freeze/FINAL_SYSTEM_MANIFEST.json` |
| Detector / BM25 | `experiments/phase5_roman_urdu/run_phase5.py` |
| Method D char table | `experiments/phase2_oracle/run_phase2_pipeline.py` |
| Sealed K/U | `experiments/phase12_new_unseen_evaluation/` |
| U qrels | `experiments/phase12_human_relevance/` |
| Notes | `docs/REPRODUCIBILITY.md` |

Do not retune M0, the dictionary, routing, or Method D on K, U, or H001–H040.

## Limitations

- Roman Urdu is weaker than native-script Urdu (U Success@5: 6/18 vs 17/18).
- Naturalistic human Success@5 is **57.50%**, not 87.18%.
- M0 is lexical BM25 and does not rewrite queries.
- K and U each have n = 40; mixed n = 4; one U annotator.

## Archive

`archive/` holds Layer A SVM/MiniLM material, old paper zips, thesis backups, and notebooks. Do not quote it as official M0 retrieval.
