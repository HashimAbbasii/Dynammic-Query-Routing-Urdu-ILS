# ULTRA Publication + Thesis Positioning Audit

**Date:** 2026-09-22  
**Branch:** `research/roman-urdu-adaptive-retrieval`  
**HEAD:** `3b2e829bf9769d16f9b604ee68d7cc50ce128fa7`  
**Mode:** Publication/thesis strategy only — no new methods, no TEST access, no Program A/B modification  

`TEST accessed: NO`

---

## 1. Executive Summary

Program A is a **frozen empirical / script-aware lexical IR system study** with an honest contribution statement already in the manuscript (“methodological novelty is modest”). It is the strongest near-term publication candidate (PLOS ONE packaging exists; printed title correctly drops “adaptive routing”).

Program B is a **frozen Roman Urdu known-item empirical comparison and failure-diagnostic program**. Best Hit@5 is Dense **20/80 (25%)**; Hybrid Hit@50 **40/80**; BND candidate ceiling **49/80**. It does **not** contain a novel retrieval algorithm. Its value is controlled negative/partial results, complementarity evidence, and a measured candidate-generation bottleneck.

The adaptive-routing / IEEE novelty chain (C1, C2a, C3, CG novelty, architecture redesign, fresh IEEE discovery) is **CLOSED with NO-GO**. There is **no defensible IEEE-level methodological novelty** remaining inside the current Roman Urdu → Urdu first-stage line that survives those gates.

**Recommended strategic posture (not a “winner” ranking):**

- **Publish / finish Program A** as an empirical script-aware BM25 study.  
- Treat **Program B primarily as thesis chapters** (empirical strengthening + diagnostic ceilings), optionally a separate empirical paper later if workload allows.  
- **Do not** continue inventing methods inside this line to chase 80% or IEEE algorithmic novelty.  
- Reframe the **MS thesis title/contribution** away from a successful adaptive router toward an empirical investigation of script-aware and multi-representation Roman Urdu retrieval, including informative negative results.  
- Any future IEEE methodological line must be a **genuinely separate research question** with a new novelty gate—not a revival of closed CG/architecture directions.

---

## 2. Repository Safety Verification

| Check | Result |
| --- | --- |
| Branch | `research/roman-urdu-adaptive-retrieval` |
| HEAD | `3b2e829bf9769d16f9b604ee68d7cc50ce128fa7` |
| Working tree | Untracked `experiments/ieee_adaptive/` only |
| Program A modified | **No** |
| Program B modified | **No** |
| TEST contents accessed | **No** |
| Unexpected modifications | **None** — proceed |

**Manuscript path note:** Prompt references `experiments/ultra_v2/paper/PLOS_ONE_V2_DRAFT.tex`. On this working tree that `.tex` is **currently missing** (paper folder holds logs/template only; not present in `git ls-files` on this branch). Program B scientific claims are audited from **`PHASE14_FINAL_REPORT.md`** (frozen SoT). Manuscript completeness for Program B is **LIMITED** until the draft is restored/located.

---

## 3. Program A Audit

### Positioning (evidence-based)

**Primary description: C — script-aware retrieval study** with strong **B — empirical IR system** character.

Not A (novel algorithm). Manuscript itself states novelty is modest and contribution is empirical (hashed freeze; separate known-item vs usefulness; Roman Urdu limitation).

### Official metrics (do not average)

| Population | Metric | Value |
| --- | --- | --- |
| Dev/val KN n=78 | ExactSource Hit@5 | 68/78 = 87.18% |
| Sealed K n=40 | ExactSource Hit@5 | 27/40 = 67.50% |
| Sealed U n=40 | Human Success@5 (A1) | 23/40 = 57.50% |

### Contribution strengths

| Dimension | Rating |
| --- | --- |
| Research question clarity | **STRONG** (RQ1–RQ4 script-aware lexical freeze) |
| Methodological novelty | **LIMITED** (detector + BM25 index selection) |
| Empirical contribution | **STRONG** (freeze protocol; sealed K/U; script-split Roman weakness) |
| Dataset/benchmark | **MODERATE** (protocol + seals; corpus third-party provenance caveats) |
| Engineering | **MODERATE** (reproducible M0) |
| Publication readiness | **MODERATE–STRONG** for PLOS-style empirical paper (packaging audited) |
| Reproducibility | **MODERATE** (SHA-256 freeze; DAS caveats on redistribution) |

### Strongest scientific story

A deterministic script-aware BM25 pipeline can recover known Urdu news articles under a hashed freeze, but **ordinary Roman Urdu remains a documented failure mode**—and known-item scores must not be confused with human usefulness.

### Weakest points / likely reviewer criticism

- Modest methodological novelty vs MSIR / Roman IR literature.  
- Single news corpus; title-derived KN construction.  
- Roman Hit@5 on K is weak (1/12 Roman in sealed K narrative).  
- Filename still says “Adaptive_dynamic_query_routing…” while printed title does not—packaging hygiene.  
- No claim of IEEE acceptance/DOI found in-repo; **do not claim published IEEE** without external confirmation.

### Improvements (minimum)

| Item | Priority |
| --- | --- |
| Keep printed title / abstract aligned with empirical claims | MUST DO |
| Data availability / corpus provenance clarity | MUST DO |
| Confidence intervals already present style — preserve | SHOULD DO |
| External CURE/Urdu MS MARCO comparison | DO NOT DO as forced SOTA claim; OPTIONAL only as non-comparable discussion |
| Combine with Program B into one paper | See §9 — not required for Program A |

### Standalone?

**Yes.** Program A should remain standalone. Program B is a later branch with different population (Roman KN n=80 TRAIN+DEV) and must not rewrite Program A tables.

---

## 4. Program B Audit

### Source of truth

`experiments/ultra_v2/PHASE14_FINAL_REPORT.md` (frozen).  
Draft manuscript path currently **unavailable** on this tree → paper-completeness rating reduced.

### Strongest defensible story

**Empirical comparison + failure analysis / diagnostic study** of Roman Urdu → Urdu-script known-item retrieval under multiple first-stage families—not a new method.

### What experiments demonstrate

- Method-D collapses on naturalistic Roman KN (5/80 Hit@5).  
- Dense e5-small is best Hit@5 (20/80).  
- Hybrid is best deployable Hit@50 (40/80).  
- Many interventions fail or partially fail under prereg stop rules (R2-1, Phase 7, 8, 10, 11, 12 skip).  
- BND union Top-50 = 49/80 ⇒ perfect ranking of that pool cannot reach 64/80.  
- Oracle best-of-3 Hit@5 = 28/80 > Hybrid Hit@5, but C1 showed query-only routing cannot exploit it.

### Overclaims to avoid

- “We propose a novel hybrid/dense/adaptive architecture.”  
- “We solve Roman Urdu retrieval.”  
- “80% is impossible for all architectures” (only for the **investigated candidate pools**).  
- Averaging Program A and Program B metrics.  
- Treating Phase 13 LLM-drafted queries without disclosure.

### Contribution ratings

| Dimension | Rating |
| --- | --- |
| RQ clarity | **MODERATE** (strengthening Roman KN; multi-phase controlled tests) |
| Methodological novelty | **NOT ESTABLISHED** |
| Empirical contribution | **STRONG** (controlled negatives + ceilings) |
| Diagnostic contribution | **STRONG** (MISS vs RANK; CG ceiling) |
| Dataset/benchmark | **MODERATE** (n=80 TRAIN+DEV; TEST sealed unused) |
| Paper completeness | **LIMITED** (draft `.tex` missing on this tree) |
| Publication readiness | **LIMITED–MODERATE** as empirical/diagnostic paper after manuscript rebuild |

---

## 5. Closed Research-Line Summary

| Gate | Decision | Why closed |
| --- | --- | --- |
| C1 detectability | NO-GO | Query-only features cannot predict winning expert; routed < fixed Dense |
| C2 / C2a institutional alias | NO-GO | Confirmed prevalence 6/31 < threshold 8 |
| C3 residue novelty | NO-GO | Residues covered by literature / too weak for journal method |
| Fresh IEEE discovery | NO-GO | Broad AI/IR search: no survivor |
| Failure decomposition | Diagnostic | CG dominates; ceiling 49/80; **not** a novelty GO |
| CG entity/name novelty | NO-GO | 18 entity cases heterogeneous; JRC-Names/EL/Phase 9 occupy class |
| Architecture redesign | NO-GO | Absent families (ColBERT/SPLADE/Doc2Query) are mature domain-transfer, not new mechanisms |

**Do not revive** these under new names.

---

## 6. Literature Positioning

Journals/conferences publish in this space as:

| Type | Examples (representative) |
| --- | --- |
| Method | Chari SIGIR 2025 script gap; Gupta SIGIR 2014 MSIR; OPTICAL WSDM 2023 CLIR distillation |
| Dataset/benchmark | MIRACL; Butt 2025 Roman Urdu IR dataset; JRC-Names-Retrieval LREC 2024 |
| Empirical / backbone study | Dense retrieval in African languages (SIGIR); multilingual training regimes (ACM TOIS) |
| Diagnostic / robustness | Script-gap degradation analyses; transliteration robustness studies |
| System / applied | PLOS ONE-style empirical system freezes; IEEE Access applied/negative-result-friendly scope |

**Implication:** Program A/B fit **empirical / diagnostic / system** venues better than **algorithmic novelty** IEEE Transactions expectations—unless substantially strengthened beyond current methods.

---

## 7. Journal Landscape

### Program A

| Class | Venue (examples) | Fit notes |
| --- | --- | --- |
| Realistic | **PLOS ONE** | Already packaged; empirical scope; OA APC |
| Realistic | **Information Processing & Management** / similar empirical IR journals | Needs stronger IR framing; higher bar |
| Ambitious | **ACM TOIS** | Expects deeper method or large-scale empirics |
| Poor fit | Top-tier IEEE Transactions expecting new algorithms | Novelty mismatch |
| IEEE option | **IEEE Access** | Scope accepts applied/empirical/negative-leaning work; APC; **not** automatic prestige; needs clear IR keywords and honest contribution type |

### Program B

| Class | Venue | Fit notes |
| --- | --- | --- |
| Realistic | Workshop / short empirical paper; or thesis-only | Diagnostic ceilings + negatives |
| Realistic | PLOS ONE / similar if rewritten as Roman Urdu multi-retriever empirical study | Must not claim new method |
| Ambitious | SIGIR short / resource paper | Needs polished benchmark release + TEST or larger sealed eval |
| Poor fit | Method-first IEEE journal claiming novel CG | Contradicts closed gates |

### Combined A+B

| Class | Notes |
| --- | --- |
| Possible | One long empirical “Urdu/Roman Urdu news IR: script-aware lexical freeze and Roman multi-retriever diagnostics” |
| Risk | Length, two populations, reviewer confusion, diluted claims |

---

## 8. IEEE Feasibility Discussion

### Can CURRENT Program A or B be submitted to an IEEE journal without falsely claiming methodological novelty?

**POSSIBLY** — for **IEEE Access** (or similar broad applied venues) as:

- empirical script-aware retrieval system study (Program A), and/or  
- empirical multilingual/script-mismatch evaluation + diagnostic ceilings (Program B),

**without** claiming a new algorithm.

**NO** — if the submission is framed as a novel adaptive router, novel CG architecture, or IEEE Transactions-style methodological breakthrough on current evidence.

**Strengthening before IEEE Access-class submission (should):**

- Restore/complete manuscript; clear contribution type in abstract.  
- Explicit related-work separation from Gupta/Chari/Butt/JRC-Names.  
- Statistical reporting discipline; no metric averaging.  
- Reproducibility package.  
- Optional: sealed TEST evaluation **only** under protocol (not for tuning)—currently unused for Program B Roman KN.

**Do not predict acceptance.** IEEE Access criteria emphasize originality of writing/contribution to knowledge, technical correctness, and scope—not “IEEE logo = accept.”

**Verified from IEEE Access About page (2026-09-22 search):** multidisciplinary OA journal; includes applied engineering and interesting solutions including negative-result-friendly framing; APC-supported; binary accept/reject. Exact APC figures differ across secondary guides—confirm on official IEEE Access author pages at submission time.

---

## 9. Separate vs Combined Paper Analysis

### Strategy A — Program A paper + separate Program B paper

| Aspect | Trade-off |
| --- | --- |
| Coherence | High per paper |
| Redundancy | Low if B cites A as prior freeze |
| Novelty clarity | A empirical; B diagnostic—clear |
| Workload | High (two manuscripts) |
| Thesis usefulness | Strong chapter split |

### Strategy B — Combine A + B

| Aspect | Trade-off |
| --- | --- |
| Narrative | “Lexical freeze then Roman multi-retriever stress test” |
| Risk | Length; mixing n=78/K/U with n=80 Roman KN |
| Novelty clarity | Still empirical, not method |
| Workload | One large paper |
| Reviewer concern | Scope creep; “what’s new beyond A?” |

### Strategy C — Publish A; keep B as thesis extension

| Aspect | Trade-off |
| --- | --- |
| Coherence | Strong for A |
| Risk | B may never appear as paper |
| Thesis usefulness | High—B supplies negative/diagnostic depth |
| Workload | Lowest for near-term publication |
| Scientific honesty | Aligns with closed novelty gates |

**Evidence-supported preference for near-term defensibility:** **Strategy C**, with Strategy A as optional later if capacity remains. Strategy B only if a single thesis-derived journal article is required and carefully structured.

---

## 10. Thesis Positioning

**Current title/proposal tone:** “Adaptive Dynamic Query Routing for Urdu Information Retrieval” implies a **successful adaptive router**.

**Actual trajectory:** Frozen script-aware BM25; dense/hybrid; adaptive routing investigated and **failed detectability (C1)**; multiple novelty/architecture NO-GOs; CG ceiling diagnosis.

### What the thesis can honestly claim

1. Design and freeze of a script-aware BM25 news retrieval system with sealed evaluation protocols.  
2. Controlled empirical evaluation of lexical, n-gram, dense, hybrid, and several expansion/fusion interventions on Roman Urdu known-item search.  
3. Diagnostic finding that **candidate-generation coverage**, not Top-5 ranking alone, dominates residual error under the evaluated architecture.  
4. Informative **negative result**: query-only adaptive selection among BM25/NG3/Dense was not detectably successful.  
5. Honest documentation that the ~80% Hit@5 stretch target is incompatible with the **current** BND Top-50 pool (49/80).

### What it cannot claim

- A working novel adaptive routing algorithm.  
- Solved Roman Urdu IR.  
- IEEE-level methodological novelty from closed gates.  
- Averaged Program A+B success rates.

### Should title change?

**Yes — recommended** for defensibility.

### Accurate title options

1. *Script-Aware and Multi-Representation Retrieval for Urdu and Roman Urdu News: An Empirical Study*  
2. *Empirical Evaluation of Lexical, Dense, and Hybrid First-Stage Retrieval for Roman Urdu Known-Item Search*  
3. *Candidate-Generation Limits in Roman Urdu to Urdu-Script News Retrieval: Controlled Experiments and Negative Results*  
4. *From Script-Aware BM25 to Multi-Retriever Diagnostics for Urdu News Search*  

(Option 1 or 4 best cover both Program A and B.)

---

## 11. Negative / Diagnostic Contribution Assessment

| Finding | Nature | Publishable? |
| --- | --- | --- |
| Query-only routing fails to beat fixed Dense | Empirical negative + diagnostic | **Useful**; supports thesis/B chapter; alone is thin for top method venues |
| CG ceiling 49/80; ranking cannot reach 80% on this pool | Structural diagnostic | **Strong empirical finding** within architecture-specific scope |
| Entity/name residual heterogeneous / literature-covered | Novelty gate outcome | Internal research integrity; not a paper by itself |
| Phase 7/8/10 unsupported under prereg | Controlled negatives | Valuable in empirical paper / thesis |

These are **not automatically novel methods**. They are **scientifically informative** relative to naive “just add a router/reranker” narratives and align with venues that accept careful empirical/negative applied studies (e.g., IEEE Access framing; PLOS ONE empirics).

---

## 12. Candidate Paper Narratives (existing evidence only)

### Narrative N1 — Program A standalone empirical

| Field | Content |
| --- | --- |
| RQ | Can script-aware BM25 recover known Urdu news articles and how useful is it naturalistically? |
| Contribution | Frozen M0; separate KN vs human metrics; Roman limitation |
| Evidence | 68/78; 27/40; 23/40 |
| Novelty | LIMITED |
| Limitation | Modest method novelty; single corpus |
| Publication type | Empirical system / script-aware IR study |
| Extra work | Packaging polish; DAS; align filename/title |

### Narrative N2 — Program B empirical multi-retriever + diagnostics

| Field | Content |
| --- | --- |
| RQ | How do lexical/n-gram/dense/hybrid and expansions behave on Roman Urdu ExactSource KN? |
| Contribution | Controlled comparisons; ceilings; negatives |
| Evidence | PHASE14 tables; 20/80; 40/80; 49/80; C1 |
| Novelty | NOT ESTABLISHED as method |
| Limitation | Small n; TRAIN+DEV; draft missing |
| Publication type | Empirical / diagnostic IR study |
| Extra work | Restore manuscript; optional TEST under seal protocol |

### Narrative N3 — Thesis-integrated empirical arc (A then B)

| Field | Content |
| --- | --- |
| RQ | What works and what fails for Urdu/Roman Urdu news retrieval from script-aware lexical freeze through multi-retriever diagnostics? |
| Contribution | End-to-end empirical program with honest negatives |
| Evidence | A + B + closed gates as Limitations |
| Novelty | LIMITED overall |
| Limitation | Not a method thesis |
| Publication type | Thesis; optional combined journal article |
| Extra work | Title/RQ reframing; chapter structure |

### Narrative N4 — “Novel adaptive routing” 

| Field | Content |
| --- | --- |
| Status | **INVALID** given C1 NO-GO |
| Action | **DO NOT pursue** |

---

## 13. Minimum Required Work

### Program A publication path

| Item | Priority |
| --- | --- |
| Keep claims empirical; no adaptive-routing overclaim | MUST DO |
| Complete Editorial Manager / DAS / SI consistency | MUST DO |
| Fix packaging title/filename mismatch awareness | SHOULD DO |
| New algorithms / TEST peek / retune K/U | DO NOT DO |

### Program B / thesis diagnostic path

| Item | Priority |
| --- | --- |
| Restore or rewrite Program B manuscript from PHASE14 | MUST DO (if publishing B) |
| Disclose LLM1 query authorship | MUST DO |
| Report ceilings and negatives honestly | MUST DO |
| McNemar / CIs where already available | SHOULD DO |
| Implement ColBERT/SPLADE/Doc2Query for “novelty” | DO NOT DO (architecture gate NO-GO) |
| Revive C1/C2a/entity CG | DO NOT DO |
| Chase 80% with combination methods | DO NOT DO |

### Thesis

| Item | Priority |
| --- | --- |
| Reframe title and RQs | MUST DO |
| Include negative/diagnostic chapters | MUST DO |
| Claim successful adaptive router | DO NOT DO |

---

## 14. Future Research-Line Decision

**Recommended strategy: D (evidence-supported mix) = primarily C + selective B**, not A.

- **C:** Focus on thesis completion with honest reframing.  
- **Publish Program A** (already furthest along).  
- Treat Program B as thesis substance; optional separate empirical paper later.  
- **B (publish existing, start separate IEEE line):** Only after thesis/A obligations, and only with a **new** problem outside closed RU first-stage CG/architecture gates.

### If a new IEEE methodological line is sought later

Do **not** casually invent a method. Require:

1. Problem **outside** closed Roman Urdu CG/entity/architecture gates (or a clearly new formulation with prevalence evidence).  
2. Literature matrix showing existing work does X but cannot address Z under Y.  
3. TRAIN/DEV feasibility gate with pre-declared binary criteria.  
4. No TEST leakage; no combination-novelty; no “Urdu is low-resource” as novelty.  
5. Contribution meaningful even if metrics stay below 80%.

---

## 15. Final Decision Matrix

| Item | Current status | Defensible contribution | Main weakness | Publication role | Next action |
| --- | --- | --- | --- | --- | --- |
| Program A | Frozen; PLOS package exists | Empirical script-aware BM25 study | Modest method novelty | Primary near-term paper | Complete/submit empirical paper path; keep frozen |
| Program B | Frozen PHASE14; draft `.tex` missing here | Empirical multi-retriever + CG diagnostics | No method novelty; small n | Thesis chapters; optional empirical paper | Restore manuscript only if publishing; else thesis |
| Adaptive routing line | C1 NO-GO | Informative negative | Not a positive method | Thesis Limitations / negative chapter | Do not revive |
| Thesis | Title misaligned with results | Empirical + diagnostic arc | Adaptive-routing branding | Degree requirement | Reframe title/RQs; write from frozen evidence |
| Future IEEE line | No surviving novelty in current RU line | None yet from this line | Prior gates closed | Separate future topic | Stop RU method invention; new gate if/when new problem |

---

## 16. Claims We Must NOT Make

1. That a novel adaptive dynamic query router was successfully developed.  
2. That Program A or B introduces a new first-stage algorithm competitive with ColBERT/SPLADE/script-gap neural IR.  
3. That 80% Hit@5 was achieved or is “almost achieved.”  
4. That 80% is impossible for **all** architectures (only for investigated pools with ceiling 49/80).  
5. That entity/name CG or architecture redesign yielded a GO novelty finding.  
6. That TEST results support any claim (TEST unused / sealed).  
7. Averaged Hit@5 across Program A n=78/K/U and Program B n=80.  
8. That an IEEE paper is accepted, submitted, indexed, or DOI-assigned without authoritative evidence (none verified in this audit).  
9. That “Urdu/Roman Urdu low-resource” alone constitutes methodological novelty.  
10. That combining BM25+Dense+RRF+EL+ColBERT is a novel contribution.

---

## Artifact index

| File | Role |
| --- | --- |
| `PUBLICATION_THESIS_POSITIONING_AUDIT.md` | This report |
| `PUBLICATION_TARGET_MATRIX.csv` | Compact contribution/target matrix |

---

**End of Publication + Thesis Positioning Audit.**
