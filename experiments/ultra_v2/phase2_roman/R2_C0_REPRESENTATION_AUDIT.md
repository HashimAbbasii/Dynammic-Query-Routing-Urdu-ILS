# R2-C0 — Roman Urdu representation and candidate-generation audit

**Status:** PASS (audit complete)  
**Date:** 2026-09-11  
**Branch:** `research/ultra-v2-strengthening`  
**Commit:** `fd54ac9b65c2db93e7e16fbf0c5a40b6a6025be1`  
**Label:** ULTRA v2 development audit. **Not a PLOS result. Not an official retrieval experiment.**  
**TEST:** not accessed. **R2-1 / R2-2:** not implemented. **M0 / dictionary / R2-B0 outputs:** not modified.

---

## 1. Executive Summary

R2-B0 established that frozen Method D fails Roman KN TRAIN+DEV: **Hit@5 = 4/51**, **Hit@50 = 6/51**, **MISS-side = 45**, **RANK-side = 2**. R2-C0 asks whether that failure is caused by **document-side Romanization** being misaligned with the Latin forms used in the queries.

**Observed evidence (TRAIN/DEV only):**

- Gold articles are Urdu-script. Query ↔ original-Latin overlap is **0.000**. Method D is the only Latin bridge.
- On gold documents, **66.5%** of tokens use the character-table fallback; **31.3%** use reverse-dictionary first-key; **2.2%** are already Latin.
- Mean query ↔ Method D **content** overlap is **0.43** on failures vs **2.00** on the four Hit@5 successes.
- **28/51** queries have **zero content-token overlap** with the Method D gold. **27/51** have no content path into Top-50 (candidate-generation Category 1).
- English-hint query tokens: **190** total, **4** exact matches in Method D gold (`mobile`, `internet`, `film`, `bank`). The four Hit@5 successes contain **zero** English-hint tokens.
- Direct character-table mappings, not intuition: `ورلڈ → orld` (query `world`), `سلمان → slman` (query `salman`), `ٹائٹل → taitl` (query `title`), `جی میل → ji mil` (query `gmail`), `زمبابوے → zmbaboe` (query `zim`).
- Dictionary first-key mismatch (`kya` vs `kiya`) remains a **function-word** issue. It does not explain content-token candidate generation. **NORM stays 0. R2-1 is still not justified.**

**COUNTERFACTUAL DIAGNOSTIC — NOT AN EXPERIMENTAL RESULT.** A stricter consonant-skeleton overlap (content tokens, skeleton length ≥ 3, non-function Method D tokens) is higher than exact overlap on **31/47** failures (ROOM: **15/19**). This diagnostic **understates** the `world`/`orld` class, because `و → o` changes the consonant, so vowel-stripping cannot recover it.

**Decision:** representation mismatch is real, general, and mechanistically tied to Method D’s fallback table and to Urdu-letter spelling of English/acronyms. It is **not** the cause of every miss (VOCAB paraphrase, one NEIGH topical neighbor, and some abbreviated entity queries remain). The Roman **representation** direction is therefore a valid controlled experiment. The Roman **normalization / R2-1** direction is not revived.

### CURRENT DECISION

`VALID HYPOTHESIS FOR CONTROLLED EXPERIMENT`

---

## 2. Scope and Safety Constraints

This is a **research audit only**.

| Action | Status |
| --- | --- |
| Open TEST query text / TEST CSVs / TEST gold / TEST retrieval | **Forbidden; not done** |
| Modify `experiments/phase5_roman_urdu/run_phase5.py` | Not done |
| Modify `experiments/phase12/**`, `results/**`, `Papers/PLOS_ONE/**` | Not done |
| Modify `models/roman_urdu_dict_expanded.json` | Not done (read-only) |
| Modify R2-B0 artifacts | Not done |
| Tune BM25 k1/b, Top-K, routing, tokenization | Not done |
| Implement R2-1, R2-2, dense/hybrid/rerank, new retrieval | Not done |
| Authorized inputs | R2-B0 TRAIN/DEV Roman KN, R2-B0 outputs, R2-B0 failure analysis, corpus rows of those gold IDs, Method D source (inspect), dictionary (inspect) |

Temporary in-memory overlap / skeleton calculations are labeled counterfactual diagnostics. They are **not** new Hit@5 numbers.

---

## 3. Repository / Branch / Commit

| Item | Value |
| --- | --- |
| Branch | `research/ultra-v2-strengthening` |
| Commit | `fd54ac9b65c2db93e7e16fbf0c5a40b6a6025be1` |
| Python | 3.13.9 |
| Diagnostic script | `experiments/ultra_v2/phase2_roman/run_r2_c0_audit.py` |
| Frozen M0 module | `experiments/phase5_roman_urdu/run_phase5.py` (imported; not edited) |
| Git at audit start | `M .gitignore`; untracked `experiments/ultra_v2/` (collection + Phase 2). No frozen-path diffs. |

Checkout, reset, commit, and push were not performed.

---

## 4. Authorized Data

| File | Role |
| --- | --- |
| `experiments/ultra_v2/benchmark/train/queries_kn.csv` | Roman KN TRAIN (n=33) |
| `experiments/ultra_v2/benchmark/dev/queries_kn.csv` | Roman KN DEV (n=18) |
| `experiments/ultra_v2/phase2_roman/artifacts/r2_b0_per_query.csv` | Frozen R2-B0 ranks / Hit@k |
| `experiments/ultra_v2/phase2_roman/R2_B0_FAILURE_ANALYSIS.csv` | Existing primary labels |
| `experiments/ultra_v2/phase2_roman/R2_B0_FAILURE_ANALYSIS.md` | Existing diagnosis |
| `data/clean_articles.csv` | Gold document text by `source_doc_id` |
| `models/roman_urdu_dict_expanded.json` | Reverse-dict inspect only |
| `experiments/phase5_roman_urdu/run_phase5.py` | Method D implementation |
| `artifacts/_index_cache.pkl` | Cached frozen roman BM25 for competitor inspection only |

NL queries were not scored (no official pooled qrels). Urdu KN queries were not included (R2-B0 primary is Roman KN).

Roman KN TRAIN+DEV **n = 51**. Detector vs metadata mismatches: **0** (R2-B0).

---

## 5. TEST-Seal Verification

| Check | Result |
| --- | --- |
| TEST query CSVs opened | **No** |
| TEST query IDs searched / printed | **No** |
| TEST retrieval / TEST metrics | **No** |
| `run_r2_c0_audit.py` TEST path | Hard-refuse: any path under `experiments/ultra_v2/benchmark/test/` raises `REFUSED` |
| Splits loaded | `train` and `dev` only |
| Seal manifest (metadata only) | `experiments/ultra_v2/benchmark/test/seal.json` |
| Seal `kind` | `ultra_v2_test_seal` |
| Seal `aggregate_sha256` (from seal.json metadata only) | `48610601209c3723a7252bb9a197d8fbbece18640e0bf7aef972884816ab46c4` |

Sealed relative files in the manifest: `queries_kn.csv`, `queries_nl.csv`. Those files were **not** read. `verify_test_seal.py` was **not** run, because it would read TEST file bytes to re-hash them.

`r2_c0_summary.json` records `"test_accessed": false`.

---

## 6. Method D Implementation Reconstruction

Reconstructed from `run_phase5.py`, not from memory. Official M0 Roman path used by `run_r2_b0.py`:

```
Query
  → detect_script (U+0600–U+06FF vs ASCII letters)
  → ROMAN ⇒ tokenize(query) as typed
  → BM25.search on romanized-document index
  → Top-50 candidates
  → official cutoff Top-5
```

Documents were romanized at index time; queries were not.

### 6.1 Script detection

- **Location:** `detect_script` in `run_phase5.py` (~L128).
- **Input:** raw query string.
- **Rule:** Urdu-letter count vs ASCII-letter count → `URDU` / `ROMAN` / `MIXED` / `OTHER`.
- **Routing (M0):** `ROMAN` → Method D roman BM25; other scripts → Urdu BM25.
- **Information loss:** Latin-only English civic queries are labeled ROMAN. That is detector behavior, not a claim that the string is chat Roman Urdu.

### 6.2 Query tokenization / representation

- **Location:** `tokenize` (~L113); `TOKEN_RE = [\u0600-\u06FF]+|[A-Za-z0-9]+`.
- **Input:** query text.
- **Output:** lowercased script-runs / alphanumerics. Punctuation splits. No stemming, no dictionary, no alias fold, no n-grams.
- **R2-B0:** `qtoks = tokenize(query_text)` then `roman_bm25.search(qtoks)`.
- **Mismatch risk:** fused tokens (`kiahua`) stay one token; English and Roman Urdu share the same Latin channel.

The mixed-query branch in `run_phase5.py` (~L610–613) romanizes Urdu tokens *inside MIXED queries*. R2-B0 Roman KN does **not** use that branch.

### 6.3 Document romanization

- **Location:** index loop ~L407–411; per-token `romanize_token` (~L221).
- **Input:** corpus token from the same tokenizer.
- **If Urdu letters and token is a reverse-dict value:** emit **first JSON key** (`load_reverse_roman` uses `setdefault`).
- **Else if Urdu letters:** `naive_roman_word` via `_CHAR_ROMAN` (45 entries, ~L55–63).
- **Else:** lowercase Latin/alnum kept.
- **Empty strings dropped.**

Closed character table (complete):

| Class | Mapping |
| --- | --- |
| Vowels / matres | `ا→a`, `آ→aa`, `و→o`, `ی→i`, `ے→e`, `ئ→i`, `ؤ→o`, `أ→a`, `إ→i`, `ع→a` |
| Deleted | `ء→""` |
| Consonants | `ب→b` … `ک→k`, `گ→g`, `ش→sh`, `خ→kh`, `غ→gh`, `ژ→zh`, `ٹ/ط→t`, `ڈ→d`, `ں→n`, … |

**Critical substitutions for this audit:**

1. **`و → o` always.** Urdu `ورلڈ` (the usual spelling of *world*) becomes `orld`, not `world`. The English consonant W is not preserved.
2. **Unwritten short vowels are never generated.** `سلمان` → `slman`, not `salman`.
3. **`ی → i`**, so names users type with `y`/`i` variation become `shahd` not `shahid`.
4. **Letter-named acronyms.** `ایف` `بی` `آر` → `aif` `bi` `aar`, not `fbr`.

### 6.4 Dictionary load / usage

- **Path:** `models/roman_urdu_dict_expanded.json`
- **Keys:** 198 Latin → 188 unique Urdu values
- **SHA-256:** `30c3f61a64ec641abbb3acdbc7a8bcaf197f0238f1bf9e76c2c7ce8e590f86a3` (verified)
- **Query side (Method D):** unused
- **Document side:** reverse first-key only
- **Multi-key Urdu values:** 9 groups. Canonical (first key) vs later aliases include `kiya`/`kya`, `government`/`hukumat`, `football` as a first-key English form for `فٹبال`, `mobile` for `موبائل`

### 6.5 Vocabulary matching and BM25

- **Location:** `BM25.search` (~L257). Missing postings are skipped (`if t not in self.post: continue`).
- **k1 = 1.5, b = 0.75** (frozen)
- **Candidate depth:** `TOP_K = 50`
- **Official cutoff:** 5
- **Unknown query tokens:** kept on the query; they contribute 0 if absent from the index. R2-2 remains a no-op.

### 6.6 Possible information loss (no fix proposed)

| Stage | Loss / mismatch |
| --- | --- |
| Tokenizer | Splits Urdu-letter acronyms into one-letter tokens |
| Reverse dict | First key may be English (`government`) or a sibling (`kiya` not `kya`) |
| Character table | `و→o`; no short vowels; hamza deleted |
| Query | User types English/chat Roman; index holds table output |
| BM25 exact match | Near-forms (`world`/`orld`) do not match |

---

## 7. R2-B0 Baseline Recap

Independent R2-B0 run (`run_r2_b0.py`, 2026-09-11). Not recomputed as a new official experiment here.

| Split | n | Hit@1 | Hit@5 | Hit@10 | Hit@50 | MRR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| TRAIN | 33 | 1 | 3 | 3 | 4 | 0.0472 |
| DEV | 18 | 0 | 1 | 1 | 2 | 0.0198 |
| TRAIN+DEV | **51** | **1** | **4 (0.0784)** | **4** | **6 (0.1176)** | **0.0375** |

Hit@5 successes: KN004 (rank 1), KN012 (5), KN023 (3), KN038 (3).  
RANK: KN014 train gold 79754 rank 44; KN048 dev gold 20073 rank 42.

Existing failure taxonomy (**not redefined**):

| Primary | n | % of 47 failures |
| --- | ---: | ---: |
| ROOM | 19 | 40.4% |
| ENT | 16 | 34.0% |
| VOCAB | 9 | 19.1% |
| RANK | 2 | 4.3% |
| NEIGH | 1 | 2.1% |
| NORM / QAMB / TEMP | 0 | 0% |

MISS-side 45, RANK-side 2. Sum of primaries = 47.

R2-B0 overlap counters (inputs, not labels): `sibling_any=8`, `near_any=45`, `zero_content_overlap=26`, `zero_overlap=2`.

---

## 8. Character-Table Artifact Analysis

Scope: the **51 TRAIN/DEV Roman KN gold documents**, romanized with the frozen `romanize_token` path.

| Measurement | Result |
| --- | --- |
| Gold docs using reverse-dictionary at least once | **51/51** |
| Gold docs using fallback at least once | **51/51** |
| Mean fraction of tokens via dictionary | **0.3133** |
| Mean fraction via fallback character table | **0.6649** |
| Mean fraction already Latin | **0.0217** |
| Mean `len(fallback_roman)/len(original_token)` | **1.0279** |
| Empty romanizations | **0** |
| Gold docs with ≥1 roman-form collision (two original tokens → same Latin) | **13/51** |

Token length is **not** the distortion. Fallback strings are about as long as the Urdu token because digraphs (`sh`, `kh`) offset missing short vowels. Distortion is **substitution and omitted vowels**, not truncation.

### 8.1 Systematic forms produced by the table

Quantified by applying the frozen table to attested gold tokens (not hypothetical English):

| Original Urdu (gold) | Method D | Ordinary query form in this set | Mechanism |
| --- | --- | --- | --- |
| ورلڈ | `orld` | `world` (KN001, KN013, KN050) | `و→o` |
| چیمپئن | `chimpin` | `championship` | table + tokenization (`شپ`→`shp`) |
| زمبابوے | `zmbaboe` | `zim` / Zimbabwe | omitted vowels + `و→o` |
| سلمان | `slman` | `salman` | omitted short `a` |
| ٹائٹل | `taitl` | `title` | `آ→aa` residue + omitted `i` |
| کولکتہ | `kolkth` | `kolkata` | `ہ`/`ۃ` + omitted `a` |
| جنگل بک | `jngl` `bk` | `jungle` `book` | omitted vowels |
| جی میل | `ji` `mil` | `gmail` | token boundary + `ی→i` |
| فٹنس | `ftns` | `fitness` | omitted vowels |
| شاہد | `shahd` | `shahid` | omitted `i` |

These are **unlikely to be typed** by a Roman Urdu or English-mixing user. They are table artifacts.

### 8.2 Vowel deletion vs consonant damage

Two fallback subclasses must be kept separate:

1. **Unwritten short vowels** (`سلمان→slman`, `جنگل→jngl`). Consonant skeleton can still match if matching is not exact BM25.
2. **Consonant substitution** (`ورلڈ→orld`). Skeleton(`world`)=`wrld` ≠ skeleton(`orld`)=`rld`. Vowel-stripping **cannot** recover this class.

Subclass 2 is why a naive “normalize vowels” story is insufficient, and why R2-1 (dictionary siblings) is the wrong instrument.

---

## 9. Query–Document Lexical Alignment

For every authorized Roman KN query, tokens were compared as:

- A. raw query tokens (`tokenize` as typed)
- B. gold original tokens (Urdu-script tokenizer output)
- C. gold Method D tokens
- D. exact BM25-matching tokens = A ∩ C

| Metric | All 51 | Hit@5 success n=4 | Failures n=47 |
| --- | ---: | ---: | ---: |
| Mean query tokens | 11.59 | 11.00 | 11.64 |
| Mean Method D overlap (any token) | 3.00 | 4.25 | 2.89 |
| Mean **content** overlap with Method D | **0.55** | **2.00** | **0.43** |
| Mean overlap with original **Latin** tokens | **0.00** | 0.00 | 0.00 |
| Zero content overlap with Method D | **28** | 0 | 28 |
| Zero any-token overlap | **2** (KN001, KN017) | 0 | 2 |

**Does Method D make the gold less lexically accessible than the original document?**

The original document is Urdu script. Latin queries have **zero** exact overlap with original tokens. Method D is more accessible than the raw Urdu original **by construction**, but the Latin it emits is still the wrong Latin. The scientifically relevant comparison is therefore:

> query forms vs Method D Latin vs a less-distorted romanization of the same Urdu document.

That last comparison is the counterfactual in §17, not a new official score.

Function-word overlap accounts for most of the mean 3.0 raw overlap (`ke`, `mein`, `hai`, `ka`, `ne`, `se`). Content overlap is the retrieval-relevant quantity.

**Taxonomy limitation (not a relabel):** R2-B0 reported `zero_content_overlap=26`. This diagnostic uses an explicit function-word list and counts **28**. The two-query difference is a definition delta, not evidence that R2-B0 was wrong. Primary labels were not changed.

---

## 10. ROOM Analysis

ROOM = 19, all `miss_side=MISS` (existing labels).

| ROOM slice | n |
| --- | ---: |
| Zero Method D content overlap (Category 1) | **11** |
| Some content overlap but gold not in Top-50 (Category 3) | **8** |
| Content skeleton ≥3 gain vs exact overlap | **15** |
| Zero content skeleton ≥3 | **2** |

### 10.1 Mechanism breakdown of the 19 (not a new primary taxonomy)

Counts below are **mechanism tags on the existing ROOM set**. A query may show more than one mechanism; the dominant one is listed.

| Dominant mechanism | n | IDs (dominant) |
| --- | ---: | --- |
| English/loanword vs character-table form (`world`/`orld`, `title`/`taitl`, `photo`/`foto`, `gmail`/`ji mil`) | 10 | KN001, KN008, KN011, KN013, KN021, KN037, KN044, KN045, KN050, KN051 |
| Acronym letter-naming (`ipl`/`aii pi ail`, `adb`/`ae di bi`, `fbr`/`aif bi …`, `psl`/`pi ais ail`) | 5 | KN006, KN010, KN025, KN047, KN049 |
| Mixed table + high-df leftover (`fifa`/`pakistan` match; `germany`/`ranking` do not) | 2 | KN024, KN031 |
| Semantic translation inside a ROOM-labeled row | 2 | KN027 (`chameleon` vs `گرگٹ`/`grgt`); part of KN011 (`solar` vs `شمسی`) |

KN006 has **zero** content skeleton ≥3 (`kolkata`/`kolkth` skeletons differ; `ipl` vs three Urdu letter-names). That is representation, but **not** vowel-stripping.

### 10.2 What was lost

On the 11 ROOM Category 1 rows, **no content query token** occurs in the Method D gold. English tokens (`world`, `championship`, `tennis`, `hydrogen`, `twitter`, `gmail`, …) are systematically unmatched. Urdu-derived Roman tokens sometimes survive as function words only (`ke`, `hai`).

English tokens in ROOM golds **do not survive as English**: they were written in Urdu script in the article, then table-romanized.

ROOM is not “the query is hard.” It is “the index string is not the query string for the same named concept.”

---

## 11. Entity Analysis

ENT = 16, all MISS (existing labels).

| ENT slice | n |
| --- | ---: |
| Zero Method D content overlap | **9** |
| Of those 9, content skeleton ≥3 > 0 | **5** |
| Content skeleton ≥3 gain vs exact (all ENT) | **11** |
| Some exact content overlap, still miss Top-50 | **7** |

### 11.1 Entity-type inventory (existing R2-B0 grouping, with Method D forms)

**Persons / names:** KN016 `priyanka` vs `prianka`; KN019 `jlo` vs `jinifr lopiz`; KN022 `shahid`/`mira` vs `shahd`/`mira` (`mira` matches); KN026 `salman` vs `slman`; KN029 `kumar sanu` vs `kmar sanoki`; KN030 `imran tahir` (`imran` matches); KN032 `umar akmal` vs fused `amrakml`; KN033 `shane warne` vs `shin oarn`; KN034 `sharmeen obaid` vs `shrmin abid`; KN035 `zaheer` vs `zhir` (`khan` dict-matches); KN054 `kangana`/`momina` vs `kngna`/`momnh`.

**Products:** KN040 `samsung galaxy` vs `gliksi`; KN043 `moto` matches, `p30`/`apple` do not; KN052 `samsung` vs `sam sng`; KN053 `huawei mate` vs missing `huawei`, `pakistan` leftover.

**Event:** KN002 `zim t20` vs `zmbaboe` / `ti tointi`.

### 11.2 Distortion vs query-form vs “entity not the problem”

| Pattern | n (descriptive) | Interpretation |
| --- | --- | --- |
| Strong semantic link, **zero** exact content overlap, Method D name is a table artifact | 8 | representation (e.g. `zmbaboe`, `slman` with no exact match, `shin oarn`) |
| Partial exact overlap (family name, `mira`, `imran`, `khan`, `film`, `moto`, `pakistan`) | 7 | distinctive entity token still lost; leftover is high-df |
| Query uses a nickname/acronym the gold never contains (`jlo`) | 1 (KN019) | **not** solely Method D; even `jennifer lopez` romanized as `jinifr lopiz` would miss `jlo` |
| Token fusion (`عمراکمل` → `amrakml`) | 1 (KN032) | tokenizer + table; representation |

**Do not overclaim:** fixing Method D romanization would not automatically retrieve `jlo` or `zim` if the gold never contains those short forms. It **would** address `salman`/`slman`, `shahid`/`shahd`, `zaheer`/`zhir`, `samsung`/`sam sng` (سام سنگ letter split), `zimbabwe`/`zmbaboe` if the query used a fuller form.

Entity distortion is **systematic for names written in Urdu and passed through `_CHAR_ROMAN`**. It is not 16/16 of ENT.

---

## 12. VOCAB Analysis

VOCAB = 9, all MISS (existing labels). The audit must not recode these as representation by default.

| ID | Query content (abbrev.) | Gold Method D headline (abbrev.) | Dominant |
| --- | --- | --- | --- |
| KN017 | `boom supersonic passenger prototype unveil` | `oaz se gna tiz rftar … tiarh` (Concorde-class paraphrase) | **B paraphrase** (zero overlap) |
| KN020 | `cpec joint cooperation committee session` | `aqtsadi rahdari … taaon kmiti ajlas` | **B** (CPEC vs راہداری) |
| KN041 | `caretaker finance minister cpec projects` | `nGran wazir khzanh` + راہداری | **B** (zero content and zero skel≥3) |
| KN015 | `viral maths puzzle … confuse` | `riazi … soal`; `internet` matches | **C both** (internet survives; puzzle≠سوال) |
| KN028 | `state bank external debt burden percent` | `astit bank` + Urdu debt terms | **C** (`bank` matches; `external debt`≠`ghir mlki qrzon`) |
| KN036 | `local oil gas output izafa` | `kham til` `gis` | **C** (`gas`/`gis` is table-like; `oil`/`til` is lexical) |
| KN039 | `nokia android handset … sold out` | `nokia` matches; `frokht` vs `sold` | **C** |
| KN042 | `current account deficit … sbp` | `jari khate … astit bank` | **B/C** |
| KN046 | `ml1 railway upgrade deadline` | `arbon dollar projikt` | **B** |

**A (representation-only): 0 of 9 as the sole story.**  
**B (genuine paraphrase): 4 clear** (KN017, KN020, KN041, KN046).  
**C (both): 5.**

`vocab_skel_gain` on the loose skeleton metric is 7 because short skeletons and incidental consonants fire. Under the stricter ≥3 content skeleton, KN041 remains a clean paraphrase miss. **VOCAB is not a Romanization failure class.** Treating it as one would manufacture a Method D success story.

---

## 13. English Token Analysis

`ENGLISH_HINT` is a **closed list of TRAIN/DEV query words**, not a linguistic English detector. Report it as such.

| Measurement | Result |
| --- | ---: |
| English-hint tokens in 51 queries | **190** |
| Exact match in Method D gold | **4** |
| Exact match in original Latin gold tokens | **0** |
| Mean English-hint tokens, Hit@5 success | **0.00** |
| Mean English-hint tokens, failures | **4.04** |

The four exact Method D matches: KN014 `mobile` (dictionary first-key for `موبائل`), KN015 `internet`, KN026 `film`, KN028 `bank`.

English **content** words (`world`, `championship`, `fitness`, `satellite`, `twitter`, `samsung` as a Latin query, …) are almost entirely absent from Method D golds because the articles write those concepts in **Urdu script**, then the table emits `orld`, `chimpin`, `ftns`, `sitlait`, `toitr`, `sam sng`.

Method D does **not** treat “English in the document” as English. It treats Urdu-script loanwords as character-table strings. Roman Urdu-derived function words (`ke`, `hai`) and a few dictionary values (`mobile`, `khan`, `football`) are the exceptions.

Success vs fail English means is **descriptive only** (success n=4). It is consistent with the mechanism: the four successes are chat-Roman / Urdu-derived (`ghee`, `dadi`, `aziz mian`, `peshawar`), not English-heavy named-event queries.

---

## 14. Query Structure Analysis

| Feature | Success n=4 | Fail n=47 |
| --- | ---: | ---: |
| Mean query length (tokens) | 11.00 | 11.64 |
| Mean content tokens | 7.00 | 7.40 |
| Mean English-hint tokens | 0.00 | 4.04 |

Query **length** and **content-token count** do not separate success from failure. English-hint load does, descriptively.

**Sample size is too small for a statistical test.** No t-test or correlation is reported. n=4 successes cannot support a population claim.

---

## 15. Candidate-Generation Analysis

R2-B0: 45 MISS-side, 2 RANK-side. R2-C0 maps golds into four evidence categories:

| Category | Definition used here | n |
| --- | --- | ---: |
| 0 | Hit@5 success | **4** |
| 1 | No Method D **content** overlap and not in Top-50 | **27** |
| 2 | In Top-50, not Top-5 (RANK) | **2** |
| 3 | Some content overlap, still not in Top-50 | **18** |
| 4 | Other | **0** |

### Category 1 — no meaningful lexical path into Top-50

27 queries. Gold is absent from Top-50 and shares no content token with the query. BM25 can only score function words or nothing. KN001 and KN017 score **nothing** (zero overlap). This is candidate generation, not ranking.

Competitors inspected from the **cached frozen** roman BM25 (diagnostic, not a new official run) are other Roman-index documents that share leftover Latin fragments. They are not evidence that gold “almost” made it.

### Category 2 — RANK

KN014 rank 44: matching `mobile` (dict), `hone`, `ki`, `hai`. Lost distinctive terms: `charge` vs `charj`, `ghalti` vs `ojh`.  
KN048 rank 42: matching `10`, `2020`, `aur`. `samsung` vs `sam sng`; `lite` unmatched.

Both are **in** the candidate list. Distinctive tokens are still table-damaged. Ranking is the official miss_side; representation still explains why they sit at 42–44.

### Category 3 — lexical leftovers, lose to competitors

18 queries have ≥1 content match (`pakistan`, `india`, `fifa`, `nokia`, `film`, `lahore`, `imran`, …) and still miss Top-50. The matching terms are **high document-frequency** relative to the missing distinctive terms. Competitors are other documents that also contain `pakistan` / `film` / `nokia`.

This is **candidate generation among a misleading lexical neighborhood**, not proof that gold had a strong unique path.

### Category 4

Not used. No evidence of an implementation bug that drops a strong exact-match gold (e.g. empty romanization of the gold). Empty romanizations on gold tokens = 0.

**Conclusion for §15:** the Roman KN problem is **fundamentally candidate generation** (45/51 not in Top-50). Representation explains why distinctive query tokens have no postings on the gold. Ranking among true candidates is a 2-query phenomenon.

---

## 16. Reverse-Dictionary Analysis

| Measurement | Result |
| --- | --- |
| Dictionary keys | 198 |
| Unique Urdu values | 188 |
| Urdu values with >1 Latin key | **9** |
| Gold-doc tokens using dict (mean fraction) | 0.313 |
| Gold-doc tokens using fallback | 0.665 |

The nine multi-key groups and first keys: `aaj` (`aj`,`today`); `adalat` (`court`); `gaya` (`geya`); `government` (`hukumat`); `jeet` (`win`); `kiya` (`kya`); `loss` (`shikast`); `ne` (`ny`); `se` (`sy`).

**First-key behavior observed in failures:** `کیا` indexes as `kiya` while 8 queries use `kya`. All 8 are function-word siblings already rejected as primary NORM in R2-B0.

**Dictionary is not the main driver of the 45 MISS-side cases.** Fallback covers two-thirds of gold tokens, including almost all names, English loanwords, and acronyms. Dictionary expansion is **not** supported as the next experiment. Occasional English first-keys (`mobile`, `football`) **help** when the query uses that English, which is the opposite of a “dictionary caused the miss” story.

---

## 17. Counterfactual Diagnostic Analysis

**COUNTERFACTUAL DIAGNOSTIC — NOT AN EXPERIMENTAL RESULT.**  
No official Method D run was replaced. No Hit@5 is claimed.

Question: if gold were represented in a less distorted Latin form, would query–gold mismatch decrease?

Two in-memory diagnostics:

| Diagnostic | Failures n=47 | ROOM n=19 | ENT n=16 |
| --- | ---: | ---: | ---: |
| Loose content skeleton overlap > exact content overlap | 43 | 18 | (included in 43) |
| **Stricter:** content tokens, skeleton length ≥ 3, vs non-function Method D tokens, overlap > exact | **31** | **15** | **11** |
| Zero exact content **and** zero stricter skeleton | **11** | 2 | (rest are VOCAB/NEIGH/short nicknames) |

Mean stricter skeleton overlap on failures: **1.62** vs mean exact content overlap **0.43**.

**Limitations (mandatory):**

- Skeleton overlap is **not** retrieval. It does not model IDF, false positives, or competitors.
- Loose skeletons overcount (`air`→`r`, `ke`→`k`). The ≥3 cutoff was added for that reason.
- Stricter skeletons **under-count** `world`/`orld` (`wrld`≠`rld`) and short nicknames (`zim`, `jlo`).
- Therefore 31/47 is a **lower bound** on “same concept, different Latin,” not an upper bound on recoverable Hit@50.

The diagnostic supports a **document-representation** experiment. It does not select a romanizer, a parameter, or a Top-K.

---

## 18. Representation vs Semantic Failure Separation

Dominant cause **for this audit**, without forcing every row into representation:

| Group | n | Dominant cause | Notes |
| --- | ---: | --- | --- |
| ROOM | 19 | **1 REPRESENTATION** (character table + acronym letter-naming + token split) | 2 rows mix semantic translation (`chameleon`/`گرگٹ`) |
| ENT | 16 | **3 ENTITY FORM** mixed with **1 REPRESENTATION** | Table-distorted names are representation; `jlo`/`zim` are query-side short forms |
| VOCAB | 9 | **2 QUERY VOCABULARY / PARAPHRASE** | 5 mixed with table-like English |
| NEIGH | 1 | **6 TOPICAL NEIGHBOR** | KN005 Iran/US equities vs PSX open |
| RANK | 2 | **4 CANDIDATE GENERATION** already succeeded; leftover is still table damage | KN014 `charge`/`charj`; KN048 `samsung`/`sam sng` |
| NORM / QAMB / TEMP | 0 | — | Unchanged |
| Ambiguity | 0 | **5 AMBIGUITY** not supported | |

**Bottleneck for the Roman KN slice:** representation-driven **candidate generation**, concentrated in ROOM and in ENT name distortion. Not “all 47 failures are Method D.” Not “close the Roman direction.” Not “revive R2-1.”

---

## 19. Quantitative Evidence Table

Only computed values. No invented cells.

| Evidence | Result |
| --- | --- |
| Roman KN TRAIN+DEV n | 51 |
| Hit@5 | 4/51 |
| Hit@50 | 6/51 |
| MISS-side | 45 |
| RANK-side | 2 |
| ROOM / ENT / VOCAB / NEIGH / RANK / NORM | 19 / 16 / 9 / 1 / 2 / 0 |
| Gold docs using dictionary (≥1 token) | 51/51 |
| Gold docs using fallback (≥1 token) | 51/51 |
| Mean token fraction dictionary / fallback / Latin | 0.313 / 0.665 / 0.022 |
| Mean query→original Latin overlap | 0.00 |
| Mean query→Method D overlap (any) | 3.00 |
| Mean query→Method D **content** overlap | 0.55 (success 2.00; fail 0.43) |
| Zero content overlap (this diagnostic) | 28 |
| Zero any overlap | 2 |
| English-hint tokens / exact Method D matches | 190 / 4 |
| Entity: ENT zero content / of which skel≥3>0 | 9 / 5 |
| Character-table: fallback token share | 0.665 |
| Character-table: `ورلڈ→orld`, `سلمان→slman`, `زمبابوے→zmbaboe` | attested on gold tokens |
| Candidate Category 1 / 2 / 3 | 27 / 2 / 18 |
| Counterfactual stricter skel gain (failures) | 31/47 — **not a retrieval result** |
| Roman collisions on gold docs | 13/51 |
| TEST accessed | no |

---

## 20. Representative Case Studies

Not only dramatic failures. Includes successes, RANK, VOCAB paraphrase, and an ENT nickname.

### 20.1 KN004 — Hit@5 success (rank 1)

- **Query:** `desi ghee sehat ke liye faida mand hai ya nuqsan deh`
- **Gold original headline:** گھی دوست یا دشمن
- **Method D headline:** `ghee dost ia dushman`
- **Matching:** `ghee hai ke sehat` (content: `ghee`, `sehat`)
- **Missing content:** `desi faida mand nuqsan deh` (some still skeleton-close)
- **Mechanism:** dictionary / conventional Roman for `گھی`; chat-Roman query; **no English-hint tokens**
- **Conclusion:** Method D can work when query Latin ≈ index Latin for content words.

### 20.2 KN023 — Hit@5 success (rank 3)

- **Query:** `qawwal aziz mian ki barsi …`
- **Gold:** معروف قوال عزیز میاں کی 16 ویں برسی → `marof qoal aziz mian ki 16 oin brsi`
- **Matching content:** `aziz mian`
- **Conclusion:** person names that survive as typed Roman match. `qawwal`/`qoal` still distorted but leftover name tokens suffice.

### 20.3 KN038 — Hit@5 success (rank 3, DEV)

- **Query:** `peshawar used car mela mein logon ki dilchaspi …`
- **Matching content:** `peshawar`, `logon`
- **Missing:** `car mela` (English/loan) vs `garion` `nmaish`
- **Conclusion:** a high-idf place name in both query and index can rescue an otherwise mixed query. Not a counterexample to English-token loss; `used`/`car` still miss.

### 20.4 KN012 — Hit@5 success (rank 5)

- **Matching content:** `dadi` only among content words.
- **Conclusion:** thin lexical path; still in Top-5. Success n=4 includes a near-miss-looking overlap. Do not treat 4/51 as proof that Method D is generally adequate.

### 20.5 KN001 — ROOM, Category 1, zero overlap

- **Query:** `malaysia air race world championship third round kab shuru hua`
- **Gold original:** کوالالمپور ائیر ریس ورلڈ چمپئن شپ کا تیسرا مرحلہ
- **Method D:** `koalalmpor aiir ris orld chmpin shp ka tisra mrhlh`
- **Matching:** none
- **Non-matching content:** `malaysia air race world championship …` vs `orld` `chmpin` `shp` `aiir`
- **Mechanism:** `و→o` (`world`/`orld`); championship split; Kuala Lumpur table form vs query `malaysia`
- **Conclusion:** same event, no BM25 path. Representation, not paraphrase.

### 20.6 KN051 — ROOM, token boundary

- **Query:** `gmail ke naye interface ko purane layout jaisa kaise banaya ja sakta hai`
- **Gold original:** کیا جی میل کے نئے ڈیزائن کو پرانے جیسا بنانا چاہتے ہیں
- **Method D:** `kiya ji mil ke nie dizain ko prane jisa bnana …`
- **Matching:** `hai ke ko` (function)
- **Mechanism:** `gmail` vs `ji`+`mil`; `interface`/`layout` vs `dizain`
- **Conclusion:** tokenizer + table, not a dict-alias problem.

### 20.7 KN047 — ROOM, acronym letter-naming

- **Query:** `fbr aur sindh revenue board ne sales tax input par kya deal ki`
- **Gold original:** ایف بی اور ایس بی ارکے درمیان سیلز ٹیکس معاہدہ طے ہوگیا
- **Method D:** `aif bi aur ais bi arke drmian silz tiks maahdh …`
- **Matching:** function words
- **Conclusion:** FBR/SRB as Urdu letter names. Representation of abbreviations, not “hard news.”

### 20.8 KN002 — ENT, event name

- **Query:** `zim t20 mein hosts ko chase ke liye kitna target mila`
- **Gold original:** دوسرا ٹی ٹوئنٹی زمبابوے کا پاکستان کو جیت کیلئے 176 رنز کا ہدف
- **Method D:** `dosra ti tointi zmbaboe ka pakistan ko jeet kilie 176 rnz ka hdf`
- **Matching:** `ke ko mein` (function)
- **Missing:** `zim t20 hosts chase target` vs `zmbaboe` `ti tointi` `hdf`
- **Conclusion:** entity + table. `zim` would still be a short-form problem under a better romanizer of `زمبابوے`. `zmbaboe` is nonetheless not a user form.

### 20.9 KN026 — ENT, person name distortion

- **Query:** `salman ki wrestler film ka pehla poster …`
- **Gold original:** سلمان خان کی نئی فلمسلطانکا پہلا پوسٹر جاری
- **Method D:** `slman khan ki nii flmsltanka phla postr jari`
- **Matching content:** `film`
- **Skeleton ≥3:** `slmn`, `flm`, `phl`, `pstr`
- **Conclusion:** classic omitted-vowel name. Category 3 leftover `film` is not enough for Top-50.

### 20.10 KN019 — ENT, nickname (entity not only representation)

- **Query:** `jlo ne 50 saal ki umar mein fitness kaise maintain ki`
- **Gold original:** جینیفر لوپیز 50 سال کی عمر میں اتنی فٹ اور کامیاب کیسے ہیں
- **Method D:** `jinifr lopiz 50 sal ki amr mein atni ft …`
- **Matching:** `50 ki mein ne`
- **Conclusion:** `jlo` is absent from gold under any honest romanization of جینیفر. `fitness`/`ft` is still table damage. Mixed ENT.

### 20.11 KN017 — VOCAB paraphrase (negative control)

- **Query:** `boom supersonic passenger prototype kab unveil hua`
- **Gold original:** واز سے گنا تیز رفتار سے سفر کرنے والا طیارہ متعارف
- **Method D:** `oaz se gna tiz rftar se sfr krne oala tiarh mtaarf`
- **Matching:** none
- **Conclusion:** different lexemes for the same story. **Not** a Method D romanization miss. A better romanizer still yields `tiarh` not `supersonic`.

### 20.12 KN020 — VOCAB paraphrase

- **Query:** `cpec joint cooperation committee …`
- **Gold:** اقتصادی راہداری … مشترکہ تعاون کمیٹی کا اجلاس
- **Matching:** `ka mein`
- **Conclusion:** English CPEC jargon vs Urdu راہداری. Representation will not create `cpec` from that headline unless the article also contains CPEC in some form.

### 20.13 KN014 — RANK 44

- **Query:** `mobile slow charge hone ki user side ghalti kya ho sakti hai`
- **Gold original:** فون دیر سے چارج ہونے کی ایک وجہ خود
- **Method D:** `fon dir se charj hone ki aik ojh khod`
- **Matching:** `hai ho hone ki mobile` (content: `mobile` via dict)
- **Conclusion:** gold **is** generated. `charge`≠`charj` keeps it at rank 44. RANK-side, representation-tinged.

### 20.14 KN048 — RANK 42

- **Query:** `samsung s10 lite aur note 10 lite 2020 lineup kab launch honay walay thay`
- **Gold original:** سام سنگ کا نئے سستے فلیگ شپ فونز کے ساتھ 2020 کا غاز
- **Method D:** `sam sng ka nie sste flig shp fonz ke sath 2020 ka ghaz`
- **Matching:** `10 2020 aur`
- **Conclusion:** `سام سنگ` letter-split vs query `samsung`. In Top-50 via digits.

### 20.15 KN005 — NEIGH (not representation)

- **Query:** Iran/US tension, local equities rebound
- **Gold Method D:** `pakistan astak aikschinj mein business ka msbt aghaz`
- **Conclusion:** different story. Closing Roman representation would not be justified from this row; keeping it open is not justified from this row either.

---

## 21. Normalization Reassessment

R2-B0: `sibling_any=8` (all `kya`↔`kiya`), `near_any=45`, `zero_content_overlap=26`, `NORM=0`.

Re-evaluation in light of representation:

| Claim | Verdict |
| --- | --- |
| Canonicalizing `kya`→`kiya` would fix candidate generation | **Rejected.** Function word; content tokens still absent |
| `near_any=45` is a closed spelling-normalization hypothesis | **Rejected.** Mostly `world`/`orld`-class table neighbors or noise (`teen`↔`mein`) |
| R2-1 is justified by R2-C0 | **No.** R2-C0 locates the mismatch in **document fallback**, not in the 198-key alias list |
| A generic “Roman Urdu spelling is variable” program | **Too weak.** The attested mechanism is a **fixed 45-letter table** plus letter-named acronyms |

Normalization of query siblings would not plausibly recover a substantial fraction of the 27 Category 1 misses.

---

## 22. Hypothesis Quality Test

**Hypothesis (for a later experiment, not implemented):**

> Method D’s document-side fallback (`naive_roman_word` / `_CHAR_ROMAN`) and Urdu-letter tokenization of English names and acronyms produce Latin index tokens that systematically fail to match the English and chat-Roman content tokens of ULTRA v2 Roman KN queries. That lexical inaccessibility is the primary cause of Top-50 candidate-generation failure on TRAIN/DEV ROOM cases and of a substantial share of ENT name misses.

| Criterion | Pass? | Evidence |
| --- | --- | --- |
| **H1 Generality** | **Pass** | 19 ROOM + multiple ENT/RANK rows; both TRAIN and DEV; 27 Category 1 |
| **H2 Mechanism** | **Pass** | `و→o`, omitted short vowels, letter-named acronyms, token splits; exact code path |
| **H3 Quantitative support** | **Pass** | 45/51 not in Top-50; 28 zero content overlap; 4/190 English exact matches; 15/19 ROOM stricter-skeleton gain |
| **H4 Non-triviality** | **Pass** | Not “spelling varies.” It is a closed character table plus tokenizer behavior. R2-1 siblings do not encode `world`/`orld` |
| **H5 Experimental testability** | **Pass** | Freeze queries, BM25 k1/b, Top-50, dictionary, TEST. Change **only** document romanization of Urdu tokens that currently take fallback (and optionally letter-split Latinization). Pre-register Hit@50 on ROOM Category 1 as the test; VOCAB paraphrase (KN017/KN020/KN041) as negative control |
| **H6 No leakage** | **Pass** | TRAIN/DEV only; TEST CSVs not opened |
| **H7 No tuning** | **Pass** | No k1/b/K/threshold/dictionary edits; overlaps are diagnostics |

No criterion failed.

---

## 23. Proposed Future Hypothesis — if justified

**OBSERVED EVIDENCE** is §§7–21. What follows is **POSSIBLE FUTURE HYPOTHESIS** only.

### Exact hypothesis

See §22.

### Affected failure categories

Primary expected movement: **ROOM** (especially Category 1 English/loanword and acronym rows) and **ENT name-table distortion** (`slman`, `shahd`, `zmbaboe`, `sam sng`).  
Secondary: RANK distinctive tokens (`charj`, `sam sng`).  
**Not expected to move:** VOCAB paraphrase (KN017, KN020, KN041, KN046), NEIGH KN005, nickname ENT KN019 (`jlo`).

### Expected mechanism

A less lossy document Latin (preserving `w` for `و` in loanwords, or producing conventional Roman for names, or not splitting `جی میل` away from `gmail`-like forms) would create exact or near-exact postings for query content tokens that currently have none, allowing BM25 to generate gold into Top-50 **without** changing the query, the scorer, or TEST.

### Proposed next experiment (high level — not implemented)

Isolated **document-representation** swap on TRAIN/DEV Roman KN. One pre-registered alternative romanizer vs frozen Method D. Same queries, same k1/b, same Top-50, same gold IDs. Report Hit@50 first (candidate generation), Hit@5 second. Slice by existing R2-B0 primaries.

### What must remain frozen

`run_phase5.py` as the official M0; Phase 12; PLOS; historical H/K/U/QTRN; TEST seal; R2-B0 artifacts; dictionary file bytes; BM25 parameters; query text; candidate depth for the comparison.

### Metric that tests the hypothesis

Pre-registered: **ExactSource Hit@50** on the 19 ROOM queries, and on the 11 ROOM Category 1 subset. Secondary: Hit@50 on ENT excluding KN019.

### Falsification

If Hit@50 on ROOM Category 1 does not increase, or if the only gains are on VOCAB paraphrase rows, the representation hypothesis is **falsified** and the Roman representation direction should then be closed.

**Do not implement this experiment in R2-C0.**

---

## 24. Final Decision

`VALID HYPOTHESIS FOR CONTROLLED EXPERIMENT`

Not `NO VALID HYPOTHESIS — CLOSE ROMAN DIRECTION`: representation is the dominant ROOM mechanism and a large ENT contributor; closing the whole Roman **representation** question would ignore 15/19 ROOM stricter-skeleton gains and the attested `orld`/`slman`/`ji mil` mappings.

Not `BLOCKED`: TRAIN/DEV, R2-B0, Method D source, dictionary, and corpus gold rows were accessible; TEST was not required and not used.

---

## 25. Reproducibility Notes

| Item | Value |
| --- | --- |
| Branch / commit | `research/ultra-v2-strengthening` / `fd54ac9b65c2db93e7e16fbf0c5a40b6a6025be1` |
| Python | 3.13.9 |
| Diagnostic | `experiments/ultra_v2/phase2_roman/run_r2_c0_audit.py` (deterministic; TRAIN/DEV only; TEST refuse) |
| Inputs | listed in §4 |
| Outputs | this file; `R2_C0_REPRESENTATION_AUDIT.csv`; `artifacts/r2_c0_summary.json`; `artifacts/r2_c0_case_snippets.txt` |
| Corpus SHA-256 | `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231` (verified) |
| Dict SHA-256 | `30c3f61a64ec641abbb3acdbc7a8bcaf197f0238f1bf9e76c2c7ce8e590f86a3` (verified) |
| R2-B0 outputs | read, not rewritten |
| TEST accessed | **no** |
| Frozen files changed | **no** |
| Competitor doc IDs | from cached `roman_bm25.search` on failures only; diagnostic |
| `ENGLISH_HINT` | closed heuristic list in the diagnostic script |
| SHA-256 `run_r2_c0_audit.py` | `ee718a73ce4899e50c01ba0b755d8a1563f203c5089e3d1d93a3b47e2c1bce8f` |
| SHA-256 `R2_C0_REPRESENTATION_AUDIT.csv` | `fa8101cc0459ee828a3c9cf5932aab2fc5eeef138ac8683e82e1eb38cc14212b` |
| SHA-256 `artifacts/r2_c0_summary.json` | `f8c4c1392da963969d4bb63c3ddcfe86f7d81029065d86c7a7bca7b1dcf57142` |
| SHA-256 `artifacts/r2_b0_per_query.csv` (unchanged read) | `cc0d31c2b4bb108ea7114811cafe1da68c1f1f4a88db8dd1d4700a5dd9429509` |

Temporary helper `_r2_c0_snippets.py` was deleted after extracting headlines into `r2_c0_case_snippets.txt`.

---

## 26. Safety Confirmation

- TEST query files were not loaded, printed, or searched.
- Seal aggregate recorded from `seal.json` metadata only; TEST CSVs were not hashed in this audit.
- M0, Phase 12, PLOS, `results/**`, historical qrels, dictionary bytes, BM25 hyperparameters: unchanged.
- R2-B0 `artifacts/r2_b0_*`: not modified by this audit.
- No R2-1, R2-2, dense, hybrid, rerank, or official new retrieval method.
- No commit, reset, checkout, or push.
- Counterfactual numbers are labeled and are not official metrics.

**STOP after R2-C0.**
