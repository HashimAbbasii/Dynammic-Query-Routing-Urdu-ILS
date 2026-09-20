# R2-1 — Controlled document-side fallback Roman representation

**Status:** COMPLETE  
**Decision:** `R2-1 NOT SUPPORTED — CLOSE FALLBACK REPRESENTATION DIRECTION`  
**Date:** 2026-09-11  
**Branch:** `research/ultra-v2-strengthening`  
**Commit:** `fd54ac9b65c2db93e7e16fbf0c5a40b6a6025be1`  
**Label:** ULTRA v2 development experiment. **Not a PLOS result.**  
**TEST:** NOT ACCESSED.

---

## 1. Status

R2-1 ran to completion on TRAIN/DEV Roman KN only.

| Gate | Result |
| --- | --- |
| Frozen-state / TEST seal | Pass |
| R2-B0 baseline reproduction | **PASS** (exact match to expected TRAIN+DEV metrics and per-query ranks) |
| Reverse-dictionary unchanged | Pass (0 mismatches) |
| Query side unchanged | Pass |
| BM25 k1/b, Top-50, Top-5 | Unchanged |
| Primary metric | **No improvement** |
| Candidate-generation recovered / regressed | **0 / 0** |

---

## 2. Research question

Does replacing **only** Method D’s document-side fallback romanizer (`naive_roman_word`) with a deterministic, principled Latin/Roman fallback increase gold-document **candidate inclusion** (Hit@50) for Roman KN queries, especially R2-C0 ROOM Category 1, without changing queries, routing, BM25, or the reverse dictionary?

---

## 3. Hypothesis

Pre-registered **before** treatment retrieval (printed by `run_r2_1_experiment.py` at start):

> **H1:** Replacing only the current document-side fallback romanization with a deterministic, principled Latin/Roman representation will increase gold-document candidate inclusion for Roman Urdu KN queries, especially ROOM Category 1 failures, without changing query representation, routing, BM25 parameters, dictionary behavior, or benchmark data.

**Primary falsification target:** ROOM Category 1 Hit@50. If this does not materially improve, close the fallback-representation direction rather than adding uncontrolled fixes.

This hypothesis was **not** rewritten after seeing results.

---

## 4. Frozen assumptions

| Item | Value |
| --- | --- |
| M0 module | `experiments/phase5_roman_urdu/run_phase5.py` — **not edited** |
| Dictionary | `models/roman_urdu_dict_expanded.json` SHA-256 `30c3f61a64ec641abbb3acdbc7a8bcaf197f0238f1bf9e76c2c7ce8e590f86a3` |
| Corpus | `data/clean_articles.csv` SHA-256 `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231` |
| BM25 | k1=1.5, b=0.75, `run_phase5.BM25` |
| Candidate depth | 50 |
| Official cutoff | 5 |
| Query representation | `tokenize(query)` as typed |
| Reverse dictionary | first JSON key via `setdefault` |
| Splits | TRAIN + DEV Roman KN only |
| R2-B0 / R2-C0 artifacts | read-only |
| TEST | sealed; not loaded |

---

## 5. Baseline reproduction

CONTROL retrieval used the frozen R2-B0 roman BM25 cache (read-only). Reproduced TRAIN+DEV metrics:

| Metric | Expected | Reproduced |
| --- | ---: | ---: |
| n | 51 | 51 |
| Hit@1 | 1 | 1 |
| Hit@5 | 4 | 4 |
| Hit@10 | 4 | 4 |
| Hit@50 | 6 | 6 |
| MRR | 0.0375 | 0.0375 |

Every per-query CONTROL rank matched `artifacts/r2_b0_per_query.csv`. **No discrepancy. Experiment proceeded.**

`run_r2_b0.py` was **not** re-executed, so R2-B0 output files were not rewritten.

---

## 6. Treatment design

| Factor | CONTROL | TREATMENT |
| --- | --- | --- |
| Document text | same corpus | same |
| Tokenizer | frozen `TOKEN_RE` | same |
| Reverse-dictionary first key | Method D | **identical** |
| Fallback (Urdu, not in reverse dict) | `naive_roman_word` / `_CHAR_ROMAN` | `hunterian_ascii_positional_v1` |
| Already-Latin tokens | lowercase | same |
| Query tokens | as typed | **same** |
| BM25 | k1=1.5, b=0.75, Top-50 | **same** |

The only manipulated factor is fallback output for non-dictionary Urdu tokens.

---

## 7. Romanizer design

**Name:** `hunterian_ascii_positional_v1`  
**File:** `experiments/ultra_v2/phase2_roman/fallback_roman_v1.py`  
**Version:** 1.0.0

Closed ASCII inventory matching Method D for consonants and non-و/ی matres. **Position-aware و and ی:**

| Letter | Token-initial | Non-initial |
| --- | --- | --- |
| و | `w` | `o` |
| ی / ئ | `y` | `i` |

No short-vowel insertion, no lexicon, no diacritics, no query IDs, one output string per input token.

---

## 8. Why this representation was selected

R2-C0 identified Method D’s unconditional `و → o` as a consonant-destroying table artifact (`ورلڈ → orld`). Urdu orthography treats و as **both** /w/ (typical initially) and /o~u/ (typical after a consonant). A positional Hunterian/ASCII rule is a published-style operationalization of that dual, corpus-wide, without benchmark words.

**uroman 1.3.1.1 was evaluated and not selected:**

- Established and deterministic, but maps **every** و → `w` (`دو → dw`, `ہو → hw`), which is worse for chat Roman vowels than Method D.
- Still does not insert unwritten short vowels (`سلمان → slman`).
- Adds a pinned third-party data dependency; the in-repo table is fully hashable.

Letter-name joining, n-grams, vowel lexicons, and query aliases were **not** added (they would be a different experiment).

---

## 9. Safety checks

- Romanizer source contains no `KN001`, `QTRN`, `K001`, `U001`, or hard-coded query strings.
- TEST paths raise `REFUSED`.
- Dictionary and corpus SHA assertions.
- k1==1.5, b==0.75, Top-50, Top-5 assertions.
- Reverse-dictionary outputs required to match Method D (0 mismatches on 10,115,123 dict tokens).
- Diagnostic sample: fixed linguistic list plus corpus docs **0, 250, 2500, 25000, 50000**, excluding KN gold IDs.

Pre-retrieval diagnostic: 64 token comparisons, **5 changed**, **0 empty** on that sample, deterministic repeats. Changed generic examples include `وقت oqt→wqt`, `وزیر ozir→wzir`, `یہ ih→yh`. `دو` stayed `do`.

---

## 10. Dataset used

| Split | Roman KN | Used |
| --- | ---: | --- |
| TRAIN | 33 | scored |
| DEV | 18 | scored |
| TRAIN+DEV | **51** | primary pool |
| TEST | — | **not accessed** |
| NL | — | not scored (no official qrels) |

ROOM Category 1 IDs (frozen from R2-C0 `cand_cat==1` and `primary==ROOM`, n=11):

KN001, KN006, KN008, KN010, KN011, KN018, KN037, KN045, KN047, KN050, KN051.

---

## 11. Exact evaluation protocol

ExactSource rank of `source_doc_id` in Top-50 BM25. Hit@k = rank ≤ k. MRR = 1/rank if retrieved else 0. Same queries, tokenizer, gold IDs as R2-B0.

---

## 12. Primary metric

**Hit@50 on R2-C0 ROOM Category 1 (n=11).**

| | Baseline | Treatment | Δ |
| --- | ---: | ---: | ---: |
| Hit@50 count | **0 / 11** | **0 / 11** | **0** |
| Hit@50 rate | 0.0% | 0.0% | 0.0 pp |
| Newly recovered | 0 | | |
| Regressions | 0 | | |

**The pre-registered test did not move.**

---

## 13. Secondary metrics

ExactSource, Roman KN only.

### TRAIN (n=33)

| | Control | Treatment |
| --- | ---: | ---: |
| Hit@1 | 1 (0.0303) | 1 (0.0303) |
| Hit@5 | 3 (0.0909) | **2 (0.0606)** |
| Hit@10 | 3 | 3 |
| Hit@50 | 4 | 4 |
| MRR | 0.0472 | 0.0445 |

### DEV (n=18)

| | Control | Treatment |
| --- | ---: | ---: |
| Hit@1 | 0 | 0 |
| Hit@5 | 1 | 1 |
| Hit@10 | 1 | 1 |
| Hit@50 | 2 | 2 |
| MRR | 0.0198 | 0.0198 |

### TRAIN+DEV (n=51)

| | Control | Treatment |
| --- | ---: | ---: |
| Hit@1 | 1 (0.0196) | 1 (0.0196) |
| Hit@5 | **4 (0.0784)** | **3 (0.0588)** |
| Hit@10 | 4 | 4 |
| Hit@50 | **6 (0.1176)** | **6 (0.1176)** |
| MRR | 0.0375 | 0.0358 |

Hit@50 is the candidate-generation metric: **unchanged**. Hit@5 declined because KN012 moved from rank 5 to rank 9 (still in Top-50).

---

## 14. Results (headline)

- **1.11 million** fallback tokens changed vs control (5.4% of 20.5M fallback tokens).
- Unique fallback types almost unchanged (345,883 vs 345,888): the intervention mostly rewrites initial `o…` to `w…`.
- Query–gold **exact overlap** increased on only **2 / 51** queries, both by the function token `ya` (یہ → `yh`/`ya` interaction with `یا`). No ROOM Category 1 query gained a content match.
- **0** golds entered Top-50; **0** left Top-50.

---

## 15. Per-query analysis

Full table: `experiments/ultra_v2/phase2_roman/R2_1_PER_QUERY.csv`.

| cand_change | n |
| --- | ---: |
| unchanged_miss | 45 |
| unchanged_rank | 5 |
| rank_regression | 1 (KN012, 5→9) |
| recovered | 0 |
| regressed (out of Top-50) | 0 |
| rank_improvement | 0 |

The only rank change among retrieved golds is KN012 (`dadi` success). Overlap stayed 2. The positional `ی` rule and competitor re-scoring moved a borderline Top-5 document to rank 9. That is **not** a candidate-generation recovery.

---

## 16. Category analysis

R2-C0 primaries were **not** relabeled.

| Category | n | Ctrl Hit@50 | Trt Hit@50 | Ctrl Hit@5 | Trt Hit@5 |
| --- | ---: | ---: | ---: | ---: | ---: |
| ROOM | 19 | 0 | 0 | 0 | 0 |
| ENT | 16 | 0 | 0 | 0 | 0 |
| VOCAB | 9 | 0 | 0 | 0 | 0 |
| NEIGH | 1 | 0 | 0 | 0 | 0 |
| RANK | 2 | 2 | 2 | 0 | 0 |
| SUCCESS | 4 | 4 | 4 | 4 | 3 |
| NORM / QAMB / TEMP | 0 | — | — | — | — |

ROOM Category 1 (11): all remain outside Top-50.  
ENT: no candidate-generation change.  
VOCAB: remain failures (as expected if they are paraphrase).

---

## 17. Negative controls

| ID | Category | Ctrl Hit@50 | Trt Hit@50 | Overlap Δ |
| --- | --- | ---: | ---: | ---: |
| KN017 | VOCAB | 0 | 0 | 0 |
| KN020 | VOCAB | 0 | 0 | 0 |
| KN041 | VOCAB | 0 | 0 | 0 |

They stayed failures. **Do not attribute any semantic rescue to R2-1** — there was none. This is consistent with R2-C0: `cpec` vs راہداری and `supersonic` vs تیز رفتار طیارہ are not fallback-table problems.

---

## 18. Regression analysis

| | n | IDs |
| --- | ---: | --- |
| Recovered into Top-50 | 0 | — |
| Lost from Top-50 | 0 | — |
| Net Hit@50 | 0 | — |
| Hit@5 loss with gold still in Top-50 | 1 | KN012 rank 5→9 |

No category other than SUCCESS Hit@5 was damaged. The KN012 movement is a ranking side-effect of a small index rewrite, not evidence that ROOM improved.

---

## 19. Statistical analysis

n=51 is small. No significance is manufactured.

| Comparison | Improved | Unchanged | Regressed | McNemar |
| --- | ---: | ---: | ---: | --- |
| Hit@50 all 51 | 0 | 51 | 0 | no discordant pairs, p=1.0 |
| Hit@50 ROOM Category 1 (n=11) | 0 | 11 | 0 | no discordant pairs, p=1.0 |

A zero-discordance result cannot support H1. It also cannot be spun as “trending positive.”

---

## 20. Failure analysis

### Why ROOM Category 1 stayed at 0/11

Post-hoc qualitative check of the **same mechanism**, not used to choose the romanizer:

| Urdu token | Control | Treatment | Typical query form | Exact BM25? |
| --- | --- | --- | --- | --- |
| ورلڈ | `orld` | `wrld` | `world` | **no** |
| سلمان | `slman` | `slman` | `salman` | **no** |
| جی + میل | `ji` `mil` | `ji` `mil` | `gmail` | **no** (token split) |
| زمبابوے | `zmbaboe` | `zmbaboe` | `zim` | **no** (و not initial; nickname) |
| سام + سنگ | `sam` `sng` | `sam` `sng` | `samsung` | **no** (token split) |

**Mechanism remaining after R2-1:**

1. **Unwritten short vowels.** Character-level romanization cannot emit `salman` from `سلمان` without a lexicon.
2. **English spelling ≠ letter transcription.** `wrld` is a better skeleton than `orld` but BM25 is exact-token. The query is `world`.
3. **Tokenizer boundaries.** `جی میل`, `سام سنگ`, `ایف بی آر` remain multiple tokens; queries are `gmail`, `samsung`, `fbr`.
4. **Acronym letter-names** (`aii pi ail` vs `ipl`) were never in scope of a per-token waw/ye rule.
5. **Paraphrase / nickname** (VOCAB; `jlo`; `zim`) unchanged, as required.

Remaining ROOM Category 1 IDs: all 11. None acquired a new **content** overlapping term.

### KN012 rank regression

Gold stayed in Top-50. Borderline success (rank 5) fell to 9. Overlap unchanged. Likely competitor re-weighting after 1.1M token rewrites elsewhere in the index. Not a ROOM recovery.

---

## 21. Limitations

- Exact BM25 cannot use skeleton similarity; R2-C0’s counterfactual overlap is **not** a retrieval result and was not used as a metric here.
- One romanizer only; uroman was evaluated offline and rejected, not A/B’d as a second official treatment.
- n=51 / ROOM Category 1 n=11: underpowered for anything except an all-or-nothing candidate-generation shift, which did not occur.
- 6,573 empty treatment fallback strings (vs 20.5M fallback tokens); not investigated as a recovery path.
- TRAIN/DEV only; no TEST generalization claim is licensed.

---

## 22. Decision

`R2-1 NOT SUPPORTED — CLOSE FALLBACK REPRESENTATION DIRECTION`

ROOM Category 1 Hit@50 did not improve (0/11 → 0/11). No gold entered Top-50. The 1.1M token edits did not create a lexical BM25 bridge to Roman/English query forms. Adding n-grams, fuzzy match, dictionary expansion, or query aliases **now** would unblind the experiment. Those are different hypotheses.

This does **not** say “Roman Urdu is solved,” “close all Roman research forever,” or “Method D is adequate.” It says: **replacing the fallback character table with a principled positional romanizer is not a sufficient candidate-generation fix** on this benchmark.

---

## 23. Reproducibility information

| Item | Value |
| --- | --- |
| Script | `experiments/ultra_v2/phase2_roman/run_r2_1_experiment.py` |
| Romanizer | `experiments/ultra_v2/phase2_roman/fallback_roman_v1.py` |
| Python | 3.13.9 |
| Tokenize wall time | 323.7 s |
| Determinism | closed table; no RNG |
| CONTROL | frozen R2-B0 `roman_bm25` cache |
| Second run | same table + same corpus SHA ⇒ same representation hash |

---

## 24. Git state

Recorded at experiment end (no commit, no push, no checkout, no reset):

- Branch: `research/ultra-v2-strengthening`
- Commit: `fd54ac9b65c2db93e7e16fbf0c5a40b6a6025be1`
- Working tree: existing `M .gitignore`; untracked `experiments/ultra_v2/` including new R2-1 files
- Frozen paths (M0, dictionary, PLOS, Phase 12, R2-B0, R2-C0): **no modifications**

---

## 25. Hashes

| Object | SHA-256 |
| --- | --- |
| Dictionary | `30c3f61a64ec641abbb3acdbc7a8bcaf197f0238f1bf9e76c2c7ce8e590f86a3` |
| Corpus | `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231` |
| `fallback_roman_v1.py` | `8ca3829435bf768cd1728d3cea0eadcb7fc9807b9f33b189dfdad64ed48369e7` |
| Treatment representation stream | `ee1166787b0f0028bcaae64594d46f56f88142060c324407be1dcca72e9e6c9d` |
| R2-B0 `r2_b0_per_query.csv` (unchanged) | prefix `cc0d31c2b4bb108e…` (full hash unchanged from R2-C0) |
| R2-C0 CSV (unchanged) | prefix `fa8101cc0459ee82…` |
| M0 `run_phase5.py` (unchanged) | prefix `7e529142809f4c00…` |
| TEST seal aggregate (metadata only) | `48610601209c3723a7252bb9a197d8fbbece18640e0bf7aef972884816ab46c4` |

Code hash of `run_r2_1_experiment.py` at run time is in `artifacts/r2_1_config.json`.

---

## TEST safety

**TEST NOT ACCESSED.**

TEST query CSVs were not loaded, printed, tokenized, or retrieved against. Seal.json was read only as previously recorded metadata (kind + aggregate). No TEST-derived artifact was created. No TEST source IDs were used.
