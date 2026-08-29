# Adaptive Dynamic Query Routing for Urdu IR

MS thesis (Air University). Student: **Hashim Shazad** · Supervisor: **Dr. Adnan Aslam**.

**Official frozen retrieval system: M0**  
URDU/MIXED → Urdu BM25 · ROMAN → Method D · Unicode script detector · \(k_1=1.5\), \(b=0.75\) · 111,860 documents · dictionary 198 keys.

Do **not** run new retrieval, BM25, MiniLM, annotation, or H041+. Do **not** tune M0.

---

## Official final metrics (do not average)

| Evaluation | Type | Metric | Result |
| --- | --- | --- | --- |
| Phase 2 n=78 | Known-item, development/validation | ExactSource Hit@5 | **68/78 = 87.18%** |
| Phase 12 K001–K040 | Known-item, new sealed | ExactSource Hit@5 | **27/40 = 67.50%** |
| Phase 12 K (secondary) | Same | Hit@1 / Hit@10 / Hit@50 | 50.00% / 70.00% / 75.00% |
| Phase 12 U001–U040 | Human usefulness, new sealed | Success@5 | **23/40 = 57.50%** |
| Phase 12 U (secondary) | Same | P@5 / nDCG@5 / MRR | 0.2050 / 0.6460 / 0.4542 |
| Phase 12 U script (descriptive) | Success@5 | URDU / ROMAN / MIXED | 17/18 / 6/18 / 0/4 |
| Phase 11 | Ablation | n=78 Hit@5 | M0–M4 all 68/78; **M0 stays official** |
| H001–H040 | Diagnostic only | Success@5 | 25/40 = 62.5% (not primary unseen) |

87.18% is **not** real-world accuracy. 57.50% is **not** ExactSource Hit@5. There is **no** 80% unseen usefulness claim.

Full interpretation: `experiments/FINAL_EXPERIMENTAL_RESULTS_ANALYSIS.md`

---

## Submission drafts (content)

| Document | Path |
| --- | --- |
| Thesis scientific draft (AU chapters) | `Thesis_Paper/Air_Thesis_Formate/ULTRA_THESIS_SUBMISSION_DRAFT.md` |
| How to paste into the Word file | `Thesis_Paper/Air_Thesis_Formate/HOW_TO_UPDATE_WORD_THESIS.md` |
| AU Word shell (formatting) | `Thesis_Paper/Air_Thesis_Formate/Hashim_Shazad_243259_AU_Thesis_ULTRA.docx` |
| IEEE-style **M0** paper | `Thesis_Paper/IEEE_M0/main.tex` |
| Older IEEE **MiniLM routing** paper (different study) | `Thesis_Paper/IEEE/main.tex` |
| Finalization manifest | `CLEAN_FINALIZATION_MANIFEST.md` |

---

## Historical Layer A (not official M0 retrieval)

Earlier work trained an SVM SHORT/LONG router and a MiniLM dual-index. Frozen Phase 3B classification is 86% vs 84% word-count. Dual-index P@5 on H001–H040 did **not** improve over word count. Do not mix those P@5 numbers with M0 Success@5.

---

## Reproducibility-critical paths (do not archive)

- `data/clean_articles.csv`
- `models/roman_urdu_dict_expanded.json`
- `experiments/phase5_roman_urdu/run_phase5.py`
- `experiments/phase8_final_freeze/`
- `experiments/phase9_heldout_evaluation/`
- `experiments/phase11_improvement/`
- `experiments/phase12_new_unseen_evaluation/` (sealed queries + retrieval dumps)
- `experiments/phase12_human_relevance/` (U qrels)

Obsolete backups live in `experiments/archive/` (moved, not deleted).

---

## Contact

Hashim Shazad · MS Artificial Intelligence · Air University
