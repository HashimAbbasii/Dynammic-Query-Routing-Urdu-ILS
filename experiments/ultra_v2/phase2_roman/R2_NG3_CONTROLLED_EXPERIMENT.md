# R2-NG3 Controlled Character 3-Gram Experiment

**Status:** COMPLETE  
**Decision:** `R2-NG3 PARTIALLY SUPPORTED`  
**Date:** 2026-09-11  
**Branch:** `research/ultra-v2-strengthening`  
**Commit:** `fd54ac9b65c2db93e7e16fbf0c5a40b6a6025be1`  
**n:** 3 (only)  
**TEST:** NOT ACCESSED  
**Hunterian / R2-1 romanizer:** not used

Pre-registration was written **before** treatment evaluation: `R2_NG3_PREREGISTRATION.md`.

---

## 1. Executive Summary

Frozen Method D exact-token BM25 was reproduced on Roman KN TRAIN+DEV (n=51). Character 3-grams were then built **inside each existing Method D token** (and each query token) and scored with the same BM25 (k1=1.5, b=0.75, Top-50).

**Primary (ROOM Category 1 Hit@50, n=11): 0/11 → 1/11.** Recovered: **KN050** (rank 1). Ten ROOM Category 1 golds remain outside Top-50.

**All 51:** Hit@50 **6 → 8**; Hit@5 **4 → 6**; Hit@1 **1 → 3**; MRR **0.0375 → 0.075**. Golds outside Top-50: **45 → 43**. Recovered 4 (KN017, KN035, KN039, KN050). Regressed 2 (**KN012** Hit@5 success became MISS; **KN014** RANK became MISS).

McNemar on Hit@50: 4 vs 2 discordant pairs, two-sided p=0.6875. Do not claim significance.

Negative-control **KN017** (VOCAB) unexpectedly entered Top-5. That is reported, not deleted, and is **not** evidence that 3-grams solve paraphrase.

---

## 2. Research Question

Can fixed character 3-gram matching over **frozen Method D** tokens recover ROOM Category 1 golds into Top-50 when exact-token BM25 cannot?

---

## 3. Pre-Registered Hypothesis

**H1:** 3-grams over frozen Method D tokens recover at least some ROOM Category 1 golds into Top-50 via partial lexical similarity.

**H0:** ROOM Category 1 Hit@50 stays 0/11.

Candidate generation, not ranking, is the primary frame.

---

## 4. Experimental Scope

One IV: exact tokens → overlapping character 3-grams (n=3), token-internal. No other n, no fuzzy match, no R2-1 romanizer, no dictionary edit, no BM25/Top-K tune, no TEST.

---

## 5. Repository / Freeze Verification

| Item | Value |
| --- | --- |
| Branch / commit | `research/ultra-v2-strengthening` / `fd54ac9b65c2db93e7e16fbf0c5a40b6a6025be1` |
| Git | `M .gitignore`; untracked `experiments/ultra_v2/` |
| M0 | `run_phase5.py` imported, not edited |
| Dictionary SHA-256 | `30c3f61a64ec641abbb3acdbc7a8bcaf197f0238f1bf9e76c2c7ce8e590f86a3` |
| Corpus SHA-256 | `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231` |
| Method D token stream SHA-256 | `323a07b46e2377b5ec807006c2efd06f9b1ae19a65f1389d22f32b435ca0c3fb` |
| R2-1 hunterian used | **false** |

---

## 6. Dataset Safety

TRAIN/DEV Roman KN only (n=51). TEST query CSVs not opened. Seal metadata only: `ultra_v2_test_seal` / `48610601209c3723a7252bb9a197d8fbbece18640e0bf7aef972884816ab46c4`.

**TEST NOT ACCESSED.**

---

## 7. Frozen Baseline Reproduction

CONTROL = R2-B0 cached Method D exact-token BM25. Per-query ranks matched `r2_b0_per_query.csv`. Success ranks: KN004=1, KN012=5, KN023=3, KN038=3. RANK: KN014=44, KN048=42.

TRAIN+DEV: Hit@1=1, Hit@5=4, Hit@10=4, Hit@50=6, MRR=0.0375. **PASS.** Treatment then proceeded.

---

## 8. R2-NG3 Method

1. Tokenize documents with the frozen tokenizer.  
2. Romanize with frozen `romanize_token` (reverse-dict first key else `_CHAR_ROMAN`).  
3. Expand each Method D token to character 3-grams (short tokens kept).  
4. Build `run_phase5.BM25` on those feature bags, k1=1.5, b=0.75.  
5. Expand query tokens the same way (no dictionary).  
6. Retrieve Top-50.

---

## 9. Exact Character 3-Gram Definition

Policy **A**: within each existing token; no cross-token concatenation.

- `len(t) < 3` → feature `{t}`  
- `len(t) ≥ 3` → `t[i:i+3]` for `i = 0 … len(t)-3`

Toy check (not an experimental result): `world` → `wor orl rld`; `orld` → `orl rld`.

---

## 10. Query Representation

Frozen `tokenize` as typed. Then token-internal 3-grams. No `kya` fold, no rewrite.

---

## 11. Document Representation

Frozen Method D only. Confirmed by: no import of `fallback_roman_v1`; config `r2_1_hunterian_used=false`; dictionary SHA frozen.

---

## 12. Scoring / Ranking Procedure

Same BM25 equation as Method D (`run_phase5.BM25.search`), with 3-gram/short features as terms. IDF `log((N-n+0.5)/(n+0.5)+1)`. Missing terms skip. Zero scores dropped. Search repeated on all 51 queries: **identical ranks**.

---

## 13. Primary Endpoint

ExactSource Hit@50 on frozen ROOM Category 1 (n=11). Baseline **0/11**.

| | n | Hit@50 |
| --- | ---: | ---: |
| Baseline | 11 | **0** |
| NG3 | 11 | **1** |
| Absolute Δ | | **+1** |
| Recovered | | **KN050** (rank 1) |
| Regressed (this slice) | | **0** |
| Unchanged misses | | **10** |

---

## 14. Secondary Endpoints

Roman KN TRAIN+DEV n=51.

| Metric | Baseline | NG3 |
| --- | ---: | ---: |
| Hit@1 | 1 (0.0196) | 3 (0.0588) |
| Hit@5 | 4 (0.0784) | 6 (0.1176) |
| Hit@10 | 4 | 6 |
| Hit@50 | **6 (0.1176)** | **8 (0.1569)** |
| MRR | 0.0375 | 0.075 |

TRAIN Hit@50 4→4; DEV Hit@50 2→4. TRAIN Hit@5 3→4; DEV Hit@5 1→2.

---

## 15. Negative Controls

See §22.

---

## 16. Overall Results

Transitions (n=51):

| Baseline → NG3 | Count |
| --- | ---: |
| MISS → MISS | 41 |
| MISS → HIT | 3 (KN017, KN035, KN050) |
| MISS → RANK | 1 (KN039 rank 17) |
| HIT → HIT | 3 (KN004, KN023, KN038) |
| HIT → MISS | 1 (**KN012**) |
| RANK → RANK | 1 (KN048 42→31) |
| RANK → MISS | 1 (**KN014**) |

Net Hit@50 = +2. Not a clean slice-only win.

---

## 17. ROOM Category 1 Results

| ID | Base | NG3 | In50 | Shared 3-grams (sample) | Note |
| --- | --- | --- | --- | --- | --- |
| KN001 | — | — | no | `orl rld` plus `mal mpi` | `world`/`orld` grams present; still MISS (competitors) |
| KN006 | — | — | no | `kol olk` function grams | Split `ipl`; pre-declared not sufficient |
| KN008 | — | — | no | `itl nis jee` | `title`/`taitl` partial; still MISS |
| KN010 | — | — | no | `ami nam` | `benami` split; FBR letters |
| KN011 | — | — | no | `dro sol fra` | loanword fragments; still MISS |
| KN018 | — | — | no | `add din lad` | `aladdin`/`alh din` split |
| KN037 | — | — | no | `oto` | `photo`/`foto`; still MISS |
| KN045 | — | — | no | function/`ais` | messenger/facebook split |
| KN047 | — | — | no | `ndh aur` | `fbr` vs letter names; pre-declared |
| **KN050** | — | **1** | **yes** | `orl rld afg fgh … tan` | `world`/`orld` **and** `afghanistan` |
| KN051 | — | — | no | `jai ke` | `gmail` vs `ji mil`; pre-declared |

**10/11 still miss** even when diagnostic 3-gram overlap is non-zero. Overlap is **not** sufficient for Top-50 when grams are common (`orl`, `hai`, `ke`).

---

## 18. Per-Query Recovery Analysis

**KN050 (ROOM Cat1, recovered rank 1).** Query contains `world` and `afghanistan`. Method D gold has `orld` (`orl`,`rld`) and `afghanstan` (`afg`…`tan`). This is the pre-registered partial-bridge mechanism, plus a distinctive name. KN001 shares `orl`/`rld` but not a rare name prefix and did not enter Top-50.

**KN035 (ENT, recovered rank 5).** Name 3-grams (`sha`,`adi`,`kha`,`han`,`sag`) align with table-shortened names. Consistent with entity distortion, not the primary slice.

**KN039 (VOCAB, rank 17).** `nokia` plus `android` fragments (`ndr`,`oki`). Candidate generation yes; not Top-5. Mixed VOCAB/English.

**KN017 (VOCAB negative control, rank 5).** Shared grams `pro rot oto tot rso son` indicate **string-level** overlap with the gold **body**, not a solved `supersonic`↔تیز رفتار paraphrase in the headline. Honest unexpected lexical hit. Does **not** license calling VOCAB a romanization success.

**KN012 (regressed, 5 → MISS).** `dadi`/`nahi` 3-grams remain (`dad`,`adi`,`nah`) but were not enough against a 3-gram index of 68.9M features. A previous Hit@5 success left Top-50.

**KN014 (regressed, 44 → MISS).** `mobile`/`hone` grams (`mob`,`obi`,`hon`) did not keep the gold in Top-50.

---

## 19. Candidate-Generation Analysis

| | Count |
| --- | ---: |
| Baseline outside Top-50 | **45** |
| NG3 outside Top-50 | **43** |
| Recovered (MISS → in50) | **4** |
| Newly lost (in50 → MISS) | **2** |
| Net | **+2** |

Primary-slice recovery is **1** of those 4. The other three are outside ROOM Cat1.

---

## 20. Ranking Analysis

Golds in Top-50 under either system:

| ID | Base | NG3 |
| --- | ---: | ---: |
| KN004 | 1 | 1 |
| KN012 | 5 | MISS |
| KN014 | 44 | MISS |
| KN017 | MISS | 5 |
| KN023 | 3 | 3 |
| KN035 | MISS | 5 |
| KN038 | 3 | 1 |
| KN039 | MISS | 17 |
| KN048 | 42 | 31 |
| KN050 | MISS | 1 |

KN038 improved 3→1. KN048 improved 42→31 (still RANK). No reranker was added.

---

## 21. Failure / Regression Analysis

Regressions are **not** hidden:

- **KN012:** only baseline Hit@5 loss; gold leaves the candidate set. 3-grams can **destroy** a thin exact-token path (`dadi`).  
- **KN014:** RANK path via `mobile` is lost.

Remaining ROOM Cat1 misses: 3-gram overlap often exists (`orl`/`rld` on KN001) but BM25 over a 9140-term 3-gram vocabulary prefers documents that repeat common grams. Split/acronym cases (KN006, KN047, KN051) behaved as pre-declared: **not recovered**.

---

## 22. Negative Control Analysis

| ID | Base | NG3 | Interpretation |
| --- | --- | --- | --- |
| KN017 | MISS | **Hit@5 (rank 5)** | Unexpected. Body-level 3-gram overlap, not paraphrase solved. |
| KN020 | MISS | MISS | As expected (`cpec` vs راہداری). Overlap 10 is function/incidental grams. |
| KN041 | MISS | MISS | As expected. |
| KN006 | MISS | MISS | Split `ipl`; as declared. |
| KN047 | MISS | MISS | `fbr` letters; as declared. |
| KN051 | MISS | MISS | `gmail` vs `ji mil`; as declared. |

Do not treat KN017 as confirmation of the romanization story.

---

## 23. Computational Cost

| Item | Value |
| --- | --- |
| Documents | 111,860 |
| Method D tokens | 31,229,767 |
| NG3 features | 68,929,325 |
| Short-token passthrough | 7,761,213 |
| NG3 vocabulary | 9,140 terms |
| Tokenize+expand | 108.7 s (successful run) |
| BM25 build | 49.6 s |
| Python | 3.13.9 |
| Search repeat | identical ranks |

Peak memory was not separately instrumented; the NG3 posting lists fit in the same process as R2-B0 BM25.

---

## 24. Limitations

- n=11 primary slice: +1 is small.  
- 3-grams are common; overlap ≠ retrieval.  
- KN017 shows 3-grams also match non-ROOM lexical accidents.  
- Two Top-50 losses include a former Hit@5.  
- DEV Hit@50 2→4 is descriptive, not a TEST result.  
- Full corpus was indexed once; 51-query search was repeated, not a second full index build.

---

## 25. Interpretation

The pre-registered mechanism **can** fire: KN050 shows `world`/`orld` trigrams plus a distinctive name taking gold to rank 1. It does **not** generalize across ROOM Category 1 (10/11 still MISS). It is **not** confined to ROOM (VOCAB/ENT recoveries). It **harms** at least one exact-token success.

That is **partial support** for candidate-generation 3-grams, not a license to tune n, fuse dense retrieval, or claim Roman KN is solved.

McNemar p=0.6875: no significance claim.

---

## 26. Scientific Decision

`R2-NG3 PARTIALLY SUPPORTED`

ROOM Category 1 Hit@50 moved **0/11 → 1/11** (KN050), matching the hypothesized `orl`/`rld` bridge, while 10/11 stayed out, two previously retrieved golds left Top-50 (including KN012), and negative-control KN017 entered Top-5. Do **not** try n=4, fuzzy match, dictionary expansion, or dense fusion inside this experiment.

Narrower Roman-branch statement: exact-token Method D, simple fallback-table replacement (R2-1), and this single 3-gram bridge **together** still leave almost all ROOM Category 1 golds ungenerated. That is **not** “Roman Urdu retrieval is impossible.” It is that **this family of simple lexical matching tests has limited, fragile gains** and must not be rescued with ad-hoc extras here.

A later **independent** confirmation protocol could be designed separately. R2-NG3 itself is finished.

---

## 27. Reproducibility / Hashes

See the final response for SHA-256 of new files. Config and representation stats record dictionary, corpus, Method D stream, and NG3 feature-stream hashes. `ng3_matching.py` contains no benchmark IDs. Runner refuses TEST paths.
