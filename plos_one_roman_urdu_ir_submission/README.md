# PLOS ONE submission package — Roman Urdu first-stage retrieval

Submission-ready LaTeX for:

**Roman Urdu first-stage retrieval for Urdu news: dense and hybrid candidates after a frozen lexical baseline**

Authors: Hashim Shazad, Adnan Aslam (Air University)

## Contents

| File | Role |
|------|------|
| `manuscript.tex` | Single-file PLOS ONE manuscript (template v3.8) |
| `references.bib` | BibTeX entries used by the manuscript |
| `plos2025.bst` | Official PLOS BibTeX style from the template zip |
| `README.md` | This file |

Template extract retained under `template_extract/` for reference only; compile from this folder root.

## What changed from the V2 draft (`PLOS_ONE_V2_DRAFT`)

- Kept Tables 1–3 counts frozen from Phase 14; no Hit@k numbers were recomputed or altered.
- Strengthened the empirical / diagnostic contribution framing (Introduction, Discussion, Conclusion). Explicitly **does not** claim a new retrieval algorithm.
- Incorporated the confirmed **31 CG-failure** diagnostic:
  - Covered **17** / Partial **14** / Uncovered **0**
  - Potential_New_Mechanism = Yes: **0**
  - Failures are heterogeneous and explainable by existing method families (transliteration, entity linking, acronym expansion, char n-gram, dense, query expansion)
  - No shared previously unmodeled structural phenomenon survived the evidence test
- Added a Methods subsection describing that diagnostic (post-Phase 14; TRAIN+DEV only; no retuning).
- Promoted **Limitations** to its own section (PLOS structure).
- Abstract updated for the 55-point stretch shortfall and the CG-failure conclusion; TEST remains sealed; Program B numbers are not averaged with M0’s 87.18% / 67.50% / 57.50%.
- Bibliography cleaned to cited keys only (`references.bib`); unused Sentence-BERT entry removed.

## Confirmations

- **31 CG analysis conclusion:** incorporated in Abstract, Methods, Results, Discussion, Conclusion, and Acknowledgments.
- **TEST:** remains sealed / never opened; no generalization claims.
- **Program A headlines:** cited only as historical context; not averaged with Program B.

## Compile instructions

Preferred (official PLOS path — pdfTeX):

```bash
pdflatex manuscript
bibtex manuscript
pdflatex manuscript
pdflatex manuscript
```

On Windows (MiKTeX / TeX Live):

```powershell
pdflatex manuscript.tex
bibtex manuscript
pdflatex manuscript.tex
pdflatex manuscript.tex
```

`\DisableLigatures` is wrapped in `\ifdefined\pdftexversion` so local Tectonic/XeTeX compiles do not halt; under pdfTeX the official ligature disable still runs.

A local `manuscript.pdf` was produced with Tectonic in this environment. For PLOS upload, recompile with `pdflatex` when available.

## Scientific source of truth

- Program B Hit@k: `experiments/ultra_v2/PHASE14_FINAL_REPORT.md`
- CG diagnostic: `experiments/ieee_adaptive_extension/CG31_FAILURE_ANALYSIS_SUMMARY.md`
- Narrative base: `PLOS_ONE_V2_DRAFT.pdf` / recovered V2 draft text
