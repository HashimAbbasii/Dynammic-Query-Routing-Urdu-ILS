# Architecture Redesign + 80% Feasibility Gate

**Date:** 2026-09-22  
**Branch:** `research/roman-urdu-adaptive-retrieval`  
**HEAD:** `3b2e829bf9769d16f9b604ee68d7cc50ce128fa7`  
**Nature:** Architecture research gate — **no method implementation**  
**Final decision:** **NO-GO**

`TEST accessed: NO`

---

## 1. Executive Summary

Program B’s frozen first-stage stack (Method-D BM25 + NG3 + multilingual e5 Dense + Hybrid RRF, plus closed probes for NORM, letter-name, WP titles, 3-way RRF, cascade, routing, institutional alias, and entity/name CG) has a TRAIN+DEV ExactSource Top-50 union ceiling of **49/80 = 61.25%**. That makes **80% Hit@5 (64/80) structurally impossible** under the *current* candidate architecture.

This gate asked whether a **fundamentally redesigned** architecture could raise that ceiling through a **technically distinct, under-addressed** mechanism suitable for IEEE journal contribution—not whether importing ColBERT/SPLADE/Doc2Query would likely help metrics.

**Answer: No such under-addressed architectural mechanism survives.**

What is absent from the ULTRA stack (late interaction, learned sparse expansion, Doc2Query-style document views, transliterate-train) is **present and mature in 2019–2025 IR literature**. Applying those families to Roman Urdu → Urdu news is **domain transfer / combination**, not a new research architecture. Deeper inspection of the **31** CG failures shows **heterogeneous** structural tags (brands, sports, persons, institutional aliases, script-of-same-EN, underspecification, macro paraphrase)—not one coherent missing representation that literature fails to formulate.

**Decision: NO-GO.**  
**Next step: STOP — do not implement another architecture within this research line.**

---

## 2. Current Architecture Autopsy

Full detail: `experiments/ieee_adaptive/ARCHITECTURE_AUTOPSY.md`.

**Present:** lexical Method-D BM25 (doc-side romanization), NG3, e5-small dense, Hybrid RRF, plus exhausted probes (NORM, Phase 7 letter-name, Phase 9 WP titles, Phase 8/10 fusion/cascade, C1 routing, C2a institutional alias).

**Solves:** thin lexical hits; some char-overlap; some semantic bridges; complementary pools up to 49/80.

**Cannot solve:** 31/80 golds outside BND Top-50; 80% Hit@5 under current pool; always-on fusion as ceiling-raiser.

**Absent but literarily mature:** ColBERT-class late interaction; SPLADE-class learned sparse; Doc2Query / multi-view docs; Chari-style transliterate-train.

---

## 3. Current 49/80 Candidate Ceiling

| Quantity | Value |
| --- | ---: |
| BM25 ∪ NG3 ∪ Dense Hit@50 | **49/80 = 61.25%** |
| Perfect-ranking Hit@5 upper bound (same pool) | **49/80** |
| Dense Hit@5 | 20/80 |
| Hybrid Hit@50 | 40/80 |
| Oracle best-of-3 Hit@5 | 28/80 |
| Target 80% Hit@5 | **64/80** |
| Gap: 64 − 49 | **+15 unique golds minimum** |

Math fact (unchanged): **64 > 49 ⇒ ranking alone cannot reach 80%.**

---

## 4. 31 Candidate-Generation Failures

From frozen Failure Decomposition (unchanged files):

| Secondary mechanism | n |
| --- | ---: |
| entity_name | 18 |
| acronym_institution | 6 |
| orthographic_variation | 3 |
| semantic_paraphrase | 2 |
| lexical_mismatch | 1 |
| other | 1 |

Prior CG novelty gate: the 18 entity/name cases are **heterogeneous** and literature-covered → **NO-GO**. This gate does **not** rebuild an entity system.

---

## 5. Deeper Failure Structure

Additional query-side structural tags on the 31 (TRAIN/DEV C2A query text only; multi-label allowed; uncertain allowed):

| Structural tag | Approx. n (multi-label) |
| --- | ---: |
| INST_OR_ACRONYM_SURFACE | 10 |
| EN_BRAND_PRODUCT | 6 |
| SPORTS_EVENT | 6 |
| DESCRIPTIVE_URDU_ALIAS | 6 |
| SCRIPT_ORTHO_SAME_EN | 5 |
| PERSON_NAME_LATIN | 4 |
| MACRO_SEMANTIC_PARAPHRASE | 4 |
| UNDERSPECIFIED_OR_IMPLICIT | 3 |
| ENTERTAINMENT_TITLE | 2 |
| UNCERTAIN_MIXED | 1 |

**Interpretation:** Failures span **institutional alias** (C2a-closed), **script-of-same-English-name**, **brands**, **sports events**, **persons**, **macro paraphrase**, and **underspecified** queries. There is **no single missing architecture** that cleanly explains the majority with a new mechanism. Underspecified cases lean toward **semantic/benchmark limitation**, not a new first-stage family.

---

## 6. Architecture Families Investigated

| Family | Explored? |
| --- | --- |
| A. Multi-stage candidate generation beyond BM25+Dense+RRF | Yes |
| B. Query–document semantic bridge generation | Yes |
| C. Intermediate representation (non-trivial vs translit/dense) | Yes |
| D. Knowledge-grounded CG | Yes (closed / Phase 9) |
| E. Document-side multi-representation | Yes (Doc2Query / multi-view) |
| F. Cross-lingual lexical–semantic bridge | Yes (e5 + Chari + Butt) |
| G. Late interaction / token-level | Yes (ColBERT family) |
| H. Retrieval + structured intermediate reasoning | Yes (rejected as generic agentic) |
| Learned sparse expansion | Yes (SPLADE family) |

---

## 7. Literature Findings (architecture-focused, 2018–2026)

| Family | Anchor works | Status vs “under-addressed” |
| --- | --- | --- |
| Late interaction | ColBERT (SIGIR 2020); ColBERTv2; PLAID; WARP (SIGIR 2025); ColBERT-X / Translate-Distill; Jina-ColBERT-v2 (2024); mLateOn | **Mature, multilingual CLIR-capable** |
| Learned sparse | SPLADE (SIGIR 2021); SPLADE++; Formal et al. TOIS sparse neural IR | **Mature first-stage class** |
| Doc expansion / multi-view | Doc2Query (2019); Doc2Query--; dual-index Doc2Query++ (2025); multi-view dense docs | **Mature** |
| Script gap | Chari et al. SIGIR 2025 transliterate-train | **Defines the neural script-gap architecture** |
| RU IR / translit | Butt et al. 2025 LowResNLP + LoResMT | **Occupies RU IR/translit tooling** |
| Entity/KB CG | BLINK; GENRE; JRC-Names-Retrieval; Phase 9 | **Closed for novelty on this evidence** |
| Adaptive / agentic | Adaptive-RAG; SoKs | **Crowded; C1 closed** |

**Central question answer:**  
What type of representation/interaction is absent from BM25+NG3+global dense?  
→ **Late interaction, learned sparse expansion, and document-side predicted-query views.**  
Are those scientifically unresolved?  
→ **No.** They are established architecture families. Absence in Program B ≠ research gap.

---

## 8. Novelty Matrix Summary

File: `experiments/ieee_adaptive/ARCHITECTURE_NOVELTY_MATRIX.csv`

| Verdict | Count |
| --- | ---: |
| DOMAIN TRANSFER | 4 |
| COMBINATION ONLY | 2 |
| TOO CLOSE TO CLOSED DIRECTION | 2 |
| ALREADY SOLVED | 1 |
| TOO GENERIC | 2 |
| POTENTIAL / STRONG POTENTIAL | **0** |

---

## 9. Candidate Architectures (max 5)

### ARC-1 — Multilingual late interaction (ColBERT-X / Jina-ColBERT-v2 class) on Urdu news

| Field | Content |
| --- | --- |
| Input | Roman query; Urdu (or dual-script) documents |
| Intermediate | Per-token contextual vectors; MaxSim |
| CG | Token-level matches may retrieve docs global pooling misses |
| Why existing fail | Single-vector e5 may bury entity/token alignments |
| Why lit already solves | ColBERT family + multilingual ColBERT-X / Jina-ColBERT-v2 / mLateOn |
| Verdict | **DOMAIN TRANSFER → reject** |

### ARC-2 — Doc2Query / multi-view document-side Roman bridges

| Field | Content |
| --- | --- |
| Input | Urdu docs → generated RU/EN queries appended or dual-indexed |
| Intermediate | Predicted query strings / multi-view embeddings |
| CG | RU query matches doc-side predicted Roman forms |
| Why lit already solves | Doc2Query lineage 2019–2025 |
| Verdict | **DOMAIN TRANSFER → reject** |

### ARC-3 — SPLADE-style learned sparse expansion

| Field | Content |
| --- | --- |
| Intermediate | Sparse WordPiece expansion weights |
| CG | Learned expansion terms enter inverted index |
| Why lit already solves | SPLADE / sparse neural IR TOIS |
| Verdict | **DOMAIN TRANSFER → reject** |

### ARC-4 — Transliterate-train fine-tuning of dense or late-interaction models

| Field | Content |
| --- | --- |
| Intermediate | Shared encoder exposed to romanized + native queries |
| Why lit already solves | Chari SIGIR 2025 |
| Verdict | **DOMAIN TRANSFER → reject** |

### ARC-5 — Multi-retriever megafusion (add ColBERT+SPLADE+Doc2Query to BND)

| Field | Content |
| --- | --- |
| Mechanism | Larger union via known components |
| Why reject | Explicit **combination-only**; Phase 8 showed naive fusion can hurt ranking |
| Verdict | **COMBINATION ONLY → reject** |

No candidate reaches POTENTIAL / STRONG POTENTIAL.

---

## 10. Technical Difference from Existing Work

For every ARCH above, the methodological difference from published work reduces to:

> **Apply architecture family F to Urdu news / Roman Urdu queries.**

That is **not** a new technical mechanism under this gate’s novelty rule.

---

## 11. Expected Candidate-Coverage Mechanism

| Architecture | How it *might* raise coverage (engineering conjecture) | Novel? |
| --- | --- | --- |
| Late interaction | Fine-grained token matches | No |
| Doc2Query | Doc-side RU surfaces | No |
| SPLADE | Learned expansion terms | No |
| Transliterate-train | Better script robustness | No |
| Megafusion | More generators in union | No |

No claim is made that any would recover +15 unique golds; that would require implementation, which this gate forbids without GO.

---

## 12. 80% Structural Feasibility

### Shared math

| Item | Value |
| --- | ---: |
| Current BND coverage | 49/80 |
| Target Hit@5 | 64/80 |
| **Minimum theoretical new unique golds in Top-50** | **≥15** |
| Realistic coverage for imperfect ranking (illustrative) | **≳70/80** (would require recovering most of the 31 CG misses **and** strong ranking) |

### Per candidate (theoretical only)

| Candidate | Could coverage *in principle* exceed 49? | Enough for structural 64 path? | Novel enough to research? |
| --- | --- | --- | --- |
| ARC-1 late interaction | Possibly (unknown without run) | Unknown; needs ≫15 uniques | **No** |
| ARC-2 Doc2Query | Possibly | Unknown | **No** |
| ARC-3 SPLADE | Possibly | Unknown | **No** |
| ARC-4 transliterate-train | Possibly | Unknown | **No** |
| ARC-5 megafusion | Possibly by construction | Still combination | **No** |

**Important:** Metric possibility ≠ scientific GO. Even if ColBERT recovered 20 of 31 misses tomorrow, the contribution would remain **application of a known architecture** unless a new mechanism were identified—which it was not.

**80% stress-test conclusion:** Redesigning by importing mature families *might* change the ceiling empirically; it does **not** create a defensible IEEE journal *architectural novelty* claim on this evidence. This gate therefore does **not** authorize an 80%-chasing implementation.

---

## 13. Minimal Feasibility Experiment

**Not designed for execution** — no surviving novel architecture.

(If this were only an engineering bake-off, a probe would measure unique Top-50 golds vs 49/80 for an off-the-shelf multilingual ColBERT—**explicitly out of scope** as a novelty-authorized next step.)

---

## 14. IEEE Journal Contribution Assessment

| Dimension | Assessment |
| --- | --- |
| Methodological novelty | **Insufficient** — redesign options = known families |
| Technical depth | High *if* building ColBERT-X from scratch, but depth is borrowed |
| Empirical significance | Coverage ceiling diagnosis is already established; importing F is evaluation |
| Reproducibility | Application studies would be reproducible |
| Generalization | ColBERT/SPLADE/Doc2Query already claim general IR generality |
| Relation to literature | Application / systems evaluation, not new architecture theory |

A strong journal paper could still be an **honest empirical Program B systems paper** (ceilings, failures, negative results)—that is **outside** this gate’s “new architecture” objective and was previously marked out-of-scope for novelty discovery.

---

## 15. Final Decision

### **NO-GO**

No fundamentally distinct, under-addressed retrieval architecture survives literature separation while targeting a coherent subset of the 31 CG failures.

---

## 16. One Next Step

**STOP — do not implement another architecture within this research line.**

Reassess thesis/publication strategy around frozen Program B evidence and measured ceilings (Dense Hit@5 25%; Hybrid Hit@50 50%; BND perfect-ranking ≤61.25%), not a new first-stage redesign narrative.

---

## Integrity

| Check | Status |
| --- | --- |
| TEST accessed | **NO** |
| Program A modified | **NO** |
| Program B modified | **NO** |
| Phase 13/14 modified | **NO** |
| Failure Decomposition CSVs modified | **NO** (read-only) |
| Method implemented | **NO** |

## Artifacts

| File | Role |
| --- | --- |
| `ARCHITECTURE_AUTOPSY.md` | Current stack autopsy |
| `ARCHITECTURE_NOVELTY_MATRIX.csv` | Architecture novelty matrix |
| `ARCHITECTURE_REDESIGN_FEASIBILITY_REPORT.md` | This report |

---

**End of Architecture Redesign + 80% Feasibility Gate.**
