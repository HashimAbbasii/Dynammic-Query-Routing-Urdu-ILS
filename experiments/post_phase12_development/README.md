# Post-Phase-12 research development set (R-dev)

**Status:** Protocol and tooling only. **No queries created yet.**

## Read first

- `docs/POST_PHASE12_DEVELOPMENT_SET_PROTOCOL.md` — construction protocol
- `SCHEMA.md` — CSV / manifest fields

## Purpose

Provide a **new**, scientifically independent development set for:

- Module 1 Roman normalization ablations
- Later character-level, hybrid, and routing experiments

This is **not** Phase 2 (87.18%), **not** K001–K040, **not** U001–U040.

## Overlap checker (contamination detection only)

From repository root:

```text
python experiments/post_phase12_development/overlap_check.py --help
python experiments/post_phase12_development/overlap_check.py path/to/draft_queries.csv
```

Uses leakage normalization from `experiments/phase2_oracle/textnorm.py`.  
Does **not** run retrieval. Does **not** modify sealed files.

## Next step after protocol approval

1. Human approval of size, authorship, and annotation budget.  
2. Write `queries_r_dev.csv` under the protocol bans.  
3. Run overlap checker until clean.  
4. Seal checksums in `SEAL.json`.  
5. Only then approve retrieval for labeling / metrics (separate task).
