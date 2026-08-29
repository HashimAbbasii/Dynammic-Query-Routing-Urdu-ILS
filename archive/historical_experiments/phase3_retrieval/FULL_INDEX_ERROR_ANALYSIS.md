# Full-index error analysis

Eval = Phase 2 **dev + internal_val** only (n=78). Known-item = the article the query was written from. Frozen H001–H040 unused.

## Pool mix

| Slice | n |
| --- | --- |
| Urdu | 46 |
| Roman Urdu | 23 |
| Mixed | 9 |
| short | 33 |
| contextual | 27 |
| detailed | 9 |
| ambiguous | 9 |

## Outcome counts (source in top-5)

| Outcome | n | What it means |
| --- | --- | --- |
| Both hit | 19 | Source is easy in both rooms |
| Headline only | 16 | Full room loses a document the title room finds |
| Full only | **1** | Full room almost never uniquely helps |
| Both miss | 42 | Known-item not in either top-5 |

Full source-in-top-15: **22 / 78**. Chunk “might recover if a full chunk ANN existed”: **11 / 78** (source cosine to best chunk > 15th Chroma neighbor, but source not in those 15). That is a **hypothesis**, not a measured ANN result.

## 1. Full win (n=1) — QTRN_140 (Urdu, detailed, lead)

Query is the **lead sentence** of the body: gold price 1467 USD/oz.

- Headline rank: not in 15. Full rank: **1**. Chunk re-rank: 4.
- cos(q, headline)=0.56, cos(q, truncated full)=**0.83**, cos(q, best chunk)=0.82.

The query string **is** the body lead. The encoder’s 128-token full vector is “title + lead”, so this is the one case where the full room is the right string. Headline neighbors are other gold-price titles (same topic, wrong day/article).

**Indexing vs query:** not a query-processing bug. The full vector happens to contain the query.

## 2. Headline wins — named entity in the title

### QTRN_003 (Urdu, contextual / why)

Query: Urmila Matondkar’s 40th birthday, plus the template “کیوں ہوا”.

- Headline rank 1 (cos 0.98). Full rank not in 15 (cos 0.77; best chunk 0.82).
- Full top-1 is **Aishwarya Rai’s 40th birthday** — same template, wrong person.

The title is a tight name+event key. The truncated full vector dilutes the name with boilerplate birthday biography and collides with other celebrity-birthday articles. Template words (`کیوں ہوا`) do not select the body.

### QTRN_012 (Urdu, contextual / why)

Query ≈ title “نیپرا نے کراچی کے صارفین پر پھر بجلی گرادی” + “کیوں ہوا”.

- Headline rank 1 (cos 0.93). Full miss (cos 0.70; best chunk 0.80).
- Full neighbors: other K-Electric / NEPRA tariff stories.

Same pattern: **title is the unique key; body is a cluster of tariff articles.**

### QTRN_010 (Urdu, short, 569 tokens)

Query is a clipped title about South Africa vs New Zealand.

- Headline rank 1 (cos 0.94). Full miss (cos 0.59). Source is long (8 chunks).
- Full top-1 is a different series (“Kiwis beat Kangaroos”).

Truncation + topical crowding. One vector cannot keep “South Africa beat New Zealand in *this* ODI series” distinct from other NZ series stories.

## 3. Both miss — Urdu

### QTRN_026 (effects template)

Query: “حقیقت سے قریب تر تھری ڈی چہروں کی **کے اثرات کیا ہیں**”.

Source title is about selling 3D face rights in Japan. The **effects** template dropped the informative tail (“خرید فروخت انتہائی مقبول”) and added a question the article does not answer.

- cos(q, headline)=0.43, cos(q, full)=**0.11**, best chunk=0.26.
- Retrieved: 3D *movies* / Galaxy S 3D emoji — “تھری ڈی” is the only shared token.

This is **query construction**, not a Chroma bug. Known-item is a poor target for an “effects” question nailed onto a shopping feature.

### QTRN_044 (effects template)

Query: “XCMG group Pakistani housing **کے اثرات کیا ہیں**”.

Source is an investment *announcement*. Neighbors are **stock exchange** stories (XCMG / “ایکس چینج” collision).

Template + entity ambiguity. Not fixed by chunking the lead.

## 4. Both miss — Roman Urdu

### QTRN_016

Raw: `nishnl ds aibld ti20 pntgolr kp cricket tornamnt sndh ne jeet liya`  
After dict: only `کرکٹ`, `نے`, `جیت`, `لیا` become Urdu. `nishnl ds aibld ti20 pntgolr` stays Latin.

cos ≈ 0.51–0.53 to the source, but top hits are unrelated “won a tournament” stories. See `ROMAN_URDU_ANALYSIS.md`.

### QTRN_031

`pakistan orld asnokr chimpin shp ke fainl mein phnch gaya` → partial map (`پاکستان`, `کے`, `میں`, `گیا`); `orld asnokr chimpin shp` stays Latin. Hits include “Fashion Pakistan Week”.

## 5. Both miss — mixed / known-item vs topical

### QTRN_054

Query: “سندھ کے بجٹ کیلئےتجاویز Pakistan news update”.

cos(q, source headline)=**0.76**, best chunk=0.82, yet ranks are 999. Top-5 are **other Sindh budget articles** (same year/topic, different piece).

The full index is not “returning garbage”. It is returning **on-topic substitutes**. Known-item nDCG treats them as zeros. That is an **evaluation ceiling**, not proof that retrieval is empty.

## 6. Are both-zero rows retrieval failure or MIXED-class honesty?

On this eval set, **42 / 78** both-miss top-5.

| Kind | Typical signal |
| --- | --- |
| Roman / broken transliteration | Low cosine (~0.4), Latin leftovers, off-topic titles |
| Template queries (why / effects / how) | Query no longer equals title; many topical neighbors |
| True crowding | High cosine to source *and* to neighbors; known-item loses |

MIXED in Phase 2 is therefore a **mixture of (A) genuine topical ambiguity and (B) retrieval/script failure**. It is not safe to train a 3-class router on MIXED as if it meant “either index is fine.”

## 7. Indexing vs query processing (short)

| Symptom | Likely cause |
| --- | --- |
| Full top-5 are same-topic, wrong article | Indexing/representation + known-item metric |
| Full top-5 are wrong *type* of story | Query too short / template / Roman |
| Headline rank 1, full rank 999, name in title | Truncated full vector dilutes the key |
| Query equals body lead, full rank 1 | Full room working as designed |

## 8. What we are not claiming

- We did **not** rebuild a 111k chunk ANN. Eleven “might recover” flags are not extra hits.
- We did **not** judge human relevance of neighbors. Several both-miss rows look topically fair.
