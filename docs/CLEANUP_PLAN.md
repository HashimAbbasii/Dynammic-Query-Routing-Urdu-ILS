# CLEANUP PLAN — STAGE 1 ONLY

**Date:** 29 August 2026  
**Status:** INSPECTION COMPLETE. **No files were moved or deleted.**  
**Scientific results:** unchanged (this file is a plan only).

Official frozen system remains **M0**. Official metrics remain:

| Evaluation | Metric | Result |
| --- | --- | --- |
| Phase 2 n=78 (dev/val known-item) | ExactSource Hit@5 | 68/78 = **87.18%** |
| Phase 12 K001–K040 | ExactSource Hit@5 | 27/40 = **67.50%** |
| Phase 12 U001–U040 | Human Success@5 | 23/40 = **57.50%** |

Do not average these. Do not treat 87.18% as unseen/human usefulness. Do not treat 57.50% as ExactSource Hit@5.

---

## Current project structure (summary)

```
ULTRA_Project/
├── README.md                          # current M0 research README
├── README (3).md                      # obsolete SVM dual-index README copy
├── CLEAN_FINALIZATION_MANIFEST.md
├── DEFENSE_DEMO.md                    # SVM/MiniLM defense script
├── INSTRUCTIONS_URDU.txt              # old overlay-install notes
├── validation_response.py             # SVM supervisor-response script
├── results.zip                        # 1.6 MB zip (gitignored)
├── Write-Host                         # empty 0-byte junk file
├── .gitignore  .gitattributes  .git/  .vscode/
├── data/          ~4.9 GB  (corpus + embeddings + Chroma; most gitignored)
├── models/        dict + SVM pickles + backups
├── experiments/   ~1.4 GB  (phase4 zip dominates; Phase 8–12 evidence is small)
├── results/       currently Layer-A SVM “CURRENT” files, not M0 headlines
├── notebooks/     development SVM/MiniLM notebooks
├── validate/      Layer A SVM / dual-index / Phase 3B evidence
├── artifacts/     Phase 10 diagnostic CSV
├── scripts/       empty
└── Thesis_Paper/  thesis + PLOS + IEEE (live M0 + historical MiniLM + old zips)
```

Approximate inventory: **~500+ tracked/untracked files** plus large gitignored binaries (`data/chromadb/` ~3.6 GB, embeddings ~570 MB, `phase4a_chunk_index.zip` ~1.4 GB).

---

## Proposed final folder structure (Stage 2 — after your approval)

**Principle:** MOVE, do not copy. Leave a one-line pointer README where an old path was well-known. Do **not** duplicate the corpus, dictionary, or Phase 12 dumps.

```
ULTRA/
├── README.md
├── .gitignore
├── CLEANUP_PLAN.md                    # this plan
├── docs/
│   ├── PROJECT_STATUS.md              # from CLEAN_FINALIZATION_MANIFEST (moved/renamed)
│   ├── REPRODUCIBILITY.md             # hashes, freeze paths, how to cite metrics
│   └── FINAL_EXPERIMENTAL_RESULTS_ANALYSIS.md  # MOVE from experiments/
├── src/
│   └── README.md                      # map to M0 code (see UNCERTAIN: do not move .py yet)
├── data/
│   ├── README.md                      # what is official vs generated
│   └── clean_articles.csv             # KEEP in place (n=111,860)
├── models/
│   └── roman_urdu_dict_expanded.json  # KEEP (198 keys)
├── results/
│   ├── FINAL_RESULTS.md               # official 87.18 / 67.50 / 57.50 (from existing reports)
│   ├── DEVELOPMENT/                   # pointers or moved Phase 8/2 reports
│   ├── PHASE12/                       # pointers or moved K/U reports
│   └── ABLATION/                      # pointers or moved Phase 11 reports
├── experiments/                       # KEEP Phase 2, 5, 8, 9, 11, 12, 12_human, 10c
├── Thesis/
│   └── FINAL/
│       ├── Hashim_Shazad_243259_AU_Thesis_ULTRA.docx
│       └── ULTRA_THESIS_SUBMISSION_DRAFT.md
├── Papers/
│   ├── PLOS_ONE/FINAL/                # live M0 tex/bib/bst/Fig1/Fig2
│   ├── PLOS_ONE/SUBMISSION_PACKAGE/   # existing clean ZIP
│   ├── IEEE/FINAL/                    # IEEE_M0 main.tex + IEEEtran.cls
│   └── IEEE/SUBMISSION_PACKAGE/       # existing clean ZIP
└── archive/                           # historical MiniLM/SVM papers, old zips, bak, notebooks
```

`src/` will **not** blindly relocate `run_phase5.py` unless you approve (relative paths and paper citations currently point at `experiments/`).

---

## A. KEEP (must remain; official / reproducibility)

### Root / git
- `README.md` (will be updated in Stage 2 to match new layout)
- `.gitignore` (do not weaken; do not force-add large files)
- `.gitattributes`

### Corpus / dictionary / freeze
- `data/clean_articles.csv`
- `models/roman_urdu_dict_expanded.json`
- `experiments/phase8_final_freeze/` (entire folder, including `FINAL_SYSTEM_MANIFEST.json`, `FROZEN_CONFIGURATION.json`, `DEVELOPMENT_RESULTS.md`)
- `experiments/FINAL_EXPERIMENTAL_RESULTS_ANALYSIS.md`

### M0 implementation
- `experiments/phase5_roman_urdu/run_phase5.py` (`detect_script`, BM25, Method D routing)
- `experiments/phase2_oracle/run_phase2_pipeline.py` (Method D character table)
- `experiments/phase12_new_unseen_evaluation/run_phase12.py`

### Official evaluation evidence
- `experiments/phase9_heldout_evaluation/` (reports, `HELD_OUT_PER_QUERY.csv`, `official_metrics.json`)
- `experiments/phase11_improvement/` (ablation protocol, `M0`–`M4` JSON, `PHASE11_ABLATION_RESULTS.md`)
- `experiments/phase11_improvement_design/PHASE11_INVENTORY.md` (and design folder as supporting)
- `experiments/phase12_new_unseen_evaluation/` including:
  - `queries_k.csv`, `queries_u.csv`, `SEAL.json`
  - `PHASE12_SEALED_PROTOCOL.md`, `PHASE12_RETRIEVAL_PROTOCOL.md`, `QUERY_GENERATION_*.md`
  - `K_RESULTS.md`, `K_TOP50_RETRIEVAL.csv`, `U_TOP50_RETRIEVAL.csv`, `U_TOP5_FOR_ANNOTATION.csv`
- `experiments/phase12_human_relevance/` including `U_QRELS.csv`, `U_PER_QUERY.csv`, `PHASE12_HUMAN_RESULTS.md`
- `experiments/phase10c_human_relevance/PHASE10C_RESULTS.md` (H001–H040 **diagnostic** only)

### Final thesis
- `Thesis_Paper/Air_Thesis_Formate/Hashim_Shazad_243259_AU_Thesis_ULTRA.docx`
- `Thesis_Paper/Air_Thesis_Formate/ULTRA_THESIS_SUBMISSION_DRAFT.md`
- `Thesis_Paper/Air_Thesis_Formate/HOW_TO_UPDATE_WORD_THESIS.md` (useful until TOC is updated in Word)

### Final PLOS (M0)
- `Thesis_Paper/Clause_1_Formate/PLOS_ULTRA_paper/main.tex`
- `references.bib`, `plos2025.bst`
- `figures/Fig1_m0_routing.png`, `figures/Fig2_u_script_split.png`
- `README.md` in that folder
- `Thesis_Paper/ULTRA_PLOS_ONE_FINAL_SUBMISSION.zip`

### Final IEEE (M0)
- `Thesis_Paper/IEEE_M0/main.tex`
- `Thesis_Paper/IEEE_M0/IEEEtran.cls`
- `Thesis_Paper/IEEE_M0/README.md`
- `Thesis_Paper/ULTRA_IEEE_M0_FINAL_SUBMISSION.zip`

### Indexing / docs that describe the freeze
- `CLEAN_FINALIZATION_MANIFEST.md`
- `Thesis_Paper/OUTDATED_DRAFTS.md` (until paths are updated after moves)

**Keep count (authoritative set):** ~80–100 files. Not the whole repo.

---

## B. ARCHIVE / MOVE (historical or obsolete; not the live M0 product)

Destination: `archive/` (consolidate; `experiments/archive/` already exists and is gitignored — Stage 2 can use `archive/` at repo root for *tracked* historical papers, and keep gitignored junk in `experiments/archive/`).

### Thesis backups and repair scripts
| Path | Reason |
| --- | --- |
| `Thesis_Paper/Air_Thesis_Formate/Hashim_Shazad_243259_AU_Thesis_ULTRA.pre_m0_cleanup.bak.docx` | Pre-M0 Word snapshot |
| `Thesis_Paper/Air_Thesis_Formate/Hashim_Shazad_243259_AU_Thesis_ULTRA.pre_consistency_audit.bak.docx` | Pre-audit snapshot |
| `Thesis_Paper/Air_Thesis_Formate/_apply_m0_*.py`, `_audit_*.py`, `_fix_toc_fields.py`, `_finalize_front_matter.py`, `_rewrite_one_story.py`, `_insert_defense_figures.py` | One-off Word repair scripts |
| `Thesis_Paper/Air_Thesis_Formate/_audit_*.txt`, `_thesis_extract.txt` | Temporary dumps |

### Historical papers / old PLOS packages
| Path | Reason |
| --- | --- |
| `Thesis_Paper/IEEE/` (MiniLM dual-index `main.tex` + figures) | **Not** official M0 IEEE paper |
| `Thesis_Paper/PLOS_ONE/` Word drafts + `_build_plos_manuscript.py` | Pre-M0 routing Word paper |
| `Thesis_Paper/Clause_1_Formate/PLOS_ULTRA_paper_final.zip` | Old SVM-headed PLOS zip |
| `Thesis_Paper/Clause_1_Formate/PLOS_ULTRA_paper_revised.zip` | Old zip |
| `Thesis_Paper/Clause_1_Formate/PLOS_ULTRA_paper_source_Sample.zip` | Old zip |
| `Thesis_Paper/Clause_1_Formate/Adaptive_Dynammic_Query_Clause1.zip` | Old zip |
| `Thesis_Paper/Clause_1_Formate/Adaptive_Dynammic_Query.pdf` | Old PDF |
| `Thesis_Paper/Clause_1_Formate/Adaptive_Dynamic_Query_Routing_PLOS_ONE.pdf` | Old PDF |
| `Thesis_Paper/Clause_1_Formate/PLOS_ULTRA_paper/main.pdf` | **Stale** PDF (compiled before M0 rewrite) |
| `Thesis_Paper/Clause_1_Formate/PLOS_ULTRA_paper/figures/` except Fig1/Fig2 | SVM/MiniLM figures unused by live M0 tex |
| `Thesis_Paper/Clause_1_Formate/PLOS_ULTRA_paper/_honest_from_methods.tex`, `_stitch_honest.py`, `_make_m0_figures.py` | Scratch / generator |
| `experiments/archive/` (already: unzipped PLOS trees, `PLOS_ULTRA_paper.main.pre_m0.tex`) | Keep as archive; do not promote |

### Misleading “current results” (Layer A, not M0)
| Path | Reason |
| --- | --- |
| `results/CURRENT.txt`, `CURRENT.json` | Still describe SVM 86/84 and MiniLM P@5 as “current frozen” |
| `results/figures/` (cue split, dual-index P@5, two rooms) | Layer A figures |
| `results/_archive_development_cv/` | Development 100% / P@15 charts |
| `results/roman_urdu_results.json`, `phase3_retrieval_results.json`, `phase4_retrieval_results.json` | Historical supporting JSON |
| `README (3).md` | Duplicate outdated README |

### Layer A / defense (scientific history, not live product)
| Path | Reason |
| --- | --- |
| `notebooks/` | SVM/MiniLM development notebooks |
| `validate/` | Phase 3B, traps, dual-index P@5, lights demo |
| `models/svm_classifier.pkl`, `scaler.pkl`, `training_info.json`, `training_data.json` | Layer A SVM, not M0 |
| `models/backup_*`, `*_PRE_GAPFIX_backup.pkl` | Old SVM snapshots |
| `data/training_queries_real.py` | SVM training queries |
| `DEFENSE_DEMO.md` | SVM dual-index demo |
| `validation_response.py` | SVM supervisor memo |
| `INSTRUCTIONS_URDU.txt` | Old overlay instructions |
| `artifacts/phase10/` | Diagnostic dump |
| `experiments/phase0_baseline` through `phase7_human_relevance` (except Phase 2 oracle char table + Phase 5 M0 code) | Development / MiniLM / chunk ANN **reports** — archive as history, do not delete evidence |
| `experiments/phase10a_evidence`, `phase10b_frozen_dump` | Pre-Phase-12 diagnostics |

### Stage 2 *moves of live finals* (not archive — reorganization)
After approval, **move** (not copy):
- Thesis FINAL docx+md → `Thesis/FINAL/`
- PLOS M0 source → `Papers/PLOS_ONE/FINAL/`
- IEEE_M0 source → `Papers/IEEE/FINAL/`
- Existing submission ZIPs → `Papers/.../SUBMISSION_PACKAGE/`
- `experiments/FINAL_EXPERIMENTAL_RESULTS_ANALYSIS.md` → `docs/`

Leave `Thesis_Paper/README.md` as a pointer so old paths are not silent.

**Archive/move estimate:** ~150–200 files (mostly historical papers, notebooks, validate, old zips, Layer A results).

---

## C. SAFE DELETE (clear junk only — Stage 2 after approval)

| Path | Reason |
| --- | --- |
| `Write-Host` | Empty 0-byte accidental file at repo root |
| `**/__pycache__/`, `*.pyc` | Python cache (already gitignored) |
| `.vscode/` | IDE metadata (already gitignored) |
| `~$*` Word lock files | None found in this scan; delete if they appear |
| `scripts/` | Empty directory |

**Not listed for delete:** corpus, dictionary, qrels, sealed queries, Phase 8–12 reports, final thesis/papers/zips.

**Delete estimate:** ~10 pycache trees + 1 empty file + empty `scripts/` + `.vscode/` if you want a cleaner working tree. **Very small.**

---

## D. UNCERTAIN — STOP; need your approval before any action

These are **not** junk, but they are large, historical, or path-sensitive.

| Item | Why uncertain | Suggested default if you say “be aggressive” | Suggested default if you say “be conservative” |
| --- | --- | --- | --- |
| Move M0 `.py` into `src/` | Breaks documented paths (`experiments/phase5_roman_urdu/run_phase5.py`) | Keep code in `experiments/`; `src/README.md` is a map only | Same |
| `data/chromadb/` (~3.6 GB) | Generated MiniLM index; gitignored; not M0 | **Delete locally** (regenerable; not official IR) | Leave on disk, still gitignored |
| `data/*.npy` embeddings (~570 MB) | Generated; gitignored; MiniLM | **Delete locally** | Leave |
| `data/urdu_news.csv` (~264 MB) | Possible precursor of `clean_articles.csv`; gitignored | Confirm it is unused, then archive/delete locally | KEEP until confirmed |
| `experiments/phase4_chunk_ann/phase4a_chunk_index.zip` (~1.4 GB) | Generated; already gitignored | **Delete locally**; keep the CSV/MD reports | Keep zip on disk |
| `results.zip` (1.6 MB, gitignored) | Duplicate of some `results/` | Delete locally | Archive |
| Entire `notebooks/` | Historical methods for thesis Layer A | Archive | KEEP in `archive/notebooks/` |
| Entire `validate/` | Frozen Phase 3B / trap / P@5 **evidence** | Archive, do not delete | KEEP under `archive/layer_a/` |
| SVM `models/*.pkl` | Not M0, but Layer A reproducibility | Archive | KEEP |
| `experiments/phase3_retrieval`, `phase4b_*`, `phase6_*`, `phase7_*` | Development IR, not official M0 headlines | Archive reports (keep files) | KEEP in `experiments/` |
| Empty-looking `experiments/archive` vs nested unzipped PLOS | Already archived; gitignored | Leave | Leave |
| Rewrite `results/CURRENT.txt` to M0 numbers | Presentation only; numbers already exist in Phase 12 reports | Yes, in Stage 2 `results/FINAL_RESULTS.md` | Yes |

**I will not delete or move any UNCERTAIN item in Stage 2 unless you say so.**

---

## Estimated impact (if you approve the conservative Stage 2)

| Action | Approx. count |
| --- | --- |
| KEEP in active tree | ~100 official/repro files + corpus + dict |
| MOVE live thesis/papers into `Thesis/` and `Papers/` | ~15 files |
| ARCHIVE historical papers, bak, Layer A results, old zips | ~150 files |
| DELETE (junk only) | ~15 cache/empty/IDE items |
| UNCERTAIN left untouched | large gitignored binaries, notebooks, validate, SVM pickles, early experiment folders |

Root would drop the accidental files (`Write-Host`, `README (3).md`) and stop looking like a thesis-dump.

---

## What Stage 2 will **not** do (even after approval)

- No retrieval, training, BM25, MiniLM, annotation
- No change to M0 routing, corpus, dictionary, queries, qrels, or reported metrics
- No git commit / push / reset / clean / checkout / history rewrite
- No force-add of `*.f32`, Chroma, embeddings, phase4 zip, `ultra_env/`
- No deletion of Phase 8/9/11/12 official evidence
- No deletion of the final thesis DOCX, live PLOS tex, or IEEE_M0 tex
- No averaging of 87.18 / 67.50 / 57.50

---

## Confirmation (Stage 1)

- **No scientific file was modified.**
- **No file was moved or deleted.**
- Only this plan file is new: `CLEANUP_PLAN.md`.

---

## STOP

Reply with approval and preferences, for example:

1. **Conservative** (recommended): junk delete + archive old papers/baks/zips + move finals into `Thesis/` and `Papers/` + new `results/FINAL_RESULTS.md`; leave notebooks, validate, SVM pickles, early phases, and all large gitignored binaries.
2. **Aggressive disk clean:** also delete local `data/chromadb/`, `data/*.npy`, and `phase4a_chunk_index.zip` (already not in Git).
3. Custom: tell me which UNCERTAIN rows to keep vs archive vs delete.

**Stage 2 will not start until you explicitly approve.**
