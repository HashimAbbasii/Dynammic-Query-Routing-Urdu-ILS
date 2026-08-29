# PHASE 6 FINAL REPORT

Eval = Phase 2 **dev + internal_val**, **n=78**, known-item `source_doc_id`.  
Frozen Phase 5 policy: URDU/MIXED → Urdu BM25; ROMAN → Method D.  
**H001–H040 unused.** No SVM, RRF, fusion, reranker, BM25 retune, or Method D change.  
Official metric is unchanged: exact-source Hit@5.

---

## 1. Reproduction

Phase 5 reproduced? **Yes.**

| | Expected | Observed |
| --- | ---: | ---: |
| Script-aware Hit@5 | 0.8718 | **0.8718** |
| nDCG@5 | 0.8107 | 0.8107 |
| MRR | 0.797 | 0.797 |
| Residual misses | 10 | **10** |
| Headline Hit@5 | 0.4487 | **0.4487** |

68 / 78 Hit@5. Indexes rebuilt from the frozen tokenizer and romanizer; not copied from Phase 5 rank files.

---

## 2. Residual inventory

| Split | n | Ids |
| --- | ---: | --- |
| DEV | 4 | QTRN_168, QTRN_170, QTRN_189, QTRN_225 |
| INTERNAL_VAL | 6 | QTRN_010, QTRN_031, QTRN_099, QTRN_108, QTRN_216, QTRN_258 |

| Script | n | Ids |
| --- | ---: | --- |
| URDU | 4 | QTRN_010, QTRN_168, QTRN_170, QTRN_258 |
| ROMAN | 1 | QTRN_031 |
| MIXED | 5 | QTRN_099, QTRN_108, QTRN_189, QTRN_216, QTRN_225 |

INTERNAL_VAL misses were **not** used to propose a method. They are reported for diagnosis only.

---

## 3. Rank-depth analysis

Script-aware ranks of the 10 misses:

| Bucket | Count | Ids |
| --- | ---: | --- |
| Top-5 | 0 | (by definition) |
| Rank 6–10 | **4** | QTRN_010 (9), QTRN_031 (9), QTRN_099 (9), QTRN_168 (7) |
| Rank 11–20 | **0** | |
| Rank 21–50 | **2** | QTRN_170 (37), QTRN_258 (23) |
| Miss Top-50 | **4** | QTRN_108, QTRN_189, QTRN_216, QTRN_225 |

6 / 10 sources are already in the Top-50 candidate list. 4 / 10 are complete Top-50 misses — all four are **mixed** queries.

Headline depth on the same 10: Top-5 = 3, rank 6–10 = 1 (QTRN_258 at 7), miss-50 = 6.

---

## 4. Retrieval room complementarity

This is an **oracle**, not a deployed result. No RRF.

| | n | Hit@5 |
| --- | ---: | ---: |
| Script-aware | 68 / 78 | 0.8718 |
| Headline | 35 / 78 | 0.4487 |
| Both Hit@5 | 32 | |
| Headline-only recoveries (wrong-room) | **3** | QTRN_010, QTRN_168, QTRN_170 |
| Script-aware-only recoveries | 36 | |
| Both miss Top-5 | **7** | |
| Union oracle | **71 / 78** | **0.9103** |

Headline uniquely recovers **3 / 10** residual misses (all Urdu). It does not recover any mixed miss (the `Pakistan news update` suffix dominates MiniLM). It does not recover QTRN_031.

---

## 5. Failure taxonomy

One primary label per miss (see `FAILURE_TAXONOMY.csv`).

| Category | Count | Percentage | DEV | INTERNAL_VAL |
| --- | ---: | ---: | ---: | ---: |
| QUERY_AMBIGUITY | 4 | 40% | 2 | 2 |
| WRONG_ROOM | 3 | 30% | 2 | 1 |
| ENTITY_COLLISION | 1 | 10% | 0 | 1 |
| TOPICAL_NEIGHBOUR | 1 | 10% | 0 | 1 |
| KNOWN_ITEM_AMBIGUITY | 1 | 10% | 0 | 1 |

Largest **primary** category: **QUERY_AMBIGUITY** (4/10), all `mixed_short` titles plus the Latin template suffix.

If QUERY_AMBIGUITY, ENTITY_COLLISION, TOPICAL_NEIGHBOUR, and KNOWN_ITEM_AMBIGUITY are grouped as “not a missing-room problem”: **7 / 10**.

Answers:

1. Recoverable by Headline (oracle): **3 / 10**
2. Ranking failures (source in ranks 6–20): **4 / 10** (all 6–10; none 11–20)
3. Top-50 complete misses: **4 / 10**
4. Weak lexical overlap vs hits: **NO** (see §6)
5. Topical-neighbour / known-item issues in Top-5: **10 / 10** (qualitative); primary label in that family: **7 / 10**
6. Single largest remaining failure category: **QUERY_AMBIGUITY** from mixed truncated titles

---

## 6. Lexical analysis

Do failed queries have lower lexical overlap? **NO.**

Mean token coverage of the **source** (query tokens found in source headline / body):

| | 10 misses | 68 hits |
| --- | ---: | ---: |
| Headline coverage | **0.619** | 0.465 |
| Body coverage | **0.644** | 0.592 |
| Content-headline coverage | **0.760** | 0.521 |
| Query length (tokens) | 8.9 | 10.8 |

Misses overlap the labelled source **at least as much** as hits. They also overlap **many other articles** (repeated wires, entity names, genre phrases). The failure mode is **non-unique overlap**, not missing overlap.

Caveat: QTRN_031 shows 0 Urdu-script Jaccard because the query is Latin; Method D still places the source at rank 9. That row is a measurement artifact, not a Method D script miss.

---

## 7. Top-result analysis

Every script-aware Top-5 for these 10 is in-domain:

- **Topical neighbours (7):** other SA–NZ cricket; other snooker championship reports; other women’s cricket; other “number one team” rankings; other PSX third-day wires; other PAK–WI T20s; other SECP stories.
- **Entity collision:** `ایس ای سی پی`, `ئی سی سی`, Pakistan, South Africa / New Zealand — names that flood the corpus.
- **Temporal confusion:** QTRN_168 (same stock template, different dates); QTRN_258 (recurring CNG opening wires).
- **Lexical mismatch:** QTRN_189 and QTRN_225 dropped the distinctive title span (`انٹرپول` / `انٹ مین`) during `mixed_short` construction.
- **Ambiguity:** QTRN_258 is a near-duplicate cluster; several Top-5 headlines are as aligned as the labelled source.

Headline Top-5 on mixed queries is **not** a topical neighbour of the Urdu fragment; it is hijacked by `Pakistan news update`.

---

## 8. Known-item evaluation limitation

Of the 10 residual misses:

- **7** retrieve topically relevant non-source articles (TOPICALLY_RELEVANT_NEIGHBOUR)
- **2** retrieve same-domain but different-event articles (PARTIALLY_RELATED)
- **1** is AMBIGUOUS among near-duplicate wires
- **0** are CLEARLY_IRRELEVANT in the BM25 room

Official Hit@5 on these 10 remains 0. Do not rewrite Phase 5 as “topical P@5”.

---

## 9. Main bottleneck

The remaining 12.8% is not a missing encoder: it is **known-item identity among topical neighbours**, driven by **truncated mixed queries** (5/10) and **repeated Urdu news wires** (stock / cricket / CNG), with only **3/10** showing a complementary Headline room.

---

## 10. Phase 7 recommendation

Recommend **exactly one** experiment:

**Human graded-relevance evaluation of residual misses (DEV-first annotation protocol), before any new retrieval architecture.**

Why this gate, not the others:

- Wrong-room / Headline-recovers is only **3/10**, so a candidate-union or RRF experiment is **not** the majority leftover (oracle ceiling +3 → 0.9103, and mixed union is already known to add 0).
- Rank 6–10 is **4/10**, but those four are neighbours of the source, not random ranking noise. A reranker would be asked to pick `source_doc_id` among equally on-topic wires.
- Deep miss / semantic mismatch does **not** dominate: overlap is high; BM25 Top-5 is on-topic; MiniLM Headline does not rescue mixed queries.
- Query-ambiguity + topical-neighbour + known-item ambiguity **do** dominate (7/10 primary; 10/10 Top-5 neighbours). The decision table says: human relevance **before** claiming more architecture.

Protocol constraint if Phase 7 is run: draft the rubric on **DEV** misses only (QTRN_168, 170, 189, 225), freeze it, then apply once to INTERNAL_VAL. Do not use H001–H040. Do not implement RRF, a reranker, or a new dense index in that phase.

STOP.
