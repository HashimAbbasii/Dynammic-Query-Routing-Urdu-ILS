# ULTRA v2 Phase 5 — R2-NG3 reproduction + dual-miss comparison

**Document type:** pre-registration / controlled design  
**Experiment ID:** R2-NG3-P5-REPRO  
**Directory:** `experiments/ultra_v2/phase5_ng3/`  
**Branch:** `research/ultra-v2-strengthening`  
**Commit at design freeze:** `fd54ac9b65c2db93e7e16fbf0c5a40b6a6025be1`  
**Timestamp (UTC, written before this reproduction’s official comparison tables):** `2026-09-12T13:40:00Z`

This file must not be silently rewritten after Phase-5 scores or comparison tables are observed.

Phase 2 already completed R2-NG3 (decision `R2-NG3 PARTIALLY SUPPORTED`, 2026-09-11). **That record stays frozen.** Phase 5 does not change n, does not try raw-Urdu grams, does not try TF-IDF, and does not rewrite Phase-2/3/4 artifacts.

---

## 1. Status

**DESIGN ONLY — NOT EXECUTED.**

Option B (user-confirmed): reproduce the **same frozen R2-NG3 method** once under this directory, **gate** per-query gold ranks against `experiments/ultra_v2/phase2_roman/R2_NG3_PER_QUERY.csv`, then — only if the gate passes — compute the **new** overlap/recovery comparison vs Method-D BM25, Phase-3 dense, the 25 BM25∩Dense dual misses, and ROOM Category 1.

---

## 2. Scientific question

Can the **already frozen** character 3-gram lexical retriever (R2-NG3) recover Roman-KN ExactSource gold documents that **both** word-level Method-D BM25 **and** dense e5-small miss?

This is a **candidate-generation** comparison. It is not fusion, not reranking, and not a new embedding model.

Phase 2 asked whether 3-grams recover ROOM Category 1 vs Method D. Phase 5 asks whether those same lists recover the **dual-miss** set that only became defined after Phase 3/4.

---

## 3. Hypothesis

**H1:** Frozen R2-NG3 Top-50 lists contain at least some gold documents from the BM25∩Dense dual-miss set, showing a lexical n-gram signal that neither exact-token BM25 nor dense e5-small generated.

**H0:** R2-NG3 does not recover dual-miss golds into Top-50 (0 recoveries), or any apparent unique hits are not a scientifically useful candidate-generation gain after regressions and ROOM Category 1 are considered.

These hypotheses will not be changed after seeing Phase-5 tables.

---

## 4. Frozen method (identical to Phase 2 R2-NG3)

| Item | Frozen value |
| --- | --- |
| n | **3** only |
| Token boundary | Policy A: 3-grams **inside each existing token**; no cross-token concat |
| Short tokens | `len(t) < 3` → keep `{t}` |
| Document text | Frozen Method D: `romanize_token` (reverse-dict first key else character table), **then** char-3-grams |
| Query text | Frozen `tokenize` as typed, **then** char-3-grams; no dictionary |
| Scorer | `run_phase5.BM25`, k1=**1.5**, b=**0.75** |
| Depth | Top-50 |
| Encoder / TF-IDF / raw-Urdu grams / Hunterian R2-1 | **forbidden** |

Helper (read-only import): `experiments/ultra_v2/phase2_roman/ng3_matching.py`  
BM25 implementation (read-only import): `experiments/phase5_roman_urdu/run_phase5.py`

Toy check (not a result): `world` → `wor, orl, rld`; `orld` → `orl, rld`; `ke` → `ke`.

---

## 5. Corpus and queries

| Item | Value |
| --- | --- |
| Corpus | `data/clean_articles.csv` |
| Corpus SHA-256 | `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231` |
| n_docs | 111,860 |
| Dictionary SHA-256 | `30c3f61a64ec641abbb3acdbc7a8bcaf197f0238f1bf9e76c2c7ce8e590f86a3` |
| Queries | `benchmark/train/queries_kn.csv`, `benchmark/dev/queries_kn.csv` |
| Population | Roman KN TRAIN+DEV, **n=51**, unmodified |
| Gold | `source_doc_id` (ExactSource) |
| Forbidden | `benchmark/test/**` query CSVs |

Query IDs and gold IDs must match Phase 3 `DENSE_PER_QUERY.csv` and Phase 4 `HYBRID_PER_QUERY.csv`. Mismatch → **BLOCKED**.

---

## 6. Mandatory reproduction gate

Before any official Phase-5 comparison table:

1. Confirm corpus SHA-256 and the n=51 Roman KN list (IDs + `source_doc_id`) match Phase 3/4.
2. Reproduce Method-D Top-50 gold ranks; they must match `r2_b0_per_query.csv` (same empty-rank = 999 convention).
3. Reproduce R2-NG3 Top-50 gold ranks for all 51 queries.
4. Compare **per query** to frozen `phase2_roman/R2_NG3_PER_QUERY.csv` (`ng3_rank`, `ng3_hit@1/5/10/50` as stored: empty rank = miss).

**If any gold rank / hit flag disagrees: STOP. Decision = `BLOCKED`. Do not write official overlap/recovery results. Do not “fix” the method.**

Optional representation check (same stop rule if it fails): Method D token-stream SHA-256 `323a07b46e2377b5ec807006c2efd06f9b1ae19a65f1389d22f32b435ca0c3fb` and NG3 feature-stream SHA-256 `1ab004bb26e9231827137020808ca008981648d62a834755af5779454d8c553d`.

Do not overwrite the frozen Phase-2 CSV.

---

## 7. Official comparison (only if the gate passes)

Read frozen files; do **not** re-run Phase 3 dense encoding or Phase 4 RRF:

- `phase2_roman/artifacts/r2_b0_per_query.csv`
- `phase3_dense/DENSE_PER_QUERY.csv`
- `phase4_hybrid/HYBRID_PER_QUERY.csv`

**Dual-miss set:** queries with Method-D Hit@50 = 0 **and** dense Hit@50 = 0, from those CSVs. This set must have size **25** and must equal Phase-4 `E_both_miss==1`. If not: **BLOCKED**.

Primary metrics (NG3, n=51): Hit@1, Hit@5, Hit@10, Hit@50, MRR  
(MRR = 0 if gold not in Top-50; same convention as R2-B0 / Phase 3.)

Required comparison tables:

1. NG3 vs BM25 vs Dense vs Hybrid on Hit@1/5/10/50/MRR (Hybrid from frozen Phase 4 only).
2. Query-level Hit@50 overlap: NG3 ∩ BM25, NG3 ∩ Dense, NG3-only, BM25-only, dense-only.
3. Recovery count of the 25 dual-miss queries (NG3 Hit@50).
4. ROOM Category 1 (frozen n=11): KN001, KN006, KN008, KN010, KN011, KN018, KN037, KN045, KN047, KN050, KN051  
   Compare to frozen BM25=0/11, Dense=3/11, Hybrid=3/11.
5. Live BM25∩NG3 **candidate-list** overlap (|Top-50 ∩ Top-50| per query) is allowed because Method D is searched as part of this reproduction. Dense candidate IDs are **not** re-searched.

---

## 8. Decision labels (choose exactly one)

Defined for **this** Phase-5 question (dual-miss candidate generation). They do not rewrite the Phase-2 label.

- `R2-NG3 SUPPORTED` — dual-miss recovery is large enough to show n-grams solve a substantial share of the 25, without merely rearranging already-retrieved lexical hits, and ROOM Category 1 is not still almost entirely ungenerated.
- `R2-NG3 PARTIALLY SUPPORTED` — at least one dual-miss gold enters NG3 Top-50, and/or NG3 shows unique Hit@50 evidence vs BM25 and dense, but most of the 25 remain misses and/or ROOM Category 1 stays largely unsolved and/or there are important regressions vs Method D.
- `R2-NG3 UNSUPPORTED` — zero dual-miss recoveries, or NG3 adds no scientifically useful candidate-generation beyond BM25∪Dense.
- `BLOCKED` — corpus/query mismatch, dual-miss set mismatch, or NG3 rank reproduction failure.

No “≥80% = success” rule. No second n. No fusion. No reranker in this phase.

---

## 9. Leakage / freeze

- No TEST query files
- No gold used to build queries or n-grams
- No tuning of n, k1, b, or depth
- No Phase-3 embedding regeneration
- No Phase-4 RRF rewrite
- Phase-2 `R2_NG3_*` files are read-only

**Blinding note:** Phase-2 NG3 ranks existed before this preregistration. Design work inspected that those ranks recover some dual-miss IDs. The **method** was frozen on 2026-09-11, before dense/hybrid. Official Phase-5 numbers are the gated reproduction, not a new matcher fitted to the 25.

---

## 10. Expected outputs

All new files under `experiments/ultra_v2/phase5_ng3/` only:

- `R2NG3_PREREGISTRATION.md` (this file)
- `run_r2ng3_p5.py`
- `R2NG3_PER_QUERY.csv`
- `R2NG3_CONTROLLED_EXPERIMENT.md`
- `artifacts/r2ng3_config.json`
- `artifacts/r2ng3_summary.json`
- `artifacts/r2ng3_representation_stats.json` if the index is actually rebuilt
