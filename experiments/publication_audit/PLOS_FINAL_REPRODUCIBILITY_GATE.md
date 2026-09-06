# PLOS ONE final pre-submission / reproducibility gate

**Date:** 6 September 2026  
**Branch:** `publication/plos-one-final`  
**Canonical manuscript:** `Papers/PLOS_ONE/Adaptive_dynamic_query_routing_for_Urdu_information_retrieval.tex`  
**PDF:** `Papers/PLOS_ONE/Adaptive_dynamic_query_routing_for_Urdu_information_retrieval.pdf` (14 pages)  
**Template ZIP:** `Thesis_template/PLOS ONE/PLOS_latex_template (1).zip` (Version 3.8, April 2026)

Mode: **verify**. Science frozen. No experiments. No commit / push / merge.

**Decision: PASS WITH MINOR ISSUES**

This snapshot should be treated as the frozen PLOS scientific+formatting version. Remaining items are editorial/portal/process, not new science.

---

## A. Branch status

| Check | Result |
| --- | --- |
| `git branch --show-current` | `publication/plos-one-final` |
| Tracks | `origin/publication/plos-one-final` |
| Merge from `research/post-phase12` | None |
| Cherry-pick / rebase | None |

Working tree is **intentionally dirty** (uncommitted publication manuscript, PDF, README/`REPRODUCE.md`, audit notes). That is not a scientific regression. **Do not commit in this gate.**

---

## B. Template status

ZIP is PLOS LaTeX **3.8 (Apr 2026)**: `article` 10pt letter, required packages present, caption-only figures, `\clearpage` + line numbers after abstract, SI `\paragraph*{S1 Table.}` pattern, `plos2025.bst`, Acknowledgments for general thanks only.

| Requirement | Status |
| --- | --- |
| Printed title in ZIP title-block structure | Pass |
| No Author Summary (PLOS ONE) | Pass |
| No `\includegraphics` of Figs 1–5 | Pass |
| Funding / competing interests / CRediT **not** in body | Pass (portal comments) |
| Methods Data Availability retained | Pass (required scientific provenance; also paste into EM) |
| `\section*{Conclusion}` singular | Pass |
| Short title not on page 1 | Pass (EM field) |

**Template vs PLOS portal (documented, not silently “fixed”):** ZIP/PLOS guidelines put funding, competing interests, CRediT, and DAS in Editorial Manager. This manuscript keeps **Methods DAS** so reviewers see the third-party corpus, SHA-256, and non-redistribution facts. Funding/CI/CRediT stay in header comments for EM paste.

**Severity:** INFORMATIONAL (process), not a scientific conflict.

---

## C. Manuscript consistency

Printed title: **Script-aware BM25 retrieval for Urdu and Roman Urdu news search**. Abstract, Introduction, Methods, Results, Discussion, Limitations, Conclusion all describe deterministic Unicode detection + BM25 index selection. M0 is **not** described as learned, neural, RL, LLM, or online adaptive routing.

Filename `Adaptive_dynamic_query_routing_for_Urdu_information_retrieval.tex` is packaging-only. **INFORMATIONAL.**

RQ1–RQ4 each have an official result in the paper (68/78; 27/40 transfer failure of the 87% figure; A1 23/40; M1–M4 did not beat 68/78).

`research/post-phase12` is disclosed in Limitations and is not in Table 1.

---

## D. Scientific freeze verification

Manuscript and SI match the freeze. S1 Table recomputed this gate:

| Item | Freeze | Verified |
| --- | --- | --- |
| Corpus n | 111,860 | Yes |
| SHA-256 | `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231` | Yes (text + `FINAL_SYSTEM_MANIFEST.json`) |
| BM25 | k1=1.5, b=0.75; retrieve 50; cutoff 5 | Yes |
| M0 paths | URDU/MIXED/OTHER → Urdu BM25; ROMAN → Method D | Yes (tex + Fig 1 + `detect_script`) |
| Freeze-pool | 68/78 = 87.18%; nDCG@5 0.8107; MRR 0.797 | Yes |
| K | Hit@1 20/40; Hit@5 27/40; Hit@10 28/40; Hit@50 30/40 | Yes (S1 Table counts) |
| K script | URDU 26/28; ROMAN 1/12 | Yes |
| Fig 4 buckets | Urdu 26/2/0; Roman 1/1/10 | Yes (K002 r6, K010 r49, K031 r17; 10 Roman absent) |
| U A1 | 23/40; P@5 0.2050; nDCG@5 0.6460; MRR 0.4542 | Yes |
| U script | 17/18, 6/18, 0/4 | Yes |
| Labels | A41 B26 C53 D80 E0 | Yes |
| Phase 5 Roman | 0/23 Method A; 22/23 Method D; DEV n=13 | Yes |
| Phase 6 comparators | 0.2564 / 0.2821 / 0.4487 / 0.5897 / 0.8718; oracle 0.9103 | Yes (Table 2 + Fig 2) |
| Phase 11 | M0–M4 all 68/78 | Yes |
| H001–H040 | Diagnostic 25/40; not official U | Yes |
| R-dev 19/50 | Not in official tables | Yes |
| Phase 6 taxonomy 4/10, 3/10, … | Not restated as counts in the paper; text scopes labels to the ten n=78 residuals only | Pass (no generalization to Phase 12) |
| 644,100 chunks | In Phase 4 reports only; not a PLOS headline | INFORMATIONAL |

**Number-search notes**

- `67.50%` appears as K Hit@5 (27/40) **and** A2 five-way agreement (135/200). Both are correct; denominators differ. **INFORMATIONAL.**
- `0.797` vs `0.8107`: freeze-pool MRR vs nDCG@5; not mixed with U 0.4542 / 0.6460.

**No scientific mismatch requiring STOP.**

---

## E. A1 / A2 verification

| Rule | Status |
| --- | --- |
| A1 official Success@5 = 23/40 | Abstract, Table 1, Table 5, Discussion, SI |
| A2 = 26/40 reliability only | S2 File / S4 Table / Limitations; not Table 1 |
| Not averaged / not replacement | Explicit |
| Annotator 2 named Areena Rahman | Yes |
| Dual-role (query author = A1) disclosed | Yes |
| Fig 5 is A1 labels 41/26/53/80/0 | Yes; no A2 bars |

---

## F. Dataset / Data Availability

Consistent with `DATASET_SOURCE_CHAIN.md`:

- Third-party compilation; Kaggle V1 inferred; Mendeley V3 DOI cited
- Precursor 111,861 → one truncated row dropped → 111,860
- Frozen SHA-256 stated
- Provider SHA **not** completed
- Authors do **not** redistribute article text; SI has no corpus
- Reconstruction via Kaggle/Mendeley + hash check
- GitHub materials: dictionary, code, queries, qrels, `REPRODUCE.md`, branch `publication/plos-one-final`

`data/*.csv` is gitignored. `git ls-files data/*.csv` empty.

**This gate:** `REPRODUCE.md` M0 bullet now includes **OTHER → Urdu BM25** (it previously said only URDU/MIXED). README already had OTHER. **Not a result change.**

---

## G. Figure verification

| Figure | File | Values | Status |
| --- | --- | --- | --- |
| Fig 1 | `Fig1_m0_routing.png` + `Fig1.tif` | Unicode detector; URDU/MIXED/OTHER → Urdu BM25; ROMAN → Method D; Top-50 / Top-5 | Pass |
| Fig 2 | `Fig2_development_comparators.png` + `Fig2.tif` | 0.2564, 0.2821, 0.4487, 0.5897, 0.8718 | Pass |
| Fig 3 | `Fig3_script_splits.png` + `Fig3.tif` | K 26/28, 1/12; U 17/18, 6/18, 0/4 | Pass |
| Fig 4 | `Fig4_k_miss_analysis.png` + `Fig4.tif` | Urdu 26/2/0; Roman 1/1/10 | Pass |
| Fig 5 | `Fig5_u_label_distribution.png` + `Fig5.tif` | A1 41/26/53/80/0 | Pass |

PNG/TIFF binaries were **not** modified this gate. Filename `Fig1_m0_routing.png` still says “routing”; figure content is script-aware. **INFORMATIONAL.**

---

## H. Table verification

Tables 1–6 values match the freeze. Captions after first citation in source. ZIP `[!ht]` floats: **Table 1 on PDF page 8** (first cited p. 7). Readable; values unchanged. Acceptable.

No clipping of official counts in the extracted PDF. No overfull boxes in the last successful compile log.

---

## I. Reference verification

- Keys bib1–bib17: all cited; no orphans
- `plos2025.bst` untouched (ZIP-identical after newline normalization)
- bib5 `@inproceedings` IEEE ICoDT2
- bib3 remains preprint
- bib13 `3(4):333–389`
- bib14 `3982–3992`
- Printed bibliography 17 Vancouver items with DOIs where present

BibTeX warnings: empty author/publisher on bib16/bib17 dataset `@misc`. Printed entries still show Shahane and Hussain et al. **LOW / harmless.**

---

## J. Reproducibility verification

| Item | Status |
| --- | --- |
| `REPRODUCE.md` clean-clone + corpus absence | Pass |
| Python 3.13.9 + `requirements.txt` (numpy 2.3.5, pandas 2.3.3, matplotlib 3.10.6) | Pass |
| Optional sklearn 1.7.2 / scipy 1.16.3 documented | Pass |
| M0 scripts: `run_phase5.py`, Phase 2 char table, `run_phase12.py` | Pass |
| Dictionary in git; hash in manuscript | Pass |
| `verify_corpus_hash.py` | Pass |
| Frozen path: do not retune on K/U | Pass |
| Official metrics traced to sealed reports / SI / qrels | Pass |
| Full retrieval without local CSV | **Not claimed** |
| Large corpus / Tectonic `.exe` tracked | No |

**Reproducibility class: PARTIAL** by design (third-party article text required).

---

## K. Build verification

Last full compile (Tectonic 0.15.0, this publication pass): exit 0; 14-page PDF; 0 Overfull / 0 Underfull / 0 undefined citations.

This gate did **not** re-download Tectonic (no local pdfLaTeX; fetching a compiler binary is outside a read-only check). The on-disk PDF matches the current `.tex` (no manuscript edits after that compile). Engine binary is **not** in git.

Harmless: XeTeX vs ZIP pdfTeX `\DisableLigatures` guard; `lineno.sty` UTF-8 warning; bib16/17 field warnings.

---

## L. PDF visual QA

| Page 1 | Pass: scientific title; three authors; one affiliation; corresponding email; unstructured abstract; **no** short title; **no** funding/CI/CRediT blocks |
| --- | --- |
| Body | Line numbers from p. 2; headings; IDF equation (1); Fig/Table captions; SI list |
| Tables | All six present; official fractions intact |
| Figures | Captions only (PLOS rule) |
| Acknowledgments | Supervisor thanks + confirmed thesis sentence; no funding dump |
| References | 1–17 through last page; DOIs present |
| Blank / overlap / missing SI | None observed in text extract |

Minor: Table 1 float; XeTeX ligatures can extract as `T able`.

---

## M. Git cleanliness

**Unchanged (must stay frozen):** Phase 12 dumps/qrels, A1/A2 labels, M0 code, figure binaries, SI CSVs, `plos2025.bst`, `.bib` entries, `data/*.csv` (untracked/gitignored).

**Modified / untracked (publication packaging, not results):** `.tex`, `.pdf`, `.aux/.bbl/.blg`, `README.md`, `REPRODUCE.md`, `docs/REPRODUCIBILITY.md`, `experiments/publication_audit/*.md`.

**Do not upload** `Papers/PLOS_ONE/SUBMISSION_PACKAGE/ULTRA_PLOS_ONE_FINAL_SUBMISSION.zip` without rebuilding — it may predate the script-aware title/PDF. **MEDIUM** process risk if the old zip is submitted by mistake.

---

## N. Remaining risks

| ID | Severity | Type | Item |
| --- | --- | --- | --- |
| N1 | — | Scientific (disclosed) | Modest novelty; n=40; mixed n=4; Roman K n=12; A1 dual role; no dense/hybrid on K/U; third-party provenance |
| N2 | MEDIUM | Process | Stale `SUBMISSION_PACKAGE` zip; submit the current PDF + SI + TIFFs, not the old zip |
| N3 | LOW | Editorial | Table 1 float to page 8 |
| N4 | LOW | Build | Compile was Tectonic/XeTeX, not pdfLaTeX |
| N5 | LOW | BibTeX | Dataset entries bib16/bib17 field warnings |
| N6 | INFORMATIONAL | Packaging | `.tex` filename still says Adaptive Dynamic Query Routing |
| N7 | INFORMATIONAL | Portal | Paste funding, competing interests, CRediT, DAS, short title into Editorial Manager |
| N8 | INFORMATIONAL | Git | Default GitHub branch is still `main`; clone `publication/plos-one-final` |
| N9 | INFORMATIONAL | Working tree | Publication files uncommitted (by instruction) |

**No BLOCKER. No HIGH scientific inconsistency.**

---

## O. Final decision

**PASS WITH MINOR ISSUES**

The PLOS version on `publication/plos-one-final` is internally consistent with the frozen evidence, template-compliant enough to submit, and honest about corpus/A1/A2/post-phase12 limits.

Treat this PLOS scientific+format snapshot as **FROZEN**. Future strengthening (unseen queries, Roman matching, dense/hybrid, reranking, larger independent eval) is a **separate phase**.

---

## Portal paste (Editorial Manager)

- **Short title:** Script-aware BM25 for Urdu news search  
- **Funding:** No specific funding was received for this work.  
- **Competing interests:** The authors have declared that no competing interests exist.  
- **CRediT:** Hashim Shazad — Conceptualization, Methodology, Software, Formal analysis, Writing – original draft, Writing – review & editing. Adnan Aslam — Supervision, Writing – review & editing. Areena Rahman — Validation (independent A2 reliability annotation only; does not replace A1 23/40).  
- **DAS:** use the Methods Data Availability paragraph (third-party corpus; SHA-256; non-redistribution; GitHub branch `publication/plos-one-final`).  
- **Ethics:** do **not** enter IRB / exemption / consent.  
- **ORCID:** enter in EM (not invented here).
