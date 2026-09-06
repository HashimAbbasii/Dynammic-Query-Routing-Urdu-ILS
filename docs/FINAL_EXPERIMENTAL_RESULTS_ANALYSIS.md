# Final experimental results analysis (frozen M0)

**Status:** Analysis only. No retrieval. No tuning. No change to M0.  
**Official system:** M0 (Phase 8/9 freeze). Phase 11 did not replace it.  
**Date of this write-up:** 27 August 2026.

This document is thesis-ready source text for Results, Discussion, Limitations, and Future Work. It uses only frozen, already-reported numbers. It does not average them, hide the naturalistic result, or claim 80%.

---

## 0. Official frozen system (M0)

- URDU / MIXED → Urdu BM25  
- ROMAN → Method D romanized-document BM25  
- Unicode script-count detector  
- BM25 \(k_1=1.5\), \(b=0.75\), \(\mathrm{top}_k=50\)  
- Corpus: `data/clean_articles.csv`, \(n=111{,}860\)  
- Corpus SHA-256: `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231`  
- Dictionary: 198 keys (unchanged)

Phase 11 models M1–M4 were query-side ROMAN expansions only. None improved n=78 ExactSource Hit@5. **M0 remains the official system.**

---

## 1. What each frozen number actually proves

### 1.1 Phase 2 development/validation — 68/78 = 87.18% ExactSource Hit@5

**What was measured.** Title-derived known-item queries `QTRN_*` on the Phase 2 **dev + internal_val** pool (\(n=78\)). Gold is `source_doc_id`. Success means the **exact source article** appeared in the Top-5.

**What it proves.** On this development/validation known-item set, script-aware lexical retrieval (Urdu BM25 + Method D for Roman) found the designated source in the Top-5 for 68 of 78 queries. On the same pool, raw Urdu BM25 without a Roman path was 0.5897 Hit@5; Method A (raw BM25 on Roman queries) was **0/23** on the Roman subset. Method D recovered **22/23** of those development Roman known-items (Phase 5).

**What it does not prove.**

- It is **not** accuracy on unseen user queries.  
- It is **not** human usefulness (A/B in Top-5).  
- It is **not** the H001–H040 result.  
- It is **not** the Phase 12 K or U result.

Phase 5 already recorded that QTRN Roman strings are Phase 2 **`title_roman`** (dictionary reverse + character romanization), **not** naturalistic chat Roman Urdu. That construction matches Method D’s document romanization more closely than ordinary user Roman. The 87.18% figure is therefore a **strong development known-item ceiling for title-like queries**, not a forecast of chat-style Roman performance.

### 1.2 Phase 12 K001–K040 — 27/40 = 67.50% ExactSource Hit@5

**What was measured.** A **new** sealed known-item set. Each query has a `source_doc_id` assigned **at creation**, from headlines not used as QTRN sources. Same metric as §1.1: exact source in Top-5. Frozen M0, one retrieval pass.

Secondary (same task): Hit@1 = 20/40; Hit@10 = 28/40; Hit@50 = 30/40.

**What it tells us.** The 87.18% development result **does not automatically transfer** to a new title-like known-item sample. 67.5% is still well above random Top-5 in a 111,860-document collection, but it is a **lower independent known-item estimate**.

By detector on K (descriptive, not a tuning signal):

- URDU path: 26/28 ExactSource Hit@5  
- ROMAN path: 1/12 ExactSource Hit@5  

The drop from 87.18% to 67.50% is concentrated on **ordinary Roman Urdu title queries**, not on Urdu-script titles. Development Roman queries were `title_roman`; Phase 12 K Roman queries were ordinary Roman Urdu of the headline. That is a **query-form shift** on the Roman path, not a failure of Urdu BM25.

**What it does not prove.** Human Success@5. It must not replace 68/78. It must not be averaged with U.

### 1.3 Phase 12 U001–U040 — 23/40 = 57.50% human Success@5

**What was measured.** New sealed **naturalistic** queries with **no** `source_doc_id`. Frozen M0 Top-5, then Phase 7 A/B/C/D/E labels (**A1**, official). Success@5 = at least one **A or B** in the retrieved Top-5. Official Success@5 remains **23/40**. An independent second annotation (A2) is a reliability check only and does not replace A1.

Also: conservative P@5 = 0.2050 (mean of A-count/5); nDCG@5 = 0.6460 (gains A=3, B=2, C=1, D=E=0); MRR = 0.4542 (first A or B).

**What it tells us.** For queries a bilingual news user might type, frozen M0 was **useful** (A or B in Top-5) for **23 of 40** queries. Conservative precision is low: many successes are a single B, not five A’s. nDCG@5 **overstates** usefulness because C has gain 1 (an all-C list can have nDCG@5 = 1.0 with no A/B).

Script split (detector; Success@5):

| Script | Success@5 |
| --- | --- |
| URDU | 17/18 = 94.44% |
| ROMAN | 6/18 = 33.33% |
| MIXED | 0/4 = 0% |

**What it does not prove.** ExactSource Hit@5 (there is no gold document). It is not 87.18%. It is not 80%.

### 1.4 Phase 10C H001–H040 — 25/40 = 62.50% Success@5 (diagnostic only)

Same human metric as U, **different query set**. H001–H040 were routing-trap strings, later replayed and labeled. Query text, rank-1, and labels are now **known**. They are **contaminated** for tuning and **must not** be presented as the official unseen human result. Phase 12 U is the clean naturalistic number.

Do **not** average 62.5% with 57.5%.

### 1.5 Phase 11 — M1–M4 did not beat 68/78

All of M0–M4 scored **68/78** ExactSource Hit@5 on the development/validation pool. Roman-train Hit@5 stayed 61/64. M1–M4 nDCG@5 was slightly **worse** than M0. Allowed query-side spelling expansion did not move the official known-item score. **M0 stays frozen.** Phase 11 is not evidence that Roman chat queries would improve if M1 were deployed; that was never tested on a sealed unseen set.

---

## 2. Why these metrics cannot be averaged

| Result | Task | Gold | Question |
| --- | --- | --- | --- |
| 87.18% | Known-item, title-derived, **development/validation** | `source_doc_id` | Did the exact source reach Top-5? |
| 67.50% | Known-item, title-like, **new sealed K** | `source_doc_id` | Same question, new sample |
| 57.50% | Naturalistic, **new sealed U** | Human A/B | Was anything in Top-5 useful? |
| 62.50% | Naturalistic-style traps, **H001–H040** | Human A/B | Diagnostic only; set is burned |

Averaging 87.18% with 57.5% answers **no scientific question**. It mixes:

- development vs new test,  
- known-item vs graded usefulness,  
- title-derived vs chat-like needs,  
- `title_roman` vs ordinary Roman Urdu.

There is **no** single “system accuracy.”

---

## 3. Why 87.18% must not be called unseen performance

1. The n=78 pool is **dev + internal_val**, used to select Method D and freeze M0.  
2. H001–H040 have **no** `source_doc_id`; Phase 9 correctly reported ExactSource Hit@5 as **undefined** on that set.  
3. Phase 12 later measured unseen known-item Hit@5 on **K**, and it was **67.5%**, not 87.18%.  
4. Unseen human usefulness on **U** was **57.5%**, a different metric.

Valid sentence: *“On the Phase 2 development/validation known-item set, ExactSource Hit@5 = 68/78 = 0.8718.”*

Invalid sentence: *“The system achieves 87.18% accuracy on unseen queries.”*

---

## 4. Why 57.5% must not be called ExactSource Hit@5

U queries have **no** intended source document. Success@5 counts **A or B** in Top-5. A useful neighbour of the topic can succeed even if no single “right” article exists. ExactSource Hit@5 is only defined when `source_doc_id` is assigned **before** retrieval (n=78 and K).

---

## 5. Why Roman Urdu is the major weakness

Convergent evidence, **not** a licence to retune on U or K:

1. **Without Method D**, development Roman known-item Hit@5 was 0/23 (Phase 4B/5). Method D was necessary on **`title_roman`**.  
2. On **new K**, ordinary Roman title queries: ExactSource Hit@5 **1/12**, vs Urdu titles **26/28**.  
3. On **new U**, chat-style Roman: Success@5 **6/18**, vs Urdu **17/18**. MIXED **0/4**.  
4. Phase 11 query-side expansions (M1–M4) did **not** raise n=78 Hit@5, so a small spelling table is not a demonstrated fix.  
5. Development Roman success does **not** contradict (2)–(3): those QTRN strings were generated to resemble Method D’s romanization, not WhatsApp-style Roman.

The honest thesis statement is: **Urdu-script news search under M0 is strong; ordinary Roman Urdu remains the main failure mode.**

Do **not** use K/U misses to edit the dictionary or Method D. Those sets are now burned for that system.

---

## 6. Strongest scientifically defensible thesis claim

A master’s thesis can defend **all** of the following together, and should not claim more:

1. A frozen script-aware lexical system (M0) was specified before the Phase 12 query seal.  
2. On development/validation **known-item** queries, ExactSource Hit@5 = **68/78 (87.18%)**, substantially above Urdu-only BM25 (0.5897) on that pool, because Method D addresses `title_roman` script mismatch.  
3. On a **new** sealed known-item set, ExactSource Hit@5 = **27/40 (67.5%)**. Urdu titles remain high; ordinary Roman titles do not.  
4. On a **new** sealed naturalistic set, human Success@5 = **23/40 (57.5%)**. Urdu-script needs are usually met; Roman and mixed needs often are not.  
5. Allowed query-side Roman expansions (Phase 11) did not improve the 68/78 known-item score; M0 stays official.  
6. H001–H040 Success@5 = 25/40 is a **historical diagnostic**, not official unseen performance.

That is a complete, honest contribution: **routing + Method D works for Urdu script and for Method-D-like Roman titles; it does not yet solve naturalistic Roman Urdu IR.**

---

## 7. Thesis-ready results table

| Dataset | Query type | n | Evaluation method | Metric | Result | Interpretation |
| --- | --- | ---: | --- | --- | --- | --- |
| Phase 2 dev + internal_val (`QTRN_*`) | Title-derived known-item (`title_short` / `title_roman` / related) | 78 | Exact `source_doc_id` in Top-5 | ExactSource Hit@5 | **68/78 = 87.18%** | Development/validation known-item result. **Not** unseen. **Not** human relevance. |
| Same pool, Urdu-only BM25 (no Roman path) | Same | 78 | ExactSource Hit@5 | ExactSource Hit@5 | 0.5897 | Shows why a Roman path was needed on this pool. |
| Same pool, Roman subset, Method A | `title_roman` | 23 | ExactSource Hit@5 | ExactSource Hit@5 | 0/23 | Script mismatch without Method D. |
| Same pool, Roman subset, Method D | `title_roman` | 23 | ExactSource Hit@5 | ExactSource Hit@5 | 22/23 | Method D works when queries match its romanization. |
| Phase 11 M0–M4 | Same n=78 known-item | 78 | ExactSource Hit@5 | ExactSource Hit@5 | 68/78 for all | Query-side expansions did not beat M0. Official system remains M0. |
| Phase 9 H001–H040 | Routing-trap strings | 40 | ExactSource Hit@5 | — | **Undefined** | No `source_doc_id`. Not a Hit@5 of 0%. |
| Phase 10C H001–H040 | Same traps | 40 | Human A/B in Top-5 | Success@5 | 25/40 = 62.5% | **Diagnostic only.** Queries and labels are contaminated. **Not** official unseen. |
| Phase 12 K001–K040 | New title-like known-item | 40 | Exact `source_doc_id` in Top-5 | ExactSource Hit@5 | **27/40 = 67.5%** | Independent known-item test of frozen M0. |
| Phase 12 K, URDU | Title-like | 28 | ExactSource Hit@5 | ExactSource Hit@5 | 26/28 | Urdu known-item remains strong. |
| Phase 12 K, ROMAN | Ordinary Roman titles | 12 | ExactSource Hit@5 | ExactSource Hit@5 | 1/12 | Ordinary Roman known-item is weak. |
| Phase 12 U001–U040 | New naturalistic; no gold id | 40 | Human A/B in Top-5 | Success@5 | **23/40 = 57.5%** | Official unseen **usefulness** result. **Not** ExactSource. |
| Phase 12 U | Same | 40 | Count of A / 5, mean | Conservative P@5 | 0.2050 | Few fully answering documents per query. |
| Phase 12 U | Same | 40 | Graded A=3,B=2,C=1,D=E=0 | nDCG@5 | 0.6460 | Inflated by topical C; not a usefulness headline. |
| Phase 12 U | Same | 40 | First A or B | MRR | 0.4542 | Rank of first useful hit, if any. |
| Phase 12 U, URDU | Naturalistic | 18 | Success@5 | Success@5 | 17/18 = 94.44% | Urdu-script user needs usually met. |
| Phase 12 U, ROMAN | Naturalistic chat Roman | 18 | Success@5 | Success@5 | 6/18 = 33.33% | Main usefulness gap. |
| Phase 12 U, MIXED | Both scripts | 4 | Success@5 | Success@5 | 0/4 | Small n; all failed. Do not over-generalize, do not hide. |

Do not add a row that averages 87.18%, 67.5%, and 57.5%.

---

## 8. Thesis-ready discussion: the gap 87.18% → 67.5% → 57.5%

The three headline percentages look like a collapse of one system. They are **three different measurements**.

**Development 87.18%.** The n=78 set is title-derived known-item search, including Roman queries built as `title_roman`. Method D was **selected** on that Roman construction (Phase 5: DEV Hit@5 then nDCG@5). High Hit@5 is expected when the query is a shortened headline and, for Roman, when the spelling family matches the index. This number answers: *Can M0 recover a known news article from a title-like query on the freeze set?* Yes, often.

**New known-item 67.5%.** K is the same **task** (exact source in Top-5) on a **new sample**, with Roman queries written as ordinary Roman Urdu rather than `title_roman`. Urdu K stays high (26/28). Roman K does not (1/12). The 19.7 point drop from 87.18% to 67.50% is therefore largely a **Roman query-form shift** plus ordinary sampling variation on \(n=40\), not evidence that Urdu BM25 “broke.” 67.5% is the honest **unseen known-item** figure for this sealed K set.

**Naturalistic 57.5%.** U is a **different task**. There is no single gold article. Factoid, explanatory, and named-entity needs, short underspecified strings, and chat Roman are harder than “find this headline.” Success@5 only requires one A or B. Even so, Roman U is 6/18 and MIXED is 0/4. P@5 = 0.205 shows that Top-5 is rarely packed with fully answering documents. This number answers: *If a user types a natural need, how often is something useful in the first five hits?* About 58% overall; about 94% when they type Urdu script.

**Reading the staircase without spinning it.** From development titles, to new titles, to natural questions, **difficulty and mismatch increase**, especially on Roman. That is a standard IR pattern (known-item vs ad hoc). It is **not** a reason to discard 57.5%, and **not** a reason to keep quoting 87.18% as the user-facing score.

**What remains strong.** Frozen M0 is a credible **Urdu-script news BM25** system with a working script router. Method D is a credible fix for **pipeline-romanized titles**. The thesis contribution is this measured architecture and these **separated** evaluations—not a single high percentage.

---

## 9. Limitations

**Sample size.** K and U have \(n=40\). A binomial 95% interval around 23/40 is wide (roughly the mid-40s to low-70s for Success@5). Point estimates must be reported with n. Do not claim a precise “58% in the wild.”

**Official labels are A1.** U official labels are Annotator 1 (first author; also wrote the U queries). An independent second annotation (A2) was later run on the same 200 judgments as a reliability check (five-way κ = 0.5490). A2 does not replace 23/40 and does not remove dual-role bias. Conservative A vs B (prefer B) reduces over-claiming full answers; it does not remove subjectivity.

**Known-item vs naturalistic.** ExactSource and Success@5 are not interchangeable. The thesis must keep two evaluation chapters or two clearly separated tables.

**Roman Urdu.** Ordinary Roman spelling is open-ended. A 198-key dictionary plus character romanization of **documents** does not cover chat Roman **queries**. Phase 11 showed that small query expansion did not move n=78 Hit@5. The limitation is the Roman path, not the Urdu index.

**Distribution shift.** Development Roman ≠ K Roman ≠ U Roman. Development titles ≠ natural factoids. Temporal queries were judged as archive type-of-fact, not live “today.” MIXED \(n=4\) is too small for a rate claim beyond “these four failed.”

**nDCG@5 with C=1.** Topical neighbours inflate nDCG. Report Success@5 and MRR as usefulness; treat 0.646 nDCG as secondary and qualified.

**H001–H040.** No gold id (Phase 9). Human labels exist (Phase 10C) but the set is **open**. Do not tune on it. Do not call 62.5% the official unseen human score.

**K and U are different tasks.** Do not rank “67.5% vs 57.5%” as the same system getting worse at the same job.

**Older paper drafts.** Clause-1 PLOS text and related figures (e.g. 100% routing accuracy, P@15 near 90%) are **not** the frozen M0 retrieval results in this document. The thesis must follow Phases 8–12, not those drafts, unless a separate study is re-run and sealed.

**No fusion/reranker.** Phase 6–7 evidence did not justify adding a model. That is a scope limit, not a hidden extra score.

---

## 10. Future work

Do **not** tune BM25, the dictionary, routing, or Method D on U001–U040, K001–K040, or H001–H040.

If the system changes later:

1. Freeze the new system **before** writing queries.  
2. Seal a **new** query file (new ID namespace).  
3. Retrieve once.  
4. Label (if naturalistic) only after the dump exists.  
5. Report new numbers **alongside** the frozen M0 table; do not overwrite 68/78, 27/40, or 23/40.

Useful directions (each needs that new test):

- Roman Urdu: better query–document matching than Method D + 198 keys, without fitting the burned U/K strings.  
- Mixed-script queries (current \(n=4\) is only a warning).  
- Second annotator / IAA on a **new** naturalistic set.  
- Larger sealed U (\(n \ge 80\)) if annotation budget allows.  
- Error taxonomy on a **held-out** Roman sample designed **without** looking at U failures.

---

## 11. Invalid claims (do not put in the thesis)

- “87.18% accuracy on unseen queries.”  
- “87% human relevance.”  
- “The system achieved ~80%.”  
- “U Success@5 is ExactSource Hit@5.”  
- Any average of 87.18%, 67.5%, and 57.5%.  
- “H001–H040 prove unseen official performance.”  
- “M1 is the official system.”  
- Hiding 57.5% or the Roman 6/18 split.

---

## 12. Sources (frozen reports)

- `experiments/phase8_final_freeze/DEVELOPMENT_RESULTS.md`  
- `experiments/phase5_roman_urdu/PHASE5_RESULTS.md`  
- `experiments/phase9_heldout_evaluation/PHASE9_RESULTS.md`  
- `experiments/phase10c_human_relevance/PHASE10C_RESULTS.md`  
- `experiments/phase11_improvement/PHASE11_ABLATION_RESULTS.md`  
- `experiments/phase12_new_unseen_evaluation/K_RESULTS.md`  
- `experiments/phase12_human_relevance/PHASE12_HUMAN_RESULTS.md`  

M0, queries, and labels were not modified for this write-up.
