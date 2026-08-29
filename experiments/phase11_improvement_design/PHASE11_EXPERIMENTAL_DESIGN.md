# Phase 11 — experimental design (not executed)

**Status:** PLAN ONLY. Do not retrieve. Do not change BM25, Method D, the dictionary, or routing until this protocol is explicitly approved **and** a later implementation phase is approved.

**Does not modify:** Phase 9, Phase 10B, Phase 10C, H001–H040 labels, or `heldout_retrieval_template.csv`.

---

## 0. What “~80% genuine usefulness” can and cannot mean

Two different numbers already exist. They must stay separate.

| Claim | Pool | Metric | Value | Role |
|---|---|---|---|---|
| Official known-item | `QTRN_*` n=78 | ExactSource Hit@5 | **68/78 = 0.8718** | **Preserve.** Already above 80%. |
| Frozen human usefulness | H001–H040 n=40 | Success@5 (A or B in Top-5) | **25/40 = 0.6250** | **Historical baseline of the frozen system.** Contaminated for tuning. |
| Official H known-item | H001–H040 | ExactSource Hit@5 | **undefined** | No `source_doc_id`. Do not invent. |

Phase 11 is **not** a project to push 0.8718 toward 0.90 (Phase 8 forbade chasing 90% on n=78).  
Phase 11 is **not** a project to retune until H001–H040 Success@5 looks like 80%.

A genuine ~80% **human** Success@5, if it happens, can be claimed only on a **new** unseen set (H041+), after improvements are frozen on development data.

If that new-set number lands at 65% or 72% instead of 80%, **report it honestly**. Do not force 80%.

---

## 1. Scientific problem (from allowed evidence only)

### 1.1 What n=78 actually tests

Phase 2 `QTRN_*` Roman strings are `title_roman`: dictionary reverse + naive character romanization of **headlines**, not chat-style user Roman (Phase 5 report). Method D already recovers **22/23** of those known-items. Remaining n=78 misses (Phase 6) are mostly **query ambiguity / topical neighbours / mixed-title truncation**, not missing Roman overlap.

So: changing Method D to “fix H036 `diesel rate`” would be **test peeking**, and it would target a **different query distribution** than the official 87.18% pool.

### 1.2 What 10C actually showed (diagnostic only — do not tune on it)

Frozen-system human Success@5 = 62.5%; conservative P@5 = 12.5%.  
Urdu 14/20 vs Roman 11/20; 8/10 all-D queries were Roman.

**Allowed use of 10C:** motivate *which class of method* to study (query-side Roman / loanwords), already anticipated by Phase 8 `FUTURE_WORK.md` item 3.

**Forbidden use of 10C:** adding dictionary rows for `diesel`, `temperature`, `iphone`, `kab`, or dropping H036-like queries; re-scoring H001–H040 after a fix and calling that unseen.

### 1.3 Phase 8 future work that is in-bounds

1. Graded qrels on a sample **that is not the sealed/contaminated test**  
3. Naturalistic Roman Urdu ≠ `title_roman`  
2. Date-aware retrieval **only if** corpus timestamps exist (not assumed)  
4–6. Headline fusion / dense GPU / reranker — **not** Phase 11 primary (Phase 6/7 already judged them unjustified for +1–3 known-items)

---

## 2. Architecture freeze (what must not be the first knob)

Keep unless a later phase pre-registers a change **and** n=78 does not collapse:

- Unicode `detect_script` (n=78: 78/78; H dump: 20/20). Routing is **not** the bottleneck.
- URDU/MIXED → Urdu BM25 on raw tokens  
- ROMAN → Method D **document** index (romanized corpus)  
- `k1=1.5`, `b=0.75`, tokenizer, 198-key reverse dict **as the document romanizer**  
- Corpus hash `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231`

**Preferred improvement surface:** **query-side** transforms on the ROMAN path only, leaving the Method D **document** index identical. That isolates ablations and limits damage to the 22/23 Roman known-items.

---

## 3. Data split for Phase 11

| Pool | IDs | n | Use in Phase 11 |
|---|---|---|---|
| **Regression (frozen baseline)** | Phase 2 `dev` + `internal_val` | 78 | ExactSource Hit@5 **must be reported every time**. Selection must not sacrifice this without a pre-registered tolerance. |
| **Selection / training of query-side rules** | Phase 2 `train` | 182 | Primary **development** pool. Subset `language_type == roman_urdu` for Roman methods. |
| **DEV Roman known-item (historical)** | Phase 5 DEV Roman | 13 | Already used to **select Method D**. Do not re-select Method D here. May be used only as a **smoke check** that query-side changes do not destroy D. |
| **Diagnostic contaminated** | H001–H040 | 40 | **Locked.** Read-only history. No labels edited. No comparison shopping. |
| **New unseen** | H041+ (not created yet) | TBD (recommend 40) | Created **after** the improved system is frozen. One annotation pass. |

No H001–H040 string may appear in a loanword list, variant list, or “hard query” mining script.

---

## 4. Metrics

### 4.1 Must preserve (every candidate)

- ExactSource Hit@5 on n=78  
- Roman subset Hit@5 on the 23 eval Roman `QTRN_*` (frozen D = 22/23)  
- Urdu subset Hit@5 on the 46 eval Urdu `QTRN_*` (frozen ≈ 0.913)

**Hard gate (pre-registered):** reject a candidate if n=78 ExactSource Hit@5 **< 68/78 (0.8718)**.  
Optional note-only tolerance: a 67/78 result may be discussed as a regression, **not** accepted as the new official known-item system.

### 4.2 Used to *select* a Roman query-side method (development only)

On **train** `roman_urdu` rows (known-item `source_doc_id`):

- Primary: ExactSource Hit@5  
- Secondary: nDCG@5, MRR  

On a **pre-registered User-Roman proxy** built from **train Urdu titles only** (see §6.1):

- Same known-item metrics (proxy still has `source_doc_id` because it is title-derived)

Do **not** use human Success@5 on H001–H040 to pick a winner.

### 4.3 Used only after freeze, on H041+ (future Phase 12)

Same 10C definitions, new IDs:

- Success@5 (A or B in available Top-5) / n  
- Conservative P@5 (A-count / 5)  
- All-D rate  

Also run the **frozen Phase 9 system** and the **Phase 11 system** once each on H041+ (both frozen before the set is opened). Difference = genuine improvement.

---

## 5. Ranked improvement candidates

Scale: impact / defensibility / implementation risk / risk to 0.8718 / thesis-paper fit.

### Rank 1 — Query-side Roman spelling normalization (do first)

**What:** On ROMAN path only, expand or canonicalize query tokens using a **closed** variant table derived from:

- existing `models/roman_urdu_dict_expanded.json` (198 keys) and any **already-in-repo** variant map (e.g. Phase 5 `_VARIANT_TO_DICT_KEY`)  
- **train** `title_roman` vs naive romanization mismatches (Phase 2 train only)

**Do not** add keys because of H010 `waja` / H016 `girawut`.

| Axis | Rating |
|---|---|
| Expected impact | Medium on *user* Roman; **low** on n=78 (title_roman already matches Method D) |
| Defensibility | High if table is train/corpus-closed and listed in a freeze file |
| Implementation risk | Low (query-side, ablatable) |
| Risk to 0.8718 | Low if gated: apply only when detector=ROMAN; skip tokens that already hit the Method D index |
| Thesis / IEEE | Strong: “Method D is for title_roman; we add a documented query normalizer for spelling variation” |

### Rank 2 — Closed English-loanword expansion on ROMAN queries (do second, same phase)

**What:** If a ROMAN query token is ASCII and **already occurs as a Latin token in the frozen corpus**, optionally add the Method D romanization(s) of **co-occurring Urdu** words from **train headlines / train source articles only** (e.g. document contains both `diesel` and `ڈیزل`). That is corpus statistics, not H036.

**Forbidden:** Hand-typing `diesel → diesel/dizl` because 10C failed `diesel rate`.

| Axis | Rating |
|---|---|
| Expected impact | High on naturalistic/English-mixed Roman; unknown on n=78 |
| Defensibility | Medium–high if the extraction script uses train+corpus only and the word list is frozen before H041+ |
| Implementation risk | Medium (over-expansion / topic drift) |
| Risk to 0.8718 | Medium — **must** pass the 68/78 hard gate |
| Thesis / IEEE | Strong if framed as OOV English in Roman Urdu news search, with ablations |

Phase 8 item 3 is the citation for why this is legitimate even though 10C made the gap visible.

### Rank 3 — Optional DEV-only ablation: downweight/stop high-df Roman function words

Examples of the *class* (not H-specific rules): very common tokens that collide under character romanization (`aaj` / `kab` class).  

**Procedure:** On **train** Roman known-item, test a **closed stoplist** of function words taken from a pre-registered list (e.g. `ka, ki, ke, mein, hai, kya, kab, aaj` **only if** they appear in train roman queries). Measure Hit@5. Accept only if train Roman Hit@5 does not fall and n=78 gate holds.

| Axis | Rating |
|---|---|
| Expected impact | Low–medium |
| Defensibility | Medium (stopwords are standard; must not be fitted to H027 Kaaba) |
| Risk to 0.8718 | Low–medium |
| Thesis / IEEE | Acceptable as a one-row ablation, not the main contribution |

This is the **only** temporal-adjacent lever that does not require article timestamps.

### Rank 4 — Homograph-aware retrieval (`ہار` / `فیل` / `ڈوبی`) — **not Phase 11 primary**

Phase 6: residual n=78 failures are **not** primarily missing overlap. Homographs showed up in **contaminated** H traps. Solving them needs WSD or query context; easy to overfit three examples.

**Defer.** Document as limitation / future work.

### Rank 5 — Query expansion (RM3 / synonyms) — **not Phase 11 primary**

Phase 6: misses already overlap many neighbours. Expansion likely **worsens** known-item uniqueness. High risk to 0.8718.

### Rank 6 — Hybrid Headline+body / RRF / reranker — **not Phase 11 primary**

Headline oracle +3/78. Phase 7: not justified. Dense GPU index: Phase 4B failed the time gate. Revisit only in a later phase with a new protocol.

### Rank 7 — Date-aware “today” retrieval — **not Phase 11 unless dates exist**

Phase 8 item 2. First **audit** whether `clean_articles.csv` has a reliable date field. If not, do not fake recency. For QTRN, Phase 7 already treats undated recurring wires as type-level relevant. Temporal H queries remain a **task/corpus mismatch**, not a BM25 bug to patch with H-specific rules.

---

## 6. Proposed Phase 11 experiment (after approval)

Name: **Phase 11 — query-side Roman robustness, Method D index unchanged.**

### 6.1 User-Roman proxy (development, no H IDs)

From Phase 2 **train** rows with Urdu `query_text` or source headline:

1. Generate 1–2 **chat-style** romanizations with a **frozen** letter map (the existing Phase 5 char table) plus a **frozen** small spelling-variant table from train only.  
2. Keep the same `source_doc_id`.  
3. Write `experiments/phase11_roman_query_side/USER_ROMAN_PROXY_TRAIN.csv` with a generation log (no H001–H040).

This proxy is still known-item (optimistic vs true users) but **closer** to naturalistic Roman than `title_roman` without using the contaminated 40.

### 6.2 Candidates to ablate (all ROMAN path, query-side)

| ID | System |
|---|---|
| **M0** | Frozen Phase 9 (control) |
| **M1** | M0 + spelling variant expansion |
| **M2** | M0 + train/corpus English-loanword expansion |
| **M3** | M1 + M2 |
| **M4** | M3 + optional function-word stoplist (only if §5 Rank 3 passes train) |

Do not change Urdu BM25 in these runs.

### 6.3 Selection rule (freeze before H041+)

1. Discard any Mx with n=78 Hit@5 < 0.8718.  
2. Among survivors, maximize train Roman ExactSource Hit@5; tie-break train User-Roman-proxy Hit@5; then nDCG@5.  
3. Confirm **once** on n=78 (already computed in step 1) — no second peek at H001–H040.  
4. Write `SELECTED_METHOD.json`. Stop.

### 6.4 Acceptance / rejection

| Outcome | Decision |
|---|---|
| No Mx beats M0 on train Roman **and** proxy, or all fail the 68/78 gate | **Reject** Phase 11 as a system change. Thesis reports frozen 87.18% + frozen 10C 62.5% human. IEEE claim stays “script-aware BM25 for title-derived Urdu/Roman.” |
| An Mx passes the gate and improves train/proxy Roman known-item | **Accept** as a **candidate improved system**. Do **not** yet claim 80% human. |
| Accepted Mx later scores Success@5 on **H041+** clearly above frozen M0 on the **same** H041+ | **Meaningful improvement** (see §9). |

---

## 7. Contamination safeguards

1. Scripts that build variant/loanword tables must **assert** no `H00` query_id and no exact H001–H040 query strings in the training tables.  
2. Do not open `HELD_OUT_QRELS.csv` while building tables.  
3. Do not copy MiniLM template labels.  
4. Code review: ROMAN-path `if` only; URDU queries tokenized as today.  
5. After selection, **one** dump of the chosen system on H041+; no iterate-and-rerun on H041+.  
6. H001–H040 may appear in the thesis only as **frozen 10C baseline**, never as the selection set.

---

## 8. How to create H041+ (later; **do not create now**)

Wait until Phase 11 method is frozen (or until Phase 11 is rejected and the frozen system remains official).

**Design (pre-register in a short protocol before writing queries):**

- n = **40** (same size as H001–H040, comparable Success@5)  
- Mix: ~20 Urdu / ~20 Roman; short, factoid, and long controls — **new text**, not paraphrases of H001–H040  
- **Ban list:** do not reuse H query strings; do not write `diesel rate` / `petrol kyun mehnga` / `aaj lahore ka temperature` clones  
- Still **no** `source_doc_id` unless you separately sample known-item queries from unused corpus rows (optional second track)  
- Author the list without 10B Top-5 or 10C labels on screen  
- Persist Top-5 **before** labeling (logging complete, unlike Phase 9)  
- Annotate with the Phase 10C addendum (raw query; temporal type-of-fact)  
- Run **M0 and selected Mx** in one sealed window so comparison is fair

Optional: a second known-item unseen sample (new `QTRN`-style titles from articles **not** used in QTRN_001–260) if you want an unseen **ExactSource** number. That is extra work; not required for a valid MS thesis if 0.8718 stays the official known-item result.

---

## 9. What counts as a meaningful result

**Meaningful improvement (system change justified):**  
On H041+, Success@5(Mx) − Success@5(M0) ≥ **+0.10** (e.g. 0.63 → 0.73) **and** n=78 Hit@5 stays ≥ 0.8718.  
Secondary: all-D rate decreases; conservative P@5 not collapsed.

**Strong MS AI thesis claim (even without 80% human):**

- Official known-item: 68/78 = 87.18% script-aware BM25  
- Honest limitation: Method D matches `title_roman`, not necessarily user Roman / English loanwords  
- Frozen human diagnostic: 25/40 = 62.5% Success@5 on H001–H040 (contaminated; not used for tuning)  
- If Phase 11 accepts Mx: query-side Roman robustness with ablations and a **new** human eval  

That is already a complete, defensible thesis **without** fabricating 80%.

**Credible IEEE-style paper claim:**

- Same two-metric story (known-item vs graded usefulness)  
- n=78 + comparators already in `DEVELOPMENT_RESULTS.md` (raw BM25 0.59, MiniLM headline 0.45, Method D 22/23 Roman)  
- If Mx is accepted: one table of M0–M4 on train/proxy + n=78 gate + H041+ Success@5 for M0 vs Mx  
- Do **not** title the paper “80% unseen Urdu IR” unless H041+ Success@5 actually reaches that band

**Sufficient for an “~80% usefulness” sentence:**  
Only if **H041+** Success@5 is **≥ 0.80** under the frozen 10C rubric, with n=78 still ≥ 0.8718. Treat 0.80 as a **hope**, not a gate to cheat toward.

---

## 10. Exact files to create later (not now)

| Path | When |
|---|---|
| `experiments/phase11_roman_query_side/PHASE11_SEALED_PROTOCOL.md` | Copy of this design, status APPROVED |
| `run_phase11_inventory.py` | Train roman counts; ASCII tokens in **train sources** only |
| `VARIANT_TABLE.json` / `LOANWORD_TABLE.json` | Frozen, with provenance |
| `USER_ROMAN_PROXY_TRAIN.csv` | Train-only proxy |
| `run_phase11_ablation.py` | M0–M4; persist Top-5; n=78 + train metrics |
| `ABLATION_RESULTS.md` / `SELECTED_METHOD.json` | After runs |
| `experiments/phase12_new_unseen/` | H041+ protocol **after** selection |

---

## 11. What you should do next (beginner path)

**This week (no code that searches H queries, no H041+):**

1. **Approve or edit this plan** (especially the 68/78 hard gate and “query-side only”).  
2. After approval, run a **table-building inventory only**: how many train rows are `roman_urdu`; which Latin tokens appear in train source articles. No BM25 search on H001–H040.  
3. Freeze `VARIANT_TABLE` / `LOANWORD_TABLE` from that inventory.  
4. Only then approve **Phase 11 retrieval ablations** (M0–M4) on train + n=78.

**Do not do next:**

- Re-label H001–H040  
- Add `diesel` to the dictionary by hand  
- Create H041+ before the method is frozen  
- Turn on Headline fusion or a reranker “to get 80%”

**How to talk about 80% to a supervisor:**  
“We already have 87% known-item on n=78. Human Success@5 on the diagnostic traps was 62.5% and those 40 queries are burned for tuning. Phase 11 will try a query-side Roman fix on train data without touching the official index. If it passes the 87.18% gate, we will test once on 40 **new** queries. We will report whatever Success@5 we get; we will not tune toward 80% on the test.”
