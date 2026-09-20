# ULTRA — Complete Project History (external transfer)

**Document type:** read-only synthesis for an advisor with no prior v2 context  
**Written:** 2026-09-13  
**Sources:** repository reports, freeze manifests, manuscripts, and ULTRA v2 phase records  
**Not a new experiment.** Numbers below are copied from sealed reports; they were not recomputed here.  
**TEST query text:** not opened.

**Repository:** https://github.com/HashimAbbasii/Dynammic-Query-Routing-Urdu-ILS  
**PLOS snapshot branch:** `publication/plos-one-final` (HEAD of that snapshot and of `research/ultra-v2-strengthening` at freeze: `fd54ac9b`, 2026-09-06).  
**Current working branch (this write-up):** `research/ultra-v2-strengthening`. ULTRA v2 files under `experiments/ultra_v2/` exist in the working tree and were **not** part of that 6 Sep commit.

Two scientific programs share one corpus and one frozen lexical system (**M0**). They must not be averaged.

1. **Original / PLOS thread (through Phase 12, ~August–early September 2026):** freeze script-aware BM25 (M0) and report three *different* evaluations.  
2. **ULTRA v2 (September 2026, TRAIN/DEV only):** a new unseen-query benchmark plus controlled attempts to strengthen **Roman** retrieval, without rewriting PLOS numbers or opening v2 TEST.

---

## 1. Timeline

Folder numbers are **not** chronological. The table follows the order work actually happened, as dated in reports and git.

| When (approx.) | Name | What it tested | Key result | Status | Where it lives |
| --- | --- | --- | --- | --- | --- |
| Mid–late Aug 2026 | Dual-index SVM “Layer A” | SVM SHORT/LONG routing into MiniLM **headline** vs **full-article** indexes | Held-out trap **classification** SVM 60% vs word-count 20%; **retrieval P@5** SVM **33.00%** vs word-count **36.50%** (SVM lost P@5) | **Superseded** as official retriever; kept as historical Layer A | `archive/historical_experiments/` (`phase0_baseline`, `validate/dual_index_routing`, MiniLM/Chroma) |
| ~23 Aug 2026 | Phase 0 freeze + Phase 1 forensic | Diagnose why SVM beats protocol labels but loses P@5 | Protocol gold ≠ retrieval-optimal index on 20/40 traps; cue-short queries hurt when sent LONG | Diagnostic, closed | `archive/historical_experiments/phase0_baseline`, `phase1_forensic` |
| ~24 Aug 2026 | Phase 2 oracle pool | New **known-item** QTRN queries (n=260 split train/dev/internal_val) labeled by which MiniLM index ranks the **source article** higher | Created the n=78 dev+internal_val pool later used for M0; H001–H040 unused | **Retained** (query pool + Method D char table) | `experiments/phase2_oracle/` |
| ~24 Aug 2026 | Phase 3 dense (historical) | Truncated full-article MiniLM vs headline MiniLM on n=78 | Headline Hit@5 **0.4487** > old full **0.2564** | Abandoned as official path | `archive/historical_experiments/phase3_retrieval/` |
| 24 Aug 2026 | Phase 4A chunk ANN | Whole-corpus chunk HNSW (MiniLM, 96/32 tokens) vs truncated full index | Chunk Hit@5 **0.2821** vs old full 0.2564 vs headline **0.4487**. Headline still stronger. **Not adopted** | Closed / not M0 | `experiments/phase4_chunk_ann/` |
| ~25 Aug 2026 | Phase 4B benchmark (historical) | BM25 vs dense on n=78; Roman subset | Urdu BM25 strong on title-copy Urdu; Roman BM25 **0/23**, dense **~1/23** | Evidence that led to Phase 5 | `archive/historical_experiments/phase4b_retrieval_benchmark/` |
| ~25–26 Aug 2026 | Phase 5 Roman Urdu | Methods A–D on DEV Roman, then confirm internal_val | **Method D** selected. All-Roman Hit@5 **22/23**. Script-aware n=78 Hit@5 **68/78 = 87.18%** | **Frozen as M0 implementation** | `experiments/phase5_roman_urdu/run_phase5.py` |
| ~26 Aug 2026 | Phase 6 residual (historical) | Reproduce script-aware vs headline; fusion justification | Hit@5 0.8718 reproduced; fusion/headline oracle **not** deployed | Closed | `archive/historical_experiments/phase6_residual_diagnosis/` |
| ~26 Aug 2026 | Phase 7 human protocol (historical) | A/B/C/D/E rubric (not the later v2 Phase 7) | Protocol for later H and U labeling | Superseded by 10C / Phase 12 human folders | `archive/historical_experiments/phase7_human_relevance/` |
| **27 Aug 2026** | **Phase 8 final freeze** | Freeze M0 + evaluation protocol; do **not** score H001–H040 here | Manifest + hashes; official system named M0 | **Frozen (PLOS/M0)** | `experiments/phase8_final_freeze/` |
| ~27 Aug 2026 | Phase 9 held-out | One-shot M0 on H001–H040 | ExactSource Hit@5 **undefined** (no `source_doc_id`). Top-50 lists produced | Frozen diagnostic | `experiments/phase9_heldout_evaluation/` |
| ~27–28 Aug 2026 | Phase 10B dump + 10C labels | Human A–E on frozen H Top-5 | Success@5 **25/40 = 62.50%**. Set **burned** for tuning | Diagnostic only | `experiments/phase10c_human_relevance/`; dump in `archive/.../phase10b_frozen_dump/` |
| ~28 Aug 2026 | Phase 11 M0–M4 | Query-side ROMAN expansions vs M0 on n=78 | All **68/78**. **M0 not replaced** | Frozen (negative ablation) | `experiments/phase11_improvement/`, `phase11_improvement_design/` |
| Late Aug 2026 | Phase 12 K/U | New sealed known-item K and naturalistic U | K ExactSource Hit@5 **27/40 = 67.50%**; U Success@5 (A1) **23/40 = 57.50%** | **Official unseen M0 tests** (burned for further M0 tuning) | `experiments/phase12_new_unseen_evaluation/`, `phase12_human_relevance/` |
| ~early Sep 2026 | Phase 12 A2 | Independent labels on same U Top-5 | A2 Success@5 **26/40 = 65%**; five-way κ **0.5490**; binary κ **0.6816**. Does **not** replace 23/40 | Reliability only | `experiments/phase12_independent_annotation/` |
| 29 Aug–6 Sep 2026 | Cleanup + publication audit | Organize files; corpus SHA/provenance | Corpus SHA verified locally; public reconstruct **partial** | Infrastructure | `CLEANUP_FINAL_REPORT.md`, `experiments/publication_audit/`, `docs/` |
| 6 Sep 2026 | PLOS / IEEE M0 manuscripts | Paper packaging on `publication/plos-one-final` | Official M0 numbers in LaTeX; Editorial Manager checklist | **Submission snapshot in repo; no DOI/acceptance found** | `Papers/PLOS_ONE/`, `Papers/IEEE/` |
| ~9–13 Sep 2026 | **ULTRA v2** Phases 0–8 | New TRAIN/DEV/TEST benchmark; Roman KN n=51 methods | See §5. TEST **never retrieved**. None of these replace 87.18% / 67.5% / 57.5% | **Active research; not in the 6 Sep freeze commit** | `experiments/ultra_v2/` |

`experiments/post_phase12_development/` contains empty subdirectory shells (`artifacts/`, `m3e_evaluation/`, `module1/`, `module2/`) and **no scientific reports**. Treat as unused.

---

## 2. Original / PLOS thread — how M0 was built and frozen

### 2.1 Starting point: dual-index SVM (not M0)

The original thesis direction was **adaptive query routing** between two **MiniLM** rooms:

- Headline embeddings (`paraphrase-multilingual-MiniLM-L12-v2`)
- Full-article Chroma index (same encoder, truncated long documents)

An SVM classified queries SHORT vs LONG (later with confidence “lights”). Protocol labels on **H001–H040** (“trap” queries) rewarded beating a word-count baseline.

**What the forensic freeze showed** (`archive/historical_experiments/phase0_baseline/FROZEN_BASELINE.md`):

| Layer | SVM | Word-count / other |
| --- | --- | --- |
| Phase 3B V2 classification (n=50) | 86% | 84% |
| Held-out trap classification (n=40) | **60%** | 20% (word count); θ=150 never fired LONG |
| Held-out dual-index **P@5** (400 judgments) | **33.00%** | **36.50%** word count; always-headline 35.00% |

The router could match protocol labels and still **hurt retrieval**. That killed “SVM accuracy” as the official IR claim. Older drafts quoting **~90% P@15** or **100% routing** are Layer A / Clause-1 text, **not** frozen M0.

### 2.2 New known-item pool (Phase 2 oracle)

`experiments/phase2_oracle/` built **260** title/lead-derived queries (`QTRN_*`) from unused corpus rows, with a designated `source_doc_id`. MiniLM headline vs full nDCG@5 produced HEADLINE/FULL/MIXED **oracle route** labels for a possible future router. Splits: train 182 / dev 39 / internal_val 39. **H001–H040 untouched.**

This pool later became the **development/validation** set for lexical M0: **dev + internal_val = n=78**.

The Method D character table `_CHAR_ROMAN` still lives in `run_phase2_pipeline.py` and is copied into `run_phase5.py`.

### 2.3 Dense/chunking did not beat title MiniLM

Phase 4A (`experiments/phase4_chunk_ann/`, 24 Aug 2026): 644,100 chunks, MiniLM max 128 tokens, chunks 96/overlap 32. On n=78:

| System | Hit@5 |
| --- | ---: |
| Headline MiniLM | **0.4487** |
| Chunk ANN | 0.2821 |
| Old truncated full | 0.2564 |

Chunking helped truncated-full slightly and lost badly to headlines. **Not the official system.**

### 2.4 Roman Urdu was the wall; Method D became M0

Phase 4B/5: on the 23 Roman `QTRN` strings (these are **`title_roman`**, dictionary reverse + character romanization, **not** chat Roman):

- Method A (raw Urdu BM25): **0/23**
- Headline MiniLM: **1/23**
- Method B (query-side 198-key dict): still ~0 on DEV
- Method C (rule transliteration to Urdu BM25): DEV 13/13 Hit@5 but weaker nDCG and 6/10 on internal_val (post-hoc)
- **Method D** (romanize **documents**, search Roman queries as typed): DEV **13/13**, internal_val **9/10** → **22/23** overall

Selected **before** internal_val interpretation: Method D (`artifacts/selected_method.json`).

**Deployed routing (M0):**

- Detector: Unicode counts → `URDU` / `ROMAN` / `MIXED` / `OTHER` (`detect_script` in `run_phase5.py`; 78/78 agreement on n=78 oracle script tags)
- URDU / MIXED / OTHER → Urdu-script Okapi BM25  
- ROMAN → Method D romanized-document BM25  
- \(k_1=1.5\), \(b=0.75\), retrieve 50, official cutoff **5**

**Development/validation headline (same n=78):**

| Metric | Value |
| --- | --- |
| ExactSource Hit@5 | **68/78 = 87.18%** |
| P@5 | 0.1744 (= 0.2 × Hit@5, because known-item P@5 is 0 or 0.2) |
| nDCG@5 | 0.8107 |
| MRR | 0.797 |
| Raw Urdu BM25 (no Roman path) | Hit@5 **0.5897** |
| Urdu-script subset | Hit@5 **0.913** (n=46) |
| Mixed subset | Hit@5 **0.4444** (n=9) |

This **87.18% is the PLOS/M0 development known-item number**. It is **not** unpublished-only: it is Table-1-style official development performance. It is **not** unseen chat accuracy.

Corpus: `data/clean_articles.csv`, n=111,860, SHA-256 `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231`.  
Dictionary: `models/roman_urdu_dict_expanded.json`, 198 keys, SHA-256 `30c3f61a64ec641abbb3acdbc7a8bcaf197f0238f1bf9e76c2c7ce8e590f86a3`.

### 2.5 Phase 8 freeze (27 Aug 2026)

`experiments/phase8_final_freeze/FINAL_SYSTEM_MANIFEST.json` (`phase8-freeze-2026-08-27`):

- System name: ULTRA script-aware lexical retrieval  
- SVM: **false**  
- Do not change k1, b, tokenizer, detector, Method D, routing table, corpus, dictionary keys, primary metric  
- Tokenizer: `[\u0600-\u06FF]+|[A-Za-z0-9]+`, lowercase, no stemming/stopwords  

This freeze **did not** open H001–H040.

### 2.6 Phase 9: H001–H040 cannot yield ExactSource Hit@5

H001–H040 are routing-trap strings with **no** `source_doc_id`. Phase 9 ran frozen M0 once, produced Top-50 lists, and correctly reported ExactSource Hit@5 as **not defined** (n_scored = 0). That is not a Hit@5 of 0%.

### 2.7 Phase 10C: human usefulness on H (diagnostic)

Labels on the frozen H Top-5 (196 documents: 38×5 + H027×5 + H036×1). Success@5 = at least one A or B in Top-5:

- **25/40 = 62.50%**  
- Conservative P@5 = **0.1250** (also variable-denominator P@5 = 0.1250)  
- All-D queries: **10/40**  
- Label counts: A 25, B 42, C 45, D 84, E 0  
- Qrels: `experiments/phase10c_human_relevance/HELD_OUT_QRELS.csv`  
- `PHASE10C_RESULTS.md` conclusion: diagnostic only; **not** ExactSource; **not** a system change; H set **burned**

**Must not** be sold as the official unseen human result (queries were already seen; they were traps). Phase 12 **U** replaces that role.

### 2.8 Phase 11: M1–M4 did not beat 68/78

Query-side ROMAN expansions only (dictionary file **not** edited; H001–H040 not loaded):

| Model | What | n=78 Hit@5 | Roman-train Hit@5 |
| --- | --- | --- | --- |
| M0 | Frozen control | 68/78 | 61/64 = 95.31% |
| M1 | Spelling/chat variants (kya/kiya, nahi, …) | 68/78 | 61/64 |
| M2 | Small bilingual synonyms (win/jeet, …) | 68/78 | 61/64 |
| M3 | Roman function-word stoplist | 68/78 | 61/64 |
| M4 | M2+M3 | 68/78 | 61/64 |

M1–M4 nDCG@5/MRR on Roman-train slightly **below** M0. **M0 remains official.**

### 2.9 Phase 12: genuine unseen sets for *this* M0

New queries sealed **before** retrieval. Not QTRN, not H.

**K001–K040** (known-item, new headlines):

| Metric | Result |
| --- | --- |
| Hit@1 | 20/40 = 50.00% |
| Hit@5 (primary) | **27/40 = 67.50%** |
| Hit@10 | 28/40 = 70.00% |
| Hit@50 | 30/40 = 75.00% |
| Detector split (descriptive) | Urdu titles **26/28**; ordinary Roman titles **1/12** |

The drop 87.18% → 67.50% is concentrated on **ordinary Roman titles**, not Urdu BM25. Development Roman was `title_roman`; K Roman is naturalistic romanization of headlines.

**U001–U040** (naturalistic, **no** source id; Annotator 1 official):

| Metric | Result |
| --- | --- |
| Success@5 (A or B in Top-5) | **23/40 = 57.50%** |
| Conservative P@5 | 0.2050 |
| nDCG@5 | 0.6460 (C has gain 1; can overstate usefulness) |
| MRR | 0.4542 |
| Script split Success@5 | URDU **17/18**; ROMAN **6/18**; MIXED **0/4** (n=4 descriptive) |

**Annotator 2** (same frozen Top-5, independent): Success@5 **26/40 = 65.00%**; five-way raw agreement 135/200 = 67.50%; Cohen’s κ five-way **0.5490** (moderate); binary A/B vs not κ **0.6816** (substantial). Official U remains **23/40**.

After Phase 12, K/U/H are **burned** for retuning M0, Method D, or the dictionary.

### 2.10 Exact frozen / “published” headline numbers

The PLOS manuscript’s scientific freeze is these **three** numbers, **not averaged**:

1. Development/validation ExactSource Hit@5 = **68/78 = 87.18%**  
2. Sealed known-item K ExactSource Hit@5 = **27/40 = 67.50%**  
3. Sealed naturalistic U Success@5 (A1) = **23/40 = 57.50%**

**87.18% is the frozen M0 development result** and is what people mean by “the 87.18% Hit@5.” It is **not** a published journal DOI in this repository (see §6). It **is** the official PLOS Table-1 development cell.

Honest one-line thesis claim (from `docs/FINAL_EXPERIMENTAL_RESULTS_ANALYSIS.md`): **Urdu-script news search under M0 is strong; ordinary Roman Urdu remains the main failure mode.**

---

## 3. Relationship between PLOS/M0 and ULTRA v2

**Repo evidence, not speculation:**

| Question | What the repo says |
| --- | --- |
| Does v2 **replace** M0 in the PLOS paper? | **No.** `experiments/ultra_v2/README.md`: this folder “does **not** replace the frozen PLOS ONE M0 study.” PLOS numbers “stay historical” (`PROTOCOL.md`). |
| Does v2 **rewrite** 87.18% / 67.5% / 57.5%? | **No.** v2 runners refuse TEST and treat M0 `run_phase5.py` as read-only. |
| Is v2 meant to **improve** M0? | **Yes, as a later research program**, specifically Roman / cross-script candidate generation on a **new** benchmark. Objective (`PROTOCOL.md`): show that any improvement over frozen M0 **survives genuinely unseen evaluation**. |
| Why not reuse K/U as v2 TEST? | K/U were sealed, retrieved, labeled, sliced by script, and put in the PLOS trail. Using them to invent v2 rules would be leakage. Phase 12 already said: if the system changes, K/U are burned. |
| Has v2 been evaluated on its sealed TEST? | **No.** `benchmark/test/` exists with `seal.json` only; query CSVs must not be opened. All v2 scores so far are Roman KN **TRAIN+DEV n=51**. |
| Is v2 a second paper yet? | **Not declared as submitted.** It is a strengthening branch (`research/ultra-v2-strengthening`) with controlled experiments. No v2 manuscript folder parallel to `Papers/PLOS_ONE/`. |
| Git | `publication/plos-one-final` and `research/ultra-v2-strengthening` both pointed at `fd54ac9` on 6 Sep 2026. Subsequent v2 phase directories are **uncommitted working-tree research**, not the PLOS snapshot. |

**One sentence:** ULTRA v2 is an **extension program** to attack M0’s documented Roman failure on a **fresh** TRAIN/DEV/TEST split; it is **not** a replacement of the PLOS freeze and **not** allowed to tune on K/U/H.

---

## 4. Numbers and targets that appear in `docs/`, `results/`, and root guides

Official **results** (copy these; do not average):

| Number | Meaning | Source |
| --- | --- | --- |
| 68/78 = 87.18% | Dev/val ExactSource Hit@5 (QTRN n=78) | `results/FINAL_RESULTS.md`, `docs/PROJECT_STATUS.md`, `docs/FINAL_EXPERIMENTAL_RESULTS_ANALYSIS.md` |
| 0.5897 | Same pool, Urdu BM25 without Roman path | `results/DEVELOPMENT_VALIDATION.md` |
| 0/23 ; 22/23 | Roman subset Method A vs Method D | same |
| 61/64 = 95.31% | Phase 11 Roman-train Hit@5 (all of M0–M4) | `results/PHASE11_ABLATION.md` |
| 27/40 = 67.50% | K ExactSource Hit@5 | `results/PHASE12_RESULTS.md` |
| 20/40, 28/40, 30/40 | K Hit@1 / @10 / @50 | same |
| 26/28 vs 1/12 | K Urdu vs Roman titles Hit@5 | same |
| 23/40 = 57.50% | U Success@5 Annotator 1 | same |
| 0.2050 ; 0.6460 ; 0.4542 | U P@5, nDCG@5, MRR | same |
| 17/18, 6/18, 0/4 | U Success@5 URDU / ROMAN / MIXED | same |
| 25/40 = 62.50% | H001–H040 Success@5 (diagnostic) | `docs/PROJECT_STATUS.md`, `docs/FINAL_EXPERIMENTAL_RESULTS_ANALYSIS.md` |
| 26/40 = 65.00% | U Success@5 Annotator 2 (not official) | `REPRODUCE.md`, `experiments/phase12_independent_annotation/AGREEMENT.md` |
| 135/200 = 67.50% | A1–A2 five-way raw agreement | `AGREEMENT.md` |
| 169/200 = 84.50% | A1–A2 binary (A/B vs not) raw agreement | `AGREEMENT.md` |
| κ 0.5490 / 0.6816 | Five-way / binary Cohen’s κ | `AGREEMENT.md` |
| 17/18 = 94.44%; 6/18 = 33.33%; 0/4 = 0% | U Success@5 by script | `docs/FINAL_EXPERIMENTAL_RESULTS_ANALYSIS.md` |
| 0.1744; 0.8107; 0.797 | n=78 P@5, nDCG@5, MRR | `experiments/phase8_final_freeze/DEVELOPMENT_RESULTS.md`, `REPRODUCE.md` |
| 0.4487; 0.2564; 0.2821 | Headline MiniLM / truncated full / chunk ANN Hit@5 on n=78 | same |
| 0.9103 | Headline + script-aware **oracle** Hit@5 (not deployed) | same |
| 78/78 | Unicode detector vs oracle script tags | same |
| 111,860 | Corpus size | freeze manifest |
| SHA `8992a6acca…97a9f231` | Frozen `clean_articles.csv` | freeze / `docs/REPRODUCIBILITY.md` / `REPRODUCE.md` |
| SHA `30c3f61a64…90f86a3` | 198-key dictionary | same |
| SHA `7662b6e850…7926062` | Local precursor CSV (optional check) | `REPRODUCE.md` |
| DOI 10.17632/834vsxnb99.3 | Mendeley Urdu News Dataset 1M V3 | `REPRODUCE.md` |
| 19.7 points | Drop 87.18% → 67.50% (K) | `docs/FINAL_EXPERIMENTAL_RESULTS_ANALYSIS.md` |
| “mid-40s to low-70s” | Informal 95% binomial interval around 23/40 | same |

**Aspirations / forbidden claims** (appear in the same docs as warnings, **not** as achieved results):

| Phrase | Context | Source |
| --- | --- | --- |
| ~80% usefulness / “the system achieved ~80%” | Explicitly **rejected** as a claim | `docs/FINAL_EXPERIMENTAL_RESULTS_ANALYSIS.md`, `results/PHASE12_RESULTS.md`, `experiments/phase12_new_unseen_evaluation/PHASE12_SEALED_PROTOCOL.md` |
| 87.18% as unseen or real-world accuracy | Forbidden | `docs/FINAL_EXPERIMENTAL_RESULTS_ANALYSIS.md` |
| Average 87.18% with 57.5% | Forbidden | same |
| 90% ExactSource Hit@5 on n=78 | Phase 8 future-work forbids chasing this | `experiments/phase8_final_freeze/FUTURE_WORK.md` |
| ~90% P@15, 100% routing | Historical Layer A / Clause-1 drafts, **not M0** | `docs/PROJECT_STATUS.md`, `Thesis_template/FINAL/ULTRA_THESIS_SUBMISSION_DRAFT.md` |
| 80% as v2 pass/fail | `PROTOCOL.md`: aspiration, **not** a hypothesis test | `experiments/ultra_v2/PROTOCOL.md` |
| Clopper–Pearson 77.68–93.68% | 95% CI on 68/78 (manuscript, not a new experiment) | `experiments/publication_audit/MANUSCRIPT_NUMBERS_AUDIT.md` |

`CLEANUP_FINAL_REPORT.md` (29 Aug 2026): file moves only; same three official metrics copied, not recomputed.

`REPRODUCE.md`: independent reproduction of **M0 only**; `research/post-phase12` exploratory work is out of official Table 1.

---

## 5. ULTRA v2 recap (Phases 2–8) — brief, already documented

Population unless noted: **Roman KN TRAIN+DEV, n=51**, ExactSource, Top-50. **TEST sealed / not accessed.** NL not scored. Corpus and dictionary SHAs identical to M0.

| Phase | Decision | Hit@1 / @5 / @10 / @50 / MRR | One-line |
| --- | --- | --- | --- |
| R2-B0 Method-D BM25 | Baseline established | 1 / 4 / 4 / 6 / 0.0375 | Frozen M0 Roman path **fails** this new Roman KN set (Hit@5 4/51 vs old QTRN Roman 22/23). |
| R2-1 fallback romanizer | NOT SUPPORTED | Hit@50 6→6; ROOM Cat1 0/11 | Document-side Hunterian fallback closed. |
| R2-NG3 (char 3-grams) | PARTIALLY SUPPORTED | 3 / 6 / 6 / 8 / 0.075 | Recovers KN050 (rank 1), KN035 (rank 5); 2 dual-miss golds. |
| Phase 3 Dense e5-small | PARTIALLY SUPPORTED | **5 / 15 / 16 / 22 / 0.1726** | Best first-stage overall; lost all 4 BM25 Hit@5 successes. |
| Phase 4 Hybrid RRF k=60 | PARTIALLY SUPPORTED | 3 / 11 / **19 / 25** / 0.1422 | Restores BM25 Top-50 hits; worse than dense on Hit@5/MRR. Dual-miss n=25. |
| Phase 5 NG3 repro | PARTIALLY SUPPORTED | same as R2-NG3 | Gated match to Phase 2 NG3; NG3 recovers 2/25 dual-miss. |
| Phase 6 diagnostics | Analysis only | McNemar BM25 vs Dense Hit@5 p=0.019211; Hit@50 p=0.001544. Hybrid vs dense n.s. Union BM25∪Dense∪NG3 vs 2-way Hybrid Hit@5 p=0.006348, Hit@50 p=0.25 | 23 remaining four-way misses; routing **51/51 ROMAN**; ~9.6% docs >512 whitespace tokens (Phase 3 **truncated**, did not chunk). |
| Phase 7 letter-name | UNSUPPORTED | 0 / 0 / 0 / 1 / 0.0007 | 0/23 recovered; destroyed 5/6 BM25 Top-50 hits. |
| Phase 8 3-way RRF k=60 | UNSUPPORTED | 4 / **8** / 14 / 24 / 0.131 | Worse than 2-way Hybrid on Hit@5 (11→8). Union statistic ≠ better ranked list. KN035/KN050 stay in Top-50 at **worse** ranks than NG3 alone. 0/23 of remaining misses. |

ROOM Category 1 (n=11): BM25 0/11; Dense/Hybrid 3/11; NG3 1/11 (KN050); Phase 8 3/11 (KN001, KN011, KN050 — swapped out KN045).

**v2 has not beaten “M0 on PLOS metrics”** because it is not scoring QTRN/K/U. On its **own** Roman KN TRAIN/DEV, Method D is weak; dense is the strongest single retriever so far; unweighted fusion and letter-name expansion have not solved the remaining misses.

---

## 6. Papers and manuscripts in the repository

| Item | Path | Apparent status (repo evidence only) |
| --- | --- | --- |
| **PLOS ONE M0 paper** | `Papers/PLOS_ONE/Adaptive_dynamic_query_routing_for_Urdu_information_retrieval.tex` | Printed title: **“Script-aware BM25 retrieval for Urdu and Roman Urdu news search.”** Official frozen system M0. Editorial Manager checklist dated **6 Sep 2026**; submission ZIP under `Papers/PLOS_ONE/SUBMISSION_PACKAGE_FINAL/`. Branch `publication/plos-one-final`. **No DOI, acceptance letter, or “published” stamp found.** Treat as **submission-ready / submitted snapshot**, not as a published article, unless you have portal status outside this repo. |
| PLOS figures / SI | `Papers/PLOS_ONE/figures/`, `supporting_information/` | Packaged for upload (Fig1–Fig5 TIFF + SI tables). |
| **IEEE-style M0 paper** | `Papers/IEEE/FINAL/main.tex` | Title: **“Script-Aware BM25 for Urdu News Search: Known-Item Recovery, Sealed Generalization, and Human Usefulness.”** Same three official metrics. ZIP: `Papers/IEEE/SUBMISSION_PACKAGE/ULTRA_IEEE_M0_FINAL_SUBMISSION.zip`. **Separate venue packaging of M0, not a different system.** No IEEE acceptance evidence in-repo. |
| Historical MiniLM IEEE draft | `archive/historical_papers/IEEE_MiniLM/` | Dual-index SVM/MiniLM conference draft. **Not** the official M0 headline. |
| Historical PLOS Word / old zips | `archive/historical_papers/` | Clause-1 / MiniLM-era text (100% routing, ~90% P@15). Do not quote as M0. |
| **AU master’s thesis (Word)** | `Thesis_template/FINAL/Hashim_Shazad_243259_AU_Thesis_ULTRA.docx` | Live thesis file (cleanup also mentions copies under `Thesis_Paper/Air_Thesis_Formate/`). Markdown companion: `ULTRA_THESIS_SUBMISSION_DRAFT.md`. Status: scientific content aligned with frozen M0; historical SVM/P@15 sections still labeled Layer A; TOC may need Word refresh. |
| Thesis markdown draft | `Thesis_template/FINAL/ULTRA_THESIS_SUBMISSION_DRAFT.md` | Source for honest M0 claims; forbids 80% unseen and 87.18% as real-world accuracy. |
| ULTRA v2 | no manuscript yet | Experiment reports only under `experiments/ultra_v2/`. |

Authors on the PLOS/IEEE M0 papers (from the tex): **Hashim Shazad**, **Adnan Aslam**; PLOS CRediT also names **Areena Rahman** for independent A2 labels.

---

## 7. Publication audit (what was checked)

`experiments/publication_audit/` (6 Sep 2026, on the PLOS branch):

- Local corpus SHA **PASS** (gitignored; not on GitHub).  
- Provenance **PARTIAL** (Kaggle/Mendeley Urdu News Dataset 1M, DOI 10.17632/834vsxnb99.3; byte identity vs a fresh download not verified).  
- 111,861 → 111,860 explained as dropping one truncated last record (`dropna`), not dedup.  
- Tools: `verify_corpus_hash.py`, reconstruct notes.  
- Independent A2 kappas recorded; official U stays 23/40.

---

## 8. What an advisor should remember

1. **Official published-study system is M0**, a Unicode script router plus two BM25 indexes — **not** the SVM/MiniLM dual-index thesis Layer A.  
2. **Three M0 numbers, three questions:** 87.18% (dev known-item), 67.50% (new known-item K), 57.50% (new human U). Mixing them is a scientific error.  
3. **Roman Urdu is the failure mode** on independent tests (K 1/12, U 6/18). Development 22/23 Roman used `title_roman`, which overfits Method D’s own romanizer.  
4. **ULTRA v2** is a new TRAIN/DEV/TEST program to try to fix that Roman gap **without** touching PLOS artifacts or v2 TEST. So far, on 51 new Roman KN queries, Method D collapses; dense helps partially; NG3 helps two dual-misses; letter-name and 3-way RRF do not beat 2-way hybrid as rankers.  
5. **Nothing in this repo documents a journal acceptance.** PLOS and IEEE M0 PDFs/ZIPs are submission packages.

---

## 9. Pointers (do not open v2 TEST CSVs)

| Need | Read |
| --- | --- |
| M0 one-pager | `results/FINAL_RESULTS.md` |
| How not to over-claim | `docs/FINAL_EXPERIMENTAL_RESULTS_ANALYSIS.md` |
| Freeze hashes | `experiments/phase8_final_freeze/FINAL_SYSTEM_MANIFEST.json` |
| M0 code | `experiments/phase5_roman_urdu/run_phase5.py` |
| Reproduce M0 | `REPRODUCE.md` |
| v2 protocol | `experiments/ultra_v2/PROTOCOL.md` |
| v2 Phase 8 decision | `experiments/ultra_v2/phase8_3way_fusion/PHASE8_CONTROLLED_EXPERIMENT.md` |
