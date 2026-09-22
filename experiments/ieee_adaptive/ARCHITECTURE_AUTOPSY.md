# ULTRA v2 Architecture Autopsy

**Date:** 2026-09-22  
**Branch:** `research/roman-urdu-adaptive-retrieval`  
**HEAD:** `3b2e829bf9769d16f9b604ee68d7cc50ce128fa7`  
**Scope:** Document what Program B’s frozen first-stage architecture already contains.  
**TEST accessed:** NO  
**Program A/B modified:** NO

---

## 1. Current architecture (what is already present)

### 1.1 Lexical / sparse

| Component | Role in Program B |
| --- | --- |
| Method-D BM25 | Document-side romanized index; Roman queries search Latinized document tokens |
| Script routing (detector) | ROMAN → Method D; URDU/MIXED → Urdu BM25 (M0 context; v2 Roman KN all detector-ROMAN) |
| Character 3-gram (NG3 / R2-NG3) | Orthographic / partial-string bridge on romanized space |
| Dictionary / NORM / R2-1 fallback romanizer | Closed as insufficient for ROOM Category 1 |
| Phase 7 letter-name acronym expansion | Fired often; **0/23** Quad-23 Top-50 recoveries — UNSUPPORTED |
| Phase 9 Wikipedia title/redirect expansion | Entity-resource lexical CG; small gains; weak on B-class CG misses |

### 1.2 Dense / semantic

| Component | Role |
| --- | --- |
| multilingual-e5-small | Global query/document embeddings; strongest Hit@5 (20/80) |
| Semantic similarity ANN | Recovers some paraphrase/entity cases lexical systems miss |

### 1.3 Hybrid / fusion / cascade

| Component | Role |
| --- | --- |
| Hybrid RRF (BM25+Dense, k=60) | Best deployable Hit@50 pool (40/80) |
| Phase 8 3-way RRF (+NG3) | Dilutes Hybrid — Hit@5/50 worse — UNSUPPORTED |
| Phase 10 / 10b Hybrid-first cascade | No net-positive CG story vs Hybrid |
| Oracle union BM25∪NG3∪Dense | Diagnostic pool membership **49/80** — not a deployable ranker |

### 1.4 Ranking / adaptation (explored, not deployed as winners)

| Component | Status |
| --- | --- |
| Phase 12 reranking | **SKIPPED** — pool not expanded enough |
| C1 query-only adaptive expert routing | **NO-GO** (undetectable) |
| C2a institutional descriptive alias | **NO-GO** (prevalence 6/31) |
| CG entity/name novelty gate | **NO-GO** (heterogeneous + literature-covered) |

---

## 2. What the current architecture already solves

- Exact / near-exact Roman–romanized lexical match (thin Method-D successes).  
- Partial character overlap (some NG3 recoveries).  
- Cross-lingual semantic proximity when e5 embeddings align (Dense Hit@5 = 20/80).  
- Lexical+dense complementarity at pool level (Hybrid Hit@50 = 40/80; BND union = 49/80).  
- Script-routing errors are **not** the Roman KN failure mode (Phase 6: 51/51 detector-ROMAN).

---

## 3. What it cannot solve (structural)

- Gold outside **all** of BM25/NG3/Dense Top-50 for **31/80** queries.  
- Perfect ranking of the existing union cannot exceed **49/80** Hit@5.  
- Fixed Hybrid is **not** the Hit@5 oracle (oracle best-of-3 = 28/80).  
- Always-on third-list fusion and cascade did **not** raise the CG ceiling usefully.  
- Wikipedia title CG and letter-name expansion did **not** close the CG tail.

---

## 4. Representations / mechanisms that are absent

| Absent in Program B stack | Exists in literature? |
| --- | --- |
| Late interaction / multi-vector token MaxSim (ColBERT-class) | **Yes** — SIGIR 2020+; multilingual ColBERT-X / Jina-ColBERT-v2 / mLateOn |
| Learned sparse expansion (SPLADE-class) | **Yes** — SIGIR 2021+ |
| Doc2Query / document-side predicted-query expansion | **Yes** — 2019+; Doc2Query--; dual-index fusion 2025 |
| Multi-view document embeddings from pseudo-queries | **Yes** — ACL/dense multi-rep papers |
| Neural transliterate-train for script gap | **Yes** — Chari SIGIR 2025 (not Urdu-specific) |
| Full BLINK/GENRE entity CG wired into doc search | **Yes** as EL class; Phase 9 is a narrow WP-title instance |
| Agentic / multi-hop retrieval controllers | **Yes** — crowded Adaptive-RAG / SoK space |

**Key autopsy conclusion:** The stack is **missing several mature first-stage families**, but those families are **not scientifically under-addressed**. Their absence is an **engineering gap in Program B**, not an open architectural research void.

---

## 5. Ideas that look new but duplicate prior work

| Apparently new idea | Actually duplicates |
| --- | --- |
| “Token-level / late interaction for RU→Urdu” | ColBERT; ColBERT-X; Jina-ColBERT-v2; mLateOn |
| “Document-side Roman query views” | Doc2Query / multi-view dense docs |
| “Learned expansion sparse bridge” | SPLADE / DeepImpact / uniCOIL family |
| “Knowledge bridges for entities” | Phase 9 + JRC-Names + EL CG (closed novelty) |
| “Intermediate RU meaning then Urdu match” | Multilingual dense + transliteration (Butt 2025; Chari 2025) |
| “Multi-stage CG beyond BM25+Dense” | Standard multi-retriever pipelines; Phase 8/10 already tested fusion variants |
| “Failure-aware adaptive architecture” | C1 closed; Adaptive-RAG crowded |
| “Combine ColBERT + SPLADE + Doc2Query for Urdu” | Combination / domain transfer |

---

## 6. Implication for architecture redesign gate

Any redesign that merely **imports** ColBERT / SPLADE / Doc2Query / transliterate-train / EL into Roman Urdu news is:

**DOMAIN TRANSFER or COMBINATION ONLY**,

unless a **specific unresolved mechanism**—not covered by those families and coherent in the 31 CG misses—can be stated with literature separation.

This autopsy finds **no such under-addressed mechanism** inside the current evidence base.
