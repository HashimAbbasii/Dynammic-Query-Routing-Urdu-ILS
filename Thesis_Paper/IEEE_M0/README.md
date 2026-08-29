# IEEE M0 paper

`main.tex` is the official IEEE-style manuscript for **frozen script-aware BM25 (M0)**.

It is **not** the MiniLM dual-index routing paper in `../IEEE/main.tex`. Do not merge P@5 tables from that file into this one.

Compile:
```
pdflatex main.tex
pdflatex main.tex
```

Requires `IEEEtran.cls` (copied into this folder for the submission ZIP). No new experiments were run for this draft.

Official metrics (do not average): 68/78 ExactSource Hit@5 (dev/val); 27/40 ExactSource Hit@5 (K); 23/40 human Success@5 (U).
