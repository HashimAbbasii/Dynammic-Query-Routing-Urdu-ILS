# ULTRA v2 Phase 7 — Letter-name acronym expansion (query-side)

**Document type:** pre-registration / controlled design  
**Experiment ID:** PHASE7-LETTERNAME  
**Directory:** `experiments/ultra_v2/phase7_entity_norm/`  
**Branch:** `research/ultra-v2-strengthening`  
**Commit at design freeze:** `fd54ac9b65c2db93e7e16fbf0c5a40b6a6025be1`  
**Timestamp (UTC, written before scoring):** `2026-09-12T14:10:00Z`

This file must not be silently rewritten after Phase-7 scores are observed.

Phase 3–5 artifacts stay frozen. No Wikidata. No fusion. No reranking. No TEST.

---

## 1. Status

**DESIGN ONLY — NOT EXECUTED.**

User-confirmed Option 1: a **26-letter Urdu name table** plus frozen Method-D `_CHAR_ROMAN` / `naive_roman_word`, **query-side only**, retrieved with frozen Method-D BM25, Top-50, as its **own** candidate list.

---

## 2. Scientific question

Can expanding Latin **acronym-like** query tokens into Method-D-compatible **letter-name** tokens recover ExactSource golds that word-level Method D misses because Urdu news wrote those initials as letter names?

This targets the **acronym** subset of the Phase-6 entity/surface-form bucket. It does **not** claim to fix celebrity/product names (`gmail`, `aladdin`, `twitter`, …). Those would need a different, external name resource (Option 2 / Wikidata), which is **out of scope**.

---

## 3. Hypothesis

**H1:** Query-side letter-name expansion of 2–4 letter Latin tokens will put at least some previously missed golds (especially letter-named org acronyms) into the Method-D Top-50.

**H0:** The expansion does not recover a scientifically useful number of the 23 remaining four-way misses, and/or it mainly injects noise that regresses existing Method-D successes.

These hypotheses will not be changed after seeing scores.

---

## 4. Gazetteer source and independence

**Not a named-entity list. Not derived from the 23 queries or the 51-query benchmark.**

| Piece | Provenance |
| --- | --- |
| 26 Urdu names of English letters | Public Pakistani/Urdu orthographic convention for Latin letter names (primer / news style: اے، بی، سی، … زیڈ). Frozen in §5. No extra rows for specific orgs. |
| Romanization of those names | Frozen `run_phase5.naive_roman_word` / `_CHAR_ROMAN` (PLOS Method D). |
| Tokens **not** expanded | Keys of frozen `models/roman_urdu_dict_expanded.json` (198 keys, SHA-256 `30c3f61a64ec641abbb3acdbc7a8bcaf197f0238f1bf9e76c2c7ce8e590f86a3`). Those are already canonical Method-D reverse-dict hits. |

Independence: every Latin letter gets the same name. `fbr` expands if and only if it matches the frozen regex and is not a dict key — the same rule that expands `bbc`. No row was added because a diagnosed query contained that string.

---

## 5. Frozen 26-letter table

Urdu name (input to `naive_roman_word`):

| Latin | Urdu name |
| --- | --- |
| a | اے |
| b | بی |
| c | سی |
| d | ڈی |
| e | ای |
| f | ایف |
| g | جی |
| h | ایچ |
| i | آئی |
| j | جے |
| k | کے |
| l | ایل |
| m | ایم |
| n | این |
| o | او |
| p | پی |
| q | کیو |
| r | آر |
| s | ایس |
| t | ٹی |
| u | یو |
| v | وی |
| w | ڈبلیو |
| x | ایکس |
| y | وائی |
| z | زیڈ |

Toy check (not a benchmark result): `bbc` → `bi` `bi` `si`.

---

## 6. Frozen token rule (one rule, not searched)

After frozen `tokenize` (lowercased):

A token **T** is replaced by the sequence of 26-table romanizations of its letters **iff all** of:

1. `T` matches `^[a-z]{2,4}$` (length 2–4, letters only).
2. `T` is **not** a key in the frozen 198-key dictionary.

Otherwise **T** is left unchanged.

Length 5+ tokens (e.g. ordinary English words, product names) are never expanded. Mixed alphanumeric tokens (e.g. `t20`) are never expanded.

The expanded query is the concatenation of per-token outputs (one original token may become several letter-name tokens).

---

## 7. Retrieval

| Item | Value |
| --- | --- |
| Index | Frozen Method-D roman BM25 (`phase2_roman/artifacts/_index_cache.pkl` if meta matches) |
| k1, b | 1.5, 0.75 |
| Depth | Top-50 |
| Documents | **not** reprocessed |
| Encoder / NG3 / RRF / rerank | **forbidden** |

---

## 8. Corpus and queries

Same as Phases 3–5: corpus SHA-256 `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231`, n=111,860; Roman KN TRAIN+DEV **n=51**, unmodified; no TEST.

---

## 9. Metrics and secondary analysis

Primary (n=51): Hit@1, Hit@5, Hit@10, Hit@50, MRR (0 if gold not in Top-50).

Secondary:

- Overlap of Hit@50 with frozen BM25, Dense, NG3.
- Recovery of the **23** four-way misses (Phase 6 list, frozen here):  
  KN002, KN005, KN006, KN008, KN010, KN018, KN020, KN021, KN022, KN024, KN025, KN026, KN027, KN028, KN032, KN036, KN037, KN041, KN042, KN044, KN047, KN051, KN054.
- ROOM Category 1 (same 11 IDs as prior phases).
- How many queries actually received ≥1 expansion (diagnostic, not a tuning knob).

---

## 10. Decision labels (choose exactly one)

- `PHASE7 SUPPORTED` — letter-name expansion recovers a substantial share of acronym-type misses among the 23 without destroying Method-D successes.
- `PHASE7 PARTIALLY SUPPORTED` — at least one of the 23 (or a clear acronym gold) enters Top-50, but most of the 23 remain out and/or there are important regressions / remaining ROOM misses.
- `PHASE7 UNSUPPORTED` — zero recoveries of the 23, or no useful candidate-generation beyond noise.
- `BLOCKED` — corpus/query gate fail, cache meta mismatch, or TEST access.

No “≥80% = success” rule. No second table. No Wikidata in this run.

---

## 11. Stop / leakage

- No TEST query files  
- No gazetteer rows from gold documents or the 23  
- No document re-index  
- No fusion into hybrid RRF  
- Do not start Wikidata/Option 2 from this file  
