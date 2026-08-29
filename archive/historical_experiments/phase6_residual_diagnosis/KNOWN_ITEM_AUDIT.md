# Known-item vs relevance audit

Qualitative only. **Official metric stays exact `source_doc_id` Hit@5.**  
This audit does not relabel Phase 5 scores. No H001–H040. No system change.

The 10 script-aware misses were inspected using: the query, the source headline, a body clip, and the Top-5 headlines from the frozen script-aware room (and Headline for comparison).

## Labels used

- **CLEARLY_IRRELEVANT** — Top-5 not about the query topic
- **PARTIALLY_RELATED** — same broad domain, not the same event/entity instance
- **TOPICALLY_RELEVANT_NEIGHBOUR** — same event family / entity / beat; a reader could accept them as related news
- **AMBIGUOUS** — several returned articles are as plausible as the designated source for this query string

## Per-query

### QTRN_010 (internal_val, urdu) — TOPICALLY_RELEVANT_NEIGHBOUR

Query is the source headline without the last word `شکست`. BM25 Top-5 are other South Africa vs New Zealand cricket articles. Headline cosine recovers the exact source at rank 1. This is a **known-item identity** miss for BM25, not an off-topic miss.

### QTRN_031 (internal_val, roman_urdu) — TOPICALLY_RELEVANT_NEIGHBOUR

Source: Pakistan reach the **final** of the World Team Snooker Championship. Frozen Method D rank **9**. Top-5 are other Pakistan snooker-championship reports (semi-final, other players). Headline (after dictionary transliteration) is irrelevant (`فیشن پاکستان ویک`, PSL, etc.). Lexical room is on-topic; exact article is a near-duplicate ranking problem.

### QTRN_099 (internal_val, mixed) — TOPICALLY_RELEVANT_NEIGHBOUR

Query = `ویمن کرکٹ میچ پاکستان` + generation suffix `Pakistan news update`. Rank 9. Top-5 are other Pakistan women’s cricket stories. The Urdu fragment is a **beat**, not a unique match report. Headline room is pulled toward `Pakistan` and returns Pakistan–India cricket, not women’s cricket.

### QTRN_108 (internal_val, mixed) — TOPICALLY_RELEVANT_NEIGHBOUR

Query = `عالمی نمبر ایک ٹیم` + suffix. Source is Pakistan receiving the ICC Test mace. Not in Top-50. Top-5 are other “world number one” ranking stories (India ODI, Pakistan T20, etc.). On-topic **ranking news**, wrong instance and format.

### QTRN_168 (dev, urdu) — TOPICALLY_RELEVANT_NEIGHBOUR

Query copies a repeated PSX wire template (`کاروباری ہفتے کا تیسرا روز…`) and drops the distinctive point delta / close. BM25 Top-5 are the **same template on other dates**. Headline rank 1. Known-item / temporal neighbours.

### QTRN_170 (dev, urdu) — TOPICALLY_RELEVANT_NEIGHBOUR

Query is PAK vs WI second T20 plus the generation suffix `کے اثرات کیا ہیں`. BM25 rank 37 among many T20/WI articles (toss reports, women’s T20, other series). Headline rank 4. Related cricket, not the designated match report.

### QTRN_189 (dev, mixed) — PARTIALLY_RELATED

Query is only `ئی سی سی کا` + suffix. Source is ICC–Interpol anti-corruption. Top-5 are other ICC personnel stories. Same organisation, **not** the interpol event. Distinctive body terms never entered the query (title was clipped).

### QTRN_216 (internal_val, mixed) — TOPICALLY_RELEVANT_NEIGHBOUR

Query is the entity `ایس ای سی پی` + suffix. Source is a record month of company registrations. Top-5 are other SECP articles (fraud brokers, filings, Companies Act). Same entity, different events. Not in Top-50.

### QTRN_225 (dev, mixed) — PARTIALLY_RELATED

Query is the genre `سائنس فکشن ایکشن فلم` + suffix. Source is the **Ant-Man** teaser (`انٹ مین` not in the query). Top-5 are other sci-fi teasers (Alien, Transformers, …). Same genre, different films.

### QTRN_258 (internal_val, urdu) — AMBIGUOUS

Query and source headline are nearly identical to a cluster of Sindh CNG-station opening wires (`سندھ بھر میں سی این جی اسٹیشنز صبح … کھل`). BM25 rank 23; Headline rank 7. Several Top-5 headlines are as good a match as the labelled source. This is **source_doc_id under-determination**, not a random retrieval fail.

## Counts (residual misses only)

| Label | n |
| --- | ---: |
| TOPICALLY_RELEVANT_NEIGHBOUR | 7 |
| PARTIALLY_RELATED | 2 |
| AMBIGUOUS | 1 |
| CLEARLY_IRRELEVANT | 0 |

**None of the 10 script-aware Top-5 lists is clearly off-topic** in the BM25 room. Headline Top-5 *is* off-topic for mixed queries (the Latin suffix `Pakistan news update` hijacks MiniLM).

## Implication

Under graded topical relevance, a large share of these “failures” would not be zeros. Under official known-item Hit@5 they remain zeros. Do not raise Phase 5 Hit@5. Any architecture that only chases exact `source_doc_id` on truncated mixed titles and wire-copy clusters will overfit this construction process.
