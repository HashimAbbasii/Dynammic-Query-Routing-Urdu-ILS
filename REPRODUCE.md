# ULTRA Reproduction Guide

This guide is for an independent researcher. It describes how the frozen M0 study was produced and how far it can be reproduced from this repository.

It does **not** change official scores. Official metrics were copied from sealed Phase 8–12 reports.

Repository: https://github.com/HashimAbbasii/Dynammic-Query-Routing-Urdu-ILS  
**Submission branch:** `publication/plos-one-final`  
Canonical manuscript: `Papers/PLOS_ONE/Adaptive_dynamic_query_routing_for_Urdu_information_retrieval.tex` (printed title: Script-aware BM25 retrieval for Urdu and Roman Urdu news search)

Later exploratory work on `research/post-phase12` is **not** part of the official scores in this guide.

---

## 1. Scope

This guide covers:

1. The frozen script-aware BM25 system (**M0**).
2. How the 111,860-article retrieval collection was derived from a third-party news compilation.
3. How to verify the frozen corpus checksum.
4. How to re-run official retrieval code on a local copy of that corpus.
5. How official K, U, A1, and A2 numbers relate to repository files.

It does **not** cover retraining SVM routers, MiniLM/Chroma indexes, or other material under `archive/`. Those are historical and are not the official PLOS ONE system.

---

## 2. Frozen study definition

**Official retriever: M0**

- Unicode script detector (not an SVM).
- URDU, MIXED, and OTHER queries → Urdu-script Okapi BM25.
- ROMAN queries → Method D (BM25 over romanized documents).
- BM25 \(k_1 = 1.5\), \(b = 0.75\).
- Retrieve 50 documents; official cutoff is 5.
- Roman Urdu dictionary: `models/roman_urdu_dict_expanded.json` (198 keys).

Do not retune M0, routing, Method D, BM25 parameters, or the dictionary on K, U, or H001–H040.

**Official evaluations (do not average):**

| Evaluation | Set | Metric | Frozen result |
| --- | --- | --- | --- |
| Development / validation known-item | Phase 2 pool, n = 78 | ExactSource Hit@5 | 68/78 = 87.18% |
| Sealed known-item | K001–K040 | ExactSource Hit@5 | 27/40 = 67.50% |
| Sealed naturalistic, Annotator 1 | U001–U040 | Success@5 | 23/40 = 57.50% |

Annotator 2 (A2) is a **reliability analysis** of the same frozen U Top-5. A2 Success@5 = 26/40 = 65.00% does **not** replace 23/40.

---

## 3. Repository structure

| Path | Role |
| --- | --- |
| `experiments/phase5_roman_urdu/run_phase5.py` | M0 detector, BM25, Method D |
| `experiments/phase2_oracle/run_phase2_pipeline.py` | Method D character table (historical source of the table copied into `run_phase5.py`) |
| `experiments/phase12_new_unseen_evaluation/run_phase12.py` | Sealed K/U retrieval runner |
| `experiments/phase12_human_relevance/` | Annotator-1 protocol, qrels, official U metrics |
| `experiments/phase12_independent_annotation/` | Annotator-2 labels and agreement |
| `experiments/phase8_final_freeze/FINAL_SYSTEM_MANIFEST.json` | Freeze hashes and BM25 settings |
| `experiments/publication_audit/` | Dataset provenance notes and hash/reconstruct helpers |
| `models/roman_urdu_dict_expanded.json` | Frozen dictionary (in git) |
| `data/` | Local corpus location; **CSV files are gitignored** |
| `Papers/PLOS_ONE/` | Manuscript and Supporting Information |
| `archive/` | Historical SVM/MiniLM experiments; not official M0 |

---

## 4. Data source

The retrieval collection is a locally processed copy of a third-party Urdu news compilation.

| Record | Value |
| --- | --- |
| Compilation title | Urdu News Dataset 1M |
| Mendeley | V3, DOI **10.17632/834vsxnb99.3** |
| Kaggle | Saurabh Shahane, Urdu News Dataset, **Version 1** |
| Kaggle file | `urdu-news-dataset-1M.csv` |
| Local precursor | `data/urdu_news.csv`, **111,861** CSV records |
| Frozen collection | `data/clean_articles.csv`, **111,860** articles |

Kaggle acknowledgements (retrieved 6 September 2026) cite:

Hussain, Khalid; Mughal, Nimra; Ali, Irfan; Hassan, Saif; Daudpota, Sher Muhammad (2021), “Urdu News Dataset 1M”, Mendeley Data, V3, doi: 10.17632/834vsxnb99.3

The compilation title uses “1M”. The file used here has 111,861 precursor records. “1M” is the public title and a depositor description claim, not a verified row count of the local file.

A SHA-256 comparison between a **fresh** Kaggle or Mendeley download and the local precursor was **not** completed. Local precursor identity, when the file is present, has been hashed as:

`7662b6e8508ccb080bbb9adcb5678388a363a94f67fff44102551c7cc7926062` (276,791,832 bytes)

That hash is **not** a proof that a new download will match.

This project does **not** claim unrestricted redistribution of article text.

---

## 5. Data access restrictions

`data/*.csv` is listed in `.gitignore`. Cloning GitHub does **not** download the news corpus.

**Not in this repository, not in PLOS Supporting Information, not on Git LFS:**

- `data/clean_articles.csv` (~515 MB)
- `data/urdu_news.csv`

Redistribution permission for the underlying news article text has **not** been independently verified. Deposit pages currently display CC BY 4.0, and the Mendeley “Steps to reproduce” text also mentions non-commercial research with credit to the news source. Those statements were not reconciled here. See `experiments/publication_audit/DATASET_LICENSE_VERIFICATION.md`.

Researchers must obtain the source dataset from Kaggle and/or Mendeley under those providers’ terms.

No download CLI is recorded in this repository (**COMMAND NOT VERIFIED**). Typical access is a manual download of Kaggle Version 1 `urdu-news-dataset-1M.csv`, then a local copy/rename to `data/urdu_news.csv`. Do not overwrite a known-good local precursor until hashes are compared.

Mendeley also has V4 (`10.17632/834vsxnb99.4`). Kaggle cited **V3**. Using V4 without a hash check is not a reproduction of this paper’s corpus.

---

## 6. Corpus reconstruction

Documented transform (historical notebook `archive/historical_experiments/notebooks/01_preprocessing.ipynb`):

1. `pd.read_csv(..., encoding="utf-8-sig", encoding_errors="replace")`
2. Set columns to `Index`, `Headline`, `News Text`, `Category`, `Date`, `URL`, `Source`, `News length`
3. `df.dropna()` then `reset_index(drop=True)`
4. `combined_text = Headline + ' ' + News Text`
5. `to_csv(..., index=False, encoding="utf-8-sig")`

No category filter, no duplicate drop, no Unicode normalization.

**Why 111,861 → 111,860:** the local precursor’s last record is truncated (3 of 8 fields; `Index` = 111860; no trailing newline). `dropna()` drops that incomplete row.

A complete public file, if one exists, would not necessarily drop a row. Identity depends on matching this truncated precursor **or** matching the frozen SHA-256.

**Frozen identity (do not “fix” a mismatch by editing the freeze):**

- File: `data/clean_articles.csv`
- Rows: 111,860
- Bytes: 540,050,203
- SHA-256: `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231`

The archived notebook uses `../data/` relative to a former `notebooks/` layout. Running it from `archive/historical_experiments/notebooks/` does **not** write repository `data/`. Equivalent steps that **refuse to overwrite** the frozen file:

```
python experiments/publication_audit/reconstruct_corpus.py --input data/urdu_news.csv --output data/clean_articles.reconstructed.csv
python experiments/publication_audit/verify_corpus_hash.py --path data/clean_articles.reconstructed.csv
```

Require `status: MATCH`. `pandas.DataFrame.to_csv` is not guaranteed bit-identical across pandas versions. Row count 111,860 is necessary but not sufficient.

If you already have the frozen file locally:

```
python experiments/publication_audit/verify_corpus_hash.py
```

---

## 7. Environment

Recorded at Phase 12 preflight (`experiments/phase12_new_unseen_evaluation/artifacts/preflight.json`):

| Item | Value | Status |
| --- | --- | --- |
| Python | 3.13.9 (Anaconda, 64-bit Windows) | **Verified** in preflight.json and the manuscript |
| numpy | 2.3.5 | **Verified** in preflight.json |
| pandas | 2.3.3 | **Verified** in preflight.json |
| matplotlib | 3.10.6 | **Verified** on the same Anaconda 3.13.9 interpreter that produced preflight.json; **not** written into the freeze JSON |
| scikit-learn | 1.7.2 | **Verified** for A2 kappa only (`AGREEMENT.md`); not used by M0 retrieval |
| SciPy | 1.16.3 | **Stated in the manuscript** for Clopper–Pearson intervals; not used by M0 retrieval |
| torch / transformers / chromadb / sentence-transformers / urduhack / ftfy | — | **Not required** for official M0 / Phase 12 |

There was no `requirements.txt` at freeze time. `requirements.txt` at the repository root pins the verified numpy/pandas versions and lists matplotlib without a invented pin.

---

## 8. Installation

From the repository root, with a Python 3.13 interpreter if you have one:

```
python -m venv .venv
```

Windows:

```
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

macOS / Linux:

```
source .venv/bin/activate
python -m pip install -r requirements.txt
```

The freeze used Anaconda Python 3.13.9. A `conda create -n ultra python=3.13.9` line is **not** recorded in historical project files. If 3.13.9 is unavailable, install the packages in `requirements.txt` and treat interpreter mismatch as unverified.

Optional extras (not M0 retrieval):

```
python -m pip install scikit-learn==1.7.2 scipy==1.16.3
```

---

## 9. Reproduction workflow

1. **Clone the git repository.** This does not include the news CSV.
2. **Install** the environment in §8.
3. **Obtain** Kaggle Version 1 `urdu-news-dataset-1M.csv` and/or the Mendeley V3 deposit under provider terms. Place a local copy at `data/urdu_news.csv` if you intend to reconstruct.
4. **Optional precursor check:** SHA-256 of the local precursor previously used here is `7662b6e8508ccb080bbb9adcb5678388a363a94f67fff44102551c7cc7926062`. A different download is not this paper’s input.
5. **Reconstruct** a candidate file with `reconstruct_corpus.py`, **or** use an existing local `data/clean_articles.csv` that you already trust.
6. **Verify** with `verify_corpus_hash.py`. Require MATCH on SHA-256 `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231`.
7. **Confirm** the dictionary is present: `models/roman_urdu_dict_expanded.json` (198 keys; SHA-256 `30c3f61a64ec641abbb3acdbc7a8bcaf197f0238f1bf9e76c2c7ce8e590f86a3`).
8. **Retrieval (optional verification run):** from the repository root:

```
python experiments/phase12_new_unseen_evaluation/run_phase12.py
```

That command exists as `if __name__ == "__main__": main()` in `run_phase12.py`. It **will write** Top-50 dumps in the Phase 12 folder. Compare printed K ExactSource counts to `experiments/phase12_new_unseen_evaluation/K_RESULTS.md`. Do not treat a new run as a replacement official table. Restore git-tracked dumps if you do not mean to keep new files.

9. **Do not re-label U.** Official A1 labels are `experiments/phase12_human_relevance/U_QRELS.csv` and `U_PER_QUERY.csv`. Official Success@5 remains 23/40.

10. **A2 is optional reliability only.** See `experiments/phase12_independent_annotation/AGREEMENT.md`. Do not average A1 and A2.

Full Phase 5 method-selection (`python experiments/phase5_roman_urdu/run_phase5.py`) is the historical comparison that **selected** Method D. Re-running it is not required to read official PLOS scores. That script also expects `experiments/phase4b_retrieval_benchmark/QUERY_LEVEL_COMPARISON.csv`, which now lives at `archive/historical_experiments/phase4b_retrieval_benchmark/QUERY_LEVEL_COMPARISON.csv`. Official M0 scores are the sealed reports, not a new Phase 5 run.

---

## 10. Official evaluation

| Piece | What it is | Primary files | Official? |
| --- | --- | --- | --- |
| Development / freeze pool | Known-item ExactSource on Phase 2 dev + internal_val, n = 78 | `experiments/phase8_final_freeze/`, `results/FINAL_RESULTS.md` | Yes: 68/78 = 87.18%; nDCG@5 = 0.8107; MRR = 0.797 |
| Phase 12 K | Sealed known-item ExactSource | `queries_k.csv`, `K_RESULTS.md` | Yes: Hit@1 = 20/40; Hit@5 = 27/40 = 67.50%; Hit@10 = 28/40; Hit@50 = 30/40 |
| Phase 12 U retrieval | Frozen Top-5 dump for human labels | `U_TOP5_FOR_ANNOTATION.csv` | Retrieval artifact; not a usefulness rate by itself |
| A1 | Annotator 1 human Success@5 on that dump | `U_QRELS.csv`, `U_PER_QUERY.csv`, `PHASE12_HUMAN_RESULTS.md` | **Yes: 23/40 = 57.50%** |
| A2 | Independent second annotation of the same 200 documents | `AGREEMENT.md`, `A1_A2_PER_QUERY.csv` | Reliability only: 26/40 = 65.00%. Does not replace A1 |

H001–H040 are diagnostic / burned. They are not the official unseen tests.

---

## 11. Frozen results

Documentation values only. Do not recompute them into new official numbers.

**M0 development / validation (n = 78)**

- ExactSource Hit@5 = 68/78 = 87.18%
- nDCG@5 = 0.8107
- MRR = 0.797

**Phase 12 K (n = 40)**

- Hit@1 = 20/40
- Hit@5 = 27/40 = 67.50%
- Hit@10 = 28/40
- Hit@50 = 30/40

**Phase 12 U, Annotator 1 (official)**

- Success@5 = 23/40 = 57.50%
- P@5 = 0.2050
- nDCG@5 = 0.6460
- MRR = 0.4542

**A2 (reliability only)**

- Success@5 = 26/40 = 65.00%
- Five-way agreement = 135/200 = 67.50%
- Five-way Cohen’s kappa = 0.5490
- Binary agreement = 169/200 = 84.50%
- Binary kappa = 0.6816

---

## 12. Expected limitations

- The third-party article corpus is not redistributed.
- Exact provider-download SHA match was not completed.
- Reproduction of retrieval requires obtaining a source file that reconstructs to the frozen SHA-256, or an already-held copy of `clean_articles.csv`.
- Provider-side dataset changes (including Mendeley V4) may prevent reconstruction.
- pandas `to_csv` may yield a different byte string at the same row count.
- How a Mendeley “1M” description became a ~111,861-record Kaggle file is **not** explained in this repository.
- Original ULTRA code and documentation are under the MIT License (`LICENSE`). That grant does **not** license the third-party news corpus.

---

## 13. Troubleshooting

Issues actually found in this repository:

| Issue | Effect | What to do |
| --- | --- | --- |
| `data/clean_articles.csv` missing after clone | Hash check prints `status: MISSING`; Phase 12 cannot retrieve | Obtain source; reconstruct; or use a local frozen copy. Not a git failure. |
| Archived preprocessing notebook `../data/` paths | Notebook does not write live `data/` | Use `reconstruct_corpus.py`, or run equivalent pandas steps against repository `data/` |
| Former `validate/dual_index_routing/retrieve.py` import | Would fail on a clean clone and would pull MiniLM/SVM if pointed at the archive | Official M0 no longer imports that package. Method B lookup lives in `run_phase5.py`. The archive tree remains historical. |
| `run_phase5.py` full experiment needs Phase 4B CSV at a live path | Historical method-selection rerun incomplete | Dense comparison file is under `archive/historical_experiments/phase4b_retrieval_benchmark/`. Official PLOS scores do not require re-running Phase 5. |
| Hard-coded developer `ROOT` paths (fixed to relative paths) | Agreement/scoring scripts failed off this machine | Use current `Path(__file__).resolve().parents[2]` versions. Do not edit qrels. |
| Re-running `run_phase12.py` | Overwrites retrieval dumps in the Phase 12 folder | Compare to sealed reports; restore git-tracked files if needed |
| Hash MISMATCH after reconstruct | Not the frozen collection | Do not overwrite `clean_articles.csv` to force a match. Record the new hash. |

---

## 14. Citation

**Dataset (as cited by Kaggle Version 1 acknowledgements / Mendeley V3):**

Hussain, Khalid; Mughal, Nimra; Ali, Irfan; Hassan, Saif; Daudpota, Sher Muhammad (2021). Urdu News Dataset 1M. Mendeley Data, V3. https://doi.org/10.17632/834vsxnb99.3

**Kaggle compilation:**

Shahane, Saurabh. Urdu News Dataset. Kaggle, Version 1. https://www.kaggle.com/datasets/saurabhshahane/urdu-news-dataset

**This repository:**

https://github.com/HashimAbbasii/Dynammic-Query-Routing-Urdu-ILS

**Manuscript:** `Papers/PLOS_ONE/Adaptive_dynamic_query_routing_for_Urdu_information_retrieval.tex`

Supporting reconstruction notes without article text: `Papers/PLOS_ONE/supporting_information/S3_file.md`

---

## License (not a grant of news-text rights)

Original ULTRA code and documentation are released under the MIT License. See the root `LICENSE` file.

That software license does **not** license `data/clean_articles.csv`, `data/urdu_news.csv`, underlying third-party article text, or news headlines/snippets in evaluation files. `plos2025.bst` remains under LPPL 1.3 or later. PyPI dependencies retain their own licenses.
