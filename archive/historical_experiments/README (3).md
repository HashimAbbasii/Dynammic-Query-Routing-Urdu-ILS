# Adaptive Dynamic Query Routing for Urdu IR

MS thesis project (Air University). Extends **ULTRA** (Bashir, Qaiser, Hussain, 2026).

**One sentence:** ULTRA’s θ = 150 character rule is the wrong switch; this system learns SHORT vs LONG as *headline is enough* vs *need the article*, then searches **two rooms** (headline index vs full-article index), with confidence **lights**.

Student: **Hashim Shazad** · Supervisor: **Dr. Adnan Aslam** · Branch for this work: `feat/dual-index-svm-routing`

This file is kept as a copy of `README.md` so older links still match the current story.

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

**Cue split (same 40):** cue fires n=18 → SVM 100% vs word count 11.11%; no cue n=22 → both 27.27%.

**Held-out dual-index P@5 (400 judgments):** word count 36.50%, always-headline/θ=150 35.00%, always-full 34.25%, SVM 33.00%. nDCG@5 highest for always-headline (0.6868).

**Do not report 96%.**

Full layout, demo command, and examiner FAQ: see `README.md` and `DEFENSE_DEMO.md`.
