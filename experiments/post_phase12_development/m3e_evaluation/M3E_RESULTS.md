# M3-E Results — Union-Pool NAT Evaluation

**Status:** EXECUTED  
**Date:** 2026-09-05  
**Protocol:** `M3E_UNION_POOL_NAT_PROTOCOL.md` / `M3E_UNION_POOL_NAT_EVALUATION_PROTOCOL.md` (v1.0, identical)  
**Scope:** Evaluation / annotation only — no retrieval, no Module 3 candidate

---

## 1. Execution status

**Complete.** Union pool materialized, all 312 new pairs labeled under system-blind sheets, carried M0 labels merged into `M3E_QRELS_UNION.csv` (legacy `qrels_r_dev.csv` untouched), paired Success@5 computed for M0 / M2-A / M2-B.

Sanity checks passed. Frozen inputs remained byte-identical postflight.

---

## 2. Pool size statistics

| Quantity | Value |
| --- | --- |
| NAT queries | R051–R100 (n = 50) |
| Systems | M0 ∪ M2-A ∪ M2-B Top-5 |
| Unique `(query_id, doc_id)` pairs | **557** |
| Carried from `qrels_r_dev.csv` | **245** |
| New judgments | **312** |
| Pool size / query | min 5, median 12, max 15, mean **11.14** |

Provenance of system membership: `M3E_POOL_PROVENANCE.csv` (analyst-only; not shown to annotator).

---

## 3. Annotation counts (A/B/C/D/E)

**New pairs only (`M3E_NEW_JUDGMENTS.csv`):**

| A | B | C | D | E |
| --- | --- | --- | --- | --- |
| 21 | 6 | 56 | 229 | 0 |

**Full union (`M3E_QRELS_UNION.csv`):**

| A | B | C | D | E |
| --- | --- | --- | --- | --- |
| 37 | 19 | 84 | 417 | 0 |

**Mode:** `thesis_author_single` (same as original R-dev NAT). Six draft labels were calibrated to match frozen A–E / R-dev style (logged in `M3E_ANNOTATION_MANIFEST.json`). No agreement subsample.

---

## 4. M0 original vs union-pool Success@5

| Figure | Result | Meaning |
| --- | --- | --- |
| **Legacy M0-pool** (original qrels) | **12/50 = 24%** | Historical sealed baseline |
| **Union-pool rescore of M0** | **12/50 = 24%** | Required sanity: carried labels + frozen M0 Top-5 |

Union-pool M0 equals legacy M0, as required. Original qrels were **not** overwritten.

---

## 5. M2-A union-pool Success@5

| Figure | Result |
| --- | --- |
| Legacy M0-pool-restricted (Module 2 report) | **8/50 = 16%** |
| **Union-pool (authoritative for M3-E)** | **11/50 = 22%** |
| Δ vs M0 (union) | **−1 hit (−2 pp)** |

---

## 6. M2-B union-pool Success@5

| Figure | Result |
| --- | --- |
| Legacy M0-pool-restricted (Module 2 report) | **8/50 = 16%** |
| **Union-pool (authoritative for M3-E)** | **11/50 = 22%** |
| Δ vs M0 (union) | **−1 hit (−2 pp)** |

---

## 7. Paired improved / worsened / unchanged (vs M0)

| Candidate | Improved | Worsened | Unchanged |
| --- | --- | --- | --- |
| M2-A | **1** (R080) | **2** (R087, R096) | **47** |
| M2-B | **1** (R065) | **2** (R053, R074) | **47** |

---

## 8. Script-stratum results (M0 `detector_label`)

NAT R-dev script mix under frozen M0 detector: URDU n=1, ROMAN n=36, MIXED n=12.

| System | URDU | ROMAN | MIXED |
| --- | --- | --- | --- |
| M0 | 1/1 | 7/36 | 4/12 |
| M2-A | 1/1 | 5/36 | 4/12 |
| M2-B | 1/1 | 7/36 | 3/12 |

M2-A’s union NAT shortfall vs M0 is concentrated in **ROMAN** (−2). M2-B’s is in **MIXED** (−1).

---

## 9. R080 handling

| Item | Value |
| --- | --- |
| Query | R080 (`mickey arthur`) |
| In NAT denominator | **Yes** |
| M0 Top-5 hits | **0** → Success@5 = **0** (no synthesized docs) |
| M2-B Top-5 hits | **0** → Success@5 = **0** |
| M2-A Top-5 hits | **5** (all labeled **A** — named-entity main subject) → Success@5 = **1** |

This is the sole M2-A paired improvement vs M0.

---

## 10. Sanity checks

| Check | Result |
| --- | --- |
| Legacy M0 Success@5 under `qrels_r_dev.csv` | **12/50** reproduced |
| Union-rescored M0 Success@5 | **12/50** |
| New-pair count | 312 / 312 complete |
| Carried ∩ new overlap | none |
| Missing Top-5 labels | none |
| Rubric | unchanged A–E |
| K/U / unseen test | not used |

---

## 11. Integrity / hash verification

Preflight = postflight (frozen inputs unchanged):

| Artifact | SHA-256 |
| --- | --- |
| `queries_r_dev.csv` | `1603b37eeee41fa6270f4e13d185c8eebd4512d025cd5fc67e8a81de9407e75f` |
| `R_TOP50_RETRIEVAL.csv` | `927a14a25b6f1de2a5c28aabdc2d8cbc0d4336e0b2b437490691a7bff63a2aa2` |
| `R_TOP5_FOR_ANNOTATION.csv` | `042006bc3232719514a6ca4b638f4e6348415d168294271fe366ff95704b23c5` |
| `qrels_r_dev.csv` | `506305b5401102a3659d21b69c7a937bcdcde78b21a1409a6a6132255ff37bcb` |
| `M2-A_TOP50_RETRIEVAL.csv` | `b9d4c77ef4cf2a7ba7442031a79c7cb1c78eaf00b88bcdabc4627d084d3d801e` |
| `M2-B_TOP50_RETRIEVAL.csv` | `9a16855977fa43fe8766d325065f621009182094d60f999e080051d50e45630a` |

Output artifact hashes: `M3E_ANNOTATION_MANIFEST.json`.

---

## 12. Limitations

1. Top-5 union only — useful docs exclusively at ranks 6–50 remain unlabeled.  
2. Single-annotator mode — no full-set IAA.  
3. Retrospective M2 scoring clarifies history; does not license post-hoc M2 tuning.  
4. Near-duplicates with different `doc_id` judged independently.  
5. R-dev only — no claim about K/U or future unseen tests.  
6. Dual role (author as annotator) — same limitation as original R-dev NAT.  
7. M3-E does not improve retrieval and does not select a deployment system.

---

## 13. Scientific interpretation

**Do not treat 11/50 vs 8/50, or 11/50 vs 12/50, as evidence for a new retrieval architecture.**

M3-E’s purpose was to test whether Module 2’s NAT −4 (8/50 vs M0 12/50 under **M0-only** qrels) was a **pool-measurement artifact**, a **genuine usefulness regression**, or **mixed**.

### Decomposition

1. **Pool artifact (substantial):** Under fair union labels, both M2-A and M2-B rise from **8/50 → 11/50**. About **+3** of the historical −4 is recovered by crediting candidate-only Top-5 documents that legacy qrels never labeled. Candidate-only Top-5 docs are ~9% A/B (M2-A 16/183; M2-B 12/133) — some useful substitution was invisible before.

2. **Genuine paired shortfall (small but real):** Fair comparison still leaves both candidates at **11/50 vs M0 12/50** (−1). Paired flips: each candidate improves on **1** query and worsens on **2**.

3. **Module 2 rejection stand:** KI guardrails already failed in Module 2. Union-pool NAT clarification does **not** revive M2-A/M2-B as M0 replacements. It closes the **NAT measurement confound**.

### Module 2 NAT −4 verdict

**Mixed — majority pool artifact, residual genuine regression under paired Success@5.**

---

## Decision

**M3-E VALID:** union-pool evaluation completed successfully and provides a valid paired NAT evaluation basis.

Rationale: protocol followed; system-blind annotation sheet confirmed; R080 kept in denominator with zero-hit Success=0 for M0/M2-B; legacy and union M0 Success@5 both 12/50; all system Top-5 labels present; frozen inputs SHA-matched on re-verification; `qrels_r_dev.csv` not overwritten.

Read-only re-verification artifact: `M3E_INTEGRITY_REPORT.json`.

---

## Artifacts

```text
experiments/post_phase12_development/m3e_evaluation/
  M3E_UNION_POOL_NAT_PROTOCOL.md
  M3E_UNION_POOL_NAT_EVALUATION_PROTOCOL.md
  M3E_POOL_MANIFEST.json
  M3E_POOL_PROVENANCE.csv
  M3E_ANNOTATION_SHEET.csv
  M3E_NEW_JUDGMENTS.csv
  M3E_QRELS_UNION.csv
  M3E_ANNOTATION_MANIFEST.json
  M3E_METRICS.json
  M3E_PROVENANCE_AUDIT.json
  M3E_INTEGRITY_REPORT.json
  M3E_RESULTS.md
```

**STOP.** No M3-I, neural retrieval, reranking, or other candidate is authorized in this task.
