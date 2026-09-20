# Phase 10 — design draft (NOT a preregistration)

**Program B** · branch `research/ultra-v2-strengthening`  
**Status:** DRAFT FOR REVIEW ONLY — no scoring, no frozen prereg, no TEST  
**Date (UTC draft):** 2026-09-20  

Phases 2–9 remain frozen. Program A / M0 / TEST untouchable.

---

## 0. Hard constraint from Phase 9

Phase 9 scored by **appending** Method-D romanizations of matched Urdu titles into the BM25 query string. That diluted IDF and produced a ranking regression on a *correct* match (KN023: `aziz mian` still matched, gold 3→6).

**Phase 10 rule:** Hybrid’s Method-D BM25 query is never rewritten. Phase 9 and NG3 may only contribute as **separate Top-50 candidate lists**, fused at ranking time (RRF-style or append-below), the same architectural pattern as frozen Phase-4 Hybrid (BM25 list ∪ Dense list → RRF).

---

## 1. Base list (always)

For every Roman KN TRAIN+DEV query (n=51):

- Reproduce frozen **HYBRID-RRF** (Phase 4): Method-D BM25 Top-50 + dense e5-small Top-50 → unweighted RRF `k=60`, tie-break smaller `doc_id`.
- Artifacts / SHAs / encoder / cache gates unchanged from Phase 4.
- This fused Top-50 is the **default output** whenever the deployable trigger does not fire.

---

## 2. Two separate objects — do not conflate

### (a) ORACLE DIAGNOSTIC — upper bound only (NOT a method)

**Definition (uses gold):** query where frozen Hybrid’s Top-50 does **not** contain `source_doc_id` (`hybrid_hit@50 = 0` in `HYBRID_PER_QUERY.csv`).

**Ceiling count: 26 / 51**

| IDs (oracle Hybrid Top-50 miss) |
| --- |
| KN002, KN005, KN006, KN008, KN010, KN018, KN020, KN021, KN022, KN024, KN025, KN026, KN027, KN028, KN032, KN035, KN036, KN037, KN040, KN041, KN042, KN044, KN047, KN050, KN051, KN054 |

**Decomposition (context only):**

| Subset | n | Note |
| --- | ---: | --- |
| `E_both_miss` (gold in neither BM25 nor Dense Top-50) | 25 | Candidate-generation ceiling; fusion alone cannot recover |
| Dense Top-50 hit but Hybrid rank >50 | 1 | **KN040** only (known Phase-4 class F) |

**ROOM Category 1 ∩ oracle:** **8 / 11**  
`KN006, KN008, KN010, KN018, KN037, KN047, KN050, KN051`  
(Not in oracle: KN001, KN011, KN045 — Hybrid already Hit@50.)

**Label for all future reports:** this set is **non-deployable / diagnostic**. A live system has no gold to test “Hybrid missed.” It must never be scored or claimed as Phase 10’s trigger or Phase 10’s result. It only bounds how much a perfect cascade router could help (≤26 queries; actual recovery still depends on Phase 9 / NG3 lists containing the gold).

Among oracle IDs, frozen Phase 9 v2 already places gold in Top-50 for **KN027, KN051** only (the two unique dual-miss recoveries). NG3 Top-50 already covers oracle IDs **KN035, KN050**. That is headroom context for *what lists can supply*, not a trigger.

---

### (b) DEPLOYABLE TRIGGER — candidate Phase 10 method

**Proposed trigger (gold-free):**

> Fire the cascade iff the frozen Phase-9 v2 matcher returns **≥1** English-title hit on the query  
> (`n_en_hits ≥ 1` under `match_rule.py` v2: 10k wordlist + dab exclusion + letter-name UR lookup + L≥2 exact title + caps).

**Why this signal (independent of gold Hybrid misses):**

1. Computable at retrieval time from query text + frozen bilingual table only — no `source_doc_id`, no Hit@k.
2. The v2 match rule was frozen for Phase 9 entity aliasing **before** Phase 9 scoring and was **not** retuned against Hybrid miss labels or ROOM IDs.
3. Scientific intent of the cascade: inject *alias / surface-form* candidates when Wikipedia title structure is present — exactly when Phase 9 has something to contribute as its own list. If there is no title hit, Phase 9’s list is empty or trivial; cascading cannot help via Phase 9.
4. Avoids score-threshold shopping on Hybrid confidence.

**Why not the alternatives considered:**

| Signal | Verdict |
| --- | --- |
| Hybrid top-1 RRF score &lt; τ | **Reject.** With near-disjoint BM25/Dense lists (mean \|∩\| = 0.53; **42/51** have `n_overlap = 0`), top-1 RRF is almost always `1/(60+1) ≈ 0.01639`. No discriminative threshold exists. |
| `n_overlap = 0` | **Reject.** Selects 42/51 — nearly always-on; not a miss proxy. |
| Dense top-1 cosine &lt; τ | **Reject as primary.** Available (`dense_rank1_similarity`), gold-free, but on this n=51 the values are tightly packed (min ≈ 0.821, max ≈ 0.891, median ≈ 0.861). Literature-ish floors (0.80 / 0.85) either select nobody or require picking τ inside that band — any τ chosen by maximizing agreement with the 26 oracle misses would be **threshold-shopping / leakage**. Not proposed. |
| Always-on 3- or 4-list RRF for all 51 | Deployable, but **not** a selective trigger; closer to extending Phase 8. Kept as a **design alternative** if review rejects selective routing (see §6). |

**Explicit leakage check:** The title-hit trigger does **not** use Hybrid miss labels. Reporting how often it coincides with the oracle (below) is a **post-hoc diagnostic of proxy quality**, not how the threshold was chosen. There is no numeric threshold to tune.

**If review wants a confidence trigger instead:** say so; the honest statement is that Hybrid RRF top score and dense top-1 cosine **cannot** currently be frozen into a miss-router on this data without either selecting almost everyone or shopping τ against gold. Prefer title-hit or always-on over a fake confidence gate.

---

## 3. What happens when trigger (b) fires

For **triggered** queries only, build **two independent** Top-50 lists (never merge tokens into Hybrid’s BM25 query):

| List | Source | How scored | Depth |
| --- | --- | --- | --- |
| **P9-list** | Frozen Phase-9 v2 match → Method-D romanization of matched Urdu titles → **standalone** Method-D BM25 search (same mechanics as scored PHASE9-WPTITLES, but output is a candidate list) | BM25 scores on that list’s own query tokens | Top-50 |
| **NG3-list** | Frozen Phase-5 R2-NG3 char-trigram retriever | NG3 scores as frozen | Top-50 |

For **non-triggered** queries: emit Hybrid Top-50 **unchanged** — no P9-list, no NG3-list, no rescoring.

**Important distinction:** Expansion tokens may exist *inside* the P9-list retriever (that is how Phase 9 builds its own ranking). They must **not** be appended to the Hybrid pipeline’s BM25 query. Hybrid’s BM25 half stays the original Roman tokens.

---

## 4. Two fusion options for triggered queries (do not silently pick)

Both options start from the frozen Hybrid Top-50 as list **H**. Optional inputs: **P9**, **NG3**. Output: one Top-50.

### Option A — Multi-list RRF (k=60)

Treat **H** as one ranked list (Hybrid’s fused order is the rank), plus **P9** and **NG3** as two further lists:

\[
\mathrm{RRF}(d)=\sum_{L\in\{H,\,P9,\,NG3\}}\frac{1}{60+\mathrm{rank}_L(d)}
\]

(missing list → 0). Sort by RRF desc, tie-break smaller `doc_id`. Truncate at 50.

**Variant A1 (recommended if A is chosen):** three lists as above.  
**Variant A2:** collapse P9∪NG3 into one “cascade” list first (e.g. RRF of P9+NG3 only), then 2-way RRF of H + cascade — fewer channels, less early-rank dilution.

**Tradeoffs**

| Pros | Cons |
| --- | --- |
| Same fusion family as Phase 4 / Phase 8; no new machinery | Interleaves foreign candidates into early ranks → can regress Hybrid Hit@1/5 (same failure mode Phase 4 saw vs dense alone) |
| Docs supported by multiple lists rise naturally | Hybrid’s internal BM25+Dense balance is only preserved *inside* H’s ranks; RRF does not re-weight Hybrid’s components |
| Symmetric treatment of P9 and NG3 | Empty/noisy P9 or NG3 lists still inject mass if present |

### Option B — Hybrid-first, fill from cascade

1. Keep all of **H** in order as ranks 1…\|H\| (typically 50).  
2. If \|H\| &lt; 50 (should not happen under Phase-4 depth), or — more usefully — **replace nothing**; instead define a **pool of 50** as: take H entirely, then if we want room for cascade, **reserve last R slots** (e.g. R=10) for cascade-only docs: ranks 1…(50−R) = H[1…50−R]; ranks (50−R+1)…50 = next docs from P9/NG3 (by their own score or by RRF of P9+NG3) not already in H.

Cleaner **B-strict** statement for prereg later:

- Output ranks 1–50 = Hybrid list unchanged when trigger is off.  
- When trigger is on: ranks **1–40** = Hybrid[1–40]; ranks **41–50** = top cascade-only docs (P9/NG3 RRF or score), excluding any doc already in Hybrid[1–40].

Or **B-append-only-beyond-50** is useless for Hit@50. So B must **displace** some Hybrid tail.

**Tradeoffs**

| Pros | Cons |
| --- | --- |
| Protects Hybrid early precision (Hit@1/5/10 largely intact) | Cascade recoveries can only appear in the reserved tail → hard to improve Hit@5; mainly Hit@50 / MRR-at-depth |
| Matches “Hybrid is primary; cascade is rescue” story | Needs a frozen reserve size R (another constant — freeze a priori, e.g. R=10, not tuned on gold) |
| Limits Phase-9 IDF-style damage to early ranks | KN027-style recoveries that need early rank may stay RANK-only |

**Draft recommendation for review (not frozen):** prefer stating **both** A and B in any future prereg as a **single prechosen primary** after review — not both scored. Scientific preference if cascade is about **candidate generation for Hybrid misses**: Option A maximizes chance gold enters Top-50; Option B maximizes safety of Hybrid’s existing 25/51 Hit@50. Given oracle ceiling is mostly generation (25 both-miss), **Option A** is the better scientific test of whether P9/NG3 lists contain missing golds; **Option B** is the safer product-style router.

---

## 5. Counts (deployable vs ceiling)

| Set | n / 51 | Role |
| --- | ---: | --- |
| **(b) Title-hit trigger** | **22** | Deployable Phase 10 router |
| **(a) Oracle Hybrid miss** | **26** | Ceiling / diagnostic only |
| **(b) ∩ (a)** | **11** | Trigger fires on a true Hybrid miss |
| **(b) \ (a)** | **11** | Trigger fires though Hybrid already Hit@50 (cascade risk / dilution) |
| **(a) \ (b)** | **15** | True Hybrid misses with **no** Phase-9 title hit — cascade cannot use P9; NG3-only still possible only if trigger were widened |

**Proxy quality (diagnostic, not used to choose the trigger):**

- Precision of (b) as predictor of (a): 11/22 ≈ **50%**
- Recall of (a) covered by (b): 11/26 ≈ **42%**
- Gap: trigger under-covers the ceiling by **15** queries and over-fires on **11** Hybrid successes.

**Trigger (b) IDs (22):**  
KN006, KN014, KN018, KN021, KN022, KN023, KN027, KN028, KN029, KN030, KN031, KN033, KN034, KN035, KN037, KN043, KN044, KN045, KN047, KN049, KN051, KN053  

**Intersection with oracle (11):**  
KN006, KN018, KN021, KN022, KN027, KN028, KN035, KN037, KN044, KN047, KN051  

### ROOM Category 1 (n=11) overlap

| Set | ROOM IDs | n |
| --- | --- | ---: |
| ROOM ∩ oracle (a) | KN006, KN008, KN010, KN018, KN037, KN047, KN050, KN051 | **8** |
| ROOM ∩ trigger (b) | KN006, KN018, KN037, KN045, KN047, KN051 | **6** |
| ROOM ∩ (a) ∩ (b) | KN006, KN018, KN037, KN047, KN051 | **5** |

ROOM Hybrid successes **not** in oracle: KN001, KN011, KN045. Of those, trigger (b) still fires on **KN045** (facebook title) — a known dilution risk for Option A.

---

## 6. Design alternatives to park (not proposed as primary)

1. **Always-on:** RRF(H, P9, NG3) for all 51 — no trigger. Deployable; avoids proxy gap; higher regression risk on Hybrid successes. Closest to “Phase 8 + Phase 9 list.”
2. **NG3-only cascade when no title hit:** would cover some of the 15 oracle\trigger IDs (e.g. KN050) but needs a second gold-free rule; not drafted here.
3. **Confidence τ on dense/BM25:** not freezeable without leakage on this band of scores (see §2b).

---

## 7. What this draft deliberately does not do

- No retrieval / Hit@k scoring of Phase 10  
- No `PHASE10_PREREGISTRATION.md` freeze  
- No threshold search against the 26 oracle IDs  
- No editing Phase 2–9 artifacts  
- No TEST access  
- No query-side injection into Hybrid BM25  

---

## 8. Review asks

1. Accept **title-hit ≥1** as deployable trigger (b), or prefer always-on / reject selective cascade?  
2. Choose **fusion Option A (multi-RRF)** vs **Option B (Hybrid-first reserve)** as the single primary for a future prereg.  
3. Confirm oracle (a) stays permanently labeled diagnostic in all reports.

Stop here pending review.
