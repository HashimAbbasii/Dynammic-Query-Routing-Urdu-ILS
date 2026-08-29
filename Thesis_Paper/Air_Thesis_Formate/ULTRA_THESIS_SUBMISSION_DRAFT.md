# Adaptive Dynamic Query Routing for Urdu Information Retrieval

**Hashim Shazad (243259)**  
M.S. Artificial Intelligence, Air University, Islamabad  
Supervisor: Dr. Adnan Aslam  
2026

**Status:** Submission-ready *scientific content* for the Air University thesis. Paste into `Hashim_Shazad_243259_AU_Thesis_ULTRA.docx` (certificates, TOC fields, and AU front-matter stay in Word). Do not run new experiments. Do not quote Clause-1 PLOS 100% routing or ~90% P@15 as frozen M0 retrieval results.

**Official frozen retrieval system:** M0 (Unicode script detector; URDU/MIXED → Urdu BM25; ROMAN → Method D romanized-document BM25). Corpus: 111,860 articles. Dictionary: 198 keys.

---

## How this draft maps onto the AU six-chapter structure

| Required topic | AU location in this draft |
| --- | --- |
| Abstract | Abstract |
| Introduction, problem, RQs, objectives | Chapter 1 |
| Literature review | Chapter 2 |
| Methodology, architecture, routing, Roman Urdu, setup, protocol | Chapters 3–4 |
| Results, discussion, error analysis | Chapter 5 |
| Limitations, conclusion, future work | Chapter 6 |
| References | References |

**Two evaluation layers (do not mix).**  
Layer A (historical): SVM SHORT/LONG routing and MiniLM dual-index pilots.  
Layer B (official IR): frozen M0 ExactSource Hit@5 and human Success@5.

---

## Abstract

Urdu news search is difficult because users type both Perso-Arabic Urdu and informal Roman Urdu, while many systems still apply one retrieval path to every query. This thesis extends the ULTRA news-retrieval setting with *adaptive dynamic query routing*: a script-aware switch that sends native-script and mixed-script queries to an Urdu BM25 index and Roman queries to a Method D romanized-document BM25 index. The official frozen system is called M0. It was not changed after the freeze, and query-side variants M1–M4 did not improve the primary known-item score.

The frozen ULTRA system achieved an ExactSource Hit@5 of **87.18% (68/78)** on the Phase 2 development/validation known-item evaluation set. That figure is genuine for title-derived known-item search on that pool. It is not real-world accuracy, not human usefulness, and not unseen natural-query performance.

Independent Phase 12 evaluation of the same frozen system produced two further results that must be reported separately. On a new sealed known-item set (K001–K040), ExactSource Hit@5 was **67.50% (27/40)**. On a new sealed naturalistic set (U001–U040), human Success@5 was **57.50% (23/40)**, with conservative P@5 = 0.2050, nDCG@5 = 0.6460, and MRR = 0.4542. Success@5 is a human-relevance metric, not ExactSource Hit@5.

These three numbers must not be averaged. They show strong controlled known-item retrieval, a drop on independently sampled known-item queries, and a further gap on realistic user needs. In the U sample, Urdu-script queries succeeded in 17/18 cases, Roman queries in 6/18, and mixed-script queries in 0/4. The contribution is therefore a frozen, reproducible Urdu IR framework with an explicitly measured Roman/mixed limitation—not a claim of 87% or 80% unseen usefulness.

---

# Chapter 1: Introduction

## 1.1 Background

Urdu is written in a cursive Perso-Arabic script, but many users search in Roman Urdu: Urdu words typed with Latin letters and inconsistent spelling. A news retriever that indexes only native-script text will miss those queries even when the right article is in the collection. The ULTRA framework (Bashir, Qaiser, and Hussain, 2026) provides a dual-embedding Urdu news architecture and a large news corpus. Its original switch is a static character-length threshold (θ = 150). Length is easy to code and easy to fool: a short “why” question may need the full article, and a long factoid may be answered by a headline.

This thesis started from that routing problem and then asked a stricter retrieval question: after the system is frozen, how often does it recover a known news article, and how often is the Top-5 actually useful to a person? The official answer uses lexical retrieval (BM25) with a script detector, not a claim that an SVM or a MiniLM dual-index solved Urdu search.

## 1.2 Problem Statement

The practical problem is bilingual/script-mixed Urdu news search over a fixed corpus of 111,860 articles. Users issue:

- native-script Urdu queries,
- Roman Urdu queries with non-standard spelling,
- occasional mixed-script queries.

A single Urdu-text BM25 index is a poor match for Roman queries (development Roman known-item Hit@5 was 0/23 without a Roman path). A static length threshold does not decide which *script index* to open. Learned SHORT/LONG routing can be studied as a separate classification task, but classification accuracy is not the same as finding the right news article.

The scientific problem is therefore: **specify a frozen retrieval system, evaluate known-item recovery under a defined protocol, then evaluate generalization on new known-item queries and naturalistic human usefulness—without mixing those metrics.**

## 1.3 Motivation

Urdu IR still has fewer shared, honestly reported end-to-end evaluations than English. Overstating a development known-item score as “real-world accuracy” would make the field worse, not better. This thesis is motivated by two complementary needs:

1. A deployable, inspectable retriever (BM25 + a 198-key dictionary + Unicode routing) that can be frozen and hashed.
2. An evaluation design that separates development known-item search from new known-item search and from human usefulness.

## 1.4 Research Gap

Prior Urdu resources (CURE; Urdu MS MARCO) and ULTRA address collections and embeddings more than *script-conditional lexical routing* with a sealed, multi-layer evaluation. English query routing (sparse vs dense; complexity-aware RAG) does not handle Roman Urdu. Roman Urdu work is mostly classification (sentiment, offensive language), not news retrieval. This thesis fills that gap with a frozen M0 system and three non-averaged evaluation layers.

## 1.5 Research Questions

**RQ1.** Can a script-aware lexical pipeline (Urdu BM25 + Method D) recover known news articles from title-derived queries on a development/validation pool?

**RQ2.** Does that known-item score transfer to a new sealed known-item sample written independently of the freeze set?

**RQ3.** How often is frozen M0 *useful* (at least one relevant or partially relevant document in the Top-5) on new naturalistic queries with no gold article?

**RQ4.** Do query-side Roman expansions (M1–M4) improve the official n=78 ExactSource Hit@5 enough to replace M0?

**RQ5 (historical Layer A).** Can a lightweight SVM predict SHORT vs LONG better than ULTRA’s θ = 150 on development data, and does that routing decision improve MiniLM dual-index P@5? (Answered as a separate study; not the official M0 headline.)

## 1.6 Objectives

1. Freeze an official retrieval system (M0) with documented hashes, routing rules, and BM25 parameters.
2. Report ExactSource Hit@5 on Phase 2 development/validation known-item queries (n=78).
3. Report ExactSource Hit@5 on sealed K001–K040 without using those queries for tuning.
4. Report human Success@5, P@5, nDCG@5, and MRR on sealed U001–U040 without using those queries for tuning.
5. Report the Phase 11 M0–M4 ablation and keep M0 official if Hit@5 does not improve.
6. State limitations, especially Roman and mixed-script performance, without hiding weaker Phase 12 numbers.

## 1.7 Contributions

1. A frozen script-aware BM25 architecture (M0) with Unicode routing and Method D for Roman documents.
2. A development/validation known-item result: ExactSource Hit@5 = 68/78 = 87.18%.
3. An independent sealed known-item result: ExactSource Hit@5 = 27/40 = 67.50% (also Hit@1 = 50.00%, Hit@10 = 70.00%, Hit@50 = 75.00%).
4. An independent sealed human-usefulness result: Success@5 = 23/40 = 57.50% (P@5 = 0.2050; nDCG@5 = 0.6460; MRR = 0.4542).
5. A descriptive script finding on U: Urdu 17/18, Roman 6/18, Mixed 0/4.
6. Evidence that M1–M4 did not improve n=78 Hit@5, so M0 remains official.
7. Historical SVM routing experiments (Layer A), kept distinct from official IR metrics.

## 1.8 Scope

Official retrieval evaluation is news-domain, offline, and English/Urdu/Roman-Urdu query text against `data/clean_articles.csv`. The thesis does not claim legal, medical, or live web search. It does not replace M0 with M1. It does not treat H001–H040 as the primary unseen test. Interactive session features and LLM generation of answers are out of scope.

## 1.9 Significance

The significance is methodological as much as numerical: a master’s IR thesis can be defensible when it reports a strong development score *and* the weaker independent tests. The practical finding is that native-script Urdu BM25 is strong on this corpus, while ordinary Roman Urdu remains the main failure mode.

## 1.10 Thesis Layout

Chapter 2 reviews Urdu NLP, Roman Urdu, low-resource retrieval, and query routing. Chapter 3 states BM25, ExactSource Hit@k, Success@5, and (briefly) the historical SVM. Chapter 4 describes M0, Method D, corpora, and the sealed protocols. Chapter 5 reports results and discussion. Chapter 6 states conclusions, limitations, and future work that does not tune on burned test sets.

---

# Chapter 2: Literature Survey

Urdu information retrieval sits at the intersection of Urdu NLP, IR evaluation, and query-adaptive routing. This chapter uses only sources already cited in the project thesis/IEEE drafts. No new publications are invented.

## 2.1 Foundations

### 2.1.1 Urdu NLP

Daud, Khan, and Che (2017) survey Urdu’s script, morphology, and resource gap relative to English. Kazi and Khoja (2025) discuss Urdu document retrieval and embeddings, focusing on representation quality rather than per-query script routing.

### 2.1.2 Roman Urdu

Roman Urdu has no standard orthography. Hussain et al. (2025) and Mehmood et al. (2020) treat Roman Urdu mainly as a *classification* problem (offensive language; sentiment). Sitaram et al. (2019) survey code-switching more broadly. None of these works freeze a news BM25 system and then measure ExactSource Hit@5 versus human Success@5 on sealed Urdu/Roman queries.

### 2.1.3 Low-resource retrieval

Wu, Ren, and Verberne (2024) show that multilingual dense retrieval can degrade for languages outside the pretraining head. Conneau et al. (2020) show that scaling multilingual pretraining helps Urdu on NLI, but a single encoder still applies one strategy to every query. Chari, MacAvaney, and Ounis (2025) discuss users of low-resource varieties being forced toward high-resource query forms—analogous to typing Roman Urdu.

### 2.1.4 Urdu IR benchmarks

Iqbal, Tahir, and Mehmood (2021) introduce CURE. Butt, Varanasi, and Neumann (2024) provide Urdu MS MARCO baselines (BM25 and fine-tuned multilingual models; reported MRR@10 = 0.247 for their best configuration). Those collections do not define the M0 freeze or the Phase 12 K/U protocol used here. Direct numerical comparison to MS MARCO MRR@10 would be misleading.

## 2.2 Retrieval and routing paradigms

Lexical methods (BM25; Robertson and Zaragoza, 2009) match terms without a neural encoder. Classical classifiers (Cortes and Vapnik, 1995) can learn a routing boundary over engineered features. Dense retrieval (Karpukhin et al., 2020; Reimers and Gurevych, 2019) matches embeddings; ULTRA uses a multilingual MiniLM backend for its original dual-embedding design. LLM-based routers (Jeong et al., 2024; Hsu and Tzeng, 2025) add latency and cost. This thesis’s *official* retriever is lexical and script-aware. The SVM router is a historical Layer A experiment, not the M0 ranker.

## 2.3 Evaluation metrics

Routing papers report classification accuracy. IR papers report P@k, nDCG@k, and MRR. This thesis uses two *different* IR questions:

- **ExactSource Hit@k:** is the pre-assigned source document in the top k? Requires `source_doc_id`.
- **Success@5:** is at least one human A (relevant) or B (partially relevant) label in the Top-5? Used when there is no gold document.

nDCG@5 with a positive gain for topical-but-not-useful documents (label C) can look high even when Success@5 fails. This thesis therefore treats nDCG as secondary.

## 2.4 Prior routing work and ULTRA

Carmel and Yom-Tov (2010) survey query-difficulty prediction, which estimates failure risk for a *fixed* ranker. Arabzadeh, Yan, and Clarke (2021) learn sparse vs dense selection on English. Jeong et al. (2024) route RAG by predicted complexity. Bashir, Qaiser, and Hussain (2026) propose ULTRA with a length-based switch on Urdu news. The gap is a frozen Urdu/Roman *lexical* router evaluated with known-item *and* naturalistic human labels, without averaging those scores.

## 2.5 Gap summary

No reviewed Urdu system reports the three-layer protocol used here (development known-item, new known-item, new human usefulness) under a hashed freeze. That is the evaluation gap this thesis addresses.

---

# Chapter 3: Mathematical Formulation

## 3.1 Official routing: Unicode script detection

For a query string \(q\), let \(n_U\) be the number of characters in the Arabic/Urdu block U+0600–U+06FF and \(n_L\) the number of ASCII letters. Then:

- URDU if \(n_U > 0\) and \(n_L = 0\),
- ROMAN if \(n_L > 0\) and \(n_U = 0\),
- MIXED if \(n_U > 0\) and \(n_L > 0\),
- OTHER otherwise (not used as a retrieval path in M0).

M0 maps URDU and MIXED to the Urdu BM25 index and ROMAN to the Method D index. This is *adaptive dynamic query routing* in the official system: the path depends on the query’s script, not on a 150-character cutoff.

## 3.2 BM25

Documents are scored with Okapi BM25 (Robertson and Zaragoza, 2009) with frozen \(k_1 = 1.5\) and \(b = 0.75\). Let \(f(t,d)\) be term frequency of \(t\) in document \(d\), \(\mathrm{df}(t)\) document frequency, \(N\) the collection size, and \(\mathrm{avgdl}\) mean document length. M0 does not tune \(k_1\) or \(b\) on Phase 12.

## 3.3 Method D (Roman path)

Method D builds a second BM25 index over *romanized documents*. Tokens are produced with the Phase 2 character table plus the reverse of `models/roman_urdu_dict_expanded.json` (198 keys; first Latin key wins on duplicate Urdu values). The Roman *query* is tokenized as typed; it is not rewritten by M0. Method D was selected on development `title_roman` queries (Phase 5), not on chat-style Roman Urdu.

## 3.4 ExactSource Hit@k

For a query with gold document id \(s\), Hit@k = 1 if \(s\) appears in the retrieved top \(k\), else 0. The official cutoff is \(k=5\). Mean Hit@5 is the fraction of queries with Hit@5 = 1.

This metric is **undefined** if no `source_doc_id` exists (H001–H040; U001–U040).

## 3.5 Human Success@5, P@5, nDCG@5, MRR

Labels: A relevant, B partially relevant, C topically related, D not relevant, E unused in the U set (0 counts).

- Success@5 = 1 if at least one of ranks 1–5 is A or B.
- Conservative P@5 = (count of A)/5, then mean over queries.
- nDCG@5 uses gains A=3, B=2, C=1, D=E=0. C-gain inflates nDCG; do not call nDCG “usefulness.”
- MRR uses the reciprocal rank of the first A or B (0 if none).

## 3.6 Historical SVM (Layer A only)

The development SVM maps an eight-feature vector (script ratios, length, mixed flag) to SHORT/LONG with Platt confidence and HIGH/MEDIUM/LOW tiers. That mathematics remains valid as a *classifier* description. It is **not** how M0 ranks documents. MiniLM cosine search is likewise Layer A infrastructure, not the official M0 scorer.

---

# Chapter 4: Methods Developed

## 4.1 Official system architecture (M0)

```
Query
  → Unicode detector (URDU / ROMAN / MIXED)
       URDU or MIXED → BM25 on Urdu article text
       ROMAN        → BM25 on Method D romanized article text
  → Top-50 list; official reporting cutoff Top-5
```

No query rewriting. No SVM on the official path. No MiniLM on the official path. Phase 11 M1–M4 were query-side Roman expansions only; they were not deployed.

Corpus: `data/clean_articles.csv`, 111,860 documents, SHA-256 `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231`.  
Dictionary SHA-256 `30c3f61a64ec641abbb3acdbc7a8bcaf197f0238f1bf9e76c2c7ce8e590f86a3`.  
Implementation reference: `experiments/phase5_roman_urdu/run_phase5.py` (`detect_script`, BM25, Method D). Freeze record: `experiments/phase8_final_freeze/FINAL_SYSTEM_MANIFEST.json`.

## 4.2 Dataset and statistics

**Table 1. Dataset / collection statistics**

| Item | Value |
| --- | --- |
| Corpus | Urdu news articles (`clean_articles.csv`) |
| Documents | 111,860 |
| Domain | News (Sports, Business & Economics, Entertainment, Science & Technology) |
| Gold id convention | 0-based row index = `source_doc_id` |
| Development/validation known-item | Phase 2 `dev` + `internal_val`, n=78, `QTRN_*` |
| New known-item | K001–K040, n=40, sealed before retrieval |
| New naturalistic | U001–U040, n=40, no `source_doc_id` |
| Diagnostic traps | H001–H040, n=40, no `source_doc_id` |
| Phase 12 K seed | 120260827; eligible rows 111,574 after excluding 260 QTRN sources |

## 4.3 System configuration

**Table 2. Official M0 configuration**

| Component | Frozen setting |
| --- | --- |
| Detector | Unicode Urdu vs Latin letter counts |
| URDU / MIXED path | Urdu BM25, field `combined_text` |
| ROMAN path | Method D BM25, romanized documents |
| BM25 \(k_1\), \(b\) | 1.5, 0.75 |
| top_k stored | 50 |
| Official cutoff | 5 |
| Dictionary | 198 keys, not edited after freeze |
| Query-side M1–M4 | Not applied on official runs |

## 4.4 Adaptive dynamic query routing

In the official system, routing means **script-conditional index selection**. MIXED queries use the Urdu index (frozen rule). The historical SVM routed SHORT vs LONG between headline and full-article *dense* indexes; that is Layer A and is not used to produce 68/78, 27/40, or 23/40.

## 4.5 Roman Urdu / Urdu retrieval

Urdu-script queries match the native index directly. Roman queries search documents that were romanized with the same family of character mapping used to build Phase 2 `title_roman`. That is why Method D can score 22/23 on development Roman known-items and still fail on ordinary/chat Roman: the *query form* changed.

## 4.6 Experimental setup and reproducibility

Python BM25 implementation as in the Phase 5/12 runners. No GPU is required for M0. Preflight checks compared corpus and dictionary hashes before Phase 9, 11, and 12 scoring. Each official retrieval pass was specified as one-shot (no test-set tuning).

## 4.7 Evaluation protocol

**Development/validation known-item (Phase 2 n=78; reported in Phase 8/9).** Title-derived queries with `source_doc_id`. Metric: ExactSource Hit@5.

**Phase 11 ablation.** Same n=78 pool. M0 vs M1–M4 query-side Roman transforms. Primary gate: n=78 Hit@5 must not fall. H001–H040 not used.

**Phase 12 K.** Queries sealed (`queries_k.csv` SHA-256 `124e452693f98baedf510618240c154df68d56b6b7a37ed085a6512c13d13ff6`) before retrieval. Frozen M0 once. Metric: ExactSource Hit@k.

**Phase 12 U.** Queries sealed (`queries_u.csv` SHA-256 `684fd1e19eddb717f5897d869ef0ca0ed586316c5a7e1d2d23006e0748fc53b9`) before retrieval. Top-5 labeled A–E by one annotator after the dump existed. Metric: Success@5 (primary); P@5, nDCG@5, MRR (secondary).

**H001–H040.** Phase 9: ExactSource Hit@5 undefined. Phase 10C: human Success@5 = 25/40 = 62.5%, diagnostic only. Not combined with U.

---

# Chapter 5: Results and Discussion

Layer A (SVM accuracy, development P@15, Phase 3B 86% vs 84%, MiniLM dual-index P@5) remains part of the project history. Those numbers describe routing classification or a different retriever. They are **not** ExactSource Hit@5 or U Success@5. The remainder of this chapter is Layer B: official M0.

## 5.1 Phase 2 development/validation known-item (n=78)

**Table 3. Phase 9 / Phase 2 n=78 ExactSource results**

| System / slice | Evaluation type | Metric | Result |
| --- | --- | --- | --- |
| M0 (script-aware BM25) | Known-item, development/validation | ExactSource Hit@5 | **68/78 = 87.18%** |
| Urdu-only BM25 (no Roman path) | Same pool | ExactSource Hit@5 | 0.5897 |
| Roman subset, Method A (raw BM25) | `title_roman`, n=23 | ExactSource Hit@5 | 0/23 |
| Roman subset, Method D | `title_roman`, n=23 | ExactSource Hit@5 | 22/23 |
| Secondary M0 (same n=78) | Known-item | nDCG@5 / MRR | 0.8107 / 0.797 |

The frozen ULTRA system achieved an ExactSource Hit@5 of 87.18% (68/78) on the Phase 2 development/validation known-item evaluation set.

This result is genuine within its protocol: gold ids were assigned with the queries; the source article was in the Top-5 for 68 of 78 strings. The Roman comparators show why a second index was needed on this pool.

**Limitation of 87.18%.** The pool was used to select Method D and freeze M0. Roman `QTRN_*` strings are Phase 2 `title_roman`, not chat Roman. 87.18% is therefore not unseen usefulness and not “overall system accuracy.”

## 5.2 Phase 11 ablation (M0 remains official)

**Table 4. Phase 11 M0–M4 ablation (n=78 known-item)**

| Model | n=78 ExactSource Hit@5 | Roman train Hit@5 | Roman train nDCG@5 | Decision |
| --- | --- | --- | --- | --- |
| M0 | 68/78 = 87.18% | 61/64 = 95.31% | 0.8960 | **Official control** |
| M1 | 68/78 = 87.18% | 61/64 = 95.31% | 0.8940 | Gate-pass only; no Hit@5 lift |
| M2 | 68/78 = 87.18% | 61/64 = 95.31% | 0.8940 | No Hit@5 lift |
| M3 | 68/78 = 87.18% | 61/64 = 95.31% | 0.8940 | No Hit@5 lift |
| M4 | 68/78 = 87.18% | 61/64 = 95.31% | 0.8940 | No Hit@5 lift |

M1–M4 did not improve primary known-item Hit@5. nDCG@5 was slightly worse than M0. M1 is not a successful improvement and is not the deployed system.

## 5.3 Phase 12 new known-item (K001–K040)

**Table 5. Phase 12 K ExactSource results (frozen M0)**

| Metric | Hits | n | Rate | Evaluation type |
| --- | ---: | ---: | --- | --- |
| ExactSource Hit@1 | 20 | 40 | 50.00% | New sealed known-item |
| **ExactSource Hit@5** | **27** | **40** | **67.50%** | **Primary K result** |
| ExactSource Hit@10 | 28 | 40 | 70.00% | New sealed known-item |
| ExactSource Hit@50 | 30 | 40 | 75.00% | New sealed known-item |

Descriptive detector split (not used for tuning): URDU 26/28; ROMAN 1/12. The drop from 87.18% to 67.50% is concentrated on ordinary Roman title queries, not on native-script titles. 67.50% does not replace 68/78 and is not human Success@5.

## 5.4 Phase 12 naturalistic human evaluation (U001–U040)

**Table 6. Phase 12 U human results (frozen M0 Top-5)**

| Metric | Value | Evaluation type |
| --- | --- | --- |
| **Success@5** | **23/40 = 57.50%** | Human usefulness (A or B in Top-5) |
| Conservative P@5 | 0.2050 | Mean of (A-count / 5) |
| nDCG@5 | 0.6460 | Graded; C-gain = 1 (secondary) |
| MRR | 0.4542 | First A or B |

U labels on 200 documents: A=41, B=26, C=53, D=80, E=0. 57.50% is **not** ExactSource Hit@5. nDCG@5 is **not** the usefulness headline: an all-C list can receive nDCG@5 = 1.0 with no A/B.

**Table 7. Script-wise U Success@5 (descriptive)**

| Script | Success@5 | n | Comment |
| --- | --- | ---: | --- |
| URDU | 17/18 = 94.44% | 18 | Strong on this sample |
| ROMAN | 6/18 = 33.33% | 18 | Main observed weakness |
| MIXED | 0/4 = 0% | 4 | All four failed; n is too small for a population rate |

These splits are descriptive. They do not license retuning Method D on U failures, and they do not prove that Method D is “universally bad.” They do show that, in this sealed sample, Urdu-script needs were usually met and Roman/mixed needs often were not.

## 5.5 Diagnostic H001–H040 (not primary unseen)

Phase 9: ExactSource Hit@5 **undefined** (no gold id).  
Phase 10C: human Success@5 = **25/40 = 62.5%**.

Do not present 62.5% as the official unseen usefulness result. Do not average it with 57.50%.

## 5.6 Final comparison of evaluation settings

**Table 8. Final comparison (do not average rows)**

| Setting | n | Gold | Metric | Result | Role |
| --- | ---: | --- | --- | --- | --- |
| Phase 2 dev+val | 78 | `source_doc_id` | ExactSource Hit@5 | 68/78 = 87.18% | Development/validation known-item |
| Phase 12 K | 40 | `source_doc_id` | ExactSource Hit@5 | 27/40 = 67.50% | New known-item |
| Phase 12 U | 40 | Human A/B | Success@5 | 23/40 = 57.50% | New naturalistic usefulness |
| H001–H040 | 40 | Human A/B | Success@5 | 25/40 = 62.5% | Diagnostic only |

## 5.7 Why 87.18% is genuine — and why it cannot be “real-world usefulness”

The 87.18% score answers a defined question: *on these title-derived known-item queries, did the designated article appear in the Top-5?* For 68/78 queries, yes. Comparators on the same pool (Urdu-only 0.5897; Method A 0/23; Method D 22/23) indicate that the score is not an empty bookkeeping artifact.

It cannot be generalized into 87.18% real-world usefulness because (i) the set was used during architecture selection, (ii) Roman strings match Method D’s `title_roman` construction, and (iii) usefulness for a person is a different random variable (U Success@5).

## 5.8 Why Phase 12 matters

Without K and U, the thesis would stop at a freeze-set known-item number. Phase 12 was sealed before retrieval and did not change M0. It is the independent check. Hiding 67.50% or 57.50% would be the scientifically weaker choice.

## 5.9 The generalization gap (87.18% → 67.50% → 57.50%)

These results suggest a staircase of **task difficulty and query-form mismatch**, not a single accuracy that “fell.”

- 87.18% is known-item recovery on the freeze pool, including `title_roman`.
- 67.50% is the **same known-item question** on new titles. Urdu titles remain high (26/28); ordinary Roman titles do not (1/12). Independent sampling at n=40 also adds ordinary variance.
- 57.50% is a **different question**: natural needs, no gold article, one A/B anywhere in the Top-5. P@5 = 0.2050 suggests many successes are a single useful document, not a Top-5 of complete answers.

Known-item evaluation alone is insufficient for a usefulness claim. Human evaluation provides a different perspective: the system can miss the exact source and still help, or return topical neighbours (C) that do not answer the need.

## 5.10 Error analysis (descriptive)

**Urdu path.** Development and K Urdu titles, and U Urdu queries (17/18), suggest that BM25 on native script is a strong match to this news collection when the query language matches the index.

**Roman path.** Development `title_roman` succeeded (22/23); K ordinary Roman titles mostly failed (1/12); U chat Roman succeeded in 6/18. These results suggest that Method D is sensitive to whether the query spelling family matches document romanization. They do not, by themselves, isolate a single linguistic cause (named entities, English loanwords, underspecification, and temporal wording can co-occur).

**Mixed.** 0/4 on U is reported because all four failed. n=4 cannot support a stable rate. MIXED is routed to Urdu BM25 by freeze rule; Latin tokens may then match poorly. This is a limitation, not a licence to retune on those four strings.

**Temporal / archive.** U used a type-of-fact rule for “today/current” wording: archive articles that answer the *kind* of fact can be A/B; live “right now” correctness was not claimed. That protocol choice should be read as part of the usefulness definition.

**nDCG inflation.** U037–U039 illustrate all-C lists with high nDCG and Success@5 = no. Report Success@5 and MRR for usefulness.

Query distribution matters: a 50/50 Urdu/Roman U design will look worse overall than an Urdu-only test, even if the Urdu component is strong. That is a property of the sample, not a reason to drop Roman queries from the thesis.

## 5.11 Discussion (scientific story)

The final scientific story is:

1. 87.18% demonstrates strong retrieval under the original known-item protocol.
2. 67.50% indicates that performance is not perfectly stable on independently sampled known-item queries, especially ordinary Roman titles.
3. 57.50% shows a further gap between controlled known-item retrieval and realistic user needs.
4. The strongest observed weakness in the U sample is script: Urdu ≫ Roman > Mixed (small n).

Adaptive dynamic query routing in M0 is a working **script switch**. Method D is a necessary Roman-document index for `title_roman`-like queries and is not a complete solution for naturalistic Roman Urdu. Phase 11 showed that small allowed query expansions did not move 68/78. These results suggest that future Roman work needs a new sealed test, not edits to U/K/H.

Layer A’s MiniLM dual-index P@5 on H001–H040 (word count 36.50% vs SVM 33.00% in the IEEE routing paper) is a **different** negative retrieval result. It must not be blended with M0 Success@5 = 57.50%.

---

# Chapter 6: Conclusions and Recommendations

## 6.1 Conclusions

ULTRA, as frozen in M0, demonstrates strong performance under its development/validation known-item protocol, achieving **87.18% ExactSource Hit@5 (68/78)**.

Independent evaluation reveals a meaningful generalization gap: **67.50%** ExactSource Hit@5 on new known-item queries (K001–K040) and **57.50%** naturalistic human Success@5 (U001–U040).

Therefore the contribution is not “87% real-world accuracy.” The contribution is a retrieval framework with strong controlled known-item performance, adaptive script routing, Method D for romanized documents, and an explicitly evaluated limitation on naturalistic Roman and mixed queries.

M0 remains the official frozen system. M1–M4 did not improve n=78 Hit@5. H001–H040 Success@5 = 62.5% is diagnostic only.

## 6.2 Summary of contributions

See Section 1.7. Each contribution is tied to a labeled metric and evaluation setting in Tables 3–8.

## 6.3 Limitations

- **Sample size.** K and U use n=40. Point estimates have wide uncertainty. Numerators and denominators must be reported.
- **Known-item vs naturalistic.** ExactSource Hit@5 and Success@5 are different tasks. 87.18% → 57.50% is not one metric getting worse.
- **Roman Urdu variability.** Ordinary and chat spelling diverge from `title_roman`. A 198-key dictionary does not cover that space.
- **Mixed queries.** n=4; all failed in this sample. Do not hide; do not over-generalize.
- **Corpus/domain.** News only. No claim for other domains.
- **Temporal queries.** Archive type-of-fact judging is not live current-events QA.
- **Human annotation.** One annotator; no inter-annotator agreement.
- **No broad external public qrels** for this freeze (CURE / MS MARCO were not this protocol).
- **No claim of 80% unseen usefulness** and no claim of 87.18% real-world accuracy.
- **nDCG@5** with C-gain=1 overstates usefulness.
- **H001–H040** cannot be the primary unseen result; ExactSource is undefined there.
- **K and U are burned** for any later change to M0.
- **Layer A development P@15 / 100% routing** must not be cited as frozen M0 IR performance.

## 6.4 Future work

Do not tune BM25, the dictionary, routing, or Method D on U001–U040, K001–K040, or H001–H040. Do not create H041+ for that purpose.

If the system changes: freeze first, seal a **new** query file, retrieve once, then label. Report new scores beside 68/78, 27/40, and 23/40.

Useful directions: better Roman query–document matching; mixed-script evaluation with more than four queries; a second annotator on a **new** naturalistic set; larger sealed U if annotation budget allows.

## 6.5 Practitioner note

For native-script Urdu news search on this collection, frozen M0 is a reasonable lexical baseline. For Roman Urdu user traffic, expect a large drop relative to the 87.18% freeze-set figure. Do not ship 87.18% as a user-facing SLA.

## 6.6 Closing remarks

An honest MS AI thesis can hold two facts at once: the development known-item protocol produced a real 68/78, and independent tests produced 27/40 and 23/40. Routing by script is the load-bearing adaptive mechanism of M0. Solving chat Roman Urdu remains open.

---

# CLAIMS WE CAN SAFELY MAKE

1. 87.18% ExactSource Hit@5 on Phase 2 n=78 development/validation known-item queries.
2. 67.50% ExactSource Hit@5 on independently sealed K001–K040 (Hit@1 = 50.00%, Hit@10 = 70.00%, Hit@50 = 75.00%).
3. 57.50% human Success@5 on independently sealed naturalistic U001–U040 (P@5 = 0.2050, nDCG@5 = 0.6460, MRR = 0.4542).
4. In the Phase 12 U sample, Urdu queries substantially outperformed Roman queries (17/18 vs 6/18); Mixed was 0/4 (descriptive, small n).
5. M0 remains the official frozen system; M1–M4 did not improve n=78 ExactSource Hit@5.
6. H001–H040 Success@5 = 62.5% is diagnostic only; ExactSource Hit@5 on that set is undefined.

# CLAIMS WE MUST NOT MAKE

1. “ULTRA has 87.18% real-world accuracy.”
2. “ULTRA achieved 87.18% unseen usefulness.”
3. “ULTRA achieved 80% unseen usefulness.”
4. “57.50% is ExactSource Hit@5.”
5. “Phase 12 U proves the system is 57.5% accurate.”
6. Any claim that Phase 11 M1–M4 improved the official system.
7. Averaging 87.18%, 67.50%, and 57.50%.
8. Treating H001–H040 as the primary unseen evaluation.
9. Calling nDCG@5 = 0.6460 the usefulness headline.
10. Quoting development 100% routing or ~90% P@15 as frozen M0 retrieval performance.

---

# References

Arabzadeh, N., Yan, X., & Clarke, C. L. A. (2021). Predicting efficiency/effectiveness trade-offs for dense vs. sparse retrieval strategy selection. In *Proceedings of CIKM* (pp. 2862–2866).

Bashir, A., Qaiser, F., & Hussain, I. (2026). ULTRA: Urdu Language Transformer-based Recommendation Architecture. arXiv:2602.11836.

Butt, U., Varanasi, S., & Neumann, G. (2024). Enabling low-resource language retrieval: Establishing baselines for Urdu MS MARCO. arXiv:2412.12997.

Carmel, D., & Yom-Tov, E. (2010). *Estimating the Query Difficulty for Information Retrieval*. Morgan & Claypool.

Chari, A., MacAvaney, S., & Ounis, I. (2025). Improving low-resource retrieval effectiveness using zero-shot linguistic similarity transfer. In *ECIR 2025*, LNCS 15575 (pp. 290–306). Springer.

Conneau, A., et al. (2020). Unsupervised cross-lingual representation learning at scale. In *Proceedings of ACL* (pp. 8440–8451).

Cortes, C., & Vapnik, V. (1995). Support-vector networks. *Machine Learning, 20*(3), 273–297.

Daud, A., Khan, W., & Che, D. (2017). Urdu language processing: A survey. *Artificial Intelligence Review, 47*, 279–311.

Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q. (2017). On calibration of modern neural networks. In *Proceedings of ICML*.

Hsu, H.-L., & Tzeng, J. (2025). DAT: Dynamic Alpha Tuning for hybrid retrieval in retrieval-augmented generation. arXiv:2503.23013.

Hussain, N., et al. (2025). Fine-tuning large language models with QLoRA for offensive language detection in Roman Urdu-English code-mixed text. arXiv:2510.03683.

Iqbal, M., Tahir, B., & Mehmood, M. A. (2021). CURE: Collection for Urdu Information Retrieval Evaluation and Ranking. arXiv:2011.00565.

Jeong, S., et al. (2024). Adaptive-RAG: Learning to adapt retrieval-augmented large language models through question complexity. In *Proceedings of NAACL* (pp. 7036–7050).

Karpukhin, V., et al. (2020). Dense passage retrieval for open-domain question answering. In *Proceedings of EMNLP* (pp. 6769–6781).

Kazi, S., & Khoja, S. A. (2025). Towards building Urdu language document retrieval framework. Pre-print / journal under review.

Lewis, P., et al. (2020). Retrieval-augmented generation for knowledge-intensive NLP tasks. In *NeurIPS*, 33.

Mehmood, F., et al. (2020). A precisely Xtreme-multi channel hybrid approach for Roman Urdu sentiment analysis. arXiv:2003.05443.

Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence embeddings using Siamese BERT-networks. In *Proceedings of EMNLP-IJCNLP* (pp. 3982–3992).

Robertson, S., & Zaragoza, H. (2009). The probabilistic relevance framework: BM25 and beyond. *Foundations and Trends in Information Retrieval, 3*(4), 333–389.

Sitaram, S., Chandu, K. R., Rallabandi, S. K., & Black, A. W. (2019). A survey of code-switched speech and language processing. arXiv:1904.00784.

Wu, J., Ren, Z., & Verberne, S. (2024). What are the limits of cross-lingual dense passage retrieval for low-resource languages? arXiv:2408.11942.

---

*Sources for numbers: `experiments/phase8_final_freeze/DEVELOPMENT_RESULTS.md`, `PHASE9_RESULTS.md`, `PHASE11_ABLATION_RESULTS.md`, `K_RESULTS.md`, `PHASE12_HUMAN_RESULTS.md`, `FINAL_EXPERIMENTAL_RESULTS_ANALYSIS.md`. No new retrieval was run for this draft.*
