# PLOS ONE format final audit (Phase 7)

**Date:** 6 September 2026  
**Branch:** `publication/plos-one-final`  
**Template ZIP:** `Thesis_template/PLOS ONE/PLOS_latex_template (1).zip` (Version 3.8 Apr 2026)  
**Manuscript:** `Papers/PLOS_ONE/Adaptive_dynamic_query_routing_for_Urdu_information_retrieval.tex`  
**Compiled PDF:** `Papers/PLOS_ONE/Adaptive_dynamic_query_routing_for_Urdu_information_retrieval.pdf` (14 pages)

Mode: formatting / submission safety. Scientific freeze unchanged.

---

## 1. Manuscript

| Check | Status | Notes |
| --- | --- | --- |
| Printed title | Pass | **Script-aware BM25 retrieval for Urdu and Roman Urdu news search** (63 characters; sentence case). Not the old Adaptive Dynamic Query Routing title. Filename unchanged. |
| Short title | Pass | Removed from title page (not in ZIP title block). Portal comment: **Script-aware BM25 for Urdu news search** (38 characters). Enter in Editorial Manager. |
| Authors | Pass | Hashim Shazad¹*, Adnan Aslam¹, Areena Rahman¹. Affiliation: Department of Creative Technologies, Air University, Islamabad, Pakistan. Corresponding: `abbasihashim30@gmail.com`. No invented ORCID/degrees. |
| Abstract | Pass | Unstructured (PLOS ONE). ≈183 words (<300). No Author Summary (correctly skipped). |
| Section structure | Pass | Introduction → Materials and methods → Results → Discussion → Conclusion (singular, matching ZIP) → Supporting information → Acknowledgments → References. |
| Line numbers | Pass | Start after abstract `\clearpage` + `\newgeometry` + `\linenumbers`. Stop before bibliography (`\nolinenumbers`). |
| Single `.tex` file | Pass | No `\input`. |
| Template packages | Pass | None of the ZIP packages were deleted. `changepage` retained even after unused `adjustwidth` wrappers were removed. |
| Graphics in manuscript | Pass | No `\includegraphics` of scientific figures. Caption-only `figure` environments. TIFF uploads: `Fig1.tif`–`Fig5.tif`. |
| Acknowledgments | Pass | General thanks only (supervisor + M.S. thesis). |
| Funding / competing interests / CRediT in body | Pass | Removed from manuscript body per ZIP Acknowledgments instruction and PLOS submission guidelines. Exact approved wording remains in portal comments for Editorial Manager. |
| Data availability | Pass with documented exception | Methods `\subsection*{Data availability}` retained so reviewers see third-party corpus / SHA-256 / non-redistribution. Same facts are in portal comments for the EM DAS field. Not placed in Acknowledgments. |
| Ethics | Pass | Conservative Methods subsection. No invented IRB. |
| Post-phase-12 disclosure | Pass | `research/post-phase12` named in Limitations; not in official tables. |
| Adaptive/dynamic overclaim | Pass | Printed title and abstract do not claim learned/adaptive routing. Historical SVM is labeled development, not M0. |

---

## 2. Figures

| Item | Status |
| --- | --- |
| Fig 1–5 cited as `Fig` | Pass |
| Captions after first citation | Pass (source). Floats may move in PDF (Table 1 / figures follow `[!ht]` as in ZIP). |
| Scientific plots unchanged | Pass — PNG sources and TIFF derivatives not regenerated |
| Numbering | Pass |
| File formats | TIFF for EM (`Fig1.tif`–`Fig5.tif`); PNG sources retained |
| Empty figure env (no graphics in PDF) | Pass — required by ZIP / PLOS LaTeX page |

---

## 3. Tables

| Table | Values | Formatting | Verified vs `MANUSCRIPT_NUMBERS_AUDIT.md` |
| --- | --- | --- | --- |
| Table 1 | 68/78 (87.18%); 27/40 (67.50%); 23/40 (57.50%) + CIs | Cell-based; `adjustwidth{-2.25in}` removed (unsafe after 1 in body geometry; ZIP example table does not use it). `Development\slash validation` allows a line break. | Yes |
| Table 2 | MiniLM / Urdu-only / M0 0.8718 / 0.8107 / 0.797 / oracle | Unchanged values | Yes |
| Table 3 | M0–M4 all 68/78 | Unchanged values | Yes |
| Table 4 | 20/40, 27/40, 28/40, 30/40 | Unchanged values | Yes |
| Table 5 | 23/40; 0.2050; 0.6460; 0.4542; A41 B26 C53 D80 E0 | Unchanged values | Yes |
| Table 6 | 17/18, 6/18, 0/4 and other slices | Unchanged values | Yes |

No official number was rounded or edited. A1 was not replaced by A2. R-dev 19/50 was not added.

**Minor visual:** Table 1 floats to page 8 while first cited on page 7. ZIP uses `[!ht]`; PLOS production reflows tables. Not treated as a scientific error.

---

## 4. Supporting information

Manuscript `\paragraph*{S# Type.}` labels match packaged files:

| Label | File | Present |
| --- | --- | --- |
| S1 Table | `S1_table.csv` | Yes |
| S2 Table | `S2_table.csv` | Yes |
| S3 Table | `S3_table.csv` | Yes |
| S4 Table | `S4_table.csv` | Yes |
| S1 File | `S1_file.json` | Yes |
| S2 File | `S2_file.md` | Yes |
| S3 File | `S3_file.md` | Yes |
| S1 Text | `S1_text.md` | Yes |

No article-text corpus in SI. README in that folder is packaging notes and must **not** be uploaded.

ZIP uses the same `\paragraph*` + `\nameref` convention (S1 Fig / S1 File / S1 Appendix / S1 Table examples). This paper has no SI figures; main Figs 1–5 are article figures.

---

## 5. Declarations (where they belong)

| Item | Manuscript body | Editorial Manager (portal comments) |
| --- | --- | --- |
| Funding | Removed (ZIP/PLOS: not in `.tex`) | “No specific funding was received for this work.” |
| Competing interests | Removed | “The authors have declared that no competing interests exist.” |
| Author contributions | Removed | CRediT mapping for Shazad / Aslam / Rahman (A2 Validation; does not replace A1 23/40) |
| Data availability | Methods subsection kept (scientific provenance) | Same conservative DAS in comments |
| Ethics | Methods subsection | Do **not** enter IRB/exemption/consent |
| ORCID | Not invented | Enter in EM |
| Short title | Not on title page | Script-aware BM25 for Urdu news search |

---

## 6. Reproducibility wording (unchanged in substance)

- GitHub: `https://github.com/HashimAbbasii/Dynammic-Query-Routing-Urdu-ILS` branch `publication/plos-one-final`
- Code, dictionary, queries, qrels, `REPRODUCE.md` in git
- Full retrieval requires the third-party article CSV (not in git)
- Frozen SHA-256 `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231`
- Provider SHA identity not completed
- Redistribution of news text not independently verified
- Official metrics copied from sealed Phase 8–12 reports

---

## 7. References

- `\bibliographystyle{plos2025}`; `\bibliography{plos_bibtex_sample}`
- ZIP `plos2025.bst` **byte-identical** to manuscript copy after CRLF/LF normalization. **`.bst` not modified.**
- Audited `.bib` not replaced with ZIP dummy biology entries.
- Compiled list: 17 numbered Vancouver entries with DOIs where present.
- BibTeX warnings remain for `bib16`/`bib17` (dataset `@Webpage` author/publisher fields). Printed entries still show Shahane and Hussain et al. **Not edited** (references stage already PASS). Harmless for submission if EM accepts dataset citations this way.
- Citation [12] is Adaptive-RAG (other paper). Not a claim about M0.

---

## 8. LaTeX compilation

| Item | Result |
| --- | --- |
| Engine | Tectonic 0.15.0 (XeTeX). ZIP does not document a compile script; PLOS implies pdfLaTeX+BibTeX. Tectonic ran TeX + BibTeX + reruns. |
| Exit code | 0 |
| Overfull `\hbox` | 0 after Table 1 column/`\slash` fix |
| Underfull `\hbox` | 0 |
| Undefined citations/labels | 0 |
| Missing figures in compile | N/A (captions only, as required) |
| `\DisableLigatures` | ZIP unconditional (pdfTeX). Guarded with `\ifdefined\pdftexversion` so Tectonic does not error. **Minor engine compatibility.** |
| Harmless warnings | `lineno.sty` UTF-8 byte (Tectonic); Fontconfig missing on Windows; Tectonic `.bbl` rerun consistency; `epstopdf` driver note |
| Submission-critical errors | None |

Temporary Tectonic binary was used only to compile and was **deleted** (not a repo artifact).

---

## 9. PDF visual inspection (14 pages)

| Region | Observation |
| --- | --- |
| Page 1 title | Correct scientific title; wraps onto two lines; no old routing title |
| Authors / affiliation / email | Three authors; one affiliation; corresponding asterisk |
| Abstract | Full revised abstract; A1 23/40; A2 reliability only; Roman limitation |
| Short title / Author summary | Absent from page 1 (correct) |
| Headings | Unnumbered `\section*` / `\subsection*` as in ZIP |
| Line numbers | Pages 2–12 |
| Tables | All six present; official counts match freeze |
| Figure captions | Fig 1–5 present; no embedded plots |
| Equation | IDF formula numbered (1) |
| SI block | S1–S4 Table, S1–S3 File, S1 Text |
| Acknowledgments | Two sentences; no funding dump |
| References | 1–17; DOIs; no clipping in extract |
| Footer | `September 6, 2026  n/14` |
| Blank pages | None |
| Minor | Table 1 float to page 8; XeTeX ligatures (`Table` may extract as `T able`) — display is standard Times ligatures, not a missing-symbol error |

---

## 10. Scientific integrity

| Gate | Result |
| --- | --- |
| Official results changed | **No** |
| Experiments added | **No** |
| Metrics manipulated | **No** |
| R-dev promoted | **No** |
| A1 replaced by A2 | **No** |
| Frozen dumps / qrels / A1 / A2 / M0 / figures / corpus | **Not modified** |
| Limitations removed | **No** |
| Branch merge | **No** (`publication/plos-one-final` only) |

---

## 11. Rejection-risk split

### Formatting / editorial (fixable; this phase)

Addressed: ZIP structure, Conclusion heading, no graphics in PDF, SI `\paragraph*` labels, Funding/CI/CRediT out of body, compiled PDF with no undefined refs, title/abstract match freeze.

Residual minor: compile with Tectonic rather than pdfLaTeX; Table 1 float; dataset BibTeX field warnings; Methods DAS also in PDF.

### Scientific (already disclosed; do not hide)

Modest novelty (Unicode + BM25); n=40; mixed n=4; Roman K n=12; A1 query-author dual role; A2 reliability only; third-party provenance; no dense/hybrid on K/U; post-phase12 outside official evaluation.

---

## 12. Git safety (this phase)

Allowed: `.tex` formatting, PDF/aux/bbl/blg rebuild, `PLOS_TEMPLATE_AUDIT.md`, this file. Prior uncommitted README/`REPRODUCE.md` wording from the scientific-revision stage remains uncommitted (not a frozen-result change).

Forbidden paths not touched: Phase 12 dumps, A1/A2 qrels, `data/clean_articles.csv`, M0 code, figure PNG/TIFF binaries, `plos2025.bst`, audited `.bib` entries.

**Not committed** (per instructions).
