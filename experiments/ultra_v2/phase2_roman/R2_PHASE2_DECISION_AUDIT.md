# R2 Phase-2 Decision Audit

**Status:** COMPLETE  
**Date:** 2026-09-11  
**Branch:** `research/ultra-v2-strengthening`  
**Commit:** `fd54ac9b65c2db93e7e16fbf0c5a40b6a6025be1`  
**TEST query text:** not accessed  
**Implementation of a new retriever in this task:** none

---

## 1. Audit Scope

This is an **evidence-based decision audit** after R2-B0, R2-C0, and R2-1. It does not implement, wire, tune, or evaluate a new retrieval method. It asks whether TRAIN/DEV evidence justifies **one** next controlled experiment, or whether the Roman lexical branch should close.

Authoritative inputs: existing R2 artifacts and frozen Method D source (read-only). Counts below were re-checked from CSVs, not re-run as new retrieval.

---

## 2. Repository and Freeze Verification

| Item | Value |
| --- | --- |
| Branch | `research/ultra-v2-strengthening` |
| Commit | `fd54ac9b65c2db93e7e16fbf0c5a40b6a6025be1` |
| Git status (audit start) | `M .gitignore`; untracked `experiments/ultra_v2/` |
| Frozen PLOS branch present | `publication/plos-one-final` (local and `origin`) |
| Also present | `main` |
| R2-B0 artifacts | present (`R2_B0.md`, failure analysis, `artifacts/r2_b0_*`) |
| R2-C0 artifacts | present (audit MD/CSV, `r2_c0_summary.json`, `run_r2_c0_audit.py`) |
| R2-1 artifacts | present (report, per-query CSV, `run_r2_1_experiment.py`, `fallback_roman_v1.py`, `r2_1_*`) |
| Phase-1 TRAIN/DEV KN | present |
| TEST seal | `experiments/ultra_v2/benchmark/test/seal.json` exists |
| Checkout / reset / commit | **not performed** |
| M0 / PLOS / Phase 12 / dictionary edited this audit | **no** |

`.gitignore` was already modified before this audit (pickle ignore). It was **not** changed here.

---

## 3. Dataset Safety

| Rule | Status |
| --- | --- |
| TEST query CSVs opened / printed / loaded / retrieved | **No** |
| TEST used for hypothesis choice | **No** |
| Seal metadata inspected | Yes: `kind=ultra_v2_test_seal`; aggregate `48610601209c3723a7252bb9a197d8fbbece18640e0bf7aef972884816ab46c4`; manifest lists `queries_kn.csv`, `queries_nl.csv` — **files not read** |
| `verify_test_seal.py` | **Not run** (it would hash TEST CSV bytes) |
| Evaluation pool | Roman KN TRAIN+DEV only (n=51) |
| Forbidden H/K/U/QTRN/Phase-12 result mining | **Not used** |

`run_r2_phase2_decision_audit.py` re-read R2 CSVs and seal **metadata** only; it refuses other TEST paths.

**TEST NOT ACCESSED.**

---

## 4. R2-B0 Evidence

Frozen Method D, Roman KN TRAIN+DEV, verified from `r2_b0_summary.json` and failure CSV.

| Metric | Value |
| --- | ---: |
| n | 51 |
| Hit@1 | 1/51 |
| Hit@5 | 4/51 (7.84%) |
| Hit@10 | 4/51 |
| Hit@50 | 6/51 (11.76%) |
| MRR | 0.0375 |

Hit@5 failures = 47: **MISS 45**, **RANK 2** (KN014 rank 44, KN048 rank 42).

Primary taxonomy (not reinterpreted): ROOM 19, ENT 16, VOCAB 9, NEIGH 1, RANK 2, NORM 0, TEMP 0, QAMB 0.

`sibling_any=8` is entirely `kya`↔`kiya` (function word). **NORM = 0.** Query-side sibling fold is not justified.

---

## 5. R2-C0 Evidence

The audit’s conclusions are **logically supported** by the measured TRAIN/DEV overlaps, with the caveats R2-C0 already stated (skeleton diagnostics are not retrieval scores; VOCAB is not romanization).

Supported:

- Gold articles are Urdu-script; query↔original-Latin overlap = 0; Method D is the Latin bridge.
- Gold-token mix: fallback **0.6649**, dictionary **0.3133**, already-Latin **0.0217**.
- Zero Method D **content** overlap: **28/51**. No content path into Top-50: **27/51**.
- Mean content overlap: failures **0.43**, Hit@5 successes **2.00**.
- English-hint tokens **190**, exact Method D matches **4**. The four successes had **zero** English-hint tokens.
- Attested table/split forms: `ورلڈ→orld` vs `world`; `سلمان→slman` vs `salman`; `جی میل→ji mil` vs `gmail`; `زمبابوے→zmbaboe` vs `zim`; `سام سنگ→sam sng` vs `samsung`.
- ROOM often had higher consonant-skeleton overlap than exact overlap; that is **diagnostic**, not a Hit@50.
- VOCAB includes genuine paraphrase (`cpec` vs راہداری; `supersonic` vs تیز رفتار طیارہ).
- Dictionary first-key `kya`/`kiya` is not the content-failure mechanism.

R2-C0 therefore justified **one** controlled document-side fallback experiment. It did **not** justify query normalization, dictionary expansion, or reranking.

ROOM Category 1 (frozen): n=11  
KN001, KN006, KN008, KN010, KN011, KN018, KN037, KN045, KN047, KN050, KN051.

---

## 6. R2-1 Evidence

Controlled IV: fallback `naive_roman_word` → `hunterian_ascii_positional_v1` (initial `و→w` / else `o`; initial `ی→y` / else `i`). Reverse dictionary, queries, BM25, Top-50 unchanged. Baseline reproduction **PASS**.

| Primary | Baseline | Treatment |
| --- | ---: | ---: |
| ROOM Category 1 Hit@50 | **0/11** | **0/11** |
| Recovered into Top-50 | | **0** |
| Lost from Top-50 | | **0** |

All-51: Hit@50 **6→6**; Hit@5 **4→3** (KN012 rank 5→9); MRR **0.0375→0.0358**. Negative controls KN017/KN020/KN041 unchanged.

Qualitative after the fact (not used to choose R2-1): `ورلڈ` became `wrld`, still not `world`. `سلمان` stayed `slman`. Splits stayed splits.

**Decision stands:** `R2-1 NOT SUPPORTED — CLOSE FALLBACK REPRESENTATION DIRECTION`.

This closes **positional/simple fallback-table replacement**. It does not prove that every possible lexical matching function is impossible.

---

## 7. Candidate-Generation vs Ranking Diagnosis

**The primary problem is candidate generation.**

45/51 golds are outside Top-50. Only 2 golds are in Top-50 and outside Top-5. A reranker that reorders the current Top-50 **cannot** recover the 45 MISS-side golds. Reranking is **not** justified as the next experiment.

R2-1 did not change that structure (still 6 in Top-50).

---

## 8. Failure-Mechanism Matrix

Full machine-readable table: `R2_PHASE2_DECISION_AUDIT.csv`.

| ID | Mechanism | Strength | Next experiment? |
| --- | --- | --- | --- |
| A | Simple transliteration-table mismatch | Strong that tables distort; **strong that swapping the table is insufficient** (R2-1) | Already tested; **rejected** |
| B | Multi-variant Roman representation | Weak as the next IV (orld+wrld still ≠ world) | Rejected (overlaps R2-1) |
| C | Query-side Roman normalization | Strong **against** (NORM=0) | Rejected |
| D | English vs Roman vs Urdu lexical mismatch | Strong mismatch; not a standalone detector experiment | Absorbed into matching-granularity test |
| E | Entity / name / acronym handling | Strong ENT=16 fail; a manual entity list would overfit | Rejected as standalone |
| F | Token splitting | Strong **examples**; count beyond examples **NOT ESTABLISHED** | Not selected; tokenizer stays frozen |
| G | Semantic paraphrase (VOCAB) | Strong for n=9; not the majority | Negative control, not the IV |
| H | Exact-token BM25 candidate generation | **Strong** (45 MISS; 27 no content path; R2-1 recovered 0) | **Selected** as R2-NG3 |
| I | Ranking after candidates exist | Strong that this is **not** the bottleneck (n=2) | Rerank rejected |

Approximate counts that **are** established: MISS=45, RANK=2, ROOM=19, ENT=16, VOCAB=9, ROOM Cat1=11, English-hint matches 4/190. Counts that are **not** established: exact n of ROOM rows that are “pure n-gram recoverable,” exact n of acronym-split rows as a closed set. Those are tagged `NOT ESTABLISHED` in the CSV rather than invented.

---

## 9. Evaluation of Candidate Next Directions

| Direction | Addresses | Support | Weakens | Isolated? | Verdict |
| --- | --- | --- | --- | --- | --- |
| Multi-representation fusion | A/B | Two Latin forms exist | R2-1 alternate still does not equal the query | Would stack failed IVs | Premature / rejected |
| Query-side normalization | C | 8 `kya` siblings | NORM=0; no content | Already audited | Rejected |
| **Character n-gram matching** | H, D, part of E | Exact identity failed; `world`/`orld` share `orl`,`rld`; `salman`/`slman` share `lma`,`man`; R2-C0 sub-token diagnostics | Split tokens (`gmail`/`ji mil`, `fbr`/`aif bi`) often still miss; false-positive risk; n must not be searched | **Yes:** freeze n=3, freeze Method D, freeze BM25 | **Selected** |
| Another romanizer / lexical map | A | — | R2-1 closed this | No | Rejected |
| Dense retrieval | G, maybe nicknames | VOCAB=9 is semantic | Majority failure is lexical ROOM+ENT; dense would confound attribution | Possible later, not this step | Premature as *next Roman* test |
| Hybrid lexical+dense | H+G | — | Two IVs | No | Rejected now |
| Reranking | I | 2 RANK cases | 45 not in the list | Isolated but unjustified | Rejected |
| Dictionary expansion | E/D | Dict covers only ~31% of gold tokens | Benchmark-specific entries; R2-C0: dict is not the MISS driver | High leakage risk | Rejected |
| Fuzzy / edit-distance retrieval | H | `near_any=45` exists | R2-B0 called much of that noise; threshold = tuning | Weaker isolation than fixed n=3 | Rejected vs n-gram |
| Query rewriting | C/G | — | Mixes lexical and semantic; not isolated | No | Rejected |

---

## 10. Rejected Directions

1. **Another fallback romanizer** — tested; Hit@50 unchanged.  
2. **Query `kya`/`kiya` fold** — NORM=0.  
3. **Dictionary expansion** — wrong layer; overfit risk.  
4. **Entity gazetteers / per-query maps** — forbidden-style tailoring.  
5. **Tokenizer rewrite** — second IV; F count not established.  
6. **Fuzzy matching with a threshold** — extra free parameter.  
7. **Query rewriting / expansion** — not isolated.  
8. **Reranking** — gold mostly absent from Top-50.  
9. **Dense or hybrid retrieval as the next Roman experiment** — would target VOCAB (negative-control class) and hide whether lexical matching granularity was ever tested.  
10. **BM25 k1/b or Top-K retune** — not a mechanism test.

---

## 11. Proposed Next Controlled Experiment

**Name:** R2-NG3 — Character 3-gram matching on **frozen Method D** tokens.

**Do not implement in this audit.**

### Why this and not “close the branch”

R2-1 falsified “a better one-to-one letter table will emit the query string.” The remaining **lexical** claim, supported by R2-C0 overlaps and by R2-1’s `wrld`≠`world` outcome, is that **exact token identity** is the wrong matching granularity. Character 3-grams are a single, pre-registerable matching-feature change. They are not a second romanizer.

They are **not** expected to fix paraphrase VOCAB or letter-named acronyms. That limitation is pre-declared, not an excuse after the fact.

### Why ROOM Category 1 is used — and why it is not the whole benchmark

ROOM Category 1 (n=11) is the **mechanistic** slice: no content path into Top-50 under Method D. It is the same primary R2-1 used, so the next test is comparable.

It is **not** a substitute for the 51-query Roman KN pool. Any write-up must report all-51 Hit@k. A gain on 3–4 English-loan tokens is **not** a benchmark-wide Roman success.

### Hypothesis

If exact token identity is the dominant remaining cause of ROOM/ENT candidate-generation failure, then representing frozen Method D tokens and the unchanged query tokens as **pre-registered character 3-grams**, scored with the same BM25 (k1=1.5, b=0.75) and Top-50, will increase ExactSource Hit@50 on R2-C0 ROOM Category 1, without changing the Method D romanizer, dictionary, tokenizer, routing, or golds.

### Target population

- **Reporting population:** all Roman KN TRAIN+DEV (n=51).  
- **Primary slice (frozen IDs):** the 11 ROOM Category 1 IDs listed in §5.  
IDs are taken from R2-C0, not chosen after a future treatment run.

### Primary endpoint

**ExactSource Hit@50 on those 11 ROOM Category 1 queries** (count and rate; absolute Δ).

### Secondary endpoints (not post-hoc success rules)

- Hit@1/5/10/50 and MRR on all 51  
- Recovered / regressed Top-50 lists  
- Hit@50 on ENT (n=16) as descriptive  
- Overlap of 3-gram features vs exact tokens (diagnostic, not a metric to optimize)

### Controls

- Baseline = frozen R2-B0 Method D exact-token BM25  
- Tokenizer unchanged  
- Method D `romanize_token` / `_CHAR_ROMAN` unchanged (**do not use R2-1 hunterian as the index**)  
- Dictionary unchanged  
- k1=1.5, b=0.75, Top-50, Top-5 cutoff unchanged  
- Queries and golds unchanged  
- Routing unchanged  
- **n=3 frozen**; do not search n∈{2,4,5}

### Negative controls

- VOCAB paraphrase: **KN017, KN020, KN041** — not expected to become hits if the IV is lexical 3-grams. If these move and ROOM Cat1 does not, attribution fails.  
- Split/acronym ROOM Cat1 where 3-grams are **not claimed to be sufficient** (from R2-C0 examples, declared now): **KN006** (`ipl` vs letter names), **KN047** (`fbr`), **KN051** (`gmail` vs `ji mil`). Improvement here is **not** required for support; treating them as the headline would be invalid.

### Exclusions

No R2-1 romanizer, no dictionary edit, no query aliases, no fuzzy threshold, no dense/hybrid/rerank, no TEST, no k1/b/K tune, no tokenizer change.

### Stop criteria

If ROOM Category 1 Hit@50 remains **0/11**, **R2-NG3 is unsupported**. Then **close remaining Roman lexical-matching work**. Do not “rescue” with n=4, fuzzy match, or embeddings in the same step.

If ROOM Cat1 Hit@50 rises but all-51 Hit@50 is driven only by negative-control VOCAB rows, **do not** call the lexical hypothesis supported.

---

## 12. Pre-registration

| Item | Value |
| --- | --- |
| Experiment id | R2-NG3 |
| IV | char 3-grams of frozen Method D tokens + query tokens; BM25 otherwise identical |
| Primary | Hit@50, ROOM Category 1, n=11 |
| Confirmatory reporting | all 51 Roman KN TRAIN+DEV |
| n search | forbidden |
| TEST | forbidden |
| Small-n stats | report absolute counts; McNemar only if discordant Hit@50 pairs exist; do not manufacture significance (R2-1 had 0 discordant pairs) |

---

## 13. Limitations

- n=51 / slice n=11: only large, pre-registered count changes are interpretable.  
- 3-grams can retrieve the right document for the wrong shared trigram; recovered cases need a mechanism check.  
- Token splits and paraphrase will remain; a supported R2-NG3 still would not “solve Roman Urdu.”  
- DEV is not a substitute for sealed TEST.  
- This audit does not re-estimate n-gram overlap on the corpus (that would begin the experiment).

---

## 14. Reproducibility Information

| Item | Value |
| --- | --- |
| Verification script | `experiments/ultra_v2/phase2_roman/run_r2_phase2_decision_audit.py` (read-only; TEST CSVs not loaded) |
| Counts re-checked | R2-B0 failure CSV; R2-C0 audit CSV; R2-1 per-query CSV |
| Python | 3.13.9 |
| This audit implements retrieval | **no** |

---

## 15. Final Decision

`NEXT EXPERIMENT JUSTIFIED — R2-NG3 CHARACTER 3-GRAM MATCHING`

One experiment only. **Not implemented here.**
