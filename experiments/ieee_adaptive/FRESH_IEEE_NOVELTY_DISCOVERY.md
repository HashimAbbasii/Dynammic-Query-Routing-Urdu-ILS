# Fresh IEEE Novelty Discovery

**Search date:** 2026-09-22  
**Branch:** `research/roman-urdu-adaptive-retrieval`  
**HEAD:** `3b2e829bf9769d16f9b604ee68d7cc50ce128fa7`  
**Decision:** **NO-GO**

**Scope:** Broad AI/IR research-problem discovery for a future IEEE journal contribution for an MS AI researcher.  
**Explicitly excluded revitalizations:** C1 adaptive routing, C2a institutional-alias CG, C3 Program-B residue methods, Program A/B modification.

This gate asks whether a problem **deserves** research — not whether something can be forced into a paper.

---

## 0. Search Protocol

| Item | Detail |
| --- | --- |
| Engines / sources | Cursor WebSearch over ACL Anthology, ACM/SIGIR, arXiv HTML, MLR proceedings, reputable survey pages |
| Emphasis | 2023–2026 + foundational classics where needed |
| Queries (representative) | `RAG hallucination retrieval faithfulness…`; `agentic retrieval… Adaptive-RAG…`; `long-context RAG vs LC LLM LaRA…`; `LLM-as-judge relevance assessment limitations…`; `query variation robustness transformer…`; `citation faithfulness post-rationalization VeriCite RECLAIM…` |
| Non-fabrication | Citations below are from retrieved primary/abstract pages; absence from search ≠ proof of non-existence |

**Limitation:** This is a **breadth discovery**, not a months-long deep dive into one subfield. Breadth can miss niche gaps; it is still enough to reject saturated/combination candidates.

---

## 1. Repository State

| Field | Value |
| --- | --- |
| Branch | `research/roman-urdu-adaptive-retrieval` |
| HEAD | `3b2e829bf9769d16f9b604ee68d7cc50ce128fa7` |
| Working tree | Untracked `experiments/ieee_adaptive/` only |
| Program A modified | **No** |
| Program B modified | **No** |

## 2. TEST Integrity

| Field | Value |
| --- | --- |
| TEST accessed | **No** |
| TEST content inspected | **No** |
| Statement | `TEST_CONTENT_ACCESSED = FALSE` |

---

## 3. Research Areas Investigated (12)

1. RAG hallucination / citation attribution / faithfulness  
2. Agentic / adaptive multi-step retrieval (“when to retrieve”)  
3. Long-context LLMs vs RAG routing  
4. IR evaluation methodology / LLM-as-judge qrels  
5. Query-variation / noise / adversarial robustness  
6. First-stage semantic retrieval & vocabulary mismatch (general)  
7. Conversational / multi-turn search (high-level)  
8. Multimodal retrieval (high-level saturation check)  
9. Resource-constrained / efficient retrieval routing  
10. Explainable / trustworthy attributed generation  
11. Low-resource & multilingual IR (excluding closed Urdu method paths)  
12. Retrieval failure diagnosis / error taxonomies (RAG/IR)

---

## 4. Candidate Catalog (14)

### CAND-01 — Citation faithfulness methods (beyond correctness)

| Field | Content |
| --- | --- |
| Area | Trustworthy RAG / attribution |
| Problem | Citations may be correct (entailed) but unfaithful (post-rationalized) |
| Why it matters | Misplaced user trust |
| Existing | ALCE; AttributionBench; CiteEval; Wallat et al. “Correctness ≠ Faithfulness”; **RECLAIM (NAACL Findings 2025)**; **VeriCite (2025)** |
| Limitation of “gap claim” | Phenomenon identified **and** 2025 methods already target verification / interleaved cite-claim generation |
| RQ (if pursued) | Improve faithfulness under black-box constraints |
| Novelty risk | **HIGH** — active, occupied |
| Evidence class | Literature-saturated for “new problem discovery” |
| Gate | **NO-GO** |

### CAND-02 — Standardized counterfactual faithfulness benchmark

| Field | Content |
| --- | --- |
| Area | Evaluation methodology |
| Problem | Faithfulness probes exist but are paper-specific |
| Existing | Wallat et al. adversarial planting; CiteBench/CiteEval; AttributionBench |
| Gap claim weakness | Extending their probes is incremental evaluation engineering; CiteEval already principle-driven |
| Novelty risk | HIGH–MEDIUM |
| Feasibility | Annotation-heavy |
| Evidence class | Weak / incremental |
| Gate | **NO-GO** |

### CAND-03 — Agentic RAG stopping / mid-reasoning retrieval

| Field | Content |
| --- | --- |
| Area | Agentic retrieval |
| Problem | When to retrieve during long reasoning chains |
| Existing | Adaptive-RAG; Self-RAG; IRCoT/FLARE; SoK Agentic RAG; “When to Retrieve During Reasoning” (2026 preprint lineage) |
| Limitation | Hot lab-competitive space; high compute |
| Novelty risk | **HIGH** |
| Evidence class | Literature-saturated for MS entry |
| Gate | **NO-GO** |

### CAND-04 — Query-complexity routing among no/single/multi retrieval

| Field | Content |
| --- | --- |
| Area | Adaptive RAG |
| Problem | One strategy unfit for all complexities |
| Existing | Adaptive-RAG (NAACL 2024) and follow-ons |
| Why reject | Directly solved as published framework; also overlaps closed C1 spirit (routing) |
| Gate | **NO-GO** |

### CAND-05 — RAG vs long-context routing under cost

| Field | Content |
| --- | --- |
| Area | LC vs RAG |
| Problem | When to retrieve vs stuff context |
| Existing | Lost-in-the-middle; LaRA (2025); hybrid RAG–LC studies |
| Exact limitation already stated by LaRA | “No silver bullet” — interplay of model/task/length |
| Novelty risk | HIGH (combination/routing) |
| Gate | **NO-GO** |

### CAND-06 — LLM-as-judge IR evaluation reliability

| Field | Content |
| --- | --- |
| Area | Evaluation methodology |
| Problem | LLM qrels distort top-system ranking / significance |
| Existing | SIGIR 2025 limitations papers; “LLMs can be fooled…”; “still can’t replace human…” |
| Gap | Building another judge or hybrid protocol is active and contested; hard to claim journal novelty without deep TREC-scale studies |
| Feasibility | Needs large run pools / human labels — heavy for MS |
| Evidence class | Literature-saturated / unrealistic for solo MS depth |
| Gate | **NO-GO** |

### CAND-07 — Query-variation robustness of modern dense/LLM retrievers

| Field | Content |
| --- | --- |
| Area | Retrieval robustness |
| Problem | Semantic-preserving query noise drops effectiveness |
| Existing | Penha et al. variation generators; EMNLP Findings 2024 reproduction; AdvBEIR; typo-aware CharacterBERT / Dual Self-Teaching |
| Exact limitation already studied | Typo robustness ≠ other variation types; focusing one type can hurt others |
| Novelty risk | HIGH |
| Gate | **NO-GO** |

### CAND-08 — First-stage semantic models for vocabulary mismatch

| Field | Content |
| --- | --- |
| Area | Classical IR modernization |
| Problem | BM25 blocks relevant docs from rerankers |
| Existing | Guo et al. TOIS comprehensive review; decades of QE/expansion/dense first-stage |
| Novelty risk | **HIGH** — foundational & reviewed |
| Gate | **NO-GO** |

### CAND-09 — Resource-constrained sparse/dense selection

| Field | Content |
| --- | --- |
| Area | Efficient retrieval |
| Problem | Dense cost vs sparse adequacy |
| Existing | Arabzadeh CIKM 2021; LiteGator; MoR |
| Overlap with C1 | Conceptually related to expert selection — **closed spirit** |
| Gate | **NO-GO** |

### CAND-10 — Multimodal retrieval for noisy OCR / screenshots

| Field | Content |
| --- | --- |
| Area | Multimodal IR |
| Problem | Retrieve under OCR noise |
| Existing | Large multimodal retrieval literature (CLIP-class, document VQA/IR tracks) |
| Evidence in this search | Not a clear under-addressed MS-scale gap without domain partnership |
| Novelty risk | HIGH |
| Evidence class | Insufficient evidence (from this gate) + likely saturated |
| Gate | **NO-GO** |

### CAND-11 — Conversational search state tracking failures

| Field | Content |
| --- | --- |
| Area | Conversational IR |
| Problem | Topic shift / context carryover errors |
| Existing | TREC CAsT and large conversational IR literature |
| Novelty risk | HIGH |
| Gate | **NO-GO** |

### CAND-12 — RAG error taxonomy → automatic repair controller

| Field | Content |
| --- | --- |
| Area | Failure diagnosis |
| Problem | Map errors to interventions |
| Existing | RAG error taxonomy papers (2025); stage-wise classifiers |
| Why reject | Taxonomy+controller without new mechanism = engineering pipeline; overlaps agentic RAG |
| Gate | **NO-GO** |

### CAND-13 — Apply any modern RAG method to Urdu/Roman Urdu

| Field | Content |
| --- | --- |
| Area | Low-resource application |
| Problem | Domain transfer |
| Why reject | Explicit weak novelty (“existing X + language Y”); C3 already closed Program-B residues |
| Gate | **NO-GO** |

### CAND-14 — Package Program B as IEEE empirical paper (not new method)

| Field | Content |
| --- | --- |
| Area | Empirical systems / multilingual IR |
| Problem | Reporting frozen multi-representation Roman→Urdu news results |
| Contribution type | Evidence packaging, **not new technical mechanism discovery** |
| Why out of scope here | This discovery gate seeks a **new research problem/method**, not a write-up plan for completed Program B |
| Note | May be a legitimate *publication strategy* elsewhere — **not** a NEW NOVELTY CANDIDATE under this gate’s definition |
| Gate | **Out of scope / not a discovery hit** |

---

## 5. Novelty Matrix (condensed)

| Candidate | Problem | Existing Work | Exact Limitation | Specific Gap | Proposed Mechanism | Closest Paper | Overlap | Novelty Evidence | Main Risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CAND-01 | Unfaithful citations | ALCE; CiteEval; RECLAIM; VeriCite | Correctness≠faithfulness known | Mitigation methods already 2025 | Cite-claim / verify pipelines | Wallat et al.; RECLAIM | High | Weak | Saturation |
| CAND-02 | Faithfulness eval std. | AttributionBench; CiteEval | Auto-eval hard (~80% F1) | Incremental benchmark extension | Counterfactual suite | AttributionBench | High | Weak | Incremental |
| CAND-03 | Mid-reason retrieve | Adaptive-RAG; SoK; reasoning RAG | Temporal mismatch known | Occupied by concurrent work | Triggers at step granularity | Adaptive-RAG; “When to Retrieve…” | High | Weak | Compute/competition |
| CAND-04 | Complexity routing | Adaptive-RAG | Over/under retrieve | Published solution | Complexity classifier | Adaptive-RAG | Very high | None | Already solved |
| CAND-05 | RAG vs LC | LaRA; hybrid studies | No universal winner | Benchmarked | Router | LaRA | High | None | Combination |
| CAND-06 | LLM qrels fairness | SIGIR 2025 critiques | Top-system unfairness shown | Contested space | Hybrid human–LLM | Limitations of LLM assessments | High | Weak | Scale/annotation |
| CAND-07 | Query noise robustness | Penha; EMNLP’24 Findings; AdvBEIR | ~20% drops; typo≠all variants | Known open engineering | Multi-variation training | EMNLP Findings 2024 | High | Weak | Saturated |
| CAND-08 | First-stage semantic | TOIS review | Vocab mismatch classic | Decades of work | Dense first-stage | Guo et al. TOIS | Very high | None | Classic |
| CAND-09 | Cost routing | Arabzadeh; LiteGator; MoR | Latency/utility | Known | Classifier | Arabzadeh 2021 | High | None | C1-adjacent |
| CAND-10 | Multimodal noisy docs | Multimodal IR lit | OCR noise | Unclear MS gap | Multimodal encoder | CLIP-class IR | High | Insufficient | Domain |
| CAND-11 | Conversational drift | TREC CAsT etc. | Context errors | Mature area | State tracking | CAsT literature | High | Weak | Saturated |
| CAND-12 | Error→repair | RAG taxonomies 2025 | Stage errors | Pipeline engineering | Controller | RAG error taxonomy | High | Weak | Engineering |
| CAND-13 | Urdu apply-X | Butt; Chari; Program B | Domain transfer | Not a mechanism | Domain apply | Many | Total | None | Weak novelty |
| CAND-14 | Write Program B | Program B freeze | N/A | N/A | Empirical report | Empirical IR papers | N/A | N/A | Out of scope |

---

## 6. Rejected Directions (summary)

All 14 candidates fail at least one hard filter:

- **Literature already formulates and/or mitigates** the apparent phenomenon (especially RAG faithfulness, adaptive/agentic retrieval, LC–RAG, query robustness, LLM judges).  
- **Combination / routing / “apply to Urdu”** novelty (explicitly forbidden).  
- **C1-adjacent** efficiency/expert selection.  
- **Unrealistic MS resources** (TREC-scale judge studies; frontier agentic systems).  
- **Insufficient evidence** from this breadth search to claim a specific under-addressed Z.

Negative evidence was sought deliberately (e.g., faithfulness “gap” checked against RECLAIM/VeriCite 2025 — **gap occupied**).

---

## 7. Strongest Surviving Candidate

**NONE.**

Do not manufacture one.

---

## 8. Exact Research Gap

**No specific, verifiable, MS-feasible, IEEE-journal-scale methodological gap survived this discovery scope.**

What *is* true:

- Many IR/RAG problems remain imperfectly solved in practice.  
- That does **not** imply an unexplored research *formulation* ready for a solo MS journal contribution within the investigated areas.  
- Several “gaps” from 2023–2024 were **already attacked by 2025 methods**.

---

## 9. Closest Literature (anchors)

1. Wallat et al. — Correctness ≠ Faithfulness in RAG attributions (post-rationalization).  
2. RECLAIM — interleaved reference–claim generation (Findings NAACL 2025).  
3. VeriCite — verified citation pipeline (2025).  
4. Adaptive-RAG — complexity-adaptive retrieval strategies (NAACL 2024).  
5. LaRA — RAG vs long-context benchmarking (2025).  
6. SIGIR 2025 — limitations of LLM relevance assessments.  
7. Penha et al. / EMNLP Findings 2024 — query variation robustness.  
8. Guo et al. — Semantic models for first-stage retrieval (TOIS).  
9. SoK / surveys — Agentic RAG taxonomies and open directions (crowded).  

---

## 10. Why Different From C1 / C2a / C3

| Prior gate | This discovery |
| --- | --- |
| C1 | Routing among frozen RU experts — **not revisited** |
| C2a | Institutional alias prevalence on Program B — **not revisited** |
| C3 | Program B residue mechanisms — **not reinterpreted as positive** |
| This gate | Broad AI/IR space beyond Urdu defaults; still **no survivor** |

A clean negative across both narrow (C3) and broad (this) scopes is consistent: **forcing a method is not justified**.

---

## 11. Feasibility (N/A — no survivor)

| Dimension | Status |
| --- | --- |
| Dataset | N/A |
| Compute | N/A |
| Annotation | N/A |
| Timeline | N/A |
| Evaluation | N/A |

---

## 12. FINAL DECISION

# **NO-GO**

---

## 13. NEXT STEP

**STOP.**

Do not invent C5/C6 to continue this discovery chain.  
Do not implement RAG faithfulness / agentic / LC-routing / LLM-judge / robustness projects under a claim of “discovered novelty” from this gate.

If research continues later, it must start from a **new, deep specialization** chosen independently (advisor-driven topic selection with a focused literature deep-dive), not from another breadth “find something publishable” sweep.

---

## 14. Scientific Interpretation

This NO-GO does **not** mean “IR is finished.”  
It means: within a serious breadth review of currently hot and classical IR/RAG areas, **no candidate simultaneously satisfied** specificity, literature separation, MS feasibility, and IEEE journal methodological depth — without collapsing into combination novelty, saturated threads, or revitalizing closed Program C ideas.

A clean stop is preferable to a weak paper.

---

## 15. Artifact Hashes

| File | Role |
| --- | --- |
| `experiments/ieee_adaptive/FRESH_IEEE_NOVELTY_DISCOVERY.md` | This report |
| `experiments/ieee_adaptive/FRESH_IEEE_CANDIDATE_MATRIX.csv` | Compact candidate table |

---

**End of Fresh IEEE Novelty Discovery.**
