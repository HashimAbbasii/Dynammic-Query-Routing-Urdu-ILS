# PLOS ONE template audit (Phase 7)

**Date:** 6 September 2026  
**Branch:** `publication/plos-one-final`  
**Authoritative ZIP:** `Thesis_template/PLOS ONE/PLOS_latex_template (1).zip`  
**Template version:** PLoS LaTeX template **3.8 (Apr 2026)**  
**Canonical manuscript:** `Papers/PLOS_ONE/Adaptive_dynamic_query_routing_for_Urdu_information_retrieval.tex`

Mode: formatting inventory only. Scientific freeze unchanged. This file was written **before** manuscript edits.

---

## 1. ZIP inventory

Extracted to a working folder (deleted after audit; not a submission artifact):

| File | Size (bytes) | Role |
| --- | ---: | --- |
| `plos_latex_template.tex` | 20,434 | Master `.tex` structure, preamble, comments, example sections |
| `plos_latex_template.pdf` | 186,025 | Compiled example (lorem ipsum; **not** scientific content) |
| `plos2025.bst` | 40,858 | Vancouver/PLOS BibTeX style |
| `plos_bibtex_sample.bib` | 5,723 | **Example** bibliography only — do not copy entries |

No `.cls` or extra `.sty` in the ZIP. The class is standard `\documentclass[10pt,letterpaper]{article}` plus packages listed in the template preamble.

No compilation script is in the ZIP. Official PLOS LaTeX page: initial submission is a **PDF** (figures uploaded separately); source `.tex` is requested after acceptance. Standard workflow implied by `\bibliographystyle{plos2025}`: `pdflatex` → `bibtex` → `pdflatex` → `pdflatex`.

---

## 2. Template requirements (from ZIP + PLOS LaTeX page)

| Requirement | Source |
| --- | --- |
| Single `.tex` file (no `\input` / `\externaldocument`) | Template comments |
| Do not delete packages listed in the template | Template comments |
| No colors/graphics in text; **do not** `\includegraphics` figures in the manuscript | Template comments; PLOS LaTeX page |
| Figure/table captions immediately after first citation | Template comments |
| Cite figures as `Fig`, equations as `Eq` | Template comments |
| Captions: bold label + period (`caption` package settings) | Preamble |
| `\bibliographystyle{plos2025}` | Preamble |
| Line numbers after abstract (`\clearpage` + `\newgeometry` + `\linenumbers`) | Body |
| No Author Summary for PLOS ONE | Template comment |
| Abstract unstructured, keep below 300 words | Template comment |
| Title ≤ 250 characters; sentence case | Template comment |
| Acknowledgments: general thanks only | Template Acknowledgments block |
| Funding, competing interests, author contributions, data-availability **portal fields** → Editorial Manager, not Acknowledgments | Template Acknowledgments block; PLOS submission guidelines |
| SI: `\paragraph*{S1 Table.}` + `\label{S1_Table}` + `\nameref` | Supporting information example |
| Heading depth ≤ 3 | Template comment |
| Tables: cell-based; no nested `tabular`; no graphics/colored text in cells | Template comments |

---

## 3. Component comparison

| Template Component | Template Requirement | Current Manuscript | Action |
| --- | --- | --- | --- |
| Template version header | `% Template for PLoS` / Version 3.8 Apr 2026 | Present | Keep |
| `\documentclass[10pt,letterpaper]{article}` | Exact | Match | Keep |
| `geometry` 0.85in top / 2.75in left (title page) | Exact | Match | Keep |
| Required packages (`amsmath`, `amssymb`, `changepage`, `textcomp`, `marvosym`, `cite`, `nameref`, `hyperref`, `lineno`, `microtype`, `xcolor`, `array`, `caption`, `lastpage`, `fancyhdr`, `graphicx`, `epstopdf`) | Must not be deleted | All present | Keep |
| `\DisableLigatures[f]{encoding = *, family = * }` | Unconditional in ZIP (pdfTeX) | Wrapped in `\ifdefined\pdftexversion` for Tectonic/XeTeX | Keep wrapper if compiling without pdfTeX; still execute on pdfTeX. Document as minor engine compatibility, not a package deletion |
| `\textwidth` / `\textheight` / `\raggedright` / parindent 0.5cm | Exact | Match | Keep |
| Fancy header/footer, `\lfoot{\today}`, page n/N | Exact | Match | Keep |
| Dummy `\lorem`/`\ipsum` macros | Example only | Absent (correct) | Do not copy dummy macros |
| Title block `\begin{flushleft}` + `\Large\textbf{...}` | Exact structure | Match; printed title is the approved scientific title | Keep scientific title; do not revert to Adaptive Dynamic Query Routing |
| Short title on title page | **Not** in ZIP title block (EM field) | Visible `Short title:` line on page 1 | **Remove from title page**; keep in portal comments |
| Authors / affiliation / corresponding `*` | No titles/degrees | Hashim Shazad, Adnan Aslam, Areena Rahman; Air University; `abbasihashim30@gmail.com` | Keep approved authorship; unused equal-contribution symbols stay commented |
| Abstract `\section*{Abstract}` | Unstructured for PLOS ONE; <300 words | Unstructured; ≈183 words | Keep scientific abstract; formatting only if needed |
| Author summary | Skip for PLOS ONE | Skipped | Keep skipped |
| `\clearpage` + `\newgeometry{left=1in,right=1in}` + `\linenumbers` | Exact | Match | Keep |
| Introduction | `\section*{Introduction}` | Match | Keep content |
| Materials and methods | `\section*{Materials and methods}` | Match | Keep content |
| Results | `\section*{Results}` (may combine with Discussion) | Separate Results | Keep separate (science already written this way; template allows it) |
| Discussion | `\section*{Discussion}` | Match | Keep content |
| Conclusion heading | `\section*{Conclusion}` (singular in ZIP) | `\section*{Conclusions}` | **Rename heading only** |
| Figures | Caption-only `figure` env; no includegraphics; `Fig~\ref{fig1}` | Five caption-only figures; TIFF uploads `Fig1.tif`–`Fig5.tif` | Keep; do not regenerate plots |
| Tables | Cell-based `tabular`; optional `adjustwidth` if too wide | Tables 1–6; Tables 1–3 wrap `adjustwidth{-2.25in}` | **Drop `-2.25in` adjustwidth after 1in body geometry** (ZIP example table does not use it; −2.25in would overflow a 1in left margin). Preserve all values |
| Equation | `eqnarray` + `\label`; no `\nonumber` | One `eqnarray` IDF formula | Keep |
| Supporting information | `\paragraph*{S# Type.}` + `\label` + bold title | S1–S4 Table, S1–S3 File, S1 Text | Keep labels; match ZIP paragraph convention |
| Acknowledgments | General thanks only | Thanks + thesis sentence; also has Funding / CI / CRediT as **body sections** | **Remove Funding, Competing interests, Author contributions from body**; keep exact approved wording in portal comments for Editorial Manager |
| Data availability | ZIP: enter in EM, not in Acknowledgments | Methods `\subsection*{Data availability}` plus portal comments | **Keep Methods DAS** (reviewers must see third-party corpus / SHA / non-redistribution in the PDF). Duplicate paste-ready text remains in portal comments. Document as a deliberate Methods exception, not an Acknowledgments dump |
| Bibliography | `\bibliography{...}` + `plos2025.bst` | `\bibliography{plos_bibtex_sample}` + local `plos2025.bst` | Keep audited `.bib`. **Do not** replace with ZIP sample entries. BST bytes match ZIP after CRLF/LF normalization (identical style; manuscript copy is CRLF). **Do not modify `.bst`** |
| Sample `.bib` in ZIP | Example only | Manuscript `.bib` is the audited scientific bibliography that happens to use the same filename | Do not copy ZIP dummy references |
| Ethics | Not a ZIP dummy section; PLOS methods when relevant | Conservative Methods ethics subsection | Keep (approved; no invented IRB) |
| Compilation | pdfLaTeX + BibTeX implied; this machine has no `pdflatex` in PATH at audit time | Stale PDF still shows pre-revision title | Rebuild PDF after formatting edits |

---

## 4. Conflicts (formatting vs science)

1. **Portal-only declarations vs Methods DAS.** ZIP + PLOS guidelines forbid putting funding / competing interests / CRediT in the manuscript file. Those body sections will be removed (content preserved in comments). Methods Data availability is retained because it is scientific provenance, not an Acknowledgments dump. If an editor later insists DAS appear only in Editorial Manager, the Methods subsection can be shortened without changing facts.

2. **`.bst` line endings.** ZIP `plos2025.bst` is LF; manuscript copy is CRLF. Content is identical. No replacement (user freeze: do not modify `plos2025.bst`).

3. **`.tex` filename** vs printed title. Filename may remain `Adaptive_dynamic_query_routing_for_Urdu_information_retrieval.tex`. Printed title stays **Script-aware BM25 retrieval for Urdu and Roman Urdu news search**.

4. **Engine.** ZIP assumes pdfTeX `\DisableLigatures`. Compilation may use Tectonic (XeTeX) if pdfLaTeX is unavailable; the `\ifdefined` guard is a formatting compatibility patch, not a scientific change.

No scientific decision is required to apply the template. **No new experiment.**

---

## 5. What will not be copied from the ZIP

- Lorem ipsum title, authors, abstract, body, tables, figures, SI blurbs
- Dummy bibliography (`bib1`–`bib13` biology examples)
- Author summary (not valid for PLOS ONE)
- Unused equal-contribution / deceased / consortium notes as live text

---

## 6. Official numbers (unchanged by this phase)

Freeze-pool 68/78 = 87.18%, nDCG@5 0.8107, MRR 0.797; K 20/40, 27/40, 28/40, 30/40; U A1 23/40, P@5 0.2050, nDCG@5 0.6460, MRR 0.4542; U script 17/18, 6/18, 0/4; labels A41 B26 C53 D80 E0; A2 reliability only. Corpus n=111,860; SHA-256 `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231`. BM25 k1=1.5, b=0.75.
