# Phase 12 U annotation protocol

Judges the **frozen** Phase 12 Top-5 for **U001–U040** only.

Does not rerun retrieval. Does not modify M0. Does not load H001–H040 or Phase 10C qrels.

## Labels (Phase 7)

Exactly one label per retrieved article, from headline + snippet only.

| Code | Name | Meaning |
|---|---|---|
| A | RELEVANT | Directly satisfies the need; a reader could stop here |
| B | PARTIALLY_RELEVANT | Same event/occasion, but does not fully answer |
| C | TOPICALLY_RELATED | Same topic/entity/genre, not the asked need |
| D | NOT_RELEVANT | Does not meaningfully address the query |
| E | AMBIGUOUS | Only if A–D cannot be decided from headline+snippet |

## Phase 12 / 10C rules that are not H-id-specific

- Judge **raw** `query_text` (no QTRN suffix stripping).
- Temporal (`آج` / `aaj` / `موجودہ` / `mojooda`): `query_asks_today=1`. **A** = the article states the requested **type of fact** for a **dated occasion in the article**, not the annotator’s calendar day.
- A vs B: prefer **B** unless the need is clearly satisfied.
- B vs C: **B** only if the article helps answer the asked need.
- Do not search for a better document. Do not invent hits.
- Recurring wires with no date in the query (gold price, budget date, eclipse date, stock close): same wire type can be **A** even if dates differ (Phase 7 §3).
- Named-entity lookups (`محمد رضوان`, `virat kohli`): an article whose **main subject** is that person is **A**. Same-person news that misses a specified slot (e.g. PSL vs Tests) is **C**.

## Metrics

- Success@5: ≥1 A or B in available Top-5 / 40
- Conservative P@5: mean(count of A / 5)
- Variable P@5: mean(count of A / min(5, n_hits))
- nDCG@5: gains **A=3, B=2, C=1, D=0, E=0** (Phase 12 sealed protocol)
- MRR: 1 / rank of first A or B; 0 if none

nDCG includes topical **C**. A list of five C documents can have nDCG@5 = 1.0 with **no** A/B. Success@5 and MRR are the usefulness metrics.

## Forbidden

Tuning M0, editing queries, ExactSource Hit@5 on U, pooling with 68/78 or with K001–K040.
