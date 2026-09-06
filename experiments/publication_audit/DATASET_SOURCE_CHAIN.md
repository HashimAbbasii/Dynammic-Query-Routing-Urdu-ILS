# Dataset Source Chain Audit

Inspection date: 6 September 2026  
Branch: `publication/plos-one-final`  
Mode: audit only. No corpus upload, no dataset rewrite, no manuscript edit, no M0/Phase 12/label/metric change.

Local freeze reconfirmed this session (read-only):

- `data/clean_articles.csv`: 540,050,203 bytes; SHA-256 `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231`; 111,860 data rows
- `data/urdu_news.csv`: 276,791,832 bytes; SHA-256 `7662b6e8508ccb080bbb9adcb5678388a363a94f67fff44102551c7cc7926062`; 111,861 CSV records

Status labels used below: **VERIFIED** (direct evidence), **INFERRED** (consistent but not proven), **UNRESOLVED**.

---

## 1. Executive Finding

The frozen 111,860-article file is a **local derivative** of `data/urdu_news.csv`, produced by the archived notebook `dropna()` plus headline/body concatenation. That local step is **VERIFIED**.

The local precursor is **schema- and size-consistent** with Kaggle “Urdu News Dataset” Version 1 (`urdu-news-dataset-1M.csv`, 276.79 MB, ~111,861 records). Historical project notebooks **name Kaggle / Shahane**. There is **no** download script, **no** git-tracked CSV, and **no** SHA-256 comparison to a fresh Kaggle or Mendeley download. Statement “obtained from Kaggle”: **INFERRED**, not byte-proven.

Kaggle **publicly cites** Mendeley “Urdu News Dataset 1M”, V3, DOI `10.17632/834vsxnb99.3`. That citation is **VERIFIED**. Whether the Kaggle ~111k file **is** the full Mendeley dump is **UNRESOLVED**. The string “1M” is the **dataset title and a depositor/description claim** (“above 1 Million”). It is **not** a verified row count of the Kaggle Version 1 file.

Public redistribution of the 111,860-article CSV is **NOT VERIFIED**. Safest PLOS ONE posture: **Option B** (do not rehost article text; cite third-party source; checksum + preprocessing notes). That matches the already-decided project policy.

The chain `Mendeley → Kaggle → urdu_news.csv → clean_articles.csv` is therefore **PARTIALLY** proven, not fully proven.

---

## 2. Mendeley Source

Authoritative records retrieved 6 September 2026:

| Field | Evidence | Status |
| ----- | -------- | ------ |
| Title | “Urdu News Dataset 1M” | VERIFIED (Mendeley V3 page; DataCite) |
| Version | 3 | VERIFIED |
| DOI | **10.17632/834vsxnb99.3** | VERIFIED |
| Concept DOI | 10.17632/834vsxnb99 (HasVersion .1 .2 .3 .4) | VERIFIED (DataCite concept record) |
| Later version | V4, 10.17632/834vsxnb99.4, issued 14 August 2024 | VERIFIED (exists; **not** the DOI Kaggle cites) |
| Publisher / platform | Mendeley / Mendeley Data | VERIFIED |
| V3 issued / published | 27 January 2021 | VERIFIED (Mendeley “Published”; DataCite date Issued) |
| Institution on page | Sukkur Institute of Business Administration | VERIFIED |
| Stated contents | “above 1 Million Urdu news stories”; four categories: Business & Economics, Science & Technology, Entertainment, Sports | VERIFIED as **description text** |
| File name(s) on Mendeley | HTML “Files” section empty in this scrape; DataCite `sizes`/`formats` empty; public-api files endpoint 400/404 | **UNRESOLVED** |
| Row count of Mendeley files | Not on the landing page in this retrieval | **UNRESOLVED** |
| Stated license | CC BY 4.0; DataCite SPDX `cc-by-4.0`; legalcode URI https://creativecommons.org/licenses/by/4.0/legalcode | VERIFIED as **deposit-page / DataCite rights** |
| Additional restriction text | “Steps to reproduce”: scrapers found content usable for **non-commercial research purpose only by crediting the news source** | VERIFIED as **page text** (V1, V3, V4 wording retrieved earlier/this audit) |
| Named outlets Geo/Dawn/Ab Tak/92/Express | Not named on Mendeley/DataCite; only “major Urdu news sources” | Those five names **not verified** on Mendeley |

DataCite V3 creator list is **Saif Hassan** only, with Hussain, Mughal, Ali, Daudpota as contributors. Kaggle’s acknowledgement cites five names including Hassan as authors of V3. V4 DataCite lists six creators including Wahaj Hassan. **Do not invent a single author string.**

Independent papers citing this DOI repeat the “1 million” **description** (e.g. PeerJ CS 10.7717/peerj-cs.1176; IEEE Access 10.1109/access.2022.3173259). Those papers are **not** a row-count audit of Mendeley’s files. They do show that users of the DOI treat “1M” as the collection size. Column names in the IEEE Access paper (Headline, News Text, Category, Date, plus URL/source in related text) are **compatible** with the eight-column schema, not proof of 1,000,000 rows on disk.

**What “1M” means on Mendeley:** publicly documented as the **dataset title** plus the claim “above 1 Million” stories. It is **not** verified here as an exact row count of any downloadable Mendeley object.

---

## 3. Kaggle Source

https://www.kaggle.com/datasets/saurabhshahane/urdu-news-dataset  
schema.org Dataset JSON on that page (6 September 2026):

| Field | Evidence | Status |
| ----- | -------- | ------ |
| Title | Urdu News Dataset | VERIFIED |
| Alternate name | “1 Million Urdu News Stories Corpus” | VERIFIED as **label**, not as row count |
| Compiler / page creator | Saurabh Shahane | VERIFIED |
| Version | 1 (`version`: 1; explorer “Version 1 (276.79 MB)”) | VERIFIED |
| `dateModified` | 2021-03-27T11:53:23.647Z | VERIFIED |
| License badge | Attribution 4.0 International (CC BY 4.0); license URL https://creativecommons.org/licenses/by/4.0/ | VERIFIED as **Kaggle metadata** |
| Download | zip `contentSize` 65,042,116 bytes; `requiresSubscription` true | VERIFIED |
| Acknowledgements | Hussain, Mughal, Ali, Hassan, Daudpota (2021), “Urdu News Dataset 1M”, Mendeley Data, V3, doi: 10.17632/834vsxnb99.3 | VERIFIED |
| Description | Same “above 1 Million” prose as Mendeley | VERIFIED as **copied description** |
| File name | `urdu-news-dataset-1M.csv` | VERIFIED |
| Displayed uncompressed size | 276.79 MB | VERIFIED |
| Columns | Index, Headline, News Text, Category, Date, URL, Source, News length | VERIFIED |
| Explorer URL count | 111,861 | VERIFIED on page |
| Source mix on explorer | Geo News 35%, Dawn News 34%, Other 31% (Other count 34,603) | VERIFIED on page |

The Kaggle **filename and subtitle say 1M**; the **explorer counts ~111,861 records**. Those two facts are both on the same page. “1M” on Kaggle is therefore **not** a verified count of Version 1.

Historical in-repo string “Shahane, **2020**” (`archive/historical_experiments/notebooks/07_evaluation.ipynb`; `archive/historical_figures/results_layer_a/_archive_development_cv/evaluation_report.txt`) conflicts with Kaggle `dateModified` 2021-03-27. Year 2020: **UNRESOLVED / not verified**.

---

## 4. Relationship Between Mendeley and Kaggle

| Claim | Status |
| ----- | ------ |
| Kaggle presents itself as using / acknowledging Mendeley V3 DOI 10.17632/834vsxnb99.3 | **VERIFIED** (acknowledgements) |
| Kaggle Version 1 file is byte-identical to Mendeley V3 files | **UNRESOLVED** (Mendeley file bytes not retrieved) |
| Kaggle ~111k file is the complete “above 1 Million” dump | **UNRESOLVED** (description vs explorer conflict; Mendeley file list empty) |
| Kaggle is a subset, sample, or incomplete copy of Mendeley | **INFERRED** as one possible explanation; **not proven** |
| This repository contains a script that copied Mendeley → Kaggle or Mendeley → `urdu_news.csv` | **VERIFIED absent** |

---

## 5. Local `urdu_news.csv`

| Field | Value | Status |
| ----- | ----- | ------ |
| Path | `data/urdu_news.csv` | VERIFIED |
| Git | gitignored (`data/*.csv`); never a git blob on this branch | VERIFIED |
| Bytes | 276,791,832 = 276.79 MB (decimal) | VERIFIED |
| SHA-256 | `7662b6e8508ccb080bbb9adcb5678388a363a94f67fff44102551c7cc7926062` | VERIFIED locally |
| Header | Index, Headline, News Text, Category, Date, URL, Source, News length | VERIFIED |
| Record count | 111,861 | VERIFIED |
| 8-field records | 111,860 | VERIFIED |
| Last record | Index `111860`; **3 fields**; missing Category, Date, URL, Source, News length; file has **no** trailing newline | VERIFIED |
| Filesystem mtime (this machine) | 2026-05-24 15:21:26 | VERIFIED as local timestamp only |
| Download command / URL in repo | none | VERIFIED absent |
| SHA vs fresh Kaggle/Mendeley file | not compared this audit (authenticated download not completed) | **UNRESOLVED** |

**Can we state “the local precursor was obtained from Kaggle”?**

- **FACT:** Project notebooks and old papers **call** the collection “Kaggle Urdu News Dataset (Shahane, 2020)” / “Kaggle Urdu News”.
- **FACT:** Local file **matches** Kaggle Version 1 on displayed size (276.79 MB), eight column names, ~111,861 records, and Geo/Dawn-majority sources (clean-file Other sources 34,602 vs Kaggle Other 34,603; off-by-one matches dropping the truncated last row).
- **FACT:** No commit, script, or README records a Kaggle download.
- **INFERENCE:** The local file is a copy (or truncated copy) of that Kaggle Version 1 CSV, likely renamed to `urdu_news.csv`.
- **UNRESOLVED:** Byte identity; whether the last truncated record is also on Kaggle; whether the file was obtained from Mendeley instead and only **described** as Kaggle.

Sufficient for a **defensible DAS sentence** of the form: “The local precursor matches the public Kaggle Version 1 listing on size and schema; Kaggle cites Mendeley V3; a SHA-256 match to a fresh download has not been completed.”  
**Not** sufficient for: “We downloaded Kaggle file X and its SHA is …”

---

## 6. Transformation to `clean_articles.csv`

Script: `archive/historical_experiments/notebooks/01_preprocessing.ipynb` (saved outputs).

Operations **in that notebook** (not invented):

1. `pd.read_csv("../data/urdu_news.csv", encoding="utf-8-sig", encoding_errors="replace")`
2. Force eight column names
3. `df.dropna()` then `reset_index(drop=True)`
4. `combined_text = Headline + ' ' + News Text`
5. `to_csv("../data/clean_articles.csv", index=False, encoding="utf-8-sig")`

Printed: input `(111861, 8)`; after cleaning **111860**.

**Why one row disappears (local files, this session):** record 111861 is malformed (3 fields). Pandas treats missing columns as NA. `dropna()` drops it. **Not** a category filter and **not** deduplication.

`clean_articles.csv` mtime on this machine: 2026-05-24 21:25:37 (about six hours after `urdu_news.csv`). **INFERRED** as same-day preprocess; not proof of origin.

Frozen identity **unchanged** this session: n=111,860; SHA-256 `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231`.

Notebook `../data/` paths assume the old `notebooks/` layout, not `archive/historical_experiments/notebooks/`. Reconstruct CLI: still **COMMAND NOT VERIFIED**.

---

## 7. Provenance Evidence Table

| Claim | Evidence | Status |
| ----- | -------- | ------ |
| Mendeley dataset exists under DOI 10.17632/834vsxnb99.3 | Mendeley + DataCite | VERIFIED |
| That record is titled “Urdu News Dataset 1M” and claims “above 1 Million” stories | Same | VERIFIED as description |
| Mendeley V3 contains exactly 1,000,000 (or 111,861) rows | No file listing/size in retrieved metadata | UNRESOLVED |
| Kaggle dataset cites that DOI | schema.org acknowledgements | VERIFIED |
| Kaggle Version 1 file is ~111,861 rows / 276.79 MB / 8 columns | Kaggle explorer | VERIFIED |
| “1M” equals the Kaggle Version 1 row count | Same page: title 1M vs explorer ~111k | **Not supported** |
| Local `urdu_news.csv` is gitignored and 276,791,832 bytes / 111,861 records / truncated last row | Local inspection | VERIFIED |
| Local precursor SHA equals Kaggle file SHA | No download comparison | UNRESOLVED |
| Local precursor was obtained from Kaggle | Size/schema match + historical “Kaggle” labels; no download log | INFERRED |
| `dropna()` on the truncated last row yields 111,860 | Notebook + local CSV structure | VERIFIED |
| Frozen `clean_articles.csv` SHA is `8992a6ac…` | This session hash | VERIFIED |
| Manuscript DAS: corpus on GitHub, no redistribution restrictions | `.tex` L393–395; CSVs gitignored | Claim **false** vs repo |
| Manuscript Corpus cites bib10 ULTRA as the precursor setting | `.tex` L308; bib10 is Bashir et al. arXiv:2602.11836, not Hussain/Mendeley | **Contradiction** (see §7 of the user checklist, documented in §11) |
| CC BY 4.0 on deposit pages licenses Geo/Dawn article bodies for rehosting | CC legalcode: only rights the licensor can grant; scrape note is non-commercial | NOT VERIFIED / requires human confirmation |

---

## 8. License and Rights Analysis

**A. Compilation / metadata license (publicly documented)**  
Kaggle and DataCite/Mendeley **display** Creative Commons Attribution 4.0 International (CC BY 4.0). That is **publicly documented**. It is **not verified** as a valid grant covering every news article body.

**B. Rights in underlying article text**  
Local/frozen `Source` values include Geo News, Dawn News, Ab Tak News, 92 News, Express News (**VERIFIED** in CSV). Publisher copyright in those texts: **not verified** as transferred to Shahane, Hussain et al., or ULTRA. Mendeley scrape note: non-commercial research + credit news source (**publicly documented** page text). **Conflict with CC BY 4.0** (CC BY, if it applied, allows commercial use). This audit does **not** resolve the conflict.

CC BY 4.0 legal code: Licensed Rights are only those the Licensor has **authority to license**; others may hold copyright in the material.

**C. Permission to redistribute the 111,860-article corpus**  
**NOT VERIFIED.** Cleaning (null drop + concatenation) does not by itself create a right to rehost full article text.

**D. Permission to use the corpus for research**  
**REQUIRES HUMAN CONFIRMATION.** Deposit pages are public; scrape note claims non-commercial research with credit. Whether that is enough for this PLOS paper is an IP/supervisor question, not something this audit can certify.

**E. Public redistribution via GitHub / Zenodo / Kaggle**  
**NOT currently justified** on verified evidence. Project policy: do not redistribute unless future human/IP review says otherwise. PLOS SI also **cannot** hold 515 MB (20 MB cap) — independent of license.

Wording to keep: “publicly documented,” “not verified,” “requires human/rightsholder confirmation.” Do not say “the dataset is illegal to redistribute.”

---

## 9. Redistribution Decision

| Question | Finding |
| -------- | ------- |
| May ULTRA rehost `clean_articles.csv` now? | **NOT VERIFIED**; project decision is **do not redistribute** |
| Is redistribution proven forbidden? | **NOT VERIFIED** (no single decisive prohibition found) |
| GitHub git blob for 515 MB | **VERIFIED NO** (GitHub blocks files > 100 MiB; also gitignored) |
| Human/rightsholder confirmation before any upload | **REQUIRES HUMAN CONFIRMATION** |

---

## 10. PLOS ONE Data Availability Recommendation

Evaluate only on evidence:

**Option A — Publicly deposit the complete corpus**  
Not supported. Redistribution of article text is not verified. PLOS repository licenses should not be stricter than CC BY, while Mendeley also documents a non-commercial scrape note. SI size cap forbids 515 MB SI.

**Option B — Do not redistribute the corpus; provide source, reconstruction notes, checksum, code, access path**  
Supported. Matches PLOS third-party data rule. Matches the decided policy. Access path: existing public Kaggle and Mendeley pages (Kaggle download may require an account). Freeze identity: SHA-256 `8992a6ac…`. Preprocessing: archived notebook + truncated-row explanation. Share dictionary, queries, qrels, code.

**Option C — Restricted-access committee / special provider**  
Not supported. No data-access committee, license agreement, or controlled repository is documented. Do not invent one.

**Recommended: Option B.**

Do not change the manuscript in this task. The live DAS (GitHub + “no redistribution restrictions”) remains **unsafe** until rewritten under Option B.

---

## 11. Reproducibility Gaps Remaining

1. No SHA-256 of a **fresh** Kaggle Version 1 or Mendeley V3 file vs local `7662b6e8…`.
2. No download command in the repository.
3. Mendeley actual file bytes / row count **UNRESOLVED**; “1M” vs Kaggle ~111k unexplained.
4. Archived notebook relative paths do not hit live `data/`.
5. `pandas.to_csv` bit-identity across versions not guaranteed; SHA is the freeze.
6. `run_phase5.py` import of `validate/dual_index_routing/retrieve.py` is stale (archive move).
7. No `requirements.txt` / `LICENSE`.
8. Live manuscript DAS and bib10 corpus citation contradict the evidence in this audit (**not silently fixed**).

### Contradictions in current documentation (reported, not edited)

| Location | Says | Conflicts with |
| -------- | ---- | -------------- |
| Manuscript DAS (~L393–395) and TeX comments L15–20 | Corpus on GitHub; no redistribution restrictions | gitignore; GitHub `data/` has no CSV; license not verified |
| Manuscript Corpus (~L308) | Precursor used in ULTRA setting `\cite{bib10}` | bib10 is Bashir/Qaiser/Hussain arXiv ULTRA paper, not Mendeley/Kaggle dataset authors |
| `README.md` “data/ Official corpus” | Implies CSV lives in the repo | `data/*.csv` gitignored |
| `docs/CLEANUP_PLAN.md` | `urdu_news.csv` “Possible precursor”; “~264 MB” | Later audits: it **is** the precursor; size is 276.79 MB |
| `data/README.md` | Other files “generated or precursor”; not required to read M0 metrics | True that metrics can be *read* without the CSV; false that a new researcher can *reproduce retrieval* without it |
| Historical notebooks | “Shahane, 2020” | Kaggle `dateModified` 2021-03-27 |
| Kaggle/Mendeley title “1M” | Million-scale | Kaggle explorer and local file ~111k records |
| Mendeley CC BY 4.0 vs scrape note | Commercial-capable CC vs non-commercial research | Unresolved legal conflict |
| Prior audit files vs manuscript | Option B / not redistributed | Manuscript still Option-A language |

---

## 12. Exact Next Action

1. Keep **Option B**. Do not upload `clean_articles.csv` or `urdu_news.csv`.
2. When the manuscript is later edited (not now): replace the GitHub/unrestricted DAS with third-party source + SHA-256 + “redistribution permission for underlying news text has not been independently verified”; add a data citation to DOI `10.17632/834vsxnb99.3` after a human picks the author string.
3. Optional later (human with Kaggle login): download Version 1 to a **temp directory outside the repo**, hash it, compare to `7662b6e8…`, **do not** overwrite project CSVs. Record MATCH or MISMATCH in a new note if asked.
4. Do not retune M0 or change 23/40, 26/40, or the kappas.

---

## Scientific freeze check (this task)

- M0: not modified
- Phase 12: not modified
- A1 / A2 labels: not modified
- Metrics: not modified
- `data/clean_articles.csv`: not modified (SHA reconfirmed `8992a6ac…`)
- `data/urdu_news.csv`: not modified
- Corpus not uploaded
- Manuscript not modified
- Other audit markdown: not modified
