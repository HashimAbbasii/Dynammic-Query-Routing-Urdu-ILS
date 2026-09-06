# S1 Text. Human relevance annotation protocol (U001–U040)

This protocol is the official Annotator-1 (A1) labeling protocol for the frozen Phase 12 naturalistic evaluation. It judges the sealed Top-5 lists for queries U001–U040 only.

It does not rerun retrieval. It does not modify the frozen system M0. It does not use H001–H040, Phase 10C qrels, or known-item ExactSource Hit@5.

Official Success@5 remains Annotator 1: **23/40 = 57.50%**. An independent second annotation (A2) is a reliability analysis only; it does not replace 23/40. See S2 File and S4 Table.

## Labels

Assign exactly one label per retrieved article, from headline and snippet only.

| Code | Name | Meaning |
| --- | --- | --- |
| A | RELEVANT | Directly satisfies the need; a reader could stop here |
| B | PARTIALLY_RELEVANT | Same event or occasion, but does not fully answer |
| C | TOPICALLY_RELATED | Same topic, entity, or genre, not the asked need |
| D | NOT_RELEVANT | Does not meaningfully address the query |
| E | AMBIGUOUS | Only if A–D cannot be decided from headline and snippet |

## Decision rules

- Judge the raw query text.
- Prefer **B** over **A** unless the need is clearly satisfied.
- Prefer **C** over **B** unless the article helps answer the asked need.
- Do not search for a better document. Do not invent hits.
- Temporal queries using آج / `aaj` / موجودہ / `mojooda`: **A** means the article states the requested type of fact for a dated occasion in the article, not the annotator’s calendar day.
- Recurring wires with no date in the query (gold price, budget date, eclipse, stock close): the same wire type can be **A** even if dates differ.
- Named-entity lookups: an article whose main subject is that person is **A**. Same-person news that misses a specified slot (for example a different tournament) is **C**.

## Metrics

- Success@5: a query succeeds if at least one Top-5 document is A or B. Rate = successes / 40.
- Conservative P@5: mean over queries of (count of A labels / 5).
- nDCG@5 gains: A = 3, B = 2, C = 1, D = 0, E = 0.
- MRR: 1 / rank of the first A or B; 0 if none.

nDCG includes topical C. A list of five C documents can have nDCG@5 = 1.0 with no A or B. Success@5 and MRR are the usefulness metrics.

## Frozen official A1 results (do not recompute as a replacement)

- Success@5 = 23/40 = 57.50%
- Conservative P@5 = 0.2050
- nDCG@5 = 0.6460
- MRR = 0.4542
- Label counts on 200 documents: A 41, B 26, C 53, D 80, E 0

Per-query A1 labels are in S2 Table.
