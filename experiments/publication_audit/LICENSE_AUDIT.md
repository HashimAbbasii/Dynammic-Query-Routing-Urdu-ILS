# Repository LICENSE audit

Date: 6 September 2026  
Branch: `publication/plos-one-final`  
Mode: governance only. Scientific freeze unchanged.

**Status: LICENSE STAGE — PASS**

`NO SCIENTIFIC RESULTS CHANGED`

---

## 1. Existing License Status

**No root `LICENSE`, `COPYING`, `NOTICE`, or `COPYRIGHT` file exists.**

`REPRODUCE.md` already records that a code license has not been chosen and that any future license must not be read as covering `data/clean_articles.csv`, `data/urdu_news.csv`, or underlying news text.

The only in-tree third-party license text found for a *vendor file* is:

- `Papers/PLOS_ONE/plos2025.bst` — LaTeX Project Public License (LPPL) 1.3 or later (Vancouver/PLOS BibTeX style). **Do not relicense this file.**

The PLOS LaTeX template comments in the manuscript `.tex` are PLOS production instructions, not a grant of rights in the news corpus.

There is **no** dataset license file. Deposit-page CC BY badges are documented in `DATASET_LICENSE_VERIFICATION.md` and are **not** treated as a verified license of article bodies for this repository.

---

## 2. Repository Material Inventory

| Category | Examples | Author-generated? | Licensable as ULTRA software? | Action |
| -------- | -------- | ----------------- | ----------------------------- | ------ |
| A. Author-generated code | `experiments/phase5_roman_urdu/run_phase5.py` (detector, custom BM25 class, Method D); `experiments/phase12_new_unseen_evaluation/run_phase12.py`; `experiments/phase2_oracle/run_phase2_pipeline.py`; `experiments/publication_audit/verify_corpus_hash.py`; `reconstruct_corpus.py`; `run_agreement.py`; `_score_u.py`; other `experiments/**/*.py` | Yes (project scripts; BM25 is a standard Okapi formula implemented in-repo, not an imported `rank_bm25` package) | **Yes**, if a software license is applied with a data carve-out | Cover under recommended software license |
| A. Historical code | `archive/historical_experiments/**/*.py` (SVM router, MiniLM/Chroma retrieve) | Yes, as project code, but **not** official M0 | Yes as code; MiniLM *weights* are not shipped | Same software license; do not treat as official retriever |
| B. Author-generated documentation | `README.md`, `REPRODUCE.md`, `docs/*.md`, `experiments/**/*.md` protocols, `results/*.md` | Yes | Yes (documentation) | Cover; keep DAS wording |
| C. Author-generated evaluation material | U query *strings* in `queries_u.csv`; A1/A2 *labels*; agreement metrics; annotation protocols; SI tables without article bodies (`S1_table.csv`, `S2_table.csv`, `S4_table.csv`) | Query text and labels: yes. K queries are title-like shortenings of headlines (see notes column) — **derived** | Labels/protocols: yes. Headline-derived K strings: treat as evaluation artifacts, not as a grant of news copyright | License labels/code; do not claim ownership of source headlines |
| D. Third-party data | `data/urdu_news.csv`, `data/clean_articles.csv` | No | **No** | Remain gitignored; **outside** software license |
| E. Derived from third-party news | Frozen CSV (concatenate + dropna); git-tracked **headlines/snippets** in `U_QRELS.csv`, `U_TOP5_FOR_ANNOTATION.csv`, `K_TOP50_RETRIEVAL.csv`, labeled A2 sheets, `DISAGREEMENTS.csv` | Derived excerpts, not author-authored news | **Do not** put article text under MIT/Apache as if authors own it | Keep files for reproducibility of labels; LICENSE/NOTICE must exclude news text/excerpts |
| F. Third-party libraries | `numpy`, `pandas`, `matplotlib`; optional `scikit-learn`, `scipy` (`requirements.txt`) | No (dependencies) | N/A — use their licenses | Do not relicense; all are BSD/PSF-family, compatible with MIT/Apache/BSD |
| F. PLOS/LaTeX tooling | `plos2025.bst` (LPPL); PLOS manuscript template structure | No | No — keep LPPL | Do not wrap in MIT |
| G. Must not redistribute | Full `clean_articles.csv` / `urdu_news.csv`; Chroma DB; embedding `.npy` (gitignored) | Third-party or generated indexes | No | `.gitignore` already excludes `data/*.csv`; **do not** reverse that |
| Other | `models/roman_urdu_dict_expanded.json` (198 keys) | Yes — project mapping list (common words/names, not article bodies) | Yes, as project data/code artifact | Include under software/data-of-the-project, distinct from news CSV |
| Other | `data/training_queries_real.py` | Yes — Layer A SVM training strings, not M0 | Yes as code/data of the project | Historical; not official M0 |
| Other | `archive/**/*.pkl` SVM/scaler | Author-trained sklearn pickles | Weights are project artifacts; sklearn is BSD | Optional to mention; not M0 |
| Other | Figures (`Papers/PLOS_ONE/figures/*.png`) | Project plots of frozen results | Yes as project figures | Software/docs license; PLOS will apply journal CC BY to the published article/figures per PLOS policy (separate from this repo) |
| Other | Thesis DOCX / IEEE sources | Author manuscripts | Yes as author copyright in those files | Not a substitute for a code LICENSE |

BM25 provenance: `class BM25` in `run_phase5.py` implements the usual Robertson/Sparck Jones Okapi weighting (\(k_1\), \(b\), IDF \(\log\frac{N-n+0.5}{n+0.5}+1\)). That is a published retrieval formula. No `rank_bm25` import or third-party BM25 license file is present. Treat the **implementation** as project code.

Copied/adapted code with unclear provenance: none identified with a third-party copyright header in official M0 runners. Historical `retrieve.py` loads `SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")` at runtime; weights are Hugging Face/third-party and **must not** be relicensed by ULTRA.

---

## 3. Third-Party Dataset Boundary

The news corpus **must remain outside** any repository software license.

Reasons (already documented; not re-argued as a new legal opinion):

1. Articles originate from news organizations (Geo, Dawn, and others in `Source`). Publisher copyright in article bodies is **not** assigned to ULTRA.
2. Mendeley V3 DOI `10.17632/834vsxnb99.3` and Kaggle Shahane Version 1 display CC BY 4.0. CC BY grants only rights the licensor has authority to license. This project does **not** treat that badge as proof that article bodies may be relicensed by Hashim Shazad et al.
3. Mendeley “Steps to reproduce” text also mentions non-commercial research with credit to the news source. That conflict is **unresolved**.
4. Redistribution permission for underlying news text has **not** been independently verified.
5. Files are gitignored (`data/*.csv`). GitHub does not host them. PLOS SI does not contain them (~515 MB vs 20 MB cap).
6. A root MIT/Apache/BSD file that simply says “this repository” without a carve-out would be **misread** as licensing 111,860 articles.

Frozen identity (for reconstruction, not for relicensing):

- 111,861 precursor records → 111,860 frozen articles  
- SHA-256 `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231`

**Do not:** add the dataset to LICENSE; claim authors own the corpus; claim the corpus is CC BY; upload or commit the CSV; weaken `.gitignore`.

---

## 4. Third-Party Material Audit

| Item | Treatment |
| --- | --- |
| Urdu News Dataset 1M / Kaggle Version 1 | Cite only; obtain from provider; **not** ULTRA-licensed |
| News headlines/snippets inside git-tracked evaluation CSVs | Third-party excerpts used for annotation; **exclude from software license grant** |
| `plos2025.bst` | LPPL 1.3+; keep as-is |
| PLOS template comments in `.tex` | PLOS instructions; article text is the authors’ manuscript (PLOS CC BY applies **on publication**, not via this git LICENSE) |
| numpy / pandas / matplotlib / sklearn / scipy | BSD or PSF; list in README or NOTICE as dependencies; do not copy their licenses into ULTRA LICENSE as if they were ULTRA’s |
| MiniLM / Chroma / torch (historical archive code) | Runtime third-party models; not official M0; do not relicense model cards or weights |
| sklearn `.pkl` in `archive/` | Project-trained; optional; not M0 |

No separate `NOTICE` of copied GPL snippets was found in official M0 Python.

---

## 5. License Comparison

| | MIT | Apache-2.0 | BSD-3-Clause |
| --- | --- | --- | --- |
| Academic reproducibility | Excellent; one short file | Excellent | Excellent |
| Attribution | Copyright + permission notice | Copyright + NOTICE + NOTICE file if required | Copyright + conditions |
| Patent grant | None | Explicit patent license from contributors | None |
| Simplicity | Highest | Longer; extra conditions (NOTICE, patent termination) | Short; extra no-endorsement clause |
| Dependency compatibility | Compatible with numpy/pandas/sklearn BSD | Compatible | Compatible |
| Risk of covering news CSV | Same for all three unless **scope is limited in README/NOTICE** | Same | Same |
| Fit for this repo | Strong default for thesis/code reuse | Better if patents are a concern (none recorded) | Fine; little gain over MIT here |

Copyleft (GPL) was **not** selected for comparison as a recommendation: it would complicate reuse of small evaluation scripts and is unnecessary for PLOS code availability.

---

## 6. Recommended License

**Recommend: MIT License, limited in scope to original ULTRA source code and original project documentation, with an explicit exclusion of third-party news text.**

Why MIT:

- Matches PLOS/academic need: others can copy `run_phase5.py` / `run_phase12.py` / hash tools to reproduce **computational** workflow.
- Matches dependency licenses (BSD-family).
- No recorded patents, so Apache’s patent clause is unused complexity.
- Easy for a small thesis repository.

MIT must **not** stand alone as “the whole GitHub tree including any CSV you might add.” Implementation (when approved) should be:

1. Root `LICENSE` = MIT text + copyright line (after confirmation).  
2. Short `NOTICE.md` or a README **License** section stating: MIT applies to original code and original docs; it does **not** apply to `data/clean_articles.csv`, `data/urdu_news.csv`, or news article text/excerpts in evaluation files; those remain third-party.

---

## 7. Copyright Holder

Manuscript authors: Hashim Shazad, Adnan Aslam, Areena Rahman.

CRediT already recorded: **Software** is Hashim Shazad. Areena Rahman: Validation (A2) only. Adnan Aslam: Supervision.

**Do not invent** Air University as copyright holder. Student/employee IP rules are not in this repository.

**AUTHOR CONFIRMATION REQUIRED** for the copyright line, for example one of:

- `Copyright (c) 2026 Hashim Shazad` (software author only), or  
- `Copyright (c) 2026 Hashim Shazad, Adnan Aslam, and Areena Rahman` (all paper authors), or  
- a university-owned line **only if** Air University IP policy requires it (not evidenced here).

Year 2026 matches freeze timestamps; confirm if an earlier year is preferred.

Until that line is confirmed, **do not create `LICENSE`.**

---

## 8. README / Data README Consistency

Current `README.md` and `data/README.md` already say the article CSV is not in git and is third-party. They do **not** yet say what a software license will cover.

**Required wording when LICENSE is applied (not applied in this audit):**

- Root README: one short **License** subsection — MIT (or chosen license) covers original code/docs; news corpus is **not** included and is **not** licensed by that file.
- `data/README.md`: one sentence — local CSVs are third-party news text and are outside the repository software license.
- `REPRODUCE.md` § License: replace “no LICENSE file” with the chosen license **plus** the same carve-out.

Do not rewrite DAS. Do not claim CC BY for the corpus.

---

## 9. PLOS Reproducibility Impact

MIT on **code** supports reasonable reuse of M0 scripts, dictionary JSON, query files, and label files for checking reported numbers **if** the researcher obtains the news corpus from Kaggle/Mendeley and matches SHA-256.

It does **not**:

- grant rights to article bodies;
- make a clean-clone full-corpus rerun possible without the third-party file;
- replace the manuscript DAS.

That matches the current DAS and `REPRODUCE.md`.

---

## 10. Required Actions

**Do not do these until copyright wording is confirmed:**

1. Author confirms copyright holder string (and year).  
2. Add root `LICENSE` (MIT text + that copyright).  
3. Add `NOTICE.md` **or** README License section: software vs third-party news vs LPPL `plos2025.bst` vs PyPI dependencies.  
4. Point `REPRODUCE.md` at `LICENSE`; keep corpus exclusion.  
5. One-sentence updates to `README.md` and `data/README.md`.  
6. Leave `.gitignore` `data/*.csv` unchanged.  
7. Do not commit or upload `clean_articles.csv` / `urdu_news.csv`.  
8. Do not relicense `plos2025.bst`.  
9. Do not change M0, Phase 12, A1/A2, qrels, or metrics.

---

## End status (audit-time)

The items above were the pre-application audit. Author confirmation is now resolved. See **LICENSE APPLICATION — COMPLETE**.

---

## LICENSE APPLICATION — COMPLETE

Date applied: 6 September 2026  
Branch: `publication/plos-one-final`

Author confirmation received:

- Original ULTRA code and documentation are the project author’s work.
- MIT License approved.
- Copyright holder confirmed: **Hashim Shazad**.

Record:

- MIT applied to original ULTRA code/documentation via root `LICENSE`.
- Copyright: `Copyright (c) 2026 Hashim Shazad`
- Standard MIT legal wording used; no extra clauses added to `LICENSE` itself.
- Third-party corpus excluded: MIT is **not** a license of `data/clean_articles.csv`, `data/urdu_news.csv`, or underlying news article text.
- Third-party materials retain their own terms (`plos2025.bst` LPPL 1.3+; PyPI dependencies; news excerpts in evaluation CSVs).
- README boundary updated: new **License** section.
- Data README boundary updated: one sentence that MIT does not license the corpus.
- `REPRODUCE.md` License section updated so it no longer says a code license is missing.
- `.gitignore` still contains `data/*.csv`. Corpus files were not added, committed, or uploaded.
- No `NOTICE.md` created; the README/data README/`REPRODUCE.md` carve-out is the scope notice.
- No scientific files, metrics, qrels, M0, Phase 12, A1/A2, tables, or figures were modified.

Validation:

1. `LICENSE` is the standard MIT License text.
2. Copyright holder is exactly `Hashim Shazad`.
3. Year is `2026`.
4. No third-party dataset is named or granted in `LICENSE`.
5. README and `data/README.md` do not imply that the news corpus is MIT licensed.
6. `.gitignore` still excludes `data/*.csv`.
7. No scientific results changed.

`LICENSE STAGE — PASS`

`NO SCIENTIFIC RESULTS CHANGED`
