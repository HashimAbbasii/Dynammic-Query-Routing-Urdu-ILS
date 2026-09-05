# POST–MODULE 2 M3-E UNION-POOL NAT EVALUATION PROTOCOL

**Status:** PRE-REGISTRATION / DESIGN ONLY (not executed)  
**Version:** 1.0  
**Date:** 2026-09-05  
**Branch context:** `research/post-phase12`  
**Role:** Evaluation-design gate before any further retrieval Module 3  
**Does not authorize:** retrieval runs, M0 edits, query edits, K/U use, parameter tuning, or new IR candidates

---

## 1. Purpose

Define a scientifically valid, pre-registered procedure to annotate a **union pool** of naturalistic (NAT) R-dev documents so that:

1. M0 and any frozen candidate Top-5 lists can be scored with **paired, comparable** Success@5;
2. NAT regressions observed under M0-only pool qrels (e.g. Module 2) can be decomposed into genuine usefulness loss vs **pool-measurement artifact**;
3. Future retrieval candidates are not rejected or accepted solely because they retrieve documents that were never labeled.

This protocol creates **evaluation capacity**. It does **not** select a retrieval system and does **not** claim generalization beyond R-dev.

---

## 2. Scientific motivation

### 2.1 Established facts

| Fact | Evidence |
| --- | --- |
| R-dev NAT = R051–R100 (n = 50) | `queries_r_dev.csv` |
| M0 NAT Success@5 = 12/50 = 24% | Frozen M0 Top-5 + `qrels_r_dev.csv` |
| Existing qrels judge **M0 Top-5 only** | First annotation pass (protocol §7.3 of R-dev construction) |
| Module 1 NAT Δ = 0 | Rankings identical to M0 |
| Module 2-A/B changed nearly all rankings; NAT = 8/50 under M0-pool qrels | `module2/MODULE2_RESULTS.md` |

### 2.2 Ambiguity that M3-E must resolve

Under M0-pool qrels, a candidate Top-5 that differs from M0 can yield lower Success@5 for any mix of:

1. **Genuine regression** — A/B documents leave Top-5 and are not replaced by other A/B documents;
2. **Useful substitution** — unlabeled but A/B-worthy documents replace M0 documents (invisible credit);
3. **Irrelevant substitution** — D/E (or C-only) documents replace M0 A/B documents;
4. **Mixture** of the above.

Without union-pool labels, Module 2 NAT (−4) is **scientifically under-determined**. Further retrieval modules that change Top-5 would inherit the same confound.

### 2.3 Why this precedes Module 3 retrieval

Lexical Module 1–2 are exhausted under pre-registered configs. Any new retrieval hypothesis needs a NAT metric that can credit newly retrieved useful documents. M3-E is that gate.

---

## 3. Frozen inputs

**Read-only.** Do not modify.

| Artifact | Role |
| --- | --- |
| `experiments/post_phase12_development/queries_r_dev.csv` | Sealed R-dev queries (NAT = R051–R100) |
| `experiments/post_phase12_development/SEAL.json` | Seal record |
| `experiments/post_phase12_development/R_TOP50_RETRIEVAL.csv` | Frozen M0 Top-50 (use ranks ≤ 5 for M0 Top-5) |
| `experiments/post_phase12_development/R_TOP5_FOR_ANNOTATION.csv` | Frozen M0 Top-5 annotation sheet |
| `experiments/post_phase12_development/qrels_r_dev.csv` | **Legacy** M0-pool qrels (retained; not overwritten) |
| `experiments/post_phase12_development/module2/M2-A_TOP50_RETRIEVAL.csv` | Frozen M2-A Top-50 |
| `experiments/post_phase12_development/module2/M2-B_TOP50_RETRIEVAL.csv` | Frozen M2-B Top-50 |
| `data/clean_articles.csv` | Headlines/snippets for judgment display |
| `experiments/phase12_human_relevance/ANNOTATION_PROTOCOL.md` | A–E rubric source |

Record SHA-256 of every frozen input in the M3-E pool/annotation manifests **before** annotation begins.

**Forbidden frozen edits:** M0 code, Method D, dictionary, Phase 12, K/U, R-dev queries, existing qrels rows, Module 1/2 retrieval CSVs.

---

## 4. Pool construction

### 4.1 Decision (pre-registered)

**Primary union pool for M3-E Phase 1:**

```text
For each NAT query q ∈ {R051…R100}:
  Pool(q) = UniqueDocs(
      M0_Top5(q)
    ∪ M2-A_Top5(q)
    ∪ M2-B_Top5(q)
  )
```

**Depth:** Top-**5** per system only (not Top-10/Top-50).

**Systems in Phase 1 union:** exactly **M0, M2-A, M2-B** — the systems whose NAT comparison is currently scientifically ambiguous.

### 4.2 Why Top-5 ∪ Top-5 (not Top-10/50)

| Option | Pros | Cons | Verdict |
| --- | --- | --- | --- |
| **Top-5 ∪ Top-5 (chosen)** | Matches Success@5 cutoff; minimal new labels; directly resolves Module 2 NAT ambiguity | Does not credit useful docs only at ranks 6–50 | **Best cost/validity for Success@5** |
| Top-10 ∪ Top-10 | Slightly richer | Extra annotation; still not needed for Success@5 | Reject for Phase 1 |
| Top-50 ∪ Top-50 | Near-complete candidate pool | ~50× labeling cost; invites post-hoc depth shopping | Reject |
| M0∪candidate only (one candidate) | Smaller | Would require re-annotation for every future candidate | Inferior to a **closed** retrospective set for M2 |

### 4.3 Multiple candidates together

**Yes — include M0 ∪ M2-A ∪ M2-B in one closed pool.**

**Rationale:**

- Both rejected candidates already exist as frozen artifacts.
- One annotation pass answers the Module 2 NAT confound for **both** without sequential peeking.
- Documents shared across systems are judged **once**.

**Future candidates (post–M3-E):** If a new pre-registered Module 3 retrieval candidate appears later, construct a **new** union  
`Pool_future(q) = UniqueDocs(M0_Top5(q) ∪ Cand_Top5(q) ∪ (optional prior labeled docs))`  
under a **new** pre-registration. Do **not** silently enlarge Phase 1 mid-annotation.

### 4.4 Query coverage (what to annotate)

**All NAT queries R051–R100 (n = 50).**

| Alternative | Why rejected |
| --- | --- |
| Only ranking-changed queries | Outcome-defined subset → selection bias; M1 would have empty set; understates unchanged successes |
| Only NAT failures | Cherry-picking hard cases |
| Stratified subsample only | Acceptable for **agreement measurement**, not for primary Success@5 on n=50 |

Changed-ranking queries may be **reported** descriptively after annotation; they must **not** define the annotation set.

### 4.5 Document identity

- Primary key: corpus `doc_id` (= `Index`).
- `UniqueDocs` = set of distinct `doc_id`.
- If the same article appears under one ID, judge once; reuse label for all systems that retrieved it.
- Near-duplicate different IDs: judge **independently** (no automatic merge). Record as limitation.

### 4.6 Zero-hit / short lists (e.g. R080)

- If a system returns \(k < 5\) hits, its contribution to the union is those \(k\) docs.
- If a system returns **0** hits, it contributes nothing to the pool for that query.
- Query remains in the NAT **denominator** for every system’s Success@5.
- Success@5 for a zero-hit system on that query = **0**.

### 4.7 Expected pool size (order of magnitude)

Upper bound ≤ \(50 \times 5 \times 3 = 750\) judgments; realized size ≪ bound due to overlap with M0 Top-5 and cross-candidate overlap. Exact counts go in `M3E_POOL_MANIFEST.json` after pool materialization (execution stage — not this design task).

### 4.8 Reuse of existing M0 labels

- For `(query_id, doc_id)` already in `qrels_r_dev.csv`, **carry forward** the frozen label into the union qrels **without re-judging**, unless a documented quality audit finds a clear clerical error (must be logged; not used to improve scores).
- New `(query_id, doc_id)` pairs only: new human judgments under §5–6.

---

## 5. Annotation procedure

### 5.1 Sequencing (mandatory)

```text
1. Freeze this protocol (no edits after annotation starts)
2. Materialize union pool + SHA manifests (execution phase)
3. Build system-blind annotation sheets (no system IDs visible)
4. Annotate new pairs
5. Merge carried M0 labels + new labels → union qrels
6. Compute paired Success@5 for M0, M2-A, M2-B
7. Write audit report
8. STOP evaluation work per §12
```

### 5.2 Annotator interface (system-blind)

Annotators see **only**:

- `query_id`, `query_text`
- `doc_id` (opaque)
- headline
- short snippet / news lead (same style as original R-dev Top-5 sheet)

Annotators must **not** see: system name (M0/M2-A/M2-B), rank, BM25/RRF score, retrieval path, candidate IDs, Module 2 metrics, or KI source IDs.

Shuffle document order **within** each query (fixed seed recorded in manifest) so rank position is not inferable from sheet order.

### 5.3 Retrospective evaluation of M2-A / M2-B

**Yes — retrospectively rescore M2-A and M2-B** using union-pool labels.

**How this stays non-tuning:**

| Allowed | Forbidden |
| --- | --- |
| Report paired Success@5 for already-frozen M0/M2-A/M2-B | Change M2-A/M2-B parameters, indexes, or fusion |
| Interpret whether Module 2 NAT −4 was pool artifact vs true regression | Select a new “winner” retrieval system for deployment solely from this |
| Inform whether evaluation was biased | Invent M2-C/D from union labels |
| Gate future Module 3 retrieval design | Peek at labels mid-annotation to alter pool |

M2-A/M2-B remain **rejected as M0 replacements** under the Module 2 protocol unless union-pool results plus KI guardrails (already failed) would have changed that decision — which they cannot reverse for KI. Union-pool NAT only clarifies the **NAT** side of the Module 2 audit trail.

### 5.4 Who annotates

See §10. Default for MS continuity: **same single-annotator mode** as original R-dev NAT, with documented limitation + optional agreement subsample.

---

## 6. Relevance rubric

**Preserve existing Phase 7 / Phase 12 / R-dev A–E definitions. No silent changes.**

| Code | Meaning |
| --- | --- |
| **A** | Directly satisfies the information need |
| **B** | Same occasion/event but incomplete |
| **C** | Topically related, not the asked need |
| **D** | Not relevant |
| **E** | Ambiguous (headline + snippet insufficient) |

**Success@5 definition (unchanged):** query succeeds iff **≥ 1** document in that system’s Top-5 has label **A or B**.

**A/B vs C:** C never counts as Success@5. Do not “upgrade” C to B to move the metric. Borderline A/B and B/C cases: see §10.

**No scientific necessity** has been identified to alter A–E for M3-E; changing the rubric would break comparability with Phase 12 U and original R-dev M0 NAT.

---

## 7. Metrics

### 7.1 Primary NAT metric (paired)

For each system \(S \in \{\mathrm{M0}, \mathrm{M2\text{-}A}, \mathrm{M2\text{-}B}\}\):

\[
\mathrm{Success@5}(S) = \frac{1}{50}\sum_{q \in \mathrm{NAT}} \mathbf{1}\big[\exists\, d \in \mathrm{Top5}_S(q):\ \mathrm{label}(q,d)\in\{A,B\}\big]
\]

Report: hits/50, percentage, Δ vs M0 (hits and rate).

### 7.2 Required secondary reports

| Report | Purpose |
| --- | --- |
| Per-query success vectors for M0 / M2-A / M2-B | Improved / worsened / unchanged vs M0 |
| Script strata (URDU / ROMAN / MIXED) using frozen M0 `detector_label` | Guardrail transparency |
| Pool statistics: \|Pool(q)\|, overlap fractions M0∩Cand | Annotation audit |
| Label source: `carried_m0` vs `new_m3e` | Provenance |
| Confusion-style transition: among M0 Success queries, how many remain Success under candidate | Decomposition of NAT drop |
| Among candidate-only docs in Top-5: fraction A/B vs C/D/E | Useful-sub vs irrelevant-sub |

### 7.3 Explicitly out of scope for M3-E

- ExactSource Hit@5 (KI) — already scored; not relabeled here  
- P@5 / nDCG@5 as headline promotion metrics (C-gain inflation risk) — optional descriptive only if pre-declared  
- Any target percentage (e.g. 80%)

### 7.4 Missing judgments

If any required `(q, d)` in a system Top-5 lacks a label after annotation close:

- **Do not** impute A/B.
- Mark metric for that system as **incomplete** until filled, **or** treat missing as non-A/B (must be pre-declared; default = **STOP and complete labels**).

---

## 8. Fair M0 vs candidate comparison

### 8.1 Paired rescoring rule

1. Build union labels \(L(q,d)\) for all docs in Phase 1 pool.  
2. For M0: evaluate Success@5 using **only** docs in `M0_Top5(q)` and labels \(L\).  
3. For M2-A / M2-B: evaluate using **only** docs in that candidate’s Top-5 and the **same** \(L\).  
4. Compare on the **same 50 NAT queries**, including zero-hit queries.

### 8.2 Relationship to legacy M0 Success@5 = 12/50

- Recalculated M0 Success@5 under union labels **must equal 12/50** if carried M0 labels are unchanged and M0 Top-5 is unchanged.  
- If recalculated M0 ≠ 12/50 → **STOP** (label carry bug or Top-5 mismatch).  
- Candidate Success@5 may rise or fall relative to the legacy 8/50 pool-restricted figures; both figures may be reported:

| Figure | Meaning |
| --- | --- |
| Legacy pool-restricted Success@5 | Historical Module 2 report (biased against new docs) |
| **Union-pool Success@5** | Fair paired metric (authoritative for M3-E conclusions) |

### 8.3 Ties

- Retrieval ties already resolved in frozen CSVs.  
- Metric ties (same Success@5): report equality; no forced ranking of systems.  
- Do not break ties by nDCG unless pre-registered as secondary descriptive only.

---

## 9. Leakage and blinding controls

| Control | Requirement |
| --- | --- |
| Protocol freeze | This document frozen before sheet generation / new labeling |
| No query rewriting | `queries_r_dev.csv` immutable |
| No K/U/H inspection for design or labeling | Already satisfied for this design; maintain in execution |
| System-blind sheets | No system/rank/score columns on annotator UI |
| No retrieval during annotation | Use frozen Top-5 lists only |
| No candidate-guided relabeling | Cannot change labels after seeing which system benefited |
| No editing Module 2 retrieval outputs | Rescore only |
| Legacy qrels preserved | New file for union qrels (see §11); do not overwrite `qrels_r_dev.csv` |
| Blinding of analyst during annotation | Person applying labels should not optimize for a preferred Δ; if same person as thesis author (as in R-dev), document dual-role limitation |

---

## 10. Reliability / adjudication

### 10.1 Primary mode (compatible with existing R-dev)

**Single annotator** (`thesis_author_single` or equivalent), same as original R-dev NAT.

**Justification:** Continuity with existing labels; MS resource limits; POST_PHASE12 §7.2 allows single annotator if limitation is documented.

**Mandatory documentation:** no inter-annotator agreement for the full set; subjectivity risk on B/C borderlines.

### 10.2 Recommended reliability add-on (pre-registered subsample)

If resources allow **without delaying the gate**:

- Double-annotate a **pre-specified** stratified subsample of **new** pairs only (e.g. 20% of new `(q,d)`, stratified by query script label), chosen **before** seeing labels.
- Report Cohen’s κ (or percent agreement) on A–E and on binary Useful={A,B} vs Other.
- Disagreements: supervisor adjudication on A/B and B/C borderlines (POST_PHASE12 §7.4).
- Adjudicated label becomes canonical for metrics.

### 10.3 Disagreement / E labels

- **E:** retained; does not count for Success@5; may trigger optional second look if pre-registered (default: keep E).  
- Do not convert E→C or E→B to raise Success@5.

---

## 11. Artifact and hash requirements

Proposed directory (execution later; not created by this design-only task unless supervisor requests file drop):

```text
experiments/post_phase12_development/m3e_evaluation/
  M3E_UNION_POOL_NAT_PROTOCOL.md      # this document
  M3E_POOL_MANIFEST.json              # pool construction + SHAs
  M3E_ANNOTATION_SHEET.csv            # system-blind rows for new judgments
  M3E_NEW_JUDGMENTS.csv               # filled new labels only
  M3E_QRELS_UNION.csv                 # carried M0 ∪ new judgments
  M3E_ANNOTATION_MANIFEST.json        # annotator, dates, κ, counts
  M3E_METRICS.json                    # paired Success@5 + transitions
  M3E_AUDIT_REPORT.md                 # human-readable conclusions
```

### 11.1 Suggested schemas

**`M3E_ANNOTATION_SHEET.csv` (blind):**  
`annotation_row_id, query_id, query_text, doc_id, headline, snippet, shuffle_position`

**`M3E_NEW_JUDGMENTS.csv`:**  
`query_id, doc_id, relevance_label, annotator, annotation_date, label_source=new_m3e`

**`M3E_QRELS_UNION.csv`:**  
`query_id, doc_id, relevance_label, annotator, annotation_date, label_source ∈ {carried_m0, new_m3e, adjudicated}`

**`M3E_POOL_MANIFEST.json` must include:**  
frozen input SHAs; systems in union; depth=5; per-query pool sizes; total unique pairs; carried vs new counts; git commit; protocol version hash; confirmation `qrels_r_dev.csv` unchanged.

**`M3E_ANNOTATION_MANIFEST.json` must include:**  
annotator mode; agreement subsample definition (if any); κ; label histogram; zero-hit query handling; blinding confirmation; stop-after-annotation flag.

### 11.2 Provenance / audit log

Append-only log of: protocol freeze time, pool build time, annotation start/end, any clerical corrections, adjudication events. No metric-driven pool edits.

---

## 12. Stop conditions

### 12.1 Stop annotation work and proceed when

1. Union pool materialized and SHA-verified;  
2. All new pairs labeled (or adjudicated subsample complete);  
3. Recalculated M0 Success@5 = **12/50** (sanity);  
4. Paired Success@5 published for M0, M2-A, M2-B with improved/worsened/unchanged;  
5. Written conclusion answering: *Was Module 2 NAT −4 primarily pool artifact, genuine regression, or mixed?*  
6. Decision recorded: evaluation gate **closed** for Module 2 NAT ambiguity.

### 12.2 Stop and escalate (do not proceed to Module 3 retrieval) if

- Frozen SHA mismatch or temptation to edit queries/qrels/M0;  
- Recalculated M0 Success@5 ≠ 12/50 unexplained;  
- Blinding broken (system identity visible during labeling);  
- Labels altered after seeing which system benefits;  
- K/U used;  
- Pool silently expanded mid-study;  
- Rubric changed without amendment record.

### 12.3 After M3-E closes — scientific branching

| Finding | Next stage |
| --- | --- |
| M2 NAT drop largely **pool artifact**; KI guardrails still fail | Keep M2 rejected; evaluation capacity ready for future candidates |
| M2 NAT drop largely **genuine regression** | Strengthens M2 rejection; still no M2 revival |
| Mixed | Report decomposition; do not average away regressions |
| Evaluation capacity ready | Only then consider a **separately pre-registered** retrieval Module 3 (e.g. identity/date rerank), if still justified |

---

## 13. Limitations

1. **Top-5 union only** — useful documents exclusively at ranks 6–50 remain unlabeled.  
2. **Single-annotator primary mode** — no full-set IAA unless subsample add-on runs.  
3. **Retrospective M2 scoring** — clarifies history; does not license post-hoc M2 tuning.  
4. **Near-duplicate different doc_ids** — judged separately; may inflate topical C.  
5. **R-dev only** — no claim about K/U or future unseen tests.  
6. **Does not fix ExactSource identity hardness** — KI neighbour ambiguity remains evaluation-hard.  
7. **Does not improve retrieval** — M3-E is measurement, not a system.  
8. **Dual role** (author as annotator) — same limitation as original R-dev NAT.

### What M3-E can establish

- Fair paired NAT Success@5 for M0 vs frozen candidates whose Top-5 differ.  
- Whether Module 2’s NAT −4 was measurement-biased.  
- A reusable template for future candidate union pools.

### What M3-E cannot establish

- That any system generalizes to unseen tests.  
- That M0 should be replaced.  
- That neural/lexical Module 3 will work.  
- A path to a target percentage (e.g. 80%).

---

## 14. Recommended next action

1. **Supervisor review and freeze** of this M3-E protocol (v1.0).  
2. **Do not** implement retrieval Module 3 yet.  
3. Upon approval, execute **pool materialization + blind annotation** only (separate engineering task).  
4. Publish paired M0 / M2-A / M2-B union-pool NAT metrics and close the Module 2 NAT ambiguity.  
5. Only afterward, reconsider whether any **new retrieval hypothesis** remains justified.

**End of protocol.**  
No retrieval, no labeling, and no metric computation were performed in producing this document.
