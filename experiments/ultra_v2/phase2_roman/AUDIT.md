# Phase 2 Roman Urdu implementation audit

**Date:** 2026-09-09  
**Branch:** `research/ultra-v2-strengthening`  
**Scope:** frozen M0 Roman path, dictionary, tokenizer. No TEST query text. No M0 edits. No retrieval in this document.

This audit was written **before** Phase 2 treatments were implemented.

---

## 1. How ROMAN queries are detected

Frozen function: `detect_script` in `experiments/phase5_roman_urdu/run_phase5.py`.

- `urdu` = count of characters in U+0600..U+06FF
- `latin` = count of ASCII letters A–Z / a–z
- `OTHER` if both zero; `MIXED` if both positive; `URDU` if only Urdu; else `ROMAN`

Official M0 routing (`experiments/phase12_new_unseen_evaluation/run_phase12.py` `route_m0`):

- `ROMAN` → Method D romanized-document BM25
- `URDU` / `MIXED` / `OTHER` → Urdu BM25

Latin-only English civic queries are labeled **ROMAN**. That is detector behavior, not a claim that the string is chat Roman Urdu.

---

## 2. Tokenizer

Frozen regex (M0):

```text
[\u0600-\u06FF]+|[A-Za-z0-9]+
```

Lowercased via `tokenize()`. Punctuation is a splitter. There is **no** stemming, no character n-grams, no whitespace-collapse of fused tokens (`kiahua` stays one token).

---

## 3. Dictionary load

Path: `models/roman_urdu_dict_expanded.json`  
Keys: **198**  
SHA-256 (publication): `30c3f61a64ec641abbb3acdbc7a8bcaf197f0238f1bf9e76c2c7ce8e590f86a3`

Load: `json.load` as a Latin-key → Urdu-script-value map. Exact `lower()` key match. No fuzzy match.

---

## 4. How dictionary mappings are applied

**Not on the official Method D query.**

| Method | Query | Index |
| --- | --- | --- |
| A | raw tokenize | Urdu BM25 |
| B | `transliterate_roman` (dict replace; unknown Latin kept) | Urdu BM25 |
| C | closed variants + dict + grapheme→Urdu | Urdu BM25 |
| **D (M0 Roman)** | **raw tokenize (query unchanged)** | **romanized documents** |

Reverse map: `load_reverse_roman` uses `setdefault`, so each Urdu value keeps the **first** JSON key only. That first key is the document-side canonical Latin form for dictionary values.

---

## 5. What Method D currently does

1. Tokenize every corpus article with the frozen tokenizer.
2. For each token containing Urdu letters: if the exact token is a dictionary **value**, emit the reverse-canonical Latin key; else emit `naive_roman_word` from the closed `_CHAR_ROMAN` table.
3. Latin/alphanumeric tokens: lowercase and keep.
4. Build BM25 (`k1=1.5`, `b=0.75`) over those romanized token lists (all 111,860 rows).
5. Search with the **original** Roman query tokens.

This is the document-side counterpart of Phase 2 `title_roman`, not a chat-Roman normalizer.

---

## 6. Unknown Roman tokens

**Queries are not discarded** when a token is unknown.

- Method D does not look the query up in the dictionary, so “unknown to the dict” is irrelevant on the query side.
- `BM25.search` skips terms absent from the posting list (`if t not in self.post: continue`) and continues with remaining terms.
- Therefore **preserving vs dropping OOV query terms is operationally identical** for this scorer.

R2-2 (unknown-token preservation vs drop) is **not a distinct Method D experiment**. It is already the baseline.

---

## 7. How Urdu documents are converted/indexed for Roman retrieval

Per token, `romanize_token(tok, rev)`:

1. Urdu-script token + exact reverse-dict hit → first Latin key
2. Urdu-script token, no reverse hit → character table (`ی→i`, `و→o`, `ا→a`, …)
3. Already Latin → lowercase

Empty romanizations are dropped. The roman index is a **full-corpus** second BM25, not a subset of known-item sources.

---

## 8. Query expansion

Official M0 / Method D: **none**. Query tokens are used as typed.

Method C has a closed five-entry alias table onto dictionary keys (`kia→kya`, `kiya→kya`, `nahin→nahi`, `nai→nahi`, `mai→mein`). **M0 Roman does not apply this table.**

---

## 9. Spelling variants

Inside the 198-key dictionary, several Urdu values have **multiple Latin keys**. Reverse-canonical (first key) vs later aliases:

Examples (not an exhaustive DEV-mined list; derived from JSON order):

| Urdu value | Canonical (document) | Other keys (query may use these) |
| --- | --- | --- |
| کیا | `kiya` | `kya` |
| آج | `aaj` | `aj`, `today` |
| نے | `ne` | `ny` |
| سے | `se` | `sy` |
| گیا | `gaya` | `geya` |
| حکومت | `government` | `hukumat` |
| شکست | `loss` | `shikast` |
| جیت | `jeet` | `win` |
| عدالت | `adalat` | `court` |

A user query token `kya` searches for `kya`. The romanized document token for کیا is `kiya`. That is a **closed, dictionary-internal** mismatch. It does **not** justify inventing `hy→hai` (no `hy` key exists).

Method C’s `kia→kya` would still miss Method D documents unless folded onward to `kiya`.

---

## 10. Character-level matching

None in M0 retrieval. Character table is **document romanization only**, not query n-grams. Do not add n-grams unless TRAIN/DEV failures show orthographic mismatch that alias-folding cannot address.

---

## 11. BM25

Custom `BM25` class in `run_phase5.py` (not rank-bm25, not Elasticsearch).

- `k1=1.5`, `b=0.75` (frozen; do not retune here)
- IDF: `log((N-n+0.5)/(n+0.5)+1)`
- Top-50 retrieve; official cutoff Top-5
- Zero-score documents excluded from the hit list

---

## 12. Reusable infrastructure (do not edit)

| Asset | Reuse |
| --- | --- |
| `run_phase5.py` `detect_script`, `tokenize`, `romanize_token`, `BM25`, `load_roman_dict`, `load_reverse_roman` | Import only |
| `models/roman_urdu_dict_expanded.json` | Read-only |
| `data/clean_articles.csv` | Read-only, gitignored corpus |
| Phase 12 `route_m0` | Copy the **policy**, do not edit Phase 12 |
| v2 TRAIN/DEV `queries_kn.csv` | Authorized development |
| `verify_test_seal.py` | Confirm seal; do not read TEST queries |

---

## 13. Must remain untouched

`experiments/phase5_roman_urdu/run_phase5.py`, `experiments/phase12/**`, `results/**`, `Papers/PLOS_ONE/**`, QTRN/H/K/U, Phase 11 inventories, frozen qrels, TEST query files.

---

## 14. Indexes / artifacts

Roman and Urdu BM25 indexes may be rebuilt in `experiments/ultra_v2/phase2_roman/` as a **cache**. That cache is not a frozen publication artifact and must not overwrite Phase 5/12 outputs.

---

## 15. Authorized development data

| Split | KN file | Use |
| --- | --- | --- |
| TRAIN | `benchmark/train/queries_kn.csv` | Development, error taxonomy draft |
| DEV | `benchmark/dev/queries_kn.csv` | Confirmation; not TEST |
| TEST | sealed | **Forbidden** |

NL: no `qrels.csv`. Official NL Success@5 is **pending pooled annotation**. Do not invent gold documents.

---

## 16. Hypotheses after audit (not yet tested)

**H-canon:** Folding query tokens onto reverse-dictionary canonical keys (and Method C’s five aliases onto those keys) will change Roman KN ranks, because documents emit the first JSON key.

**H-expand:** Bounded expansion to all sibling keys for the same Urdu value may recover queries that use a non-canonical spelling, at the cost of extra function-word posting lists.

**H-preserve:** Unknown-token drop vs keep cannot change Method D BM25 scores.

**H-not-assumed:** These treatments may improve, hurt, or do nothing on v2 TRAIN/DEV. Historical K/U Roman weakness does not licence mining those sets for rules.

---

## 17. Experimental order justified by this audit

1. **R2-B0** — frozen M0 on v2 TRAIN/DEV KN (no modifications).
2. **R2-2** — skip as a retrieval treatment; record as vacuous for this BM25.
3. **R2-1** — query-side canonical fold from the frozen dictionary (+ frozen Method C five aliases). Unknown tokens unchanged.
4. **R2-3** — only if R2-1/B0 shows spelling/canonical mismatch; bounded sibling expansion, no n-grams, no dense retrieval.

Do not add `hy→hai` or other new keys unless a later pre-registered experiment justifies a **single closed addition** from TRAIN evidence without TEST.
