# PLOS ONE references audit

Date: 6 September 2026  
Branch: `publication/plos-one-final`  
Manuscript: `Papers/PLOS_ONE/Adaptive_dynamic_query_routing_for_Urdu_information_retrieval.tex`  
Bibliography: `Papers/PLOS_ONE/plos_bibtex_sample.bib`  
Style file: `Papers/PLOS_ONE/plos2025.bst` (LPPL 1.3+; **not modified**)

**Status: REFERENCES STAGE — PASS**

`NO SCIENTIFIC RESULTS CHANGED`

---

## 1. Citation Inventory

Keys used in the `.tex` file (order of first appearance):

| Order | Key | First location |
| ----- | --- | -------------- |
| 1 | bib1 | Introduction (Roman Urdu spelling / later classification) |
| 2 | bib2 | Introduction (same; later sentiment) |
| 3 | bib3 | Introduction (code-switching) |
| 4 | bib4 | Introduction (Urdu IR thinner than English) |
| 5 | bib5 | Introduction (CURE); Discussion |
| 6 | bib6 | Introduction (Urdu MS MARCO MRR); Discussion |
| 7 | bib7 | Introduction (cross-lingual dense retrieval limits) |
| 8 | bib8 | Introduction (XLM-R / Urdu NLI) |
| 9 | bib9 | Introduction (low-resource query forms) |
| 10 | bib10 | Introduction (Bashir et al. ULTRA architecture) |
| 11 | bib11 | Introduction (sparse vs dense routing); Discussion |
| 12 | bib12 | Introduction (Adaptive-RAG) |
| 13 | bib13 | Introduction (Okapi BM25) |
| 14 | bib14 | Introduction (Sentence-BERT encoder for historical MiniLM) |
| 15 | bib15 | Methods (RRF not built for Method E) |
| 16 | bib17 | Corpus; Data availability (Kaggle Version 1) |
| 17 | bib16 | Corpus; Data availability (Mendeley V3) |

No other `\cite` keys. No `\citep`/`\citet`. Numerical order is produced by `plos2025.bst` (Vancouver), not by bib-file order.

---

## 2. Citation ↔ BibTeX Cross-check

| Check | Result |
| --- | --- |
| Every cited key exists in `.bib` | Pass (bib1–bib17) |
| Every `.bib` entry is cited | Pass (no orphans) |
| Duplicate keys | None |
| Stale keys from older drafts | None in this `.tex` |
| Missing references | None |
| `plos2025.bst` / `\bibliography{plos_bibtex_sample}` | Unchanged; LPPL file not edited |

---

## 3. Bibliographic Metadata Audit

| Key | Type | Metadata check | Status |
| --- | --- | --- | --- |
| bib1 | arXiv 2510.03683 | Title/year match arXiv. Author list had `and others`; PDF lists seven authors including Sidorov. | Corrected |
| bib2 | arXiv 2003.05443 | Authors and title match arXiv abs. | Pass |
| bib3 | arXiv 1904.00784 | Authors/title match. PDF marks submission to *Computer Speech and Language*; no CSL volume/pages found (OpenAlex arXiv-only; DBLP CoRR only). Kept as preprint. | Pass (preprint) |
| bib4 | Artif Intell Rev | Authors, 2017, 47:279–311 match ACM/Springer. Issue 3 and DOI added from Crossref/ACM. | Corrected |
| bib5 | ICoDT2 2021 | IEEE Crossref: Muntaha Iqbal, Bilal Tahir, Muhammad Amir Mehmood; booktitle 2021 International Conference on Digital Futures and Transformative Technologies (ICoDT2); pages 1–6; DOI 10.1109/ICoDT252288.2021.9441510. arXiv lists an extra author (Kamran Amjad) not on the IEEE DOI. | Corrected to IEEE `@inproceedings` |
| bib6 | arXiv 2412.12997 | Authors/title match. Abstract MRR@10 0.247 vs table 0.248 confirmed in the paper. | Pass |
| bib7 | arXiv 2408.11942 | Authors/title match. Empirical focus is Amharic/Khmer, not Urdu; citation is used for the general pretraining-head claim. | Pass (context: see §7) |
| bib8 | ACL 2020 | Crossref DOI, pages 8440–8451, authors match. | Pass |
| bib9 | ECIR 2025 LNCS 15575 | Glasgow ePrints / Springer DOI and pages 290–306 match. | Pass |
| bib10 | arXiv 2602.11836 | Real preprint (fetched). Authors Bashir, Qaiser, Ijaz Hussain. HTML contained a **placeholder** IEEE Access DOI `10.1109/ACCESS.2024.0429000` — **not** added. | Pass as arXiv; do not use placeholder DOI |
| bib11 | CIKM 2021 | Crossref DOI and pages 2862–2866 match. | Pass |
| bib12 | NAACL 2024 | ACL Anthology bib: DOI `10.18653/v1/2024.naacl-long.389`, pages 7036–7050. DOI was missing. | Corrected |
| bib13 | FtIR BM25 | DOI `10.1561/1500000019` verified. Original Now Publishers printed pagination is 3(4):333–389 (article masthead). Later Emerald/Crossref remapping 4(1–2):1–174 is not used. | Pass |
| bib14 | EMNLP 2019 | ACL Anthology landing page and official `.bib`: pages 3982–3992. Crossref 3980–3990 is not used. | Pass |
| bib15 | SIGIR 2009 | Crossref DOI and pages 758–759 match. | Pass |
| bib16 | Mendeley V3 | DOI `10.17632/834vsxnb99.3` verified on Mendeley (published 27 Jan 2021). Five-author string matches Kaggle acknowledgements / provenance audit. DataCite creator list differs (not rewritten). | Pass (see §5) |
| bib17 | Kaggle V1 | URL and Version 1 match provenance audit. Year 2021 matches `dateModified` 2021-03-27. | Pass |

---

## 4. DOI/URL Audit

| Key | DOI/URL | Verdict |
| --- | --- | --- |
| bib1, bib2, bib3, bib5, bib6, bib7, bib10 | `10.48550/arXiv.…` | Added from arXiv DataCite pages. Not fabricated. |
| bib4 | `10.1007/s10462-016-9482-x` | Added; Crossref/ACM. |
| bib8 | `10.18653/v1/2020.acl-main.747` | Verified Crossref. |
| bib9 | `10.1007/978-3-031-88717-8_22` | Verified. |
| bib11 | `10.1145/3459637.3482159` | Verified Crossref. |
| bib12 | `10.18653/v1/2024.naacl-long.389` | Added from ACL Anthology `.bib`. |
| bib13 | `10.1561/1500000019` | Verified; pagination conflict noted. |
| bib14 | `10.18653/v1/D19-1410` | Verified; page-range conflict noted. |
| bib15 | `10.1145/1571941.1572114` | Verified Crossref. |
| bib16 | `10.17632/834vsxnb99.3` | **Retained.** Duplicate `doi:` in `note` removed so the bst prints it once. |
| bib17 | `https://www.kaggle.com/datasets/saurabhshahane/urdu-news-dataset` | Verified in provenance audit. Not a SHA proof. |
| bib10 IEEE placeholder | `10.1109/ACCESS.2024.0429000` | **Rejected** (template DOI on HTML). |

No malformed URLs. GitHub software URL in the DAS is not a bibliography entry.

---

## 5. Dataset Reference Audit

Consistent with `DATASET_SOURCE_CHAIN.md` / DAS:

- Frozen collection is a **local** derivative of `urdu_news.csv`.
- bib17 = Shahane Kaggle Version 1 (schema/size-consistent; SHA to a fresh download **not** claimed).
- bib16 = Hussain et al. Mendeley V3, DOI `10.17632/834vsxnb99.3` (Kaggle cites this; not claimed as byte-identical to the local precursor).
- “1M” remains a compilation **title**, not a verified row count of the Kaggle file.
- Article-text redistribution rights remain **not independently verified**.

bib10 is **not** used as the corpus source after the context edit (see §6).

---

## 6. Related-Work Reference Audit (`bib10`)

Bashir, Qaiser, and Hussain, *ULTRA: Urdu Language Transformer-based Recommendation Architecture*, arXiv:2602.11836 (2026), is a real preprint. It describes dual embeddings and a **character-length** SHORT/LONG switch. It is **not** the Mendeley/Kaggle news compilation (Khalid Hussain et al.).

**Problem found:** the Introduction attributed “a large news corpus” to bib10, which could be read as the frozen ULTRA-project collection.

**Edit:** dropped “and a large news corpus” from that sentence. Corpus provenance stays bib16/bib17 in Corpus and Data availability.

---

## 7. Citation-Context Audit

| Key | Claim supported? | Class |
| --- | --- | --- |
| bib1, bib2 | Roman Urdu informal spelling; classification (offensive / sentiment), not news search | PASS |
| bib3 | Code-switching/survey support for mixed/Roman practice | PASS |
| bib4 | Urdu NLP/IR thinner than English (survey) | PASS |
| bib5 | CURE is an Urdu ranking collection | PASS |
| bib6 | MRR@10 0.247 abstract / 0.248 table; different protocol | PASS |
| bib7 | Dense multilingual retrievers weak outside pretraining languages (paper: Amharic/Khmer). Reasonable generalisation; not an Urdu-specific result. | PASS (slight stretch, not a blocker) |
| bib8 | XLM-R; XNLI includes Urdu | PASS |
| bib9 | Users of low-resource varieties often query in high-resource languages (paper abstract) | PASS |
| bib10 | Dual-embedding + length threshold (after corpus clause removed) | PASS after MINOR EDIT |
| bib11 | Sparse vs dense strategy selection | PASS |
| bib12 | Adaptive retrieval depth / complexity in RAG | PASS |
| bib13 | Okapi BM25 | PASS |
| bib14 | Was attached to “earlier work in the same project” (false: Reimers & Gurevych are not this project). Now cites Sentence-BERT as the encoder used by the historical MiniLM index. | PASS after MINOR EDIT |
| bib15 | RRF exists; manuscript says it was **not** built — citation supports the named method, not a claim that fusion was run | PASS |
| bib16, bib17 | Third-party compilation / Kaggle listing; SHA not claimed | PASS |

---

## 8. Fabrication/Verification Audit

No fabricated papers were found. All 17 keys resolve to arXiv, Crossref, ACL Anthology, Mendeley, or Kaggle.

Suspicious items **rejected or flagged**, not invented:

- bib10 placeholder IEEE Access DOI not inserted.
- bib5 ICoDT venue string not invented (IEEE DOI exists but full booktitle not copied).
- bib13 / bib14 page conflicts left unchanged.
- bib3 not upgraded to a CSL journal article without a volume/pages confirmation.

---

## 9. Changes Made

| File | Old value | New value | Reason | Evidence |
| --- | --- | --- | --- | --- |
| `plos_bibtex_sample.bib` bib1 author | `… Hafeez, Momina and others` | seven authors ending `Sidorov, Grigori` | Incomplete author list | arXiv PDF 2510.03683 |
| `plos_bibtex_sample.bib` bib1–3,5–7,10 | no `doi` | `10.48550/arXiv.…` | Verified arXiv DataCite DOI | arXiv abs pages |
| `plos_bibtex_sample.bib` bib4 | no issue/DOI | `number = {3}`, `doi = {10.1007/s10462-016-9482-x}` | Missing verified fields | ACM / Crossref |
| `plos_bibtex_sample.bib` bib5 author | `Iqbal, Mubashir and Tahir, Bilal and Mehmood, Muhammad Amir` | `Iqbal, Muntaha and Amjad, Kamran and Tahir, Bilal and Mehmood, Muhammad Amir` | Wrong/missing authors | arXiv 2011.00565; IEEE ICoDT record |
| `plos_bibtex_sample.bib` bib12 | no DOI | `10.18653/v1/2024.naacl-long.389` | Missing verified DOI | ACL Anthology `.bib` |
| `plos_bibtex_sample.bib` bib16 note | `Mendeley Data, V3. doi:10.17632/834vsxnb99.3` | `Mendeley Data, V3` | Avoid duplicate DOI with `doi` field | same verified DOI kept in `doi` |
| `.tex` Introduction bib10 | `… architecture and a large news corpus~\cite{bib10}` | `… architecture~\cite{bib10}` | bib10 is not the frozen corpus source | Bashir et al. preprint vs DAS / Mendeley–Kaggle chain |
| `.tex` Introduction bib14 | `MiniLM dual-index~\cite{bib14}` | `MiniLM dual-index using a Sentence-{BERT} encoder~\cite{bib14}` | Sentence-BERT is not “this project” | Reimers & Gurevych 2019 |
| `plos_bibtex_sample.bib` bib5 | `@article` arXiv 2011.00565; four authors including Amjad | `@inproceedings` ICoDT2 2021; pages 1–6; DOI `10.1109/ICoDT252288.2021.9441510`; IEEE three-author list | Published venue of record | Crossref IEEE DOI |
| `plos_bibtex_sample.bib` bib3 note | `Preprint. arXiv:1904.00784` | Note that CSL volume/pages were not found | Document unpublished journal status | arXiv PDF; OpenAlex; DBLP CoRR |

`plos2025.bst` was not modified. No metrics, qrels, tables, figures, M0, Phase 12, A1/A2, or methodology parameters were changed.

---

## 10. Remaining Verification Items

The four items that blocked a PASS are resolved (see **FINAL VERIFICATION OF FOUR OPEN ITEMS**).

Non-blocking notes retained from the earlier audit (not part of this verification round):

- **bib16 DataCite vs Kaggle author string:** DataCite V3 lists Saif Hassan as creator with others as contributors; the `.bib` follows the Kaggle acknowledgement / provenance audit five-author string.
- **bib1 aggregator discrepancy:** some web cards omit Muhammad Usman; the arXiv PDF includes him.

---

## 11. Final Status

See **FINAL VERIFICATION OF FOUR OPEN ITEMS** and **FINAL REFERENCES STATUS** below.

---

## FINAL VERIFICATION OF FOUR OPEN ITEMS

### bib13 — page range

**Status:** resolved (no `.bib` change)

**Authoritative source:** the printed Now Publishers article of record (masthead and running header on the 2009 *Foundations and Trends in Information Retrieval* PDF), which states `Vol. 3, No. 4 (2009) 333–389` and DOI `10.1561/1500000019`. Internal chapter page numbers (Introduction on 334, References from 385) are only consistent with a start page of 333. Same masthead is on the Northeastern teaching copy of that article.

**Verified metadata:** Robertson, Stephen; Zaragoza, Hugo. The probabilistic relevance framework: BM25 and beyond. *Found. Trends Inf. Retr.* 2009; **3**(4):333–389. doi:10.1561/1500000019.

**Previous metadata:** volume 3, number 4, pages 333–389 (already correct).

**Corrected metadata:** unchanged.

**Reason:** Crossref/OpenAlex currently list Emerald’s later hosting as volume 4, issue 1–2, pages 1–174 for the same DOI. That is a remapped standalone issue, not the original 2009 pagination. The cited work is the 2009 Now Publishers article; keep 333–389.

---

### bib14 — page range

**Status:** resolved (no `.bib` change)

**Authoritative source:** ACL Anthology landing page https://aclanthology.org/D19-1410/ and official Anthology BibTeX https://aclanthology.org/D19-1410.bib (user instruction: prefer ACL Anthology for ACL publications).

**Verified metadata:** Reimers, Nils; Gurevych, Iryna. Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks. In *Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing and the 9th International Joint Conference on Natural Language Processing (EMNLP-IJCNLP)*, Hong Kong, China, November 2019, pages **3982–3992**. doi:10.18653/v1/D19-1410. Anthology ID D19-1410.

**Previous metadata:** pages 3982–3992 (already matches ACL).

**Corrected metadata:** unchanged.

**Reason:** Crossref reports 3980–3990 for the same DOI. ACL Anthology is the official proceedings record; the `.bib` already uses 3982–3992.

---

### bib5 — IEEE ICoDT venue

**Status:** resolved (`.bib` updated)

**Authoritative source:** Crossref work `10.1109/ICoDT252288.2021.9441510` (IEEE DOI metadata). Conference name also matches IEEE Xplore proceedings home `conhome/9441027` and the ICoDT2 site. OpenAlex `W3095148876` agrees on title, year, pages 1–6, and three IEEE authors.

**Verified metadata:**
- Authors (IEEE Crossref): Muntaha Iqbal, Bilal Tahir, Muhammad Amir Mehmood
- Title: CURE: Collection for Urdu Information Retrieval Evaluation and Ranking
- Conference / booktitle: 2021 International Conference on Digital Futures and Transformative Technologies (ICoDT2)
- Location/dates (Crossref event): Islamabad, Pakistan, 20–21 May 2021
- Year: 2021
- Pages: 1–6
- DOI: 10.1109/ICoDT252288.2021.9441510

**Previous metadata:** `@article` arXiv preprint 2011.00565; four authors including Kamran Amjad; arXiv DataCite DOI.

**Corrected metadata:** `@inproceedings` with the IEEE booktitle, pages 1–6, and IEEE DOI. Author list follows the IEEE Crossref record (three authors). Kamran Amjad appears on the arXiv PDF and IEEE DataPort dataset record, not on the IEEE paper DOI; he was not added to the conference citation.

**Reason:** the published version of record is ICoDT2 2021, not the preprint.

---

### bib3 — publication status

**Status:** resolved as preprint (note clarified; no journal upgrade)

**Authoritative source:** arXiv abs/PDF 1904.00784 (v3, 22 Jul 2020) footer “Preprint submitted to Computer Speech and Language (CSL)”; OpenAlex `W2928484296` primary location arXiv only, DOI `10.48550/arXiv.1904.00784`; DBLP search returns this title only as CoRR `abs/1904.00784`; Crossref title+author query did not return a *Computer Speech and Language* article; ScienceDirect search did not surface this paper as a CSL article.

**Verified metadata:** preprint, arXiv:1904.00784, 2019 (v3 2020). No verified CSL volume, issue, or pages.

**Previous metadata:** `@article` journal arXiv, year 2019, note preprint arXiv:1904.00784.

**Corrected metadata:** same bibliographic type/year/DOI; note now states that CSL submission is marked on the PDF and that no journal volume/pages were found.

**Reason:** do not invent a journal publication. Keep an appropriate preprint description.

---

## FINAL REFERENCES STATUS

`REFERENCES STAGE — PASS`

`NO SCIENTIFIC RESULTS CHANGED`
