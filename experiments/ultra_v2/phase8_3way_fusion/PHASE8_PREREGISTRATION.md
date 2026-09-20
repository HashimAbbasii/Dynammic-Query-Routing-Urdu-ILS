# ULTRA v2 Phase 8 — 3-way RRF fusion (BM25 + Dense + NG3)

**Document type:** pre-registration / controlled design  
**Experiment ID:** PHASE8-3WAY-RRF  
**Directory:** `experiments/ultra_v2/phase8_3way_fusion/`  
**Branch:** `research/ultra-v2-strengthening`  
**Commit at design freeze:** `fd54ac9b65c2db93e7e16fbf0c5a40b6a6025be1`  
**Timestamp (UTC, written before 3-way evaluation):** `2026-09-13T07:05:00Z`

This file must not be silently rewritten after Phase-8 scores are observed.

Phase 2–7 artifacts stay frozen. No TEST. No k-search. No weighted fusion. No reranking.

---

## 1. Status

**DESIGN ONLY — NOT EXECUTED.**

Inspection (2026-09-13), before this experiment:

| Input | Path | SHA-256 vs Phase 6 |
| --- | --- | --- |
| Method-D BM25 per-query | `phase2_roman/artifacts/r2_b0_per_query.csv` | `cc0d31c2b4bb108ea7114811cafe1da68c1f1f4a88db8dd1d4700a5dd9429509` **MATCH** |
| Dense per-query | `phase3_dense/DENSE_PER_QUERY.csv` | `4875884cbaeecd025df343befc5bccc6c35fc01dda54cff45173b56efab9fdb1` **MATCH** |
| R2-NG3 per-query | `phase5_ng3/R2NG3_PER_QUERY.csv` | `0149bd52dc00d7ace5bb510e17b5789037766ea69886738368e6f546a21ab3e5` **MATCH** |

No `phase8_*` directory existed at inspection. 2-way Hybrid CSV (comparison only) SHA-256 `c5174379abc872c2e2e7584b7974a461c32c287270e37f961483d4ead959828a`.

---

## 2. Scientific question

Does a pre-registered Reciprocal Rank Fusion of **three** frozen Top-50 lists (Method-D BM25, dense e5-small, R2-NG3) improve ExactSource retrieval — especially **Hit@5** — over the frozen **2-way** Hybrid RRF (BM25+Dense only), as an actual ranking method rather than a diagnostic pool-membership count?

---

## 3. Hypothesis

**H1:** Unweighted RRF (k=60) of the three frozen Top-50 lists will improve Hit@5 and/or recover golds that 2-way Hybrid ranks poorly or misses (including KN035, KN040, KN050, which Phase 6 found only in the raw 3-way **union**), without destroying 2-way Hybrid successes.

**H0:** Adding NG3 as a third unweighted RRF input does not produce a scientifically useful ranking improvement over 2-way Hybrid (no Hit@5 gain that holds as a ranked list, and/or important regressions).

These hypotheses will not be changed after seeing scores.

Phase 6 showed the **raw union** Hit@5 vs 2-way Hybrid was significant (p=0.006348) while union Hit@50 was not (p=0.25). That is a pool statistic. This experiment asks whether **RRF re-ranking of the union** is a usable method.

---

## 4. Frozen fusion method (identical to Phase 4, one more input)

Cormack, Clarke, and Buettcher (SIGIR 2009), same constant as Phase 4:

\[
\mathrm{RRF}(d) = \sum_{s \in \{\mathrm{BM25},\,\mathrm{dense},\,\mathrm{NG3}\}} \frac{1}{k + \mathrm{rank}_s(d)}
\]

| Item | Value |
| --- | --- |
| \(k\) | **60** (Phase 4 frozen; not searched) |
| Rank | 1-based position in that system's Top-50 |
| Missing list | that term is **0** |
| Weights | none (unweighted 3-way) |
| Tie-break | higher RRF, then **smaller doc_id** (same as Phase 4) |
| Output depth | Top-50 of the fused union |
| Gold outside all three Top-50s | miss (rank 999; MRR 0) |

No CombSUM, no learned weights, no second k, no fourth list.

---

## 5. Inputs (frozen indexes / methods; Top-50 re-searched only to fuse)

Lists are not stored as full candidate files. They are **re-searched** from frozen components and **gated** to match the frozen per-query gold ranks. Document embeddings are **not** regenerated. Method D / NG3 representations are **not** redesigned.

| Component | Source | Gate |
| --- | --- | --- |
| Method-D BM25 Top-50 | `_index_cache.pkl` if meta matches | gold ranks = `r2_b0_per_query.csv` |
| Dense Top-50 | `dense_doc_embeddings.npy` + query encode | gold rank + rank-1 id = `DENSE_PER_QUERY.csv` |
| R2-NG3 Top-50 | n=3 char grams on Method-D tokens, BM25 k1=1.5 b=0.75 | gold ranks = `R2NG3_PER_QUERY.csv`; NG3 feature-stream SHA `1ab004bb26e9231827137020808ca008981648d62a834755af5779454d8c553d` |
| 2-way Hybrid (sanity) | same BM25+Dense lists, Phase-4 `fuse_rrf` k=60 | gold ranks = `HYBRID_PER_QUERY.csv` |

Mismatch → **BLOCKED**.

---

## 6. Corpus and queries

Same as Phases 3–7: corpus SHA-256 `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231`, n=111,860; dictionary SHA-256 `30c3f61a64ec641abbb3acdbc7a8bcaf197f0238f1bf9e76c2c7ce8e590f86a3`; Roman KN TRAIN+DEV **n=51**; no TEST.

ROOM Category 1 (n=11): KN001, KN006, KN008, KN010, KN011, KN018, KN037, KN045, KN047, KN050, KN051.

23 four-way misses (frozen Phase 6 list): KN002, KN005, KN006, KN008, KN010, KN018, KN020, KN021, KN022, KN024, KN025, KN026, KN027, KN028, KN032, KN036, KN037, KN041, KN042, KN044, KN047, KN051, KN054.

---

## 7. Metrics

Primary (n=51): Hit@1, Hit@5, Hit@10, Hit@50, MRR (0 if gold not in fused Top-50).

Secondary:

- vs frozen 2-way Hybrid: recovered / regressed at Hit@5 and Hit@50
- Exact McNemar vs 2-way Hybrid on Hit@5 and Hit@50, using `exact_mcnemar` copied verbatim from `phase2_roman/run_r2_1_experiment.py`
- ROOM Category 1 Hit@50 vs 0/11, 3/11, 3/11, 1/11 (BM25 / Dense / Hybrid / NG3)
- Recovery of the 23
- KN035, KN040, KN050 ranks (Phase 6 union-only golds)
- Overlap sizes among the three Top-50 lists (descriptive)

---

## 8. Decision labels (choose exactly one)

- `PHASE8 SUPPORTED` — 3-way RRF is a scientifically useful ranking improvement over 2-way Hybrid (clear Hit@5 and/or Hit@50 gain with acceptable regressions; McNemar and per-query recoveries agree it is not just a pool artifact).
- `PHASE8 PARTIALLY SUPPORTED` — some recoveries of union-only or NG3-unique golds, or a modest Hit@k move, but most of the 23 remain out, Hit@5 does not clearly beat 2-way Hybrid as a ranker, and/or important 2-way successes regress.
- `PHASE8 UNSUPPORTED` — no useful ranking improvement over 2-way Hybrid (including: union membership does not become a better ranked list).
- `BLOCKED` — corpus/query/rank gate fail, or TEST access.

No “≥80% = success” rule. No second k. No Phase 9 from this file.

---

## 9. Stop / leakage

- No TEST query files  
- No tuning k or weights  
- Do not modify Phase 2–7  
- Do not start reranking or Phase 9 from this file  
- Do not commit/push from this protocol  
