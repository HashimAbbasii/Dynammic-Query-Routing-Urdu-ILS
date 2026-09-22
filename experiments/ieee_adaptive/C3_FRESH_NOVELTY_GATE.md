# C3 Fresh IEEE Journal Novelty Gate

**Status:** complete — method-novelty discovery only (no implementation)  
**Branch:** `research/roman-urdu-adaptive-retrieval`  
**HEAD:** `3b2e829bf9769d16f9b604ee68d7cc50ce128fa7`  
**Date (local):** 2026-09-22  
**Decision:** **NO-GO**

**Permanently closed in this line (not revived):**  
- C1 query-only adaptive expert routing  
- C2a institutional Latin acronym ↔ Urdu descriptive alias method (prevalence failed)

---

## 1. Objective

Determine whether frozen Program B evidence still contains a **different**, technically meaningful research problem that could support an **IEEE journal-level** methodological contribution — after C1 and C2a were honestly closed.

Not the goal: higher Hit@k by shopping models.  
Not the goal: conference-bar lowering.  
Acceptable outcome: **NO-GO**.

---

## 2. Repository Integrity

| Check | Result |
| --- | --- |
| Branch | `research/roman-urdu-adaptive-retrieval` |
| HEAD | `3b2e829bf9769d16f9b604ee68d7cc50ce128fa7` |
| Working tree | Clean except untracked `experiments/ieee_adaptive/` |
| Program A modified | **No** |
| Program B modified | **No** |
| C1/C2a reports modified | **No** |

---

## 3. TEST Isolation

```text
TEST_CONTENT_ACCESSED = FALSE
```

---

## 4. Frozen Evidence Used

| Source | Role |
| --- | --- |
| `PHASE14_FINAL_REPORT.md` | SoT metrics, unresolved gaps, phase history |
| Phase 13 scoring CSV | n=80 Hit@k / all-miss composition |
| R2-B0 failure analysis | ROOM/ENT/VOCAB/RANK taxonomy (gold-informed) |
| Phase 6 diagnostics | MISS vs RANK; McNemar complementarity |
| Phases 7–12 reports | What was already tested and stopped |
| `C1_DETECTABILITY_DIAGNOSTIC.md` | Routing closed |
| `C2A_FEASIBILITY_PROBE.md` + annotations | Institutional-alias prevalence closed; 31-way label breakdown |

**Headline frozen facts (n=80 TRAIN+DEV):** Method-D Hit@5 5/80; Dense Hit@5 20/80; Hybrid Hit@50 40/80; BND union Top-50 misses **31/80**; Hybrid RANK-like (Hit@50 ∧ ¬Hit@5) **23/80**; Dense RANK-like **16/80**.

---

## 5. Complete Failure-Mechanism Map

| Failure mechanism | Evidence | Affected (approx.) | Already tested? | Existing literature | Remaining gap |
| --- | --- | --- | --- | --- | --- |
| Orthographic / spelling variation | ROOM; Method D near-forms | Large share of BM25 misses; 12/23 labeled miss31 on n51 have ROOM | R2-1 UNSUPPORTED; NG3 partial | MSIR Gupta 2014; FIRE; phonetic QE | Incremental only |
| Transliteration ambiguity | Multiple Roman forms; dict siblings | Present but NORM primary=0 | Dict fold rejected | UrduPhone; translit models | Tooling exists |
| Phonetic variation | ROOM/NG3 motivation | Narrow dual-miss recoveries | NG3 PARTIAL | Phonetic IR | Covered |
| Script conversion (same EN name) | C2a D cases (`state bank`↔`اسٹیٹ بینک`) | 3 confirmed D in 31 | Method D index | Chari SIGIR 2025 script gap | Covered |
| Lexical / Method-D bridge failure | R2-C0; zero content overlap | Systemic for Method D | Method D / R2-1 | Romanization IR | Diagnosed; fix failed |
| Vocabulary / bilingual paraphrase | VOCAB; Phase 11 five | 5 VOCAB in miss31 n51; Phase 11 deep Dense ranks | Dense tried; Phase 11 Option2 skipped | CLIR surveys; dense first-stage reviews | Generic CLIR |
| Morphology | Not primary in R2-B0 | Unclear / minor | Not dedicated | Morphology-aware IR | Weak evidence |
| Code-mixing | EN+RU queries common | Many queries | Implicit in Dense/BM25 | Hinglish/code-mixed IR benches | Known setting |
| Person / product / entertainment entity | C2a **B=18/31**; R2 ENT=16/47 | **Dominant among all-miss** | Phase 9 WP partial; Phase 7 letter-name no | JRC-Names; cross-script name IR; NE translit | Crowded |
| Acronym letter-name | Phase 7 | Quad-23 | UNSUPPORTED | Letter-name hacks | Closed empirically |
| Institutional descriptive alias | C2a A=6/31 | 6 confirmed | Phase 9/7/11 | Acronym↔expansion CLIR | **C2a NO-GO (rare)** |
| Semantic paraphrase | VOCAB/C | Overlaps Phase 11 | Dense | Multilingual dense / CLIR | Covered |
| Query–doc lexical bridge | ROOM+ENT+VOCAB | Most misses | Multi-rep Program B | First-stage semantic models TOIS review | Covered class |
| Candidate-generation failure | 31/80 BND miss50; Hybrid miss50=40 | Majority of residual | All first-stages | First-stage retrieval literature | Symptom, not mechanism |
| Ranking failure | Hybrid RANK-like 23; Dense 16 | Secondary | Phase 12 **skipped** (pool gate) | Rerankers | Wrong primary bet |
| Representation failure | Dense deep VOCAB misses | Phase 11 | e5-small | Multilingual embeddings | “Better model” = engineering |
| Ambiguity / NEIGH | KN005 | 1 | Labeled | Query ambiguity | Benchmark/need |
| Long / multi-concept queries | Some compositional KN queries | Present | Not isolated IV | Compositional IR | Not isolated here |
| Rare vocabulary | C2a E=1 | Small | — | OOV IR | Too few |
| Doc-side terminology variation | Method D gold encoding | Systemic | R2-C0 | Indexing choices | Engineering/analysis |
| Adaptive expert selection | Oracle 28 vs Dense 20 | Discordances exist | **C1 NO-GO** | Arabzadeh/MoR | Closed |
| Always-on multi-list fusion | Phase 8 dilution | — | UNSUPPORTED | RRF literature | Closed empirically |

Supporting CSV: `experiments/ieee_adaptive/C3_FAILURE_MECHANISM_MATRIX.csv`.

---

## 6. Candidate-Generation vs Ranking vs Representation Analysis

| Class | Status in Program B |
| --- | --- |
| **A Candidate-generation** | Primary residual: 31/80 outside BND Top-50; Hybrid still misses 40/80 at 50 |
| **B Ranking** | Real but secondary (23 Hybrid Hit@50∧¬Hit@5); Phase 12 correctly refused rerank without pool expansion |
| **C Representation** | Dense helps many ENT/ROOM but fails deep VOCAB; not a free novelty slot |
| **D Linguistic normalization** | NORM rejected; letter-name failed; script-of-same-EN-name ≠ descriptive alias |
| **E Semantic** | Phase 11 bilingual paraphrase remains hard — but that is classic CLIR |
| **F Benchmark/data** | ExactSource known-item; W1+LLM1 mix; Method D is a project-specific latin bridge; n=80 small — risks overclaiming “Roman Urdu IR in general” |

**Implication:** Any new method must target **candidate generation** of a **specific** linguistic mechanism. C2a already tested the best remaining specific mechanism (institutional descriptive alias) and failed prevalence. The next-largest residual (**person/product entities**, 18/31) is **not specific enough** for journal novelty given JRC-Names / cross-script name IR.

---

## 7. Remaining Open Problems

After closing C1/C2a and reviewing Phases 2–14:

1. **Person/product/sports entity bridging** under Roman queries → Urdu news (numerous, but literature-heavy).  
2. **Residual ROOM** orthography under Method D (already stress-tested; NG3 narrow).  
3. **Deep bilingual paraphrase** (Phase 11; Dense fails; classic CLIR).  
4. **Ranking headroom** after gold is in pool (not the 31-problem; not novel as primary claim).  

None currently clear a journal-level *method* gap under the rejection rules in §14 of the master prompt.

---

## 8. Fresh Literature Search

Mechanism-driven (not only “Roman Urdu retrieval”):

| Area | Closest work | Implication |
| --- | --- | --- |
| Script gap / Latinized queries | Chari et al. SIGIR 2025 *Lost in Transliteration* | Occupies neural script-gap repair |
| Mixed-script / translit IR | Gupta SIGIR 2014; FIRE TST; phonetic QE | Occupies spelling/script QE |
| Roman Urdu IR / translit | Butt et al. 2025 LowResNLP + LoResMT | Occupies RU IR dataset + transliteration |
| Cross-script **names** | JRC-Names; JRC-Names-Retrieval (LREC 2024); byte-level name retrieval | Occupies entity-name cross-script search |
| Code-mixed IR | Hinglish/code-mixed search benchmarks | Occupies code-mix product/search setting |
| First-stage semantic / vocab mismatch | Guo et al. TOIS review; CLIR surveys (Oard et al.) | Occupies “fix candidate gen / CLIR” |
| Acronym↔expansion | Jacquet et al. LREC 2016; NE translation resources | Occupies institutional alias inventories |
| Adaptive sparse/dense | Arabzadeh CIKM 2021; MoR EMNLP 2025 | Occupies routing (also C1-closed) |
| Error taxonomies | RAG error taxonomies 2025; IR failure analyses | Taxonomies exist; not RU-news specific enough alone for method claim |

**Wording:** No claim of “never done.” For a *new method* beyond Program B’s already-run stack, **no directly matching under-addressed journal-scale gap was identified** that is both prevalent in this evidence and distinct from the above.

---

## 9. Novelty Matrix

| Candidate | Existing work | RU | Urdu docs | Cross-script | Mechanism | Cand-gen | Proposed contribution | Novelty risk |
| --- | --- | ---: | ---: | ---: | --- | ---: | --- | --- |
| Revive query routing | C1; Arabzadeh; MoR | Yes | Yes | Yes | Predict expert | Indirect | Router | **HIGH** (closed) |
| Institutional descriptive alias method | C2a; Jacquet; Phase 7/9 | Yes | Yes | Yes | Org alias | Yes | Alias CG | **HIGH** (prevalence fail) |
| Person/product name CG | JRC-Names; name IR; Phase 9 | Yes | Yes | Yes | ENT | Yes | Name bridging | **HIGH** |
| Transliterate-train for Urdu | Chari 2025 | Apply | Yes | Yes | Script gap | Neural | Fine-tune | **HIGH** |
| Better multilingual dense | CLIR + dense reviews | Apply | Yes | Yes | Semantic | Yes | Model swap | **HIGH** |
| Rerank Hybrid pool | Standard rerankers | — | Yes | — | Ranking | No | Rerank | **HIGH** + Phase12 gate |
| Generic QE / LLM rewrite | Ubiquitous | — | — | — | Mixed | Maybe | Expansion | **HIGH** |
| Code-mix specific method | Hinglish IR benches | Partial | Yes | Partial | Code-mix | Yes | Code-mix IR | **HIGH** |
| Publish Program B empirical SoT | Empirical systems papers | Yes | Yes | Yes | Multi-fail | Diagnosed | Evidence paper | *Publication path, not new method novelty* |
| New mechanism from residues | — | — | — | — | Unclear | — | — | **No survivor** |

---

## 10. Rejected Directions

| Idea | Why rejected |
| --- | --- |
| C1-style routing / more features / LLM router | C1 NO-GO; crowded adaptive IR |
| C2a institutional alias method / lower threshold / redefine D as A | C2a NO-GO; protocol forbid |
| Person/product entity bridging as IEEE method | Dominant residual, but JRC-Names / cross-script name IR / Phase 9 already cover the class |
| Transliterate-train / larger e5 / MiniLM | Chari 2025 + engineering |
| RRF / 3-way / cascade / rerank-first | Phases 8/10/12 already decided |
| Generic QE / LLM / “transformer” | Automatic rejection criteria |
| Spelling NORM / letter-name only | Empirically unsupported or Phase 7 |
| “Roman Urdu is hard / low-resource” | Not a mechanism |
| Failure-taxonomy-only as method novelty | Useful documentation; insufficient alone as *new technical mechanism* at journal method standard without a solvable, prevalent gap |
| Benchmark expansion as novelty | Not a retrieval contribution |

---

## 11. Strongest Candidate

**None surviving as a new method-oriented IEEE journal direction.**

The *empirically largest* residual class among the 31 all-misses is **non-institutional entity** (18/31), but that is **not** a strong novelty candidate under §13–14: it fails literature separation (name/entity cross-script IR is mature) and collapses to “better entity bridging / resources,” which Phase 9 already probed.

---

## 12. Exact Research Gap

**No additional method gap clears the journal bar on this evidence.**

What remains scientifically true (but not a green light for a new IEEE method project):

- Program B documents a hard Roman Urdu → Urdu-script news setting with a large candidate-generation ceiling.  
- Complementary experts exist, but are not query-only predictable (C1).  
- Institutional descriptive alias exists but is too rare here (C2a).  
- Remaining misses are mostly entity/ROOM/VOCAB classes already addressed as research *classes* in MSIR, CLIR, name IR, and script-gap neural IR.

---

## 13. Why It Is Different From C1/C2a

C3 does not reopen C1 or C2a. It asks whether **another** mechanism remains. After mapping, the next-largest residues fail the novelty/prevalence/literature tests that C2a applied honestly to institutional aliases.

---

## 14. Feasibility

No conditional feasibility probe is authorized, because no candidate reached “promising but needs one small gate.” Launching another prevalence gate on person-names would likely either:

- fail similarly, or  
- “succeed” into a high-novelty-risk entity-IR project already covered by JRC-Names-class work.

That would waste cycles the same way a forced C2a rescue would.

---

## 15. IEEE Journal-Level Contribution Potential

**For a new method paper derived from remaining Program B residues: insufficient.**

Separately (outside C3 method-novelty scope): packaging **already-frozen Program B** as an empirical/systems journal manuscript can still be a legitimate *publication strategy* for work already done — but that is **reporting completed science**, not discovering a new implementable novelty direction in this gate. C3 does **not** authorize new method implementation under that path either.

No acceptance prediction is made for any venue.

---

## 16. Decision

# **NO-GO**

---

## 17. Next Step

> **STOP. Do not implement another method from this gate.**

Do not rescue C1 or C2a.  
Do not start person-name dictionaries, transliterate-train, rerankers, or routers.  
If future research continues, it requires a **new evidence base or a new problem statement external to “squeeze one more method out of n=80 Program B residues.”**

---

## 18. Limitations

- n=80 ExactSource; not all Roman Urdu.  
- Gold-informed taxonomies (R2-B0; C2a verification) are diagnostic, not pre-retrieval features.  
- Literature search is targeted, not exhaustive of every venue.  
- Absence from searched literature ≠ proof of non-existence — but survivors still failed prevalence or specificity.

---

## 19. Reproducibility

| Item | Value |
| --- | --- |
| Branch | `research/roman-urdu-adaptive-retrieval` |
| HEAD | `3b2e829bf9769d16f9b604ee68d7cc50ce128fa7` |
| This report | `experiments/ieee_adaptive/C3_FRESH_NOVELTY_GATE.md` |
| Matrix CSV | `experiments/ieee_adaptive/C3_FAILURE_MECHANISM_MATRIX.csv` |
| Program A/B touched | No |
| TEST accessed | No |

---

**End of C3.** Honest negative: no defensible new IEEE journal *method* novelty identified from remaining frozen Program B evidence after C1/C2a closures.
