# Thesis Chapters 5–6: what to change and paste-ready frozen-M0 text

**Purpose:** Insert the official retrieval evaluation (Phases 8–12) into the Air University thesis **without** rewriting Chapters 1–4 blindly and **without** new experiments.

**Official system in this paste pack:** M0  
URDU/MIXED → Urdu BM25; ROMAN → Method D; Unicode detector; \(k_1=1.5\), \(b=0.75\); corpus 111,860 documents.

**Do not average** 87.18%, 67.50%, and 57.50%.  
**Do not** call 57.50% ExactSource Hit@5.  
**Do not** claim 80% unseen usefulness.

---

# A. What needs changing (inspect first)

The current Word thesis (`Hashim_Shazad_243259_AU_Thesis_ULTRA.docx`) is organized as an **SVM SHORT/LONG router** story:

| Current section | What it currently says | Problem for submission |
| --- | --- | --- |
| Ch. 5 intro, 5.1–5.12 | 100% routing vs θ=150; overall P@15 43.75% → 90%; Roman P@15 92.50% (8 queries) | These are **development routing / small P@15** numbers. They are **not** frozen M0 ExactSource or U Success@5. |
| 5.13–5.14 | Phase 3B SVM 86% vs word-count 84% | Valid **only** as frozen **classification**, not as news-search Hit@5. |
| 5.15 | Phase 2.5 MiniLM human P@5-style pilot | Different system (dense dual index). Do not mix with M0. |
| 6.1–6.2, 6.7 | Answers RQ1–RQ3 as routing-vs-threshold; quotes 90% P@15 | Must add the **official retrieval** findings or the thesis will over-claim. |
| 6.3 | Dictionary 179 keys, MEDIUM/LOW untested | Dictionary is **198** keys in the freeze; add M0 / K / U / Roman gap / nDCG-C. |
| Abstract / Ch. 1 / 4.3 | “Adaptive dynamic query routing” + P@15 | Keep as **history of the router work**, then **state that official IR evaluation is script-aware BM25 (M0)**. |
| IEEE `main.tex` | MiniLM dual-index P@5 on H001–H040 | A **different paper claim**. Thesis retrieval headline must be M0, not that P@5 table. |
| Clause-1 PLOS draft | 100% routing, external 50-query 100% | **Do not** paste into Ch. 5 as frozen M0. |

**Recommended structure (minimal churn):**

1. Keep 5.1–5.15, but add a **box at the start of Chapter 5**: two layers that must not be mixed (SVM routing vs M0 retrieval).  
2. **Add new sections 5.16–5.19** (text below) as the official IR results.  
3. **Replace 6.1 Conclusions, 6.3 Limitations**, and add a short paragraph to **6.5 Future work** (do not tune U/K/H).  
4. In 5.2 and 5.12, add one sentence: *“The 90.00% P@15 figure is a development retrieval experiment on a small query set; it is not the official M0 evaluation.”*  
5. Abstract: one sentence listing 68/78, 27/40, 23/40 as **separate** metrics.

No new retrieval is required if these edits are made.

---

# B. Exact proposed text

Paste the following into the thesis. Headings match AU style (Chapter 5 / 6).

---

## Chapter 5 addition — opening box (before §5.1)

This chapter contains **two evaluation layers**.

**Layer A (Sections 5.1–5.15).** Development and frozen tests of a SHORT/LONG **SVM router** and related MiniLM dual-index pilots. Those numbers describe **routing classification** and earlier dense-index probes. They must not be quoted as ExactSource Hit@5 or as naturalistic Success@5 of the official retriever.

**Layer B (Sections 5.16–5.19).** Official **frozen retrieval system M0**: Unicode script detection, Urdu BM25 for URDU and MIXED queries, Method D romanized-document BM25 for ROMAN queries. This is the system used for known-item and human-relevance IR metrics below. Phase 11 query-side models M1–M4 did not improve n=78 ExactSource Hit@5; **M0 was not replaced**.

---

## 5.16 Official frozen retrieval system (M0)

After architecture comparison on the Phase 2 development/validation known-item pool, the official retriever was frozen as M0. Queries are not rewritten. Routing is a Unicode letter-count detector: URDU or MIXED strings search an Urdu BM25 index over article text; ROMAN strings search a Method D index in which documents are romanized with the reverse dictionary and a fixed character table, while the query is tokenized as typed. BM25 uses \(k_1 = 1.5\) and \(b = 0.75\). The corpus contains 111,860 news articles. The Roman dictionary has 198 keys and was not edited after the freeze.

Two questions are kept separate:

- **ExactSource Hit@5:** Did the **exact** source article appear in the Top-5? This requires a `source_doc_id` assigned when the query was written.  
- **Human Success@5:** Did **any** Top-5 article receive label A (relevant) or B (partially relevant)? This is used when there is no gold document.

These metrics are **not** interchangeable and are **not** averaged.

---

## 5.17 Known-item results

### 5.17.1 Development/validation pool (\(n = 78\))

On Phase 2 **dev + internal_val** title-derived queries (`QTRN_*`), gold is `source_doc_id`.

**ExactSource Hit@5 = 68/78 = 0.8718 (87.18%).**

This result is genuine for that setting: the designated source was in the Top-5 for 68 of 78 queries. On the same pool, Urdu-only BM25 without a Roman path scored 0.5897 Hit@5. On the Roman subset, raw BM25 (Method A) scored 0/23; Method D scored 22/23. Those comparisons justify keeping a Roman document index.

**Limitation of 87.18%.** The pool was used to select Method D and freeze M0. Roman `QTRN_*` strings are Phase 2 `title_roman` (dictionary reverse plus character romanization), not chat-style Roman Urdu. Therefore 87.18% is **not** unseen user accuracy and **not** human usefulness.

H001–H040 have **no** `source_doc_id`. Official ExactSource Hit@5 on that set is **undefined** (Phase 9). It is not a Hit@5 of 0%.

### 5.17.2 New sealed known-item set K001–K040 (\(n = 40\))

Queries and source ids were sealed before retrieval. Frozen M0 was run once.

**ExactSource Hit@5 = 27/40 = 0.6750 (67.50%).**

Hit@1 = 20/40; Hit@10 = 28/40; Hit@50 = 30/40.

Descriptive script split (not used for tuning): Urdu-script K queries 26/28; ordinary Roman title queries 1/12. The drop from 87.18% to 67.50% is concentrated on **ordinary Roman Urdu**, not on native-script titles.

This number **does not replace** 68/78. It is a **new** known-item estimate for frozen M0.

---

## 5.18 Naturalistic human-relevance results (U001–U040)

U queries have **no** gold document. The frozen M0 Top-5 was labeled with the project rubric: A relevant, B partially relevant, C topically related, D not relevant, E only if A–D cannot be decided. Success@5 requires at least one A or B.

**Success@5 = 23/40 = 0.5750 (57.50%).**

Conservative P@5 (mean of A-count/5) = 0.2050.  
nDCG@5 (gains A=3, B=2, C=1, D=E=0) = 0.6460.  
MRR (first A or B) = 0.4542.

nDCG@5 is **not** the usefulness headline: C has gain 1, so a Top-5 of only topical neighbours can obtain nDCG@5 = 1.0 with no A/B.

Descriptive script split of Success@5:

| Script | Success@5 |
| --- | --- |
| URDU | 17/18 = 94.44% |
| ROMAN | 6/18 = 33.33% |
| MIXED | 0/4 |

MIXED \(n=4\) is too small for a population rate; it is reported because all four failed, not because it licenses tuning.

H001–H040 human Success@5 = 25/40 = 62.5% is a **diagnostic** on contaminated trap queries. It is **not** the official unseen usefulness result. U001–U040 is.

---

## 5.19 Discussion: the gap 87.18% → 67.50% → 57.50%

The three percentages look like one system collapsing. They are **three measurements**.

**87.18%** asks: on development title-like known-item queries, including `title_roman`, did the exact source reach Top-5? Often yes. Method D matches that Roman construction.

**67.50%** asks the **same known-item question** on a **new** sealed title sample. Native-script titles remain strong. Ordinary Roman titles do not. The gap is mainly a **Roman query-form shift** (chat-like spelling vs `title_roman`), plus ordinary variation at \(n=40\).

**57.50%** asks a **different question**: on new natural needs with no gold article, was anything in Top-5 useful (A or B)? About 58% overall; about 94% when the query is Urdu script; about 33% when it is Roman. P@5 = 0.205 shows that successes are often a single useful document, not a Top-5 of complete answers.

**Adaptive dynamic query routing / Method D.** In the official M0 pipeline, “routing” is **script detection**, not the SVM SHORT/LONG switch. That detector is reliable enough that Urdu and Roman take different indexes. Method D is **necessary** for `title_roman` known-item search (0/23 → 22/23 on the development Roman subset) and **insufficient** for ordinary Roman Urdu on new K and U. Phase 11 spelling expansions did not raise 68/78 Hit@5, so M0 stays official. The scientifically defensible claim is: **script-aware BM25 is a strong Urdu-script news retriever and a partial Roman solution, not a solved Roman Urdu IR system.**

Do not average the three rates. Do not hide 57.50%. Do not retune M0 on K or U.

---

## 6.1 Conclusions (replacement)

This thesis evaluated Urdu news retrieval under a **frozen** lexical system (M0) after earlier work on learned SHORT/LONG routing. The official retriever uses Unicode script detection, Urdu BM25, and Method D for Roman queries. It was not changed after Phase 12.

Three results must be stated separately:

1. On the Phase 2 development/validation known-item set, ExactSource Hit@5 = **68/78 (87.18%)**. This is a valid known-item score for title-derived queries on that pool. It is not unseen real-world usefulness.  
2. On a new sealed known-item set (K001–K040), ExactSource Hit@5 = **27/40 (67.50%)**.  
3. On a new sealed naturalistic set (U001–U040), human Success@5 = **23/40 (57.50%)**. Conservative P@5 = 0.2050. This is not ExactSource Hit@5.

Urdu-script naturalistic queries were useful in 17/18 cases; Roman queries in 6/18. That descriptive split is the main limitation of Method D under ordinary Roman spelling. Query-side models M1–M4 did not improve 68/78; M0 was not replaced by M1.

H001–H040 Success@5 = 62.5% remains diagnostic only.

The thesis therefore supports a **qualified** conclusion: adaptive **script** routing plus Method D substantially improves development known-item search relative to Urdu-only BM25, and remains useful for native-script user queries, but **does not** deliver 87% (or 80%) usefulness on unseen natural Roman Urdu queries.

---

## 6.3 Limitations (replacement / insert as official IR limitations)

Keep existing SVM-specific limits (Phase 3B power, HIGH-tier-only confidence demo) as a **subsection on the routing layer**. Add this **official retrieval** subsection:

**Sample size.** K and U use \(n=40\). Point estimates have wide uncertainty. Report numerators and denominators.

**One annotator.** U labels are a single judge. There is no inter-annotator agreement.

**Known-item versus ad hoc.** ExactSource Hit@5 and Success@5 measure different tasks. The drop 87.18% → 57.50% is not “the same metric getting worse.”

**Roman Urdu.** Ordinary spelling does not match Method D’s `title_roman` construction. A 198-key dictionary does not cover chat Roman. Phase 11 expansions did not move n=78 Hit@5.

**nDCG@5.** Gain C=1 inflates nDCG. Use Success@5 and MRR for usefulness.

**H001–H040.** No ExactSource gold; human labels exist but the set is open. Not official unseen performance. Not a tuning set.

**K and U are burned** for any later change to M0. Future systems need a new sealed test.

**Development P@15 / 100% routing** in Sections 5.1–5.12 must not be cited as frozen M0 IR performance.

**News corpus only.** Results do not automatically extend to legal, medical, or social-media search.

---

## 6.5 Future work (insert; do not tune Phase 12)

Do not tune BM25, the dictionary, routing, or Method D on U001–U040, K001–K040, or H001–H040.

If the system is changed, freeze it first, seal a **new** query file, retrieve once, then label. Report new scores **beside** 68/78, 27/40, and 23/40; do not overwrite them.

Priority directions: better Roman query–document matching; mixed-script evaluation with more than four queries; a second annotator on a **new** naturalistic set; larger sealed U if annotation budget allows.

---

# C. Final table of results (official IR layer)

| Dataset | Query type | n | Method | Metric | Result | Use in thesis |
| --- | --- | ---: | --- | --- | --- | --- |
| Phase 2 dev+internal_val | Title-derived known-item | 78 | Exact source in Top-5 | ExactSource Hit@5 | **68/78 = 87.18%** | Development/validation only. Not unseen. |
| Same, no Roman path | Same | 78 | ExactSource Hit@5 | ExactSource Hit@5 | 0.5897 | Why a Roman index was needed. |
| Roman subset, Method A | `title_roman` | 23 | ExactSource Hit@5 | ExactSource Hit@5 | 0/23 | Script mismatch. |
| Roman subset, Method D | `title_roman` | 23 | ExactSource Hit@5 | ExactSource Hit@5 | 22/23 | Method D on matching Roman form. |
| Phase 11 M0–M4 | Same n=78 | 78 | ExactSource Hit@5 | ExactSource Hit@5 | 68/78 all | M0 not replaced. |
| Phase 9 H001–H040 | Trap strings | 40 | ExactSource Hit@5 | — | **Undefined** | No gold id. |
| Phase 10C H001–H040 | Same | 40 | Human A/B in Top-5 | Success@5 | 25/40 = 62.5% | Diagnostic only. |
| Phase 12 K | New known-item | 40 | Exact source in Top-5 | ExactSource Hit@5 | **27/40 = 67.50%** | Official new known-item. |
| Phase 12 K URDU | Titles | 28 | ExactSource Hit@5 | ExactSource Hit@5 | 26/28 | Descriptive. |
| Phase 12 K ROMAN | Ordinary Roman titles | 12 | ExactSource Hit@5 | ExactSource Hit@5 | 1/12 | Descriptive. |
| Phase 12 U | New naturalistic | 40 | Human A/B in Top-5 | Success@5 | **23/40 = 57.50%** | Official unseen usefulness. |
| Phase 12 U | Same | 40 | A-count/5 mean | Conservative P@5 | 0.2050 | Secondary. |
| Phase 12 U | Same | 40 | A=3,B=2,C=1,D=E=0 | nDCG@5 | 0.6460 | Secondary; C inflates. |
| Phase 12 U | Same | 40 | First A/B | MRR | 0.4542 | Secondary. |
| Phase 12 U URDU | Naturalistic | 18 | Success@5 | Success@5 | 17/18 = 94.44% | Descriptive. |
| Phase 12 U ROMAN | Chat Roman | 18 | Success@5 | Success@5 | 6/18 = 33.33% | Descriptive. |
| Phase 12 U MIXED | Mixed script | 4 | Success@5 | Success@5 | 0/4 | Descriptive; small n. |

**Do not add an “overall accuracy” row.**

---

# D. Final scientific interpretation (short)

M0 is a **valid frozen IR system**. 87.18% is a **real known-item score** on the freeze set. 67.50% shows that score **does not fully generalize** to new titles when Roman is ordinary spelling. 57.50% shows **unseen natural usefulness** is lower still, and is **not** ExactSource. Script routing works: Urdu BM25 is useful; Method D does not yet solve chat Roman. That is enough for an honest MS contribution. It is not enough to claim the problem is solved.

---

# Claims you CAN make

- ExactSource Hit@5 = 68/78 on development/validation known-item queries.  
- ExactSource Hit@5 = 27/40 on sealed K001–K040.  
- Human Success@5 = 23/40 on sealed U001–U040.  
- Urdu-script U queries: 17/18 Success@5; Roman: 6/18 (descriptive).  
- Method D recovered 22/23 development `title_roman` known-items; Method A recovered 0/23.  
- M1–M4 did not beat 68/78; official system is M0.  
- H001–H040 ExactSource Hit@5 is undefined; 62.5% Success@5 is diagnostic.

# Claims you CANNOT make

- 87.18% (or ~80%) on unseen or real-world queries.  
- 57.50% is ExactSource Hit@5.  
- Averaging 87.18, 67.50, and 57.50.  
- 90% P@15 or 100% routing as official M0 retrieval performance.  
- M1 is the deployed system.  
- H001–H040 is the official unseen test.

---

# Are the results sufficient for thesis submission without further experiments?

**Yes, for experimental completeness**, provided the Word thesis is **edited** so Layer B (M0 table) is the IR headline and Layer A is labeled development/routing-only.

**No further BM25, annotation, or H041+ is required** to have a defensible MS evaluation: you already have development known-item, new known-item, and new human usefulness, plus a negative Phase 11 ablation.

**Still required (writing, not experiments):** insert §§5.16–5.19 and the new 6.1/6.3 text; fix the abstract; stop quoting 90% P@15 and 87.18% as one “system accuracy.” If the examiner expects the thesis to be *only* the SVM router, you must still add M0 or the retrieval claims will contradict the freeze.

Sources: `experiments/FINAL_EXPERIMENTAL_RESULTS_ANALYSIS.md`, Phase 5/8/9/10C/11/12 reports, thesis extract of Chapters 5–6.
