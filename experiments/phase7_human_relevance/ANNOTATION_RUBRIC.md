# Phase 7 annotation rubric

Frozen on **DEV residual misses only**: QTRN_168, QTRN_170, QTRN_189, QTRN_225.

Do **not** edit this file after INTERNAL_VAL annotation.  
Official metric remains exact `source_doc_id` Hit@5. These labels are secondary.

Annotate the **frozen script-aware Top-5** (URDU/MIXED → Urdu BM25; ROMAN → Method D).

---

## 0. What is being judged

Judge the retrieved **article** against the **information need expressed by the query text**.

Do **not** award RELEVANT because:

- the article mentions the same entity as the gold source, or
- the article would be the right known-item if you already know `source_doc_id`.

The hidden gold id is recorded for analysis. It is not a relevance signal.

---

## 1. Primary labels (exactly one per retrieved article)

### A. RELEVANT

The article **directly satisfies** the information need in the query.

The reader who issued this query would be justified in stopping here.

### B. PARTIALLY_RELEVANT

The article discusses **substantially the same event or occasion** as the query asks about, but **does not fully answer** it (e.g. toss instead of result; preview instead of outcome; one stage of a tournament when the query asks for another).

### C. TOPICALLY_RELATED

Same broad topic, entity, sport, organisation, or genre, but **not** the information need (different event, different team/gender/format, personnel news instead of the asked fact, schedule instead of a match).

### D. NOT_RELEVANT

Does not meaningfully address the query.

### E. AMBIGUOUS

Use **only for an article** when A–D cannot be decided even after reading headline + snippet.  
Do not use E as a dump category for “several articles look similar.” That situation is recorded as **query-level ambiguity** (below), while each article still gets A–D.

---

## 2. Query preprocessing (DEV-derived)

Strip known QTRN **generation suffixes** before interpreting the need. They are not user intent:

- `Pakistan news update`
- `کیسے ہوا` / `کیوں ہوا`
- `کے اثرات کیا ہیں`

Judge the remaining content.

Do **not** treat `Pakistan` from the mixed-query template as a required entity constraint (it is glued onto every mixed residual).

---

## 3. Rules

### Entity overlap

Same person, team, country, or organisation is **not** enough for RELEVANT.

DEV negative (QTRN_189): query is only `ئی سی سی کا`. An ICC chairman sacking / committee story is **TOPICALLY_RELATED**, not RELEVANT.

### Incomplete / entity-only / genre-only queries

If after stripping suffixes the query is only an organisation, a genre, or a genitive fragment (`X کا`):

- Do **not** label instance articles RELEVANT.
- Organisation/entity-only → ICC/SECP-style stories: **TOPICALLY_RELATED**.
- Genre/category-only (e.g. `سائنس فکشن ایکشن فلم`) → a specific film’s teaser is **PARTIALLY_RELEVANT** (an instance of the category, not a complete unique answer).
- Mark the **query** as ambiguous in the query-level field.

### Recurring news wires and temporal differences

If the query names a **repeated wire type** (same headline template) but **no date, score, or other distinguishing slot**:

- Articles that are the **same wire type** (same event class, complete answer for their own date) are **RELEVANT**.
- Different dates do **not** downgrade them to TOPICALLY_RELATED when the query itself has no date.
- Mark the **query** as ambiguous.

DEV positive (QTRN_168): `کاروباری ہفتے کا تیسرا روز پاکستان اسٹاک مارکیٹ پوائنٹس` with no date. A 260-point decline on 8 Apr 2020 and a 102-point rise on 9 Dec 2020 are both RELEVANT third-day PSX close reports.

### Exact event vs same topic

DEV negative (QTRN_170): query is Pakistan vs West Indies in the **second T20** (result/effects).

- Toss of a PAK vs WI second T20 → **PARTIALLY_RELEVANT** (same occasion, not the result).
- Women’s second T20, or adding T20s to a tour → **TOPICALLY_RELATED**.
- A different series’ toss is still PARTIALLY_RELEVANT only if it is still PAK vs WI **second T20 toss**; otherwise TOPICALLY_RELATED. (DEV ranks 1, 2, 5 are men’s second-T20 toss reports → PARTIALLY_RELEVANT.)

### Borderline: fixture / preview / in-play score

If the query asks for a series/match **outcome** (or is a truncated outcome title) and the article is a fixture, “tomorrow,” or an in-play scorecard → **TOPICALLY_RELATED** or **PARTIALLY_RELEVANT** (in-play of that series → PARTIALLY_RELEVANT; unrelated ranking sidebar → NOT_RELEVANT).

---

## 4. DEV worked examples (rubric freeze set)

### QTRN_168 — recurring wire, no date

Query: third business day, Pakistan stock market, points.  
Gold (not used for labelling): 3 Jun 2020, −6 points.

| Rank | Article (short) | Label |
| --- | --- | --- |
| 1–5 | Other third-day PSX closes, different dates/magnitudes | **RELEVANT** |

Query-level ambiguous: **yes**.

### QTRN_170 — specified occasion, wrong document type

Query: Pakistan vs West Indies, second T20, “effects”/result.

| Rank | Article | Label |
| --- | --- | --- |
| 1, 2, 5 | Men’s second T20 toss (UAE / Trinidad / Port of Spain) | **PARTIALLY_RELEVANT** |
| 3 | Women’s second T20 result | **TOPICALLY_RELATED** |
| 4 | Extra T20s added to a tour | **TOPICALLY_RELATED** |

Query-level ambiguous: **no** (teams + format + “second T20” are specified).

### QTRN_189 — entity fragment

Query: `ئی سی سی کا`.

| Rank | Article | Label |
| --- | --- | --- |
| 1–5 | ICC chairman / big-three / committee / IPL comments | **TOPICALLY_RELATED** |

Query-level ambiguous: **yes**.

### QTRN_225 — genre only

Query: science-fiction action film.

| Rank | Article | Label |
| --- | --- | --- |
| 1–5 | Alien / Transformers / Chappie teasers | **PARTIALLY_RELEVANT** |

Query-level ambiguous: **yes**.

---

## 5. What this rubric is not

- Not a way to raise official Hit@5.
- Not fusion, reranking, or query repair.
- Not an annotation of H001–H040.
