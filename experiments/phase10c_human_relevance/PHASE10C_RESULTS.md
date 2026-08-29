# PHASE 10C RESULTS — human relevance of the frozen Top-5

Baseline human-relevance evaluation only. **Not** ExactSource Hit@5. **Not** a Phase 9 rewrite. **Not** a system improvement.

Phase 9 development known-item score remains **68/78 = 0.8718** on `QTRN_*`. That number is **not** the H001–H040 result and is **not** mixed with the figures below.

---

## A. Experiment identity

| | |
| --- | --- |
| Evaluation | Phase 10C human relevance |
| Retrieval artifact judged | `phase10b_frozen_dump` |
| Replaces Phase 9 | no |
| Retrieval rerun in 10C | **no** |
| Architecture changed | **no** |
| Labels from MiniLM / `heldout_retrieval_template.csv` | **not used** |

---

## B. Dataset and corpus

| | |
| --- | --- |
| Queries | H001–H040 |
| Query source | `heldout_traps.py` `query` field (raw text) |
| Corpus | `data/clean_articles.csv` |
| Corpus SHA-256 | `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231` |
| n_docs | 111,860 |
| Dictionary | 198 keys (frozen; unused for labeling) |
| BM25 | k1=1.5, b=0.75 (frozen) |
| Lists judged | `experiments/phase10b_frozen_dump/TOP5_FOR_ANNOTATION.csv` |
| Rank-1 vs Phase 9 (from 10B) | 40/40 match |

H001–H040 have **no** `source_doc_id`. Official ExactSource Hit@5 on this set remains **undefined**.

---

## C. Number of queries

**40** (H001–H040).

---

## D. Number of annotation rows

**196** (38 queries × 5 + H027 × 5 + H036 × 1). No padded documents.

---

## E. Label distribution (196 documents)

| Label | Meaning | Count |
| --- | --- | ---: |
| A | RELEVANT | 25 |
| B | PARTIALLY_RELEVANT | 42 |
| C | TOPICALLY_RELATED | 45 |
| D | NOT_RELEVANT | 84 |
| E | AMBIGUOUS (Phase 7: A–D undecidable) | 0 |

A+B+C+D+E = 196.

---

## F. Success@5

A query succeeds if **at least one** retrieved document in its available Top-5 is **A or B**.

**Success@5 = 25 / 40 = 0.6250**

This is **not** ExactSource Hit@5.

---

## G. Conservative P@5

Per query: (number of **A** labels) / **5**, including H036 (0/5). Then mean over 40 queries.

**Conservative P@5 = 0.1250**

(25 A-labels / 200 = 0.1250)

---

## H. Variable-denominator P@5

Per query: (number of **A** labels) / min(5, `n_hits_returned`). Then mean over 40.

**Variable-denominator P@5 = 0.1250**

H036 is the only query with `n_hits_returned < 5` (1 hit, 0 A). The two P@5 definitions therefore coincide on this run.

---

## I. All-D queries

Every retrieved document for the query is **D** (no padding).

**10 / 40 = 0.2500**

IDs: H007, H010, H015, H016, H020, H025, H027, H028, H029, H036.

---

## J. Temporal queries

`query_asks_today = 1` if the query contains `آج`, `aaj`, `موجودہ`, or `mojooda`.

**10 queries:** H017, H018, H021, H023, H024, H025, H026, H029, H031, H032.

These were **not** failed solely for not matching the annotator’s calendar day. **A** required the requested **type of fact** for a dated occasion **in the article**.

---

## K. Notable annotation patterns

1. **Success@5 is higher than conservative P@5** because many useful hits are **B**, not **A**. Short “why / how / effects” traps often retrieve same-topic news that does not fully answer the causal question (e.g. H001 petrol-price notifications vs “why expensive”).
2. **Urdu lists are stronger than Roman lists** on this sample: Success@5 **14/20** Urdu vs **11/20** Roman. Eight of ten all-D queries are Roman (H010, H015, H016, H025, H027, H028, H029, H036).
3. **English or weakly romanized tokens** on Method D frequently produce off-topic lists (Kaaba for `kab`, boxing for `aaj`, *Dhoom* for `diesel rate`, iPhone query with no iPhone launch article). This is a frozen-system observation, **not** a license to edit the dictionary on H001–H040.
4. **Homograph / title-token collisions** appear on Urdu traps (`ڈوبی` as a film title, `فیل` as turkey / “fail”, `ہار` as necklace vs loss).
5. **Factoid Urdu prices** (H018 gold tola; H023 petrol `موجودہ` price; H033–H034 diesel/gold `ریٹ`) more often contain **A** than open-ended “why” traps.
6. **H036** has a single **D** document; Success@5 and P@5 both treat it as a miss. No extra documents were invented.

---

## L. Limitations

- One annotator; labels are from headline + 500-character snippet, not the full article body.
- Phase 7 QTRN suffix-stripping was **not** applied (H queries are not QTRN templates).
- 10B Top-5 is a **frozen replay**. Rank-1 matched Phase 9 40/40; ranks 2–5 were not recoverable from the original Phase 9 files.
- H001–H040 query text and rank-1 were already open before 10C. This set is a **diagnostic held-out** pool, not a clean future test for an improved system.
- Conservative P@5 uses denominator 5 even for H036, which understates precision if interpreted as “among returned hits.”
- These metrics **must not** be reported as 87.18%, as “~80% unseen,” or as ExactSource Hit@5.

---

## Stop

No retrieval was run. No BM25 / dictionary / Method D / routing change. Phase 9 files were not written. Phase 10B files were not overwritten.

Do **not** select improvements using H001–H040. Development remains `QTRN_*` n=78. A later improved system needs a **new** unseen sample (e.g. H041+).
