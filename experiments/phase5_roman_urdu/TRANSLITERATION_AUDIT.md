# Transliteration audit

Audit of **existing** repository logic only. No mappings were added during this audit.

## 1. Which Roman words are currently mapped?

File: `models/roman_urdu_dict_expanded.json`

- Entries: **198**
- Lookup: whitespace tokens, `lower()`, exact key match
- Gate in `transliterate_roman`: if Urdu-character ratio ≥ 0.3, the query is left unchanged

The dictionary is a closed list of common function words, a few names/places (`imran`, `khan`, `lahore`, `karachi`, …), and some English news/sport terms (`cricket`, `pakistan`, `match`, …). Values are Urdu-script strings. There is no grapheme converter and no fuzzy match.

## 2. How many Roman evaluation queries are changed?

Roman evaluation queries: **23** (Phase 2 `language_type=roman_urdu`, dev + internal_val).

| | n |
| --- | ---: |
| At least one dictionary substitution | 22 |
| Unchanged (no token in the dictionary) | 1 |

Whitespace-token dictionary hits across all Roman queries: **73**.  
Whitespace tokens still unmapped and Latin: **163**.

## 3. How many remain mostly Latin?

After existing `transliterate_roman`, queries with Latin-token ratio ≥ 0.5: **22 / 23**.

Phase 2 `title_roman` generation uses reverse-dictionary lookup when an Urdu title token is an exact dictionary *value*, otherwise `naive_roman_word` (character table). Most QTRN Roman strings are therefore **lossy character romanizations**, not conventional Roman Urdu orthography. A 198-entry exact-match dictionary cannot rewrite them.

## 4. What types of spelling variation fail?

Observed **token classes** among unmapped Latin tokens (frequency sample, not a patch list):

- `krne` (n=3)
- `kilie` (n=3)
- `orld` (n=2)
- `chimpin` (n=2)
- `shp` (n=2)
- `dosre` (n=2)
- `khtm` (n=2)
- `aif` (n=2)
- `bi` (n=2)
- `fislh` (n=2)
- `on` (n=2)
- `nishnl` (n=1)
- `ds` (n=1)
- `aibld` (n=1)
- `ti20` (n=1)
- `pntgolr` (n=1)
- `kp` (n=1)
- `tornamnt` (n=1)
- `sndh` (n=1)
- `asnokr` (n=1)
- `fainl` (n=1)
- `phnch` (n=1)
- `rthr` (n=1)
- `osim` (n=1)
- `miandad` (n=1)

Failure types (general, not query-id rules):

- **Names** — person/place strings romanized letter-by-letter (`hfiz`, `babraazm`, `peshawar` is in-dict but many names are not).
- **Locations / events** — character-mapped titles, not Wikipedia-style Roman Urdu.
- **Function words** — a few are in-dict (`ka`, `ke`, `se`, `mein`, `ne`); many surface as stripped-vowel forms (`krne`, `kilie`, `mshorh`) that are not keys.
- **Spelling / vowel variation** — Phase 2 `ی→i`, `و→o`, `ا→a` produces forms unlike `kya`/`kia` user Roman Urdu.
- **English words** — some keys exist (`cricket`, `film`, `team`); others stay English (`update` is on mixed queries, not this Roman set).
- **Mixed Urdu/English** — the 23 Roman labels are Latin-only; mixed script is a separate oracle class.

Dense retrieval (Phase 4B Headline/Full/Chunk) already calls `transliterate_roman`. Raw Phase 4B BM25 did not. Neither path recovers Roman known-item Top-5 except one dense hit.

This audit did **not** add dictionary rows.
