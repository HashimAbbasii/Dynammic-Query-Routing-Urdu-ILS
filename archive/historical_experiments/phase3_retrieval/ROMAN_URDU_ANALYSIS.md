# Roman Urdu analysis (diagnosis only)

**Not used** to choose chunk size, k, or the selected full-index method.

Eval Roman Urdu rows in dev+internal_val: **n=23**.

## Pipeline (code)

`validate/dual_index_routing/retrieve.py` → `transliterate_roman`:

- If Urdu-script ratio ≥ 0.3, do nothing.
- Else split on whitespace and replace tokens via `models/roman_urdu_dict_expanded.json`.
- Unknown tokens stay Latin.
- Documents were embedded as Urdu script only. There is no Roman document index.

Notebook 05’s fuzzy `difflib` matcher is **not** on this path.

## Measured (eval Roman, k=15 cut at 5)

| Condition | Headline hit@5 | Full hit@5 |
| --- | --- | --- |
| Dictionary **on** (production) | 1 / 23 | 1 / 23 |
| Dictionary **off** (raw Latin) | 0 / 23 | 0 / 23 |
| Both miss @5 (production) | 22 / 23 | 22 / 23 |

Mean cosine to the **source** (production query):

| Representation | Mean cos |
| --- | --- |
| Headline | 0.407 |
| Truncated full | 0.387 |
| Best 96-token chunk | 0.408 |

On the full eval pool, mean cos(q, source headline) is **0.643**. Roman queries sit ~0.23 lower before ranking even starts.

Dictionary **does** change 22 / 23 strings, and it is not harmful in this small slice (full hits 0 → 1). It is also **not sufficient**.

## Is transliteration “correct”?

Partially, for closed-class words. Example QTRN_016:

- Raw: `nishnl ds aibld ti20 pntgolr kp cricket tornamnt sndh ne jeet liya`
- After dict: `کرکٹ`, `نے`, `جیت`, `لیا` mapped; `nishnl ds aibld ti20 pntgolr` unchanged.

The model therefore embeds a **Latin/Urdu hybrid** against Urdu titles. Neighbors share “tournament won”, not the disabled T20 pentangular.

Spellings are not normalized (`orld` ≠ `world`, `asnokr` ≠ `snooker`, `chimpin shp` ≠ `championship`). One dictionary cannot cover that noise.

## Does the embedding model “handle Roman Urdu”?

MiniLM-L12 is multilingual, but this corpus’s documents are Urdu script. A Roman query is a **cross-script** problem. The encoder is not given matched Roman documents. Cosine ~0.4 to the true source is weak relative to Urdu title queries (~0.64–0.98 when the query ≈ title).

## Does transliteration help or hurt?

On this eval Roman slice: **slight help, not a fix** (+1 known-item hit@5). Too small to justify a preprocessing change, and **out of scope for method selection**.

## Should Roman rows train a router?

No. 22 / 23 both-miss become MIXED under the Phase 2 rule. That MIXED is **script failure**, not “headline and full are interchangeable.” Using them as a third class, or to tune full-index chunking, would fit noise.

## What would be an honest next test (Phase 4+, not done)

A **separate** Roman experiment, pre-registered, not using H001–H040:

1. Better transliteration (or a learned transliterator) vs current dict, Urdu-script queries as control.
2. Or drop Roman from router training until (1) moves known-item hit@5 by a pre-set margin on **internal_val Roman only**.

Do not bake that into the full-article index first.
