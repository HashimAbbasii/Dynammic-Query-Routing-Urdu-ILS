# Failure analysis (diagnosis only)

No system change after this analysis. No H001–H040. No query-specific rules added.

Selected method: **D**

## Recovered

Baseline Method A miss (rank > 5) → selected method Hit@5.

- Count: **22 / 23**
- DEV: 13 — QTRN_034, QTRN_038, QTRN_056, QTRN_106, QTRN_133, QTRN_139, QTRN_191, QTRN_196, QTRN_211, QTRN_214, QTRN_220, QTRN_229, QTRN_232
- INTERNAL_VAL: 9 — QTRN_016, QTRN_067, QTRN_070, QTRN_088, QTRN_094, QTRN_128, QTRN_155, QTRN_175, QTRN_205
- Selected Hit@5 ids: QTRN_016, QTRN_034, QTRN_038, QTRN_056, QTRN_067, QTRN_070, QTRN_088, QTRN_094, QTRN_106, QTRN_128, QTRN_133, QTRN_139, QTRN_155, QTRN_175, QTRN_191, QTRN_196, QTRN_205, QTRN_211, QTRN_214, QTRN_220, QTRN_229, QTRN_232

## Still failing (selected method)

Selected rank > 5: **1 / 23**

- QTRN_031 (internal_val) — Method D rank **9**, Method C rank 32, A/B rank 999. Token overlap with the romanized source article = **10**. Hit@10 succeeds. This is not a remaining script mismatch; common tokens (`pakistan`, `ke`, `mein`, …) leave the source just outside Top-5.

## All four methods miss Hit@5

**1** queries: QTRN_031

## Categories (general)

Applied to Roman queries using token overlap with the **romanized source article** and whether B/C still look Latin. Categories were not used to edit methods.

| Category | n (non-recovered) |
| --- | ---: |
| source_article_difficult_to_retrieve | 1 |

Definitions:

- **transliteration_failure** — query-side B/C leave the string mostly Latin; document-side D also misses.
- **named_entity_mismatch** — very small overlap with the romanized source (names/titles drifted).
- **spelling_variation** — some transformation happened but rank stayed > 5.
- **english_urdu_mixture** — mixed-script (not expected on this Roman subset).
- **source_article_difficult_to_retrieve** — overlap exists but BM25 still ranks the source outside Top-5 (length / common tokens).
- **source_not_lexically_similar** — zero overlap between Roman query tokens and romanized source tokens (generation tokenizer vs index tokenizer, or title-only query vs article body romanization mismatch).
- **other** — residual.

Per-query table: `artifacts/failure_categories.csv`.

This phase **stops** after diagnosis.
