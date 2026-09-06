# Reproduce the frozen ULTRA news corpus

This guide is for researchers who want the **same 111,860-article file** used in the frozen M0 experiments. It does not authorize public rehosting of that file.

Redistribution permission for the underlying third-party news text has not been independently verified. This project **does not currently claim unrestricted redistribution** and **does not upload** `clean_articles.csv` or `urdu_news.csv`.

Official frozen identity:

- `data/clean_articles.csv`
- 111,860 rows
- 540,050,203 bytes
- SHA-256 `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231`

Do not modify that file to “improve” a hash mismatch.

---

## 1. Where the original third-party dataset comes from

Two public records, linked on the Kaggle page:

1. **Kaggle — Urdu News Dataset** (compiler: Saurabh Shahane)  
   https://www.kaggle.com/datasets/saurabhshahane/urdu-news-dataset  
   File shown: `urdu-news-dataset-1M.csv`, Version 1, 276.79 MB.

2. **Mendeley — Urdu News Dataset 1M** (Kaggle acknowledgement cites V3)  
   DOI **10.17632/834vsxnb99.3**  
   https://data.mendeley.com/datasets/834vsxnb99/3  

Kaggle acknowledgements (retrieved 6 September 2026) cite:

Hussain, Khalid; Mughal, Nimra; Ali, Irfan; Hassan, Saif; Daudpota, Sher Muhammad (2021), “Urdu News Dataset 1M”, Mendeley Data, V3, doi: 10.17632/834vsxnb99.3

This repository does **not** contain a download of those hosts. Local `data/urdu_news.csv` matches the Kaggle listing on **displayed size (276.79 MB), eight column names, and 111,861 records**. A SHA-256 comparison to a fresh Kaggle or Mendeley download was **not** performed in this package.

Deposit pages currently display CC BY 4.0. The Mendeley “Steps to reproduce” text also says scraped news was found to be usable for **non-commercial research only** with credit to the news source. Those statements were not reconciled here. See `DATASET_LICENSE_VERIFICATION.md`.

---

## 2. The cleaned corpus is not redistributed by this project

`data/*.csv` is gitignored. GitHub `publication/plos-one-final` `data/` contains only `README.md` and `training_queries_real.py`. There is no GitHub Release asset for the CSV.

A clone of the git repository is **not** enough to obtain `clean_articles.csv`.

---

## 3. Why public redistribution is not claimed

Redistribution permission for the underlying third-party news text has not been independently verified. The articles originate from named news organizations present in the `Source` column of the frozen CSV. A CC BY badge on a compiler’s deposit page is not treated here as proof that this project may rehost full article text.

This is a documentation choice, not a finding that redistribution is “illegal.”

---

## 4. How to obtain the source independently

1. Open the Kaggle URL above (a Kaggle account is typically required to download).
2. Download **Version 1** of `urdu-news-dataset-1M.csv` if it is still the listed file.
3. Optionally also record the Mendeley V3 DOI landing page, in case the Kaggle mirror changes.
4. Place the file locally as `data/urdu_news.csv` **without overwriting** a known-good copy until hashes are compared.

**COMMAND NOT VERIFIED** for any `kaggle datasets download ...` or `curl` line: none exists in this repository.

After download, compute SHA-256 of your file. The local precursor previously hashed as:

`7662b6e8508ccb080bbb9adcb5678388a363a94f67fff44102551c7cc7926062`

If your download differs, you do **not** have the same input this project used. Do not force it to match by editing `clean_articles.csv`.

---

## 5. Which project scripts transform it

| Stage | Script | Live publication-path CLI? |
| ----- | ------ | -------------------------- |
| Download | none | COMMAND NOT VERIFIED |
| 111,861 records → 111,860 articles + `combined_text` | `archive/historical_experiments/notebooks/01_preprocessing.ipynb` | COMMAND NOT VERIFIED (Jupyter cells; relative paths assume old `notebooks/` layout) |
| Hash check | `experiments/publication_audit/verify_corpus_hash.py` | Yes (this folder) |
| M0 retrieval implementation | `experiments/phase5_roman_urdu/run_phase5.py` | Documented: `python experiments/phase5_roman_urdu/run_phase5.py` |
| Sealed K/U runner | `experiments/phase12_new_unseen_evaluation/run_phase12.py` | File exists; documented shell command COMMAND NOT VERIFIED |

---

## 6. How to reproduce the 111,860-row corpus

### What the notebook actually does

Saved cells in `01_preprocessing.ipynb`:

1. `pd.read_csv("../data/urdu_news.csv", encoding="utf-8-sig", encoding_errors="replace")`
2. `df.columns = ['Index', 'Headline', 'News Text', 'Category', 'Date', 'URL', 'Source', 'News length']`
3. `df = df.dropna()` then `df = df.reset_index(drop=True)`
4. `df['combined_text'] = df['Headline'] + ' ' + df['News Text']`
5. `df.to_csv("../data/clean_articles.csv", index=False, encoding="utf-8-sig")`

Printed outputs in that notebook: input shape `(111861, 8)`; after cleaning **111860** articles.

There is **no** category filter, **no** duplicate drop, **no** Unicode normalization.

### Why one row is dropped (observed in local `urdu_news.csv`, not assumed)

Inspection of the local precursor (6 September 2026):

- 111,860 records have 8 CSV fields.
- 1 record (the last data record) has **3** CSV fields only.
- That record’s `Index` value is `111860`.
- Present fields map to `Index`, `Headline`, `News Text`.
- Absent fields: `Category`, `Date`, `URL`, `Source`, `News length`.
- The file does **not** end with a newline; the last record is truncated.

`pandas.DataFrame.dropna()` drops any row with NA. Missing trailing columns parse as NA. That is the row-count change **111,861 → 111,860** on this disk.

This package does **not** provide a new reconstruct script and must not overwrite `data/clean_articles.csv`. If you reconstruct, write a **different output path**, then verify SHA-256.

### Path gap

The notebook’s `../data/` paths worked when the file lived at repository `notebooks/01_preprocessing.ipynb`. It now lives under `archive/historical_experiments/notebooks/`. Running it as-is from the archived folder does **not** target repository `data/`. That is a **REPRODUCTION GAP**.

`pandas.DataFrame.to_csv` output can differ by pandas version. Matching 111,860 rows is necessary but **not** sufficient. SHA-256 is the freeze.

---

## 7. How to verify the SHA-256

From the repository root:

```
python experiments/publication_audit/verify_corpus_hash.py --path PATH_TO_CANDIDATE.csv
```

For the local frozen file (if present):

```
python experiments/publication_audit/verify_corpus_hash.py
```

Require `status: MATCH`.

Phase 12 preflight uses the same expected SHA (`EXPECTED_CORPUS_SHA` in `run_phase12.py`). That runner also retrieves; it is not a substitute for this small verifier.

---

## 8. If the source dataset version changes

1. Do not replace the frozen `clean_articles.csv`.
2. Record the new host version, filename, bytes, and SHA-256.
3. Compare to local `urdu_news.csv` hash `7662b6e8…` if you still have that file.
4. If they differ, the published freeze is tied to the **old** bytes. Report a provenance mismatch. Do not retune M0 or change 23/40, 26/40, or the kappas to chase a new dump.

Mendeley also has V4 (`10.17632/834vsxnb99.4`, August 2024). Kaggle cited **V3**. Using V4 without a hash check is not a reproduction of this paper’s corpus.

---

## 9. Steps that are currently impossible or incomplete

| Step | Status |
| ---- | ------ |
| Exact public-file SHA vs local `urdu_news.csv` | NOT VERIFIED (no download in this task) |
| Documented download command | COMMAND NOT VERIFIED |
| Mendeley “1M rows” → 111,861-record Kaggle file | **REPRODUCTION GAP** (not in this repo) |
| Run archived notebook against live `data/` without path edits | **REPRODUCTION GAP** |
| Bit-identical `to_csv` across pandas versions | Not guaranteed |
| Import `run_phase5` on a clean clone | May fail: `validate/dual_index_routing/retrieve.py` was moved to `archive/historical_experiments/validate/...` |
| Pinned `requirements.txt` | Missing |
| Obtain corpus by cloning GitHub only | Impossible by design (CSV gitignored) |

What **is** possible with a local copy of the frozen CSV: hash verification, and (if the Phase 5 import path is restored without changing retrieval math) re-running M0 on the same documents.

---

## Frozen scientific numbers (do not change)

- Official U Success@5: 23/40 = 57.50%
- Independent A2 Success@5: 26/40 = 65.00% (does not replace 23/40)
- Five-way Cohen’s kappa: 0.5490
- Binary Cohen’s kappa: 0.6816
- Corpus SHA-256: `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231`
