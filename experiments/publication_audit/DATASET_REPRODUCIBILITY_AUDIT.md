# Dataset & Reproducibility Audit

Inspection date: 6 September 2026  
Repository: https://github.com/HashimAbbasii/Dynammic-Query-Routing-Urdu-ILS  
Branch inspected: `publication/plos-one-final`  
Scope: dataset identity, provenance, license/redistribution, Data Availability Statement, and corpus/experiment reproducibility.  
Mode: inspection only. No manuscript, M0, Phase 12, label, dataset, or metric changes were made.

Frozen scientific numbers (recorded, not recomputed or reinterpreted):

- Official U Success@5: 23/40 = 57.50%
- Independent A2 Success@5: 26/40 = 65.00% (reliability only; does not replace 23/40)
- 5-way Cohen's kappa: 0.5490
- Binary Cohen's kappa: 0.6816

---

## 1. Executive verdict

**NOT READY**

The local frozen corpus used for the reported experiments is internally consistent: `data/clean_articles.csv` has 111,860 rows, 540,050,203 bytes, and SHA-256 `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231`. That matches the Phase 8 freeze and the manuscript Corpus subsection.

The PLOS ONE Data Availability Statement is not submission-ready. It states that the full news corpus is publicly available on GitHub with **no redistribution restrictions**. Both parts are unsupported:

- `data/*.csv` is gitignored. The GitHub tree for this branch contains only `data/README.md` and `data/training_queries_real.py`. There are no GitHub Releases hosting the CSV. The file is 515 MB, above GitHub’s 100 MB git limit, and there is no Git LFS configuration.
- No repository LICENSE exists. No dataset license is stated in-repo. The original news text is third-party publisher content. Public downloadability is not a redistribution license.

A new researcher also cannot reconstruct the exact 111,860-article file from a documented public download plus a pinned script. The only cleaning recipe is an archived notebook that starts from a local `data/urdu_news.csv` (already 111,861 rows, also gitignored). How that 111k file relates to the advertised “1 Million” Mendeley/Kaggle dumps is not verified. Attribution, CC BY, and news-publisher permission are not verified in this repository.

---

## 2. Exact corpus identity

Inspected on this machine, 6 September 2026.

| Field | Value |
| ----- | ----- |
| Filename used by reported experiments | `data/clean_articles.csv` |
| Rows (data, excluding header) | **111,860** |
| File size | **540,050,203 bytes** |
| SHA-256 | **`8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231`** |
| Encoding | UTF-8 with BOM (`utf-8-sig` in loaders) |
| Match to freeze / manuscript expected hash | **Yes** (exact match; no discrepancy to report) |

Columns (9):

1. `Index`
2. `Headline`
3. `News Text`
4. `Category`
5. `Date`
6. `URL`
7. `Source`
8. `News length`
9. `combined_text`

Category counts (sum = 111,860):

| Category | n |
| -------- | - |
| Sports | 44,829 |
| Entertainment | 34,901 |
| Business & Economics | 24,131 |
| Science & Technology | 7,999 |

`Source` values present in the frozen CSV:

| Source | n |
| ------ | - |
| Geo News | 38,881 |
| Dawn News | 38,377 |
| Ab Tak News | 18,231 |
| 92 News | 13,388 |
| Express News | 2,983 |

Duplicate status:

- Exact duplicate `URL`: **none** (every URL unique).
- Duplicate `Headline` strings: **644** headline values occur more than once (maximum frequency 27). These are repeated titles, not proof of identical articles.
- Duplicate `combined_text`: **4** distinct texts occur twice (8 rows). Because URLs are unique, these are not identical-URL clones; they are same concatenated text under different URLs.
- Empty-string fields in the frozen CSV: **0** (csv scan).

Document identifiers used in evaluation are **0-based row index after cleaning** (`source_doc_id == corpus_row_index` in `experiments/phase8_final_freeze/FROZEN_CONFIGURATION.json`), not a publisher ID.

### Precursor file (not the official freeze corpus)

| Field | Value |
| ----- | ----- |
| Filename | `data/urdu_news.csv` |
| Present locally | Yes |
| Tracked in git / GitHub | No (`data/*.csv` gitignored) |
| Bytes | 276,791,832 |
| SHA-256 (computed this audit; **not previously documented in-repo**) | `7662b6e8508ccb080bbb9adcb5678388a363a94f67fff44102551c7cc7926062` |
| Header | `Index, Headline, News Text, Category, Date, URL, Source, News length` |
| Data rows | 111,861 |

The official experiments load `clean_articles.csv`, not `urdu_news.csv`.

---

## 3. Dataset provenance

### VERIFIED FACTS

- Official retrieval/evaluation code on this branch loads `data/clean_articles.csv` (Phase 2, 4, 5, 9, 11, 12 runners; freeze manifest).
- Local `clean_articles.csv` matches the frozen n, byte size, and SHA-256.
- Local precursor `urdu_news.csv` exists, has 111,861 rows and the eight columns named in the historical preprocessing notebook.
- The archived notebook `archive/historical_experiments/notebooks/01_preprocessing.ipynb` records: load `../data/urdu_news.csv` with UTF-8-SIG and `encoding_errors='replace'`; rename those eight columns; `dropna()`; `reset_index(drop=True)`; `combined_text = Headline + ' ' + News Text`; write `../data/clean_articles.csv`; printed result 111,860 articles. Notebook outputs show input shape `(111861, 8)`.
- `archive/historical_experiments/phase3_retrieval/ARCHITECTURE_AUDIT.md` restates that same pipeline.
- Frozen CSV `Source` column contains Geo News, Dawn News, Ab Tak News, 92 News, Express News.
- Frozen CSV categories are Sports, Entertainment, Business & Economics, Science & Technology.
- Historical project artifacts (not the PLOS manuscript) name a Kaggle dataset: “Kaggle Urdu News Dataset (Shahane, 2020)” in `archive/historical_figures/results_layer_a/_archive_development_cv/evaluation_report.txt` and `archive/historical_experiments/notebooks/07_evaluation.ipynb`.
- As of 6 September 2026, https://www.kaggle.com/datasets/saurabhshahane/urdu-news-dataset exposes schema.org Dataset metadata: name “Urdu News Dataset”; creator Saurabh Shahane; acknowledgements text citing Hussain, Khalid; Mughal, Nimra; Ali, Irfan; Hassan, Saif; Daudpota, Sher Muhammad (2021), “Urdu News Dataset 1M”, Mendeley Data, V3, doi: 10.17632/834vsxnb99.3; license name “Attribution 4.0 International (CC BY 4.0)”; `dateModified` 2021-03-27; zip `contentSize` 65,042,116 bytes; `requiresSubscription` true.
- As of 6 September 2026, https://data.mendeley.com/datasets/834vsxnb99/3 lists “Urdu News Dataset 1M”, DOI 10.17632/834vsxnb99.3, licence **CC BY 4.0**, institution Sukkur Institute of Business Administration, and “Steps to reproduce” stating that scrapers found content usable for **non-commercial research purpose only by crediting the news source**.
- The PLOS manuscript Corpus subsection describes `clean_articles.csv` (111,860), precursor `urdu_news.csv`, null-drop + concatenation, and the freeze SHA-256. It does **not** name Kaggle, Shahane, Mendeley, Hussain et al. (dataset authors), a dataset DOI, or a dataset license.
- The manuscript Related Work cites Bashir, Qaiser, and Hussain (ULTRA preprint, bib10) as supplying “a large news corpus”. That is a different work from the Mendeley/Kaggle dataset depositors. Whether ULTRA and this corpus are the same dump is **not verified** from this repository.

### UNVERIFIED / NEEDS CONFIRMATION

- That the local `urdu_news.csv` is byte-identical to any specific Kaggle versioned file. **Not verified.** No Kaggle version pin, filename-from-Kaggle, or precursor checksum exists in-repo. This audit did not download Kaggle.
- That local `urdu_news.csv` is a documented subset of Mendeley “Urdu News Dataset 1M”. Kaggle/Mendeley descriptions say “above 1 Million” stories; the local precursor is 111,861 rows. The missing reduction from ~1,000,000 to 111,861 is **not in this repository**. **Not verified.**
- Year “2020” on Shahane (Kaggle `dateModified` is 2021-03-27). **Not verified.**
- That news outlets granted CC BY 4.0 covering full article text. Mendeley deposit lists CC BY 4.0; the same page’s scrape note says non-commercial research with credit. Those two statements conflict. **Not verified** which controls redistribution of full text.
- That CC BY 4.0 on the Kaggle/Mendeley **deposit page** is a valid license from the copyright holders of Geo/Dawn/Ab Tak/92 News/Express articles. Public listing is not legal proof. **Not verified.**
- Publisher-level permission to redistribute a derived 111,860-row CSV. **Not verified.**
- Exact pandas `dropna()` row (notebook says 1 row dropped; a csv empty-string scan of the precursor found 111,861 rows and 0 empty fields, so the dropped row may be a pandas NA that is not an empty string). Exact dropped index was not re-identified in this audit.

---

## 4. License and redistribution

| Question | Finding |
| -------- | ------- |
| Is there a repository `LICENSE` file? | **No.** None on `publication/plos-one-final` locally or in the GitHub root listing. |
| Does the repository state a dataset license? | **No.** `data/README.md` does not. `docs/REPRODUCIBILITY.md` does not. README does not. |
| Does the original dataset explicitly state a license? | **Kaggle and Mendeley pages currently display CC BY 4.0.** That is a **deposit-page statement**, not a verified grant from news publishers. |
| Is redistribution of the **full** corpus permitted? | **Not verified.** |
| Is redistribution of a **derived/cleaned** 111,860-article corpus permitted? | **Not verified.** Cleaning (null drop + concatenation) does not by itself create a new right to redistribute third-party news text. |
| Does the repository accidentally imply unrestricted redistribution? | **Yes.** Manuscript Data Availability (and TeX portal comments) say the corpus is on GitHub “with no redistribution restrictions.” README presents `data/` as if the official corpus is in the repository. |
| Are attribution requirements documented? | **Not in this repository.** CC BY, if applicable, requires attribution and marking of changes. Mendeley scrape notes say credit the news source. Neither is implemented as a dataset citation, LICENSE, or DAS attribution block. |

Do not infer permission from the fact that a CSV can be downloaded from Kaggle or Mendeley.

PLOS recommended-repository rule (official page, retrieved 6 September 2026): if a repository states a license, it should not be more restrictive than CC BY (no ban on commercial use or derivatives). The Mendeley “non-commercial research only” scrape note is **more restrictive than CC BY**. Depositing full news text under CC BY on a PLOS-recommended repository, or claiming “no restrictions,” is legally unsafe until a human confirms what may actually be shared.

---

## 5. Current Data Availability Statement

Canonical manuscript:

`Papers/PLOS_ONE/Adaptive_dynamic_query_routing_for_Urdu_information_retrieval.tex`

Live statement (Methods, subsection “Data availability”):

> The news corpus (`data/clean_articles.csv`; 111,860 articles), the Roman Urdu dictionary (`models/roman_urdu_dict_expanded.json`; 198 keys), and the M0 retrieval code are publicly available at https://github.com/HashimAbbasii/Dynammic-Query-Routing-Urdu-ILS with no redistribution restrictions. SHA-256 hashes reported in the Corpus subsection identify the exact artifacts used for the scores in this paper. Official metrics were copied from sealed Phase 8–12 reports and were not recomputed for this manuscript.

Matching TeX comment block (lines 15–20) repeats the same GitHub / “no redistribution restrictions” claim for the PLOS portal field.

Classification: **D. false or unsupported**, and **C. scientifically/legalistically unsafe**. It is also **B. incomplete**.

Issue list (do not edit the manuscript in this audit):

1. **False hosting claim.** GitHub `data/` on this branch has no CSV. `.gitignore` line `data/*.csv` excludes both `clean_articles.csv` and `urdu_news.csv`. GitHub Releases: empty. No LFS. 515 MB cannot be a normal git blob.
2. **False “no redistribution restrictions”.** Unverified, and contradicted by third-party news copyright plus Mendeley’s non-commercial scrape note. CC BY, even if valid, still requires attribution (it is not “no restrictions”).
3. **Does not name the source dataset** (Kaggle Shahane page and/or Mendeley Urdu News Dataset 1M / DOI 10.17632/834vsxnb99.3).
4. **Does not cite dataset authors** (Hussain, Mughal, Ali, Hassan, Daudpota) or Kaggle compiler (Shahane).
5. **Does not explain derivation** beyond the Corpus subsection’s null-drop + `combined_text`. Missing: public file identity, version, precursor checksum, how 1M became 111,861.
6. **Does not say the complete corpus is not in the git repository.**
7. **Does not say whether redistribution is legally allowed.**
8. **Does not tell a researcher how to obtain or reconstruct the exact SHA-256 file.**
9. **Checksum is in Corpus, not in DAS**, and applies only if the reader already has the file.
10. **Code availability is only partly true.** Dictionary JSON is tracked. M0 Python is tracked. Phase 5 still imports `validate/dual_index_routing/retrieve.py`, which now lives under `archive/historical_experiments/validate/...`. A clean clone cannot import `run_phase5` as written.
11. **PLOS third-party data rule not met.** Official PLOS Data Availability policy requires, when authors cannot legally distribute third-party data: describe the dataset and source; permission if applicable; how others obtain access; known restrictions; proper citation. None of that is in the DAS.
12. **PLOS SI cannot carry the corpus.** Official supporting-information / submission guidance: each SI file must be < 20 MB (recommend < 10 MB). 515 MB is ineligible as SI.
13. **SI captions point at repo markdown/JSON**, not at uploaded SI files. That is a packaging issue adjacent to data availability (S1 File = freeze manifest, which is small and could be SI; the corpus cannot).

What the DAS currently gets right: n=111,860; dictionary 198 keys; SHA-256 exist in the Corpus subsection; official metrics were copied from sealed reports rather than recomputed for typesetting.

---

## 6. Reproduction pipeline

Intended chain:

```
public source dump (Kaggle and/or Mendeley)
        ↓  download / select file
data/urdu_news.csv  (111,861 rows; local SHA-256 7662b6e8…; gitignored)
        ↓  01_preprocessing.ipynb: dropna + combined_text
data/clean_articles.csv  (111,860 rows; SHA-256 8992a6ac…; gitignored)
        ↓  M0 BM25 (k1=1.5, b=0.75) + dictionary
reported experiments
```

| Stage | File/script | Exists? | Deterministic? | Parameters documented? | Dependencies documented? | Input identified? | Output independently verifiable? |
| ----- | ----------- | ------- | -------------- | ---------------------- | ------------------------ | ----------------- | -------------------------------- |
| Original public dataset | Kaggle `saurabhshahane/urdu-news-dataset`; Mendeley `10.17632/834vsxnb99.3` | Pages exist | N/A | No in-repo pin of version/filename/hash | Download needs a Kaggle/Mendeley account (`requiresSubscription` true on Kaggle metadata) | Named only in **archive** notes, not in PLOS DAS | **No** — local precursor hash is not published; identity with public files **Not verified** |
| Download / input | `data/urdu_news.csv` | Local yes; git/GitHub **no** | N/A | None | None | Path only | Only if you already have this exact file; checksum was not in-repo before this audit |
| Cleaning (null drop) | `archive/historical_experiments/notebooks/01_preprocessing.ipynb` | Yes (archived). **No** standalone `reconstruct_corpus.py` on the publication path | Weak: `encoding_errors='replace'`; `dropna()` pandas-version dependent; `to_csv` formatting may vary by pandas | Informal notebook cells only | Notebook imports pandas (also unused transformers/chromadb in an earlier cell) | `../data/urdu_news.csv` | **Not verified** in this audit (did not rewrite the corpus). Notebook **claims** 111,860. Frozen file **is** 111,860 |
| Filtering | None beyond `dropna()` | No extra filter script | N/A | Manuscript says no Unicode folding, no dedup, no stemming | N/A | N/A | Near-duplicate combined_text left in (4 pairs) — consistent with “no dedup” |
| Deduplication | Not performed | N/A | N/A | Documented as not done | N/A | N/A | Duplicate headlines remain |
| Final corpus | `data/clean_articles.csv` | Local yes; remote **no** | File on disk is a fixed byte string | Freeze JSON records n/bytes/sha256 | Loaders use pandas/csv + utf-8-sig | Path in freeze and all M0 runners | **Yes, if you possess the file:** SHA-256 matches freeze |
| Checksum | Freeze JSON, `docs/REPRODUCIBILITY.md`, manuscript, Phase 12 preflight | Yes | SHA-256 is deterministic | Expected hash hardcoded in `run_phase12.py` | hashlib | Frozen CSV | Yes, locally |

**Missing links (corpus):**

1. Public 1M dump → 111,861-row `urdu_news.csv` (undocumented).
2. Pinned public artifact (DOI version + filename + SHA) = local precursor.
3. Publication-branch reconstruction script (notebook is under `archive/`).
4. Hosted copy of `clean_articles.csv` **or** a legally explicit non-redistribution statement plus obtain/reconstruct instructions.
5. Dataset citation and license/attribution block.

M0 retrieval, given the frozen CSV and dictionary, is specified: `experiments/phase5_roman_urdu/run_phase5.py` (`BM25_K1=1.5`, `BM25_B=0.75`, tokenizer regex, Method D), `experiments/phase12_new_unseen_evaluation/run_phase12.py` (preflight hashes). That is **experiment** reproducibility, blocked separately by the broken `retrieve.py` import and missing environment pin (Section 7).

---

## 7. Repository reproducibility

| Requirement | Exists? | File | Problem |
| ----------- | ------- | ---- | ------- |
| `requirements.txt` | No | — | Cannot pin pandas/numpy/matplotlib versions |
| `environment.yml` | No | — | Anaconda env `ultra_env` appears only in notebook stderr, not as a file |
| `pyproject.toml` / `setup.py` | No | — | Not an installable package |
| Setup instructions | Partial | `README.md`, `docs/REPRODUCIBILITY.md` | Paths and hashes; no clone → install → obtain-corpus → run sequence |
| Python version | Partial | Manuscript: Python 3.13.9 (Anaconda, 64-bit Windows) | Not in an env file; not tested as a matrix |
| Package versions | No | `run_phase5.py` imports pandas, numpy, matplotlib | Unpinned |
| Model versions | N/A for official M0 | MiniLM is not official M0 | Dense/MiniLM versions are historical; do not belong in M0 DAS as required runtime |
| BM25 parameters | Yes | `run_phase5.py` (`k1=1.5`, `b=0.75`); `FINAL_SYSTEM_MANIFEST.json`; `FROZEN_CONFIGURATION.json` | Documented and frozen |
| Preprocessing configuration | Partial | Archived notebook + manuscript Corpus subsection | Not a pinned script; `encoding_errors='replace'` |
| Random seeds | Partial | Phase 12 `SEAL.json` seed `120260827`; Phase 2 seed 42; Phase 8 notes `SEED=42` unused on official BM25 path | Official BM25 is deterministic given corpus/query; query generation seed is recorded |
| Corpus checksum | Yes | Freeze, docs, manuscript, `run_phase12.py` | File itself is not shipped |
| Precursor checksum | No (until this report) | — | `urdu_news.csv` hash was unpublished |
| Dictionary checksum | Yes | `models/roman_urdu_dict_expanded.json` tracked; SHA-256 `30c3f61a64ec641abbb3acdbc7a8bcaf197f0238f1bf9e76c2c7ce8e590f86a3` (verified this audit) | OK |
| Reproduction commands | No | — | No `REPRODUCE.md`; README has no `python ...` commands |
| Experiment commands | Partial | Phase READMEs / preflight | `run_phase12.py` exists but Phase 5 import path is broken (below) |
| Evaluation commands | Partial | Human metrics already stored in Phase 12 human folder | Re-running retrieval is possible in principle after import/env/corpus fixes; **do not rerun to change frozen numbers** |
| README instructions | Partial | `README.md` | Implies corpus lives in `data/`; points at missing thesis ZIP/docx paths; no data-license section |
| `REPRODUCE.md` | No | — | Missing |
| `LICENSE` | No | — | Missing for code and data |
| Manifest / version | Partial | `experiments/phase8_final_freeze/FINAL_SYSTEM_MANIFEST.json` | Records corpus hash and BM25; `test_set` still says `H001-H040`; routing omits OTHER (code routes OTHER to Urdu BM25). Manifest is not a data-availability object |
| Git LFS / Releases for large data | No | `.gitattributes` is only `* text=auto`; Releases API returned `[]` | Cannot deliver 515 MB via current GitHub layout |
| Obtain-corpus instructions | No | `data/README.md` | Says other files are gitignored; does not say how a reviewer gets `clean_articles.csv` |
| Broken runtime import | Yes (bug) | `experiments/phase5_roman_urdu/run_phase5.py` line 32–33 | Inserts `validate/dual_index_routing` and imports `transliterate_roman`. That tree is now `archive/historical_experiments/validate/dual_index_routing/retrieve.py`. Phase 12 imports `run_phase5`, so a fresh clone fails before retrieval |

---

## 8. Recommended Data Availability strategy

PLOS ONE (official Data Availability page, 6 September 2026) requires the minimal data needed to replicate findings, prefers repositories with persistent identifiers, allows SI under 20 MB, and has a **third-party data** clause when authors lack redistribution rights. Repository licenses should not be stricter than CC BY. An author cannot be the sole long-term access contact for restricted data.

No option below is chosen on an assumed license. Legal permission is **Not verified** for B and C.

### OPTION A — Original public dataset + exact preprocessing/reconstruction instructions

- **Scientific reproducibility:** Best *if* a public file is proven identical to `urdu_news.csv` (or a documented subsetting recipe from the 1M dump is written and checked against SHA-256 `8992a6ac…`). Currently that proof is missing, so A is **not yet executable**.
- **Legal/licensing risk:** Lower than uploading full news text yourselves, but not zero. You still use and describe third-party articles. Attribution still required if CC BY applies. Kaggle metadata marks download as requiring subscription/login; PLOS prefers no unnecessary registration, but third-party access “in the same manner as the authors” is explicitly allowed.
- **PLOS suitability:** Fits the third-party-data pattern **if** DAS lists source, DOI, how to get the file, reconstruction steps, and freeze checksum, and **if** others can actually obtain the same file.
- **Reviewer convenience:** Medium/low until reconstruction is one command and the public file is pinned.
- **Currently possible from the repository:** **No.** Missing pin, missing public-file hash, missing 1M→111k recipe, reconstruction only in an archive notebook, precursor gitignored.

### OPTION B — Host the derived 111,860-article corpus on Kaggle (if license/attribution permits)

- **Scientific reproducibility:** High for reviewers (download one CSV, verify SHA-256).
- **Legal/licensing risk:** **High until confirmed.** Full article text from named news organizations. Mendeley scrape note says non-commercial + credit source. CC BY on a Kaggle *mirror* does not prove publishers allowed it. Attribution of Hussain et al. / Shahane / outlets would still be required if CC BY is valid.
- **PLOS suitability:** Convenient, but Kaggle login and license conflicts can draw editor questions. PLOS still wants a DAS that is true.
- **Reviewer convenience:** High.
- **Currently possible from the repository:** Technically you have the local file. **Legally: Not verified. Do not upload in this audit.** GitHub does not already host it.

### OPTION C — Host the derived corpus elsewhere with a persistent identifier (Zenodo, Dryad, institutional repo, etc.)

- **Scientific reproducibility:** High if the deposited bytes match `8992a6ac…` and the DOI is in the DAS.
- **Legal/licensing risk:** Same third-party news-text problem as B. PLOS-recommended repos generally need CC BY or CC0 — which may be **the wrong license** for scraped news even if it is the license PLOS prefers. That is a conflict, not a green light.
- **PLOS suitability:** Strong *after* legal clearance. SI is not a substitute (20 MB cap).
- **Reviewer convenience:** High.
- **Currently possible from the repository:** File exists locally. **License to deposit: Not verified.** No PID exists today.

### OPTION D — Do not redistribute the corpus; provide scripts, provenance, checksum, and obtain/reconstruct instructions

- **Scientific reproducibility:** Adequate **only after** A’s missing links are filled (pinned source + deterministic reconstruct that hits `8992a6ac…`). Checksum alone does not let a reviewer build the index.
- **Legal/licensing risk:** Lowest redistribution risk. Still must not claim “no restrictions.” Must describe restrictions honestly.
- **PLOS suitability:** Explicitly contemplated for third-party data. Must include source, access path, restrictions, and citation. Must not make the corresponding author the only access contact for a *restricted* dataset if PLOS treats it as controlled; pointing at an existing public Kaggle/Mendeley deposit is the usual pattern.
- **Reviewer convenience:** Lowest of the four until reconstruct is turnkey.
- **Currently possible from the repository:** This is **what the git layout actually does** (CSV not shipped), but the DAS **claims the opposite**, and reconstruct instructions are incomplete.

**What can be said without assuming a license:** the honest DAS must stop claiming GitHub hosts the CSV and must stop saying “no redistribution restrictions.” Choosing A vs D for the published statement requires (1) confirming the public file identity and (2) human confirmation of redistribution rights before B or C.

Evaluation artifacts that **are** small and already in git (qrels, query CSVs, freeze JSON, per-query tables) can be SI or repository files regardless of corpus strategy. They are not a substitute for the 111,860-document collection used to build BM25.

---

## 9. Exact blockers

| # | Severity | Exact file/path | Exact problem | Recommended fix (do not implement in this audit) | Human/license confirmation required? |
| - | -------- | --------------- | ------------- | ------------------------------------------------ | ------------------------------------ |
| 1 | **BLOCKER** | `Papers/PLOS_ONE/Adaptive_dynamic_query_routing_for_Urdu_information_retrieval.tex` (DAS ~L393–395 and comments L15–20) | States corpus is on GitHub with no redistribution restrictions. GitHub has no CSV; license unrestricted is unverified/false. | Rewrite DAS to a true third-party or deposit statement after legal choice of A–D. Do not claim GitHub hosts 515 MB. | Yes — redistribution vs third-party-only |
| 2 | **BLOCKER** | `data/clean_articles.csv` + `.gitignore` `data/*.csv` | Official corpus is local-only; reviewers cloning the repo cannot replicate BM25. | Either (legally cleared) deposit with PID/hash, or DAS + reconstruct from a pinned public file. | Yes before any upload |
| 3 | **BLOCKER** | Missing public-file pin | No DOI+filename+SHA linking Kaggle/Mendeley bytes to `urdu_news.csv` / `7662b6e8…`. 1M vs 111,861 unexplained. | Identify the exact download; record version, filename, bytes, SHA; document any subsetting. | Yes — confirm which file was actually used |
| 4 | **BLOCKER** | No `LICENSE`; no dataset license/attribution in-repo | CC BY attribution and news-source credit are undocumented; “no restrictions” overclaims. | Add a code license if desired; separately state dataset terms without inventing permission. Cite Hussain et al. / Shahane / outlets only after confirmation. | Yes |
| 5 | **IMPORTANT** | `archive/historical_experiments/notebooks/01_preprocessing.ipynb` only | Reconstruction is an archived notebook with `encoding_errors='replace'`, not a pinned publication script. | After source pin, add a read-only reconstruct script and verify it matches `8992a6ac…` **without replacing** the frozen CSV if hashes already match. | No for drafting; yes if output differs |
| 6 | **IMPORTANT** | `experiments/phase5_roman_urdu/run_phase5.py` | Imports `validate/dual_index_routing/retrieve.py` which is only under `archive/historical_experiments/...`. Fresh clone cannot import M0. | Restore import path or vendor the needed function **without changing M0 retrieval math**. | No (engineering), do not retune BM25 |
| 7 | **IMPORTANT** | Missing `requirements.txt` / `environment.yml` / `REPRODUCE.md` | Python 3.13.9 mentioned in prose only; package versions unpinned; no reproduction commands. | Add env pin and command list. Do not change scientific results. | No |
| 8 | **IMPORTANT** | `plos_bibtex_sample.bib` / Related Work | Dataset DOI not cited; bib10 ULTRA paper is used as if it supplied this corpus. | Add a data citation to the actual source once confirmed; do not invent a DOI. | Yes — which source to cite as the dump you used |
| 9 | **IMPORTANT** | PLOS SI captions L641–662 | Captions point at experiment markdown/JSON; 515 MB corpus cannot be SI (<20 MB rule). | Upload actual small SI files (manifest, tables, protocol). Keep corpus out of SI. | No |
| 10 | **MINOR** | `data/README.md`, root `README.md` | Speak as if `data/clean_articles.csv` is “in the repository.” | Clarify gitignored + how to obtain. | No |
| 11 | **MINOR** | `FINAL_SYSTEM_MANIFEST.json` | `test_set` still H001–H040; routing omits OTHER. | Documentation accuracy for freeze JSON; not a metric change. | No |
| 12 | **MINOR** | Duplicate `combined_text` (4 pairs); duplicate headlines (644) | Not a hash mismatch. Manuscript already says near-duplicates were left in. | Optional footnote; do not deduplicate the frozen corpus. | No |

---

## 10. What AI must NOT assume

The following must not be written into the manuscript, DAS, README, LICENSE, or any public claim unless a human verifies them:

1. That redistribution of `clean_articles.csv` or `urdu_news.csv` is permitted.
2. That redistribution of a derived/cleaned corpus is permitted.
3. That the corpus is “publicly available on GitHub.”
4. That there are “no redistribution restrictions.”
5. That Kaggle CC BY 4.0 or Mendeley CC BY 4.0 is a valid license from Geo, Dawn, Ab Tak, 92 News, or Express for full article text.
6. That CC BY 4.0 and the Mendeley “non-commercial research only + credit the news source” note can be treated as the same permission.
7. That “the dataset is on Kaggle/Mendeley, therefore we may rehost it.”
8. That local `urdu_news.csv` **is** the Kaggle zip contents or the Mendeley 1M dump.
9. That the 111,860-row freeze is a documented official subset of “Urdu News Dataset 1M.”
10. That Shahane (2020) is the correct citation year.
11. That Bashir/Qaiser/Hussain ULTRA (bib10) is the legal or bibliographic source of this CSV.
12. That dropping nulls and concatenating headline+body creates a new, freely shareable dataset.
13. That PLOS will accept a 515 MB SI file.
14. That Git LFS, a Release asset, or a PID already exists.
15. That a new researcher can reconstruct SHA-256 `8992a6ac…` from public instructions in this repository as it stands.
16. Any invented license text, availability URL, or DOI.

Verified and safe to reuse without reinterpretation:

- Frozen corpus n=111,860, 540,050,203 bytes, SHA-256 `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231`
- Dictionary 198 keys, SHA-256 `30c3f61a64ec641abbb3acdbc7a8bcaf197f0238f1bf9e76c2c7ce8e590f86a3`
- BM25 k1=1.5, b=0.75
- Official U Success@5 23/40 = 57.50%; A2 26/40 = 65.00%; kappas 0.5490 / 0.6816

---

## Appendix. PLOS ONE policy notes (official pages, 6 September 2026)

Sources used (not blogs):

- https://journals.plos.org/plosone/s/data-availability
- https://journals.plos.org/plosone/s/recommended-repositories
- https://journals.plos.org/plosone/s/supporting-information
- https://journals.plos.org/plosone/s/submission-guidelines (SI files smaller than 20 MB)
- https://journals.plos.org/plosone/s/materials-and-software-sharing

Relevant requirements for this paper:

- All data needed to replicate findings must be available without restriction **or** restrictions must be legal/ethical and described.
- Third-party data the authors cannot distribute: describe source, permission if applicable, how others get access, known restrictions, cite/acknowledge.
- Deposit in a repository with PID is strongly recommended; SI is an alternative only for files < 20 MB.
- Repository licenses should not be more restrictive than CC BY.
- Code that underpins findings should be available; documentation and dependencies are expected.
- “Data not shown” is not allowed; pointing at a gitignored path as if it were public is equivalent to an unsupported availability claim.

This audit did not change M0, Phase 12, A1/A2 labels, the dataset, or reported metrics.
