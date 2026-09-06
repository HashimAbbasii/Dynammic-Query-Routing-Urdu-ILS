# Independent annotation agreement — Phase 12 U Top-5

Analysis only. Frozen M0, U queries, Top-5 ranks, and Annotator-1 labels were not modified.
Official naturalistic result remains **Annotator-1 Success@5 = 23/40 = 57.50%**.
Annotator-2 Success@5 is a reliability statistic. It does not replace 23/40. The two rates are not averaged.

## 1. Annotation dataset

Frozen Phase 12 U Top-5 lists for naturalistic queries U001–U040.
Each query has five retrieved documents (ranks 1–5). Total judgments = 40 × 5 = **200**.

## 2. Number of annotators

**2**.

- **Annotator 1** wrote the U queries under the Phase 12 protocol and later judged the frozen Top-5 (headline + snippet).
- **Annotator 2** independently judged the same frozen Top-5 dump. Annotator-1 labels were not included in the annotation package.

Independent annotation does **not** prove absence of bias. Annotator 1 remains both query author and original judge. Annotator 2 reduces, but does not eliminate, that risk.

## 3. Number of queries

**40** (U001–U040).

## 4. Number of judgments

**200** per annotator.

## 5. Annotation scale

| Code | Name |
| --- | --- |
| A | RELEVANT |
| B | PARTIALLY_RELEVANT |
| C | TOPICALLY_RELATED |
| D | NOT_RELEVANT |
| E | AMBIGUOUS |

Success@5 (both annotators): a query succeeds if **at least one** Top-5 document is **A or B**. Same definition as `experiments/phase12_human_relevance/ANNOTATION_PROTOCOL.md`.

## 6. Exact source files

| Role | File |
| --- | --- |
| Frozen Top-5 dump | `experiments/phase12_new_unseen_evaluation/U_TOP5_FOR_ANNOTATION.csv` |
| Annotator 1 labels (authoritative 200-row qrels) | `experiments/phase12_human_relevance/U_QRELS.csv` |
| Annotator 1 per-query Success@5 (derived) | `experiments/phase12_human_relevance/U_PER_QUERY.csv` |
| Annotator 1 official metrics | `experiments/phase12_human_relevance/artifacts/metrics.json` |
| Annotator 2 labeled sheet | `experiments/phase12_independent_annotation/U_TOP5_FOR_INDEPENDENT_ANNOTATION_LABELED.csv` |

`U_QRELS.csv` is the source used here for A1. Recomputing Success@5 from those 200 labels yields **23/40**, matching `metrics.json`.

## 7. Annotator-1 results (official)

| Metric | Result |
| --- | --- |
| Success@5 | **23/40 = 57.50%** |
| Label counts (200) | A 41, B 26, C 53, D 80, E 0 |

This remains the official U headline.

## 8. Annotator-2 results (reliability only)

| Metric | Result |
| --- | --- |
| Success@5 | **26/40 = 65.00%** |
| Label counts (200) | A 60, B 32, C 28, D 80, E 0 |

Queries where Success@5 differs: U018, U024, U035, U037, U039.

## 9. Five-way agreement

| Item | Value |
| --- | --- |
| Total judgments | 200 |
| Agreements | 135 |
| Disagreements | 65 |
| Raw agreement | 135/200 = 67.50% |

## 10. Five-way Cohen's kappa

κ = **0.5490** (sklearn.metrics.cohen_kappa_score, sklearn 1.7.2; unweighted, labels A–E).

Landis and Koch (1977) convention for this value: **moderate (0.41–0.60; Landis and Koch 1977 convention)**.
Those cutoffs are a naming convention, not a validity test.

## 11. Binary agreement (secondary)

Relevant = A or B. Not relevant = C, D, or E.

| Item | Value |
| --- | --- |
| Agreements | 169 |
| Disagreements | 31 |
| Raw agreement | 169/200 = 84.50% |

This does not replace the five-way labels.

## 12. Binary Cohen's kappa (secondary)

κ = **0.6816** (sklearn.metrics.cohen_kappa_score, sklearn 1.7.2; labels relevant / not_relevant).

Landis and Koch (1977) convention for this value: **substantial (0.61–0.80; Landis and Koch 1977 convention)**.

## 13. Confusion matrices

Rows = Annotator 1. Columns = Annotator 2.

### Five-way

| A1 \ A2 | A | B | C | D | E |
| --- | --- | --- | --- | --- | --- |
| **A** | 37 | 3 | 0 | 1 | 0 |
| **B** | 16 | 8 | 2 | 0 | 0 |
| **C** | 7 | 21 | 18 | 7 | 0 |
| **D** | 0 | 0 | 8 | 72 | 0 |
| **E** | 0 | 0 | 0 | 0 | 0 |

### Binary (secondary)

| A1 \ A2 | relevant | not_relevant |
| --- | --- | --- |
| **relevant** | 64 | 3 |
| **not_relevant** | 28 | 105 |

## 14. A1 vs A2 Success@5

| Annotator | Success@5 |
| --- | --- |
| 1 (official) | 23/40 = 57.50% |
| 2 (reliability) | 26/40 = 65.00% |

Per-query labels and Success@5: `A1_A2_PER_QUERY.csv`.

## 15. Number of disagreements

- Document-level five-way disagreements: **65 / 200**.
- Of those, A/B boundary only (A↔B): **19**.
- Adjacent on A–B–C–D (A↔B, B↔C, or C↔D): **57**.
- Disagreements that change useful (A/B) vs not: **31**.
- Full list: `DISAGREEMENTS.csv` (not adjudicated).

## 16. Data-integrity issues

- A2 row count, query set U001–U040, five ranks per query, and label alphabet: **pass**.
- Same 200 documents as frozen dump on `query_id` + `rank` + `doc_id`: **yes**.
- Structural field mismatches vs frozen dump (not auto-fixed): **bm25_score=42**.
- `bm25_score` string differences, if present, are consistent with spreadsheet round-trip of floating-point scores. Query text, `doc_id`, rank, headline, and snippet were required to match for the join. The join used identifiers, not row position.
- A2 `relevance_label` is populated; other judgment files were not written into the A2 sheet.
- No missing A2 labels. No labels outside A–E.

## 17. Limitations

- Two annotators only. No third adjudicator.
- Annotator 1 authored the queries.
- Labels are from headline plus snippet, not full article text.
- The A/B and B/C boundaries are subjective by design (prefer B over A unless the need is clearly satisfied).
- n = 40 queries / 200 documents. Kappa describes this sample, not all Urdu news search.
- Agreement does not prove that either annotator is correct, and does not prove lack of bias.
- E did not occur for Annotator 1; rarity of E limits what can be said about that category.

## Interpretation

Five-way κ = 0.5490 is **moderate (0.41–0.60; Landis and Koch 1977 convention)**.
Binary A/B vs not κ = 0.6816 is **substantial (0.61–0.80; Landis and Koch 1977 convention)**.

Disagreements are listed in full rather than selected.
A substantial share of the 65 five-way disagreements are adjacent on the A–B–C–D scale (57), including 19 A↔B pairs. That pattern is consistent with rubric boundary ambiguity, especially A vs B (full vs partial answer) and B vs C (helps the need vs same topic only).
31 disagreements cross the Success@5-relevant boundary (A/B vs C/D/E). Those cases can change query-level Success@5 even when many other documents agree.

High or moderate kappa would not by itself mean the original 57.50% is unbiased: Annotator 1 still wrote the queries. Low kappa would not by itself mean the retrieval system failed: it would mean the usefulness labels are unstable.
This analysis does not retune M0 and does not change the official Annotator-1 Success@5 of 23/40.

## Generated files

| File | Contents |
| --- | --- |
| `A1_A2_COMPARISON.csv` | 200 rows, A1 and A2 labels |
| `A1_A2_PER_QUERY.csv` | 40 rows, per-query Success@5 |
| `DISAGREEMENTS.csv` | five-way disagreements only |
| `AGREEMENT_METRICS.json` | machine-readable statistics |
| `AGREEMENT.md` | this report |

