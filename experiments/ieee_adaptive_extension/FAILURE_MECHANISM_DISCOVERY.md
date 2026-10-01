# FAILURE MECHANISM DISCOVERY

## Phase 1 — Why 87.18% vs Hard Roman Urdu Populations

**Date:** 2026-09-22  
**Branch:** `research/roman-urdu-novelty-extension`  
**Nature:** Diagnostic + novelty discovery only — **no method implementation**  
**TEST accessed:** NO  
**Program A/B modified:** NO  

---

## 0. Repository safety

| Item | Value |
| --- | --- |
| Branch | `research/roman-urdu-novelty-extension` |
| Base | Same line as `research/roman-urdu-adaptive-retrieval` @ novelty-check commit (see git) |
| Working tree | New `experiments/ieee_adaptive_extension/` (+ prior untracked adaptive artifacts may exist on related branches) |
| Program A | Untouched |
| Program B | Untouched |
| TEST | Sealed; query contents not opened (`benchmark/test/README.md` + seal metadata only) |

---

## 1. Evaluation populations reconstructed

| ID | Population | n | Query source | Gold | Protocol | Tuning use | Future model-dev suitability |
| --- | --- | ---: | --- | --- | --- | --- | --- |
| **A** | Phase 2 dev + internal_val QTRN | **78** | Title-derived / template (`creation_method`: title_roman 23, title_short 10, why/how/lead/effects, mixed_short 9) | ExactSource `source_doc_id` | ExactSource Hit@5 | Used to select Method D / freeze M0 | **Burned for method selection** — do not retune |
| **B** | K001–K040 | **40** | Human title-like shorten **or** “ordinary Roman Urdu of headline” | ExactSource | ExactSource Hit@5 | Sealed after freeze; not for retuning | Official unseen KN for Program A |
| **C** | U001–U040 | **40** | Human naturalistic | **None** | Human Success@5 | Sealed; not ExactSource | Usefulness only — not ExactSource Hit@5 |
| **D** | Program B Roman KN TRAIN+DEV | **80** | Naturalistic Roman; writers W1=51, LLM1=29 | ExactSource | Hit@k / MRR | TRAIN/DEV for Program B phases; TEST sealed unused | Suitable for diagnostics; not for burning into Program A |

**Do not average** 87.18%, 67.50%, 57.50%, 25%, etc.

---

## 2. What the 87.18% result represents

Official: ExactSource Hit@5 = **68/78** on Population A (`DEVELOPMENT_RESULTS.md`).

### Composition of A

| Script | n | Role in 87% |
| --- | ---: | --- |
| URDU | 46 | High query–headline token coverage (mean cov **0.70**; **80%** of Urdu queries have cov≥0.5). Urdu-subset Hit@5 ≈ **0.913** (development comparator). |
| ROMAN | 23 | **All** `creation_method=title_roman`. Method D Hit@5 = **22/23**. |
| MIXED | 9 | `mixed_short`; mixed path weaker historically. |

### Critical Phase 5 fact (repository evidence)

> QTRN Roman queries are Phase 2 **`title_roman`** strings (dictionary reverse + naive character romanization), **not naturalistic chat Roman Urdu**. Method D is the document-side counterpart of that same romanization family.

Therefore Method D’s 22/23 success is **matched romanization by construction**, not proof of robustness to ordinary Roman Urdu.

**H1 (Urdu-token overlap):** Supported for **Urdu** subset of A (high coverage). **Not** the explanation of Roman successes (Roman–Urdu-headline token cov ≈ 0 for A/K/D Roman alike).

**H10 (benchmark construction):** **Supported** as the primary explanation of the 87% vs hard Roman gap.

---

## 3. What makes hard queries different

### Population B (K) — 67.50% overall

| Slice | n | Lexical cov vs Urdu headline | Retrieval note |
| --- | ---: | --- | --- |
| URDU | 28 | mean cov **0.99**; 100% cov≥0.5 | Title-like Urdu → easy ExactSource for M0 (**26/28** per Program A narrative) |
| ROMAN | 12 | cov≈0 vs Urdu headline | “Ordinary Roman Urdu of headline” ≠ `title_roman` → Method D **~1/12** |

Overall K drop vs 87% is largely **Roman ordinary orthography + fewer easy Urdu title queries in the mix**, not a single new neural failure.

### Population C (U) — 57.50% Success@5

Different task: **no gold**, human usefulness, 18 Roman / 18 Urdu / 4 Mixed. Not comparable to ExactSource Hit@5.

### Population D (Program B) — Dense 25% Hit@5

| Property | Value |
| --- | --- |
| Script | 80/80 ROMAN |
| headline_overlap meta ≈0 | 78/80 |
| Method-D Hit@5 | 5/80 |
| Dense Hit@5 | 20/80 |
| BND Top-50 ceiling | 49/80 |
| Oracle best-of-3 Hit@5 | 28/80 |

Naturalistic Roman questions (event/factoid/topical), not title_roman strings.

---

## 4. Hypothesis tests (summary)

| H | Result |
| --- | --- |
| H1 higher lexical overlap (Urdu tokens) | **Yes for A-Urdu vs hard Roman**; Roman always ~0 vs Urdu headlines |
| H2 easier surface forms | **Yes** — title_short / title_roman / high-overlap Urdu |
| H3 fewer severe Romanization variations | **Yes** — A-Roman uses system `title_roman`, not chat orthography |
| H4 exact/near-exact lexical matching | **Yes** for Urdu title-like; **matched roman BM25** for title_roman |
| H5 greater semantic distance on hard sets | **Plausible** for D (paraphrase/entity CG tail); Dense still only 20/80 |
| H6 entities/acronyms/English phrases | Present in D CG tail (prior C2a/C3); not the main 87% explanation |
| H7 vocabulary mismatch | Yes on D dual-misses (Phase 11) |
| H8 phenomena not captured by RU normalization | **Yes** — naturalistic orthography ≠ char-table romanization |
| H9 CG vs ranking | On D: SUCCESS 28, RANKING 21, CG-dominant residual **31** (prior decomposition) |
| H10 benchmark construction | **Primary supported explanation of 87% vs hard Roman** |

---

## 5. Failure levels on Population D (n=80)

From Phase 13 + prior FD/C2A (reused, not modified):

| Level | Approx. n | Meaning |
| --- | ---: | --- |
| SUCCESS (any expert Hit@5) | 28 | — |
| LEVEL 4 ranking | 21 | In BND Top-50, not Top-5 |
| LEVEL 3 CG (+ often LEVEL 2 bridge) | ~31 | Outside BND Top-50 |
| LEVEL 1/2 script-ortho (C2a D) | 3 | Script of same English name |

**Dominant bottleneck on hard Roman KN (D):**  
**LEVEL 2 bridging** (naturalistic Roman ↔ Urdu / system-roman space) **manifesting as LEVEL 3 candidate-generation failure**, with a secondary LEVEL 4 ranking band (21).

This does **not** reduce to “just repeat 31/80”: the deeper mechanism behind many of those 31—and behind Method D’s collapse—is the **orthography / romanization-space mismatch** revealed by comparing A-Roman (`title_roman`) to D/K-Roman (naturalistic / ordinary).

---

## 6. The “missing bridge”

**What Roman Urdu queries contain that the Method D architecture systematically lacks for naturalistic text:**

> User-conventional Roman Urdu spellings and semantic paraphrases that are **not** the Phase-2 character-table `title_roman` forms shared with the romanized BM25 index.

| Bridge candidate | Current system lacks? | Explains many failures? | Literature already? | Novel method under §15? |
| --- | --- | --- | --- | --- |
| Matched char-table romanization | No (Method D has it) | Explains A success | Phase 5 | No — already implemented |
| Naturalistic spelling variants / phonetic | Partially (NORM/NG3 weak) | Yes for lexical RU | Gupta; TALLIP; FIRE | **Rejected** (§15 transliteration/phonetic/spelling) |
| Semantic cross-lingual embedding | Dense present | Partial (20/80) | Multilingual dense; Chari | **Rejected** (embeddings / domain transfer) |
| Entity/alias KB | Phase 9 tried | Partial / heterogeneous | JRC-Names; EL | **Rejected** (closed CG gate) |
| Multi-hypothesis transliteration lattice | Not as full lattice IR | Would target mismatch | Lattice translit; MSIR QE | **Rejected** (§15 + prior art) |

---

## 7. Literature findings (mechanism-targeted)

| Mechanism | Closest work | Gap? |
| --- | --- | --- |
| Mixed-script + spelling variation | Gupta et al. SIGIR 2014 | Occupies |
| Phonetic QE for transliterated search | Prabhakar et al. ACM TALLIP 2021; FIRE MSIR | Occupies |
| Neural script gap / transliterate-train | Chari et al. SIGIR 2025 | Occupies |
| Roman Urdu IR dataset/baseline | Butt et al. 2025 LowResNLP | Occupies |
| Matched document romanization | ULTRA Phase 5 Method D | Already in-program |

**No literature gap remains that is both (a) the causal 87%-vs-hard mechanism and (b) free of §15 automatic rejects.**

---

## 8. Novelty candidates

See `NOVELTY_CANDIDATE_MATRIX.csv`.

All candidates **REJECT** (fake novelty / closed direction / not a method).

**Novelty confidence for a new algorithm:** **LOW** (none survive).

---

## 9. 80% feasibility (theoretical only)

| Quantity | Value |
| --- | ---: |
| Target | 64/80 |
| Dense now | 20/80 |
| Need | +44 Hit@5 |
| Ranking headroom (BND) | ≤21 |
| BND CG ceiling | 49/80 |
| Gap beyond ceiling | ≥15 unique new CG recoveries **minimum** |

Solving naturalistic Roman bridging **might** raise coverage above 49 **in principle** (unverified). Under this gate it is **not** authorized as a novel mechanism. Therefore: **insufficient as a novelty-justified path toward ~80%.**

Language: **theoretically**, coverage expansion is required; **unverified** until experiment; **not justified** here as novel research implementation.

---

## 10. Final gate

### **NO-GO**

> No sufficiently defensible novel mechanism was identified from the investigated failure mechanisms.

The scientifically important positive outcome of this phase is **diagnostic**:

**87.18% is largely title-like Urdu + matched `title_roman`→Method D; harder Roman populations use ordinary/naturalistic Roman orthography and (for U) a different metric.**

That clue must inform honest interpretation of Program A—not a new algorithm claim.

---

## Artifacts

| File | Role |
| --- | --- |
| `FAILURE_MECHANISM_DISCOVERY.md` | This report |
| `FAILURE_MECHANISM_PER_QUERY.csv` | Per-query features (no TEST) |
| `NOVELTY_CANDIDATE_MATRIX.csv` | Novelty records |
| `NEXT_RESEARCH_GATE.md` | GO/NO-GO + next/forbidden steps |
| `POPULATION_SUMMARY.json` | Numeric summaries |
| `run_phase1_discovery.py` | Reproduction script |

---

**End of Phase 1 discovery.**
