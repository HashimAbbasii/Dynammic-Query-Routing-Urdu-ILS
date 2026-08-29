# Development results (frozen baseline)

Eval pool: Phase 2 **dev + internal_val**, **n=78**, known-item `source_doc_id`.  
**H001–H040 were not used** to produce these numbers.

## Official frozen system

Script-aware lexical retrieval (Phase 5 selected; Phase 6 reproduced):

| Metric | Value |
| --- | ---: |
| Exact-source Hit@5 | **0.8718** (68/78) |
| P@5 | 0.1744 (= 0.2 × Hit@5) |
| nDCG@5 | **0.8107** |
| MRR | **0.797** |

Phase 6 independent rebuild: Hit@5 **0.8718**, Headline Hit@5 **0.4487** (exact match to Phase 4B/5).

## Why this architecture (comparators on the same n=78)

| System | Hit@5 | nDCG@5 | MRR | Source |
| --- | ---: | ---: | ---: | --- |
| Headline MiniLM | 0.4487 | 0.4009 | 0.3885 | Phase 4A/4B |
| Old full Chroma (truncated MiniLM) | 0.2564 | 0.2203 | 0.2103 | Phase 3/4A |
| Chunk ANN | 0.2821 | 0.2362 | 0.2309 | Phase 4A |
| Raw Urdu BM25 (no Roman path) | 0.5897 | 0.5509 | 0.5425 | Phase 4B |
| **Script-aware (frozen)** | **0.8718** | **0.8107** | **0.797** | Phase 5/6 |

Raw BM25 Urdu subset: Hit@5 **0.913** (n=46). Roman subset without Method D: **0.000**. Mixed: **0.4444** (n=9). Method D recovered **22/23** Roman known-items (DEV 13/13, internal_val 9/10).

Headline + script-aware **oracle** Hit@5 = 0.9103. That is **not** a deployed system (Phase 6/7: fusion not justified).

## Decision log — approaches not selected

Evidence only from Phases 3–7. No invented scores.

### 1. MiniLM full index (`urdu_news` Chroma)

Phase 3/4A: Hit@5 **0.2564**, worse than Headline **0.4487**. The “full” vector is truncated at 128 tokens; the title is a better dense query than the truncated body. Not the official path.

### 2. Chunk ANN

Phase 4A corpus chunk index (96/32): Hit@5 **0.2821**. Unique extra Hit@5 when Headline misses: **1** query (Phase 4B). Does not beat BM25 on Urdu and does not fix Roman. Not deployed.

### 3. Long-context e5-small

Phase 4B: pre-registered `intfloat/multilingual-e5-small`, 512 tokens. CPU prototype 2.3 docs/s → **13.5 h** for 111,860 docs. 4-hour gate **failed**. Index **not built**. Encoder was not swapped after seeing scores.

### 4. Raw BM25 for Roman

Phase 4B/5 Method A: Roman Hit@5 **0.000** (0/23). Script mismatch. DEV Method A **0.000**. Rejected for the Roman path.

### 5. Existing dictionary-only transliteration (Method B)

Phase 5 DEV Roman: Hit@5 **0.000**. Audit: 198 exact keys; 22/23 Roman queries still mostly Latin after mapping. Not the Roman path.

### 6. Rule-based Roman retrieval (Method C)

Phase 5 DEV: Hit@5 tied with D at **1.0**, but nDCG@5 **0.8004 vs 0.9331**. Selection rule picked D. Internal_val diagnostic (not used for selection): C **0.6** vs D **0.9**. C is not deployed.

### 7. SVM retraining

Phases 3–7 never retrained the dual-index SVM. Script routing is the Unicode detector (**78/78** on n=78). Phase 7: no architecture experiment justified. SVM stays unused on the official retrieval path.

### 8. RRF

Never implemented as a system. Phase 5 Method E union C∪D on Roman equalled D (22/23). Phase 5 mixed-path union **0.4444 = 0.4444**. Phase 6 Headline union oracle **+3** hits only. Phase 7: do not build fusion for 1–3 complementary cases.

### 9. Score fusion

Same evidence as RRF. Mixed two-view BM25 added nothing. Not deployed.

### 10. Reranker

Phase 6: 4/10 residuals at ranks 6–10 are topical neighbours, not random rank noise. Phase 7: 8/10 residuals already have RELEVANT or PARTIALLY_RELEVANT in Top-5. A reranker would be asked to pick `source_doc_id` among on-topic wires. Not implemented.

---

Development result **87.18% ExactSource Hit@5** is a known-item score on title-derived QTRN queries. It is not a human P@5 claim and is not a held-out H001–H040 result.
