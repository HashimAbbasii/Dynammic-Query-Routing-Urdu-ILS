# FINALIZATION REPORT

**Date:** 27 August 2026  
**Experiments run:** none. M0 unmodified.

## 1. Thesis file created/updated

- **Created (scientific source of truth):** `Thesis_Paper/Air_Thesis_Formate/ULTRA_THESIS_SUBMISSION_DRAFT.md`
- **Paste guide:** `Thesis_Paper/Air_Thesis_Formate/HOW_TO_UPDATE_WORD_THESIS.md`
- **AU Word shell not auto-rewritten:** `Thesis_Paper/Air_Thesis_Formate/Hashim_Shazad_243259_AU_Thesis_ULTRA.docx` still contains Layer A SVM/P@15 body text until you paste the draft (certificates/TOC kept).

## 2. Research paper file created

- **Official M0 IEEE-style paper:** `Thesis_Paper/IEEE_M0/main.tex`
- **Historical MiniLM routing paper (unchanged):** `Thesis_Paper/IEEE/main.tex` — labeled in `Thesis_Paper/IEEE/README.md` as a different study.

## 3. Files archived (moved, not deleted)

Under `experiments/archive/`:

- Word `.bak.docx` snapshots and scratch PNGs
- Duplicate PLOS `_unzipped/` trees
- `main.pre_honest.bak.tex`
- `IEEE_conference_paper.zip` (duplicate of `Thesis_Paper/IEEE/`)

See `CLEAN_FINALIZATION_MANIFEST.md`.

## 4. Files retained

Corpus, dictionary, M0 code, Phase 9/11/12 evidence, hashes, protocols, README, thesis/paper sources. No research evidence permanently deleted.

## 5. Official frozen system

**M0:** Unicode detector; URDU/MIXED → Urdu BM25; ROMAN → Method D; \(k_1=1.5\), \(b=0.75\); 111,860 docs; 198-key dictionary.

## 6. Official final metrics

| Setting | Metric | Result |
| --- | --- | --- |
| Phase 2 n=78 | ExactSource Hit@5 | 68/78 = 87.18% |
| K001–K040 | ExactSource Hit@5 | 27/40 = 67.50% |
| K secondary | Hit@1 / @10 / @50 | 50.00% / 70.00% / 75.00% |
| U001–U040 | Success@5 | 23/40 = 57.50% |
| U secondary | P@5 / nDCG@5 / MRR | 0.2050 / 0.6460 / 0.4542 |
| U script | Success@5 | 17/18 Urdu; 6/18 Roman; 0/4 Mixed |
| Phase 11 | n=78 Hit@5 | M0–M4 all 68/78; M0 official |
| H001–H040 | Success@5 | 62.5% diagnostic only |

## 7. Claims supported

See draft appendix. Short list: 68/78 ExactSource (dev/val); 27/40 ExactSource (K); 23/40 Success@5 (U); Urdu ≫ Roman in U sample; M0 official.

## 8. Claims rejected

87.18% real-world/unseen usefulness; 80% unseen usefulness; 57.50% as ExactSource; averaging the three headlines; M1 as an improvement; H001–H040 as primary unseen.

## 9. Remaining thesis issues

1. **Word file** must still be updated by paste (AU formatting cannot be fully replaced in markdown).
2. Clause-1 PLOS `main.tex` may still contain 100% routing / ~90% P@15 — do not submit it as M0.
3. Chapter 2 in the markdown draft is a condensed honest literature chapter; if the examiner requires the longer existing Ch. 2 prose, keep that prose but add ExactSource vs Success@5 and the official tables.
4. IEEE MiniLM paper and M0 paper must not be merged into one results table.

## 10. Ready for supervisor review?

**Yes, for experimental completeness and scientific claims** — if the supervisor reads `ULTRA_THESIS_SUBMISSION_DRAFT.md` (or the Word file after paste).

**Not yet as a finished formatted AU PDF** until the Word paste in `HOW_TO_UPDATE_WORD_THESIS.md` is done.

No further experiments are required or recommended before that review.
