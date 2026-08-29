# CLEANUP FINAL REPORT

**Date:** 29 August 2026  
**Task:** Stage 2 file organization only.

## 12–14. Process confirmations

| Item | Status |
| --- | --- |
| Experiment / retrieval / tuning run | **NO** |
| Scientific result changed | **NO** |
| M0 / corpus / dictionary / queries / qrels modified | **NO** |
| Git commit | **NO** |
| Git push | **NO** |
| `git clean` / reset / history rewrite | **NO** |

Official metrics (copied, not recomputed):

- Dev/val ExactSource Hit@5 = **68/78 = 87.18%**
- K ExactSource Hit@5 = **27/40 = 67.50%** (Hit@1/@10/@50 = 50.00% / 70.00% / 75.00%)
- U human Success@5 = **23/40 = 57.50%** (P@5 = 0.2050, nDCG@5 = 0.6460, MRR = 0.4542)

---

## 1. Files moved (canonical finals)

| From | To |
| --- | --- |
| Thesis markdown + HOW_TO | `Thesis/FINAL/` |
| Thesis DOCX | **copied** to `Thesis/FINAL/` (original still locked by Word) |
| PLOS `main.tex`, `references.bib`, `plos2025.bst`, Fig1, Fig2 | `Papers/PLOS_ONE/FINAL/` |
| PLOS submission ZIP | `Papers/PLOS_ONE/SUBMISSION_PACKAGE/` |
| IEEE_M0 `main.tex`, `IEEEtran.cls` | `Papers/IEEE/FINAL/` |
| IEEE submission ZIP | `Papers/IEEE/SUBMISSION_PACKAGE/` |
| `CLEAN_FINALIZATION_MANIFEST.md` | `docs/PROJECT_STATUS.md` |
| `experiments/FINAL_EXPERIMENTAL_RESULTS_ANALYSIS.md` | `docs/FINAL_EXPERIMENTAL_RESULTS_ANALYSIS.md` |
| `CLEANUP_PLAN.md` | `docs/CLEANUP_PLAN.md` |

Python M0 entry points **not** moved (`experiments/phase5_roman_urdu/run_phase5.py`, Phase 2 oracle, Phase 12 runner).

---

## 2. Files archived

- **Thesis:** two `.bak.docx` files; all `_audit_*` / `_apply_m0_*` repair scripts → `archive/historical_thesis/`
- **Papers:** old PLOS zips/PDFs/stale `main.pdf`; PLOS Word draft; MiniLM IEEE tree → `archive/historical_papers/`
- **Figures unused by live M0 PLOS:** 20 SVM/MiniLM PNGs → `archive/historical_figures/plos_unused_svm_minilm/`
- **Layer A results:** `results/CURRENT.*`, development charts → `archive/historical_figures/results_layer_a/`
- **Experiments:** notebooks, `validate/`, `artifacts/`, phases 0/1/3/6/7/10a/10b/4b, old `experiments/archive`, SVM pickles/backups → `archive/historical_experiments/`
- **Root:** `DEFENSE_DEMO.md`, `INSTRUCTIONS_URDU.txt`, `validation_response.py`, `README (3).md`, `results.zip`

---

## 3. Files deleted

| Path | Reason |
| --- | --- |
| `Write-Host` | Empty accidental file |
| `scripts/` | Empty directory |
| Empty leftover PLOS/IEEE_M0 dirs under `Thesis_Paper/` | After moves |

**Not deleted:** `.vscode/` (Windows access denied). `__pycache__` deletion did not finish because the organizer stopped at `.vscode`. Large gitignored binaries (Chroma, `*.npy`, Phase 4 zip, `urdu_news.csv`) were **left in place**.

---

## 4. Files retained (active freeze)

- `data/clean_articles.csv`
- `models/roman_urdu_dict_expanded.json`
- `experiments/phase5_roman_urdu/run_phase5.py`
- `experiments/phase2_oracle/run_phase2_pipeline.py`
- `experiments/phase12_new_unseen_evaluation/` (queries, SEAL, Top-50 dumps)
- `experiments/phase12_human_relevance/` (`U_QRELS.csv`, `U_PER_QUERY.csv`)
- `experiments/phase8_final_freeze/FINAL_SYSTEM_MANIFEST.json`
- `experiments/phase9_heldout_evaluation/`
- `experiments/phase11_improvement/`
- `experiments/phase10c_human_relevance/` (H diagnostic)
- `experiments/phase4_chunk_ann/` (left in place; large zip gitignored)

---

## 5. Final directory tree (active)

```
README.md  .gitignore
data/  models/  src/  experiments/  results/
Thesis/FINAL/
Papers/PLOS_ONE/{FINAL,SUBMISSION_PACKAGE}
Papers/IEEE/{FINAL,SUBMISSION_PACKAGE}
docs/
archive/{historical_thesis,historical_papers,historical_figures,historical_experiments}
Thesis_Paper/   pointer README + locked leftover DOCX
```

---

## 6. Thesis verification

- Canonical file: `Thesis/FINAL/Hashim_Shazad_243259_AU_Thesis_ULTRA.docx` — **exists**
- Markdown draft: `Thesis/FINAL/ULTRA_THESIS_SUBMISSION_DRAFT.md` — **exists**
- Images: **21 PNGs embedded** in `word/media/` (`r:embed` only; `r:link` = 0). Not extracted. No external figure files required.
- `Thesis/FINAL/figures/README.md` documents this.
- **Caveat:** Word still has the original open at `Thesis_Paper/Air_Thesis_Formate/Hashim_Shazad_243259_AU_Thesis_ULTRA.docx`. Close Word and delete that leftover; use `Thesis/FINAL/`.

Scientific text of the DOCX was **not** edited in Stage 2.

---

## 7. PLOS verification

- `Papers/PLOS_ONE/FINAL/main.tex` exists (M0 manuscript)
- `\includegraphics{figures/Fig1_m0_routing.png}` → file exists
- `\includegraphics{figures/Fig2_u_script_split.png}` → file exists
- `references.bib`, `plos2025.bst` present
- ZIP: `Papers/PLOS_ONE/SUBMISSION_PACKAGE/ULTRA_PLOS_ONE_FINAL_SUBMISSION.zip`

---

## 8. IEEE verification

- `Papers/IEEE/FINAL/main.tex` exists (M0)
- **No** `\includegraphics` in this file
- `IEEEtran.cls` present
- ZIP: `Papers/IEEE/SUBMISSION_PACKAGE/ULTRA_IEEE_M0_FINAL_SUBMISSION.zip`
- Historical MiniLM paper: `archive/historical_papers/IEEE_MiniLM/` (4 figures kept with that paper)

---

## 9. Figure verification

| Document | Figures preserved | Notes |
| --- | --- | --- |
| Thesis DOCX | 21 embedded PNGs | No path update needed |
| PLOS M0 | 2 files (Fig1, Fig2) | Relative `figures/` next to `main.tex` |
| IEEE M0 | 0 | None referenced |
| Unused PLOS SVM/MiniLM PNGs | 20 archived, not deleted | Not cited by live M0 `main.tex` |
| IEEE MiniLM | 4 kept with historical paper | `two_rooms_lights`, `cue_split`, `heldout_p5`, `three_evaluation_layers` |

**Duplicates:** same MiniLM plot names appear in `archive/historical_papers/IEEE_MiniLM/figures/` and `archive/historical_figures/plos_unused_svm_minilm/`. Both archived; neither deleted (provenance differs: IEEE paper vs unused PLOS assets).

**Uncertain figures:** none deleted. Layer A `results/figures` archived.

---

## 10. Results verification

`results/FINAL_RESULTS.md`, `DEVELOPMENT_VALIDATION.md`, `PHASE12_RESULTS.md`, `PHASE11_ABLATION.md` contain the official numbers above, labeled separately. No averaging. H001–H040 marked diagnostic.

---

## 11. M0 integrity

- Routing code still at `experiments/phase5_roman_urdu/run_phase5.py`
- Dictionary still at `models/roman_urdu_dict_expanded.json`
- Corpus still at `data/clean_articles.csv`
- Phase 12 query/qrel files still under `experiments/phase12_*`

---

## Follow-up (manual, not done here)

1. Close the thesis in Word, then delete `Thesis_Paper/Air_Thesis_Formate/Hashim_Shazad_243259_AU_Thesis_ULTRA.docx` so only `Thesis/FINAL/` remains.
2. Optional later: delete local Chroma / `*.npy` / Phase 4 zip (still gitignored; not touched).
3. `.vscode/` remains (permission denied).
