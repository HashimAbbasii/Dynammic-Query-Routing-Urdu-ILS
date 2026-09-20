# PHASE10B-TAIL-PRESERVE — controlled experiment report

**Experiment ID:** PHASE10B-TAIL-PRESERVE  
**Status:** complete  
**Decision:** `PHASE10B PARTIALLY SUPPORTED`  
**Timestamp (UTC, after gated evaluation):** `2026-09-20T11:49:58Z`  
**Branch / commit:** `research/ultra-v2-strengthening` / `fd54ac9b65c2db93e7e16fbf0c5a40b6a6025be1`

Prereg SHA-256 (before scores):

`60f691c38e4b3d8a6f26f9c435cf4c0fa55ddafaa73dd7da1093bddfaa49e60e`

**Frozen Phase 10 (PHASE10-CASCADE-B) remains on record as negative** (Hit@50 24/51). Its artifacts were not overwritten.

Scored CSV: `artifacts/phase10b_scored_results.csv`  
SHA-256: `fde7ba16e43b57f753a5558bc44c1d082f363418f612ec64971740496e1436f5`

---

## 1. Sole change

Preserve Hybrid’s own ranks 41–50; cascade fills **only empty** tail slots (`|H| < 50`). Trigger (b), keep=40, slots=10, RRF k=60 for P9+NG3 — unchanged.

---

## 2. Gates

All PASS (BM25 / Dense / Hybrid / NG3 / trigger 22 / fusion repeat).  
**51/51** queries: Phase 10b Top-50 **identical** to Hybrid Top-50 (Hybrid always returned a full 50; no empty tail slots).

---

## 3. Official metrics (n=51)

| Method | Hit@1 | Hit@5 | Hit@10 | Hit@50 | MRR |
| --- | ---: | ---: | ---: | ---: | ---: |
| Frozen Hybrid | 3 | 11 | 19 | 25 | 0.1422 |
| Frozen Phase 10 (Option B, negative) | 3 | 11 | 19 | 24 | 0.1418 |
| **Phase 10b** | **3** | **11** | **19** | **25** | **0.1422** |

Hit@50 net vs Hybrid: **0** (not net-positive).

---

## 4. Focus IDs

| ID | Phase 10 | Phase 10b |
| --- | --- | --- |
| KN030 | regressed (47→miss) | **preserved @47** |
| KN043 | regressed (44→miss) | **preserved @44** |
| KN045 | regressed (45→miss) | **preserved @45** |
| KN027 | recovered @45 | **not recovered** (miss) |
| KN035 | recovered @42 | **not recovered** (miss) |

Tail-eviction regressions fixed; Phase-10 cascade recoveries do not survive (as expected when Hybrid is full Top-50).

---

## 5. ROOM Category 1

**3/11** — KN001, KN011, KN045 (identical to Hybrid; KN045 restored vs Phase 10).

---

## 6. Decision and stop

**`PHASE10B PARTIALLY SUPPORTED`** — equals Hybrid (regressions fixed, no new recoveries).  

**Stop rule fired:** Hit@50 is **not** net-positive vs Hybrid → **no further Option-B variants.** Proceed to Phase 11 planning.
