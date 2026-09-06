# Cross-branch reviewer scientific audit

**Project:** ULTRA — Adaptive Dynamic Query Routing for Urdu Information Retrieval  
**Repository:** https://github.com/HashimAbbasii/Dynammic-Query-Routing-Urdu-ILS  
**Audit date:** 6 September 2026  
**Auditor role:** Lead scientific reviewer / PLOS ONE Reviewer #1 / Reviewer #2 / methodology auditor / cross-branch auditor  

**Mode:** AUDIT ONLY. No branch merge, cherry-pick, rebase, checkout-with-commit, M0 change, qrels change, or metric recomputation.

**Branch names used (exact Git refs):**

| User label | Exact Git branch | HEAD inspected |
| --- | --- | --- |
| `main` | `main` | `eee7b9a` |
| research phase 12 | `research/post-phase12` | `dd2113f` |
| publication | `publication/plos-one-final` | `af6fc88` (working branch of this audit) |

**Authority hierarchy used here**

| Role | Branch |
| --- | --- |
| Scientific research evidence (including unmerged later work) | `research/post-phase12` + historical artifacts on all branches |
| Original project context | `main` plus older commits / `archive/` (SVM dual-index era) |
| Publication source of truth | `publication/plos-one-final` manuscript `Papers/PLOS_ONE/Adaptive_dynamic_query_routing_for_Urdu_information_retrieval.tex` |

**Critical naming clarification.** Official Phase 12 K/U evaluation already exists on `main` and on `publication/plos-one-final`. The unmerged branch is **not** the Phase 12 seal itself. It is **post-freeze development** (R-dev, Module 1–2, M3-E union-pool labels, Stage 0 error taxonomy, Roman-normalization library). Treating “missing from publication” as “Phase 12 never happened” would be false.

---

## 1. Executive Summary

If a demanding PLOS ONE reviewer could see the full Git history, the scientifically legitimate weaknesses are **not invented metrics**. The frozen numbers on the publication branch match the sealed Phase 8–12 artifacts. The paper is unusually careful about not averaging 87.18% / 67.50% / 57.50%. The attack surface is elsewhere.

**What the complete history actually shows**

1. The project began as learned SHORT/LONG SVM routing into headline vs full MiniLM indexes. On H001–H040, the SVM **lost** graded P@5 to a word-count rule (0.3300 vs 0.3650). That Layer A result is correctly demoted in the current manuscript.
2. The official frozen system (M0) is a **Unicode script detector** plus **two BM25 indexes**. URDU / MIXED / OTHER → Urdu BM25; ROMAN → Method D romanized-document BM25. That is script-conditional retrieval, not a learned router, not query rewriting, and not sparse-vs-dense routing.
3. Method D was selected on development Roman queries that are `title_roman` (dictionary reverse + character table). On that construction it repaired Method A (0/23 → 22/23). On sealed ordinary-Roman titles (K) it largely failed (1/12). On chat-style U Roman it was useful for 6/18 queries.
4. `research/post-phase12` then built a **new** development set (R-dev: 50 known-item + 50 naturalistic). Frozen M0 scored **19/50** ExactSource Hit@5 and **12/50** Success@5 there, by design a Roman/MIXED-heavy development pool. Conservative Roman normalization (Module 1) changed **nothing**. Character 3-gram BM25 and headline/body RRF (Module 2) did **not** beat M0 under guardrails. Union-pool relabeling (M3-E) showed Module 2’s NAT −4 was mostly a pool artifact, with a residual −1. Module 3 (matching or mixed dual-path) was **not run**.
5. The Phase 6 residual taxonomy (QUERY_AMBIGUITY 4/10, WRONG_ROOM 3/10, …) describes **ten misses on the n=78 title-derived pool**, not the sealed K/U Roman matching failure. The publication manuscript correctly moved the bottleneck to ordinary Roman Urdu. Using Phase 6 labels as the paper’s main diagnosis would be a **category error**.

**Reviewer-visible P0 (must fix before submit, wording/disclosure, no new M0 experiment)**

- The **title** still says “Adaptive dynamic query routing.” The methods define routing as a four-way Unicode if/else. The research history shows the learned router was abandoned. A hostile reviewer can call the title leftover branding.
- The public `research/post-phase12` branch contains later M0 scores of **19/50** and **12/50** on a new development pool. The manuscript has one sentence (“Post-freeze development work exists…”). A reviewer who opens GitHub can allege **selective reporting** unless that work is explicitly scoped out with enough detail to show it is development, not a hidden test.

**What does *not* need a new experiment before submission**

- Do not replace A1 with A2.
- Do not merge R-dev into Table 1.
- Do not retune M0, dictionary, or routing on K/U/H.
- Do not add a multilingual dense Phase 12 run as a condition of submitting *this* lexical freeze paper (the e5-small CPU abort is already disclosed; post-phase12 explicitly did not authorize neural retrieval).

**Final scientific verdict (preview):** the frozen M0 measurement is internally consistent and largely defensible **if** the contribution is described as a hashed, script-aware BM25 news retriever with a measured Roman limitation. It is **not** defensible as a demonstration that “adaptive dynamic query routing” is a new IR method. Minimum work is framing + disclosure, not a new official test.

`NO SCIENTIFIC RESULTS CHANGED` by this audit.

---

## 2. Branch Evidence Map

Inspected without checkout of other branches (`git log`, `git ls-tree`, `git show`, `git diff`).

**Divergence (merge-bases)**

| Pair | Merge-base | Unique commits |
| --- | --- | --- |
| `main` vs `publication/plos-one-final` | `eee7b9a` (= `main` HEAD) | publication is **3** commits ahead: `70f0d49` (A2 sheet), `a8b75ee` (A2 agreement), `af6fc88` (SI, DAS, LICENSE, TIFF, references, REPRODUCE.md) |
| `research/post-phase12` vs publication | `d37bbf0` | phase12 unique: `809d423` (R-dev + modules + M3-E + normalizer), `dd2113f` (Stage 0 taxonomy). Publication unique vs that fork: `a8d64e6` “Plos one convertion”, `eee7b9a`, plus the three A2/packaging commits |
| `main` vs `research/post-phase12` | `d37bbf0` | `main` has PLOS conversion; phase12 has post-freeze research |

**Tracked file counts under `experiments/`:** `main` 132 · `research/post-phase12` 198 · `publication/plos-one-final` 156.

| Component | `main` | `research/post-phase12` | `publication/plos-one-final` | Scientific significance |
| --- | --- | --- | --- | --- |
| Official M0 code (`run_phase5.py` detector + BM25 + Method D) | Present | Present (unchanged freeze) | Present (publication source of truth) | Frozen retriever. Not relocated into `src/`. |
| Phase 2 known-item pool / `title_roman` | Present | Present | Present | Source of 68/78. Architecture-selection pool. |
| Phase 4 dense comparators (headline MiniLM, chunk ANN) | Present | Present | Present | Development table only. Not Phase 12. |
| Phase 5 Roman A–D selection | Present | Present | Present | Method D selected on **n=13** DEV Roman. |
| Phase 6 residual taxonomy (QUERY_AMBIGUITY etc.) | In `archive/historical_experiments/phase6_residual_diagnosis/` | Same archive copy | Same archive copy | Diagnosis of **10** n=78 misses. Not the K/U bottleneck. |
| Phase 8 freeze manifests | Present; `test_set` still `H001-H040` | Present | Present; S1 File caption warns | Historical freeze JSON vs later K/U official tests. |
| Phase 9 H001–H040 | ExactSource Hit@5 **undefined** (no gold id) | Same | Same; paper reports 10C Success@5 25/40 diagnostic | Protects against claiming 87.18% as that test. |
| Phase 10C human labels on H | Present | Present | Present | Burned diagnostic. |
| Phase 11 M0–M4 | All 68/78; no lift | Same | Same; Table 3 | Negative ablation. M0 not replaced. |
| Phase 12 K/U seal + retrieval | Present (`phase12_new_unseen_evaluation/`) | Present | Present | Official unseen numbers. |
| Phase 12 A1 human qrels | Present | Present | Present | Official U 23/40. |
| Phase 12 A2 independent labels | **Absent** | **Absent** | **Present** (`phase12_independent_annotation/`) | Reliability only. Publication-only addition. |
| R-dev, Module 1–2, M3-E, Stage 0 taxonomy | **Absent** | **Present** (`experiments/post_phase12_development/`) | **Absent** | Later development. Must not enter Table 1. Must be disclosed as out of scope. |
| Roman normalization library `src/roman_urdu_normalization/` | Absent | Present | Absent | Failed Module 1 (Δ=0). Not official M0. |
| Canonical PLOS `.tex` | Present (pre-A2/SI packaging) | Older tree: `Papers/PLOS_ONE/FINAL/main.tex` | Canonical current `.tex` + SI + TIFF | Publication wins for wording. |
| `experiments/publication_audit/` DAS/LICENSE/refs | Absent | Absent | Present | Editorial packaging, not new science. |
| Historical SVM/MiniLM (`archive/`, `feat/dual-index-svm-routing`) | Reachable in history / archive | Archive | Archive | Original “routing” idea. Officially rejected. |
| Corpus CSV | Not in Git (all branches); SHA in manifests | Same | Same | Third-party news text. |
| Dictionary 198 keys | Present | Present | Present | Method D reverse map. |

**Important commits (non-empty messages are rare; many subjects are `.` placeholders)**

| Commit | Branch | What it actually added |
| --- | --- | --- |
| `b54ffeb` | ancestors of all three | Phase 0 freeze + Phase 1 P@5 forensic (SVM loses to word count) |
| `33f33a0` | ancestors | Merge `research/phase0-1-routing-diagnosis` |
| `a8d64e6` | `main` + publication | “Plos one convertion” — current manuscript path appears here |
| `809d423` | `research/post-phase12` only | R-dev + Modules 1–2 + M3-E + normalizer (~70 files) |
| `dd2113f` | `research/post-phase12` only | Stage 0 mechanical error taxonomy |
| `70f0d49` / `a8b75ee` / `af6fc88` | publication only | A2 + SI + DAS/LICENSE/figures/REPRODUCE |

---

## 3. Cross-Branch Scientific Consistency

**Does `main` → Phase 12 → publication form a coherent progression?**

**Yes, for official M0 numbers.** The freeze hashes, routing table, BM25 \(k_1=1.5\), \(b=0.75\), dictionary 198 keys, 68/78, 27/40, and 23/40 are the same objects on all three current tips where those artifacts exist.

**No, if one expects the Git branch names to match the science.** `main` is **not** the abandoned SVM system. `main` HEAD already contains the M0 PLOS conversion. `research/post-phase12` is **after** Phase 12, not the Phase 12 seal. Publication is `main` plus A2 and packaging, **not** a merge of post-phase12 research.

| Check | Finding | Contradiction? |
| --- | --- | --- |
| Corpus n / SHA | 111,860; `8992a6ac…` on freeze manifests and manuscript | No |
| Routing | URDU/MIXED→Urdu BM25; ROMAN→Method D | No |
| 68/78, nDCG@5 0.8107, MRR 0.797 | Phase 6/8/9/11/paper | No |
| K 20/40, 27/40, 28/40, 30/40 | `K_RESULTS.md` = paper Table 4 | No |
| U A1 23/40, P@5 0.2050, nDCG@5 0.6460, MRR 0.4542 | `metrics.json` = paper | No |
| A2 26/40, κ 0.5490 / 0.6816 | Publication only; paper does not replace A1 | No (intentional) |
| Phase 9 official Hit@5 on H | `null` / undefined | No; paper does not invent one |
| Freeze JSON `test_set: H001-H040` | Stale vs later K/U | Documentation lag, disclosed in S1 File |
| Metric definitions | ExactSource vs Success@5 kept separate | No |
| Query pools | QTRN / H / K / U / R distinct IDs | No reuse of K/U for R-dev by protocol |
| Conclusions | Paper: Urdu strong, ordinary Roman weak | Matches K/U splits; Phase 6 mixed-title taxonomy is a **different** residual story |
| `research/post-phase12` ROADMAP: “Do not use `main`” | `main` now *is* the M0 freeze line | Process comment outdated; not a metric contradiction |

**Unexplained methodological changes:** none that alter official M0. The abandoned SVM/MiniLM path is explained. Phase 11 did not replace M0. Post-phase12 candidates were **not selected**.

---

## 4. Research Missing From Publication

Compare `research/post-phase12` unique tree vs `publication/plos-one-final`.

| Phase 12 / post-phase12 evidence | Publication status | Should it affect the paper? | Why? |
| --- | --- | --- | --- |
| Official K/U dumps, protocols, A1 qrels | Present | Already in paper | Official science |
| A2 agreement | Present on publication, **absent** on `research/post-phase12` | Already handled | Reliability check; keep A1 official |
| R-dev M0 KI **19/50 = 38%** | Absent | **SHOULD CONSIDER** (limitations / “work not in this paper”), **NOT NEEDED** in Table 1 | New **development** pool, Roman/MIXED-heavy by design. Not a hidden official test. Silence + public Git is a selective-reporting risk. |
| R-dev M0 NAT **12/50 = 24%** | Absent | Same as above | Same |
| Module 1 A–D Roman normalization Δ=0 | Absent | **SHOULD CONSIDER** as supporting the paper’s claim that small spelling tables do not fix Roman | Strengthens RQ4-like interpretation; do not present as unseen |
| Module 2-A char-3gram BM25: KI +1, NAT regression under M0-pool qrels | Absent | **SHOULD CONSIDER** (negative lexical alternative) | Shows a non-BM25-word representation was tried and rejected on R-dev |
| Module 2-B headline/body RRF k=60: KI −1 | Absent | **SHOULD CONSIDER** | Directly answers “why no RRF?” if a reviewer asks; still development |
| M3-E union-pool: M2 NAT 8/50 → 11/50 vs M0 12/50 | Absent | **SHOULD CONSIDER** for methodology literacy (pool bias) | Teaches that unlabeled new hits can fake regressions; not an official score |
| Stage 0: K Roman 10/12 ABSENT; U Roman 11/18 ALL_D; mixed U mostly ALL_C | Absent as named taxonomy; **substance is already in the paper** (Fig 4, all-D lists) | **NOT NEEDED** as new table if K/U text stays | Mechanical restatement of sealed dumps. Do not retune. |
| Stage 0 implication: reranker cannot fix official Roman K | Absent as sentence | **SHOULD CONSIDER** one Discussion sentence | Uses existing K ranks; no new retrieval |
| `src/roman_urdu_normalization` | Absent | **NOT NEEDED** | Implementation of a failed Module 1 |
| Module 3 matching / MIXED dual-path | Not executed | **NOT NEEDED** for this submission | Future work. Do not promise results. |
| Older `Papers/PLOS_ONE/FINAL/main.tex` on post-phase12 | Superseded | **NOT NEEDED** | Do not resurrect. Publication `.tex` is current. |
| Phase 6 QUERY_AMBIGUITY 4/10 | Archive present on publication, **not** used as the paper’s bottleneck | **NOT NEEDED** as headline; **MUST CONSIDER** not to revive it as the main diagnosis | Different evaluation (n=78 mixed templates) |

Classification recap:

- **MUST CONSIDER (validity / honesty, not copy-into-Table-1):** (1) title vs Unicode router; (2) public R-dev existence; (3) do not re-center Phase 6 mixed-title taxonomy as the sealed-set bottleneck.
- **SHOULD CONSIDER:** one limitations paragraph naming R-dev as out-of-scope development; optional SI mention of Module 1 Δ=0 and Module 2 reject; one sentence that Top-50 reranking cannot recover 10/12 Roman K misses.
- **NOT NEEDED:** merging R-dev scores with 23/40; shipping the normalizer; running Module 3 before this paper.

---

## 5. Novelty Audit

**Challenge:** Is ULTRA “adaptive dynamic query routing,” or script classification plus BM25?

**What Phase 12 actually demonstrates**

| Claimed mechanism | What ran as official M0 | Evidence |
| --- | --- | --- |
| Adaptive | Path depends on Unicode counts of the **current query** | True in a weak sense (per-query script label). Not adaptive to retrieval difficulty, confidence, or failure. |
| Dynamic | Path can differ across queries | True in the same weak sense. Not dynamic within a query (no reformulation, no cascade, no depth policy). |
| Query routing | Choose **which BM25 index** to open | True. MIXED is hard-routed to Urdu, not a dual-path fuse. |
| Learned router | SVM SHORT/LONG | **Not** official. Historical P@5 **worse** than word count (0.3300 vs 0.3650). |
| Dense routing | MiniLM dual-index | **Not** official. Development Hit@5 0.4487 headline MiniLM vs 0.8718 M0 on n=78. |

**What the router contributes over a single strategy (development n=78)**

- Urdu-only BM25: Hit@5 **0.5897**
- Script-aware M0: **0.8718**
- Gap is almost entirely the Roman subset: Method A **0/23**, Method D **22/23**

That is a real contribution **on `title_roman` known-item search**. It is **index selection for script mismatch**, not English-style sparse/dense routing (Arabzadeh / Adaptive-RAG citations).

**Does Phase 12 show that routing still helps on unseen data?**

- Urdu K 26/28: the Urdu path works; routing is a no-op vs Urdu-only for those queries.
- Roman K 1/12: routing **did** send queries to Method D, and Method D **mostly missed the Top-50**. So Phase 12 does **not** show that the Roman path generalizes. It shows the development Roman success was construction-matched.
- No sealed **no-routing** or **wrong-index** ablation on K/U exists. A reviewer can say the unseen evaluation measures Method D’s failure, not the value of the detector.

**Engineering vs methodology**

- Engineering: hashed freeze, two indexes, character table, 198-key reverse dictionary, sealed protocols.
- Methodological: keeping ExactSource Hit@5 off human Success@5; refusing to average; reporting Roman collapse.

The second is the publication’s strongest **scientific** contribution. The first is a competent system description. Neither is a new routing algorithm.

**Novelty judgment (do not inflate):** genuine as a **measured, frozen, script-aware lexical evaluation** of Urdu news IR with an honest Roman limitation. Not genuine as a new adaptive/dynamic routing method. Historical SVM work **reduces** novelty of the word “routing” because the learned router was a negative result.

---

## 6. Research Question Audit

Publication RQs (explicit in the current `.tex`):

| RQ | Evidence | Branch | Experiment | Result | Supports RQ? |
| --- | --- | --- | --- | --- | --- |
| RQ1. Can script-aware BM25+Method D recover known articles from title-derived queries on the freeze pool? | Yes, with construction caveat | all three (artifacts) | Phase 2/5/8 n=78 | 68/78 (87.18%; CP 77.68–93.68%) | **Yes**, for `title_roman` / title-derived known-item, not chat Roman |
| RQ2. Does that score transfer to a newly sealed known-item sample? | Transfer of **87%** fails; Urdu titles still high | all three | Phase 12 K | 27/40 (67.50%); URDU 26/28, ROMAN 1/12 | **Yes** as a negative transfer answer, which the paper already states |
| RQ3. How often is frozen M0 useful on naturalistic queries with no gold article? | A1 Success@5 | all three + A2 on publication | Phase 12 U | 23/40 (57.50%); URDU 17/18, ROMAN 6/18, MIXED 0/4 | **Yes** as a sample rate with wide CI; not a population usefulness rate |
| RQ4. Do query-side Roman expansions replace M0? | Phase 11 | all three | M0–M4 on n=78 | all 68/78; nDCG slightly worse | **Yes** (no replacement). Module 1 on R-dev (post-phase12) further supports “small normalizers do not move scores” but is not in the paper |

Implicit RQ a reviewer will infer from the **title**: “Does adaptive dynamic routing improve Urdu IR over strong baselines?” **Not directly tested on K/U.** Development Table 2 supports script-aware vs Urdu-only and vs MiniLM **on n=78 only**.

Post-phase12 does **not** overturn RQ1–RQ4. It shows that a harder development mix yields lower M0 rates and that further lexical patches failed — consistent with the paper’s Roman-limitation conclusion, dangerous only if hidden.

---

## 7. Experimental Validity

### Query generation and selection

- **K:** seed `120260827`; eligible headlines excluding 260 QTRN sources (111,574); stratified category sampling; unique `source_doc_id` 40/40; SHA-256 sealed **before** retrieval. Creator **saw the source article** (required for known-item). Protocol forbade BM25-guided acceptance. Roman K = ordinary Roman of the headline, not `title_roman`.
- **U:** pre-registered quotas (18/18/4 script; length and need-type bins); no `source_doc_id`; SHA sealed before retrieval. First author wrote the queries.

**Leakage / contamination**

| Risk | Status |
| --- | --- |
| Tuning on K/U | Protocols and freeze forbid it; Phase 11 used n=78/train Roman only | Protected if later work stayed off K/U (post-phase12 protocol agrees) |
| Reuse of H strings in K/U | Generation report: H not opened | Protected by protocol (not independently audited by a third party) |
| Corpus-derived K queries | **Inherent.** Known-item from headlines. Inflates overlap vs user queries | Disclosed; still a validity limit for “real search” |
| U written by system author | Dual role with A1 | Disclosed; A2 does not remove it |
| Development Roman matching Method D | **Yes, by construction** | Paper is honest; 87.18% is a ceiling for that family |
| R-dev overlap with K/U | Dedicated `overlap_check.py` + protocol bans | Exists only on `research/post-phase12`; not used to score the paper |

### Development/freeze

Method D chosen on **n=13** DEV Roman, then confirmed on n=10 internal-val (9/10). Small selection set. BM25 hyperparameters **not** grid-searched (frozen 1.5/0.75). That is conservative, not overfit BM25, but Method D **is** overfit to the romanization family.

### Known-item n=78 vs K

Drop 87.18% → 67.50% is **not** mysterious: Roman form shifted. Binomial variation on n=40 is also real (CI 50.87–81.43% still includes values near the development CI lower bound). The **script split** is the scientifically important result, not the 19.7 point headline drop alone.

### Sample size

n=40 K and n=40 U. Mixed n=4. Roman K n=12. All too small for precise rates. Paper reports Clopper–Pearson intervals. That is the correct defense, not a larger claim.

### Duplicates

No exact duplicate query strings in K/U. Corpus: no URL duplicates; **644** duplicate headlines; **4** duplicate `combined_text` pairs (dataset audit). ExactSource treats neighbour wires as misses. Phase 6 already showed non-unique overlap on n=78 misses. This **hurts** known-item Hit@5 and can **help** Success@5 (a neighbour can be A/B). The paper discloses no-dedup.

### Could a reviewer claim the evaluation is biased toward the proposed method?

**Yes, in one precise way:** development Roman queries were generated with the same romanization family as Method D. That biases **87.18%** toward M0. The paper already says this.

**No, for Phase 12 Roman:** ordinary Roman K 1/12 and U Roman 6/18 are **biased against** claiming M0 is a Roman success. A method-boosting author would have kept `title_roman` on K.

**Partial for U overall:** quotas force 18 Roman + 4 mixed, so the 57.50% headline is **more Roman-pessimistic** than an Urdu-only user mix, and **more optimistic** than a Roman-only mix. The paper says query mix moves the headline. That is fair.

**A1 dual role:** bias toward (or against) usefulness is possible. A2 is **higher** (26/40), so A1 is not an inflated official rate relative to the second annotator.

---

## 8. Baseline Audit

Judged against the **central claim that should be defended** (script-aware lexical freeze + Roman limitation), not against a SOTA leaderboard.

| Baseline | Verdict | Reason |
| --- | --- | --- |
| Urdu-only BM25 (no Roman path) | **Present on n=78** (0.5897). **Absent on K/U** | **STRONGLY RECOMMENDED** as a **reanalysis** on sealed K (especially 12 Roman queries), not as M0 replacement. Explanation-only fallback: Method A was 0/23 on development Roman; Latin queries on an Urdu index are expected to fail. |
| Single unified Method D index for all scripts | Not run | **OPTIONAL**. Would test whether the detector is needed vs “always romanize.” Urdu queries on a romanized index could regress. |
| No-routing “always Urdu BM25” on U | Not run | **STRONGLY RECOMMENDED** only if the title stays “routing.” If retitled to script-aware BM25 measurement, **OPTIONAL** (U Urdu 17/18 already shows the Urdu index; Roman U cannot match Urdu script). |
| Multilingual MiniLM / Sentence-BERT | Present as **development** (headline 0.4487, truncated full 0.2564, chunk 0.2821). Not rerun on K/U | **NOT NECESSARY** for submitting a lexical freeze paper. **OPTIONAL** if a reviewer demands modern neural IR. CPU e5-small abort is disclosed. |
| Hybrid / RRF | Oracle headline∪M0 0.9103 **not deployed**. Post-phase12 M2-B RRF **rejected** on R-dev | **NOT NECESSARY** as official. **SHOULD CONSIDER** citing M2-B as development negative if the Git branch is public. |
| Reranking | Not built. Stage 0: 10/12 Roman K never enter Top-50 | **NOT NECESSARY**; a reranker cannot fix ABSENT. Optional for 2 Urdu near-misses only — not the paper’s bottleneck. |
| Script / Roman normalization | Phase 11 M1–M4 no Hit@5 lift; Module 1 Δ=0 on R-dev | **NOT NECESSARY** to add another table. Already answers “just normalize Roman.” |
| Alternative learned router | Historical SVM **lost** P@5 | **NOT NECESSARY** to revive. Keep as rejected alternative (paper already does). |
| CURE / Urdu MS MARCO leaderboard | Different protocol | **NOT NECESSARY**; paper correctly refuses SOTA. |
| Always-Method-D vs M0 on mixed | MIXED hard-routed to Urdu; R-dev mixed KI mass is large | **OPTIONAL** future work (Module 3 family). Do not add to this freeze paper without a locked protocol. |

**MUST ADD:** none, provided the title/abstract stop implying a new routing algorithm that was compared to routing baselines on the unseen sets.

---

## 9. Statistical Audit

| Quantity | Available? | Source |
| --- | --- | --- |
| Clopper–Pearson 95% CI on 68/78, 27/40, 23/40, and script splits | **Yes** (publication manuscript) | SciPy `binomtest`, SciPy 1.16.3 |
| Bootstrap intervals | **UNAVAILABLE FROM CURRENT ARTIFACTS** as official | Not computed in sealed JSON |
| Pre-registered significance tests on K/U | Paper correctly **does not** report p-values | Good |
| Paired test M0 vs Urdu-only on n=78 | **UNAVAILABLE** as a formal test; counts exist to compute McNemar **if** per-query hits are retained | Per-query n=78 ranks exist in phase artifacts |
| Effect size vs Urdu-only | Development Hit@5 0.8718 vs 0.5897 (large descriptive) | Table 2 |
| Per-query K ranks | **Yes** (`K_RESULTS.md`, S1 Table) | Sufficient for ABSENT vs RANK |
| Per-query U labels | **Yes** (A1 qrels, S2 Table) | Sufficient |
| Power analysis | **UNAVAILABLE FROM CURRENT ARTIFACTS** | n=40 CIs already show low precision |
| A2 kappa | **Yes** | 0.5490 / 0.6816 |

**Need before submit?** Report the CIs already in the paper. Do **not** invent tests. Optional (P2): McNemar on n=78 M0 vs Urdu-only using existing per-query hits — reanalysis, not a new retrieval.

Roman K 1/12 CI 0.21–38.48% and U Roman 6/18 CI 13.34–59.01% already prevent a precise “Roman is X%” claim. That is adequate statistical humility **if** the abstract does not over-weight 87.18%.

---

## 10. Human Evaluation Audit

### A1 (official)

- 40×5 = 200 judgments; first author; after Top-5 dump; headline+snippet; A–E rubric; prefer B over A / C over B.
- Success@5 **23/40**; A 41, B 26, C 53, D 80, E 0; 12 all-D queries.
- Query author = annotator. **Independence: no.**
- Protocol: `ANNOTATION_PROTOCOL.md` / S1 Text.

### A2 (reliability)

- Areena Rahman; same 200 documents; A1 labels not in the package (`INSTRUCTIONS.md`).
- Success@5 **26/40**; A 60, B 32, C 28, D 80, E 0.
- Five-way agreement 135/200 = 67.50%; κ **0.5490** (moderate by Landis–Koch naming).
- Binary A/B vs not: 169/200 = 84.50%; κ **0.6816**.
- 65 five-way disagreements; 31 cross the useful/not boundary; Success@5 differs on U018, U024, U035, U037, U039.
- `bm25_score` spreadsheet round-trip mismatches (42) — identifiers still matched.
- No third adjudicator. Disagreements not adjudicated.

**Does A2 strengthen confidence?** Yes, modestly: a second person still finds usefulness in the same ballpark and is **not** more conservative than A1. Binary κ is more relevant to Success@5 than five-way κ.

**Does A2 validate A1 as unbiased?** **No.** Dual-role query authorship remains. Moderate five-way κ shows the A/B/C boundaries are soft (exactly as the rubric designed).

**Must A1 remain official?** **Yes.** Replacing with A2 would be post-hoc annotator shopping (26/40 is higher). Publication policy is correct.

A2 exists only on `publication/plos-one-final`, not on `main` or `research/post-phase12`. That is packaging of a reliability study, not a change to A1.

---

## 11. Failure Analysis

### Phase 6 (n=78 residual 10 misses) — archive, all branches

| Code | Count | OBSERVED? | INTERPRETED? | PROVEN? |
| --- | --- | --- | --- | --- |
| QUERY_AMBIGUITY | 4/10 | Truncated mixed titles + `Pakistan news update` suffix among those 10 | That this is the **system’s** main bottleneck | **No** as a Phase 12 conclusion. **Proven only** as the largest primary label among 10 freeze-pool misses |
| WRONG_ROOM | 3/10 | Headline MiniLM oracle recovers 3 Urdu misses | Need a headline room in deployment | **Not proven** as worth deploying (oracle +3 → 71/78; not deployed) |
| ENTITY_COLLISION | 1/10 | QTRN_216 SECP + template | General entity problem | Single case |
| TOPICAL_NEIGHBOUR | 1/10 primary (QTRN_031); qualitative “all 10 have neighbour issues” | Rank-9 snooker near-duplicates | Neighbours exist in news wire | **Observed** for those items; not a rate |
| KNOWN_ITEM_AMBIGUITY | 1/10 | QTRN_258 near-duplicate CNG wires | Exact id weakly identified | Single case |

Phase 6 also **observed** (stronger): misses overlap the source **at least as much** as hits; failure is **non-unique overlap**, not missing terms.

### Phase 12 K/U (publication bottleneck) — OBSERVED in sealed dumps

| Pattern | Status |
| --- | --- |
| K Urdu misses are RANK (6 and 49), never ABSENT | **OBSERVED** |
| K Roman: 10/11 misses ABSENT from Top-50; 1 RANK (17) | **OBSERVED** |
| U Urdu Success 17/18 | **OBSERVED** |
| U Roman: 11/18 ALL_D | **OBSERVED** (Stage 0; paper lists all-D ids) |
| U MIXED 0/4, mostly ALL_C | **OBSERVED** (n=4) |
| “Ordinary Roman matching / index mapping is the limitation” | **INTERPRETED** from the above + Method D design; **not a causal proof** that no other Romanizer could work |
| “Rerank cannot fix official Roman K” | **PROVEN** for any reranker of the **existing Top-50** (source not in list). Does not prove no other first-stage retriever could. |

**Do not** let Phase 6 QUERY_AMBIGUITY become the manuscript’s stated bottleneck. The current paper’s Roman-matching story is the one the sealed sets support.

---

## 12. Dataset and Generalizability

**What was used:** `data/clean_articles.csv`, 111,860 articles, 540,050,203 bytes, SHA-256 `8992a6ac…`. Precursor `urdu_news.csv` 111,861 records; last truncated row dropped by `dropna()`. `combined_text = Headline + ' ' + News Text`. No NFKC, no stemming, no stopword list, no dedup.

**How it entered:** Kaggle Shahane “Urdu News Dataset” V1 cites Mendeley Hussain et al. V3 DOI `10.17632/834vsxnb99.3`. Byte-level SHA of a **fresh** provider download vs local precursor was **not** completed (manuscript and DAS audits). Title says “1M”; file has 111,861 records.

**Consistency across branches:** freeze SHA is identical. Official scores all claim this file.

**Third-party rights:** authors do not redistribute article text. Redistribution permission **not independently verified**. Reproduction without copyrighted news: possible only if a later researcher obtains Kaggle/Mendeley and matches SHA — **not demonstrated**.

**Generalization (reviewer-safe statements)**

| Target | Supported? |
| --- | --- |
| Urdu news headlines/snippets on this dump | Weakly, for native script |
| Urdu outside news | **No** |
| Other corpora | **No** |
| Other domains | **No** |
| Other languages | **No** (detector is Urdu-block vs ASCII) |
| Other scripts / informal Roman | **Contradicted** by K/U |
| Real-world search logs | **No** (author-written queries, no user logs) |

The paper’s limitations section already covers news-only and n=40. It should not add “scalable” or “generalizable” — and currently does not.

---

## 13. Reproducibility

**Strengths:** hashed corpus/dictionary; sealed query SHA; protocols; `REPRODUCE.md` on publication; M0 entry points documented; metrics copied from sealed reports; SI freeze manifest.

**Weaknesses a reviewer can cite**

- Article CSV not in Git (necessary legally; blocks clean-clone rerun). Manuscript admits no publication-time full-corpus rerun.
- Fresh Kaggle/Mendeley SHA identity **unproven**.
- Freeze JSON still names H001–H040 as `test_set`.
- Phase 6 runner path in `FROZEN_CONFIGURATION.json` points at a directory that now lives under `archive/`.
- Git commit subjects on recent work are uninformative (`.....`).
- `research/post-phase12` is not merged; a cloner of `publication/plos-one-final` will **not** get R-dev. That is acceptable if the paper does not depend on it; it is a problem if reviewers use GitHub default branch `main` (also lacks R-dev and A2).
- Publication `run_phase5.py` **inlines** `transliterate_roman` (no import of archived `validate/dual_index_routing`). Several files under `experiments/publication_audit/` still describe the **old** broken import and an **old** GitHub/unrestricted DAS. The live `.tex` DAS is already the conservative third-party statement. Treat those audit lines as stale relative to the manuscript, not as current blockers.
- Historical SVM pickle expected by archived `router.py` is **not** in git on any of the three branches. Layer A is therefore not clean-clone reproducible; it is also not official M0.

Default GitHub branch is `origin/main` → **not** the publication branch. Reviewers who clone without the branch name will miss A2/SI and will not see post-phase12 either.

---

## 14. Claim-Evidence Matrix

Extracted from the publication manuscript (strong / risky wording).

| Claim | Supporting evidence | Branch | Strength | Reviewer risk |
| --- | --- | --- | --- | --- |
| Title: “Adaptive dynamic query routing” | Unicode if/else; paper later defines it as script-conditional index choice | publication `.tex` | **Weak** as a methods claim; **honest** only after the definition | **High** — first impression vs SVM history |
| Abstract: “official frozen retriever from an adaptive dynamic query-routing project” | Project history includes SVM then M0 | all | Historically true as project biography | Medium — still loads “routing” |
| 68/78 = 87.18% ExactSource Hit@5 | Phase 5/6/8/11 | all | **Strong** for that pool | Low if not called unseen (paper doesn’t) |
| 27/40 = 67.50% | `K_RESULTS.md` | all | **Strong** | Low |
| 23/40 = 57.50% A1 | `metrics.json` | all | **Strong** as A1 sample | Medium — dual role |
| A2 26/40 reliability only | AGREEMENT.md | publication | **Strong** as IAA | Low if not averaged |
| “Queries are not rewritten” | M0 path | all | **Strong** | Low |
| Method D necessary on development Roman | 0/23 vs 22/23 | all | **Strong** for `title_roman` | Low |
| Ordinary Roman is the main limitation | K 1/12, U 6/18, all-D lists | all | **Strong** as descriptive | Medium on n=12/18 |
| RQ2 transfer fails | 87% vs 67.5% + script split | all | **Strong** | Low |
| M1–M4 did not replace M0 | all 68/78 | all | **Strong** | Low |
| “We do not claim SOTA / first Urdu retriever” | explicit | publication | Protective | Low |
| “Native-script Urdu news search … is strong” | 26/28 K; 17/18 U | all | **Moderate** (small n, one collection) | Medium if read as general Urdu IR |
| Dense MiniLM not a substitute on n=78 | Table 2 | all | **Strong** for those indexes | Low; not Phase 12 |
| e5-small not built (CPU gate) | methods | publication | Process fact | Medium — missing modern dense baseline |
| Clopper–Pearson intervals | computed from counts | publication | **Strong** | Low |
| “Post-freeze development work exists… not part of these official scores” | true | publication limitations | **Under-specified** | **High** if reviewer opens `research/post-phase12` |
| “Adaptive” / “dynamic” as scientific properties | not demonstrated beyond script switch | — | **Unsupported** as IR-theory claims | **High** |
| robust / scalable / generalizable / superior / significant / novel / SOTA | **not claimed** in body | publication | Good restraint | — |

---

## 15. Reviewer #1 Simulation

**Summary.** This manuscript reports a frozen two-index BM25 news retriever for Urdu, with Unicode script detection sending Roman queries to a romanized document index. Development known-item Hit@5 is high (68/78). A sealed known-item set and a sealed human usefulness set are lower (27/40 and 23/40), with a large native-script vs Roman gap. The authors refuse to average these figures and do not claim SOTA. The work is a careful measurement study wrapped in routing language.

**Strengths**

- Protocol hygiene: freeze hashes, seal-before-retrieval, no test tuning, metrics not mixed.
- Honest Roman failure on K/U rather than hiding it.
- Development comparators (Urdu-only BM25, MiniLM variants) on a shared n=78 pool.
- Clopper–Pearson intervals; A2 reliability with A1 retained.
- Dataset provenance and non-redistribution are discussed more candidly than typical student IR papers.

**Major concerns**

1. **Construct mismatch.** The title promises adaptive dynamic routing. The system is a deterministic script detector. Historical SVM routing underperformed a word-count baseline. The contribution should be named for what was measured.
2. **Unseen evaluation does not isolate the router.** Phase 12 shows Method D failing on ordinary Roman, not that routing beats a declared no-routing baseline on K/U.
3. **Official usefulness labels are author-judged** on author-written queries. A2 is helpful but moderate five-way κ and no adjudication.
4. **n=40** (and n=12 Roman K) cannot support precise operational claims. Mixed n=4 is anecdotal.
5. **Public unmerged `research/post-phase12`** contains later M0 development scores (19/50, 12/50) and failed lexical interventions. The paper’s one-sentence nod is insufficient if reviewers inspect the repository.
6. **Development Roman success is construction-matched** to Method D. RQ1 is narrower than a casual reader will think.

**Minor concerns**

- Freeze manifest still lists H001–H040 as the test set.
- No McNemar / paired test on development comparators.
- Near-duplicate wires; ExactSource vs Success@5 respond oppositely.
- Default GitHub branch is `main`, not the publication branch.
- e5-small not built; acceptable if the paper stays lexical, still a reviewer poke.

**Required revisions**

- Retitle and rewrite the abstract contribution sentence to “script-aware BM25” (or equivalent), keeping “routing” only as a defined index choice.
- Add a short “out of scope” paragraph: post-freeze R-dev exists on another branch; not official; not used to retune M0; negative normalizer/RRF ablations.
- Keep A1 official; report A2 as now.
- Optional: one sentence that 10/12 Roman K misses are absent from Top-50 (rerank irrelevant).
- Do not add R-dev to Table 1.

**Recommendation:** **Major revision** (framing + disclosure). Not reject on fabricated results. Not accept with the current title.

---

## 16. Reviewer #2 Attack Simulation

Try to reject the paper. For each attack: evidence, severity, valid/invalid, current defense, required action.

| # | Attack | Evidence | Severity | Valid? | Current defense | Required action |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Novelty: not routing, just BM25 + if/else | M0 detector; SVM lost P@5 | High for title | **Valid** against the title; **invalid** against a measurement paper | Methods define script-conditional routing; Layer A demoted | Retitle / deflate abstract |
| 2 | Methodology: author-written known-item from seen headlines | K protocol | Medium | **Partially valid** (standard known-item, still optimistic) | Seal, no BM25 accept/reject, exclude QTRN sources | Keep; do not call K “user queries” |
| 3 | Baselines: no dense/hybrid on test | Table 2 only n=78; e5 abort; M2-B only on R-dev | Medium | **Valid** if claiming routing SOTA; **weak** if claiming a freeze measurement | Paper refuses SOTA; discloses e5 | Retitle; optional mention of R-dev RRF reject |
| 4 | Evaluation biased toward M0 | `title_roman` = Method D family | High for 87.18% | **Valid** for RQ1 ceiling | Paper already states this | Keep prominence in abstract (already partly there) |
| 5 | Statistics: n=40, no tests | CIs exist; no p-values | Medium | **Invalid** as a reject if CIs stay; **valid** against precise rates | CIs; no p-hack | None required |
| 6 | Human annotation invalid | Dual role; κ=0.55 | High | **Partially valid** | A2; A1 conservative vs A2 | Keep A1; do not overclaim IAA |
| 7 | Dataset: not 1M; rights unclear; SHA unverified vs provider | DAS audits | High editorial / medium scientific | **Valid** as data-policy risk; **invalid** as “wrong n” if SHA of local freeze holds | Honest DAS; no redistribution | Complete provider SHA if possible; no corpus rehost |
| 8 | Not generalizable | News-only; one dump; author queries | Medium | **Valid** | Limitations | Do not add generalization claims |
| 9 | Not reproducible | CSV absent; no clean-clone rerun | Medium | **Partially valid** | REPRODUCE.md; hashes | Keep; don’t claim rerun |
| 10 | Claims inflated | Title vs body | High | **Valid** for title | Body is careful | Fix title/abstract |
| Extra | Hidden worse results on R-dev | 19/50, 12/50 public on another branch | High if found | **Valid as reporting ethics**, **invalid as official-test contradiction** | One limitations sentence | Name and scope out, do not table |
| Extra | Phase 6 says QUERY_AMBIGUITY is the bottleneck | archive PHASE6 | Medium if cited wrongly | **Invalid** against current paper (paper doesn’t use that headline) | Paper uses Roman K/U | Do not revive Phase 6 as main diagnosis |

**Hostile recommendation:** reject for oversold contribution and incomplete reporting of later development. **Fair editor outcome after rebuttal:** major revision if title and GitHub scope are fixed without touching frozen numbers.

---

## 17. Editor Simulation

**If submitted today, three strongest reasons for major revision or rejection**

1. **Mismatch between title/marketing and the actual frozen system**, worsened by public Git history of a failed SVM router.
2. **PLOS data policy / third-party news corpus:** no article-text deposit, redistribution rights unverified, provider SHA not confirmed — editorial hold even if science is honest.
3. **Official human evaluation dual role + small n**, even with A2: usefulness claim is a 40-query author-written sample.

**Risk estimates**

| Outcome | Estimate | Why |
| --- | --- | --- |
| Desk rejection | **Low–moderate (~15–25%)** | Scope fits PLOS ONE; methods exist; DAS and title could still bounce at staff/editor | 
| Major revision | **High (~55–70%)** | Framing, DAS, annotation, baselines-on-test, GitHub extra scores |
| Minor revision | **Low (~10–20%)** | Only if editor reads it as a negative-results measurement paper and likes the honesty |
| Accept as-is | **Very low** | Title + DAS + dual role |
| Scientific readiness of the **freeze** | **High** | Numbers internally consistent |
| Scientific readiness of the **routing contribution** | **Low–moderate** | Not isolated on unseen data |

PLOS ONE is not novelty-first. **Honesty of measurement is an asset.** Overselling routing is the self-inflicted wound.

---

## 18. New Experiment Decision Gate

| Possible experiment | Objection it solves | Central? | Existing evidence? | Reanalysis? | Better text? | Modify frozen M0? | Worth it? | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Urdu-only BM25 on sealed K | Routing not ablated on test | Only if title stays “routing” | Method A 0/23; Roman queries are Latin | **Yes** — run **diagnostic** scorer on K dumps/queries **without** changing official M0 | Partial | No (separate analysis) | Medium | **OPTIONAL reanalysis**; not MUST ADD if retitled |
| Dense retriever on 111,860 docs + K/U | Missing modern baseline | No for a lexical freeze paper | n=78 MiniLM; e5 abort; post-phase12 forbade neural | No | Partial | No if separate system | High cost | **NOT NECESSARY** |
| Module 3 mixed dual-path / Roman matching | Fix Roman | No for *this* paper | Stage 0 points here | No | Future work sentence | Would be a **new** system | High; burns R-dev if selected | **Do not run for this submission** |
| Adjudicate A1/A2 | Soft labels | Partially | Disagreement CSVs exist | Yes (third label) | Limitations already | No | Medium cost | **OPTIONAL**; do not replace A1 |
| Larger U | n=40 | Partially | No | No | CIs already | No | High | **NOT before this paper** |
| Provider SHA of Kaggle/Mendeley | DAS | Editorial | Local SHA exists | Check download | Already disclosed | No | Low–medium | **STRONGLY RECOMMENDED** if download possible; not an M0 experiment |
| McNemar n=78 M0 vs Urdu-only | No significance test | No | Per-query hits exist | **Yes** | Table 2 already large | No | Low | **OPTIONAL P2** |

**MUST ADD new experiment?** **NO.**

---

## 19. P0 — MUST FIX BEFORE SUBMISSION

No P0 requires changing M0, A1, Phase 12 dumps, or Table 1 numbers.

### P0-1 Title and contribution naming

- **Problem:** Title/abstract present “adaptive dynamic query routing.” Official M0 is Unicode script detection + two BM25 indexes. Learned routing was a negative historical result.
- **Evidence:** `.tex` title; `detect_script`; Phase 1 SVM P@5 0.3300 < word count 0.3650; freeze `svm: false`.
- **Branch:** publication manuscript; archive Phase 1; all freeze JSON.
- **Reviewer concern:** Misleading contribution; novelty theater.
- **Proposed fix:** Retitle toward script-aware / dual-index BM25 for Urdu+Roman news search. In the abstract, one sentence: routing = script-conditional index choice, not a learned router. Keep historical SVM only as rejected.
- **Affected publication file:** `Papers/PLOS_ONE/Adaptive_dynamic_query_routing_for_Urdu_information_retrieval.tex` (title, abstract, conclusions first sentence). Short title. Optionally README.
- **Validation:** wording only; no metric change.
- **New experiment required?** **NO**

### P0-2 Public post-freeze development must be scoped in the paper

- **Problem:** `research/post-phase12` is public and reports M0 R-dev 19/50 KI and 12/50 NAT plus failed Modules 1–2. Publication limitations: one vague sentence.
- **Evidence:** `MODULE1_RESULTS.md`, `MODULE2_RESULTS.md`, `ERROR_TAXONOMY.md`, `M3E_RESULTS.md` on `research/post-phase12`.
- **Branch:** `research/post-phase12` (evidence); publication `.tex` (missing detail).
- **Reviewer concern:** Selective reporting / hidden worse scores.
- **Proposed fix:** Limitations paragraph: after the freeze, a **separate development** set (R-dev) was built on another branch for candidate interventions; it is **not** an official test; M0 was **not** retuned on it; small normalizers and two lexical alternatives did not replace M0; scores from R-dev are **not** combined with 23/40. Do **not** put 19/50 in Table 1.
- **Affected publication file:** `.tex` Limitations (and optionally S3 File / REPRODUCE.md pointer to branch name).
- **Validation:** text review; confirm no Table 1 edit.
- **New experiment required?** **NO**

---

## 20. P1 — STRONGLY RECOMMENDED

### P1-1 Dual-role A1 prominence

- **Problem:** Official 57.50% is author-query + author-label.
- **Evidence:** methods Human relevance protocol; AGREEMENT.md §2.
- **Branch:** publication.
- **Reviewer concern:** Biased usefulness.
- **Proposed fix:** One explicit abstract/limitations reminder (A2 does not remove dual role). Keep 23/40.
- **Affected file:** `.tex`
- **Validation:** wording.
- **New experiment required?** **NO** (optional later adjudication)

### P1-2 Provider SHA / DAS completeness

- **Problem:** Local freeze SHA is strong; identity to Kaggle/Mendeley download unproven; rights unverified.
- **Evidence:** manuscript Corpus / DAS; `DATASET_REPRODUCIBILITY_AUDIT.md`.
- **Branch:** publication audits.
- **Reviewer concern:** PLOS data policy.
- **Proposed fix:** If a provider file can be downloaded, hash it. If not, keep the current “not completed” sentence — do not invent a match.
- **Affected files:** `.tex` DAS; `S3_file.md` if a hash is obtained.
- **Validation:** hash comparison only.
- **New experiment required?** **NO**

### P1-3 Default branch vs publication branch

- **Problem:** `origin/HEAD` → `main`. Reviewers cloning the repo miss A2/SI and also miss R-dev.
- **Evidence:** `git remote show` / `origin/HEAD -> origin/main`.
- **Branch:** GitHub settings, not a science file.
- **Reviewer concern:** Cannot find the submission artifacts.
- **Proposed fix:** README “For the PLOS ONE submission use `publication/plos-one-final`.” Do not merge post-phase12 into publication.
- **Affected file:** `README.md`
- **Validation:** clone instructions.
- **New experiment required?** **NO**

### P1-4 Routing ablation on K as text or optional diagnostic

- **Problem:** Unseen set does not show detector value vs always-Urdu.
- **Evidence:** Table 2 only n=78.
- **Proposed fix:** Prefer P0 retitle. If title kept, add a **non-official** diagnostic (separate script, do not overwrite M0 artifacts).
- **Affected files:** `.tex` Discussion; optionally a new analysis note under `publication_audit/` — **not** Phase 12 folders.
- **New experiment required?** **NO** if retitled; **optional diagnostic** otherwise.

### P1-5 Freeze JSON `test_set: H001-H040`

- **Problem:** Stale field vs K/U.
- **Evidence:** `FINAL_SYSTEM_MANIFEST.json`; S1 caption already warns.
- **Proposed fix:** Do **not** rewrite the historical JSON (that is a freeze artifact). Keep the S1 caption; optionally one methods sentence.
- **New experiment required?** **NO**

---

## 21. P2 — MINOR

- Phase 5 selection on n=13 DEV Roman — already in S3 Table; mention small n once in methods if not obvious.
- No McNemar on Table 2 — optional reanalysis.
- 644 duplicate headlines / 4 duplicate bodies — already “no dedup”; optional footnote.
- `bm25_score` A2 round-trip — already in AGREEMENT.md.
- Uninformative git commit messages.
- Archived Phase 6 path vs freeze `reference_runners`.
- Fig 3 Left/Right vs A/B (prior figure audit) — production, not science.
- Mixed n=4: already “descriptive only.”
- Historical IEEE/thesis trees still in repo — clutter, not contradiction.
- Stale lines in `DAS_RECOMMENDATION.md`, `REPRODUCIBILITY_STATUS.md`, and `DATASET_REPRODUCIBILITY_AUDIT.md` still say the live DAS claims GitHub + unrestricted redistribution, and/or that `run_phase5.py` still imports archived `retrieve.py`. The publication `.tex` DAS is already conservative; `run_phase5.py` on this branch already inlines `transliterate_roman`. Refresh those audit docs in a packaging pass so they do not re-open fixed issues. Do not rewrite M0 logic.
- Layer A SVM `.pkl` is absent from git. Safe to leave unrepaired for this lexical paper; do not restore it into official M0.

---

## 22. P3 — SAFE TO LEAVE

- Official 68/78, 27/40, 23/40, A2 26/40, kappas, BM25 parameters, routing table, dictionary size, corpus SHA as reported.
- A1 remaining official.
- Not merging `research/post-phase12` into the publication branch.
- Not running Module 3, dense K/U, or dictionary expansion from failures.
- Not averaging metrics.
- Not claiming CURE/MS MARCO SOTA.
- Layer A SVM/MiniLM staying non-official.
- H001–H040 remaining diagnostic.
- `plos2025.bst` untouched (out of this audit’s edit set).

---

## 23. Publication Revision Map

| Change | File | Science freeze impact |
| --- | --- | --- |
| Retitle + abstract contribution sentence | `.tex` | None on numbers |
| Limitations: name `research/post-phase12` R-dev as out-of-scope | `.tex` | None |
| Optional: Top-50 ABSENT ⇒ rerank irrelevant | `.tex` Discussion | None (uses existing K ranks) |
| README: clone publication branch | `README.md` | None |
| Provider SHA if obtained | `.tex` / S3 File | None unless hash **differs** (then DAS crisis — do not silently ignore) |
| Do not edit | M0 code, qrels, K/U CSVs, Phase 11 JSON, Table 1 counts, A1 labels, A2 labels, figures’ scientific content | Frozen |

**Do not copy** R-dev 19/50 or 12/50 into Table 1. **Do not** replace 23/40 with 26/40.

---

## 24. Final Scientific Verdict

The complete research history **supports** the publication manuscript’s **numerical** claims and its **Roman-limitation** interpretation. It does **not** support the **title-level** claim of adaptive dynamic query routing as a methodological contribution. Unmerged post-phase12 work **agrees** that small lexical patches fail and that Roman/MIXED remain hard; it is a reporting-ethics issue, not a secret contradiction of 23/40.

**Minimum defensible paper:** a frozen script-aware BM25 Urdu news retriever, hashed and sealed, with three non-exchangeable evaluations, and a measured failure of ordinary Roman Urdu.

**Minimum work before PLOS ONE:** fix naming (P0-1) and GitHub-scope disclosure (P0-2). No new official experiment. No merge. No metric surgery.

Status after this audit (science unchanged):

`REFERENCES` and other packaging stages are out of scope here.

**Scientific readiness for submission after P0 wording/disclosure only:** **conditionally ready**.  
**Scientific readiness with current title and silent R-dev:** **not ready**.

---

# TOP 10 ACTIONS

1. **Retitle** the manuscript to match M0 (script-aware dual BM25 / Unicode index selection). Remove “adaptive dynamic” as the scientific headline. **No experiment.**
2. **Rewrite the abstract contribution sentence** the same way; keep 68/78, 27/40, 23/40 un-averaged. **No experiment.**
3. **Add a limitations paragraph** naming `research/post-phase12` R-dev as post-freeze **development**, not official, not combined with Table 1, M0 not retuned. **No experiment. Do not merge the branch.**
4. **Point README** at `publication/plos-one-final` as the submission branch. **No experiment.**
5. **Keep A1 = 23/40 official**; keep A2 as reliability; do not adjudicate unless a later revision asks. **No experiment.**
6. **If the title is not changed**, run a **non-official** Urdu-only diagnostic on K (do not touch M0 artifacts). Prefer changing the title instead.
7. **Attempt provider SHA** of Kaggle/Mendeley vs local precursor; record match or “still unverified.” **No M0 change.**
8. **Add one Discussion sentence** from existing K ranks: most Roman known-item misses never enter Top-50, so reranking the current list cannot fix them. **No experiment.**
9. **Do not revive Phase 6 QUERY_AMBIGUITY** as the paper’s main bottleneck. **No experiment.**
10. **Do not run Module 3, dense retrieval, or dictionary expansion** for this submission. Those are a **different paper** after a new sealed unseen set.

---

# PUBLICATION BRANCH PROTECTION

Verified at end of audit:

| Check | Result |
| --- | --- |
| Scientific files modified (M0, qrels, Phase 12 dumps, metrics JSON, `.tex` results) | **No** (audit markdown only) |
| Manuscript results changed | **No** |
| A1 labels changed | **No** |
| Phase 12 artifacts changed | **No** |
| Branches merged | **No** |
| Commits cherry-picked | **No** |
| Metrics manipulated | **No** |
| Other branches checked out | **No** (`git show` / `git ls-tree` only) |

Working branch remained `publication/plos-one-final`.

`NO SCIENTIFIC RESULTS CHANGED`

---

## Appendix A — Frozen numbers cross-check (publication vs artifacts)

| Quantity | Publication | Artifact | Match |
| --- | --- | --- | --- |
| Corpus n | 111,860 | freeze manifest | Yes |
| k1 / b | 1.5 / 0.75 | freeze / K_RESULTS | Yes |
| Dictionary keys | 198 | K_RESULTS | Yes |
| n=78 Hit@5 | 68/78 = 87.18% | Phase 6/11 | Yes |
| nDCG@5 / MRR n=78 | 0.8107 / 0.797 | Phase 6 | Yes |
| K Hit@1/5/10/50 | 20/27/28/30 of 40 | `K_RESULTS.md` | Yes |
| U Success@5 A1 | 23/40 | `metrics.json` | Yes |
| U P@5 / nDCG@5 / MRR | 0.2050 / 0.6460 / 0.4542 | `metrics.json` | Yes |
| A2 Success@5 | 26/40 | AGREEMENT.md | Yes |
| Five-way / binary κ | 0.5490 / 0.6816 | AGREEMENT.md | Yes |

R-dev 19/50 and 12/50 are **not** publication official numbers and were **not** copied into the manuscript by this audit.

---

## Appendix B — Follow-up confirmation

Independent read-only passes on the manuscript, Phase 12 tree, and three-branch file map agreed with this audit: official K/U numbers match; title vs Unicode detector is the main claim tension; QUERY_AMBIGUITY-family labels are Phase 6 (n=10), not Phase 12; `research/post-phase12` holds R-dev / Modules 1–2 / M3-E, which publication correctly did not promote into Table 1. No P0/P1 change. P2 now records stale DAS/repro audit wording versus the already-conservative `.tex` and the inlined `transliterate_roman` helper.
