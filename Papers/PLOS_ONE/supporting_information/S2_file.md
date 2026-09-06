# S2 File. Independent second annotation (A2): reliability analysis only

This file reports independent second-annotator labels on the same frozen Phase 12 U Top-5 lists (U001–U040; 200 documents). Retrieval, M0, queries, ranks, document identifiers, and Annotator-1 labels were not modified.

**Official naturalistic result remains Annotator-1 Success@5 = 23/40 = 57.50%.**

Annotator-2 Success@5 = 26/40 = 65.00% is a reliability statistic. It does not replace 23/40. The two rates are not averaged and are not a new official metric.

Per-query A1 versus A2 labels are in S4 Table. This file contains no article bodies and no headline/snippet dumps.

## Annotators

- **Annotator 1 (official):** wrote the U queries under the Phase 12 protocol and later labeled the frozen Top-5 from headline and snippet (S1 Text). Official Success@5 = 23/40 = 57.50%.
- **Annotator 2 (reliability):** Areena Rahman independently labeled the same 200 documents. Annotator-1 labels were not shown. A2 Success@5 = 26/40 = 65.00% does not replace 23/40.

Independent annotation does not prove absence of bias. Annotator 1 remains both query author and original judge.

## Scale and Success@5 definition

Labels A–E follow S1 Text. A query succeeds if at least one Top-5 document is A or B.

## Annotator-1 results (official)

| Metric | Result |
| --- | --- |
| Success@5 | 23/40 = 57.50% |
| Label counts (200) | A 41, B 26, C 53, D 80, E 0 |

## Annotator-2 results (reliability only)

| Metric | Result |
| --- | --- |
| Success@5 | 26/40 = 65.00% |
| Label counts (200) | A 60, B 32, C 28, D 80, E 0 |

Queries where Success@5 differs: U018, U024, U035, U037, U039.

## Five-way agreement

| Item | Value |
| --- | --- |
| Judgments | 200 |
| Agreements | 135 |
| Disagreements | 65 |
| Raw agreement | 135/200 = 67.50% |
| Cohen’s kappa | 0.5490 |

Kappa used sklearn.metrics.cohen_kappa_score (sklearn 1.7.2), unweighted, labels A–E. Landis and Koch (1977) name 0.41–0.60 as moderate; that naming is a convention, not a validity test.

## Binary agreement (secondary)

Relevant = A or B. Not relevant = C, D, or E. This does not replace five-way labels.

| Item | Value |
| --- | --- |
| Agreements | 169 |
| Disagreements | 31 |
| Raw agreement | 169/200 = 84.50% |
| Cohen’s kappa | 0.6816 |

## Confusion matrices

Rows = Annotator 1. Columns = Annotator 2.

### Five-way

| A1 \ A2 | A | B | C | D | E |
| --- | ---: | ---: | ---: | ---: | ---: |
| A | 37 | 3 | 0 | 1 | 0 |
| B | 16 | 8 | 2 | 0 | 0 |
| C | 7 | 21 | 18 | 7 | 0 |
| D | 0 | 0 | 8 | 72 | 0 |
| E | 0 | 0 | 0 | 0 | 0 |

### Binary (secondary)

| A1 \ A2 | relevant | not_relevant |
| --- | ---: | ---: |
| relevant | 64 | 3 |
| not_relevant | 28 | 105 |

## Disagreement shape

- Document-level five-way disagreements: 65 / 200
- A/B boundary only (A↔B): 19
- Adjacent on A–B–C–D (A↔B, B↔C, or C↔D): 57
- Disagreements that change useful (A/B) versus not: 31

Disagreements were not adjudicated. No third annotator was used.

## Integrity notes

The 200 A2 rows match the frozen Top-5 on query identifier, rank, and document identifier. Forty-two BM25 score strings differed at floating-point display precision after spreadsheet round-trip; identifiers were required to match. No A2 labels were missing. No labels outside A–E occurred. E did not occur for Annotator 1.

## Independent annotation instructions (A2)

These instructions were used for Annotator 2. They match the A1 rubric in S1 Text.

For each of 200 rows (40 queries × 5 ranks):

1. Read the query text, headline, and snippet only.
2. Assign exactly one label: A, B, C, D, or E.
3. Do not search the web. Do not invent articles. Do not use retrieval scores as a relevance signal.
4. Prefer B over A unless the need is clearly satisfied. Prefer C over B unless the article helps answer the asked need. Use E only if A–D cannot be decided from headline and snippet.
5. Temporal “today / current” wording: A means the article states the requested type of fact for a dated occasion in the article, not today’s calendar date.
6. Recurring undated wires (gold price, budget date, eclipse, stock close): the same wire type can be A even if dates differ.
7. Person lookups: an article whose main subject is that person is A. Same-person news that misses a specified slot is C.

Headline and snippet text used during labeling is not redistributed in this Supporting Information package.

## Limitations

Two annotators only. Annotator 1 authored the queries. Labels used headline plus snippet, not full article text. n = 40 queries / 200 documents. Kappa describes this sample. Agreement does not prove that either annotator is correct and does not prove lack of bias.

This analysis does not retune M0 and does not change the official Annotator-1 Success@5 of 23/40.
