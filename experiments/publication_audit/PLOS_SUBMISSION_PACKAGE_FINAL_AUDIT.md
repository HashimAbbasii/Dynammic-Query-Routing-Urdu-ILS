# PLOS ONE FINAL SUBMISSION PACKAGE AUDIT

**Date:** 6 September 2026  
**Mode:** packaging and submission-readiness only. No new experiments. No retrieval changes. No official-result edits. No commit / push.

Canonical manuscript: `Papers/PLOS_ONE/Adaptive_dynamic_query_routing_for_Urdu_information_retrieval.tex`  
Printed title: **Script-aware BM25 retrieval for Urdu and Roman Urdu news search**  
Fresh package: `Papers/PLOS_ONE/SUBMISSION_PACKAGE_FINAL/`  
Fresh ZIP: `Papers/PLOS_ONE/ULTRA_PLOS_ONE_SUBMISSION_FINAL.zip`

Do **not** upload the older `Papers/PLOS_ONE/SUBMISSION_PACKAGE/ULTRA_PLOS_ONE_FINAL_SUBMISSION.zip`.

---

## 1. Branch

* branch name: `publication/plos-one-final`
* git status: **dirty (uncommitted publication packaging)**; tracks `origin/publication/plos-one-final`
* `git diff --stat` (working tree, not this ZIP): manuscript `.tex`/`.pdf` plus aux/bbl/blg, `README.md`, `REPRODUCE.md`, `docs/REPRODUCIBILITY.md`
* untracked: `SUBMISSION_PACKAGE_FINAL/`, `ULTRA_PLOS_ONE_SUBMISSION_FINAL.zip`, publication-audit markdown including this file
* no merge / cherry-pick / rebase / reset / checkout / push
* no `data/*.csv` added
* no Tectonic binary in the ZIP
* no frozen dumps, qrels, figure binaries, SI CSVs, `plos2025.bst`, or `.bib` scientific edits in this packaging pass

## 2. Scientific freeze

**PASS**

M0 remains deterministic Unicode script detection + BM25 index selection (`k1 = 1.5`, `b = 0.75`; retrieve 50; official cutoff 5). URDU / MIXED / OTHER → Urdu BM25; ROMAN → Method D. Not learned, neural, RL, LLM, or online adaptive routing.

Official numbers in the packaged `.tex`, PDF, SI, and figures match the freeze. A1 remains official U evaluation. A2 remains reliability only.

## 3. Manuscript consistency

**PASS**

Critical freeze strings were searched in the packaged manuscript and SI:

| Value | Location |
| --- | --- |
| 68/78; 87.18%; 0.8107; 0.797 | Abstract, Results, Table 1, Table 2 |
| 27/40; 67.50%; Hit@1 20/40; Hit@10 28/40; Hit@50 30/40 | Table 1, Table 4 |
| 23/40; 57.50%; 0.2050; 0.6460; 0.4542 | Abstract, Table 1, Table 5 |
| 17/18; 6/18; 0/4 | Abstract, Results, Fig 3 |
| A 41, B 26, C 53, D 80, E 0 | Table 5, Fig 5 |
| 26/40; 0.5490; 0.6816 | Limitations + S2 File |
| 135/200 = 67.50%; 169/200 = 84.50%; 65.00% | S2 File (A2 reliability; not Table 1) |
| 111,860; SHA-256 `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231` | Methods Data Availability |
| Fig 2: 0.2564 / 0.2821 / 0.4487 / 0.5897 / 0.8718; oracle 0.9103 | Table 2 + Fig 2 |
| K script 26/28, 1/12; Fig 4 Urdu 26/2/0, Roman 1/1/10 | Results + figures |
| Phase 5 Method A 0/23; Method D 22/23 | Results |
| H001–H040 diagnostic 25/40 | Methods / Discussion |
| `research/post-phase12` / R-dev | Limitations only; not Table 1 |

`644100` / 644,100 chunk vectors is **not** a PLOS headline. That is consistent with `PLOS_FINAL_REPRODUCIBILITY_GATE.md` (Phase 4 historical only). **Expected absence, not a STOP.**

S1 Table contains 27 `,yes` Hit@5 rows (matches 27/40). Figure PNG sources match the frozen bar values. Fig 5 is A1 only.

## 4. PLOS template compliance

**PASS WITH MINOR ISSUES**

Template authority remains PLOS LaTeX **3.8 (April 2026)**. Preserved:

* short title not on page 1 (Editorial Manager field)
* `\section*{Conclusion}`
* Funding / Competing Interests / CRediT not in the body
* Methods Data Availability retained for reviewers
* no `adjustwidth{-2.25in}`
* no `\includegraphics` for Figs 1–5
* `plos2025.bst` untouched

Documented process conflict (not silently “fixed”): ZIP/PLOS portal treat DAS as an Editorial Manager field; this manuscript also keeps Methods DAS so reviewers see third-party provenance, SHA-256, and non-redistribution. Paste the same statement into EM.

`.tex` filename still uses the historical packaging name. Printed title is the scientific title.

## 5. Figures

**PASS**

| Upload file | Source PNG | Frozen values |
| --- | --- | --- |
| `figures/Fig1.tif` | `Fig1_m0_routing.png` | Unicode detector; URDU/MIXED/OTHER → Urdu BM25; ROMAN → Method D; Top-50 / Top-5 |
| `figures/Fig2.tif` | `Fig2_development_comparators.png` | 0.2564, 0.2821, 0.4487, 0.5897, 0.8718 |
| `figures/Fig3.tif` | `Fig3_script_splits.png` | K 26/28, 1/12; U 17/18, 6/18, 0/4 |
| `figures/Fig4.tif` | `Fig4_k_miss_analysis.png` | Urdu 26/2/0; Roman 1/1/10 |
| `figures/Fig5.tif` | `Fig5_u_label_distribution.png` | A1 41/26/53/80/0; no A2 bars |

TIFF derivatives copied into the package. PNG sources were not regenerated. Captions sequential Fig 1–5. No A2 values added to Fig 5.

## 6. Tables

**PASS**

Tables 1–6 values and captions unchanged. Table 1 may float to PDF page 8 and split the following paragraph at `0.2821`. Readable; official fractions intact. Placement was not manipulated.

## 7. References

**PASS WITH MINOR ISSUES**

* bibliography compiles; last compile log has no undefined citations
* bib5: IEEE ICoDT2, pages 1–6, DOI `10.1109/ICoDT252288.2021.9441510`
* bib3: preprint (`arXiv:1904.00784`; no journal volume/pages)
* bib13: `3(4):333–389`
* bib14: `3982–3992`
* `plos2025.bst` not edited
* pre-existing BibTeX dataset-field warnings for bib16/bib17 may remain; printed entries show Shahane and Hussain et al.

## 8. Supporting Information

**PASS**

Eight SI files in the ZIP, PLOS names, no article corpus:

* `S1_table.csv`, `S2_table.csv`, `S3_table.csv`, `S4_table.csv`
* `S1_file.json`, `S1_text.md`, `S2_file.md`, `S3_file.md`

A1/A2 distinction preserved in S2/S4 and manuscript SI captions. Local `supporting_information/README.md` is **not** in the ZIP.

S1 File JSON is the historical freeze manifest (`test_set` still names H001–H040; routing object lists URDU/ROMAN/MIXED). Manuscript and `REPRODUCE.md` also document OTHER → Urdu BM25. Not a result change.

## 9. Reproducibility

**PARTIAL**

`REPRODUCE.md`, `requirements.txt`, `experiments/publication_audit/`, `data/README*` / gitignore, and Methods text correctly state:

* Python 3.13.9 and pinned packages
* official M0 entry points
* third-party corpus not in git
* SHA-256 verification route
* freeze-path: do not retune on K/U
* a git clone does not enable full retrieval without the article CSV

Audit reports listed in the master task remain in the repository and were not deleted. They are **not** required inside the PLOS ZIP.

## 10. PDF build

**PASS**

Existing Tectonic/XeTeX compile of the current `.tex`:

* 14 pages
* bibliography resolved
* 0 Overfull / 0 Underfull boxes in the compile log
* 0 undefined citations
* output PDF 113,777 bytes (SHA-256 `4a1fe11481c0409e66db1537957910306df1e307ca19599c6cf311f2c7aa0824`)

A second Tectonic download was not performed in this packaging pass (no `pdflatex`/`tectonic` on PATH). The packaged PDF is that already-successful compile of the frozen `.tex`. Tectonic binaries are **not** in the ZIP.

## 11. PDF visual QA

**PASS WITH MINOR ISSUES**

Checked via PDF text extract plus figure PNG inspection:

* title, three authors, one affiliation, corresponding email, unstructured abstract
* no short title, funding, competing interests, or CRediT on page 1
* headings including Conclusion; SI list; Acknowledgments (supervisor thanks + confirmed M.S. thesis sentence)
* tables 1–6 values intact; figure captions present (images uploaded separately)
* references 1–17 through page 14, including bib5 IEEE, bib3 preprint, bib13/bib14 pages

Minor: Table 1 float to page 8; XeTeX ligature extraction can show `T able`. No clipping of official counts, no missing SI captions, no wrong title/authors.

## 12. Editorial Manager checklist

**PASS**

`Papers/PLOS_ONE/SUBMISSION_PACKAGE_FINAL/EDITORIAL_MANAGER_CHECKLIST.md` contains paste-ready:

* Short title
* Funding
* Competing interests
* CRediT
* Data Availability Statement
* authors / affiliation / corresponding email
* ORCID marked **USER TO ENTER**
* upload map for PDF, five TIFFs, eight SI files
* ethics: do not invent IRB

## 13. Package contents

**PASS**

ZIP members (19 files):

```
EDITORIAL_MANAGER_CHECKLIST.md
MANIFEST.txt
figures/Fig1.tif … Fig5.tif
manuscript/Adaptive_dynamic_query_routing_for_Urdu_information_retrieval.pdf
manuscript/Adaptive_dynamic_query_routing_for_Urdu_information_retrieval.tex
manuscript/plos_bibtex_sample.bib
manuscript/plos2025.bst
supporting_information/S1_file.json
supporting_information/S1_table.csv
supporting_information/S1_text.md
supporting_information/S2_file.md
supporting_information/S2_table.csv
supporting_information/S3_file.md
supporting_information/S3_table.csv
supporting_information/S4_table.csv
```

**Third-party Urdu news corpus is NOT included in this package.**

## 14. Forbidden files check

**PASS**

ZIP does **not** contain:

* `data/urdu_news.csv` or `data/clean_articles.csv`
* Chroma / embeddings / 644,100-vector index
* `tectonic.exe` / `_tectonic_bin`
* `.git`
* `.aux` / `.log` / `.out` / Python cache
* `research/post-phase12`
* R-dev / H001–H040 dump artifacts
* old `SUBMISSION_PACKAGE` zip
* SI README

## 15. ZIP integrity

**PASS**

Fresh ZIP built from `SUBMISSION_PACKAGE_FINAL/` (not a reused old archive). Manuscript PDF + TeX, five TIFFs, eight SI files, bibliography, BST, MANIFEST, and EM checklist all present.

## 16. ZIP SHA-256

`6dd2a4b0ac4e4e1277ed2007605388e6b88d93a4d34300f9172e6fd0c2164fea`

## 17. ZIP size

804,359 bytes (785.5 KiB)

## 18. Number of files

19

## 19. Remaining non-blocking issues

1. ORCID must be entered in Editorial Manager (not invented here).
2. Paste portal-only fields from the checklist (short title, funding, competing interests, CRediT, DAS).
3. Table 1 may appear on PDF page 8.
4. Harmless BibTeX dataset-field warnings for bib16/bib17.
5. Historical `.tex` filename vs printed title.
6. Methods DAS retained in addition to the portal DAS field (intentional).
7. Reproducibility remains PARTIAL without the third-party article CSV.
8. S1 File JSON is a historical freeze snapshot (`test_set` = H001–H040).
9. Working tree is uncommitted by instruction; default GitHub branch may still be `main` — clone `publication/plos-one-final`.
10. Do not submit the older `SUBMISSION_PACKAGE/ULTRA_PLOS_ONE_FINAL_SUBMISSION.zip`.
11. Tectonic/XeTeX was used locally, not pdfLaTeX.
12. Postponed scientific work (Roman matching, dense/hybrid, larger eval, CIs) was not started.

## 20. Submission blockers

**NONE**

---

## FINAL VERDICT

**SUBMISSION READY WITH MINOR MANUAL STEPS**

The remaining work is Editorial Manager data entry (ORCID, portal declarations, file uploads). The scientifically frozen manuscript, figures, SI, references, reproducibility documentation, checklist, and fresh ZIP are ready.
