# PLOS ONE Data Availability Statement — recommendation

**Do not paste this into the manuscript until a human reviews it.**  
This file is a draft strategy consistent with facts verified as of 6 September 2026. It does not edit `Papers/PLOS_ONE/Adaptive_dynamic_query_routing_for_Urdu_information_retrieval.tex`.

The live manuscript DAS currently says the news corpus is on GitHub with no redistribution restrictions. That claim is not supported (CSV gitignored; redistribution permission for article text not independently verified).

Official PLOS Data Availability policy (https://journals.plos.org/plosone/s/data-availability): when authors cannot legally distribute third-party data, the DAS must describe the dataset and source, note permission if applicable, explain how others obtain access, state known restrictions, and cite the source. Authors should share analysis-specific files they **can** legally distribute.

---

## Recommended strategy (current human decision)

Do **not** publicly redistribute `data/clean_articles.csv` unless a later human/IP review explicitly allows it.

Treat the 111,860-article file as a **locally processed copy of third-party news text**. Point readers at the public Kaggle/Mendeley records. Identify the freeze with SHA-256. Ship code, dictionary, queries, qrels, and this audit folder.

---

## Facts the DAS may state (already verified)

- Retrieval used `data/clean_articles.csv`: 111,860 articles; 540,050,203 bytes; SHA-256 `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231`.
- Precursor used in project preprocessing: `data/urdu_news.csv`, 111,861 CSV records.
- Transformation: `archive/historical_experiments/notebooks/01_preprocessing.ipynb` (`dropna` + `combined_text = Headline + ' ' + News Text`). No deduplication.
- The last precursor record is truncated (3 of 8 fields); that incomplete row is the 111,861 → 111,860 change on the local files.
- Kaggle: https://www.kaggle.com/datasets/saurabhshahane/urdu-news-dataset (Urdu News Dataset; file `urdu-news-dataset-1M.csv` Version 1 listed at 276.79 MB).
- Kaggle cites Mendeley “Urdu News Dataset 1M”, V3, DOI **10.17632/834vsxnb99.3**.
- Code and Roman dictionary: git repository https://github.com/HashimAbbasii/Dynammic-Query-Routing-Urdu-ILS (branch `publication/plos-one-final` for this freeze).
- Dictionary SHA-256 `30c3f61a64ec641abbb3acdbc7a8bcaf197f0238f1bf9e76c2c7ce8e590f86a3` (198 keys).
- This project does **not** currently claim unrestricted redistribution of the news CSV.
- Redistribution permission for the underlying third-party news text has not been independently verified.
- Supporting Information cannot hold the 515 MB CSV (PLOS: each SI file smaller than 20 MB).

---

## Facts the DAS must **not** state

- That GitHub hosts `clean_articles.csv`.
- That redistribution is unrestricted, CC BY-cleared for article bodies, or “open data” in the PLOS CC BY sense for the news text.
- That the local 111,860-row file is proven byte-identical to a named Mendeley 1M dump.
- Invented committee names, emails, or permission letters.

---

## Proposed DAS text (draft only)

Researchers reproducing the frozen retrieval must use the same document collection. The collection is a locally processed copy of a third-party Urdu news corpus. The processed file used for all official M0 scores is `data/clean_articles.csv` (111,860 articles; 540,050,203 bytes; SHA-256 `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231`).

The precursor file in this project is `data/urdu_news.csv` (111,861 CSV records). It matches, on size and schema, the Kaggle dataset “Urdu News Dataset” (Saurabh Shahane), Version 1 file `urdu-news-dataset-1M.csv` (https://www.kaggle.com/datasets/saurabhshahane/urdu-news-dataset). That Kaggle page cites Hussain, Mughal, Ali, Hassan, and Daudpota, “Urdu News Dataset 1M”, Mendeley Data, V3, doi:10.17632/834vsxnb99.3 (https://data.mendeley.com/datasets/834vsxnb99/3). A SHA-256 identity check between a fresh Kaggle or Mendeley download and the local precursor was not completed for this statement.

Preprocessing was limited to dropping incomplete rows and concatenating headline and body (`combined_text`). The historical notebook is `archive/historical_experiments/notebooks/01_preprocessing.ipynb`. Reproduction notes and a SHA-256 verifier are in `experiments/publication_audit/`.

The authors do not currently redistribute the full article CSV. Redistribution permission for the underlying third-party news text has not been independently verified. Other researchers should obtain the third-party source from Kaggle and/or Mendeley in the same manner as a public download, then verify any reconstructed file against the SHA-256 above. The Roman Urdu dictionary, M0 source code, sealed query files, and human qrels are in the project GitHub repository.

---

## PLOS checklist vs current knowledge

| PLOS third-party DAS element | Status |
| ---------------------------- | ------ |
| Description of the dataset | Can be filled from Kaggle/Mendeley names + n=111,860 freeze |
| Third-party source | Kaggle URL + Mendeley DOI 10.17632/834vsxnb99.3 |
| Verification of permission to use | **REQUIRES HUMAN CONFIRMATION** |
| How others obtain access | Public Kaggle/Mendeley download (Kaggle typically requires an account). **REQUIRES HUMAN CONFIRMATION** that this is the access path the authors actually used |
| Known restrictions | Compiler pages display CC BY 4.0; Mendeley scrape note mentions non-commercial research with credit to the news source; this project does not claim unrestricted redistribution. Do not pick a winner between those license texts without IP review |
| Citation / acknowledgement | Dataset DOI should be added to the reference list when the manuscript is edited. **REQUIRES HUMAN CONFIRMATION** of the exact author string (DataCite V3 vs Kaggle citation vs V4) |
| Author as sole access contact | Not applicable if access is the existing public Kaggle/Mendeley deposit. Do not invent a committee email |
| SI for the 515 MB CSV | Not possible (20 MB cap) |
| Share analysis files the authors can distribute | Dictionary, queries, qrels, freeze JSON, audit markdown — treat as shareable code/metadata (see status report) |

---

## Items that remain REQUIRES HUMAN CONFIRMATION

1. Permission to **use** the third-party corpus for this paper (supervisor/IP; not invented here).
2. Exact bibliographic author list for the data citation.
3. Whether to name the non-commercial scrape sentence in the published DAS (legal reading).
4. Whether a later review allows depositing `clean_articles.csv` under a named license (currently: **do not deposit**).
5. Contacting `plosone@plos.org` — only after (1)–(4), if the editor still asks. Do not add that address as a data-access channel.

---

## When the manuscript is later edited (not now)

Replace the GitHub / “no redistribution restrictions” sentence. Cite the dataset DOI in `plos_bibtex_sample.bib`. Keep official metrics unchanged (U Success@5 23/40 = 57.50%; A2 26/40 = 65.00%; kappas 0.5490 / 0.6816).
