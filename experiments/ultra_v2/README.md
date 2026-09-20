# ULTRA v2

**Phase:** 14 FINAL REPORT — Program B **FROZEN**  
**Branch:** `research/ultra-v2-strengthening`  
**Status:** Phases 2–13 complete; **cite `PHASE14_FINAL_REPORT.md`** (SHA-256 in `PHASE14_FINAL_REPORT.sha256`) for all Program B claims. TEST sealed / never retrieved.

This folder is the home of ULTRA v2 work. It does **not** replace the frozen PLOS ONE M0 study.

---

## Current phase

**Phase 14 frozen.** Single source of truth: [`PHASE14_FINAL_REPORT.md`](PHASE14_FINAL_REPORT.md).

Do **not** inspect sealed TEST query text. Do not retune frozen methods.

---

## Purpose

Phase 12 K/U was unseen **relative to frozen M0**. It is **not** unseen relative to ULTRA v2 development:

- K001–K040, U001–U040, and H001–H040 have been retrieved, labeled, sliced by script, and published.
- Their misses are listed in the PLOS evidence trail.
- Using them as v2 TEST would be test leakage.

ULTRA v2 therefore needs a **new** KN (known-item) + NL (naturalistic) benchmark, with TRAIN / DEV / TEST separation and a sealed TEST set.

---

## What exists now

| Path | Role |
| --- | --- |
| `PROTOCOL.md` | Authoritative Phase 1 research protocol |
| `DATA_DICTIONARY.md` | Field definitions and allowed values |
| `REGISTRY.md` | Collection log + experiment template (no retrieval runs) |
| `benchmark/` | TRAIN/DEV/TEST query CSVs; TEST `seal.json` |
| `annotation/` | NL/KN judging guidelines |
| `evaluation/` | Metric definitions and JSON/CSV schemas |
| `phase2_roman/` | Phase 2 Roman audit, runner, TRAIN/DEV results (negative lexical result) |

---

## What does **not** exist yet

- Relevance judgments (`qrels.csv`)
- Retrieval dumps
- Roman normalizers, dense indexes, fusion, or rerankers
- Any Hit@k / Success@5 / nDCG numbers on this benchmark

---

## Relationship to frozen PLOS / M0

| Item | Location | ULTRA v2 rule |
| --- | --- | --- |
| M0 implementation | `experiments/phase5_roman_urdu/run_phase5.py` | **Do not edit in place.** Import as frozen baseline later. |
| PLOS scores | `results/`, `Papers/PLOS_ONE/` | Historical. Do not rewrite. |
| QTRN n=78 | `experiments/phase2_oracle/` | Legacy M0 development pool. Not v2 TEST. |
| K / U | `experiments/phase12_new_unseen_evaluation/` | Historical M0 unseen eval. **Cannot become v2 TEST.** |
| H001–H040 | Phase 9 / 10C | Diagnostic traps. Not v2 TEST. |

Frozen PLOS headlines remain:

- n=78 ExactSource Hit@5 = 68/78 = 87.18%
- K ExactSource Hit@5 = 27/40 = 67.50%
- U Success@5 = 23/40 = 57.50%

These are **not** ULTRA v2 results. Do not average them with future v2 numbers. Do not treat 80% as a scientific threshold.

---

## How Phase 1 proceeds

1. Review `PROTOCOL.md` (this implementation).
2. Human authorization to collect queries (granted 2026-09-09).
3. Write TRAIN/DEV/TEST queries under the protocol.
4. Validate with `scripts/validate_benchmark.py` → `PASS`.
5. Seal TEST with `scripts/seal_test.py` → `SEALED` / `MATCH`.
6. Annotate NL from **pooled** candidates after retrieval systems exist — still no Phase 2 in this step. Official NL labels require a second judge.

---

## Warning

**QTRN, H001–H040, K001–K040, U001–U040, Phase 11 token inventories, and listed historical misses are forbidden as v2 TEST.** A new filename does not make a copied information need unseen.

---

## Scripts

From the repository root:

```text
python experiments/ultra_v2/scripts/validate_benchmark.py
python experiments/ultra_v2/scripts/seal_test.py --input <test-dir> --output <seal.json>
python experiments/ultra_v2/scripts/verify_test_seal.py --seal <seal.json>
```

Current collection validates as `PASS`. TEST seal verifies as `MATCH`.
