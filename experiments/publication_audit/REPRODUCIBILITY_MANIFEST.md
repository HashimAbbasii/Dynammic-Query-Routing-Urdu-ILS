# Reproducibility Manifest

Inspection date: 6 September 2026  
Branch: `publication/plos-one-final`  
Policy: this project does **not** currently publicly redistribute `data/clean_articles.csv` or `data/urdu_news.csv`. Redistribution permission for the underlying third-party news text has not been independently verified.

This file documents identity, pipeline, and commands that can be **verified from the repository**. It does not change the frozen corpus or scientific results.

---

## Dataset

| Field | Value | Status |
| ----- | ----- | ------ |
| Original dataset name (Kaggle page) | Urdu News Dataset | Verified on https://www.kaggle.com/datasets/saurabhshahane/urdu-news-dataset (6 Sep 2026) |
| Kaggle compiler | Saurabh Shahane | Verified on that page |
| Kaggle file name | `urdu-news-dataset-1M.csv` | Verified on that page |
| Kaggle version shown | Version 1 | Verified on that page |
| Kaggle displayed size | 276.79 MB | Verified; local `urdu_news.csv` is 276,791,832 bytes (276.79 MB decimal) |
| Acknowledged upstream name | Urdu News Dataset 1M | Kaggle Acknowledgements; Mendeley |
| Original source (DOI cited by Kaggle) | Mendeley Data, V3, **10.17632/834vsxnb99.3** | Verified on Kaggle page and DataCite |
| Mendeley URL | https://data.mendeley.com/datasets/834vsxnb99/3 | Verified |
| Expected local input filename | `data/urdu_news.csv` | Used by the historical preprocessing notebook |
| Expected input row count | 111,861 CSV data records | Verified locally; Kaggle explorer listed 111,861 under URL |
| Input SHA-256 | `7662b6e8508ccb080bbb9adcb5678388a363a94f67fff44102551c7cc7926062` | Computed locally on `data/urdu_news.csv` in a prior audit; **not** compared to a fresh Kaggle/Mendeley download |
| Byte-identical match to Kaggle/Mendeley | NOT VERIFIED | This package did not download the public files |

Mendeley/Kaggle prose says “above 1 Million” stories. The Kaggle file actually previewed, and the local precursor, are ~111,861 records. How a 1M dump became this 111k file is **not in this repository**.

---

## Final corpus

| Field | Value |
| ----- | ----- |
| Filename | `data/clean_articles.csv` |
| Rows (data, excluding header) | **111,860** |
| Bytes | **540,050,203** |
| SHA-256 | **`8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231`** |
| Encoding | UTF-8 with BOM (`utf-8-sig`) |
| Columns | `Index`, `Headline`, `News Text`, `Category`, `Date`, `URL`, `Source`, `News length`, `combined_text` |
| Git / GitHub | Not shipped (`data/*.csv` gitignored) |
| Redistribution by this project | Not claimed |

Also frozen (not the corpus, but required for M0):

| Artifact | Path | SHA-256 | n |
| -------- | ---- | ------- | - |
| Roman dictionary | `models/roman_urdu_dict_expanded.json` | `30c3f61a64ec641abbb3acdbc7a8bcaf197f0238f1bf9e76c2c7ce8e590f86a3` | 198 keys |
| K queries | `experiments/phase12_new_unseen_evaluation/queries_k.csv` | `124e452693f98baedf510618240c154df68d56b6b7a37ed085a6512c13d13ff6` | 40 |
| U queries | `experiments/phase12_new_unseen_evaluation/queries_u.csv` | `684fd1e19eddb717f5897d869ef0ca0ed586316c5a7e1d2d23006e0748fc53b9` | 40 |

---

## Pipeline

```
Urdu News Dataset 1M (Mendeley DOI 10.17632/834vsxnb99.3)
        → acquisition
Kaggle Version 1 file urdu-news-dataset-1M.csv
        → acquisition (rename / copy; not scripted in this repo)
data/urdu_news.csv  (111,861 records)
        → preprocessing / filtering
archive/historical_experiments/notebooks/01_preprocessing.ipynb
data/clean_articles.csv  (111,860 rows; SHA-256 8992a6ac…)
        → M0 index + evaluation
experiments/phase5_roman_urdu/run_phase5.py
experiments/phase12_new_unseen_evaluation/run_phase12.py
```

| Arrow | Exact script | What it does |
| ----- | ------------ | ------------ |
| Mendeley → Kaggle file | **none in this repository** | Kaggle page cites the Mendeley V3 DOI. No ULTRA download script. |
| Kaggle file → `urdu_news.csv` | **none in this repository** | No documented copy/rename command. **COMMAND NOT VERIFIED.** |
| `urdu_news.csv` → `clean_articles.csv` | `archive/historical_experiments/notebooks/01_preprocessing.ipynb` | Load UTF-8-SIG with `encoding_errors='replace'`; set eight column names; `dropna()`; `reset_index(drop=True)`; `combined_text = Headline + ' ' + News Text`; `to_csv(..., index=False, encoding='utf-8-sig')`. |
| Deduplication | **none** | Not performed. |
| `clean_articles.csv` → M0 BM25 | `experiments/phase5_roman_urdu/run_phase5.py` | `pd.read_csv(..., encoding="utf-8-sig")`; field `combined_text`; Okapi BM25 k1=1.5, b=0.75; script detector; Method D for ROMAN. |
| Frozen K/U retrieval | `experiments/phase12_new_unseen_evaluation/run_phase12.py` | Imports `run_phase5`; preflight hashes; retrieve Top-50. |

### Filtering / cleaning rules (from the notebook, not inferred)

- **Filtering:** `df.dropna()` only. No category filter, no date filter, no source filter, no length cutoff.
- **Cleaning:** concatenate headline and body with a single space. No Unicode NFKC, no ye/he/kaf folding, no stemming, no stopword list, no HTML strip (stated in the manuscript Corpus subsection and `archive/historical_experiments/phase3_retrieval/ARCHITECTURE_AUDIT.md`).
- **Deduplication:** none.
- **Column transformations:** overwrite `.columns` with the eight names; add `combined_text`.
- **Row-count change 111,861 → 111,860:** the last CSV record in `urdu_news.csv` has **3 fields** (`Index`, `Headline`, `News Text`) instead of 8. Missing fields: `Category`, `Date`, `URL`, `Source`, `News length`. Index value of that record is `111860`. The file does not end with a newline; the last record is truncated. `dropna()` therefore drops that incomplete row. See `REPRODUCE_DATASET.md`.

### Determinism

| Step | Deterministic? |
| ---- | -------------- |
| Public download | Depends on the host keeping the same bytes. Not pinned by SHA in original project docs. |
| Notebook `encoding_errors='replace'` | Replacement of invalid UTF-8 is defined, but a different source file can diverge. |
| `dropna()` | Deterministic for a given pandas NA interpretation of a truncated last row. |
| `to_csv` | May differ across pandas versions (quoting/lineterminators). **Bit-identity of a reconstructed CSV is not guaranteed** even if row count matches. |
| Frozen file on disk | Fixed bytes; SHA-256 is the authority. |
| M0 BM25 given the frozen CSV | Specified in `run_phase5.py` (no RNG on the official retrieval path). |

### Dependencies (as used, not a pinned env file)

There is **no** `requirements.txt` / `environment.yml`. Observed from code:

- Preprocessing notebook: `pandas` (also imports `transformers` and `chromadb` in an unused first cell).
- M0 / Phase 12: `pandas`, `numpy`; Phase 5 also `matplotlib`.
- Manuscript states Python 3.13.9 (Anaconda, 64-bit Windows). Not pinned in an env file.

---

## Reproduction commands

Only commands that appear in the repository or that this package itself defines.

### Obtain source dataset

**COMMAND NOT VERIFIED.**  
No clone-time download script, Kaggle CLI invocation, or Mendeley URL-to-file command exists in this repository.

### Reconstruct `clean_articles.csv`

**COMMAND NOT VERIFIED.**  
The only transformation is Jupyter cells in `archive/historical_experiments/notebooks/01_preprocessing.ipynb`. Those cells use `../data/urdu_news.csv` and `../data/clean_articles.csv`, which matched the **old** `notebooks/` layout, not the current `archive/historical_experiments/notebooks/` path. Re-running the notebook from its archived location would not write the live `data/` folder without path edits. This package does **not** invent a replacement CLI, and must not overwrite the frozen CSV.

### Verify frozen corpus identity (this package)

From the repository root, if `data/clean_articles.csv` is present locally:

```
python experiments/publication_audit/verify_corpus_hash.py
```

Optional explicit path:

```
python experiments/publication_audit/verify_corpus_hash.py --path data/clean_articles.csv
```

Expected print: `status: MATCH` and SHA-256 `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231`.

A researcher who reconstructs a candidate file elsewhere should pass that path to `--path` and require **MATCH**. Do not replace the frozen file on a MATCH failure; report the mismatch.

### M0 / evaluation (documented in-repo)

From `experiments/phase5_roman_urdu/README.md`:

```
python experiments/phase5_roman_urdu/run_phase5.py
```

**Caveat (not a command invention):** `run_phase5.py` inserts `validate/dual_index_routing` and imports `transliterate_roman`. That module now lives at `archive/historical_experiments/validate/dual_index_routing/retrieve.py`. A clean clone may fail before retrieval.

Phase 12 runner file: `experiments/phase12_new_unseen_evaluation/run_phase12.py` (`if __name__ == "__main__": main()`). **Documented shell command: COMMAND NOT VERIFIED** (no README line states the `python ...` invocation). Do not rerun Phase 12 to change frozen scores.

Phase 11 (not official M0 replacement), from `experiments/phase11_improvement/README.md`:

```
python experiments/phase11_improvement/run_phase11_ablation.py
```

---

## Verification

Primary check: **SHA-256 of the reconstructed or local CSV must equal**

`8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231`

Secondary checks (same frozen identity):

- size 540,050,203 bytes
- 111,860 data rows

Use `verify_corpus_hash.py`. Phase 12 preflight also compares this SHA (`EXPECTED_CORPUS_SHA` in `run_phase12.py`) and n=111860. Row count alone is **not** sufficient if pandas `to_csv` produced different bytes.

If a newly downloaded Kaggle/Mendeley file differs from local `urdu_news.csv`, stop. Do not “fix” the frozen corpus. Record the new source hash and treat identity as unmatched until a human decides.

---

## Required inputs for a new researcher

| Class | Items |
| ----- | ----- |
| A. Publicly obtainable | Kaggle dataset page; Mendeley DOI 10.17632/834vsxnb99.3; git-tracked code, dictionary, query CSVs, qrels, protocols, this audit folder |
| B. Third-party inputs | The news CSV hosted by Kaggle/Mendeley (account may be required to download) |
| C. Project-generated outputs | `clean_articles.csv`; BM25 indexes (built at run time, not shipped); Phase 12 retrieval dumps; A1/A2 labels |
| D. Not currently redistributed by this project | `data/clean_articles.csv`, `data/urdu_news.csv` (gitignored; redistribution permission not independently verified) |
