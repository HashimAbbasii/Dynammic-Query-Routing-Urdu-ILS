# Phase 3 results

Eval = Phase 2 **dev + internal_val**, n=**78**. Frozen **H001–H040 not used**. SVM not retrained. One chunk config: 96 tokens, overlap 24, max-sim, re-rank Chroma top-15 only.

Known-item **P@5** = (source in top-5) / 5, so P@5 = 0.2 × hit@5. nDCG@5 is the primary ranking metric (same as Phase 2).

## Selected method

**Keep the current one-vector full Chroma index** (`full_one_vector_chroma_111k`).

Chunk re-rank did not raise nDCG@5 (0.2203 vs 0.2203). Urdu-only nDCG@5 also unchanged (0.3518). Hit@5 rose 2.57 points at 27× latency. Oracle ceiling did not rise. Simpler index wins.

---

## Answers required by the protocol

### 1. Current full-index architecture

One 384-d vector per article: `Headline + ' ' + News Text`, encoded with `paraphrase-multilingual-MiniLM-L12-v2`, **max 128 tokens**, stored in Chroma `urdu_news` (cosine HNSW). Query: same encoder (optional Roman dictionary), `collection.query`. No chunks, no extra Urdu normalizer. Headline room is a separate NumPy cosine scan over titles only. Details: `ARCHITECTURE_AUDIT.md`.

### 2. Main bottleneck

The “full” vector is **not a full-document vector**. **95.35%** of a 4,000-article sample exceed 128 tokens (mean 367, median 295, p99 1,378). The encoder keeps the **title plus the start of the body**. Later facts are dropped. That truncated lead is **less aligned** with the query than the title (mean cos 0.546 vs 0.643; title beats truncated-full on **73%** of eval queries).

Second bottleneck: **known-item vs topical crowding** (other same-topic articles outrank the source). Third: **Roman Urdu** (22/23 both-miss). The SVM is not the object of this phase.

### 3. Was truncation a problem?

**Yes, as representation.** 94.87% of eval source articles exceed 128 tokens. Mean eval source length 421 tokens. The model warning `222 > 128` appears as soon as we tokenize without clipping.

It is **not** the only reason known-item fails: even when the source cosine is high, neighbors can still win (QTRN_054).

### 4. Was one-vector-per-document a problem?

**Partly, as representation; not as measured retrieval.** Best-chunk cosine beats truncated-full on **73%** of eval queries (0.586 vs 0.546). So a single 128-token vector is a lossy summary.

Re-ranking the **same** top-15 with those chunks **does not** improve nDCG@5. Extra hits are documents already sitting in ranks 11–15 (full hit@15 = chunk hit@5 = 0.2821). MRR falls (0.2103 → 0.1998): some true hits are pushed down.

A **corpus-wide** chunk ANN was not built. 11/78 queries have source best-chunk cosine above the 15th Chroma neighbor — a hint, not a result.

### 5. Did chunking help?

**Outcome B, with a small recall footnote.**

| System | hit@5 | nDCG@5 | hit@10 | hit@15 | mean latency |
| --- | --- | --- | --- | --- | --- |
| Full, one vector, 111k ANN | 0.2564 | 0.2203 | 0.2564 | 0.2821 | 0.17 s |
| Chunk 96/24 max-sim re-rank top-15 | 0.2821 | 0.2203 | 0.2821 | 0.2821 | 4.52 s |

Urdu-only: hit@5 0.4130 → 0.4565, nDCG@5 **0.3518 → 0.3518**.

Not adopted: no nDCG gain, worse MRR, 27× slower, not a full ANN.

### 6. Did preprocessing changes help?

**No preprocessing change was promoted.** Document pipeline is still concatenate + encode.

Isolated **query** test E3 (Roman dict on vs off, Roman rows only, **not** for selection): full known-item hits 0 → 1. Too small; dictionary still leaves Latin debris.

### 7. Roman Urdu

See `ROMAN_URDU_ANALYSIS.md`. 23 eval rows, 22 both-miss @5. Dictionary is incomplete, documents are Urdu-script, mean source cosine ~0.39. MIXED on these rows is mostly **script failure**, not a routing target.

### 8–13. Baseline vs “improved” full (eval n=78)

| Metric | Headline | Full (current = selected) | Full + chunk re-rank (not selected) |
| --- | --- | --- | --- |
| P@5 (known-item) | 0.0897 | **0.0513** | 0.0564 |
| nDCG@5 | 0.4009 | **0.2203** | 0.2203 |
| Source hit@5 | 0.4487 | **0.2564** | 0.2821 |
| Source hit@10 | 0.4744 | 0.2564 | 0.2821 |
| Source hit@15 | 0.4744 | 0.2821 | 0.2821 |

Headline still dominates. Depth does **not** explain the full-index gap: hit@5 = hit@10 = 0.2564; only two extra sources appear by rank 15.

### 14. Latency

| System | Mean s / query |
| --- | --- |
| Headline NumPy scan | 0.77 |
| Full Chroma | **0.17** |
| Chunk re-rank (on top of Chroma) | 4.52 |

### 15. Index size

| Artifact | Bytes |
| --- | --- |
| `data/chromadb` | 3.75 GB |
| `data/embeddings.npy` | 164 MB (111,860 × 384 × float32) |
| Headline cache `.npy` | 164 MB |
| Chunk re-rank | no extra index (query-time encode) |

A real 96-token chunk ANN would be several vectors per article (eval sources: median length 355 tokens ≈ 4–5 chunks) → order of **4–5×** embedding store, not measured.

### 16–18. Oracle ceiling (routing headroom on this eval)

Oracle = per query `max(nDCG@5_headline, nDCG@5_full)`, MIXED if both 0 or \|Δ\| < 0.05.

| Setting | Mean oracle nDCG@5 | HEADLINE | FULL | MIXED |
| --- | --- | --- | --- | --- |
| Current indexes | **0.4327** | 22 | 4 | 52 |
| Full replaced by chunk re-rank | 0.4319 | 22 | 5 | 51 |

**Δ ceiling = −0.0009.** Improving full this way **does not** add routing headroom.

Phase 2 reported a ~40.8% known-item P@5 oracle on **H001–H040**. That number is **not** recomputed here. The comparable **eval-78** known-item oracle hit rate is 36/78 = **0.4615** (P@5 = 0.0923) under current indexes; chunk re-rank does not change the story.

### 19. Best retrieval configuration (selected on eval, not on frozen 40)

**Headline cache as-is. Full = current one-vector Chroma.** Chunk size 96/24 is recorded as a negative result, not as production.

### 20. Remaining weaknesses

- 128-token MiniLM cannot represent long Urdu news.
- One vector vs many: theoretically motivated, **unproven** as a full-corpus ANN.
- Known-item metric treats topical neighbors as zeros.
- Roman Urdu queries are not in the same embedding neighborhood as Urdu documents.
- Why/effects templates destroy title overlap.
- Full uniquely helps **1 / 78** queries on this pool — a 3-way router has almost no FULL class on eval.
- Headline brute-force scan is slower than Chroma (0.77 s vs 0.17 s) but more accurate.

### 21. Recommended Phase 4 (do not start it in this step)

1. Keep H001–H040 sealed. Keep the SVM frozen.
2. Do **not** train a 3-class model on Phase 2 MIXED until MIXED is split into “true tie” vs “both failed.”
3. If the goal is a stronger **full** room: pre-register a **corpus chunk ANN** or a **longer-context encoder**, not another top-15 MiniLM re-rank. Budget index size and latency before claiming ceiling gains.
4. Treat Roman as a **separate** preprocessing experiment on internal_val Roman rows only.
5. Optional: human topical judgments on a sample of both-miss Urdu queries to see how much of MIXED is evaluation, not IR.
6. Still no RRF / confidence lights until a full-room change actually moves eval oracle nDCG.

---

## Experiment log

| ID | Hypothesis | Result |
| --- | --- | --- |
| E0 | Record baselines | Headline nDCG@5 0.4009; full 0.2203 |
| E1 | Truncation hurts source cosine | Truncated-full 0.546 vs headline 0.643 vs best chunk 0.586 |
| E2 | Chunk re-rank helps ranking | hit@5 +0.026; nDCG@5 0; latency ×27; **reject** |
| E3 | Roman dict helps (diagnosis) | +1 full hit / 23; **not used for selection** |
