# Phase 11 M0–M4 ablation results

Query-side ROMAN transforms only. Phase 9 unmodified. H001–H040 not loaded. H041+ not created.

## Preflight

Corpus SHA-256 match: **True**. Dictionary SHA match: **True**. k1/b 1.5/0.75. Routing unchanged.

## Comparison

| Model | n=78 Hit@5 | Roman Train Hit@5 | Roman Train nDCG@5 | MRR | Gate | Decision |
| --- | --- | --- | --- | --- | --- | --- |
| M0 | 68/78 = 0.8718 | 0.9531 | 0.8960 | 0.8807 | PASS | CONTROL |
| M1 | 68/78 = 0.8718 | 0.9531 | 0.8940 | 0.8781 | PASS | PASS |
| M2 | 68/78 = 0.8718 | 0.9531 | 0.8940 | 0.8781 | PASS | PASS |
| M3 | 68/78 = 0.8718 | 0.9531 | 0.8940 | 0.8781 | PASS | PASS |
| M4 | 68/78 = 0.8718 | 0.9531 | 0.8940 | 0.8781 | PASS | PASS |

## M0 reproduction

M0 n=78 hits = 68. Required 68. **OK**.

## Winner (among M1–M4 that passed both gates)

**M1** (Hit@5 tied with M2–M4; nDCG@5 tied among M1–M4; simplest model).

Roman train ExactSource Hit@5 did **not** increase vs M0 (still **61/64 = 0.9531**). M1–M4 nDCG@5/MRR are slightly **below** M0 (0.8940 / 0.8781 vs 0.8960 / 0.8807). That is allowed: the reject rule is Hit@5 not lower than M0, not nDCG.

M1 is therefore a **gate-passing, no known-item lift** candidate, not evidence that title_roman retrieval got better.

Official frozen system for Phase 9 known-item remains **M0** (68/78). Do not replace Phase 9 with M1.

## Affected / empty Roman queries

| Model | Train Roman affected | Train empty | n=78 Roman affected | n=78 Roman empty |
| --- | ---: | ---: | ---: | ---: |
| M0 | 0 | 0 | 0 | 0 |
| M1 | 9 | 0 | 3 | 0 |
| M2 | 9 | 0 | 3 | 0 |
| M3 | 61 | 0 | 22 | 0 |
| M4 | 61 | 0 | 22 | 0 |

## What this is not

Not an unseen H001–H040 score. Not H041+. Not human Success@5. Not a Phase 9 rewrite.

Do not claim the winner improves future unseen performance.

