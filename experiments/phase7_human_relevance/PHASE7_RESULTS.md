# PHASE 7 FINAL REPORT

Secondary human-relevance analysis of the **10 exact-source misses** under the frozen Phase 5/6 system.  
**H001–H040 unused.** Retrieval configuration was not modified.

---

## 1. Purpose

Phase 5/6 script-aware retrieval scores **0.8718** exact-source Hit@5 (68/78). The remaining 10 misses look, from Phase 6, like topical neighbours and truncated mixed titles rather than off-topic retrieval.

This phase asks whether those official zeros are **retrieval failures** or **known-item / query-construction failures**, using a DEV-first frozen rubric. Human labels do **not** replace Hit@5.

---

## 2. Frozen system

- URDU / MIXED → Urdu BM25 (`k1=1.5`, `b=0.75`, `combined_text`)
- ROMAN → Phase 5 Method D (romanized-document BM25)

---

## 3. Official metric

Exact-source Hit@5 on n=78 remains **0.8718**.  
On these 10 residuals, official ExactSourceHit@5 = **0 / 10** by construction.

---

## 4. DEV annotation

Residual misses: **4** (QTRN_168, 170, 189, 225). Rubric designed and frozen here (`ANNOTATION_RUBRIC.md`).

| Query | Relevant in Top-5 | Partial in Top-5 | Topical in Top-5 | Not relevant | Query ambiguous |
| --- | --- | --- | --- | --- | --- |
| QTRN_168 | yes (5/5) | no | no | no | yes |
| QTRN_170 | no | yes (3/5) | yes (2/5) | no | no |
| QTRN_189 | no | no | yes (5/5) | no | yes |
| QTRN_225 | no | yes (5/5) | no | no | yes |

DEV totals (queries):

- Relevant result in Top-5: **1 / 4**
- Partially relevant in Top-5: **2 / 4**
- Relevant **or** partial: **3 / 4**
- Only topical neighbours (no A/B): **1 / 4** (QTRN_189)
- No relevant/topical document (all D): **0 / 4**
- Ambiguous queries: **3 / 4**

---

## 5. INTERNAL_VAL annotation

Same frozen rubric. Residual misses: **6**.

| Query | Relevant in Top-5 | Partial in Top-5 | Topical in Top-5 | Not relevant | Query ambiguous |
| --- | --- | --- | --- | --- | --- |
| QTRN_010 | yes (1/5) | yes | yes | yes (1/5) | yes |
| QTRN_031 | no | yes (4/5) | yes (1/5) | no | no |
| QTRN_099 | no | yes (2/5) | yes (3/5) | no | yes |
| QTRN_108 | no | yes (5/5) | no | no | yes |
| QTRN_216 | no | no | yes (5/5) | no | yes |
| QTRN_258 | yes (5/5) | no | no | no | yes |

INTERNAL_VAL totals (queries):

- Relevant result in Top-5: **2 / 6**
- Partially relevant in Top-5: **4 / 6**
- Relevant **or** partial: **5 / 6**
- Only topical neighbours: **1 / 6** (QTRN_216)
- All-not-relevant Top-5: **0 / 6**
- Ambiguous queries: **5 / 6**

The rubric was **not** changed after these labels.

---

## 6. Evaluation gap

Secondary metrics **on the 10 residuals only** (not on n=78):

| Secondary (query-level) | DEV (n=4) | INTERNAL_VAL (n=6) | Combined (n=10) |
| --- | ---: | ---: | ---: |
| ExactSourceHit@5 | 0 | 0 | **0** |
| Relevant@5 | 1 | 2 | **3** |
| PartiallyRelevant@5 | 2 | 4 | **6** |
| RelevantOrPartiallyRelevant@5 | 3 | 5 | **8** |
| TopicRelated@5 (any C) | 2 | 4 | **6** |
| Query ambiguous | 3 | 5 | **8** |
| Evaluation mismatch (official miss but A or B in Top-5) | 3 | 5 | **8** |

**8 / 10** exact-source misses still contain a RELEVANT or PARTIALLY_RELEVANT article in Top-5.

The 2 that do not (QTRN_189, QTRN_216) are **entity-only mixed fragments** (`ئی سی سی کا`, `ایس ای سی پی` + template). Their Top-5 lists are still ICC/SECP topical, not off-domain.

This is **not** an official system win. It is evidence that exact-source Hit@5 is **harsh** on underspecified QTRN strings and recurring wires.

---

## 7. Main failure

Primary residual problem: **KNOWN-ITEM EVALUATION** mixed with **QUERY AMBIGUITY**.

- Recurring wires without a date (QTRN_168, QTRN_258): retrieval returns the right *class* of article; `source_doc_id` is under-determined.
- Truncated mixed titles (QTRN_189, 225, 099, 108, 216): the query never contained the distinctive gold span.
- Ranking / near-miss (QTRN_031, QTRN_170, QTRN_010 gold at 9 / 37 / 9): Top-5 is the same event family, not a random ranking failure.

It is **not** primarily a lexical or semantic retrieval collapse: BM25 Top-5 is in-domain for all 10.

---

## 8. Architecture decision

**Does the evidence justify another retrieval architecture experiment? NO.**

Decision table:

- **Case A** (most misses have nothing relevant in Top-5): **false** (0/10 all-D; 8/10 have A or B).
- **Case B** (most have RELEVANT or PARTIALLY_RELEVANT in Top-5): **true (8/10)**. Main issue is known-item construction, not missing capability. Do not add a model.
- **Case C** (only 1–2 Headline-complementary leftovers): Phase 6 already showed **3** Headline-only recoveries. Do **not** build fusion for those.
- **Case D** (consistent rerank signal): QTRN_031 has gold at rank 9 among snooker neighbours. That is one ranking-shaped residual, not a dominating class.

Building RRF, a reranker, or a new dense index would chase `source_doc_id` on queries that several on-topic articles already satisfy.

---

## 9. Phase 8 recommendation

**Exactly one next action: Finalize the evaluation protocol.**

Spell out, in writing, that:

1. Official development score stays **exact-source Hit@5 = 0.8718** on n=78.
2. Residual zeros are mostly known-item / query-ambiguity, documented here.
3. No architecture change is justified before a protocol freeze.
4. **H001–H040 remain sealed** until that protocol is frozen and the system is frozen.

Do **not** start held-out evaluation in the same step as protocol writing if the protocol is not yet signed off. Do not start reranking, fusion, or semantic indexing.

STOP.
