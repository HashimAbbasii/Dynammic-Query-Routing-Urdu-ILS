# Phase 1 diagnosis — why SVM loses P@5 to word count

**Experiment ID:** phase1-forensic-heldout40  
**Inputs:** `validate\dual_index_routing\labels\heldout_routed_p5.json`, `validate\dual_index_routing\labels\heldout_classification.json`  
**No model change. No re-retrieval.** Oracle labels here are diagnostic only (same 40 judgments). Do not train on them.

## Oracle rule (fixed before counting)

- Retrieval-optimal index = higher **P@5**.
- If P@5 is tied, break with **nDCG@5**.
- If both tie → **TIE** (routing does not matter for that query).

## Frozen means (recomputed from the same JSON)

| System | P@5 |
| --- | ---: |
| Always headline / θ=150 | 0.3500 |
| Always full | 0.3425 |
| Word count ≥ 6 | 0.3650 |
| SVM (deployed) | 0.3300 |
| Oracle (pick better index per query) | 0.4075 |

Oracle is only +4.2 points over word count, and +7.7 over SVM. The ceiling on this 40-query set is low because many queries are weak on **both** indexes.

## Who matches the retrieval-optimal index?

| Router | Agree with oracle | Agree with protocol gold |
| --- | ---: | ---: |
| SVM | 12/31 (ties excluded from agree count; ties=9) | 24/40 |
| Word count | 16/31 | 8/40 |
| Protocol gold vs oracle | disagrees on **20/40** | — |

P@5 head-to-head SVM vs word count: SVM better **4**, word count better **7**, tie **29**.

Oracle index split: headline **19**, full **12**, tie **9**.

## Failure categories (multi-label; a query can sit in more than one)

| Code | Meaning | n |
| --- | --- | ---: |
| E | Protocol gold ≠ retrieval-optimal index | 20 |
| A | SVM did not pick the retrieval-optimal index | 19 |
| B | Word-count P@5 > SVM P@5 on that query | 7 |
| C | SVM matches protocol gold but P@5 ≤ 0.2 | 12 |
| D | Headline and full P@5 tied | 9 |

Primary tag counts: `{'E_gold_vs_oracle': 20, 'C_gold_correct_retrieval_poor': 7, 'OK_svm_matches_oracle': 3, 'D_indexes_tied_p5': 4, 'A_svm_misses_oracle': 6}`.

## Diagnosis (answer to the Phase 1 question)

**The main bottleneck is not “SVM accuracy vs protocol labels.”** SVM already beats word count 60% vs 20% on those labels. The P@5 loss comes from three stacked facts:

1. **Label–index mismatch (E, n=20).** “Headline enough vs need the article” is not the same objective as “which index returns better P@5.” Protocol gold disagrees with the retrieval-optimal index on 20/40 queries. Training harder on those gold labels cannot be assumed to raise P@5.

2. **When SVM follows gold LONG on cue-short queries, the full-article index often hurts.** Examples: H001 (headline P@5 0.50 vs full 0.30), H002 (0.80 vs 0.00). SVM is “right” on the protocol and **wrong** for retrieval. Word count stays in the headline room and wins P@5.

3. **Index quality / evaluation (C and D).** Several queries are near-zero on both rooms (H007, H011, H015, H016, H020, H026, H033, H034). Routing cannot invent relevant documents. n=40 plus 0.5 graded labels is also a noisy ceiling: oracle P@5 is only 0.4075.

**Ranking of causes on this frozen set**

1. Routing **labels** (intuition ≠ retrieval-optimal) — dominant for the SVM vs word-count P@5 gap.  
2. **Full-article index noise** on short causal queries — dominant for Category A when SVM picks FULL.  
3. **Evaluation set** (small, many dead queries, headline often already good) — limits any router.  
4. SVM **classifier** vs word count — *not* the P@5 bottleneck; it is the classification winner.

Do not retrain the SVM next. Next legal step is Phase 2 **only after** a train/dev split that is **not** these 40 test judgments.
