# ULTRA v2 annotation guidelines

**Status:** protocol. No documents to judge yet.  
**Starting point:** PLOS Phase 7 / Phase 12 A–E labels. Not blindly replaced by a 0–3 scale.

These rules apply to **NL** pooled candidates (and to optional graded labels on non-source KN hits). Track KN **primary** scoring remains ExactSource identity (`source_doc_id`), not A–E.

---

## 1. Labels

Exactly one label per (query, document, annotator, interpretation).

| Code | Name | Meaning |
| --- | --- | --- |
| **A** | RELEVANT | Directly satisfies the information need. A reader could stop here. |
| **B** | PARTIALLY_RELEVANT | Useful answer to the asked need, with a minor limitation (incomplete slot, same occasion but missing a detail). |
| **C** | TOPICALLY_RELATED | Same topic, entity, or genre, but **not** the asked slot or need. |
| **D** | NOT_RELEVANT | Does not meaningfully address the query. Weak or coincidental word overlap is D, not C. |
| **E** | AMBIGUOUS | A–D cannot be decided from the allowed evidence (headline+snippet, or full text if a pre-registered second pass). |

**Useful (Success@5 / NL Recall@50):** A or B.  
**Not useful:** C, D, E.

### Why this is not “E = irrelevant”

A draft wording that set E = irrelevant would **duplicate D** and delete the ambiguity channel. Irrelevance is D. E is reserved for undecidable cases and for documenting genuine need ambiguity when the document cannot be mapped to a single interpretation without more process (see §4). This is a PLOS-compatible protocol choice.

---

## 2. Evidence and process

1. Judge **raw** `query_text`.
2. Default evidence: **headline + snippet** only (same as Phase 12).
3. Full article text only if a later protocol amendment pre-registers a second pass.
4. Do **not** search the corpus for a better document. Do not invent hits. Do not pad missing ranks.
5. Do not look at other annotators’ labels before independent judging is complete.

### Conservatism (PLOS-compatible)

- **A vs B:** prefer **B** unless the need is clearly satisfied.
- **B vs C:** **B** only if the article helps answer the **asked** need, not merely the topic.

### Temporal needs

If the query uses `آج` / `aaj` / `موجودہ` / `mojooda` (or equivalent “current/today”):

- Set `query_asks_today=1` on the query record when collected.
- **A** means the article states the requested **type of fact** for a **dated occasion in the article**, not the annotator’s calendar day.

Recurring wires with **no** date in the query (gold price, budget date, eclipse, stock close): same wire type can be **A** even if dates differ (Phase 7 rule). Do not overfit a new temporal policy on TEST.

### Named entities

If the need is a person/team lookup: an article whose **main subject** is that entity can be **A**. Same-person news that misses a specified slot (e.g. PSL vs Tests) is **C**.

---

## 3. Independence, disagreement, adjudication

| Role | Rule |
| --- | --- |
| Judges | ≥2 independent judges for official NL where feasible |
| Query author | Must **not** be the sole official judge |
| Independence | Second judge does not see author or first-judge labels until adjudication |

**Critical boundary:** `{A,B}` vs `{C,D,E}` (useful vs not). Adjudicate every disagreement on that boundary.

**A vs B** (both useful): may remain unresolved for Success@5 (both count as success). Record both labels for nDCG_useful / P@5; official graded metrics use the **adjudicated** label when one is produced, otherwise a pre-registered rule: **conservative = worse grade** (B over A) for official secondary metrics.

**C vs D vs E:** adjudicate if they affect topical nDCG or if one judge said C and one said D (C is topical; D is not). E vs anything: discuss; if still undecidable, official = E.

Adjudication is a third pass by a designated adjudicator (can be one of the judges **after** independent labels are frozen, or a third person). Official rows have `official=1` and `adjudicated=1`.

Author-only labels, if collected, have `official=0`.

---

## 4. Ambiguous queries

If `ambiguous=1`:

1. Use writer `interpretation_notes` as the list of valid readings (`I1`, `I2`, …).
2. Label each document **per interpretation** (`interpretation_id`).
3. A document may be A for `I1` and D for `I2`.
4. Query-level Success@5 uses **any** valid interpretation unless a pre-TEST amendment requires a primary reading.
5. Do not treat genuine ambiguity as a system failure (`QAMB`).

If the query was not marked ambiguous but judges disagree because the need is unclear: they may assign E and flag `QAMB` for TRAIN taxonomy work. Do not silently add TEST queries to “fix” ambiguity after scores exist.

---

## 5. Pooling

Judge the **pooled** candidate set defined in `PROTOCOL.md` §11, not only one system’s Top-5, when NL Recall@50 is required.

Unjudged documents are unknown, not D.

---

## 6. KN

Primary: `source_doc_id` in the ranked list. Do not relabel the source as C because a judge prefers another article.

Optional A–E on other KN hits is diagnostic only.

---

## 7. Forbidden

- Using H/K/U qrels as examples **during** official v2 judging of the new set (training annotators on the **guidelines** is allowed; copying old labels onto new docs is not)
- Tuning systems from labels before TRAIN/DEV splits are respected
- Changing label definitions after TEST scoring
