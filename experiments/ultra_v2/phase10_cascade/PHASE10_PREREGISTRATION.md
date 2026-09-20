# ULTRA v2 Phase 10 — Hybrid-first title-triggered cascade

**Document type:** pre-registration / controlled design  
**Experiment ID:** PHASE10-CASCADE-B  
**Directory:** `experiments/ultra_v2/phase10_cascade/`  
**Branch:** `research/ultra-v2-strengthening`  
**Timestamp (UTC, written before scoring):** `2026-09-20T11:15:00Z`

This file must not be silently rewritten after Phase-10 scores are observed.

Phase 2–9 artifacts stay frozen. M0 / PLOS stay read-only. No TEST. No query-term injection into Hybrid’s Method-D BM25. No Option-A full multi-list RRF of Hybrid+P9+NG3. No threshold search against Hybrid miss labels.

**Status: DESIGN FROZEN — RETRIEVAL NOT YET EXECUTED AT THIS HASH.**

Prior draft: `PHASE10_DESIGN_DRAFT.md` (review decisions locked below).

---

## 1. Scientific question / hypothesis

**H1:** On Roman KN TRAIN+DEV (n=51), a **gold-free** router that fires only when the frozen Phase-9 v2 title matcher finds ≥1 hit, then **Hybrid-first** fills ranks 41–50 from independent Phase-9 and NG3 Top-50 lists (without rewriting Hybrid ranks 1–40), recovers some ExactSource golds that frozen 2-way Hybrid misses — especially among title-triggered Hybrid misses — **without** destroying Hybrid Hit@1 / Hit@5 on the ~half of triggered queries where Hybrid already succeeds.

**H0:** The cascade does not improve scientifically useful metrics over frozen Hybrid (no net recovery of Hybrid Top-50 misses worth the regressions, or Hit@1/5 regresses).

These hypotheses will not be changed after seeing scores.

---

## 2. Hard constraint (Phase 9 lesson)

Phase 9 injected expansion tokens into the BM25 query string and regressed KN023 (correct `aziz mian` match, rank 3→6) via IDF dilution.

**Phase 10:** Hybrid’s BM25 query = original Roman tokens only. Phase 9 and NG3 enter only as **separate candidate lists**. Fusion is rank-level (Option B), never query rewriting.

---

## 3. Frozen components (read-only)

| Component | Identity |
| --- | --- |
| Method-D BM25 | Phase-2 cache; corpus SHA `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231`; dict SHA `30c3f61a64ec641abbb3acdbc7a8bcaf197f0238f1bf9e76c2c7ce8e590f86a3` |
| Dense e5-small | Phase-3 matrix; model `intfloat/multilingual-e5-small` rev `8d923955b027282ba975c0a4c825486c9ca4c490` |
| Hybrid RRF | Phase-4 `fuse_rrf`, **k=60**, tie-break smaller doc_id |
| NG3 | Phase-5 / Phase-2 `ng3_matching.py`, n=3 on Method-D tokens; stream SHAs as Phase 8 |
| Phase-9 matcher | `phase9_entity_resource/match_rule.py` **v2**; title CSV SHA `7686f02d5bb2110eb4cccc7cdbd326324e4f7fa5e4dd34d7125a76d7795cf55d`; wordlist SHA `d6b3e04f1ac30be6525d41474166c0bff28486ecd8c48dcb0ab9c7c9cc05ed86` |

Frozen aggregates to reproduce at the gate (n=51):

| System | Hit@1 | Hit@5 | Hit@10 | Hit@50 | MRR |
| --- | ---: | ---: | ---: | ---: | ---: |
| Method-D BM25 | 1 | 4 | 4 | 6 | 0.0375 |
| Dense | 5 | 15 | 16 | 22 | 0.1726 |
| Hybrid RRF | 3 | 11 | 19 | 25 | 0.1422 |
| NG3 | 3 | 6 | 6 | 8 | 0.0750 |

---

## 4. Deployable method (scored)

### 4.1 Trigger (b) — gold-free

Fire cascade iff Phase-9 v2 matcher returns **≥1** English-title hit (`n_en_hits ≥ 1`).

Expected triggered set (**22 / 51**), frozen from the Phase-9 v2 match preview / scored run (match presence only — not Hit@k):

KN006, KN014, KN018, KN021, KN022, KN023, KN027, KN028, KN029, KN030, KN031, KN033, KN034, KN035, KN037, KN043, KN044, KN045, KN047, KN049, KN051, KN053.

Gate: observed trigger set must equal this set (same 22 IDs). Mismatch → `BLOCKED`.

### 4.2 Lists

For **every** query, compute frozen Hybrid Top-50 list **H** = RRF(BM25 Top-50, Dense Top-50).

For **triggered** queries only:

1. **P9-list:** standalone Method-D BM25 Top-50 using Phase-9 v2 expansion (original tokens + romanized matched Urdu titles). Same expansion as PHASE9-WPTITLES; used only as a candidate list.
2. **NG3-list:** frozen R2-NG3 Top-50 (char-trigram BM25 on Method-D tokens).

For **non-triggered** queries: output = **H** unchanged (all 50 ranks).

### 4.3 Fusion — Option B (Hybrid-first)

Constants (frozen a priori, not tuned on gold):

| Constant | Value |
| --- | ---: |
| `HYBRID_KEEP` | 40 |
| `CASCADE_SLOTS` | 10 |
| Cascade combine | RRF **k=60** of P9-list and NG3-list only (`cascade_rrf`) |
| Tie-break | smaller `doc_id` |

**Triggered output Top-50:**

1. Ranks **1–40** = `H[1…40]` (Hybrid order, untouched).
2. Build cascade ranking `C` = RRF(k=60) of P9-list and NG3-list.
3. Walk `C` in order; append doc ids **not** in `H[1…40]` until **10** slots filled → ranks **41–50**.
4. If fewer than 10 cascade-only docs: pad remaining slots from `H[41…50]` in Hybrid order (docs not already placed).

**Non-triggered:** ranks 1–50 = `H[1…50]`.

Rationale for B over A (locked at review): trigger precision vs Hybrid misses is only ~50% (11/22 fire where Hybrid already Hit@50). Full RRF of Hybrid+P9+NG3 (Option A) would interleave cascade docs into early ranks on those 11 and risk Hit@1/5 dilution (Phase 8 / Phase-9 KN023 failure mode). With small expected recovery, protecting Hybrid early precision outweighs Option A’s Hit@50 upside.

---

## 5. Oracle diagnostic (NOT scored as Phase 10)

**Definition:** `hybrid_hit@50 = 0` on frozen Phase-4 CSV → **26 / 51** IDs  
KN002, KN005, KN006, KN008, KN010, KN018, KN020, KN021, KN022, KN024, KN025, KN026, KN027, KN028, KN032, KN035, KN036, KN037, KN040, KN041, KN042, KN044, KN047, KN050, KN051, KN054.

**Permanent label:** non-deployable / diagnostic / ceiling context only.  
Report intersection with trigger and ROOM Cat1 in the controlled-experiment write-up.  
**Never** call oracle recall/precision “Phase 10’s result.” Phase 10’s primary metrics are ExactSource Hit@k / MRR of the deployable ranked lists vs frozen Hybrid.

---

## 6. Population / metrics

| Item | Value |
| --- | --- |
| Queries | Roman KN TRAIN+DEV **n=51** |
| Gold | ExactSource `source_doc_id` |
| Depth | Top-50 |
| Primary | Hit@1, Hit@5, Hit@10, Hit@50, MRR |
| Secondary | vs Hybrid Hit@50 transitions; ROOM Cat1 (n=11); 23 four-way misses; trigger diagnostics; oracle reported as context |

ROOM Cat1: KN001, KN006, KN008, KN010, KN011, KN018, KN037, KN045, KN047, KN050, KN051.  
QUAD23: same Phase-6 list as Phase 7–9.

---

## 7. Decision labels (exactly one after the single scored run)

- `PHASE10 SUPPORTED` — clear gain over Hybrid on Hit@5 and/or Hit@50 with at most trivial Hit@1/5 regressions; meaningful recoveries among triggered Hybrid misses.
- `PHASE10 PARTIALLY SUPPORTED` — some Hybrid-miss recoveries or Hit@50 gain, but important Hit@1/5 regressions and/or most oracle/Hybrid misses remain.
- `PHASE10 UNSUPPORTED` — no scientifically useful improvement over Hybrid (zero net Hybrid Top-50 recoveries worth claiming, or regressions dominate).
- `BLOCKED` — SHA / gate / trigger-set / TEST / cache failure.

No “≥80% = success.” No second fusion recipe after scores. No retuning `HYBRID_KEEP` / `CASCADE_SLOTS`.

---

## 8. Stop / safety

- No TEST  
- No edit of Phase 2–9 / M0 / PLOS  
- No Option A execution in this experiment  
- No gold-conditioned trigger  
- Documents not re-indexed beyond reproducing frozen NG3 features for the gate  
- Oracle never used as the deployable router  

---

## 9. What this file does not authorize until hashed + go

Execution requires this preregistration to be hashed and the single run performed under these gates. Scoring proceeds immediately after hash in the same authorized session that froze this text.
