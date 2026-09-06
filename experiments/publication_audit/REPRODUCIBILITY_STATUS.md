# Reproducibility Status

Date: 6 September 2026  
Branch: `publication/plos-one-final`  
Scope: infrastructure under `experiments/publication_audit/` only. Frozen science unchanged.

Official U Success@5 remains 23/40 = 57.50%. Independent A2 remains 26/40 = 65.00%. Five-way kappa 0.5490. Binary kappa 0.6816. Corpus SHA-256 `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231`.

---

## Corpus

**PASS**

Local `data/clean_articles.csv` matches the freeze: 111,860 rows, 540,050,203 bytes, SHA-256 `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231`. File is gitignored and is not on GitHub. That is a sharing choice, not an identity failure.

---

## Provenance

**PARTIAL**

Kaggle “Urdu News Dataset” (Shahane), Version 1 `urdu-news-dataset-1M.csv` at 276.79 MB, eight columns, ~111,861 records, Geo/Dawn-majority `Source`, cites Mendeley DOI **10.17632/834vsxnb99.3**. Local `urdu_news.csv` matches those **displayed** size/schema/counts. Byte-level SHA vs a fresh Kaggle or Mendeley download: **not verified**. Mendeley prose (“above 1 Million”) vs ~111k-row Kaggle file: unexplained in this repository.

---

## Preprocessing trace

**PARTIAL**

The only documented transform is `archive/historical_experiments/notebooks/01_preprocessing.ipynb` (`dropna`, `combined_text`, `to_csv`). No publication-branch CLI. Relative `../data/` paths are stale after the notebook was archived. No `requirements.txt`.

---

## 111,861 → 111,860 transformation

**PASS**

Not assumed. Local `urdu_news.csv` has 111,860 well-formed 8-field records plus **one truncated last record** with 3 fields (`Index`=`111860`, plus Headline and News Text). Missing: Category, Date, URL, Source, News length. The file does not end with a newline. `df.dropna()` in the notebook drops that incomplete row. Deduplication was not used.

A complete, non-truncated public file (if one exists) would **not** necessarily drop a row. Identity still depends on matching the same truncated precursor or the same frozen SHA.

---

## Hash verification

**PASS** (tool + frozen expected value)

Expected SHA is recorded in the Phase 8 manifest, Phase 12 preflight, manuscript Corpus subsection, and this folder. New utility: `experiments/publication_audit/verify_corpus_hash.py`. It does not modify the dataset.

---

## Reproduction commands

**PARTIAL**

| Need | Status |
| ---- | ------ |
| Download Kaggle/Mendeley | COMMAND NOT VERIFIED |
| Reconstruct CSV via notebook | COMMAND NOT VERIFIED (Jupyter; broken relative paths) |
| Verify SHA-256 | `python experiments/publication_audit/verify_corpus_hash.py` |
| Phase 5 | Documented `python experiments/phase5_roman_urdu/run_phase5.py`; import path to `retrieve.py` may fail on a clean clone |
| Phase 12 CLI | Runner exists; documented shell command COMMAND NOT VERIFIED |

---

## Public code package

**PARTIAL**

Git tracks M0 Python, dictionary, queries, qrels, freeze JSON, and this audit folder. Missing: LICENSE, requirements pin, reconstruct CLI, working `validate/dual_index_routing` import. News CSVs are intentionally not in git.

### Minimal public package classification

Do not upload or delete files based on this table.

| Item | Classification | Notes |
| ---- | -------------- | ----- |
| Preprocessing notebook / future reconstruct code (no article bodies) | SAFE TO SHARE | Already in git under `archive/` |
| M0 / Phase 12 evaluation code | SAFE TO SHARE | Code only; restore import path later without changing BM25 |
| BM25 configuration (k1=1.5, b=0.75) | SAFE TO SHARE | In `run_phase5.py` and freeze JSON |
| `models/roman_urdu_dict_expanded.json` | SAFE TO SHARE | Project-authored mappings; already tracked |
| `queries_k.csv` / `queries_u.csv` | SAFE TO SHARE | Project queries; already tracked |
| A1 qrels / A2 labels / annotation instructions | SAFE TO SHARE | Labels and protocols, not full articles |
| Experiment metadata, freeze manifest, checksums, this audit folder | SAFE TO SHARE | |
| `verify_corpus_hash.py`, manifests, DAS recommendation | SAFE TO SHARE | |
| `data/urdu_news.csv` | NOT SAFE TO SHARE | Third-party news text; redistribution not independently verified |
| `data/clean_articles.csv` | NOT SAFE TO SHARE | Same; human decision: do not redistribute unless IP later allows |
| Full article bodies in any new dump or Kaggle/Zenodo upload | NOT SAFE TO SHARE | Same policy |
| Choosing CC BY vs non-commercial scrape note as “the” license | NEEDS REVIEW | IP/supervisor |
| Data citation author string (V3 vs V4 vs Kaggle list) | NEEDS REVIEW | |
| Claiming permission to *use* the third-party dump in the paper | NEEDS REVIEW | DAS “verification of permission” |

---

## PLOS Data Availability preparation

**PARTIAL**

Draft strategy: `DAS_RECOMMENDATION.md`. Manuscript **not** edited (by instruction). Live DAS remains incorrect until a later rewrite. Human confirmation still required for permission-to-use language and the exact data citation.

---

## Remaining blockers

1. No documented download command; no public-file SHA pinned in original project files (local precursor hash is now recorded in this folder only).
2. Archived preprocessing notebook paths do not point at live `data/`.
3. `pandas.to_csv` bit-identity across versions not guaranteed; SHA is the only freeze.
4. Mendeley “1M” vs Kaggle ~111k file: **REPRODUCTION GAP**.
5. `run_phase5.py` import of `validate/dual_index_routing/retrieve.py` is stale after archive.
6. No `requirements.txt` / `environment.yml` / `LICENSE`.
7. Manuscript DAS still claims GitHub + unrestricted redistribution (**do not fix in this task**).
8. Corpus cannot go in PLOS SI (20 MB cap) and is not in git.

---

## Human decisions required

1. Keep the current “do not redistribute the CSV” policy unless IP review later allows a deposit.
2. Confirm permission **to use** the third-party corpus for PLOS (DAS checkbox), without inventing a license.
3. Decide how to describe the CC BY badge vs Mendeley non-commercial scrape sentence.
4. Pick the data-citation author/version string (Kaggle V3 cite vs DataCite lists vs V4).
5. Whether to restore the Phase 5 import path (engineering; must not change M0 math or metrics).
6. When to rewrite the manuscript DAS using `DAS_RECOMMENDATION.md`.

---

## Files in this folder (this task)

Created:

- `REPRODUCIBILITY_MANIFEST.md`
- `verify_corpus_hash.py`
- `REPRODUCE_DATASET.md`
- `DAS_RECOMMENDATION.md`
- `REPRODUCIBILITY_STATUS.md`

Unchanged from prior audits:

- `DATASET_REPRODUCIBILITY_AUDIT.md`
- `DATASET_LICENSE_VERIFICATION.md`
