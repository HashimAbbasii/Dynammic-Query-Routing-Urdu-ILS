# Final evaluation protocol

Frozen **2026-08-27T12:36:10Z**. Do not edit after H001–H040 are opened.

This protocol is for **one** held-out run on H001–H040.  
It does not authorize tuning, architecture changes, or a second test pass.

---

## 1. Dataset

**Development / validation (already used; not the final test):**

- Phase 2 `dev` + `internal_val`
- `n = 78`
- IDs `QTRN_*` from `experiments/phase2_oracle/oracle_all.csv`
- Splits in that file: `dev`, `internal_val` (and `train`, unused for this freeze)

**Final held-out test (sealed until this protocol is executed once):**

- IDs **H001–H040**
- `n = 40`
- Source of IDs: `validate/dual_index_routing/labels/heldout_traps.py` / held-out judgment files already in the repo
- **Do not open query text, source articles, ranks, or labels until the checklist in `FINAL_TEST_CHECKLIST.md` is complete and the run has started.**

Queries used for development must not be mixed into the official H001–H040 score.

---

## 2. Corpus

- File: `data/clean_articles.csv`
- Encoding: UTF-8 with BOM (`utf-8-sig`)
- Size: **111,860** rows
- Bytes: 540,050,203
- SHA-256: `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231`
- Article identifier: **row index** (0-based pandas/read order) = `source_doc_id`
- Retrieval field: `combined_text` if present, else `Headline` + space + `News Text`

Do not subset, reshuffle, or re-clean the corpus for the test run.

---

## 3. Query format

- Input: raw query string as stored for that ID.
- No manual rewriting.
- No query-specific dictionary rows.
- No stripping of mixed-query template suffixes at retrieval time (that stripping was a Phase 7 **annotation** rule only).

---

## 4. Script detection

Deterministic Unicode rule from `experiments/phase5_roman_urdu/run_phase5.py::detect_script`. Not an SVM.

```
urdu = count of characters in U+0600..U+06FF
latin = count of ASCII letters A–Z / a–z
if urdu == 0 and latin == 0: OTHER
elif urdu > 0 and latin > 0: MIXED
elif urdu > 0: URDU
else: ROMAN
```

On Phase 2 n=78 this matched oracle `language_type` **78/78**.  
If a test query is `OTHER`, treat it as URDU BM25 and record the exception. Do not invent a new class.

---

## 5. Retrieval routing

| Detector label | Index | Query tokens |
| --- | --- | --- |
| URDU | Urdu BM25 | `tokenize(query)` |
| MIXED | Urdu BM25 | `tokenize(query)` |
| ROMAN | Romanized-document BM25 | `tokenize(query)` (original Latin tokens; Method D) |

Do not send ROMAN queries to Urdu BM25.  
Do not send URDU queries to the romanized index.  
Do not fuse rooms.

Implementation reference: `experiments/phase5_roman_urdu/run_phase5.py` and `experiments/phase6_residual_diagnosis/run_phase6.py`.

---

## 6. BM25 configuration

Okapi BM25, **untuned**:

- `k1 = 1.5`
- `b = 0.75`
- IDF: `log((N - n + 0.5) / (n + 0.5) + 1.0)`
- Implementation: class `BM25` in `experiments/phase5_roman_urdu/run_phase5.py`

Tokenizer (both indexes):

```
(?u)[\u0600-\u06FF]+|[A-Za-z0-9]+
```

applied to `text.lower()`. No stemming. No stopword list at retrieval time.

**Urdu index:** tokens as above on `combined_text`.

**Roman index:** for each Urdu-script token, reverse-map via `models/roman_urdu_dict_expanded.json` (`setdefault` first Latin key wins, same as Phase 2 `load_reverse_roman`); else `naive_roman_word` using Phase 2 `_CHAR_ROMAN`. Latin/alphanumeric tokens kept lowercased. Entire corpus, not source-only.

Dictionary path: `models/roman_urdu_dict_expanded.json` (198 keys). Do not add keys.

---

## 7. Top-K

- Retrieve **top_k = 50** internally (same as Phase 5/6) so Hit@10 and Hit@15 are defined.
- Official cutoff for Hit@5 / P@5 / nDCG@5: **k = 5**.
- Report Hit@10 and Hit@15 from the same ranked list.
- Do not retrieve only 5 and then impute deeper ranks.

---

## 8. Gold definition

One relevant document per query: integer `source_doc_id` pointing at the corpus row that generated or was judged as the known item.

This is **known-item** gold, not a graded human qrel.

---

## 9. ExactSourceHit@5 calculation

For query i:

```
hit_i = 1 if rank(source_doc_id) <= 5 else 0
Hit@5 = mean(hit_i)
```

If the source is not in the retrieved 50, rank = 999 and hit = 0.

---

## 10. Secondary metrics

All use the same ranked list and the same single gold id.

- **P@5** = (1/5) if source in top-5 else 0; mean over queries.  
  (Known-item identity: P@5 = 0.2 × Hit@5.)
- **nDCG@5** = `1 / log2(rank + 1)` if rank ≤ 5 else 0; mean.
- **MRR** = `1 / rank` if rank < 999 else 0; mean.
- **Hit@10**, **Hit@15**: source in top-10 / top-15.

Human relevance labels (Phase 7) are **not** official metrics and must not be computed on H001–H040 unless a later protocol explicitly adds a sealed annotation pass.

---

## 11. Handling of ties

Use the existing scorer: accumulate BM25 scores, take `argpartition(-scores, k)`, then `argsort(-scores)` on that subset (`run_phase5.py`).

Do not add a secondary sort on `doc_id`. Freeze the NumPy behavior of that function. If two documents have identical scores, the order is whatever that code emits. Record the Python, NumPy, and pandas versions in the test run log.

---

## 12. Handling of duplicate documents

Each corpus row is a distinct `source_doc_id`. Near-duplicate wires are **not** collapsed. Retrieving a neighbour wire of the gold article is an official miss if the gold id is outside Top-5.

---

## 13. Handling of missing source_doc_id

If a held-out row has no usable `source_doc_id` (null, non-integer, or out of `[0, 111859]`):

- Do **not** guess a gold document.
- Exclude that query from official Hit@5.
- Report `n_scored` and `n_excluded` separately.

---

## 14. Handling of Roman queries

Detector `ROMAN` → Method D only: original query tokens on the romanized full-corpus BM25 index.

Do not apply `transliterate_roman` (dictionary) or Method C grapheme inverse on the official path.

---

## 15. Handling of Mixed queries

Detector `MIXED` → Urdu BM25 on the raw query (Urdu tokens + any Latin tokens).  
No romanized-index second path. No fusion. Phase 5 mixed union added **0** Hit@5 on n=9 mixed QTRN queries.

---

## 16. No tuning after test begins

Once any H001–H040 query text is read by the evaluation script:

- `k1`, `b`, tokenizer, romanizer, detector, routing, and top_k are locked.
- No extra documents, no extra dictionary keys, no query edits.

---

## 17. No test-set-driven modifications

Forbidden after unsealing:

- Choosing among systems using H001–H040 scores
- Thresholds, rerankers, fusion weights
- Dropping “hard” test queries
- Re-running with a “fix” for a failed test id

One official numbered table. If a bug in logging is found that does not change ranks, a clarifying note is allowed; changing ranks requires declaring the run invalid.

---

## 18. Reproducibility requirements

The test runner must log:

- Corpus SHA-256 (must match the manifest)
- `n_docs = 111860`
- Dictionary SHA-256 or key count 198
- `k1`, `b`, top_k
- Python / NumPy versions
- Per-query: `query_id`, detector label, predicted path, `source_doc_id`, rank, hit@5

Rebuild indexes with the same code paths as Phase 6 (`run_phase6.py` tokenize + `romanize_token` + `BM25`). Do not load a stale pickle from another machine without verifying corpus hash.

Seed: BM25 is deterministic given identical tokens; no RNG in the official path. Record `SEED = 42` as unused for retrieval (legacy from earlier phases).

---

## 19. What must be published with the test score

1. Official ExactSource Hit@5 (and secondary metrics) on H001–H040.
2. The n=78 development baseline (this freeze).
3. The known-item limitation (`PHASE7_EVALUATION_LIMITATIONS.md`).
4. Confirmation that no H001–H040 query was used for design.
