# ULTRA v2 Phase 10b — Hybrid-tail preservation (one-line correction)

**Document type:** pre-registration / controlled design  
**Experiment ID:** PHASE10B-TAIL-PRESERVE  
**Directory:** `experiments/ultra_v2/phase10_cascade/`  
**Branch:** `research/ultra-v2-strengthening`  
**Timestamp (UTC, written before scoring):** `2026-09-20T11:45:00Z`

This file must not be silently rewritten after Phase-10b scores are observed.

**Frozen Phase 10 (PHASE10-CASCADE-B) stays in the record as a negative result.**  
Do not overwrite or delete `PHASE10_PREREGISTRATION.md`, `PHASE10_CONTROLLED_EXPERIMENT.md`, `PHASE10_PER_QUERY.csv`, or `artifacts/phase10_*`.

Phase 2–9 / M0 / TEST / trigger (b) / `HYBRID_KEEP=40` / `CASCADE_SLOTS=10` / RRF k=60 for P9+NG3 combine — all unchanged from Phase 10.

**Status: DESIGN FROZEN — RETRIEVAL NOT YET EXECUTED AT THIS HASH.**

---

## 1. Question / hypothesis

**H1:** Preserving Hybrid’s own ranks 41–50 (never overwriting them with cascade) removes the Phase-10 tail-eviction regressions (KN030, KN043, KN045) while still allowing cascade fill only into **empty** Hybrid tail slots; Hit@50 is net non-worse than Hybrid and may stay non-negative vs Hybrid.

**H0:** The correction does not yield Hit@50 net-positive vs Hybrid (either equals Hybrid with zero cascade effect when Hybrid is full Top-50, or still fails to improve).

No further Option-B variants after this single run if Hit@50 is not net-positive vs Hybrid.

---

## 2. Sole change vs frozen Phase-10 Option B

**Phase 10 Option B (frozen, negative):** ranks 1–40 = `H[1…40]`; ranks 41–50 = cascade-only from RRF(P9,NG3), **replacing** Hybrid’s own `H[41…50]` (pad from Hybrid tail only if cascade short).

**Phase 10b (this experiment):**

1. Ranks **1–40** = `H[1…40]` (unchanged).  
2. Inspect Hybrid’s own Top-50 list (retrieval-time, **no gold**).  
3. For ranks **41–50**: **keep** every Hybrid entry that already occupies those ranks (`H[41…50]`). **Do not** overwrite those ranks with cascade candidates.  
4. Cascade (RRF k=60 of P9-list and NG3-list, cascade-only docs not already in the output) may fill **only empty** slots among 41–50 — i.e. only when `|H| < 50` leaves unfilled positions.  
5. Non-triggered queries: output = full `H` unchanged (same as Phase 10).

**Consequence (stated a priori):** When Hybrid returns a full Top-50 (the usual case on this corpus), Phase 10b output equals Hybrid for triggered and non-triggered queries alike; cascade never displaces a Hybrid tail doc. Recoveries that required eviction of `H[41…50]` cannot occur. That is intentional: the correction targets regressions, not new eviction.

Everything else identical to Phase 10: trigger (b) same 22 IDs; same lists; no query injection into Hybrid BM25; no Option A; no threshold retuning.

---

## 3. Gates / frozen aggregates

Reproduce Method-D / Dense / Hybrid / NG3 frozen cells (same SHAs as Phase 10).  
Trigger set must equal the same frozen 22 IDs.  
Phase-10b fusion second pass identical.  
Non-trigger Top-50 list = Hybrid Top-50.

Oracle Hybrid-miss set remains **diagnostic only** (same 26 IDs as Phase 10); never scored as Phase 10b’s result.

---

## 4. Metrics / population

Roman KN TRAIN+DEV **n=51**. ExactSource Hit@1/5/10/50/MRR.  
Secondary: vs Hybrid transitions; preserve status of KN030/KN043/KN045; survival of KN027/KN035; ROOM Cat1; comparison to frozen Phase-10 negative result (descriptive).

---

## 5. Decision labels (exactly one)

- `PHASE10B SUPPORTED` — Hit@50 **net-positive** vs Hybrid (strictly more Hit@50 than 25) with Hit@1/5 not worse than Hybrid.  
- `PHASE10B PARTIALLY SUPPORTED` — Hit@50 equal to Hybrid (regressions fixed, no new recoveries) **or** net gain with important caveats; Hit@1/5 preserved.  
- `PHASE10B UNSUPPORTED` — Hit@50 worse than Hybrid, or Hit@1/5 regresses.  
- `BLOCKED` — gate / SHA / trigger / TEST failure.

**Stop rule:** If Hit@50 is not net-positive vs Hybrid, do not attempt further Option-B variants; report honestly and proceed to Phase 11 planning.

---

## 6. Safety

No TEST. No edit of Phase 2–10 scored artifacts. No gold-conditioned trigger. No Option A.
