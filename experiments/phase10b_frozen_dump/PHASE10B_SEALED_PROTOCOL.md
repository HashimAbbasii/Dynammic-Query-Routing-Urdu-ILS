# Phase 10B — sealed protocol

**Status:** APPROVED for execution (2026-08-27). Execute the frozen-system dump only. Do not start Phase 10C.  
**Date:** 2026-08-27  
**Does not replace Phase 9.** Does not change the frozen architecture. Does not invent `source_doc_id`. Does not copy MiniLM / `heldout_retrieval_template.csv` labels.

This document is the next valid experimental step after Phase 10A. It is a **new diagnostic experiment**, not a second Phase 9 pass.

---

## 1. Current verified status

### 1.1 Official frozen evaluation (Phase 9) — unchanged

| Item | Value |
|---|---|
| Architecture | URDU/MIXED → Urdu BM25; ROMAN → Method D romanized-document BM25 |
| Detector | Unicode script counts (not SVM) |
| BM25 | `k1=1.5`, `b=0.75` |
| `top_k` | 50 |
| Dictionary | 198 keys |
| Corpus | `data/clean_articles.csv`, 111,860 rows |
| Corpus SHA-256 | `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231` |
| Development ExactSource Hit@5 | **68/78 = 0.8718** on Phase 2 `dev` + `internal_val` (`QTRN_*`) |
| H001–H040 official ExactSource Hit@5 | **undefined** (`n_scored=0`, `n_excluded=40`, reason `no_source_doc_id`) |
| Phase 9 logging | `top1_doc_id` only; Top-50 existed in memory and was discarded |

Do **not** report H001–H040 Hit@5 as 0.00, 0.8718, or ~80%. There is no official known-item score on that set.

### 1.2 What Phase 10A recovered

File: `artifacts/phase10/HELD_OUT_RETRIEVAL_DETAILS.csv` (40 rows).

Per query: `query_text`, `detector_label`, `retrieval_path`, **rank-1** `doc_id`, headline, 500-character snippet, `n_hits_returned_phase9`.

Ranks 2–5 of the official Phase 9 lists **were not persisted** and **cannot be reconstructed** without another retrieval pass. H036 originally returned **1** hit.

No A/B/C/D labels were assigned.

### 1.3 Contamination already incurred (must be stated)

H001–H040 query text and rank-1 documents are now open. Qualitative diagnosis from rank-1 is therefore **not fully blinded**.

This does **not** invalidate Phase 9 (known-item metric was never defined on these IDs).  
It **does** forbid using H001–H040 as a tuning loop, and it **does** forbid claiming a later improved score on the same 40 IDs as a clean unseen test.

---

## 2. What is scientifically measurable right now

Without another retrieval pass:

1. **Development known-item performance** — 0.8718 ExactSource Hit@5 on n=78. This is a real, frozen number. It measures “did the title-derived source row appear in Top-5?”, not human usefulness of trap queries.
2. **Routing on H001–H040** — detector 20 URDU / 20 ROMAN; paths 20 `urdu_bm25` / 20 `roman_bm25_method_D`. Matches the trap-file script field. **No routing error is visible.**
3. **Rank-1 inspection** — 40 query–document pairs from the official run. This can support **hypotheses** about failure type. It cannot support P@5, nDCG@5, Success@5, or “relevant in Top-5”.
4. **Coverage holes in the original lists** — H027 returned 8 hits; H036 returned 1. Those counts are Phase 9 facts.

Not measurable now:

- Human P@5 / Success@5 on H001–H040
- Whether a relevant document sits at ranks 2–5
- Official known-item Hit@5 on H001–H040 (no gold ids; must not be invented)

---

## 3. What is missing

| Missing item | Why it matters |
|---|---|
| Phase 9 ranks 2–50 and BM25 scores | Logging omission; not recoverable from disk |
| Human relevance labels on frozen-system Top-5 | Needed for a genuine usefulness score on trap queries |
| A development **human-relevance** pool that is not H001–H040 | Needed if the system will be changed before claiming ~80% |
| A **new** unseen query set after any system change | H001–H040 are no longer a clean test for improved systems |
| Temporal metadata aligned to “آج / aaj” queries | Several H queries ask for “today” against a static undated archive |

`validate/dual_index_routing/labels/heldout_retrieval_template.csv` is **not** a substitute. It is MiniLM HEADLINE/FULL_CONTENT with old relevance strings. Example: H001 Phase 9 rank-1 is `77997`; template HEADLINE rank-1 is `2612`. Forbidden as gold.

---

## 4. Rank-1 failure hypotheses (not labels)

These are **locked hypotheses** from Phase 10A rank-1 only. They are not A/B/C/D judgments. They must not be used to drop queries or to pick a winner on H001–H040.

### 4.1 Routing

**Not implicated.** All 40 detector labels match the designed script. Failures below are retrieval / query–corpus, not the Unicode router.

### 4.2 Dominant pattern: Roman path + English or variant spelling

Method D keeps the **query in Latin** and romanizes **documents**. Query tokens such as `temperature`, `iphone`, `diesel`, `rate`, `football`, `stock`, `points`, `max`, `Asia` match only if a document token romanizes to that exact Latin string. Character romanization of `ڈیزل` is in the `d`/`i`/`z`/`l` family (not the English word `diesel`). That is a **closed Method D property**, already flagged in Phase 8 `FUTURE_WORK.md` item 3 (naturalistic Roman ≠ `title_roman`).

Rank-1 pairs that look like this class (hypothesis):

| ID | Query | Rank-1 headline (compressed) | Likely category |
|---|---|---|---|
| H010 | `shikast ki waja` | OGRA petrol price summary | Roman spelling / weak overlap (`waja` vs `وجہ`) |
| H016 | `rupay girawut ke nataij` | ODI rankings | Roman spelling (`girawut`) + generic tokens |
| H025 | `aaj lahore ka temperature kya hai` | Amir Khan boxing (“اج”) | English loanword `temperature`; `aaj`→`اج` collision |
| H027 | `Asia cup final kab khela jayega` | Kaaba ghilaf; n_hits=8 | English `Asia`/`cup`; possible `kab`→`کعب` collision |
| H028 | `naya iphone pakistan mein kab aaya` | **Same** Kaaba doc `18668` | English `iphone`; `kab` collision |
| H029 | `aaj karachi max temperature kitna raha` | Same boxing as H025 | English `max`/`temperature` |
| H032 | `aaj stock exchange kitne points par` | Bank of England **points** cut | English `stock`/`points` |
| H036 | `diesel rate` | Aamir Khan *Dhoom* game teaser; n_hits=1 | English `diesel`/`rate`; almost empty posting list |
| H040 | long Roman cricket / selectors / form | Karachi Chamber–Japan MoU (`حکمت عملی`) | `hikmat e amli` matched business “strategy”; cricket tokens weak |

### 4.3 Short-query ambiguity / generic BM25

H001–H008 are 3–4 word Urdu “LONG need” traps. Rank-1 is often **same topic, wrong specificity** (petrol story vs “why expensive”; some flood/inflation/cricket overlap). This is expected BM25 behavior on underspecified queries. It is **not** proof of Top-5 failure.

Notable lexical traps (hypothesis, rank-1 only):

| ID | Mechanism |
|---|---|
| H003 `فلم کیسے ڈوبی` | Title token `ڈوبی` (*Jawani Le Doobi*), not “film flopped” |
| H005 `ٹیم ہار کا تجزیہ` | Homograph `ہار` (necklace in “گلے میں ہار”) vs “loss” |
| H007 `فلم فیل کی کہانی` | Homograph `فیل` (turkey in *Free Birds*) vs English “fail” |
| H013 `team haar ka tajzia` | Same `haar` / `ہار` issue on the Roman path |

### 4.4 Semantic / named-entity / corpus mismatch

| ID | Hypothesis |
|---|---|
| H008 | `روپے` matched Indian rupee story; likely PKR intent |
| H012 | `flood` matched Chennai flood, not necessarily Pakistan |
| H020 | `آئی فون` rank-1 is a kids’ smartphone / browser story |
| H021 | `حرارت` rank-1 is Antarctica record temperature, not Karachi |
| H017, H018, H024, H025, H026, H029, H032 | `آج` / `aaj` against a **static archive** with no query timestamp — “today” is not a well-posed known-item |

Urdu factoid controls H033 `ڈیزل ریٹ`, H034 `سونا ریٹ` look **on-topic at rank-1**. H035 `football score` looks on-topic (Champions League). The Roman twin H036 does not. That contrast is evidence that **script path + English tokens**, not the information need, drives the worst misses.

### 4.5 What rank-1 cannot tell us

Several Urdu rows (H004, H006, H018, H019, H022, H023, H033, H034, H038) look plausibly useful at rank-1. That is **not** ~80% system performance. One document is not Top-5, and “looks related” is not a frozen rubric label.

---

## 5. Proposed new sealed evaluation protocol

### 5.1 Experiment identity

**Name:** Phase 10B — Frozen-system retrieval dump (diagnostic).  
**Optional successor:** Phase 10C — Human relevance on the 10B Top-5 (separate protocol, after 10B artifacts exist).  
**Out of scope until a later freeze:** any BM25, dictionary, tokenizer, romanizer, fusion, or dense-index change.

Phase 9 folder, CSVs, JSON, and `PHASE9_RESULTS.md` are **read-only**.

### 5.2 Scientific purpose

1. Persist complete Top-5 (and Top-50) lists from the **same frozen code** so human evaluation becomes possible.  
2. Treat those lists as **Phase 10B artifacts**, not as a rewrite of Phase 9 ranks.  
3. Sanity-check that 10B rank-1 `doc_id` equals Phase 9 `top1_doc_id` for all 40 queries (or document any tie-order mismatch without “fixing” it).  
4. Measure **current** frozen-system usefulness later (10C), without using that measurement to retune the same 40 IDs.

### 5.3 What this experiment is not

- Not official ExactSource Hit@5 on H001–H040.  
- Not a second Phase 9.  
- Not authorization to change Method D after seeing H036.  
- Not a claim that 10B ranks **are** the historical Phase 9 Top-50 (they are a **replay** of the frozen system; rank-1 must be compared to the saved official top-1).

### 5.4 Data split (must stay explicit)

| Pool | IDs | Role in 10B/10C | Role in any later system change |
|---|---|---|---|
| Development / validation | `QTRN_*` n=78 (`dev` + `internal_val`) | Not re-scored as the 10B headline result | **Only** pool allowed for selecting improvements |
| Train (unused for freeze) | Phase 2 `train` | Unused | May supply extra **development** queries if pre-registered; never mix into H scores |
| Diagnostic held-out | H001–H040 | 10B dump + (later) 10C labels | **Do not tune on.** After 10C, do not iterate and re-report these 40 as unseen |
| Future unseen | **Not yet created** (e.g. H041+ or a new sample) | None | Required if an improved system will be claimed at ~80% |

SHORT/LONG in `heldout_traps.py` is a **routing-trap protocol label**, not an IR gold document.

### 5.5 Frozen system for the dump (byte-identical intent)

Reuse Phase 9 / Phase 5 code paths:

- Corpus, hash, `n_docs=111860`, dictionary 198 keys, `k1`, `b`, tokenizer, `detect_script`, Method D `romanize_token`, Urdu vs roman indexes.  
- Query strings: `HELDOUT_TRAPS` field `query` only. No rewriting.  
- `top_k=50`. Write ranks 1–5 for annotation and ranks 1–50 for audit.  
- If `len(hits) < 5`, write the actual rows only; do not pad with invented documents. H036 is expected to have 1 row if replay matches Phase 9 coverage.

Preflight must pass **before** search, same checks as Phase 9 `preflight.json`.

### 5.6 Rank-1 consistency rule

After the dump:

- Compare 10B rank-1 `doc_id` to `experiments/phase9_heldout_evaluation/HELD_OUT_PER_QUERY.csv` `top1_doc_id`.  
- **If 40/40 match:** 10B Top-5 is accepted as a frozen-system replay with verified rank-1 identity. Still **do not** overwrite Phase 9 files.  
- **If any mismatch:** record query id, both doc ids, both scores if available. Do **not** rerun until a mismatch, do **not** pick the “better” document, do **not** declare Phase 9 invalid unless the mismatch is shown to be a code/corpus hash failure. Human 10C uses the 10B lists and reports the mismatch count.

### 5.7 Metrics allowed in 10B (dump phase)

10B itself publishes **no IR quality score**. Allowed outputs:

- Per-hit rows (ids, ranks, scores, text)  
- `n_hits_returned`  
- Rank-1 match rate vs Phase 9  
- Detector/path counts (should duplicate Phase 9)

Forbidden in 10B:

- ExactSource Hit@5 on H001–H040  
- Copying template relevance  
- Guessing `source_doc_id`  
- P@5 from the author of this protocol

### 5.8 Phase 10C (human relevance) — sealed, after 10B only

Run **only** after 10B artifacts exist and this protocol (or a short 10C addendum) is approved.

- Judge **10B Top-5** (or fewer if `n_hits < 5`), not MiniLM lists, not corpus search.  
- Reuse Phase 7 primary labels **A RELEVANT / B PARTIALLY_RELEVANT / C TOPICALLY_RELATED / D NOT_RELEVANT** (and E only as in the Phase 7 rubric).  
- **Do not** apply Phase 7 §2 QTRN suffix-stripping to H queries (those suffixes are a QTRN generation artifact). Judge the raw H query text.  
- **Temporal rule (pre-registered):** For queries containing `آج` / `aaj` / `موجودہ` / `mojooda`, RELEVANT means the article states the asked **type of fact** (price, temperature, index, fixture) for a **specific dated occasion in the article**, not “correct for the calendar day of annotation.” Record `query_asks_today=1`. Do not fail every archive hit solely because the corpus is not live.  
- Primary 10C metrics (report all; do not pick the largest):  
  - **Success@5** = fraction of queries with ≥1 A or B in the retrieved list  
  - **P@5** = mean (count of A among up to 5 hits / 5), with a footnote that lists shorter than 5 use denominator 5 (conservative) **and** a variant using `min(5, n_hits)`  
  - Counts of queries whose entire list is D  
- 10C is the **baseline human score of the frozen system**. It is **not** a license to change BM25 and re-label the same lists.  
- Annotator must not see trap SHORT/LONG gold, SVM outputs, or `heldout_retrieval_template.csv` labels.

### 5.9 Path to ~80% genuine performance (without contaminating evaluation)

**Clarify the target metric first.** 0.8718 is already above 80%, but it is ExactSource Hit@5 on title-derived `QTRN_*`. That is **not** the same as human Success@5 on H001–H040 (short traps, factoids, naturalistic Roman, English tokens, “today”).

Valid sequence:

1. **Measure the frozen system** (10B dump → 10C labels). That number is genuine for **this** system on **these** queries. It may be far from 80% if Roman/English failures dominate.  
2. **Do not chase 80% by editing H001–H040 results.**  
3. **Pre-register improvement classes** from §4 and from n=78 Phase 6 taxonomy **before** implementing anything. Allowed development evidence: QTRN Roman n=23, Phase 6 residuals, train titles. **Disallowed:** adding dictionary rows because H036 is `diesel rate`.  
4. **Select** any change on development only (primary: n=78 ExactSource Hit@5 must not collapse; secondary: a **new** development human or proxy set, not H).  
5. **Confirm** the chosen system **once** on a **new** held-out sample (new IDs). Optionally report 10C as historical baseline of the old system.  
6. If no new held-out set is collected, the thesis may claim: frozen known-item 87.18% on n=78; frozen human Success@5 on H001–H040 from 10C; improvements only as development results. It may **not** claim “80% on unseen H001–H040 after we fixed Roman.”

Likely genuine levers (hypotheses for **later** phases, not to implement now):

- Roman user-query normalization / English loanword handling (development Roman only)  
- Homograph-unaware BM25 (`ہار`, `فیل`) — probably not fixable by routing  
- Date-aware retrieval for `آج` — needs corpus dates; Phase 8 already listed this as future work  
- Do **not** expect routing changes to move H performance; rank-1 shows the router already matched script

---

## 6. Exact files / scripts to create (after approval only)

Do **not** create or run the dump script until this protocol is approved.

### 6.1 Phase 10B (this experiment)

| Path | Role |
|---|---|
| `experiments/phase10b_frozen_dump/README.md` | Entry point: diagnostic dump; Phase 9 read-only |
| `experiments/phase10b_frozen_dump/PHASE10B_SEALED_PROTOCOL.md` | This file (frozen at approval) |
| `experiments/phase10b_frozen_dump/PREFLIGHT_CHECKLIST.md` | Same gates as Phase 9 plus “will not write into `phase9_heldout_evaluation/`” |
| `experiments/phase10b_frozen_dump/run_phase10b.py` | Rebuild indexes; search H001–H040; persist Top-50; **do not** compute Hit@5 |
| `experiments/phase10b_frozen_dump/artifacts/preflight.json` | Hash, n_docs, dict keys, k1/b, Python/NumPy/pandas, git commit |
| `experiments/phase10b_frozen_dump/artifacts/run_manifest.json` | Experiment id `phase10b_frozen_dump`, `replaces_phase9: false`, corpus hash, code entry `run_phase5.BM25` |
| `experiments/phase10b_frozen_dump/TOP50_RETRIEVAL.csv` | One row per (query, rank): ids, score, path, detector |
| `experiments/phase10b_frozen_dump/TOP5_FOR_ANNOTATION.csv` | Ranks 1–5 (or fewer) with headline + snippet |
| `experiments/phase10b_frozen_dump/RANK1_VS_PHASE9.csv` | Per-query Phase 9 top-1 vs 10B top-1, match flag |
| `experiments/phase10b_frozen_dump/PHASE10B_RESULTS.md` | Dump report only; no human P@5 |

**Required columns for `TOP50_RETRIEVAL.csv`:**  
`experiment_id, query_id, query_text, detector_label, retrieval_path, rank, doc_id, bm25_score, n_hits_returned`

**Required columns for `TOP5_FOR_ANNOTATION.csv`:**  
`experiment_id, query_id, query_text, detector_label, retrieval_path, rank, doc_id, bm25_score, headline, news_text_or_snippet, n_hits_returned`  
plus empty `relevance_label` (fill only in 10C).

`experiment_id` must be the constant `phase10b_frozen_dump`.

### 6.2 Phase 10C (later; do not start in 10B)

| Path | Role |
|---|---|
| `experiments/phase10c_human_relevance/ANNOTATION_ADDENDUM.md` | H-query rules including the temporal rule in §5.8 |
| `experiments/phase10c_human_relevance/run_phase10c_metrics.py` | Metrics from labels; no retrieval |
| `experiments/phase10c_human_relevance/HELD_OUT_QRELS.csv` | Filled A/B/C/D/E |
| `experiments/phase10c_human_relevance/PHASE10C_RESULTS.md` | Human baseline of **frozen** system |

### 6.3 Forbidden writes

- Any file under `experiments/phase9_heldout_evaluation/` except read  
- Overwriting `artifacts/phase10/HELD_OUT_RETRIEVAL_DETAILS.csv` (keep 10A as the rank-1 recovery record)  
- Using `heldout_retrieval_template.csv` as input to the dump  

---

## 7. Stop conditions

1. Phase 10B dump executed once after explicit approval (2026-08-27).  
2. No system change. No dictionary edit. No BM25 retune.  
3. No A/B/C/D labels in 10B.  
4. Preflight passed; retrieval ran once.  
5. Stop for Phase 10C approval before any labeling.

---

## 8. Approval checklist (human)

- [x] Phase 9 remains the official known-item evaluation (Hit@5 undefined on H001–H040).  
- [x] 10B is a **new** frozen-system dump, not a Phase 9 rewrite.  
- [x] Improvements, if any, will be selected on n=78 / other development data, not on H001–H040.  
- [x] A claim of ~80% after a system change requires a **new** unseen set, or must be limited to development results plus the frozen 10C baseline.  
- [x] `heldout_retrieval_template.csv` will not be used as gold.

**Approved and executed.** Do not start Phase 10C until separately approved.
