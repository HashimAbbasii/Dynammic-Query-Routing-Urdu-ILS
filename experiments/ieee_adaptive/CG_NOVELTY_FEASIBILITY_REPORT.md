# Candidate-Generation Novelty & Feasibility Gate

**Date:** 2026-09-22  
**Branch:** `research/roman-urdu-adaptive-retrieval`  
**HEAD:** `3b2e829bf9769d16f9b604ee68d7cc50ce128fa7`  
**Gate type:** Literature + TRAIN/DEV empirical alignment — **no method implementation**  
**Final decision:** **NO-GO**

`TEST_CONTENT_ACCESSED = FALSE`

---

## 1. Executive Summary

The Failure Decomposition established that **31/80** Roman KN TRAIN+DEV queries have ExactSource gold outside BM25 ∪ NG3 ∪ Dense Top-50, and that **18/31** of those are labeled non-institutional **entity/name**. This gate asked whether those 18 reveal a **specific, under-addressed** Roman Urdu → Urdu first-stage mechanism suitable for an IEEE journal method contribution.

**They do not.**

Query-surface subtyping of the 18 shows **heterogeneity**, not one mechanism: product/platform brands (**6**), sports team/event (**5**), person / person+film (**5**), geo/market (**1**), film title (**1**). Closest literature already occupies each subclass: **JRC-Names-Retrieval (LREC-COLING 2024)** for cross-script names; **BLINK / MuVER / GENRE** for entity candidate generation; **Gupta SIGIR 2014** and **FIRE / TALLIP** for mixed-script / transliterated IR; **Chari SIGIR 2025** for neural script-gap repair; **Butt et al. 2025** for Roman Urdu IR datasets/baselines. In-repo **Phase 9 Wikipedia title CG** already probed entity-resource injection on this setting and recovered only **1/18** B-class cases at Hit@50.

Institutional alias (C2a) and adaptive routing (C1) remain closed and were not revived. “Urdu is low-resource” is rejected as novelty. No of ≤3 candidate mechanisms earns GO or CONDITIONAL GO under the gate’s strict rejection criteria.

**Decision: NO-GO. STOP.**

---

## 2. Current Empirical Evidence

Population: Roman KN ExactSource TRAIN+DEV **n=80** (train 52 / dev 28).  
Sources: Phase 13 scoring; Failure Decomposition; C2A labels (unchanged).

| Metric | Value |
| --- | ---: |
| Dense Hit@5 | **20/80 = 25%** |
| Hybrid Hit@50 | **40/80 = 50%** |
| BND Top-50 coverage | **49/80 = 61.25%** |
| Perfect-ranking BND ceiling | **49/80 = 61.25%** |
| Candidate-generation failures | **31/80 = 38.8%** |
| Entity/name among CG failures | **18/31 = 58.1%** (**18/80 = 22.5%**) |
| Oracle best-of-3 Hit@5 | **28/80** |

**Statistical caution:** n=18 is a **small residual slice** of a small known-item set. Prevalence claims are TRAIN/DEV only; no TEST evidence; sampling uncertainty is high. Do not treat 18 as a large population.

Prompt coverage claims were previously verified against Phase 13/14; this gate does not recompute retrieval.

---

## 3. Research Problem Definition

**Candidate problem (under test):**

> Roman Urdu known-item queries whose primary residual failure is entity/name surface mismatch fail to place ExactSource Urdu-script news documents into the BM25 ∪ NG3 ∪ Dense Top-50 pool; is there a technically distinct first-stage mechanism—beyond generic EL, alias tables, transliteration, dense IR, or domain transfer—that is insufficiently addressed in literature and prevalent enough in this evidence to justify an IEEE journal method?

**What this is not:** ranking improvement; 80% metric chasing; revival of C1/C2a; “apply X to Urdu.”

---

## 4. Literature Review

Search date: 2026-09-22. Engines: Cursor WebSearch over ACL Anthology, ACM/SIGIR, arXiv HTML, FIRE/CEUR, JRC pages. Emphasis 2021–2026 with foundational 2011–2014 where needed.

### 4.1 Roman Urdu IR

| Work | Year | Venue | Finding |
| --- | --- | --- | --- |
| Butt, Varanasi, Neumann — *Roman Urdu as a Low-Resource Language: Building the First IR Dataset and Baseline* | 2025 | LowResNLP | First large RU IR dataset (MS MARCO multi-hop) + multilingual retrieval baseline |
| Butt et al. — *Low-Resource Transliteration for Roman-Urdu and Urdu* | 2025 | LoResMT | Strong RU↔Urdu transformer transliteration |
| Basit et al. — hybrid CLIR with Urdu/English/Roman-Urdu queries | 2023 | JCBI | Hybrid query-mode CLIR (not entity-CG novelty) |

**Implication:** Dedicated RU IR + transliteration threads **already exist (2025)**. Applying them to this news ExactSource set is **domain transfer**, not a new mechanism.

### 4.2 Cross-script / mixed-script / transliteration IR

| Work | Year | Venue | Finding |
| --- | --- | --- | --- |
| Gupta et al. — *Query expansion for mixed-script IR* | 2014 | SIGIR | Formal MSIR; joint cross-script embeddings + QE |
| FIRE Transliterated Search / MSIR tracks | 2013–2015 | FIRE | Shared tasks for Indic mixed-script retrieval |
| Prabhakar et al. — *Query Expansion for Transliterated Text Retrieval* | 2021 | ACM TALLIP | Phonetic QE (Hindex) for transliterated search |
| Chari, Ounis, MacAvaney — *Lost in Transliteration* | 2025 | SIGIR | Neural “script gap”; **transliterate-train** on Zh/Ru |

**Implication:** Script-gap and mixed-script first-stage matching are **mature**. Urdu/RU application of transliterate-train is explicitly anticipated by Chari’s framing.

### 4.3 Entity / name retrieval

| Work | Year | Venue | Finding |
| --- | --- | --- | --- |
| Steinberger et al. — JRC-Names | 2011+ | JRC resource | Multilingual person/org name variants across scripts (incl. Arabic) |
| Blair & Bar — *JRC-Names-Retrieval* | 2024 | LREC-COLING | Standardized **cross-script name search** benchmark; ByT5 gains |
| Gillick et al. — dense entity retrieval | 2019 | arXiv/EMNLP lineage | Dual-encoder entity candidate generation |
| Wu et al. — BLINK | 2020 | EMNLP | Dense zero-shot entity linking CG + ranking |
| Ma et al. — MuVER | 2021 | EMNLP | Multi-view **first-stage entity retrieval** |
| De Cao et al. — GENRE | 2021 | ICLR lineage | Autoregressive entity retrieval |

**Implication:** Cross-script **name** retrieval and **entity candidate generation** are active, well-instrumented research areas—not open methodological voids.

### 4.4 Candidate generation / first-stage IR

Entity CG is standard two-stage EL (alias table or dense nomination → ranker). Document first-stage CG for IR (sparse/dense/hybrid) is Program B’s frozen stack. Phase 9 already tested Wikipedia-title entity-resource CG on **this** Roman→Urdu news setting.

### 4.5 In-repo prior probes (not literature, but decisive overlap)

| Probe | Result on entity-like misses |
| --- | --- |
| Phase 9 WP titles | Among 18 B-class: **only KN051** Hit@50; 17/18 still miss |
| Phase 7 letter-name | Institutional/acronym path; UNSUPPORTED |
| Phase 11 | Deep Dense ranks on VOCAB dual-misses; no frozen CG path |
| C2a | Institutional descriptive alias **6/31** — closed |
| C1 | Query-only expert routing — closed |

---

## 5. Closest Prior Work (by candidate direction)

See `CG_NOVELTY_MATRIX.csv` for the full matrix. Headline closest works:

1. **Blair & Bar 2024** — cross-script name search  
2. **BLINK / MuVER / GENRE** — entity first-stage CG  
3. **Chari et al. 2025** — neural script-gap / transliterate-train  
4. **Gupta 2014 + TALLIP 2021** — mixed-script / transliterated QE  
5. **Butt et al. 2025** — Roman Urdu IR + transliteration  
6. **ULTRA Phase 9** — WP alias CG on this exact problem setting  

---

## 6. Novelty Gap Analysis

### What is already solved?

- Cross-script person/organization **name retrieval** as a distinct task (JRC-Names-Retrieval).  
- Entity **candidate generation** via aliases and dense/generative retrievers.  
- Mixed-script / transliterated **query expansion**.  
- Neural **script-gap** adaptation (transliterate-train).  
- Roman Urdu **IR datasets and transliteration models** (2025).  
- In-domain **Wikipedia title expansion** (Phase 9) — empirical negative for broad entity-resource CG.

### What remains unresolved?

Practical performance on **this** small news ExactSource set remains imperfect. That is an **engineering / resource / evaluation** residual, not evidence of a missing methodological formulation.

No surviving statement of the form:

> Existing work does X, but under condition Y it cannot address Z  

held for a **Z** that is (a) coherent in our 18, (b) prevalent enough, and (c) not reducible to domain transfer of X.

---

## 7. Empirical Alignment with the 31 / 18

### 7.1 Are the 18 one coherent mechanism?

**No.** Pre-declared query-surface subtypes (no gold document text; C2A query text already in TRAIN/DEV annotations):

| Subtype | n | Example IDs |
| --- | ---: | --- |
| PRODUCT_PLATFORM | 6 | KN044, KN051, KN102, KN113, KN118, KN037 |
| SPORTS_TEAM_EVENT | 5 | KN002, KN006, KN024, KN095, KN111 |
| PERSON / PERSON_FILM / PERSON_EVENT | 5 | KN022, KN032, KN054, KN026, KN008 |
| FILM_MEDIA | 1 | KN021 |
| GEO_MARKET | 1 | KN005 |

**C2A label B (“non-institutional entity”) is a residual bucket**, not a single linguistic failure mode.

### 7.2 Mechanism guesses within B (qualitative; query-side)

| Issue | Approx. share of 18 | Notes |
| --- | --- | --- |
| English brand/team/person string present but still BND miss50 | Large | Often not “missing transliteration” alone; Dense also fails → deeper mismatch or doc framing |
| Underspecified entity (“teen tennis sensation”, “nayi photo app”) | ≥2 | Closer to **query ambiguity / semantic** (category D) than alias CG |
| Classic cross-script person name | Few (e.g. Umar Akmal, Kangana) | Directly in JRC-Names problem class |
| Film/title entertainment | Few | Title/entity alias class |

### 7.3 Detectability

- **Query alone:** coarse subtype (person vs brand vs sports) is often surface-detectable; **which generator would recover ExactSource** is not (C1 already failed for expert routing; Phase 9 trigger recovered little of B).  
- **After candidates:** gold absence means diagnosis needs gold or oracle docs — **must not** drive method design from gold-informed rules.

### 7.4 A/B/C/D classification of the 18

All 18 are **B: candidate-generation failures** w.r.t. BND Top-50 by definition.  
Within that, a non-trivial subset also looks like **D: semantic/benchmark / underspecification** rather than fixable alias bridges.  
They are **not** ranking failures (C). Representation failure (A) may contribute but is not a separable novel mechanism here.

### 7.5 Other 13 of the 31

| Label | n | Status for this gate |
| --- | ---: | --- |
| A institutional | 6 | **Closed C2a** — do not revive |
| D orthographic/script | 3 | Covered by MSIR / script-gap lit + Method D/NG3 attempts |
| C paraphrase | 2 | Generic CLIR semantic |
| E vocab | 1 | Generic |
| G other | 1 | No coherent target |

Secondary question (“another coherent CG mechanism in the heterogeneous 31?”): **No** survivor that is both novel and prevalent.

---

## 8. Candidate Research Directions (max 3)

### CG-H1 — Unified Roman Urdu entity/name first-stage CG (WP/Wikidata/EL)

| Field | Content |
| --- | --- |
| Problem | Bridge Latin entity mentions in RU queries to Urdu news via alias/EL CG |
| Why insufficient claim fails | JRC-Names-Retrieval + BLINK/MuVER/GENRE + Phase 9 already cover the class; Phase 9 recovered 1/18 |
| Closest prior | Blair & Bar 2024; BLINK; Phase 9 |
| Exact technical difference | None beyond domain/resource scaling |
| Targets | Heterogeneous B=18 |
| Expected CG benefit | Uncertain; prior probe weak |
| Resources | WP/Wikidata; EL models |
| TRAIN/DEV feasibility | Yes, but prior evidence discourages |
| Rediscovery risk | **Very high** |
| IEEE novelty potential | **Low** (application) |
| Verdict | **NO-GO** |

### CG-H2 — Person-name-only cross-script CG

| Field | Content |
| --- | --- |
| Problem | Restrict to person-name subset |
| Why insufficient claim fails | Exactly JRC-Names task; n≈3–5 too small for journal method |
| Closest prior | JRC-Names-Retrieval |
| Verdict | **NO-GO** |

### CG-H3 — Transliterate-train multilingual dense on Urdu news

| Field | Content |
| --- | --- |
| Problem | Close script gap with Chari-style fine-tuning |
| Why insufficient claim fails | Direct domain transfer of SIGIR 2025 method; combination with existing Dense |
| Closest prior | Chari et al. 2025; Butt transliteration 2025 |
| Verdict | **NO-GO** |

No direction reaches **GO TO FEASIBILITY PROBE** or **CONDITIONAL**.

---

## 9. Feasibility Analysis

**Not performed for method implementation** — no surviving gap.  

Brief counterfactual: even if entity CG recovered all 18, BND coverage would rise 49→67 (if all newly unique), still a **metric** win that would remain **methodologically** an application of known entity/name IR unless a distinct mechanism were shown—which it was not. Prevalence and coherence fail before feasibility.

---

## 10. IEEE Journal-Level Assessment

| Dimension | Assessment |
| --- | --- |
| Methodological novelty | **Insufficient** — collapses to known entity/name/script-gap classes |
| Technical depth | Application/engineering depth only |
| Empirical testability | Testable, but that ≠ novel |
| Reproducibility | Would be reproducible as an application study |
| Generalizability | Entity IR already claims multilingual generality |
| Likely contribution type | Domain-transfer / systems evaluation — **not** a new first-stage mechanism paper |

---

## 11. Decision

### **NO-GO**

No sufficiently novel and defensible methodological gap survives among the 18 entity/name CG failures or the broader heterogeneous 31.

---

## 12. Recommended Next Step

**STOP.**

Do not implement entity linkers, Wikidata expanders, person-name dictionaries, transliterate-train, or multi-mechanism CG controllers under a claim of novelty from this gate.

Reassess thesis/publication strategy around **honest Program B empirical ceilings** (Dense Hit@5 25%; Hybrid Hit@50 50%; BND perfect-ranking ≤61.25%) rather than a new CG method narrative.

---

## Appendix A — Repository / TEST / Program integrity

| Check | Status |
| --- | --- |
| Branch | `research/roman-urdu-adaptive-retrieval` |
| HEAD | `3b2e829bf9769d16f9b604ee68d7cc50ce128fa7` |
| Working tree | Untracked `experiments/ieee_adaptive/` only |
| Program A modified | **No** |
| Program B modified | **No** |
| Phase 13/14 modified | **No** |
| TEST query contents accessed | **No** |
| Failure Decomposition CSVs modified | **No** (read-only) |

## Appendix B — Artifacts

| File | Role |
| --- | --- |
| `experiments/ieee_adaptive/CG_NOVELTY_MATRIX.csv` | Novelty matrix |
| `experiments/ieee_adaptive/CG_NOVELTY_FEASIBILITY_REPORT.md` | This report |

## Appendix C — Search queries used (representative)

1. `Roman Urdu information retrieval cross-script transliteration SIGIR ACL 2020..2026`  
2. `JRC-Names retrieval LREC 2024 multilingual person name cross-script IR`  
3. `"entity linking" retrieval candidate generation first stage SIGIR EMNLP`  
4. `mixed-script IR Hindi FIRE Gupta Patil query expansion transliterated text TALLIP`  
5. `Chari Lost in Transliteration SIGIR 2025 transliterate-train Roman Urdu Butt LowResNLP`  
6. `entity-aware dense retrieval MuVER BLINK GENRE`  

---

**End of CG Novelty & Feasibility Gate.**
