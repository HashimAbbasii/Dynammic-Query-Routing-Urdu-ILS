# Independent annotation instructions

Judge the **200 retrieved articles** in `U_TOP5_FOR_INDEPENDENT_ANNOTATION.csv`.

There are **40 queries** (`U001`–`U040`). Each query has **5** articles (ranks 1–5).

Fill **only** the `relevance_label` column. Do not change any other column.

---

## What to look at

For each row, read:

1. `query_text` — the search query
2. `headline`
3. `news_text_or_snippet`

Assign **exactly one** label: **A**, **B**, **C**, **D**, or **E**.

Judge from the headline and snippet only. Do not search the web. Do not open other files. Do not invent articles. Do not use the `bm25_score` column as a relevance signal.

---

## Labels

| Code | Name | Meaning |
| --- | --- | --- |
| A | RELEVANT | Directly satisfies the need. A reader could stop here. |
| B | PARTIALLY_RELEVANT | Same event or occasion, but does not fully answer the query. |
| C | TOPICALLY_RELATED | Same topic, entity, or genre, but not the asked need. |
| D | NOT_RELEVANT | Does not meaningfully address the query. |
| E | AMBIGUOUS | Use only if A–D cannot be decided from the headline and snippet. |

### Choosing between labels

- Prefer **B** over **A** unless the need is clearly satisfied.
- Prefer **C** over **B** unless the article helps answer the asked need.
- Use **E** only when the snippet is genuinely insufficient for A–D.

### Temporal queries

If the query uses *آج* / `aaj` / *موجودہ* / `mojooda` (or similar “today / current” wording):

- **A** means the article states the requested **type of fact** for a **dated occasion in the article**.
- Do **not** judge against today’s calendar date.

### Recurring news with no date in the query

For wires such as gold price, budget date, eclipse, or stock close: the same type of wire can be **A** even if the date in the article differs from another article.

### Named-entity queries

If the query is a person lookup: an article whose **main subject** is that person is **A**. News about the same person that misses a specified slot (for example a different tournament or show than the one asked) is **C**.

---

## How to work through the sheet

1. Open `U_TOP5_FOR_INDEPENDENT_ANNOTATION.csv`.
2. Work query by query (`U001`, then `U002`, …).
3. For each of the five rows, enter `A`, `B`, `C`, `D`, or `E` in `relevance_label`.
4. Leave no blank labels. Do not use other codes.

When finished, return the filled CSV. Do not add commentary columns unless asked.
