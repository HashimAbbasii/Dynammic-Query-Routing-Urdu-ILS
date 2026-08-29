# PHASE 4B RESULTS

Eval = Phase 2 **dev + internal_val**, **n=78**, known-item `source_doc_id`.
**H001–H040 unused.** SVM not retrained. No RRF / reranker as a system.
Known-item P@5 = 0.2 × Hit@5. This is not human graded relevance.

## Baseline reproduction

| System | Hit@5 | P@5 | nDCG@5 | MRR | latency (s) |
| --- | ---: | ---: | ---: | ---: | ---: |
| Headline | 0.4487 | 0.0897 | 0.4009 | 0.3885 | 1.1341 |
| Old Full | 0.2564 | 0.0513 | 0.2203 | 0.2103 | 0.1803 |
| Chunk ANN | 0.2821 | 0.0564 | 0.2362 | 0.2309 | 0.3194 |

Reproduction matched Phase 4A: **True**.

## BM25

| Hit@5 | P@5 | nDCG@5 | MRR | latency |
| ---: | ---: | ---: | ---: | ---: |
| 0.5897 | 0.1179 | 0.5509 | 0.5425 | 0.0140 s |

Okapi BM25 k1=1.5 b=0.75 on `combined_text`. No stemming, no roman transliteration, not tuned on n=78.

## Long-context

Full-corpus long-context index **not built** (feasibility gate). See `artifacts/longctx_feasibility.json`.

## Oracle nDCG@5

- headline+old_full: **0.4327**
- headline+chunk_ann: **0.4375**
- headline+bm25: **0.6170**
- all_rooms: **0.6170**

## Unique Hit@5 when Headline misses
{
  "bm25": 15,
  "chunk_ann": 1,
  "old_full": 1,
  "long_context": null
}

