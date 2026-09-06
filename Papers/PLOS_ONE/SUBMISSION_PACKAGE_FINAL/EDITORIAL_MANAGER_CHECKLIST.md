# PLOS ONE Editorial Manager — upload checklist

Branch: `publication/plos-one-final`  
Printed title: Script-aware BM25 retrieval for Urdu and Roman Urdu news search  
Date prepared: 6 September 2026

PLOS initial submission uses a **PDF** as the manuscript file. Figures and Supporting Information are uploaded as **separate** files. LaTeX source is typically requested after acceptance.

Do **not** upload `data/clean_articles.csv` or `data/urdu_news.csv`.

---

## 1. Article type / files to upload

| EM item | File in this package | Notes |
| --- | --- | --- |
| Manuscript (initial) | `manuscript/Adaptive_dynamic_query_routing_for_Urdu_information_retrieval.pdf` | 14 pages; captions in PDF; **no** embedded figure images (PLOS LaTeX rule) |
| Figure 1 | `figures/Fig1.tif` | Upload as Fig 1 |
| Figure 2 | `figures/Fig2.tif` | Upload as Fig 2 |
| Figure 3 | `figures/Fig3.tif` | Upload as Fig 3 |
| Figure 4 | `figures/Fig4.tif` | Upload as Fig 4 |
| Figure 5 | `figures/Fig5.tif` | Upload as Fig 5 |
| S1 Table | `supporting_information/S1_table.csv` | |
| S2 Table | `supporting_information/S2_table.csv` | Official A1 labels |
| S3 Table | `supporting_information/S3_table.csv` | |
| S4 Table | `supporting_information/S4_table.csv` | A1 vs A2; A2 is reliability only |
| S1 File | `supporting_information/S1_file.json` | Freeze manifest |
| S2 File | `supporting_information/S2_file.md` | A2 reliability analysis |
| S3 File | `supporting_information/S3_file.md` | Provenance; **no article text** |
| S1 Text | `supporting_information/S1_text.md` | A1 annotation protocol |

After acceptance (source files; not required at initial PDF upload):

| File | Purpose |
| --- | --- |
| `manuscript/Adaptive_dynamic_query_routing_for_Urdu_information_retrieval.tex` | Single-file LaTeX source (PLOS template 3.8) |
| `manuscript/plos_bibtex_sample.bib` | Audited bibliography (filename matches `\bibliography{plos_bibtex_sample}`) |
| `manuscript/plos2025.bst` | PLOS Vancouver style; **do not edit** |

---

## 2. Title and authors (EM manuscript data)

| Field | Value |
| --- | --- |
| Full title | Script-aware BM25 retrieval for Urdu and Roman Urdu news search |
| Short title | Script-aware BM25 for Urdu news search |
| Author 1 | Hashim Shazad (corresponding) |
| Author 2 | Adnan Aslam |
| Author 3 | Areena Rahman |
| Affiliation (all) | Department of Creative Technologies, Air University, Islamabad, Pakistan |
| Corresponding email | abbasihashim30@gmail.com |
| ORCID | USER TO ENTER (in EM; not invented here) |

Do not add degrees or invented affiliations.

---

## 3. Portal-only declarations (do **not** put these back into the `.tex` body)

The supplied PLOS template 3.8 / PLOS guidelines treat these as Editorial Manager fields.

### Funding

No specific funding was received for this work.

### Competing interests

The authors have declared that no competing interests exist.

### Author contributions (CRediT)

- **Hashim Shazad:** Conceptualization, Methodology, Software, Formal analysis, Writing – original draft, Writing – review & editing.
- **Adnan Aslam:** Supervision, Writing – review & editing.
- **Areena Rahman:** Validation (independent A2 relevance annotation as a reliability check only; A2 does not replace official A1 Success@5 of 23/40). User prompt phrasing “model evaluation” maps to this CRediT Validation role.

### Ethics

Do **not** enter IRB approval, exemption, consent, or human-subjects approval. The manuscript Methods ethics subsection is the conservative statement.

---

## 4. Data Availability Statement (paste into EM)

Also retained in Methods for reviewers.

The retrieval collection is a locally processed copy of a third-party Urdu news compilation titled Urdu News Dataset 1M (Mendeley Data V3, doi:10.17632/834vsxnb99.3), schema- and size-consistent with Shahane, Urdu News Dataset, Kaggle Version 1, file urdu-news-dataset-1M.csv. A SHA-256 identity check between a fresh provider download and the local precursor was not completed. The frozen file used for all official M0 scores is data/clean_articles.csv (111,860 articles; 540,050,203 bytes; SHA-256 8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231). The authors do not redistribute the full article-text CSV. Redistribution permission for the underlying news article text has not been independently verified. Researchers should obtain the source from Kaggle and/or Mendeley under those providers’ terms, then verify reconstructions against that SHA-256. The Roman Urdu dictionary, M0 code, sealed queries, qrels, and REPRODUCE.md are at https://github.com/HashimAbbasii/Dynammic-Query-Routing-Urdu-ILS (branch publication/plos-one-final). A git clone does not contain the article-text corpus.

---

## 5. Do not upload

- `data/clean_articles.csv`
- `data/urdu_news.csv`
- Any Chroma / embedding / 644,100-vector index
- `research/post-phase12` artifacts
- Tectonic or other TeX binaries
- Internal `experiments/publication_audit/` notes (unless a reviewer asks)
- `supporting_information/README.md` (local packaging note; not an SI item)
- Old `SUBMISSION_PACKAGE` zip files

---

## 6. Official numbers (do not retype incorrectly)

- Freeze-pool ExactSource Hit@5 = 68/78 = 87.18%; nDCG@5 = 0.8107; MRR = 0.797
- K Hit@5 = 27/40 = 67.50% (Hit@1 20/40; Hit@10 28/40; Hit@50 30/40)
- U official A1 Success@5 = 23/40 = 57.50%
- A2 Success@5 = 26/40 is reliability only; do not replace or average with A1
