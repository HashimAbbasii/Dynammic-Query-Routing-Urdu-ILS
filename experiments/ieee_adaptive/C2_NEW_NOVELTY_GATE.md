# C2 New Novelty Gate — Failure Analysis After C1 Closure

**Status:** complete — research-question / novelty feasibility gate (not a method implementation)  
**Branch:** `research/roman-urdu-adaptive-retrieval`  
**HEAD:** `3b2e829bf9769d16f9b604ee68d7cc50ce128fa7`  
**Date (local):** 2026-09-22  
**Decision:** **CONDITIONAL NOVELTY**

**Closed permanently in this line of work:** query-only adaptive expert routing (C1 = NO-GO). This document does **not** revive C1/C2-router.

---

## 1. Executive Summary

After C1 closed predictable expert routing, this gate re-examined **why** Roman Urdu queries fail against Urdu-script news using frozen Program B evidence plus a targeted literature pass.

**Empirical center of mass:** failures are overwhelmingly **candidate-generation** failures, not ranking failures. On n=80, BM25∪NG3∪Dense leave gold outside Top-50 for **31/80** queries; Hybrid Hit@50 peaks at **40/80**. Phase 12 correctly skipped reranking.

**Failure structure (Program B):** ROOM (romanization/orthography), ENT (names/products), and VOCAB (cross-lexeme / bilingual paraphrase) dominate BM25 misses; NORM was rejected as a primary driver. Phases 7 and 9 show that **letter-name acronym expansion** and **Wikipedia title expansion** do not close institutional acronym / paraphrase dual-misses; Dense still ranks some Phase-11 VOCAB golds in the hundreds–thousands.

**Literature:** mixed-script IR, phonetic/char bridging, Roman Urdu transliteration, Roman↔Roman IR datasets, and **neural script-gap repair via transliterate-train** (Chari, Ounis & MacAvaney, SIGIR 2025) already cover large parts of the orthographic/script story. Generic hybrid/adaptive/rerank/“better embeddings” are not novel.

**Residual candidate gap (conditional):** a mechanism that is **not** the same as pure same-word script gap — namely **Latin institutional acronyms / English institutional phrasing ↔ Urdu-script descriptive aliases** (e.g. CPEC-class forms vs Urdu corridor phrasing), which Program B showed is not solved by Method D, NG3, letter-names, Wikipedia exact titles, or off-the-shelf multilingual dense retrieval.

That gap is **promising but not yet proven large enough or methodologically distinct enough** for an IEEE method paper. Hence **CONDITIONAL NOVELTY**: one small TRAIN/DEV feasibility probe is required before authorizing any method build. If that probe fails pre-declared criteria → convert to **NO-GO**.

---

## 2. Why C1 Was Closed

| Fact | Value |
| --- | --- |
| Hypothesis | Query-only features predict best of {BM25, NG3, Dense} |
| Unique-winner n | 22 (Dense 17, NG3 4, BM25 1); ties 6; all-fail 52 |
| Majority / always-Dense | 17/22 = 0.773 |
| Query-only LOO LogReg | 14/22 = 0.636 (below majority) |
| Routed Hit@5 | 17/80 vs fixed Dense 20/80 vs oracle 28/80 |

**Interpretation retained:** experts are complementary; **query-only predictable** complementarity is not. Adaptive query-only routing remains **CLOSED**. No feature/model rescue of C1 is authorized.

Artifact: `experiments/ieee_adaptive/C1_DETECTABILITY_DIAGNOSTIC.md`.

---

## 3. New Research Question

> What are the actual failure mechanisms behind Roman Urdu → Urdu-script news retrieval failures, and is there a **specific**, technically meaningful, under-addressed mechanism that can support a new IEEE contribution?

Not: “make Roman Urdu retrieval better” in general.  
Not: revive routing.

---

## 4. Program B Failure Evidence

Sources (read-only): Phase 14 SoT; R2-B0 failure analysis; R2-C0 representation audit; Phase 6 diagnostics; Phases 5/7/8/9/10/11/12 records; Phase 13 scoring CSV (`SHA-256 f59c3710…fe5d66`).

### 4.1 Aggregate ceilings (n=80, frozen Hit@k)

| Method | Hit@5 | Hit@50 | Outside Top-50 |
| --- | ---: | ---: | ---: |
| BM25 Method D | 5 | 13 | 67 |
| NG3 | 10 | 19 | 61 |
| Dense e5-small | 20 | 36 | 44 |
| Hybrid RRF | 17 | 40 | 40 |
| Union BM25∪NG3∪Dense | 28 | **49** | **31** |

Oracle best-of-3 Hit@5 = 28/80 remains an upper bound on **selection among existing experts**, not on fixing ALL_FAIL / deep MISS cases.

### 4.2 MISS vs RANK (candidate generation vs ranking)

From Phase 6 (n=51) and Phase 13 (n=80):

- BM25 Hit@5 failures were almost all **MISS** (gold absent from Top-50): 45 MISS vs 2 RANK on n=51 R2-B0 failures.
- On n=80, Dense has 36 Hit@50 but only 20 Hit@5 → **16** “in pool, out of Top-5” cases; Hybrid has **23** such. Ranking headroom exists **only after** gold enters the pool.
- **31/80** are outside BM25∪NG3∪Dense Top-50 entirely → pure candidate-generation ceiling for current experts.
- Phase 12 reranking was **SKIPPED** because pool expansion gates were not met (Phase 14).

### 4.3 Diagnostic taxonomy (gold-informed; n=51 BM25 Hit@5 failures)

From frozen `R2_B0_FAILURE_ANALYSIS.md` (human/gold-aware labels — **not** pre-retrieval features):

| Primary | Count / 47 | Mechanism (Program B wording) |
| --- | ---: | --- |
| ROOM | 19 | Query Latin forms vs Method-D / letter-split index forms |
| ENT | 16 | Distinctive names not matching indexed romanization |
| VOCAB | 9 | Different lexemes / paraphrase (not spelling of same token) |
| RANK | 2 | In Top-50, not Top-5 |
| NEIGH | 1 | Neighbor topic |
| NORM | **0** | No recurring content-bearing normalization pattern |

R2-1 fallback romanizer: **UNSUPPORTED**. NG3: **partial** (narrow dual-miss recoveries). Phase 7 letter-name: **UNSUPPORTED** (0/23 Quad-23 Top-50). Phase 9 Wikipedia titles: **partial**, small; **FBR/CPEC/ADB/JLO-class** absent as exact title keys. Phase 8/10 fusion/cascade: net non-gains. Phase 11 five VOCAB dual-misses: Dense ranks 110–11599; existing resources gave no viable candidate-generation path; **new bilingual glossary Option 2 not authorized**.

### 4.4 Standing unresolved gaps (Phase 14 §2.3)

1. **Acronym / institutional surface forms** (FBR, CPEC, ADB, JLO-class).  
2. **Cross-lingual paraphrase / vocabulary gap** (Phase 11 five).  

These are the only Program B–endorsed open scientific problems frozen without a solution claim.

### 4.5 Limitations of n=80

Not representative of all Roman Urdu, all Pakistani news search, or all query distributions. Mix of human W1 and LLM-drafted/human-reviewed LLM1 queries. Known-item ExactSource setting. Treat as a **project research benchmark**, not a universal corpus.

---

## 5. Failure Taxonomy

Mapped to Program B evidence (categories may co-occur; primary labels are gold-informed).

| ID | Category | Evidence in Program B | Dominant type (§7) |
| --- | --- | --- | --- |
| A | Orthographic variation | ROOM; Method D `world`↔`orld`-class; NG3 sometimes helps | Type 1 / 3 |
| B | Transliteration ambiguity | Multiple Roman forms; dict siblings (`kya`/`kiya`) rejected as primary NORM | Type 3 (weak as primary) |
| C | Lexical bridge failure | ROOM + Method D index vs chat/English Roman | Type 1 / 3 |
| D | Morphological variation | Not established as primary driver | Unclear / minor |
| E | Code-mixing | English + Roman Urdu in queries (R2-C0 English-hint tokens) | Mixed 1/3/4 |
| F | Entity / acronym failure | ENT; Phase 7/9; CPEC/FBR/ADB/SBP probes | Type 1 / 3 |
| G | Semantic paraphrase | VOCAB; Phase 11 deep Dense misses | Type 1 / 4 |
| H | Unknown / rare RU vocabulary | Outside 198-key dict; Method D fallback heavy on golds | Type 3 |
| I | Candidate-generation failure | 31/80 union Top-50 misses; Phase 6 MISS dominance | Type 1 (meta) |
| J | Ranking-only failure | Few BM25 RANK; more Dense/Hybrid Hit@50∧¬Hit@5 | Type 2 |
| K | Benchmark / need mismatch | NEIGH (KN005); possible query ambiguity | Type 5 |

**NORM-style dictionary fold is not the main story** (primary NORM = 0).

---

## 6. Candidate-Generation vs Ranking Analysis

| Question | Answer from frozen evidence |
| --- | --- |
| Is reranking the right next bet? | **No** as primary — Phase 12 gating still applies for the large MISS tail |
| Is fusion/routing the right next bet? | **No** for query-only routing (C1); fixed fusion already tried and often diluted |
| Where is the mass? | **Candidate generation** (31/80 BND Top-50 misses; Hybrid still misses 40/80 at 50) |
| What remains after Dense? | Institutional acronym + bilingual paraphrase dual-misses; residual ROOM/ENT |

Any future method must target **getting gold into the pool**, not only reordering Hybrid’s Top-50.

---

## 7. Literature Review

Targeted search (ACL/EMNLP/SIGIR/CIKM/FIRE/IEEE/arXiv as available). Not exhaustive of all IR.

### Roman Urdu IR / NLP

- **Butt et al. (LowResNLP 2025)** — Roman Urdu MS MARCO–style IR (Roman↔Roman) + mT5 rerank; claims first dedicated RU IR dataset.  
- **Butt et al. (LoResMT 2025)** — Transformer Roman↔Urdu transliteration (high Char-BLEU).  
- **Khan et al. (NLE 2020)** — UrduPhone / Lex-Var normalization.  
- **Roman Urdu NER (IJCNN 2025)** — NER resources/models; not news IR candidate generation.  
- **UIR-21 / JCBI** — Urdu news IR with Urdu/English/Roman-Urdu query modes (mode pipelines, not failure-mechanism method).  
- **ULTRA Program A** — Script-aware BM25 (script routing).  
- **ULTRA Program B** — Multi-representation empirical study (this evidence base).

### Mixed-script / transliteration-aware IR

- **Gupta et al. (SIGIR 2014)** — Mixed-script IR; joint embedding + QE for spelling/script variants.  
- **FIRE transliteration search / DCU 2014** — Normalization + fuzzy matching (Hindi lyrics).  
- **Phonetic QE for transliterated Hindi** — Hindex-style expansion + BM25.  
- **Cross-script Arabizi lines** — Mapping/selection for Romanized Arabic.

### Neural script gap (highly relevant 2025)

- **Chari, Ounis & MacAvaney (SIGIR 2025)** — *Lost in Transliteration: Bridging the Script Gap in Neural IR*. Shows multilingual dense/rerankers degrade on Latinized queries; proposes **transliterate-train** (mix native + Latinized queries). Languages studied include settings such as Greeklish/Arabizi/Chinese/Russian framing — **not** a Roman-Urdu institutional-alias study, but it **directly occupies** the “fine-tune for script gap” novelty slot.

### CLIR / bilingual bridging (adjacent to VOCAB/acronym)

- Long-standing CLIR literature: query translation, bilingual lexicons, NE transliteration for CLIR, acronym/proper-name translation in CLIR (classic SIGIR/ACL lines).  
- English↔Urdu CLIR and Urdu monolingual IR (e.g. CURE) address related but not identical settings.

**Takeaway:** orthographic/script-gap and generic bilingual CLIR are **crowded**. A contribution must be narrower than “transliteration” or “CLIR.”

---

## 8. Novelty Matrix

| Work | Roman Urdu | Urdu-script Docs | Cross-script | Failure Analysis | Proposed Mechanism | Adaptive | Main Overlap |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Butt et al. LowResNLP 2025 | Yes | No (Roman passages) | Via synth. translit. pipeline | Limited | BM25 + mT5 rerank | No | Same-script RU IR dataset |
| Butt et al. LoResMT 2025 | Yes | N/A (translit.) | Yes | Eval splits | Transformer transliteration | No | Script conversion tool |
| Gupta SIGIR 2014 | No (Indic MSIR) | Mixed | Yes | Spelling/script | Joint embedding + QE | No | Orthographic/script matching |
| FIRE/DCU 2014 | No | Mixed lyrics | Yes | Vocab mismatch | Norm + fuzzy | No | Fixed spelling bridge |
| Chari et al. SIGIR 2025 | No (other langs) | Native scripts | Yes (script gap) | Script-gap degradation | Transliterate-train neural IR | No | **Blocks “just fine-tune for RU script gap” as novelty** |
| Khan NLE 2020 | Yes | N/A | Phonetic | Lexical variants | UrduPhone clustering | No | Normalization resource |
| UIR-21 JCBI | Query modes | Yes | Multi-mode | Metrics by mode | Hybrid query modes | Unclear | Mode CLIR, not mechanism |
| Program A M0 | Script detect | Yes | Method D | Limited in paper | Script-aware BM25 | Script only | Baseline system |
| Program B Phases 2–14 | Yes | Yes | Yes | **Yes (strong)** | Multiple fixed reps | No (failed cascades) | Empirical failure evidence |
| C1 detectability | Yes | Yes | Yes | Routing fail | Query-only expert predict | Yes (failed) | Closed direction |
| Phase 7/9 ULTRA | Yes | Yes | Entity/title | Controlled negatives | Letter-name / WP titles | No | Shows resource gaps for acronyms |

---

## 9. Closest Existing Work

1. **Chari et al. SIGIR 2025** — closest for “neural fix for Latinized queries → native docs.” Applying transliterate-train to Urdu is **incremental application**, not a new problem statement.  
2. **Gupta et al. SIGIR 2014 / FIRE MSIR** — closest for orthographic/script term bridging.  
3. **Butt et al. 2025 (IR + transliteration)** — closest for Roman Urdu IR/transliteration tooling; different document script setting (Roman corpus) or non-IR transliteration metrics.  
4. **Classic CLIR acronym / NE translation** — closest for institutional aliasing; **not found** in searched literature as a packaged Roman-Urdu→Urdu-**news** candidate-generation method with the specific failure profile Program B measured — wording: **adjacent / partially addressed**, not “never done.”

---

## 10. Candidate Research Gaps

### Gap α — Pure script / ROOM gap  
**Status:** **Insufficient for new novelty.** Covered by MSIR, phonetic/char methods, Method D/NG3 attempts, and Chari 2025 transliterate-train.

### Gap β — Ranking / reranking / fusion  
**Status:** **Insufficient.** Phase 8/10 negatives; Phase 12 skip; C1 routing closed.

### Gap γ — Institutional Latin acronym / English institution phrase ↔ Urdu descriptive alias (candidate generation)  
**Status:** **Conditional candidate.**  
Evidence it matters: Phase 14 unresolved #1; Phase 7/9 negatives; Phase 11 CPEC/SBP probes (0 usable title hits / wrong synonym).  
Distinct from Gap α: CPEC is **not** a character-level Romanization of اقتصادی راہداری; it is a **bilingual institutional alias**.  
Literature: partially addressed by general CLIR/NE translation; **not found** as a completed Roman-Urdu news method matching this failure profile in the searched set.  
Risks: small query count; “build a glossary” is engineering (Phase 11 Option 2 was rightly not authorized as a phase); may collapse into generic bilingual QE.

### Gap δ — Open semantic paraphrase beyond institutional aliases  
**Status:** **Weak as standalone IEEE method** without a distinct mechanism (Dense already is the semantic attempt; deep misses remain). Too close to “better CLIR / better multilingual retrieval.”

---

## 11. Rejected Directions

| Idea | Why rejected as novelty |
| --- | --- |
| Query-only adaptive routing | C1 NO-GO |
| BM25+Dense / RRF / 3-way fusion / cascade | Program B tried; fusion can dilute; not novel |
| “Better embeddings” / larger multilingual model | Engineering unless tied to a distinct mechanism; Chari occupies fine-tune-for-script-gap |
| Generic query expansion / LLM expansion | Too broad; leakage/eval risks; not mechanism-specific |
| Reranking | Wrong bottleneck for the MISS majority |
| Dictionary sibling NORM (kya/kiya) | Primary NORM = 0 |
| Document-side fallback romanizer (R2-1) | UNSUPPORTED |
| Letter-name acronym expansion alone | Phase 7 UNSUPPORTED |
| Wikipedia exact-title expansion alone | Partial; misses FBR/CPEC-class |
| “First Roman Urdu IR” claim | Contradicted by Butt 2025 (and related mode work) |
| Failure-analysis-only paper without a method | May be useful documentation; unlikely sufficient as sole IEEE research contribution |

---

## 12. Candidate Contribution

**Not authorized for implementation yet.** Conditional framing only.

### Research question (one sentence)

> Can a **candidate-generation** method that explicitly bridges **Latin institutional acronyms / English institutional phrases** to **Urdu-script descriptive aliases** recover ExactSource documents that current Method-D, character-n-gram, Wikipedia-title, letter-name, and multilingual dense first-stages miss on Roman Urdu news queries?

### Hypothesis (falsifiable)

> On a predeclared TRAIN/DEV subset of institutional-alias failures, a bridge that injects Urdu descriptive aliases (from a resource **not** mined from gold articles) will raise Hit@50 for that subset versus frozen Dense and Hybrid baselines, without relying on query-only expert routing.

### Existing limitation

Program B shows these failures are **not** fixed by orthographic bridges (NG3/Method D), letter-name expansion, Wikipedia exact titles, or off-the-shelf multilingual dense retrieval — and they are **not** the same object as pure same-lexeme script gap addressed by Chari 2025.

### Proposed mechanism (high-level only)

Institutional-alias candidate generation: detect Latin acronym / institution-like spans → map to Urdu descriptive alias set → expand or dual-query the **existing** Urdu-script / Method-D indexes to enlarge the candidate pool.  
**Not:** C1 router. **Not:** generic RRF. **Not:** unrestricted LLM rewriting without a sealed protocol.

### Why it *may* be novel

Compared to Gupta/FIRE (spelling/script variants of the **same** term) and Chari (transliterate-train for script gap), this targets **bilingual institutional aliasing** as the failure mechanism, with Program B controlled negatives showing standard MSIR-like and WP/letter-name resources fail on the measured cases.  
Compared to generic CLIR: the claim would need to stay tied to **Roman Urdu query surface + Urdu news alias inventory + candidate-generation metric**, not “CLIR works.”

### Why it may still fail the novelty bar

Classic acronym/NE CLIR may be judged sufficient prior art; n may be too small; a hand-built alias list may be dismissed as engineering.

---

## 13. Feasibility Experiment (required before any method build)

**Name:** C2a — Institutional-alias prevalence & non-gold resource probe (TRAIN/DEV only).

### Steps (diagnostic only)

1. **Prevalence audit (no new retrieval required first):** From frozen Phase 13 per-query outcomes + existing gold-informed labels/notes (ROOM/ENT/VOCAB; Phase 11 list), count how many of the **31** union Top-50 misses are plausibly institutional-alias driven vs person-ENT vs ROOM vs open paraphrase vs NEIGH. Report counts; do not hide small n.  
2. **Resource constraint:** Use only a **pre-existing public** alias/title resource (document file + hash). **Forbidden:** mining aliases from gold article text; TEST; tuning aliases to make golds hit.  
3. **Optional single frozen probe (if prevalence ≥ predeclared threshold):** Apply a **preregistered**, deterministic expansion rule to Method-D BM25 Top-50 only (no Dense retrain, no RRF tuning, no router). Score Hit@50 on the predeclared institutional subset and on full n=80 for side-effect regressions.

### Success criterion (pre-declared)

- Institutional-alias–plausible share of the 31 Top-50 misses is **≥ 8 queries** (10% of n=80), **and**  
- On that subset, the frozen probe improves Hit@50 by **≥ +3 absolute** vs Method-D alone **and** does not reduce full-population Hybrid Hit@50, **and**  
- Mechanism remains distinguishable in writing from Chari transliterate-train and Gupta MSIR.

### Failure criterion (pre-declared) → convert this gate to **NO-GO**

- Institutional-alias–plausible misses **< 8**, **or**  
- Probe gain **< +3** Hit@50 on the subset, **or**  
- Gains only appear after gold-derived alias mining, **or**  
- Contribution collapses to “add bilingual QE / fine-tune multilingual retriever” without a distinct mechanism.

### TEST protocol

TEST remains sealed. C2a uses TRAIN/DEV only. Final evaluation design (if ever authorized later) must keep TEST sealed until a single confirmatory run after freeze.

---

## 14. Decision

# **CONDITIONAL NOVELTY**

**Not** NEW NOVELTY CANDIDATE FOUND — evidence and literature gap are suggestive but not yet sufficient to authorize a full method paper build.  
**Not** NO-GO — Program B leaves a residual failure mechanism (institutional/bilingual alias candidate generation) that is **not identical** to the closed C1 routing hypothesis and **not identical** to pure script-gap repair already published at SIGIR 2025.

---

## 15. Recommended Next Step

**Exactly one next step:** run **C2a** (prevalence audit + optional preregistered non-gold resource probe) under the success/failure criteria in §13.

- If C2a **fails** → close this IEEE direction (**NO-GO**); do not invent another method.  
- If C2a **passes** → open a **new** methodology preregistration (still no TEST; still no C1 revival).  

**Do not** implement the full alias system, neural transliterate-train, or any adaptive router in this step.

---

## 16. Integrity / TEST Status

```text
TEST_CONTENT_ACCESSED = FALSE
```

| Check | Status |
| --- | --- |
| Program A modified | No |
| Program B modified | No |
| Frozen artifacts modified | No |
| C1 routing revived | No |
| Commit created | No |

**Files created by this gate:** `experiments/ieee_adaptive/C2_NEW_NOVELTY_GATE.md`  
**Files modified:** none  

---

## References (selected)

1. Chari, A., Ounis, I., & MacAvaney, S. (2025). Lost in Transliteration: Bridging the Script Gap in Neural IR. *SIGIR 2025*, 2900–2905. arXiv:2505.08411.  
2. Gupta, P., Bali, K., Banchs, R. E., Choudhury, M., & Rosso, P. (2014). Query Expansion for Mixed-Script Information Retrieval. *SIGIR ’14*.  
3. Butt, M. U. T., Varanasi, S., & Neumann, G. (2025). Roman Urdu as a Low-Resource Language: Building the First IR Dataset and Baseline. *LowResNLP*.  
4. Butt, U., Varanasi, S., & Neumann, G. (2025). Low-Resource Transliteration for Roman-Urdu and Urdu Using Transformer-Based Models. *LoResMT 2025*.  
5. Khan, A. R., et al. (2020). A Clustering Framework for Lexical Normalization of Roman Urdu. *Natural Language Engineering*.  
6. FIRE 2014 Transliteration Search / DCU participation reports.  
7. ULTRA Program B `PHASE14_FINAL_REPORT.md`; `R2_B0_FAILURE_ANALYSIS.md`; Phase 6–12 controlled experiment reports; Phase 13 scoring CSV.

---

**End of C2 New Novelty Gate.**
