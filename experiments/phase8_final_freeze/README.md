# Phase 8 — Final evaluation protocol freeze

This phase **freezes** the retrieval system and the evaluation protocol.

It does **not** run H001–H040.

## Frozen system (unchanged from Phase 5/6/7)

| Script | Path |
| --- | --- |
| URDU | Urdu BM25 |
| ROMAN | Romanized-document BM25 (Method D) |
| MIXED | Urdu BM25 |

Official metric: **exact-source Hit@5**.

## Read these first

1. `FINAL_EVALUATION_PROTOCOL.md` — how the held-out test must be run
2. `FINAL_SYSTEM_MANIFEST.json` / `FROZEN_CONFIGURATION.json` — exact configuration
3. `DEVELOPMENT_RESULTS.md` — n=78 baseline and rejected alternatives
4. `PHASE7_EVALUATION_LIMITATIONS.md` — known-item vs human relevance
5. `FINAL_TEST_CHECKLIST.md` — must all be true before opening H001–H040
6. `FUTURE_WORK.md` — ideas **not** implemented

## Stop

Do not inspect, rank, or score H001–H040 in this folder. Do not start Phase 9 from here.
