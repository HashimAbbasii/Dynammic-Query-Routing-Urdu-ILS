# Module 2 — Lexical retrieval representation ablation (R-dev)

**Status:** PRE-SPECIFIED BEFORE EXECUTION. Do not edit after seeing results.  
**Directory:** `experiments/post_phase12_development/module2/`  
**Date locked:** 2026-09-05

---

## 1. Research question

Module 1 (query-surface Roman normalization) was null on sealed R-dev (Δ = 0 for KI and NAT).

Module 2 asks:

> Does an independently pre-specified **lexical retrieval representation** change improve KI ExactSource Hit@5 on R-dev while avoiding material URDU/MIXED regression, without post-hoc tuning?

Primary target: **P2 — lexical mismatch on harder KI.**  
Secondary observation: **P1 — known-item identity among topical neighbours.**

R-dev is a **development / ablation** set. No generalization claim to a future unseen test.

---

## 2. Hypotheses

| ID | Hypothesis |
| --- | --- |
| H1 (M2-A) | Character-boundary 3-gram BM25 recovers partial lexical overlap that word BM25 misses. |
| H2 (M2-B) | Fixed RRF fusion of headline BM25 and body BM25 recovers title-local evidence lost in body-only scoring. |

Both are tested **independently**. No M2-A+M2-B. No M1 stacking.

---

## 3. Frozen inputs (read-only)

| File | Role |
| --- | --- |
| `experiments/post_phase12_development/queries_r_dev.csv` | 100 sealed queries (50 KI + 50 NAT) |
| `experiments/post_phase12_development/R_TOP50_RETRIEVAL.csv` | Frozen M0 Top-50 |
| `experiments/post_phase12_development/qrels_r_dev.csv` | Frozen NAT labels (M0 Top-5 pool) |
| `models/roman_urdu_dict_expanded.json` | Method D reverse dictionary (unchanged) |
| `experiments/phase5_roman_urdu/run_phase5.py` | M0 `detect_script`, `tokenize`, `romanize_token`, `BM25` (not modified) |
| `data/clean_articles.csv` | Corpus (`Index`, `Headline`, `News Text`, …) |

Expected SHA-256 (verified at run time):

| Artifact | SHA-256 |
| --- | --- |
| `queries_r_dev.csv` | `1603b37eeee41fa6270f4e13d185c8eebd4512d025cd5fc67e8a81de9407e75f` |
| `R_TOP50_RETRIEVAL.csv` | `927a14a25b6f1de2a5c28aabdc2d8cbc0d4336e0b2b437490691a7bff63a2aa2` |
| `qrels_r_dev.csv` | `506305b5401102a3659d21b69c7a937bcdcde78b21a1409a6a6132255ff37bcb` |
| `roman_urdu_dict_expanded.json` | `30c3f61a64ec641abbb3acdbc7a8bcaf197f0238f1bf9e76c2c7ce8e590f86a3` |
| `clean_articles.csv` | `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231` |

Frozen M0 baselines (must hold):

- KI ExactSource Hit@5 = **19/50 = 38.0%**
- NAT Success@5 = **12/50 = 24.0%** (R080 remains in denominator)

---

## 4. Routing (unchanged)

Use frozen M0 `detect_script(raw_query)`:

- `URDU` / `MIXED` / `OTHER` → Urdu lexical path  
- `ROMAN` → Method D romanized-document path  

No Module 1 transforms. Raw query after script detection only.

Method D **document-side** romanization = existing `romanize_token` + reverse dictionary; **unchanged**.

---

## 5. Candidate M2-A — Character 3-gram BM25

| Spec | Fixed value |
| --- | --- |
| Representation | `sklearn.feature_extraction.text.TfidfVectorizer(analyzer="char_wb", ngram_range=(3,3)).build_analyzer()` applied to the document/query **string**; resulting n-grams are tokens for BM25 |
| Scoring | `run_phase5.BM25` with **k1=1.5**, **b=0.75** |
| Urdu-path documents | `Headline + " " + News Text` (same combined field family as M0), then char_wb 3-grams |
| Roman-path documents | Word-tokenize → `romanize_token` each → join with spaces → char_wb 3-grams |
| Queries | Same analyzer on raw query (Urdu path) or on space-joined Method-D-romanized word tokens (Roman path) |
| Depth | Top-50 |
| Forbidden | n≠3; TF-IDF scoring as the ranker; embeddings; M1 stacking |

One retrieval pass only.

---

## 6. Candidate M2-B — Headline + body lexical hybrid (RRF)

| Spec | Fixed value |
| --- | --- |
| Headline field | `Headline` |
| Body field | `News Text` |
| Tokenization | M0 `tokenize` (word-level); Roman path uses `romanize_token` per word token |
| Channels | Independent BM25 indexes: headline-only and body-only (Urdu and Roman variants per routing) |
| BM25 | k1=1.5, b=0.75 |
| Per-channel depth | Top-50 each |
| Fusion | Reciprocal Rank Fusion: `score(d) = Σ 1/(k + rank_c(d))` over channels containing d |
| RRF k | **60** (fixed) |
| Tie-break | Higher RRF score first; if equal, lower `doc_id` |
| Empty fields | Corpus audit: 0 empty headlines, 0 empty bodies; if empty, that channel contributes no hits |
| Depth out | Top-50 after fusion |
| Forbidden | Learned weights; alternate k; embeddings; M1 stacking |

One retrieval pass only. Independent of M2-A.

---

## 7. Evaluation

| Track | Metric | Definition |
| --- | --- | --- |
| KI (primary) | ExactSource Hit@5 | Gold `source_doc_id` in Top-5 |
| NAT (secondary) | Success@5 | ≥1 frozen qrel label A or B in Top-5 |

Script strata: URDU / ROMAN / MIXED using **frozen M0 detector labels** from `R_TOP50_RETRIEVAL.csv`.

Report vs M0: overall, strata, Δ, improved / worsened / unchanged, ranking-list changed count.

### NAT pool limitation

`qrels_r_dev.csv` labels **M0 Top-5 documents only**. Newly retrieved documents outside that pool cannot receive NAT credit. No re-annotation.

---

## 8. Regression guardrails

Do not declare success from aggregate KI alone. Report URDU/MIXED KI and NAT explicitly. Material strata regression must be stated even if overall KI rises.

---

## 9. Leakage safeguards

- No use of K / U / H / Phase 2 for tuning  
- No future unseen test  
- No query edits from failures  
- No parameter change after results  

---

## 10. Forbidden post-hoc actions

Do not change after seeing results: n=3, BM25 k1/b, RRF k=60, tokenization, routing, preprocessing, field definitions, fusion formula. Do not invent M2-C/D. Do not combine M2-A+M2-B.

---

## 11. Stop conditions

Stop if frozen SHA mismatch, baseline KI/NAT mismatch, ambiguous headline/body schema, need to modify M0/Method D/dictionary/queries/qrels, or need new annotations / parameter tuning.

---

## 12. Artifacts

```text
module2/
  MODULE2_PROTOCOL.md
  candidates.py
  run_module2_ablation.py
  M2-A_TOP50_RETRIEVAL.csv
  M2-B_TOP50_RETRIEVAL.csv
  M2-A_MANIFEST.json
  M2-B_MANIFEST.json
  MODULE2_RESULTS.md
```

Scratch indexes may live under `module2/scratch/` (not scientific frozen artifacts).
