# Phase 10C annotation addendum (H001–H040)

Phase 7 `ANNOTATION_RUBRIC.md` supplies labels **A–D** and **E = AMBIGUOUS** (use E only when A–D cannot be decided after reading headline + snippet).

This addendum applies **only** to judging `experiments/phase10b_frozen_dump/TOP5_FOR_ANNOTATION.csv`.

## Differences from Phase 7

- Judge the **raw** `query_text`. Do not strip `کیوں ہوا` / `کیسے ہوا` / `کے اثرات کیا ہیں` / `Pakistan news update`.
- Do not use SHORT/LONG trap gold, `source_doc_id`, MiniLM, or `heldout_retrieval_template.csv`.
- Do not search the corpus for a better document.

## Temporal queries

If the query contains `آج`, `aaj`, `موجودہ`, or `mojooda`, set `query_asks_today=1`.

The corpus is a static archive. Do not mark a document **D** only because it is not from the annotator’s calendar day.

For these queries, **A** means the article states the requested **type of fact** (price, temperature, index, fixture/result, etc.) for a **specific dated occasion in the article**.

## Uncertainty

- A vs B: prefer **B** unless the document clearly satisfies the need.
- B vs C: use **B** only if the document provides meaningful information toward the requested answer.

## Padding

Do not invent documents. H036 has one row; label that row only.
