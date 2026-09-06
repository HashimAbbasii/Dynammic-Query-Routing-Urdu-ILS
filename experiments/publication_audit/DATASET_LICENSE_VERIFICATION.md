# Dataset License & Provenance Verification

Inspection date: 6 September 2026  
Repository: https://github.com/HashimAbbasii/Dynammic-Query-Routing-Urdu-ILS  
Branch: `publication/plos-one-final`  
Mode: inspection / verification only. No manuscript, dataset, DAS, M0, Phase 12, label, or metric changes. No uploads.

Frozen local corpus identity (reconfirmed previously; not altered):

- File: `data/clean_articles.csv`
- Rows: 111,860
- Bytes: 540,050,203
- SHA-256: `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231`

Authoritative sources retrieved 6 September 2026:

- Kaggle dataset page: https://www.kaggle.com/datasets/saurabhshahane/urdu-news-dataset
- Mendeley V3: https://data.mendeley.com/datasets/834vsxnb99/3 and https://doi.org/10.17632/834vsxnb99.3
- Mendeley V4: https://data.mendeley.com/datasets/834vsxnb99/4 and DataCite `10.17632/834vsxnb99.4`
- DataCite concept DOI: https://api.datacite.org/dois/10.17632/834vsxnb99
- DataCite version 3: https://api.datacite.org/dois/10.17632/834vsxnb99.3
- CC BY 4.0 legal code: https://creativecommons.org/licenses/by/4.0/legalcode
- PLOS Data Availability: https://journals.plos.org/plosone/s/data-availability
- PLOS Licenses and Copyright: https://journals.plos.org/plosone/s/licenses-and-copyright
- PLOS submission guidelines (SI size): https://journals.plos.org/plosone/s/submission-guidelines
- GitHub large-file limits: https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github

This verification did not download Kaggle or Mendeley files and did not contact rightsholders.

---

## 1. Executive Verdict

**REQUIRES HUMAN/RIGHTSHOLDER CONFIRMATION**

Redistribution of `clean_articles.csv` (and of `urdu_news.csv`) is **NOT VERIFIED**. It is also **not** proven forbidden by a single clear “you may not redistribute” clause that this inspection could treat as decisive.

Why this verdict, not a simpler one:

- **Not “VERIFIED FOR REDISTRIBUTION.”** Deposit pages currently label the compilation CC BY 4.0, but Creative Commons itself limits that grant to rights the licensor has authority to license. The records are news-article text. Publisher permission to put that text under CC BY, or to allow this project to rehost it, is not documented. The same Mendeley page also says scrapers found the content usable for **non-commercial research only**, with credit to the news source. That conflicts with CC BY 4.0 (which, if it applied, would allow commercial use and sharing of adapted material).
- **Not “REDISTRIBUTION NOT PERMITTED.”** No publisher takedown, no CC BY-NC badge, and no ULTRA-specific license denial was found. Saying “not permitted” would be an assumption.
- **Human/rightsholder confirmation is required** before any upload to GitHub, Kaggle, Zenodo, or PLOS SI, and before any DAS that claims the corpus may be redistributed.

PLOS implication of this verdict: treat the news corpus as **third-party data whose redistribution rights are unclear** (Scenario C below). Do not claim GitHub hosts it with “no redistribution restrictions.”

---

## 2. Original Dataset Identity

Two layers must be kept separate.

### Layer A — Immediate public file that matches the ULTRA precursor (strong circumstantial match; SHA not compared)

| Field | Verified value | Confidence |
| ----- | -------------- | ---------- |
| Exact dataset name on Kaggle | Urdu News Dataset (subtitle: “1 Million Urdu News Stories Corpus”) | Page title verified |
| Kaggle compiler / page owner | Saurabh Shahane | Kaggle profile on the dataset page |
| Kaggle URL | https://www.kaggle.com/datasets/saurabhshahane/urdu-news-dataset | Verified |
| Kaggle version shown | Version 1 | Data Explorer: “Version 1 (276.79 MB)” |
| Kaggle file name | `urdu-news-dataset-1M.csv` | Verified on page |
| Kaggle displayed size | 276.79 MB | Verified |
| Local `data/urdu_news.csv` size | 276,791,832 bytes = 276.79 MB (decimal) | Verified locally |
| Kaggle columns | Index, Headline, News Text, Category, Date, URL, Source, News length | Verified (8 of 8) |
| Local precursor columns | Same eight names | Verified |
| Kaggle URL-column count | 111,861 | Verified on page |
| Local precursor rows | 111,861 | Verified previously |
| Kaggle Source mix | Geo News 35%, Dawn News 34%, Other 31% (Other count 34,603) | Verified on page |
| Local clean Source mix | Geo News 38,881; Dawn News 38,377; Ab Tak + 92 News + Express = 34,602 | Verified in CSV; “Other” off by 1 vs Kaggle, consistent with dropping one precursor row |
| Byte-identical SHA-256 vs Kaggle file | **NOT VERIFIED** | File was not downloaded |

Kaggle Acknowledgements (verbatim on the page, 6 September 2026):

> Hussain, Khalid; Mughal, Nimra; Ali, Irfan; Hassan, Saif; Daudpota, Sher Muhammad (2021), “Urdu News Dataset 1M”, Mendeley Data, V3, doi: 10.17632/834vsxnb99.3

In-repo historical notes call this “Kaggle Urdu News Dataset (Shahane, 2020)”. Kaggle `dateModified` in page metadata was 2021-03-27. Year **2020** is **NOT VERIFIED**.

### Layer B — Acknowledged upstream compilation (Mendeley)

| Field | Verified value |
| ----- | -------------- |
| Exact dataset name | Urdu News Dataset 1M |
| Mendeley URL (V3, cited by Kaggle) | https://data.mendeley.com/datasets/834vsxnb99/3 |
| Version-3 DOI | **10.17632/834vsxnb99.3** |
| Concept DOI | 10.17632/834vsxnb99 (HasVersion .1, .2, .3, .4) |
| V3 issued | 27 January 2021 (DataCite date Issued; Mendeley “Published”) |
| Latest version seen | Version 4, DOI 10.17632/834vsxnb99.4, published 14 August 2024 |
| Publisher | Mendeley / Mendeley Data (DataCite) |
| Institution on Mendeley page | Sukkur Institute of Business Administration |
| Description | “above 1 Million Urdu news stories”; four categories: Business & Economics, Science & Technology, Entertainment, Sports |

**Authorship (do not collapse these lists):**

- Kaggle acknowledgements / citation string: Khalid Hussain; Nimra Mughal; Irfan Ali; Saif Hassan; Sher Muhammad Daudpota (2021), V3.
- DataCite for **V3** (`10.17632/834vsxnb99.3`): creator listed as **Saif Hassan** only; contributors Khalid Hussain, Nimra Mughal, Irfan Ali, Sher Muhammad Daudpota.
- DataCite for **concept DOI and V4**: Khalid Hussain, Nimra Mughal, Wahaj Hassan, Irfan Ali, Sher Muhammad Daudpota, Saif Hassan.
- HTML scrape of Mendeley V3 “Contributors” was incomplete (blank name slots). Treat DataCite + Kaggle citation as the usable records; do not invent a single canonical author string without human choice.

**Source description (what the depositors wrote):** Mendeley “Steps to reproduce” (V1, V3, and V4, same wording retrieved): major Urdu news sources in those four categories were identified; scraping policies were reviewed where available; custom Beautiful Soup / Requests scripts; preprocessing kept “Urdu text and numbers only.”

**Named outlets Geo / Dawn / Ab Tak / 92 News / Express:**

- **Verified in ULTRA’s frozen CSV** `Source` column (and Kaggle explorer names Geo News and Dawn News explicitly).
- **NOT VERIFIED** as a named list on the Mendeley or DataCite records. Those records say “major Urdu news sources,” not those five mastheads.

**1 Million vs ~111,861 rows:**

- Mendeley/Kaggle **prose** says above one million stories.
- The **Kaggle file actually previewed** is ~111,861 rows / 276.79 MB.
- Mendeley **file listing and file sizes were not visible** in the retrieved HTML (“Files” section empty). DataCite `sizes` arrays are empty.
- Whether Mendeley hosts a true 1M-row dump, and whether the Kaggle CSV is a subset or a misnamed 111k extract, is **NOT VERIFIED**.
- This repository contains **no** script that subsets 1M → 111,861.

---

## 3. License

### What the deposit pages currently state (verified as page text, not as legal sufficiency)

| Source | Stated license | License URL on record |
| ------ | -------------- | --------------------- |
| Kaggle dataset page | “Attribution 4.0 International (CC BY 4.0)” | Kaggle schema.org also pointed at https://creativecommons.org/licenses/by/4.0/ |
| Mendeley V3 and V4 pages | “Licence: CC BY 4.0” | Page control “Learn more” (full legalcode not inlined on the scrape) |
| DataCite V3, V4, concept DOI | SPDX `cc-by-4.0`; rights: “Creative Commons Attribution 4.0 International”; `rightsUri` https://creativecommons.org/licenses/by/4.0/legalcode (and a shorter `/by/4.0/` form in XML) | Verified via DataCite API |

Exact name: **Creative Commons Attribution 4.0 International**.  
Exact version: **4.0**.  
SPDX: **CC-BY-4.0**.

### What CC BY 4.0 would mean **if** the licensor actually held the licensed rights

From the legal code (retrieved 6 September 2026), not from a blog:

- **Share:** reproduce and Share the Licensed Material, in whole or in part (Section 2(a)(1)(A)).
- **Adapted Material:** produce, reproduce, and Share Adapted Material (Section 2(a)(1)(B)).
- **Commercial use:** the grant is not limited to non-commercial use. The CC BY 4.0 deed states sharing “for any purpose, even commercially.”
- **Attribution (Section 3(a)):** if you Share, retain creator identification, copyright notice, license notice, warranty disclaimer, and a URI to the material when supplied; indicate modifications; indicate the CC BY 4.0 license.
- **Critical limiter (Section 1, Licensed Rights):** rights granted are only those Copyright and Similar Rights **that the Licensor has authority to license**.
- **Critical limiter (CC “Considerations for the public”):** “Our licenses grant only permissions under copyright and certain other rights that a licensor has authority to grant. Use of the licensed material may still be restricted for other reasons, including because others have copyright or other rights in the material.”
- **Warranty (Section 5):** material is as-is; includes disclaimer of non-infringement.

This inspection does **not** treat the CC BY badge as proof that news publishers licensed the article bodies.

### Conflicting dataset-specific language (flagged, not resolved)

Mendeley “Steps to reproduce” (V1, V3, V4), retrieved 6 September 2026:

> The web scrapping policies of these new sources carefully evaluated where available in place before scrapping news stories and **found that content can be used for non-commercial research purpose only by crediting the news source.**

That sentence is **more restrictive than CC BY 4.0** (non-commercial vs any purpose including commercial; “credit the news source” in addition to dataset-author attribution).

**Apparent conflict: CC BY 4.0 vs non-commercial research + credit the news source.**  
This verification does **not** choose which text controls. Both appear on the same Mendeley records that also display CC BY 4.0.

Kaggle’s license badge is CC BY 4.0 and does not repeat the non-commercial scrape sentence on the retrieved page. Kaggle still points acknowledgements at Mendeley V3, which does contain that sentence.

### ULTRA repository

- No `LICENSE` file.
- No in-repo dataset license statement.
- Manuscript DAS currently says GitHub availability “with no redistribution restrictions.” That statement is **outside** this verification’s edit scope; it is **not** supported by the sources above (CC BY is not “no restrictions”; third-party news copyright is uncleared; GitHub does not host the CSV).

---

## 4. Underlying News Content

### A. License granted by dataset creator / compiler

- **Mendeley depositors** applied a CC BY 4.0 label to “Urdu News Dataset 1M” (DataCite + Mendeley page).
- **Saurabh Shahane** applied a CC BY 4.0 label to the Kaggle mirror and cited the Mendeley V3 DOI.
- What they can actually license is limited to rights they hold (database compilation, their own preprocessing). **Whether they hold copyright in the article text: NOT VERIFIED.**

### B. Copyright held by original news publishers

- Frozen CSV `Source` values: Geo News, Dawn News, Ab Tak News, 92 News, Express News.
- Those organizations’ copyright in the article bodies is **not** assigned to ULTRA in this repository.
- No publisher license, terms-of-use excerpt, or written permission file is in the repo.
- Mendeley itself describes the text as scraped from news sites and, in the scrape note, limited to non-commercial research with credit.
- **Redistribution rights for underlying article text: NOT VERIFIED.**

### C. Permission to redistribute the dataset (the compilation as hosted by Kaggle/Mendeley)

- The compilers already host files on Kaggle and Mendeley under a CC BY 4.0 badge.
- Whether **this project** may re-host the same bytes elsewhere depends on (A) and (B) plus the non-commercial scrape note. **NOT VERIFIED.**

### D. Permission to redistribute a cleaned/derived copy (`clean_articles.csv`)

- ULTRA’s documented changes are: drop one null row; concatenate `Headline + ' ' + News Text`; write a new CSV. That is Adapted Material in CC terms **if** CC BY validly covers the text.
- Cleaning does not create a new copyright that overrides publisher rights in the news text.
- **NOT VERIFIED.**

Do not equate “dataset page says CC BY” with “every article can safely be redistributed.”

---

## 5. ULTRA Data Pipeline

```
[A] Mendeley “Urdu News Dataset 1M” (described as >1M stories; file bytes NOT VERIFIED)
        ↓  Kaggle acknowledgement cites V3 DOI 10.17632/834vsxnb99.3
[B] Kaggle Saurabh Shahane, Version 1, file urdu-news-dataset-1M.csv
        size 276.79 MB, ~111,861 rows, 8 columns
        ↓  download / rename  — NOT DOCUMENTED IN THIS REPOSITORY
[C] data/urdu_news.csv
        111,861 rows; 276,791,832 bytes
        SHA-256 (local, previously computed): 7662b6e8508ccb080bbb9adcb5678388a363a94f67fff44102551c7cc7926062
        gitignored; not on GitHub
        ↓  archive/historical_experiments/notebooks/01_preprocessing.ipynb
[D] data/clean_articles.csv
        111,860 rows; 540,050,203 bytes
        SHA-256 8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231
        gitignored; not on GitHub
```

### Where `urdu_news.csv` came from

| Question | Finding |
| -------- | ------- |
| Documented download command / URL in publication-branch docs? | **No. REPRODUCTION GAP.** |
| Script that fetched Kaggle/Mendeley? | **No. REPRODUCTION GAP.** |
| In-repo statement that the file is the Kaggle CSV? | Historical notes say “Kaggle Urdu News Dataset (Shahane, 2020)” (`archive/historical_experiments/notebooks/07_evaluation.ipynb`; `archive/historical_figures/results_layer_a/_archive_development_cv/evaluation_report.txt`). They do not pin Version 1, filename `urdu-news-dataset-1M.csv`, or a hash. |
| Match to Kaggle explorer (size, columns, 111,861 URLs, Geo/Dawn mix)? | Strong circumstantial match. **SHA-256 vs Kaggle: NOT VERIFIED.** |
| Match to Mendeley 1M dump? | **NOT VERIFIED. REPRODUCTION GAP** (description says 1M; local/Kaggle file is ~111k). |

`data/README.md` only calls `urdu_news.csv` a “generated or precursor” artifact. It does not name Kaggle or Mendeley.

### `urdu_news.csv` → `clean_articles.csv`

Evidence: `archive/historical_experiments/notebooks/01_preprocessing.ipynb` (saved outputs) and `archive/historical_experiments/phase3_retrieval/ARCHITECTURE_AUDIT.md`.

| Step | Done? | Evidence |
| ---- | ----- | -------- |
| Load `../data/urdu_news.csv`, UTF-8-SIG, `encoding_errors='replace'` | Yes (notebook) | Cells + printed shape `(111861, 8)` |
| Force column names to the eight Kaggle/Mendeley-style names | Yes | Notebook |
| `df.dropna()` then `reset_index(drop=True)` | Yes | Printed “After cleaning: 111860 articles” |
| Deduplicate | **No** | Manuscript Corpus subsection and architecture audit: near-duplicates left in |
| Unicode/NFKC, stemming, stopword, HTML strip | **No** | Same |
| `combined_text = Headline + ' ' + News Text` | Yes | Notebook |
| `to_csv(..., index=False, encoding='utf-8-sig')` | Yes | Notebook |
| 111,861 → 111,860 | **Documented in notebook outputs** as one `dropna()` | Independent csv empty-string scan previously found 0 empty fields; the dropped row is likely a pandas NA, not an empty string. Exact dropped index: **NOT re-identified** in this verification |
| Publication-branch reconstruct script | **No. REPRODUCTION GAP.** | Only the archived notebook |

**Can the final corpus be deterministically reconstructed from a public download?**

**REPRODUCTION GAP.** Missing: pinned public file hash; documented download; 1M-vs-111k explanation if Mendeley differs; non-archived reconstruct script; pandas/`encoding_errors='replace'` pin. Local freeze file is a fixed byte string and **is** independently verifiable **if** a researcher already possesses it (SHA-256 match).

No dataset, notebook, or manuscript was modified to close these gaps.

---

## 6. Redistribution Decision Table

Answers below are **legal permission to redistribute**, except PLOS SI, which is also subject to an official size cap.  
Allowed values only: **VERIFIED YES** / **VERIFIED NO** / **NOT VERIFIED**.

| Asset | Redistributable? | Evidence | Confidence |
| ----- | ---------------- | -------- | ---------- |
| Original dataset (Mendeley/Kaggle compilation as they host it) | NOT VERIFIED | They already host it under a CC BY 4.0 badge; scrape note says non-commercial + credit news source; CC grants only rights the licensor can grant; publisher copyright in article text uncleared | Low for “we may re-host”; hosting by original depositors is a fact, not our license |
| `urdu_news.csv` | NOT VERIFIED | Local copy of an apparent Kaggle file; no independent grant to ULTRA; same third-party text issue | Low |
| `clean_articles.csv` | NOT VERIFIED | Derived by null-drop + concatenation; still full article text; no written publisher or compiler permission to rehost the derived file | Low |
| Kaggle upload (derived 111,860-row CSV) | NOT VERIFIED | Would be a new public copy of news text. CC BY badge on the *source* page is not written permission for this upload. Conflict with non-commercial scrape note unresolved | Low |
| GitHub upload | NOT VERIFIED | Legal: same as above. Technical: GitHub blocks git files > 100 MiB (official docs); 515 MB cannot be a normal git blob. LFS/Releases are separate technical paths and still lack legal clearance | Low legally; git-blob path fails on size |
| Zenodo (or similar PID repo) | NOT VERIFIED | Same legal gap. PLOS also says repository licenses should not be more restrictive than CC BY — which collides with a non-commercial scrape note and with uncleared publisher copyright | Low |
| PLOS Supporting Information | VERIFIED NO | Official PLOS submission guidelines: SI files must be smaller than 20 MB. Corpus is 540,050,203 bytes. Size policy fails even before license. (License would separately be NOT VERIFIED.) | High for the size rule |

PLOS SI, if size were ignored, would still not be a verified-yes legal path: PLOS publishes SI and deposits it on figshare, and PLOS licenses/copyright policy requires third-party content to be public domain or CC BY-compatible, or to have written permission for CC BY 4.0 publication.

---

## 7. PLOS Data Availability Strategy

Official PLOS Data Availability (retrieved 6 September 2026): share the minimal data needed to replicate findings; restrictions only if legal/ethical; third-party data that authors cannot legally distribute must be described with source, permission if applicable, how others obtain access, known restrictions, and citation. Author cannot be the sole long-term access contact for restricted data. Repository licenses should not be stricter than CC BY.

Official PLOS Licenses and Copyright: third-party content in the manuscript/SI needs public-domain or CC BY-compatible rights, or written permission to publish under CC BY 4.0. PLOS staff will not give legal advice on third-party licenses. “Don't assume that you can use any content you find on the Internet.”

Do **not** rewrite the DAS in this verification. What PLOS would require:

### Scenario A — Permission confirmed (human/rightsholder says redistribution under a PLOS-compatible license is allowed)

- Deposit the **exact** `clean_articles.csv` bytes (verify SHA-256 `8992a6ac…`) in a repository with a PID.
- State the license actually granted (if it is CC BY, meet attribution: Hussain et al. / Shahane / news sources as the grant requires).
- Cite the original dataset DOI in the reference list.
- Keep evaluation files (queries, qrels, freeze JSON) public.
- Do not put the 515 MB CSV in SI.

This scenario is **not** available today.

### Scenario B — Permission denied (rightsholder says do not redistribute article text)

- Use PLOS **third-party data** DAS: name Kaggle + Mendeley, DOI, how a reader obtains the same public file, known restrictions (including the non-commercial scrape note if it still applies), and that ULTRA will not rehost the corpus.
- Provide reconstruction instructions and the freeze checksum so a reader who obtains the source can verify `8992a6ac…`.
- Share everything ULTRA **can** legally share: code, dictionary, query files, qrels, metrics tables (SI if < 20 MB).
- Point access at the existing public Kaggle/Mendeley deposit, not at a corresponding-author inbox as the only path.

### Scenario C — Permission unclear (**current state**)

- Do **not** upload the corpus.
- Do **not** claim “no redistribution restrictions.”
- Do **not** claim GitHub contains `clean_articles.csv`.
- For submission, PLOS still needs an honest DAS. The safe pattern until confirmation is Scenario B language plus an explicit statement that redistribution rights for the article text are **not verified**, plus how others can access the third-party source **in the same manner as the authors** (Kaggle/Mendeley download).
- Ask PLOS (`plosone@plos.org`) only after the supervisor/IP office decides; PLOS will not clear publisher copyright for you.
- Close the reconstruct gaps only if instructed later (this verification does not implement them).

Current manuscript DAS is Scenario-A language without Scenario-A facts. That is a submission risk. This file does not edit it.

---

## 8. Remaining Human Confirmation

Only items that genuinely need a person (not another web scrape):

### Dataset creator / compiler

- Hussain / Mughal / Ali / Hassan / Daudpota (and Wahaj Hassan on V4): did they intend CC BY 4.0 to cover **full article bodies**, or only the compilation/metadata? How should the non-commercial scrape note be read against CC BY?
- Saurabh Shahane: is `urdu-news-dataset-1M.csv` (111,861 rows) a full copy of Mendeley V3, a subset, or a different extract? May ULTRA cite and reconstruct from Version 1 of that Kaggle dataset?

### Original news publishers

- Geo, Dawn, Ab Tak, 92 News, Express (or their rights offices): permission to **rehost** full article text in a derived CSV, and to allow PLOS/figshare/Zenodo CC BY republication, if that is even requested.  
  If the strategy is “do not redistribute; point at Kaggle/Mendeley,” publisher rehosting permission may not be required for DAS, but **use** of scraped text for the research still sits on the compilers’ scrape-policy claim. Confirm with supervisor/IP whether that is enough for Air University.

### University / supervisor

- Which DAS scenario to adopt (A vs B/C).
- Whether Air University treats this as third-party news text that must not be rehosted.
- Whether to contact `plosone@plos.org` after that decision.
- Correct bibliographic form (V3 vs V4; DataCite creator-list vs Kaggle citation string).

### Legal / IP office

- Whether CC BY on Mendeley/Kaggle is a reliable license for **this** re-use and any rehosting.
- How to treat the CC BY vs non-commercial conflict.
- Whether a derived 111,860-row file can be deposited under CC BY (PLOS repository rule) without infringing publisher copyright.
- Written permission vs “do not redistribute” strategy.

This verification does not contact those parties.

---

## 9. Exact Blockers

| # | Severity | Evidence | Why it matters | Recommended next action |
| - | -------- | -------- | -------------- | ----------------------- |
| 1 | BLOCKER | Mendeley CC BY 4.0 **and** “non-commercial research purpose only by crediting the news source” on the same records | Cannot honestly tell PLOS the corpus is unrestricted CC BY, or that it is clearly non-commercial only | Human/IP reading of the conflict; do not upload meanwhile |
| 2 | BLOCKER | CC BY 4.0 legal code: license covers only rights the licensor can grant; others may hold copyright in the material | News article text is publisher content; compiler badge is not publisher permission | Rightsholder or IP-office confirmation before any rehost |
| 3 | BLOCKER | No written permission in-repo from Geo / Dawn / Ab Tak / 92 News / Express | PLOS copyright policy for third-party content requires public-domain/CC BY-compatible rights or written permission if the text is published with the article/SI/data under CC BY | Choose Scenario B/C DAS **or** obtain written permission for Scenario A |
| 4 | BLOCKER | Current DAS (not edited here) claims GitHub + “no redistribution restrictions”; GitHub `data/` has no CSV | False availability statement is a PLOS data-policy failure | After this verification: rewrite DAS only when instructed; do not upload to make the false claim “true” |
| 5 | IMPORTANT | Kaggle file ~111,861 rows vs prose “1 Million”; Mendeley file bytes **NOT VERIFIED** | Readers cannot be told, with a pin, which public file is the precursor | Confirm with whoever downloaded `urdu_news.csv`; optionally hash a fresh Kaggle Version 1 download **without replacing** the frozen corpus |
| 6 | IMPORTANT | `01_preprocessing.ipynb` only, under `archive/`; no download recipe | **REPRODUCTION GAP** for exact SHA-256 from public sources | Document pin + reconstruct later; do not change `clean_articles.csv` |
| 7 | IMPORTANT | PLOS SI 20 MB cap vs 515 MB corpus | SI cannot carry the corpus even if license were clear | Never plan SI for the full CSV |
| 8 | MINOR | DataCite V3 creator list ≠ Kaggle citation author list ≠ V4 creator list | Attribution under CC BY would be ambiguous | Supervisor picks the citation string from DataCite/Kaggle, does not invent one |

---

## What this verification did not do

- Did not download Kaggle or Mendeley binaries (so Kaggle SHA-256 remains **NOT VERIFIED**).
- Did not contact compilers, publishers, or PLOS.
- Did not modify the manuscript, DAS, dataset, M0, Phase 12, labels, or metrics.
- Did not upload the corpus anywhere.

Redistribution rights for underlying article text: **NOT VERIFIED.**
