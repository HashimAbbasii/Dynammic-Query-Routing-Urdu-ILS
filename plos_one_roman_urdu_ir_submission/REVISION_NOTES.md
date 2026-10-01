# Revision notes — PLOS ONE manuscript

Base file preserved: `manuscript.tex`  
Revised file: `manuscript_revised.tex`  
Date: 2026-09-23

All ExactSource counts, phase decisions, TEST-sealed language, and ethics text were left unchanged except where noted below as wording/context updates.

---

## Priority 1 — Soften the “no new mechanism” claim

**Done.** Replaced global wording of the form:

> “No shared previously unmodeled structural phenomenon survived the evidence test”

with the evidence-bounded form:

> “No common previously unmodeled mechanism was identified among the 31 analyzed candidate-generation failures.”

Applied in **Abstract**, **Results (CG coverage)**, **Discussion**, and **Conclusion**.

---

## Priority 2 — Reframe the 80% target

**Done.**

- RQ4 rewritten to a neutral gap question: *“How large is the remaining first-stage retrieval gap after the preregistered methods are frozen?”*
- Stretch target described as a **preregistered development stretch target / internal planning bar**, not an external benchmark.
- Preferred wording used in Abstract, Table 1 note, Discussion (RQ4), and Conclusion:
  *“Against a preregistered development stretch target of approximately 80% ExactSource Hit@5, the best observed Hit@5 was 25% (55 percentage points short).”*

---

## Priority 3 — W1 vs LLM1 distinction

**Done.** Added **Table 4** with:

| Slice | n | Dense Hit@5 | Hybrid Hit@5 | Hybrid Hit@50 |
|-------|--:|------------:|-------------:|--------------:|
| W1 | 51 | 15/51 | 11/51 | 25/51 |
| LLM1 | 29 | 5/29 | 6/29 | 15/29 |
| Total | 80 | 20/80 | 17/80 | 40/80 |

Counts are only those already present in the prior manuscript / Phase 14 + Phase 13 descriptive slice. No new counts invented. LLM1 rates labeled descriptive / not a tuning target.

---

## Priority 4 — Statistical support

**Done.**

- New Methods subsection **Confidence intervals** (Wilson score, 95%).
- Reported for:
  - Dense Hit@5 20/80 → **0.250 [0.168, 0.355]**
  - Hybrid Hit@5 17/80 → **0.2125 [0.137, 0.314]**
  - Hybrid Hit@50 40/80 → **0.500 [0.393, 0.607]**
- Noted that Dense vs Hybrid comparisons are **paired** (same queries); intervals are descriptive; no formal superiority test claimed.
- CIs also appear in Abstract, Table 1, Results prose, and Conclusion.

---

## Priority 5 — Contribution statement

**Done.** Explicit positive empirical-diagnostic framing added/strengthened in **Introduction** and **Discussion** (and echoed in Abstract/Conclusion):

> This paper does not propose a new retrieval algorithm. It provides a preregistered empirical and diagnostic evaluation of first-stage recovery for ordinary Roman Urdu known-item queries against a frozen lexical baseline, quantifies the gap relative to an aligned development setting, and shows that residual candidate-generation failures are heterogeneous and map onto existing method families rather than a single newly identified mechanism.

---

## Priority 6 — Limitations

**Done.** Kept existing limitations and added:

1. Results are specific to the 111,860-article Urdu news collection and should not be assumed to generalize automatically to social media, web search, or other corpora.
2. ExactSource known-item recovery is not identical to usefulness for real users.

Also pointed Limitations at Table 4 for the W1/LLM1 split.

---

## Priority 7 — Abstract cleanup

**Done.** Abstract restructured to:

1. Problem (ordinary Roman Urdu gap after frozen M0)
2. Design (preregistered Program B; TRAIN+DEV; TEST sealed)
3. Main results (Dense Hit@5 25% with CI; Hybrid Hit@50 50% with CI; stretch shortfall)
4. Diagnostic (31 CG: Covered 17 / Partial 14 / Uncovered 0; softened mechanism claim)
5. Implication (empirical-diagnostic contribution, not a new algorithm)

Method-by-method clutter (letter-name, three-way, Wikipedia, cascades) removed from the Abstract; those details remain in Results/Discussion.

---

## Priority 8 — Optional figures

**Deferred.** Textual/table priorities completed first. PLOS uploads figures separately from the manuscript; no Fig captions were added. Can be added later (Hit@k bars; SUCCESS / RANKING_FAILURE / CG_FAILURE funnel) without changing counts.

---

## What was intentionally not changed

- Frozen Hit@k cells in Tables 2 and 3
- Method decision labels (Baseline / Unsupported / Partially supported)
- TEST sealed / never opened language
- Ethics statement
- Supporting Information S1–S6
- Core phase narrative and integrity constraints
- Bibliography keys

---

## Compile

```bash
pdflatex manuscript_revised
bibtex manuscript_revised
pdflatex manuscript_revised
pdflatex manuscript_revised
```

Or with Tectonic from this folder:

```bash
tectonic -X compile manuscript_revised.tex
```
