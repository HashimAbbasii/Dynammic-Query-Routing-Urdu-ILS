# IEEE M0 paper

`main.tex` is the official IEEE-style manuscript for frozen script-aware BM25 (M0).

Historical MiniLM dual-index paper: `../../../archive/historical_papers/IEEE_MiniLM/main.tex`

Compile from this directory:

```
pdflatex main.tex
pdflatex main.tex
```

Requires `IEEEtran.cls` in this folder. No figures are referenced. Official metrics (do not average): 68/78 ExactSource Hit@5 (dev/val); 27/40 ExactSource Hit@5 (K); 23/40 human Success@5 (U).
