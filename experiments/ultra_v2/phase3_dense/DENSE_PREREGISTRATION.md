# DENSE-BASELINE — pre-registration

**Experiment ID:** DENSE-BASELINE  
**Directory:** `experiments/ultra_v2/phase3_dense/`  
**Branch:** `research/ultra-v2-strengthening`  
**Known commit at freeze:** `fd54ac9b65c2db93e7e16fbf0c5a40b6a6025be1`  
**Timestamp (UTC, written before treatment evaluation):** `2026-09-11T10:30:00Z`

This file is the frozen protocol. It must not be silently rewritten after KN scores are observed.

---

## 1. Hypothesis

### H1

A multilingual dense retriever will recover some relevant Urdu documents that frozen lexical Method-D BM25 fails to retrieve, because semantic similarity can bridge:

- Roman Urdu → Urdu
- English → Urdu
- paraphrase → Urdu
- alternate lexical forms → Urdu

### H0

Dense retrieval does not produce a meaningful improvement over the frozen lexical baseline on the authorized TRAIN/DEV evaluation.

These hypotheses will not be changed after seeing results.

---

## 2. Selected model (frozen)

| Field | Value |
| --- | --- |
| Hugging Face id | `intfloat/multilingual-e5-small` |
| Pinned revision | `8d923955b027282ba975c0a4c825486c9ca4c490` |
| Source | https://huggingface.co/intfloat/multilingual-e5-small |
| Paper | Wang et al., *Multilingual E5 Text Embeddings: A Technical Report*, arXiv:2402.05672 |
| Architecture | 12-layer Multilingual MiniLM (initialized from `microsoft/Multilingual-MiniLM-L12-H384`) |
| Embedding dimension | 384 |
| Max sequence length | 512 tokens (model default; not tuned) |
| Pooling | mean pooling (Sentence-Transformers / E5 default) |
| Normalization | L2-normalize embeddings; cosine = inner product |
| Query prefix | `query: ` |
| Document prefix | `passage: ` |
| License | MIT |
| Fine-tuning on ULTRA data | **none** (zero-shot) |

One model. One configuration. No leaderboard.

---

## 3. Model-selection rationale (a priori)

Chosen **before** any v2 KN/DEV dense score was computed, using external/general criteria only:

1. **Documented retrieval purpose.** Multilingual E5 is trained and published as a text-embedding retriever, not as a generic STS encoder. The model card requires `query:` / `passage:` prefixes for asymmetric retrieval.
2. **Multilingual + Urdu support.** The card lists 100 XLM-RoBERTa languages including `ur` (Urdu). Cross-script Roman/English queries against Urdu documents is therefore a zero-shot use of a multilingual retriever, which is exactly the scientific question.
3. **Already the thesis’s designated long-context dense encoder.** Phase 4B pre-registered `intfloat/multilingual-e5-small` for full-corpus dense indexing and **did not build that index** (CPU time gate). This experiment is the first full-corpus evaluation of that already-chosen encoder on the **fresh** TRAIN/DEV benchmark. It is not a post-hoc swap after seeing v2 numbers.
4. **Public weights, documented protocol, MIT license.** Reproducible without private checkpoints.
5. **Feasible on the authorized hardware.** This machine is CPU-only (no CUDA). The small (384-d) checkpoint is the size that can be indexed under the frozen protocol. `e5-base` / `e5-large` / BGE-M3 were **not** run and will not be run in this experiment.

This is not model shopping. No second encoder will be evaluated if the first score is low.

---

## 4. Corpus

- Path: `data/clean_articles.csv`
- Expected SHA-256: `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231`
- Size: 111,860 Urdu news articles (row index = `source_doc_id`, same convention as R2-B0 / Method D)
- Document text: original Urdu `combined_text` if present, else `Headline` + ` ` + `News Text`
- **Not used:** Method D romanization, R2-1 hunterian, character n-grams, headline-only substitution, chunking
- Gold documents remain in the index. The corpus is not filtered by qrels.
- Exact-duplicate document texts will be **reported**, not removed, unless the frozen corpus definition already deduplicated (it does not)

---

## 5. Query population

Authorized files only:

- `experiments/ultra_v2/benchmark/train/queries_kn.csv`
- `experiments/ultra_v2/benchmark/train/queries_nl.csv`
- `experiments/ultra_v2/benchmark/dev/queries_kn.csv`
- `experiments/ultra_v2/benchmark/dev/queries_nl.csv`

**Primary scored population:** Roman KN TRAIN+DEV, **n = 51** (TRAIN 33, DEV 18), ExactSource via `source_doc_id`.

**Secondary:** all authorized KN TRAIN+DEV by script (`URDU`, `ROMAN`, `MIXED`, `OTHER`), with sample counts. Tiny strata will not be given statistical claims.

**Not scored:** NL (no official qrels). NL files are opened only for ID firewall / counts.

**Forbidden:** `experiments/ultra_v2/benchmark/test/**` query content. Seal metadata may be inspected without reading query CSVs.

Script labels: CSV `script` metadata, cross-checked with frozen `detect_script` from `experiments/phase5_roman_urdu/run_phase5.py` (read-only import). Mismatch → STOP.

---

## 6. Exact preprocessing

Queries:

- used **exactly as written**
- no spelling correction, translation, romanization, rewriting, expansion, or dictionary lookup
- no case/script normalization beyond what the tokenizer applies internally to subwords

Documents:

- original Urdu article text as in §4
- empty text encoded as the prefixed empty string (not dropped)

Prefixes (frozen, documented by the model card):

- queries: `"query: " + query_text`
- documents: `"passage: " + document_text`

If Sentence-Transformers injects the same prefixes via `prompt_name`, they are applied **once** (no double prefix). The actual application method is recorded in `artifacts/dense_config.json` at run start, before evaluation.

Truncation: model default `max_seq_length = 512`. No chunk size, no overlap, no alternative window. This is the documented encoder limit, not a tuned hyperparameter.

---

## 7. Embedding procedure

- Zero-shot. No fine-tuning. No query–document pairs. `source_doc_id` is unused until after retrieval.
- Each corpus document embedded once.
- Each authorized KN TRAIN/DEV query embedded once (plus a second search pass for rank identity).
- Encoder: `sentence-transformers.SentenceTransformer`
- Device: CPU (CUDA unavailable on this machine)
- `encode_batch_size = 64` is a **throughput** setting only; it is not a retrieval hyperparameter
- Embeddings stored as float32, L2-normalized
- Index implementation: exact dense matrix (NumPy memmap / ndarray). **Not** FAISS HNSW / IVF (those are approximate)

---

## 8. Similarity

Cosine similarity via inner product of L2-normalized vectors.

Tie-break: higher score first; if scores are equal, **smaller document id** wins.

No score threshold. No candidate threshold.

---

## 9. Top-K

Evaluation cutoffs frozen to match R2:

- Hit@1, Hit@5, Hit@10, Hit@50
- MRR with reciprocal rank 0 if gold rank > 50 (same convention as R2-B0: misses outside the candidate list do not contribute)

Retrieval depth for the returned list: 50. True gold rank may still be computed from the full score vector so candidate-generation (rank > 50) vs ranking (5 < rank ≤ 50) is well-defined.

---

## 10. Primary endpoint

Roman KN TRAIN+DEV, n=51:

- ExactSource Hit@1, Hit@5, Hit@10, Hit@50, MRR

Compared to frozen Method-D BM25 (R2-B0), which must remain:

| Method | n | Hit@1 | Hit@5 | Hit@10 | Hit@50 | MRR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Frozen Method-D BM25 | 51 | 1 | 4 | 4 | 6 | 0.0375 |

Those baseline cells will not be edited.

---

## 11. Secondary endpoints

- KN TRAIN/DEV by script (counts + ExactSource Hit@k / MRR)
- Per-query comparison vs R2-B0 (rank, Hit@k, gold cosine, recovered MISS, lost HIT)
- Transition matrices at Top-5 and Top-50
- Frozen R2-B0 failure taxonomy: ROOM, ENT, VOCAB, NEIGH, RANK, NORM, TEMP (NORM/TEMP historically 0)
- ROOM Category 1 diagnostic slice (n=11, **not a new test**): KN001, KN006, KN008, KN010, KN011, KN018, KN037, KN045, KN047, KN050, KN051 → Dense ExactSource Hit@50 = X/11
- VOCAB negative controls: KN017, KN020, KN041 (do not claim these as Romanization recovery)
- Candidate-generation vs ranking (Top-50 MISS vs in-50 / out-5)
- Exact McNemar on paired Hit@5 and Hit@50 vs R2-B0 (descriptive; n=51 is small; not the decision rule)
- Duplicate-document census (exact text hash)

---

## 12. Frozen comparison baseline

R2-B0 Method D BM25:

- `experiments/ultra_v2/phase2_roman/artifacts/r2_b0_per_query.csv`
- `experiments/ultra_v2/phase2_roman/artifacts/r2_b0_summary.json`
- Taxonomy: `experiments/ultra_v2/phase2_roman/R2_B0_FAILURE_ANALYSIS.csv`

The runner may independently re-read those artifacts (and, if present, the gitignored Method D index cache) to confirm 1/4/4/6 / MRR 0.0375. It must **not** rewrite them.

---

## 13. Exclusion rules

- No TEST query content
- No NL ExactSource scoring
- No QTRN / H / K / U / Phase-12 historical IDs
- No hybrid / RRF / fusion / candidate union
- No reranker / cross-encoder / LLM judge
- No second embedding model
- No fine-tuning
- No query rewriting
- No Method D / n-gram / hunterian document representation
- No gold injection / qrel filtering of the corpus

---

## 14. No-TEST rule

Code must refuse any path under `experiments/ultra_v2/benchmark/test/`.  
If query text from TEST is loaded, the run STOPS and reports `BLOCKED — DATA SAFETY FAILURE`.

---

## 15. No-tuning rule

Do not tune embedding dimension, pooling, normalization, similarity threshold, Top-K, chunk size, prefixes, or score cutoffs after seeing DEV/TRAIN metrics.  
Do not switch models after seeing scores.

---

## 16. Expected limitations (recorded before results)

- Urdu is lower-resource than English in E5’s mixture; the card warns of degradation on low-resource languages.
- Roman Urdu is not a separate labeled language: Latin-script code-mixed queries vs Urdu passages are zero-shot cross-script.
- 512-token truncation discards article tails.
- n=51 is small; percentages are unstable.
- Semantic neighbors may surface related news without recovering the exact `source_doc_id` (NEIGH / VOCAB risk).
- CPU-only indexing is slow; embeddings are cached, but the scientific object is still one frozen encoder.

---

## 17. Timestamp

Written: **2026-09-11T10:30:00Z** (before treatment evaluation).

---

## 18. Code / config hash

Recorded at run start in `artifacts/dense_config.json` (`preregistration_sha256`, `dense_retrieval_py_sha256`, `run_dense_baseline_py_sha256`, model revision, corpus SHA-256).  
If the pinned HF revision cannot be loaded, STOP (`BLOCKED`) rather than silently using another checkpoint.

Pre-run file hashes (computed after the protocol and scripts were written, **before** treatment evaluation):

- `dense_retrieval.py` SHA-256: `bd25cf497cbf004f8e09744329bf5aa82f780a5aeaba681591802f9ae7ff238b`
- `run_dense_baseline.py` SHA-256: `47ddf7dcf0794afc19d0da3900f8fe005282e295e12d69cbf53783e848a1aed9`

The preregistration document’s own SHA-256 is captured at run start (after this note) so that later silent edits would be detectable.

---

## Decision rule (pre-registered)

Choose exactly one after evidence is in:

- `DENSE BASELINE SUPPORTED` — meaningful, scientifically useful improvement on the authorized evaluation (recovery of misses, not merely a higher aggregate)
- `DENSE BASELINE PARTIALLY SUPPORTED` — some important recoveries, but substantial limitations or regressions
- `DENSE BASELINE UNSUPPORTED` — no meaningful improvement
- `BLOCKED` — invalid run (data safety, reproducibility, or implementation failure)

No arbitrary “above 50% = supported” threshold. Interpret absolute counts, ROOM Cat1, recoveries vs regressions, candidate-generation vs ranking, and reproducibility.
