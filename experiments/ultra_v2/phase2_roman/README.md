# ULTRA v2 Phase 2 — Roman Urdu strengthening

**Branch:** `research/ultra-v2-strengthening`  
**Does not edit** frozen M0 (`experiments/phase5_roman_urdu/run_phase5.py`).  
**Does not open** `experiments/ultra_v2/benchmark/test/**` query files.

This directory is the only authorized Phase 2 implementation area.

---

## TEST

Forbidden. R2-B0 does not open `benchmark/test/` at all (including `seal.json`). **TEST was not accessed.**

---

## Run R2-B0 only (TRAIN/DEV Roman KN)

```text
python experiments/ultra_v2/phase2_roman/run_r2_b0.py
```

This runner never opens `benchmark/test/`. It does not apply R2-1 treatments.

NL official metrics are not computed (no qrels).

Large index cache (gitignored): `artifacts/_index_cache.pkl`

---

## Documents

| File | Role |
| --- | --- |
| `AUDIT.md` | Implementation audit (before treatments) |
| `R2_B0_FAILURE_ANALYSIS.md` | Pre-R2-1 diagnostic; R2-1 not implemented |
| `R2_B0_REPRODUCIBILITY.md` | How to rerun R2-B0 |
| `run_r2_b0.py` | Dedicated Method D baseline runner (no TEST, no treatments) |
| `artifacts/r2_b0_summary.json` | Independent R2-B0 metrics |
| `RESULTS.md` | TRAIN/DEV KN development results (not PLOS) |
| `query_treatments.py` | Query-side transforms from the frozen dictionary / Method C alias table |
| `run_r2.py` | Index + KN evaluation wrapper around frozen M0 |
| `artifacts/phase2_summary.json` | Metrics JSON |
| `artifacts/phase2_per_query.csv` | Per-query ranks (TRAIN/DEV only) |
