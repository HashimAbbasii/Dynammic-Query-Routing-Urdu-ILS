# Phase 5 — Pre-registered methods

Written **before** method outcomes were computed.

Eval pool: Phase 2 `dev` + `internal_val` only (`n=78`).  
**H001–H040 unused.** No SVM retrain. No RRF / score fusion / reranker as a system.  
BM25 hyperparameters stay frozen from Phase 4B: Okapi `k1=1.5`, `b=0.75`.  
Tokenizer stays frozen: `[\u0600-\u06FF]+|[A-Za-z0-9]+`, lowercase, no stemming.

Selection set: **DEV queries with `language_type == roman_urdu` only.**  
Methods A–D are Roman-Urdu retrieval strategies. Method E is analysis, not a selectable system.

## Selection rule (frozen)

1. **Primary:** Hit@5
2. **Secondary:** nDCG@5
3. **Tie-break:** lower mean query latency (search only, not index build)

Do not change this rule after seeing scores.  
Do not select on `internal_val`.  
Do not select Method E.

After DEV selection, freeze **one** method among {A, B, C, D} and run it **once** on `internal_val` Roman queries.

---

## Method A — Raw Roman BM25 (baseline)

Roman query (unmodified) → existing Urdu-script BM25 index  
Index field: `combined_text` (Headline + News Text), same as Phase 4B.

Expected: script mismatch, Hit@5 ≈ 0.

---

## Method B — Existing dictionary transliteration + BM25

Roman query → `validate/dual_index_routing/retrieve.py::transliterate_roman`  
→ Urdu BM25 (same index as A).

Existing logic, unchanged:

- If Urdu-character ratio ≥ 0.3, leave query unchanged.
- Else split on whitespace, map `token.lower()` through `models/roman_urdu_dict_expanded.json`.
- Unmapped tokens kept as-is.

**No new dictionary entries. No eval-query mappings.**

---

## Method C — Rule-based normalization + transliteration + BM25

One general pipeline applied to **every** query. No query-id rules.

Then: transformed query → Urdu BM25 (same index as A).

### C1. Unicode / case

- NFKC normalize
- Lowercase

### C2. Repeated Latin letters

On Latin spans only: collapse 3+ identical letters to 2  
(`aaa` → `aa`; do **not** collapse `aa` → `a`).

### C3. Tokenize

Same frozen tokenizer as BM25.

### C4. Closed spelling-variant table

Map alternative Latin spellings onto **keys that already exist** in the repository dictionary.  
This table is closed. It was not built by inspecting eval-query ranks.

| variant | canonical dict key | rationale |
| --- | --- | --- |
| kia | kya | common Roman Urdu spelling of کیا |
| kiya | kya | already in dict; canonicalise to one key |
| nahin | nahi | common extra-n spelling |
| nai | nahi | common shortened spelling |
| mai | mein | common spelling of میں |

No other aliases. In particular: no aliases for individual person/place names, and no mappings added for a specific `QTRN_*` string.

### C5. Dictionary lookup

For each token, `dict.get(token)` using the **existing** `roman_urdu_dict_expanded.json` only.

### C6. Preserve

- Tokens that already contain Urdu letters: keep
- Digits / alphanumerics with a digit: keep (`ti20`, `2018`)
- Tokens still fully Latin after C5: apply C7

### C7. Greedy grapheme inverse of Phase 2 `_CHAR_ROMAN`

This is the inverse of the **already published** Phase 2 character table in `experiments/phase2_oracle/run_phase2_pipeline.py`. It is not derived from eval queries.

Longest-match, left to right:

| Latin | Urdu |
| --- | --- |
| aa | آ |
| ch | چ |
| kh | خ |
| gh | غ |
| sh | ش |
| zh | ژ |
| a | ا |
| b | ب |
| p | پ |
| t | ت |
| j | ج |
| s | س |
| r | ر |
| z | ز |
| d | د |
| f | ف |
| q | ق |
| k | ک |
| g | گ |
| l | ل |
| m | م |
| n | ن |
| o | و |
| h | ہ |
| i | ی |
| e | ے |
| u | و |
| w | و |
| y | ی |
| v | و |
| c | ک |

Unlisted characters kept as-is. Ambiguous letters use one default (e.g. `t` → ت, never ٹ/ط). This is lossy on purpose; Method D exists to test the non-inverted direction.

---

## Method D — Romanized-document BM25

Keep the original Roman query.

Build a **second** BM25 index over **all** 111,860 articles.  
The same token romanizer is applied to every document. Not only source documents of eval queries.

Per token (after the frozen tokenizer):

1. If the token contains Urdu letters:
   - If the exact token is a value in `roman_urdu_dict_expanded.json`, emit the first reverse-mapped Latin key (`load_reverse_roman` / `setdefault` — same as Phase 2).
   - Else emit `naive_roman_word` from Phase 2 `_CHAR_ROMAN`.
2. If the token is already Latin / alphanumeric: lowercase and keep.

This is the document-side counterpart of Phase 2 `title_roman` generation, applied to `combined_text`.  
It is **not** a new mapping invented from QTRN spellings.

Report: index build time, in-memory size, estimated romanized-text size.

Query: original Roman string, tokenized, searched on this index.

---

## Method E — Multi-view analysis (not selectable)

For Roman queries only, independently:

1. **View 1 (query-side):** Method C query → Urdu BM25
2. **View 2 (doc-side):** Method D (original Roman query → romanized corpus BM25)

Report:

- Hit@5 of each view
- Union Hit@5 (source in either top-5)
- Overlap (source in both top-5)
- Oracle overlap counts

Also report View B ∪ View D as a secondary diagnostic.

**Do not** RRF, interpolate scores, or call the union a deployable system.

---

## Mixed-query policy (pre-registered)

Oracle `mixed` queries contain both Urdu script and a Latin template suffix.

- **Deployable routing:** MIXED → Urdu BM25 (Urdu tokens can match the Urdu index).
- **Analysis only:** also run the selected Roman method and report union / oracle. No fusion.

## Urdu-query policy (pre-registered)

URDU → Urdu BM25. Do not run Methods B–D on Urdu queries in the deployable router.

## Script detector (pre-registered)

Deterministic, not an SVM.

```
urdu = count of characters in U+0600..U+06FF
latin = count of ASCII letters
if urdu == 0 and latin == 0: OTHER
elif urdu > 0 and latin > 0: MIXED
elif urdu > 0: URDU
else: ROMAN
```

---

## What this phase will not do

- Open or use H001–H040
- Retrain the SVM
- Tune `k1` / `b`
- Add dictionary rows after seeing ranks
- Manually fix QTRN_003, QTRN_014, or any other id
- Build RRF, a reranker, or long-context indexes
- Tune on `internal_val` or on the pooled 78
