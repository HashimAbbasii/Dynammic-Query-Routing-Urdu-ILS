# Phase 12 — new genuinely unseen evaluation (design only)

**Status:** DESIGN / SEALED PROTOCOL. Do not generate queries. Do not retrieve. Do not label. Do not modify M0.

**Official system:** M0 (Phase 9 freeze). Phase 11 did not replace it.

**Does not replace:** Phase 9 `HELD_OUT_*` files, n=78 ExactSource 0.8718, or Phase 10C 62.5% Success@5 on H001–H040.

H001–H040 stay a **historical diagnostic** human baseline. They are **not** the Phase 12 test set.

---

## 0. Beginner summary (what Phase 12 is for)

We already know two genuine numbers:

1. On **title-derived known-item** queries used in development, the frozen system found the exact source article in the Top-5 for **68 of 78** queries (**87.18%**).
2. On **H001–H040**, a human judged the Top-5 useful (A or B) for **25 of 40** queries (**62.5%**). Those 40 queries are now “used up” for a clean test.

Phase 12 does **not** change the search engine. It builds a **new** test so we can say, honestly, how M0 does on queries nobody used for design or labeling.

We will **not** chase 80%. If the new human score is 55% or 70%, we report that number.

---

## 1. Purpose

Phase 12 is a **sealed evaluation of frozen M0** on **new** queries.

Two different questions must stay separate:

| | A. Known-item | B. Human usefulness |
|---|---|---|
| Question | Did the **exact** source article land in Top-5? | Is **any** Top-5 article A or B for this user need? |
| Gold | `source_doc_id` assigned **when the query is written** | No gold document; A/B/C/D/E on retrieved rows |
| Primary metric | ExactSource Hit@5 | Success@5 |
| Must not be called | “human accuracy” | “ExactSource Hit@5” or “87.18%” |

**Decision — do both, as two sealed subsets (Option C).**

- **Subset K (known-item):** new title-derived queries with `source_doc_id`. Answers: “Does 87.18% hold on a **new** known-item sample, not the n=78 pool?”
- **Subset U (usefulness):** new naturalistic queries **without** `source_doc_id`. Answers: “What is M0’s **clean** human Success@5?” (H001–H040 cannot answer this anymore.)

This is the best master’s / IEEE package: one objective unseen known-item table, one graded unseen usefulness table, neither mixed into one fake “accuracy.”

Do **not** evaluate M1–M4 in official Phase 12. M1 did not improve known-item Hit@5. Optional later appendix would need its **own** protocol and must not be used to pick a winner after seeing U/K scores.

---

## 2. System under test (frozen)

Evaluate **M0 only**:

- URDU/MIXED → Urdu BM25  
- ROMAN → Method D romanized-document BM25  
- Unicode script detector  
- k1=1.5, b=0.75, top_k=50  
- Corpus `data/clean_articles.csv`, 111,860 rows  
- SHA-256 `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231`  
- Dictionary file 198 keys, **not edited**

No BM25 retune, no routing change, no Method D document change, no query-side M1 expansions in the official run.

Persist **Top-50** (ids, ranks, scores) and **Top-5** (headline + snippet). Do not repeat the Phase 9 logging omission.

---

## 3. New query set (not H001–H040)

**Namespaces (recommended):**

- Known-item: **K001–K040**  
- Usefulness: **U001–U040**  

Do **not** continue H041–H080 if that invites pooling with H001–H040. If IDs must stay `H*`, start at **H041** but **never** average them with H001–H040.

**Total: 80 queries** (40 + 40).  
Human labels only on subset U (about 200 Top-5 rows). Subset K is scored automatically from `source_doc_id`.

That is realistic for one annotator and comparable to Phase 10C’s 40-query human set, plus a matched-size known-item unseen set.

### 3.1 Why not 50 / 60 / 80 human-only?

| Size | Human Top-5 labels (≈5 each) | Verdict |
|---|---|---|
| 40 usefulness only | ~200 | Valid but **no** clean unseen known-item number |
| 50–60 usefulness | 250–300 | Better CI; still no new ExactSource unseen |
| 80 usefulness | ~400 | Heavy for MS; still misses unseen known-item |
| **40 K + 40 U** | **~200 human + 40 automatic** | **Recommended** |

40-query Success@5 has a wide confidence interval. That is acceptable if we **do not** over-claim precision (“exactly 80%”). IEEE can report n, hits, and a binomial interval.

### 3.2 Construction quotas (pre-registered; not copied from H failures)

Quotas are **type counts**, not “write another diesel/temperature trap.” Do **not** open H001–H040, 10C qrels, or MiniLM templates while writing K/U text.

**Subset K (n=40) — title-derived known-item**

- Script (by Unicode detector after writing, not by forcing): target **~22 Urdu, ~12 Roman (`title_roman` style), ~6 MIXED** if mixed occurs naturally; if MIXED is rare, keep Roman/Urdu and **do not** glue `Pakistan news update`.
- Length: mix of short titles (3–8 tokens) and slightly longer titles (9–14). No requirement to match trap SHORT/LONG.
- Source articles: rows **not** used as `source_doc_id` in `QTRN_001`–`QTRN_260`. Prefer unused headlines.
- Query ≈ shortened/paraphrased **headline or lead**, in the same spirit as Phase 2 known-item (not chat questions).
- Creator **may see** the source article (required to assign `source_doc_id`).
- Creator **must not** run BM25 while writing.

**Subset U (n=40) — naturalistic, no gold id**

Target (counts are ±1 if a cell is impossible without copying old traps):

| Slot | n | Notes |
|---|---|---|
| Urdu | 18 | Natural information needs in Urdu script |
| Roman Urdu | 18 | Chat-style Roman, **not** forced to be Phase 2 `title_roman` |
| MIXED (both scripts in one string) | 4 | Real mixed (e.g. one English name + Urdu), **not** the old template suffix |
| Short (≤5 tokens) | 12 | Underspecified user queries are allowed; do not harvest H examples |
| Medium (6–12) | 16 | |
| Long (13+) | 12 | Explanatory / “review” style |
| Factoid (one fact: price, score, fixture, who/when) | 14 | Include **4** temporal (`آج` / `aaj` / `موجودہ` / `mojooda`) — not 10/40, not zero |
| Explanatory (why / how / effects) | 14 | |
| Named entity / person-team-place heavy | 12 | Overlap with the rows above is allowed; the three need-types should sum to 40 |

Categories (Sports, Business, Entertainment, Science/Tech, other): aim for **diversity**, not a copy of any old trap sheet.

**Banned while writing U/K:**

- Reading H001–H040 query strings or 10C labels  
- MiniLM `heldout_retrieval_template.csv`  
- Adding dictionary/test terms to “stress” Method D  
- Rewriting a query after seeing retrieval  
- Inventing `source_doc_id` for subset U  

Details: `QUERY_GENERATION_PROTOCOL.md`.

---

## 4. Gold and relevance

### 4.1 Who writes queries

Student (thesis author) writes K and U under this protocol. Supervisor may check that **quotas and bans** were followed, not that scores look good.

### 4.2 Subset K — `source_doc_id`

- Assigned **at creation**, equal to the corpus row that inspired the query.  
- Integer in `[0, 111859]`.  
- **Never** assigned or changed after retrieval.  
- If a draft has no clear source, **drop it**; do not guess after search.

### 4.3 Subset U — no source gold

- `source_doc_id` empty.  
- Do not pick a “best” article from the corpus as hidden gold.

### 4.4 Human labels (subset U only)

Reuse Phase 7 **A/B/C/D** and **E = AMBIGUOUS** (article-level, only if A–D cannot be decided from headline+snippet).

Apply the Phase 10C rules that are **not** H-id-specific:

- Judge **raw** `query_text` (no QTRN suffix stripping).  
- Temporal: `query_asks_today=1` for `آج` / `aaj` / `موجودہ` / `mojooda`; **A** = type of fact for a dated occasion **in the article**, not the annotator’s calendar day.  
- A vs B: prefer B unless the need is clearly satisfied.  
- B vs C: B only if the article helps answer the asked need.  
- Do not search for a better document. Do not pad missing hits.

Annotate **after** the sealed retrieval dump exists. Empty `relevance_label` until then.

### 4.5 Metrics

**Subset K (primary / secondary):**

| Role | Metric |
|---|---|
| **Primary** | ExactSource Hit@5 |
| Secondary | ExactSource Hit@1, MRR, nDCG@5 (known-item graded by rank of the source) |

If `n_hits < 5`, Hit@5 is still 1 iff source rank ≤ 5.

**Subset U (primary / secondary):**

| Role | Metric |
|---|---|
| **Primary** | Success@5 = (# queries with ≥1 **A or B** in retrieved Top-5) / 40 |
| Secondary | Conservative P@5 = mean(count of **A** / 5) |
| Secondary | Variable P@5 = mean(count of **A** / min(5, n_hits)) |
| Secondary | All-D query rate; A/B/C/D/E counts |
| Optional | Graded nDCG@5 with gains A=3, B=2, C=1, D=E=0 (report as optional; not mixed with known-item nDCG) |

Do **not** compute ExactSource Hit@5 on U. Do **not** compute Success@5 on K unless a later protocol adds human labels on K (not required).

n=78 **0.8718** stays the **development/validation** known-item result. Phase 12 K is a **new** number with its own n=40.

---

## 5. Contamination firewall

1. Freeze M0 **before** K/U files are finalized (already true).  
2. Write and **seal** `queries_k.csv` / `queries_u.csv` (checksum) **before** any Phase 12 search.  
3. One retrieval pass per subset (or one joint pass). Persist full Top-50.  
4. **No** query edits after seeing ranks.  
5. **No** BM25/dict/routing/M1 changes after seeing Phase 12 scores.  
6. If the system changes later, Phase 12 K/U are **burned** for that new system; a **third** unseen set is required.  
7. Do not use H001–H040 to choose which U queries to write or drop.  
8. Do not mix H001–H040 Success@5 with U Success@5 into one “unseen” average.  
9. Phase 9 directory remains **read-only**.

---

## 6. Folder structure (create now: protocol only)

```
experiments/phase12_new_unseen_evaluation/
    README.md                          (this overview)
    PHASE12_SEALED_PROTOCOL.md         (this file may be copied as the freeze)
    QUERY_GENERATION_PROTOCOL.md
    annotation/
        README.md                      (label after dump; empty until then)
    artifacts/                         (preflight.json later; empty now)
    # later, after approval of QUERY WRITING:
    #   queries_k.csv
    #   queries_u.csv
    #   SEAL.json
    # later, after approval of RUN:
    #   run_phase12.py
    #   TOP50_K.csv / TOP5_K.csv
    #   TOP50_U.csv / TOP5_U.csv
    #   U_QRELS.csv
    #   PHASE12_RESULTS.md
```

`run_phase12.py` is **not** written in this design step.

---

## 7. Valid vs invalid claims after Phase 12 (once executed)

**Valid (fill in X after the run):**

- “On the Phase 2 development/validation known-item set, ExactSource Hit@5 = 68/78 = 0.8718.”  
- “On a **new** sealed known-item set K001–K040, frozen M0 ExactSource Hit@5 = X/40.”  
- “On H001–H040 (diagnostic, not clean unseen), frozen M0 human Success@5 = 25/40 = 0.625.”  
- “On a **new** sealed naturalistic set U001–U040, frozen M0 human Success@5 = Y/40.”  

**Invalid:**

- “87.18% accuracy on unseen queries.”  
- “87.18% human relevance.”  
- “The system achieved ~80% unseen” unless Y/40 (or a pre-registered metric) is actually ≥ 0.80.  
- Averaging 0.8718 with Success@5.  
- Calling H001–H040 the Phase 12 unseen set.  
- Calling M1 the official system because it “won” a no-lift ablation.

Preserve validity over a high headline number.

---

## 8. Stop (this design step)

Stop **before**:

- writing K001–K040 / U001–U040  
- running BM25  
- labeling  
- changing M0  

**Next action after this protocol is approved:** follow `QUERY_GENERATION_PROTOCOL.md` and write the two CSV query lists only — still **no retrieval**.
