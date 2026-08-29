# Phase 12 sealed evaluation

K and U were sealed before retrieval. They are **not** the same protocol.

## K001–K040 — new known-item (ExactSource)

| Metric | Result |
| --- | --- |
| ExactSource Hit@1 | 20/40 = 50.00% |
| ExactSource Hit@5 (primary) | **27/40 = 67.50%** |
| ExactSource Hit@10 | 28/40 = 70.00% |
| ExactSource Hit@50 | 30/40 = 75.00% |

Descriptive detector split (not used for tuning): Urdu-script titles 26/28; ordinary Roman titles 1/12.

This does **not** replace 68/78 and is **not** human Success@5.

Evidence: `experiments/phase12_new_unseen_evaluation/K_RESULTS.md`, `queries_k.csv`, `K_TOP50_RETRIEVAL.csv`, `SEAL.json`

## U001–U040 — naturalistic human evaluation (Success@5)

Human Success@5 = at least one Top-5 document labeled A (relevant) or B (partially relevant). **Not** ExactSource Hit@5.

| Metric | Result |
| --- | --- |
| Human Success@5 (primary) | **23/40 = 57.50%** |
| Conservative P@5 | 0.2050 |
| nDCG@5 | 0.6460 |
| MRR | 0.4542 |

Descriptive script split: URDU 17/18; ROMAN 6/18; MIXED 0/4 (n = 4 is too small for a population rate).

Evidence: `experiments/phase12_human_relevance/PHASE12_HUMAN_RESULTS.md`, `U_QRELS.csv`, `U_PER_QUERY.csv`

## H001–H040 — diagnostic only

Human Success@5 = 25/40 = 62.5% on earlier trap queries. ExactSource Hit@5 is **undefined** (no `source_doc_id`). Not the official unseen usefulness result. Do not combine with U.

Do not retune M0, Method D, or the dictionary on K, U, or H001–H040.
