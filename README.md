# Adaptive Dynamic Query Routing for Urdu IR

MS thesis project (Air University). Extends **ULTRA** (Bashir, Qaiser, Hussain, 2026).

**One sentence:** ULTRA’s θ = 150 character rule is the wrong switch; this system learns SHORT vs LONG as *headline is enough* vs *need the article*, then searches **two rooms** (headline index vs full-article index), with confidence **lights**.

Student: **Hashim Shazad** · Supervisor: **Dr. Adnan Aslam** · Branch for this work: `feat/dual-index-svm-routing`

---

## Verified numbers (do not mix)

Recomputed from frozen files on 23 Aug 2026. Deployed pickle is **12 features**. Phase 3B **86/84** is the frozen **V2 (8-feature)** result and was not overwritten. Dictionary on disk: **198** pairs.

| Layer | What it is | SVM | Word count ≥ 6 | θ = 150 |
| --- | --- | --- | --- | --- |
| Development / CV | Learnability only. **Not** the paper headline. | 100% on some splits | — | 50% |
| Frozen Phase 3B (V2, 50 primary) | Independent generalization vs a fair tape | **86%** (43/50) | **84%** (42/50) | — |
| Frozen traps H001–H040 | Need labels; **never trained on** | **60%** | **20%** | **50%** |

McNemar Phase 3B: 2 SVM-only-correct, 1 word-count-only, p = 1.0.  
McNemar traps: 16–0, p < 0.001.

**Cue split on the same 40 (the scientific limit):**

| Slice | n | SVM | Word count |
| --- | --- | --- | --- |
| V3 cue fires (why/how/fact phrasing) | 18 | **100%** (18/18) | 11.11% (2/18) |
| No cue | 22 | **27.27%** | **27.27%** |

**Dual-index graded P@5 (same 40 queries, 400 judgments):** word count **36.50%**, always-headline / θ=150 **35.00%**, always-full **34.25%**, SVM **33.00%**.  
nDCG@5 is **highest for always-headline (0.6868)**, then word count 0.6476, SVM 0.6149, always-full 0.6020.

**Phase 2.5 dual-index P@5 (33 judged queries, depth 5):** SVM **35.76%**, word count **35.15%**, θ=150 **32.73%**. Tiny SVM edge. Judgments stop at rank 5.

**Do not report 96%.** That number leaks trap overlap into Phase 3B after the 12-feature retrain.

---

## What the system actually does

```
Query (Urdu or Roman Urdu)
        │
        ▼
Roman Urdu dictionary (198 pairs on disk) if Latin script
        │
        ▼
SVM: SHORT = headline enough | LONG = need the article
        │
        ▼
HIGH ≥ 85%  → search only the chosen room
MED  60–85% → mix headline room + full-article room
LOW  < 60%  → expand query, then mix both rooms
```

Rooms:

- **Headline room** — semantic search on titles (`data/headline_embeddings_phase2_5_cache.npy`)
- **Full-article room** — Chroma collection `urdu_news` (~111,860 articles)

Code: `validate/dual_index_routing/router.py`, `retrieve.py`.

---

## How to run the defense demo

From repo root, with `ultra_env` (or any env that has the project packages):

```text
python validate/dual_index_routing/demo_confidence_tiers.py
```

Expected live behaviour (already captured in `demo_confidence_tiers.json`):

| Light | Query | Conf. | Action | Top-1 (live, 23 Aug 2026) |
| --- | --- | --- | --- | --- |
| GREEN | کرکٹ میچ | 99.2% | headlines only | کرکٹ کلاسک وقار کی میچ وننگ کارکردگی |
| YELLOW | ڈالر کی قیمت کتنی بڑھی | 82.7% | mix both rooms | ڈالر کی قدر میں پھر اضافہ |
| YELLOW (near RED) | آج سٹاک ایکسچینج کتنے پوائنٹ پر | 65.6% | mix both rooms | سٹاک ایکسچینج میں مندی کا رجحان |

RED (<60%) is coded but did not fire on the 23 Aug 2026 probe of demo + trap queries. Do not use the stale JSON that showed 53.8% on the score query (that query is GREEN ~97% on the deployed pickle).

Spoken script: `DEFENSE_DEMO.md`.

Thesis figures (regenerate anytime):

```text
python validate/dual_index_routing/make_defense_figures.py
```

---

## Project layout (current)

```
models/svm_classifier.pkl          # deployed 12-feature SVM
models/scaler.pkl
models/training_info.json
models/roman_urdu_dict_expanded.json
models/backup_v2_pre_trap_retrain_2026-08-22/   # frozen V2 86/84
validate/phase3/                   # Phase 3A extractor + frozen 3B CSVs
validate/phase2_5/                 # 33-query human P@5 pilot
validate/dual_index_routing/       # two rooms, lights, held-out traps
Thesis_Paper/Air_Thesis_Formate/Hashim_Shazad_243259_AU_Thesis_ULTRA.docx
Thesis_Paper/Clause_1_Formate/PLOS_ULTRA_paper/   # supervisor PLOS LaTeX
Thesis_Paper/IEEE/main.tex                        # IEEE conference draft (not yet Xplore)

```

---

## Setup

```text
conda activate ultra_env
pip install sentence-transformers chromadb scikit-learn pandas numpy matplotlib
```

Large artifacts (not all on GitHub): `data/clean_articles.csv`, `data/chromadb/`, headline embedding cache.

---

## Examiner FAQ (short)

**100% vs 86% vs 60%?** Three tables. CV = learnable. 86/84 = frozen V2 vs word count. 60/20 = frozen need-traps. Never substitute one for another.

**Did routing improve retrieval?** On the 40 traps, no. Word count has the best graded P@5. That is in the thesis on purpose.

**Two independent annotators?** No. Protocol labels, first pass assisted, then saved. 40/40 with the written rule.

**Is θ=150 a fair baseline?** No, for this query set it almost never fires LONG. Word count ≥ 6 is the fair simple rule.

---

## Contact

Hashim Shazad · MS Artificial Intelligence · Air University
