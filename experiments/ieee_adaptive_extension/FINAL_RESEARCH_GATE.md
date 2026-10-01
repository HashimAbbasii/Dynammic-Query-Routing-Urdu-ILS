# FINAL RESEARCH GATE — Roman Urdu → Urdu IR Novelty Discovery

**Date:** 2026-09-22  
**Branch:** `research/roman-urdu-novelty-extension`  
**Commit baseline:** `44acf3a` (session start)  
**Publication targets considered:** IEEE + PLOS ONE only  

**TEST accessed:** NO  
**Program A modified:** NO  
**Program B frozen artifacts modified:** NO  

---

## Final decision

# NO-GO

No genuinely novel, technically distinguishable, sufficiently prevalent, IEEE/PLOS-defensible **retrieval mechanism** survived empirical failure-mechanism discovery and literature separation inside:

> Roman Urdu user query → Urdu-script news document retrieval

---

## What was investigated (this round)

1. Reconfirmed population structure explaining **68/78 = 87.18%** ExactSource Hit@5 (title-like Urdu + Method-D-aligned `title_roman`).
2. Reconfirmed Program B hardness (Method-D 5/80; Dense 20/80; BND ceiling 49/80).
3. Ran LEVEL 1–5 tagging on all **n=80** naturalistic Roman TRAIN+DEV queries (`FINAL_FAILURE_MECHANISM_PER_QUERY.csv`).
4. Fragmented the prior coarse “entity ≈ 18” CG bucket into finer bridge mechanisms.
5. Literature-checked every surviving empirical cell against 2021–2026 IR/NLP work (code-switching IR, mixed-language queries, TOT, brand EL, MSIR/transliteration, dense CLIR).
6. Applied novelty tests A–K and IEEE/PLOS fit; all candidates **REJECT**.

Artifacts:

- `FINAL_FAILURE_MECHANISM_DISCOVERY.md`
- `FINAL_FAILURE_MECHANISM_PER_QUERY.csv`
- `FINAL_MECHANISM_SUMMARY.json`
- `FINAL_NOVELTY_CANDIDATE_MATRIX.csv`
- this file: `FINAL_RESEARCH_GATE.md`

---

## Research question (answered)

> If obvious Roman→Urdu bridging approaches are already known, what information is actually missing when a naturalistic Roman Urdu query fails — and does that missing information define a new mechanism?

**Answer:** Failures are **heterogeneous**. The empirically visible “missing bridge” is a **mixture** of:

- code-switched English jargon/brand/acronym composed with entity/event intent,
- institutional descriptive aliases,
- cross-script entity variants,
- underspecified referents,
- residual paraphrase / rare vocabulary,

…not a single intermediate representation that is under-addressed in the literature.

---

## Exact reason for NO-GO

1. **No new dominant mechanism:** largest non-closed CG cells are **6/31** and **5/31**; none reaches a prevalence level that can responsibly underwrite recovering ≥15 additional golds toward 64/80.
2. **Every empirically supported cell maps to existing families:** code-switching IR (MiLQ; CSR-L), TOT/underspecification, brand/entity linking, MSIR/transliteration (Gupta; Chari; Butt), dense paraphrase matching — or to **CLOSED** gates (C2 institutional alias; routing; RRF; QE; ColBERT/SPLADE/Doc2Query).
3. **Combination of known bridges is not novelty** under the scientific honesty rule.
4. **Domain transfer to Roman Urdu is not methodological novelty** for IEEE method positioning; PLOS ONE could host rigorous empirical negatives, but that is not a new mechanism GO.
5. **80% remains structurally blocked** by the BND Top-50 ceiling (**49/80**) unless CG expands via methods that are not novel under this gate.

---

## Novelty tests (aggregate)

| Test | Result |
|---|---|
| A Exact mechanism already proposed? | YES (for each cell, under standard names) |
| B Same mechanism under another name? | YES |
| C Application of existing technique to Urdu? | YES |
| D Combination of known methods? | YES if stacked to chase coverage |
| E Technically distinguishable? | NO (after literature separation) |
| F Solves demonstrated failure? | PARTIAL per cell only |
| G Sufficient prevalence? | NO for any single cell |
| H Plausible CG improvement? | Limited per cell (≤6) |
| I Plausible Hit@5 to 64/80? | NO without unsupported assumptions |
| J Evaluable without TEST leakage? | YES (not decisive) |
| K ~3 months? | YES for known methods (not decisive) |

---

## IEEE assessment

- **Methodological contribution:** not identified.
- A reviewer would reasonably classify proposed “fixes” as MSIR/CS-IR/EL/dense transfers or ensembles.
- Ablations would compare known modules, not a new mechanism.
- Empirical diagnosis of title_roman vs naturalistic Roman is a **limitation / evaluation finding**, not an IEEE method claim.

## PLOS ONE assessment

- A rigorous, reproducible **empirical failure analysis / negative method result** could be scientifically informative.
- That is **not** authorization to claim a new retrieval mechanism.
- This gate’s question was novelty of a mechanism → **NO-GO**.

---

## 80% feasibility

- Need **64/80** Hit@5.
- Current union Top-50 ceiling **49/80**.
- Need ≥ **15** new unique golds in CG, then rank them into Top-5.
- No surviving novel mechanism has evidenced path to those 15 golds.

---

## Exact next step

### STOP.

Do **not** implement another variant under a novelty claim.

Do **not** revive closed directions (routing, RRF, transliteration-as-novelty, institutional alias, ColBERT/SPLADE/Doc2Query, entity linking alone, etc.).

Do **not** open TEST.

Scientifically acceptable uses of this round (outside novelty implementation):

- Keep Program A/B frozen.
- Treat **87.18%** as population-specific and document the title_roman confound in thesis/limitations when writing.
- If publication is pursued later, position as **empirical / evaluation** contribution (not a new Roman Urdu retrieval architecture), subject to a separate writing authorization.

---

## Congratulations clause

**Not applicable.** No defensible new research mechanism survived the novelty and feasibility gates.
