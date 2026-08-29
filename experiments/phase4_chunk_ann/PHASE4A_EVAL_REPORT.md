# Phase 4A evaluation report

**Date:** 24 Aug 2026  
**Eval set:** Phase 2 `dev` + `internal_val`, **n=78** known-item (`source_doc_id`).  
**Not used:** `oracle_train.csv`, H001–H040. SVM not retrained. Index not rebuilt.

Gold is the source article. This is **not** human graded relevance.

---

## Setup verification

| Check | Result |
| --- | --- |
| `phase4a_chunk_index.zip` | present (1884.2 MB) |
| `index_build.json` | present; `n_chunks = chroma_count = 644100` |
| Extract destination | `artifacts/chroma_chunks/` (from existing `CHROMA_DIR`) |
| Collection | `urdu_news_chunks_p4a` count **644100** |
| `_cpu_partial_backup` | not used |
| Script | existing `run_phase4a.py --stage eval` |

Zip layout is `artifacts/chroma_chunks/...`, which matches the script. Only that folder was extracted. CPU backup was left alone.

Smoke test (5 `QTRN` rows: 003, 010, 012, 014, 016): collection loaded, 80 chunks returned, parent `article_id` mapped, Top-5 unique articles, no duplicate parents. QTRN_003 and QTRN_014 recovered the source at rank 1.

Official eval then ran **once**.

---

## Metrics (n=78)

| System | Hit@5 | P@5 | nDCG@5 | MRR |
| --- | ---: | ---: | ---: | ---: |
| Headline | 0.4487 | 0.0897 | 0.4009 | 0.3885 |
| Old Full | 0.2564 | 0.0513 | 0.2203 | 0.2103 |
| Chunk ANN | **0.2821** | **0.0564** | **0.2362** | **0.2309** |

Headline / Old Full match the recorded Phase 3 baselines exactly.

Chunk ANN latency: **0.27 s** mean (embed 0.13 + ANN 0.14 + agg ~0). Faster than Phase 3 top-15 re-rank (4.52 s), slower than Old Full (~0.09 s).

---

## Chunk ANN vs Old Full

| Metric | Old Full | Chunk ANN | Δ |
| --- | ---: | ---: | ---: |
| Hit@5 | 0.2564 | 0.2821 | **+0.0257** |
| P@5 | 0.0513 | 0.0564 | +0.0051 |
| nDCG@5 | 0.2203 | 0.2362 | **+0.0159** |
| MRR | 0.2103 | 0.2309 | +0.0206 |

Per-query **rank** (lower is better; 999 = miss in top-15):

- Chunk ANN better than Old Full: **10**
- Old Full better than Chunk ANN: **6**
- Ties: **62**

Hits@5:

- Newly found by Chunk ANN (Full miss@5): **5** — QTRN_003, QTRN_014, QTRN_054, QTRN_117, QTRN_168
- Lost by Chunk ANN (Full hit@5): **3** — QTRN_046, QTRN_140, QTRN_255
- Found by Chunk ANN while **both** Headline and Old Full miss@5: **1** — **QTRN_054**

---

## Chunk ANN vs Headline

Headline remains the stronger room.

| Metric | Headline | Chunk ANN | Δ |
| --- | ---: | ---: | ---: |
| Hit@5 | 0.4487 | 0.2821 | −0.1666 |
| nDCG@5 | 0.4009 | 0.2362 | −0.1647 |
| MRR | 0.3885 | 0.2309 | −0.1576 |

Rank: Headline better on **21**, Chunk ANN better on **7**, ties **50**.

---

## Oracle ceilings (same max-nDCG@5 rule as Phase 2/3)

MIXED if both nDCG@5 are 0 or margin &lt; 0.05.

| Setting | mean nDCG@5 | vs 0.4327 |
| --- | ---: | --- |
| Headline + Old Full (recorded / reproduced) | **0.4327** | — |
| Headline + Chunk ANN | **0.4375** | **+0.0047** (+1.1%) |
| Headline + Old Full + Chunk ANN | **0.4503** | **+0.0176** (+4.1%) |

Headline + Chunk ANN oracle routing counts: HEADLINE 19, FULL (chunk room) 5, MIXED 54.

The extra three-room number is the mean of `max(headline, full, chunk)` nDCG@5. It is a **ceiling**, not a deployable router.

---

## Does Chunk ANN create meaningful new headroom?

**A little, not a new ceiling that changes the routing story.**

- As a **Full-room replacement**, nDCG@5 rises 0.2203 → 0.2362 on n=78.
- Pre-registered adoption rule also requires Urdu-only nDCG@5 not to fall.
  - Urdu-only (n=46): Full **0.3518** vs Chunk ANN **0.3477** (slight drop).
- Therefore the script’s selected method stays: **`full_one_vector_chroma_111k`**.
- Oracle vs Headline+Full: **+0.0047 nDCG@5**. That is small next to the Headline room (0.4009) and the remaining dual-miss mass.
- One query (QTRN_054) is a true dual-miss recovery. Five Full-miss recoveries vs three Full-hit losses.

Truncation is partly real: corpus-wide chunks do recover some known-items the one-vector Full index misses, and hit@15 for Chunk ANN is 0.3718 vs Full 0.2821. It does **not** overtake Headline, and it does not pass the Urdu-only gate for replacing Full.

---

## Files written (baselines not modified)

| File | Contents |
| --- | --- |
| `phase4a_statistics.json` | full metrics, oracle, latency, selection |
| `CHUNK_ANN_COMPARISON.csv` | Headline / Full / Chunk ANN |
| `ORACLE_CEILING_COMPARISON.csv` | three oracle settings |
| `RECOVERY_ANALYSIS.csv` | Full miss recoveries |
| `eval_query_comparison.csv` | per-query ranks |
| `COMPARISON_BREAKDOWN.csv` | beat / tie / recovery IDs |
| `figures/hit_at_k.png` | hit@5/10/15 |
