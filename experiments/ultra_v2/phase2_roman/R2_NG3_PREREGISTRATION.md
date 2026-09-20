# R2-NG3 Pre-registration

**Experiment ID:** R2-NG3  
**Date (pre-registration):** 2026-09-11  
**Branch:** `research/ultra-v2-strengthening`  
**Commit at pre-registration:** `fd54ac9b65c2db93e7e16fbf0c5a40b6a6025be1`  
**Status:** Pre-registered **before** treatment evaluation.  
**TEST:** not used.

This document is the locked design. Treatment metrics must not rewrite it.

---

## Hypothesis

**H1:** Replacing exact-token lexical matching with a fixed character 3-gram lexical representation over the **frozen Method D** document tokens will recover at least some previously missed ROOM Category 1 gold documents into the Top-50 candidate set, because character 3-grams can preserve partial lexical similarity when Roman query strings and Method D romanized document strings differ by transliteration, vowel omission, or token-form variation.

**H0:** Character 3-gram matching will not recover ROOM Category 1 gold documents into Top-50 beyond the frozen R2-B0 baseline (0/11).

This is a **candidate-generation** hypothesis (Hit@50), not a ranking hypothesis (Hit@5).

---

## Exact n

**n = 3.** No other n. No search over n.

---

## Character 3-gram construction

Operate **independently within each existing token** (policy A). Do **not** concatenate across token boundaries or whitespace.

Let `t` be a lowercase Method D or query token produced by the frozen tokenizer.

1. If `len(t) == 0`: emit nothing.  
2. If `len(t) < 3`: emit `{t}` as a single feature (short-token passthrough). Required so that existing exact matches on tokens such as `ke`, `50`, `10` are not deleted.  
3. If `len(t) >= 3`: emit overlapping character 3-grams  
   `{ t[i:i+3] for i in 0..len(t)-3 }`  
   in left-to-right order. Example: `world` → `wor`, `orl`, `rld`; `orld` → `orl`, `rld`.

Digits and ASCII letters already present in the token are kept. No extra alphabet filter. No padding.

Features from all tokens of a document (or query) are concatenated into one bag; term frequency is the count of each 3-gram/short feature.

---

## Query preprocessing

1. Frozen `tokenize` (`[\u0600-\u06FF]+|[A-Za-z0-9]+`, lowercased).  
2. No dictionary, no `kya`/`kiya` fold, no spelling correction, no rewriting.  
3. Apply the 3-gram construction above to each query token.

---

## Document preprocessing

1. Frozen corpus `data/clean_articles.csv`.  
2. Frozen Method D: `romanize_token` = reverse-dictionary first key else `naive_roman_word`.  
3. **Not** R2-1 `hunterian_ascii_positional_v1`.  
4. Apply the 3-gram construction to each Method D token.

---

## Candidate depth and official cutoff

- Candidate depth: **Top-50**  
- Official cutoff (secondary): **Top-5**  
Neither is tuned.

---

## Scoring rule

Use the same BM25 implementation as Method D (`run_phase5.BM25`):

- k1 = **1.5** (frozen)  
- b = **0.75** (frozen)  
- IDF: `log((N-n+0.5)/(n+0.5)+1)`  
- Documents are bags of 3-gram/short features instead of word tokens.  
- Query is a bag of 3-gram/short features.  
- Missing features contribute 0.  
- Rank by descending BM25 score; ties follow the implementation’s `argpartition` order (same as R2-B0).  
- Zero-score documents are excluded from the hit list (same as frozen `BM25.search`).

No extra weights, query boosts, document boosts, or interpolation.

---

## Primary population and endpoint

- Reporting population: Roman KN TRAIN+DEV, **n = 51**.  
- **Primary slice:** R2-C0 ROOM Category 1, **n = 11**, IDs frozen:  
  KN001, KN006, KN008, KN010, KN011, KN018, KN037, KN045, KN047, KN050, KN051.  
- **Primary endpoint:** ExactSource Hit@50 on that slice.  
  Baseline = **0/11**.

Do not change the ID list after seeing treatment ranks.

---

## Secondary endpoints

On all 51:

- ExactSource Hit@1, Hit@5, Hit@10, Hit@50, MRR  
- Recovered / regressed Top-50 counts  
- MISS vs RANK vs HIT transitions  
- Rank changes among golds that are in Top-50 under either condition  

3-gram overlap with the gold document is **diagnostic only**, not the primary metric.

All-51 results must be reported; they do not replace the primary slice.

---

## Negative controls

- VOCAB paraphrase: **KN017, KN020, KN041** — not expected to become Hit@50 if the IV is lexical 3-grams.  
- Split/acronym ROOM Cat1, **not claimed to be sufficient**: **KN006, KN047, KN051**.

Unexpected improvement on negative controls is reported, not deleted.

---

## Exclusion rules

No TEST. No NL scoring. No Urdu-KN mixing into the primary. No H/K/U/QTRN mining. No R2-1 romanizer.

---

## Stop criteria

If ROOM Category 1 Hit@50 remains **0/11**, conclude **R2-NG3 UNSUPPORTED — CLOSE REMAINING ROMAN LEXICAL MATCHING**. Do not then try n=4, fuzzy match, dictionary expansion, dense, hybrid, or rerank inside this experiment.

---

## Unchanged components

Script detector, query tokenizer, query text, dictionary file and first-key behavior, Method D romanizer, BM25 k1/b, Top-50, Top-5, gold IDs, splits, routing.

---

## Forbidden post-hoc modifications

Changing n; tuning BM25 or K; adding fuzzy/edit-distance; expanding the dictionary; query rewrite; entity lists; dense/hybrid/rerank; dropping hard queries; redefining ROOM Category 1; using TEST; reversing primary vs secondary endpoints after seeing numbers.
