# PHASE 4B FINAL REPORT

Eval = Phase 2 **dev + internal_val**, **n=78**, known-item `source_doc_id`.  
**H001–H040 unused.** SVM not retrained. No RRF, reranker, or fusion as a system.

Known-item P@5 = 0.2 × Hit@5. This is **not** human graded relevance.  
QTRN queries are **corpus-derived** (title / lead / romanised title). Lexical methods are advantaged on Urdu script. That does not equal 80% P@5 on a human IR task.

Hardware: **CPU only** (12 cores, PyTorch 2.13 CPU). No CUDA.

---

## 1. Baseline reproduction

Exact match to Phase 4A (Δ hit = 0, Δ nDCG = 0).

| System | Hit@5 | P@5 | nDCG@5 | MRR | latency (s) |
| --- | ---: | ---: | ---: | ---: | ---: |
| Headline | 0.4487 | 0.0897 | 0.4009 | 0.3885 | 1.13 |
| Old Full | 0.2564 | 0.0513 | 0.2203 | 0.2103 | 0.18 |
| Chunk ANN | 0.2821 | 0.0564 | 0.2362 | 0.2309 | 0.32 |

---

## 2. BM25

Untuned Okapi BM25 (`k1=1.5`, `b=0.75`) on `combined_text` (Headline + News Text).  
Tokenizer: Urdu unicode letters + `[A-Za-z0-9]`. **No stemming. No roman transliteration.** Not tuned on n=78.

| | Hit@5 | P@5 | nDCG@5 | MRR | latency |
| --- | ---: | ---: | ---: | ---: | ---: |
| all (n=78) | **0.5897** | **0.1179** | **0.5509** | **0.5425** | **0.014 s** |
| Urdu (n=46) | **0.9130** | 0.1826 | 0.8676 | 0.8577 | |
| Roman Urdu (n=23) | **0.0000** | 0.0000 | 0.0000 | 0.0000 | |
| Mixed (n=9) | 0.4444 | 0.0889 | 0.3402 | 0.3179 | |

Index: 111,860 docs, mean length 279 word-tokens, build 127 s, in-memory.

**Roman Urdu:** raw BM25 does **not** help. Query and document do **not** share script tokens. Script mismatch remains.

---

## 3. Long-context

| | |
| --- | --- |
| Pre-registered model | `intfloat/multilingual-e5-small` |
| Context | 512 tokens |
| Dim | 384 |
| Prototype | 400 docs in 174 s → **2.3 docs/s** |
| Extrapolated full corpus | **13.5 hours** on this CPU |
| 4-hour gate | **failed** |
| Full index | **not built** |

No n=78 long-context scores. The encoder was **not** swapped after seeing scores.

---

## 4. Best individual retrieval room

**BM25**, on this known-item set: highest Hit@5 / nDCG@5 / MRR, 80× faster than Headline.

Caveat: Urdu QTRN queries copy title/lead tokens. BM25 is the right *lexical* room, not proof of 80% P@5 under human judgments.

Headline remains the best **dense** room (0.4487 Hit@5). Old Full and Chunk ANN are weaker.

---

## 5. Retrieval diversity

When Headline misses (43/78):

| Room | extra Hit@5 |
| ---: | ---: |
| BM25 | **15** |
| Chunk ANN | 1 |
| Old Full | 1 |
| Long-context | n/a |

Headline hits 4 queries that BM25 misses (mostly the one Roman dense hit + a few mixed/Urdu mismatches).

**All four rooms miss: 28/78.** Of those, **22/23 are Roman Urdu.**

---

## 6. Oracle ceilings (nDCG@5)

| Setting | nDCG@5 |
| --- | ---: |
| Headline + Old Full | 0.4327 |
| Headline + Chunk ANN | 0.4375 |
| Headline + BM25 | **0.6170** |
| All rooms (H+Full+Chunk+BM25) | **0.6170** |

Adding Full or Chunk ANN **does not** raise the Headline+BM25 ceiling.

---

## 7. Urdu (n=46)

| System | Hit@5 | nDCG@5 |
| --- | ---: | ---: |
| Headline | 0.7174 | 0.6487 |
| Old Full | 0.4130 | 0.3518 |
| Chunk ANN | 0.4130 | 0.3477 |
| BM25 | **0.9130** | **0.8676** |

---

## 8. Roman Urdu (n=23)

| System | Hit@5 | nDCG@5 |
| --- | ---: | ---: |
| Headline | 0.0435 | 0.0435 |
| Old Full | 0.0435 | 0.0435 |
| Chunk ANN | 0.0435 | 0.0435 |
| BM25 | **0.0000** | **0.0000** |

Dense methods find **1/23**. BM25 finds **0/23**. This is the barrier to any overall ~80% Hit@5.

---

## 9. Computational cost

| System | query latency | storage |
| --- | ---: | --- |
| Headline | 1.13 s | 0.17 GB cache |
| Old Full | 0.18 s | 3.75 GB Chroma |
| Chunk ANN | 0.32 s | 1.37 GB Chroma |
| BM25 | 0.014 s | RAM inverted index |
| e5-small (not indexed) | — | 0.17 GB vectors if built; 13.5 h CPU embed |

---

## 10. What actually moves toward ~80% Hit@5

On **this** known-item pool, lexical overlap in **Urdu script** is the unused signal. BM25 already has Urdu Hit@5 **91%**. Overall Hit@5 is **59%** because Roman Urdu is almost a complete miss.

The 80% overall number is **not** a MiniLM-truncation problem first. It is a **script / Roman Urdu** problem, plus known-item construction that inflates Urdu BM25.

Truncation (Full / Chunk / 512-token e5) is secondary here.

---

## 11. What should not be pursued next

- Replacing Headline with Old Full or Chunk ANN
- RRF/fusion of Full+Chunk (oracle gain ~0 beyond Headline+BM25)
- SVM retrain before rooms are fixed
- H001–H040
- Ten-model dense sweeps on n=78
- Claiming BM25 “solves IR” (title-derived queries)
- Silent model swap for long-context after the CPU gate failed

---

## 12. Recommended next phase

**One experiment:** Roman Urdu as a first-class retrieval problem.

Pre-register (do not tune on H001–H040):

1. Raw BM25 (done)
2. **Transliterate-then-BM25** vs **BM25 on romanised documents** vs **dense after dictionary transliteration** (already in retrieve.py)
3. Measure Urdu (must not collapse) and Roman separately on n=78
4. Only then consider Headline + BM25 as two rooms for a router

Long-context e5-small full-corpus indexing belongs on **GPU** (T4, as in Phase 4A), as a truncation control, **after** Roman is diagnosed — not as the next CPU job.

STOP. No RRF, reranker, SVM, or frozen test in this phase.
