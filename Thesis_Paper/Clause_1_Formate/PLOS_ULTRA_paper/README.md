# PLOS ONE manuscript (official M0)

Live source: `main.tex`

This manuscript reports **frozen script-aware BM25 (M0)**. It does not headline the historical SVM / MiniLM dual-index study.

Compile (from this directory):
```
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

Required files: `main.tex`, `references.bib`, `plos2025.bst`, `figures/Fig1_m0_routing.png`, `figures/Fig2_u_script_split.png`.

PLOS typically wants figures uploaded as separate files in addition to the manuscript.

Official metrics (do not average):
- 68/78 = 87.18% ExactSource Hit@5 (Phase 2 development/validation)
- 27/40 = 67.50% ExactSource Hit@5 (K001–K040)
- 23/40 = 57.50% human Success@5 (U001–U040)
