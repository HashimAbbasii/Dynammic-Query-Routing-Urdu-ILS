# PHASE10-CASCADE-B — controlled experiment report

**Experiment ID:** PHASE10-CASCADE-B  
**Status:** complete  
**Decision:** `PHASE10 PARTIALLY SUPPORTED`  
**Timestamp (UTC, after gated evaluation):** `2026-09-20T11:28:19Z`  
**Branch / commit:** `research/ultra-v2-strengthening` / `fd54ac9b65c2db93e7e16fbf0c5a40b6a6025be1`

Protocol frozen in `PHASE10_PREREGISTRATION.md` **before** scores. SHA-256:

`c85eeb3509423d98fb40eb5ff8e9d44d5e6ee76e2239dc162a9c4ef710369eee`

Prereg matching procedure was not rewritten after scores. TEST not opened. Phase 2–9 / M0 not modified. No query-term injection into Hybrid BM25. Option A not run.

Scored CSV: `artifacts/phase10_scored_results.csv`  
SHA-256: `b32a7a4d52f2688b65df7636cd570393011c15333c8418455339bdecedc2d0c6`

---

## 1. Question

Does a gold-free Phase-9 title-hit trigger + Hybrid-first Option B fill (ranks 1–40 = Hybrid; 41–50 from RRF(P9,NG3) cascade-only) improve ExactSource retrieval over frozen 2-way Hybrid without destroying Hit@1/5?

---

## 2. Gates

| Gate | Result |
| --- | --- |
| BM25 / Dense / Hybrid / NG3 aggregates vs frozen | **PASS** |
| Trigger set = frozen 22 IDs | **PASS** |
| P9-list ranks vs `phase9_scored_results.csv` (triggered) | **PASS** |
| Option B second pass identical | **PASS** |
| Non-trigger Top-50 list = Hybrid Top-50 | **PASS** |

---

## 3. Official metrics (n=51 Roman KN TRAIN+DEV)

| Method | Hit@1 | Hit@5 | Hit@10 | Hit@50 | MRR |
| --- | ---: | ---: | ---: | ---: | ---: |
| Frozen Hybrid RRF | 3 | 11 | 19 | **25** | **0.1422** |
| **PHASE10-CASCADE-B** | **3** | **11** | **19** | **24** | **0.1418** |

Hit@1 / Hit@5 / Hit@10 **unchanged** (Option B protected early Hybrid ranks). Hit@50 **25→24** (net −1). MRR slightly down.

Triggered queries: **22/51** (title-hit).

---

## 4. vs Hybrid (deployable result)

|  | Hybrid HIT@50 | Hybrid MISS@50 |
| --- | ---: | ---: |
| P10 HIT@50 | 22 | 2 |
| P10 MISS@50 | 3 | 24 |

**Recovered Hybrid Top-50 misses:** KN027 (P10 rank **45**), KN035 (P10 rank **42**).  
**Regressed Hybrid Top-50 hits:** KN030 (47→miss), KN043 (44→miss), KN045 (45→miss).  
**Hit@5 regressions:** **none**.

Both recoveries land in the cascade band (41–50), as designed.

---

## 5. Oracle diagnostic (NON-DEPLOYABLE — context only)

Oracle = frozen Hybrid Top-50 miss: **26/51**.  
Trigger ∩ oracle: **11/26**.  

Of those 11, Phase 10 recovers **2** (KN027, KN035). KN051 (Phase-9 standalone rank 12) remains a Hybrid miss under Option B — cascade RRF(P9,NG3) did not place it in the 10 fill slots. KN050 (NG3 Hit@1) is an oracle miss **without** title trigger, so cascade never runs.

**This paragraph is ceiling context, not Phase 10’s claimed result.**

---

## 6. ROOM Category 1 (n=11)

| Method | Hit@50 | IDs |
| --- | ---: | --- |
| Hybrid | 3/11 | KN001, KN011, KN045 |
| Phase 10 | **2/11** | KN001, KN011 |

ROOM regression: **KN045** (Hybrid rank 45 → displaced by cascade fill).

---

## 7. 23 four-way misses

Phase 10 Hit@50 among QUAD23: **1/23** — **KN027** only.  
(KN035 is not in the Phase-6 four-way-miss list; it is an NG3/Hybrid-miss recovery via cascade.)

---

## 8. Decision

**`PHASE10 PARTIALLY SUPPORTED`**

- Early precision preserved (Hit@1/5/10 = Hybrid).  
- Two Hybrid-miss recoveries in the cascade tail (KN027, KN035).  
- But three Hybrid Top-50 successes lost (including ROOM KN045); net Hit@50 falls 25→24.  
- Most oracle / dual-miss queries remain out; KN051 not recovered under Option B.

---

## 9. Safety

| Check | |
| --- | --- |
| TEST accessed | no |
| Hybrid BM25 query rewritten | no |
| Option A full RRF | no |
| Oracle used as trigger | no |
| Phase 2–9 modified | no |
