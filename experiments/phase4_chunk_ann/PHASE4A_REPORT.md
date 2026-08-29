# Phase 4A Report — Corpus-Level Chunk ANN

**Project:** Adaptive Dynamic Query Routing for Urdu Information Retrieval  
**Phase:** 4A (proper full-article chunk ANN)  
**Date:** 23 August 2026  
**Status:** **in progress** — baseline and corpus statistics complete; chunk index building; evaluation not yet run.

This report records what Phase 4A is testing, what has already been measured, and what is still blocked. It is **not** a final result paper. Chunk-ANN accuracy, recovery of missed sources, latency, and storage of the finished index are not available until indexing completes.

---

## 1. Research question

Does a **corpus-level chunk ANN** give a meaningfully better Full Article retrieval representation than the current **one truncated vector per article**?

Current Full index:

- Encoder: `paraphrase-multilingual-MiniLM-L12-v2`
- Dimension: 384
- `max_seq_length` = **128**
- Representation: Headline + News Text, **one vector per article**
- Index: Chroma `urdu_news`, cosine, HNSW

Phase 3 showed that this “full article” vector is truncated for most of the corpus, and that **re-ranking chunks of the already retrieved Top-15 articles** is not a real chunk ANN. That re-rank was rejected (source hit@5 0.2564 → 0.2821; nDCG@5 unchanged at 0.2203; latency 0.17 s → 4.52 s).

Phase 4A tests the different design:

```text
Article → overlapping chunks → one embedding per chunk
      → ANN over ALL corpus chunks
      → query → top chunks
      → max aggregation by article → Top-5 articles
```

---

## 2. Frozen rules (this phase)

| Allowed | Not allowed |
| --- | --- |
| New chunk Chroma collection (separate path) | Retrain SVM |
| Same encoder as the Full index | Change Headline index |
| Phase 2 `dev` + `internal_val` (n=78) | Use or tune on H001–H040 |
| One pre-registered chunk config | RRF, confidence routing, new classifier |
| Max chunk-similarity aggregation | Overwrite Phase 0–3 |

H001–H040 remain sealed. Oracle labels are not modified.

**Adoption rule (pre-registered):** adopt chunk ANN only if nDCG@5 rises on n=78 **and** Urdu-only nDCG@5 does not fall.

---

## 3. Step 1 — Baseline reproduction (complete, PASS)

Same evaluation subset as Phase 3: Phase 2 **dev + internal_val**, **n=78**, known-item source article.

| System | k | source hit | P@k | nDCG@k | MRR | mean latency | index size |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Headline | 5 | 0.4487 | 0.0897 | 0.4009 | 0.3885 | 0.83 s | 0.16 GB (cache) |
| Full one-vector | 5 | **0.2564** | **0.0513** | **0.2203** | 0.2103 | 0.09 s | 3.49 GB |
| Full one-vector | 10 | 0.2564 | 0.0256 | 0.2203 | 0.2103 | 0.09 s | 3.49 GB |
| Full one-vector | 15 | 0.2821 | 0.0188 | 0.2270 | 0.2103 | 0.09 s | 3.49 GB |

Δ vs Phase 3 Full @5: hit **0.000**, nDCG **0.000**. Reproduction is exact. Safe to continue.

Files: `baseline_reproduction.csv`, `baseline_reproduction.json`.

This is **known-item** evaluation (did the source article appear?). It is not human relevance labelling.

---

## 4. Step 2 — Full-corpus article lengths (complete)

Tokenizer: the same MiniLM tokenizer. Lengths are **content tokens** (`add_special_tokens=False`). Corpus: **111,860** articles (`data/clean_articles.csv`).

| Statistic | Tokens |
| --- | ---: |
| Minimum | 41 |
| Maximum | 9,769 |
| Mean | 369 |
| Median | 291 |
| 75th percentile | 442 |
| 90th percentile | 661 |
| 95th percentile | 838 |
| 99th percentile | 1,456 |

- Share of articles **> 128 tokens:** **94.42%**
- Share of articles **> 96 tokens:** **98.30%**

Pre-registered 96/32 chunking estimate:

| Quantity | Value |
| --- | ---: |
| Total chunks | **644,100** |
| Mean chunks / article | 5.76 |
| Median chunks / article | 5 |
| 95th percentile chunks / article | 13 |
| Maximum chunks / article | 153 |
| Embedding dimension | 384 |
| Raw embedding storage | **~0.99 GB** |

File: `CORPUS_CHUNK_STATISTICS.md`.

---

## 5. Step 3 — One primary chunking configuration (locked)

Protocol suggestion was **192 tokens / overlap 32**. That configuration was **not used**.

**Reason (tokenizer, before any indexing, not tuned on eval or H001–H040):**

The encoder’s `max_seq_length` is **128 including special tokens**. A 192-token chunk would be silently truncated to 128, so 192/32 would **not** isolate chunking from the same truncation already present in the one-vector Full index.

**Locked primary config:**

| Parameter | Value |
| --- | --- |
| Chunk size | **96** content tokens |
| Overlap | **32** tokens |
| Stride | **64** tokens |
| Encoder | `paraphrase-multilingual-MiniLM-L12-v2` (unchanged) |
| Aggregation | **max** chunk cosine per article |
| Candidates | retrieve **80** chunks, then unique articles |
| ANN | Chroma HNSW, cosine |
| Collection | `urdu_news_chunks_p4a` under `artifacts/chroma_chunks/` |

The live Full collection `urdu_news` is not overwritten.

---

## 6. Steps 4–7 — Chunking, embeddings, ANN, aggregation (in progress)

Each chunk stores `article_id`, `chunk_id`, `chunk_start`, `chunk_end`. Article identity is preserved. Query embedding uses the same encoder. Article score = **maximum chunk similarity**. Output is Top-5 **articles**, not chunks.

**Machine:** CPU only (CUDA unavailable). No FAISS, no standalone hnswlib. Chroma **1.5.9**. Encoding ≈ 18 embeddings/s.

**Index job** (`python run_phase4a.py --stage index`), snapshot 23 Aug 2026 ~21:42 PKT:

| | |
| --- | ---: |
| Articles processed | **3,500 / 111,860** (3.1%) |
| Chunks written | **34,302 / 644,100** (5.3%) |
| Elapsed | **28.5 min** |
| Estimated remaining | **~14–15 hours** |
| Resumable | yes (`artifacts/index_progress.json`) |

Do not run `--stage eval` until Chroma count equals **644,100** and `index_build.json` exists.

---

## 7. Steps 8–13 — Not yet measured

Blocked on the finished index:

| Step | What will be reported | Status |
| --- | --- | --- |
| 8 | P@5, nDCG@5, Recall@5, source hit@5, MRR on n=78 vs current Full | pending |
| 9 | Full misses recovered by Chunk ANN (source found at chunk rank vs article rank) | pending |
| 10 | Headline vs current Full vs Chunk ANN | pending |
| 11 | Query embed time, ANN search, aggregation, total latency vs 0.17 s / 4.52 s | pending |
| 12 | Articles, chunks, raw embeddings, ANN size, metadata, total disk vs ~3.75 GB | pending |
| 13 | Whether one article dominates Top-N chunks | pending |

**Phase 4B will not be started from this phase.**

---

## 8. Comparison already known (without Chunk ANN)

| System | source hit@5 | nDCG@5 | P@5 | latency |
| --- | ---: | ---: | ---: | ---: |
| Headline (unchanged) | **0.4487** | **0.4009** | 0.0897 | ~0.83 s |
| Current Full (one truncated vector) | 0.2564 | 0.2203 | 0.0513 | ~0.09 s |
| Phase 3 Top-15 chunk re-rank (rejected) | 0.2821 | 0.2203 | — | ~4.52 s |
| Phase 4A corpus chunk ANN | — | — | — | — |

Headline remains the stronger room on this known-item set. The open question is whether a real chunk ANN can close that gap as the Full room.

---

## 9. How to finish this experiment

Leave the current index process running, or resume:

```text
python run_phase4a.py --stage index
python run_phase4a.py --stage eval
```

Working directory: `experiments/phase4_chunk_ann`.  
Environment: `KMP_DUPLICATE_LIB_OK=TRUE` (OpenMP duplicate-DLL workaround on this Windows machine).

After eval, this report should be replaced or extended with measured Chunk ANN metrics. Until then, **do not claim** that chunk ANN beats or loses to the current Full index.

---

## 10. Files

| File | Contents |
| --- | --- |
| `PHASE4A_REPORT.md` | This report |
| `README.md` | Protocol and stages |
| `STATUS.md` | Short live status |
| `CORPUS_CHUNK_STATISTICS.md` | Full-corpus token and chunk estimates |
| `baseline_reproduction.csv` | Headline / Full reproduction |
| `run_phase4a.py` | Reproducible pipeline |
| `artifacts/index_progress.json` | Resume cursor |

SVM not retrained. Frozen test set unused. Previous experiment folders not overwritten.
