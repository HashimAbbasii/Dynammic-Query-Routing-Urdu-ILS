# CLEAN_FINALIZATION_MANIFEST

**Date:** 27 August 2026  
**Action:** Documentation and archive only. No new experiments. No retrieval. No change to M0.

---

## Official frozen system

**M0** — ULTRA script-aware lexical retrieval (Phase 8 freeze).

| Item | Value |
| --- | --- |
| Routing | URDU/MIXED → Urdu BM25; ROMAN → Method D |
| Detector | Unicode Urdu vs Latin counts (`detect_script` in `experiments/phase5_roman_urdu/run_phase5.py`) |
| BM25 | \(k_1=1.5\), \(b=0.75\), top_k=50, official cutoff 5 |
| Corpus | `data/clean_articles.csv`, n=111,860, SHA-256 `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231` |
| Dictionary | `models/roman_urdu_dict_expanded.json`, 198 keys, SHA-256 `30c3f61a64ec641abbb3acdbc7a8bcaf197f0238f1bf9e76c2c7ce8e590f86a3` |
| Phase 11 | M1–M4 did not improve n=78 Hit@5; **M0 not replaced** |

---

## Official final results

| ID | Evaluation | Metric | Result |
| --- | --- | --- | --- |
| 1 | Phase 2 n=78 known-item (dev+internal_val) | ExactSource Hit@5 | 68/78 = 87.18% |
| 2 | Phase 12 K001–K040 | ExactSource Hit@1 | 20/40 = 50.00% |
| 2 | Phase 12 K001–K040 | ExactSource Hit@5 | 27/40 = 67.50% |
| 2 | Phase 12 K001–K040 | ExactSource Hit@10 | 28/40 = 70.00% |
| 2 | Phase 12 K001–K040 | ExactSource Hit@50 | 30/40 = 75.00% |
| 3 | Phase 12 U001–U040 | Human Success@5 | 23/40 = 57.50% |
| 3 | Phase 12 U001–U040 | Conservative P@5 | 0.2050 |
| 3 | Phase 12 U001–U040 | nDCG@5 | 0.6460 |
| 3 | Phase 12 U001–U040 | MRR | 0.4542 |
| 4 | U script (descriptive) | Success@5 | URDU 17/18; ROMAN 6/18; MIXED 0/4 |
| 5 | Phase 11 M0 | n=78 Hit@5 | 68/78; Roman train 61/64 = 95.31% |
| 5 | Phase 11 M1–M4 | n=78 Hit@5 | 68/78 (no improvement) |

**Diagnostic only:** H001–H040 Success@5 = 25/40 = 62.5%. ExactSource Hit@5 undefined.

---

## Files archived (moved to `experiments/archive/`, not deleted)

| Archived path | Reason |
| --- | --- |
| `obsolete_thesis_backups/*.pre_*.bak.docx` | Intermediate Word snapshots; live thesis is `Hashim_Shazad_243259_AU_Thesis_ULTRA.docx` |
| `obsolete_thesis_backups/_air_logo_from_backup.png`, `_current_image1.png` | Scratch images from thesis repair |
| `duplicate_plos_unzips/_unzipped/` | Duplicate extract of PLOS zips that remain under `Thesis_Paper/Clause_1_Formate/` |
| `obsolete_paper_backups/main.pre_honest.bak.tex` | Backup of PLOS tex; live file is `PLOS_ULTRA_paper/main.tex` |
| `obsolete_paper_backups/IEEE_conference_paper.zip` | Zip duplicate of `Thesis_Paper/IEEE/` source tree |

**Not archived (kept as evidence or reproducibility):** raw corpus, dictionary, M0 code, Phase 2–12 reports and CSVs, hashes, protocols, README, thesis/paper sources, Phase 11 inventory/ablation.

---

## Files retained (reproducibility-critical)

### Corpus and models
- `data/clean_articles.csv`
- `models/roman_urdu_dict_expanded.json`
- `experiments/phase8_final_freeze/FINAL_SYSTEM_MANIFEST.json`

### M0 implementation
- `experiments/phase5_roman_urdu/run_phase5.py`
- `experiments/phase2_oracle/run_phase2_pipeline.py` (character table used by Method D)
- `experiments/phase12_new_unseen_evaluation/run_phase12.py`

### Official evidence
- `experiments/phase8_final_freeze/DEVELOPMENT_RESULTS.md`
- `experiments/phase9_heldout_evaluation/PHASE9_RESULTS.md`
- `experiments/phase11_improvement/PHASE11_ABLATION_RESULTS.md`
- `experiments/phase11_improvement_design/PHASE11_INVENTORY.md`
- `experiments/phase12_new_unseen_evaluation/QUERY_GENERATION_REPORT.md`
- `experiments/phase12_new_unseen_evaluation/PHASE12_SEALED_PROTOCOL.md`
- `experiments/phase12_new_unseen_evaluation/PHASE12_RETRIEVAL_PROTOCOL.md`
- `experiments/phase12_new_unseen_evaluation/K_RESULTS.md`
- `experiments/phase12_new_unseen_evaluation/queries_k.csv`, `queries_u.csv`, `SEAL.json`
- `experiments/phase12_new_unseen_evaluation/K_TOP50_RETRIEVAL.csv`, `U_TOP50_RETRIEVAL.csv`, `U_TOP5_FOR_ANNOTATION.csv`
- `experiments/phase12_human_relevance/PHASE12_HUMAN_RESULTS.md`
- `experiments/phase12_human_relevance/U_QRELS.csv`, `U_PER_QUERY.csv`
- `experiments/phase10c_human_relevance/PHASE10C_RESULTS.md` (H diagnostic)
- `experiments/FINAL_EXPERIMENTAL_RESULTS_ANALYSIS.md`

### Thesis / paper
- `Thesis_Paper/Air_Thesis_Formate/Hashim_Shazad_243259_AU_Thesis_ULTRA.docx`
- `Thesis_Paper/Air_Thesis_Formate/ULTRA_THESIS_SUBMISSION_DRAFT.md`
- `Thesis_Paper/IEEE_M0/main.tex` (official IEEE-style M0 paper)
- `Thesis_Paper/Clause_1_Formate/PLOS_ULTRA_paper/main.tex` (official PLOS ONE M0 paper)
- `Thesis_Paper/ULTRA_IEEE_M0_FINAL_SUBMISSION.zip`
- `Thesis_Paper/ULTRA_PLOS_ONE_FINAL_SUBMISSION.zip`
- `Thesis_Paper/IEEE/main.tex` (historical MiniLM paper; not M0 headline)

---

## Misleading / outdated if quoted as M0 (retained, labeled)

See `Thesis_Paper/OUTDATED_DRAFTS.md`. Live PLOS LaTeX and IEEE_M0 are frozen M0. The AU Word thesis still contains historical SVM/P@15 Layer A in §§5.1–5.17 (labeled). `Thesis_Paper/PLOS_ONE/*.docx` and `Thesis_Paper/IEEE/main.tex` are historical, not M0. Older PLOS zips under `Clause_1_Formate/` predate the M0 rewrite.

---

## Claims supported / rejected

Supported and rejected lists: end of `Thesis_Paper/Air_Thesis_Formate/ULTRA_THESIS_SUBMISSION_DRAFT.md`.
