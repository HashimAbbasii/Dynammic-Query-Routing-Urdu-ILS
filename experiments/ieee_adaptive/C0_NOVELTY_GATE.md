# C0 Novelty Gate

**Status:** Investigation complete — feasibility assessment only (not a novelty claim)  
**Branch:** `research/roman-urdu-adaptive-retrieval`  
**HEAD:** `3b2e829bf9769d16f9b604ee68d7cc50ce128fa7`  
**Date (local):** 2026-09-22  
**TEST:** sealed; query contents not accessed  
**Program A / Program B frozen files:** read-only; not modified  

---

## 1. Research Question

Is there a **defensible research novelty opportunity** for a future Program C that would:

> detect Roman Urdu–specific query characteristics or failure modes and dynamically select complementary retrieval representations for **Urdu-script news** retrieval?

This gate does **not** implement a router, train a classifier, tune parameters, evaluate TEST, or claim novelty. It asks whether further methodology work is justified.

Hypothesized representations (word BM25, character n-grams, transliteration-aware, phonetic, multilingual dense) remain **hypotheses only**.

---

## 2. Repository State

| Check | Result |
| --- | --- |
| Branch | `research/roman-urdu-adaptive-retrieval` (tracks `origin/...`) |
| HEAD | `3b2e829bf9769d16f9b604ee68d7cc50ce128fa7` |
| Working tree at start | clean |
| Program A entrypoint (frozen) | `experiments/phase5_roman_urdu/run_phase5.py` — **not modified** |
| Program B SoT (frozen) | `experiments/ultra_v2/PHASE14_FINAL_REPORT.md` — **not modified** |
| Orientation docs used | Root `README.md`; Program B `PROTOCOL.md` / phase reports. `PROJECT_ORIENTATION.md` was **not present** on this branch snapshot |
| TEST seal (metadata only) | `benchmark/test/seal.json`: `queries_kn.csv` (6572 B), `queries_nl.csv` (7209 B); `aggregate_sha256=48610601209c3723…`; README documents seal. **Query CSV contents not opened** |

Program C does not yet exist as a system. This directory (`experiments/ieee_adaptive/`) is a new investigation workspace only.

---

## 3. Literature Search Scope

Targeted searches (not exhaustive of all IR) covered ACL Anthology, arXiv, ACM DL / SIGIR, IEEE (CURE), Cambridge UP (NLE), FIRE/DCU reports, and related venues, with emphasis on **2023–2026** plus foundational older work.

| Area | Example query themes |
| --- | --- |
| A. Roman Urdu IR | Roman Urdu information/document/news retrieval; Romanized Urdu IR |
| B. Roman Urdu NLP | Normalization, transliteration, spelling variation, phonetic encoding, code-switching |
| C. Transliteration-aware / cross-script IR | Mixed-script IR; romanized→native; Arabizi; FIRE transliteration search |
| D. Adaptive retrieval | Query-adaptive / sparse–dense routing; mixture of retrievers; learned selection |
| E. Difficulty / failure prediction | QPP; failure prediction; dynamic strategy selection |
| F. Character / phonetic IR | Character n-gram BM25; phonetic query expansion; spelling-robust retrieval |

**Limitation:** Absence from searched literature ≠ proof of non-existence. Claims below use careful language.

---

## 4. Closest Existing Work

### 4.1 Roman Urdu IR (strongest same-language IR prior)

- **Butt, Varanasi & Neumann (2025)** — *Roman Urdu as a Low-Resource Language: Building the First IR Dataset and Baseline* (LowResNLP @ RANLP). Large Roman Urdu MS MARCO–style collection via EN→UR→Roman multi-hop; BM25 + mT5 reranker. Claims first dedicated Roman Urdu IR dataset/baseline.  
  **Critical difference vs Program C setting:** retrieval is **Roman Urdu ↔ Roman Urdu passages**, not Roman queries over **Urdu-script news**.

### 4.2 Roman Urdu → Urdu news / CLIR-adjacent

- **UIR-21 hybrid-query CLIR (JCBI)** — Supports Urdu / English / Roman-Urdu queries over Urdu news (UIR-21), with separate URM/ERM/RURM modes and precision/recall reporting.  
  **Difference:** Fixed per-mode pipelines / hybrid query modeling; **not** failure-type detection + dynamic representation selection among complementary first-stage experts.

- **ULTRA Program A (frozen M0)** — Script-aware routing: Unicode detector → Urdu BM25 vs Method-D romanized BM25. Script routing ≠ Roman Urdu failure-mode–aware multi-representation selection.

- **ULTRA Program B (frozen Phases 2–14)** — Empirical Roman KN → Urdu-script news study (BM25 Method D, NG3, dense e5-small, Hybrid RRF, entity/cascade variants). Fixed methods; Phase 14 SoT. Motivation for Program C, not prior published “adaptive Program C.”

### 4.3 Transliteration / mixed-script IR (Indic & general)

- **Gupta et al. (SIGIR 2014)** — Mixed-script IR; joint deep model for cross-script term matching + spelling variation; query expansion. Hindi/Indic-heavy MSIR framing.  
- **FIRE transliteration search / DCU@FIRE-2014** — Normalization + fuzzy matching for mixed-script Hindi lyrics.  
- **Phonetic QE for transliterated Hindi (ACM TALLIP / related)** — Phonetic encodings (Hindex, etc.) + BM25/TF-IDF for lyrics.  
- **Darwish et al.–style cross-script (Arabizi)** — Native-script queries ↔ Romanized Arabic microblogs via mapping/selection.  

These establish that **transliteration-aware / mixed-script IR is mature** for Indic/Arabic settings. They typically use **fixed** expansion/normalization/phonetic bridges, not RU news failure taxonomy → retriever routing.

### 4.4 Roman Urdu NLP (representation, not adaptive IR)

- **Khan et al. (NLE 2020)** — UrduPhone + Lex-Var clustering for Roman Urdu lexical normalization.  
- **Transformer transliteration Roman↔Urdu (e.g. 2025 arXiv)** — Sequence models for script conversion; IR is a *cited motivation*, not an adaptive retrieval method.  
- Sentiment/MT/opinion mining (RUOMIS, parallel corpora) — Not first-stage news IR.

### 4.5 Adaptive / query-dependent retriever selection (crowded)

- **Arabzadeh, Yan & Clarke (CIKM 2021)** — Per-query classifier selecting sparse vs dense vs hybrid (efficiency/effectiveness) on MS MARCO.  
- **LiteGator (2025)** — Lightweight SVM routing sparse vs dense from shallow query (+ BM25) features.  
- **MoR (EMNLP 2025)** — Mixture of sparse/dense/(human) retrievers with pre- and post-retrieval weighting.  
- **LTRR / RouterRetriever / Adaptive-RAG (2024–2025)** — Learned retriever ranking / complexity-based strategy selection for RAG.  

**Conclusion:** Query-dependent sparse/dense/(hybrid) selection is **already established** in English/general IR.

### 4.6 Query performance prediction / failure awareness

- **Carmel & Yom-Tov (2010)** — Foundational QPP / query difficulty.  
- **Arabzadeh et al. (CIKM 2023; ECIR tutorial 2024)** — Dense QPP; modern QPP surveys.  
- Post-retrieval score statistics, agreement/divergence signals used for weak-retrieval prediction in recent applied work.  

QPP predicts *difficulty* or *utility*, usually for a fixed retriever or for cost-aware routing — **not** a Roman Urdu linguistic failure taxonomy (ROOM / ENT / VOCAB / …) mapped to representation choice for Urdu-script news.

### 4.7 Character n-gram / phonetic retrieval

- Classic **character n-gram** robustness to transliteration/spelling (e.g. Hindi n-gram tech reports; widespread BM25-char practice).  
- Program B **R2-NG3** already evaluated char-3gram BM25 on Method-D tokens (partially supported; weak overall; some unique recoveries).

---

## 5. Novelty Matrix

| Work | Year | Roman Urdu? | IR? | Urdu-script target? | Transliteration / mixed-script? | Adaptive? | Query-specific routing? | Multiple representations? | Failure-aware (linguistic)? | Main difference vs Program C hypothesis |
| --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Butt et al. LowResNLP | 2025 | Yes | Yes | No (Roman passages) | Synthetic transliteration pipeline | No | No | BM25 + mT5 rerank | No | Same-script Roman IR dataset/baseline |
| UIR-21 / JCBI hybrid query | ~2022 | Query modes yes | Yes | Yes (news) | Query translation / multi-mode | Unclear (modes, not learned router) | Per-mode, not failure router | Multi-language modes | No | Fixed CLIR modes, not RU failure→rep selection |
| ULTRA Program A M0 | frozen | Script detect | Yes | Yes | Method D romanization | Script-level only | Script detector | 2 BM25 indexes | No | Script routing ≠ failure-type routing |
| ULTRA Program B Phases 2–14 | frozen | Yes | Yes | Yes | Method D / NG3 / dense | No (fixed / failed cascades) | No | Yes (evaluated) | Diagnostic taxonomy only | Empirical motivation; no adaptive method |
| Gupta et al. SIGIR | 2014 | No (Indic MSIR) | Yes | Native+Roman mixed | Yes (core) | No | No | Joint embedding + QE | Spelling variation, not RU taxonomy | Mixed-script QE, not adaptive multi-retriever |
| FIRE / DCU 2014 TST | 2014 | No (Hindi lyrics) | Yes | Mixed | Normalization + fuzzy | No | No | Fuzzy + LM/BM25 | No | Fixed normalization |
| Khan et al. NLE UrduPhone | 2020 | Yes | No (normalization) | N/A | Phonetic encoding | No | No | Clustering variants | Lexical variation clustering | NLP resource, not IR router |
| Arabzadeh et al. CIKM | 2021 | No | Yes | N/A (MS MARCO) | No | Yes | Yes (sparse/dense/hybrid) | Yes | Cost/utility, not RU linguistics | Generic adaptive selection |
| LiteGator | 2025 | No | Yes (QA) | N/A | No | Yes | Yes | Sparse/dense | Shallow features | Generic light router |
| MoR EMNLP | 2025 | No | Yes | N/A | No | Yes | Yes (mixture weights) | Many retrievers | QPP-like signals | Generic MoE retrieval |
| Carmel & Yom-Tov | 2010 | No | Meta | N/A | No | Indirect | Indirect | N/A | Difficulty prediction | Foundational QPP |
| Char n-gram IR (classical + hybrid char+dense) | 1997–2025 | Rarely RU | Yes | Varies | Often spelling/translit robust | Usually fixed hybrid | Rare | Char + dense common | Orthographic noise | Representation exists; adaptive RU news gap remains |

**Unclear cells:** Exact internal architecture of the JCBI UIR-21 “hybrid query model” beyond reported URM/ERM/RURM modes was not fully reconstructable from available text; marked as mode-based rather than confirmed learned failure router.

---

## 6. What Is Clearly Not Novel

The following **cannot** carry a Program C novelty claim by themselves:

- BM25 / Okapi  
- Multilingual dense retrieval (e.g. e5-family)  
- Character n-gram sparse retrieval  
- Phonetic encoding / lexical normalization for Roman Urdu (UrduPhone line)  
- Transliteration or mixed-script query expansion (Gupta/FIRE line)  
- Fixed BM25 + dense hybrid / RRF  
- Generic “adaptive retrieval”  
- Generic query-dependent sparse vs dense vs hybrid selection (Arabzadeh; LiteGator; MoR)  
- Generic QPP / query difficulty prediction  
- Script detection routing (already Program A)  
- “Roman Urdu IR exists” as a claim (Butt et al. 2025; UIR-21 modes; Program A/B)

---

## 7. Potential Research Gap

### Explicit Q&A

**Q1. Has Roman Urdu retrieval already been studied?**  
**Yes.** Strongest recent IR baseline: **Butt et al. (2025)** (Roman↔Roman MS MARCO-style). Earlier/adjacent: UIR-21 Roman-Urdu query mode; Program A/B in this repo.

**Q2. Has Roman Urdu → Urdu-script retrieval already been studied?**  
**Yes, in limited forms.** UIR-21 reports Roman-Urdu query modes over Urdu news; ULTRA Program A/B study Roman queries against Urdu-script news (Method D / dense / hybrids). Not an empty problem.

**Q3. Has transliteration-aware retrieval for Roman Urdu already been studied?**  
**Partially.** Dedicated RU IR papers emphasize transliteration *pipelines* and lexical BM25 weakness; mixed-script IR is strong for **Hindi/Indic** and Arabizi. A polished, failure-aware *adaptive* transliteration+dense+char stack for **RU→Urdu news** was **not identified** as an existing packaged method.

**Q4. Has adaptive retrieval already been studied?**  
**Yes** — extensively.

**Q5. Has query-dependent sparse/dense retriever selection already been studied?**  
**Yes** (Arabzadeh 2021; LiteGator 2025; MoR 2025; related RAG routers).

**Q6. Has linguistic failure-type-aware retriever selection already been studied?**  
**Not in the Roman Urdu → Urdu-script news sense found here.** Closest are generic complexity/QPP routers and orthographic/mixed-script *fixed* expansions. No directly matching work was identified that (i) defines RU-specific failure types, (ii) detects them from the query (or query+cheap signals), and (iii) selects complementary representations for Urdu news.

**Q7. Has this exact combination already been proposed?**  

> A Roman-Urdu-specific system that identifies query characteristics/failure modes and dynamically selects complementary retrieval representations for Urdu-script news retrieval.

**No directly matching work was identified in the searched literature.**  
This is **not** a claim that “this has never been done.”

### Potentially novel intersection (feasibility, not claim)

A **narrow** intersection *may* be defensible **if and only if** Program C is framed as more than “Arabzadeh on Roman Urdu”:

1. Roman Urdu linguistic variability under Method-D / Urdu-script indexing (ROOM / ENT / VOCAB-class phenomena from Program B),  
2. **Detectable** query-side (or cheap pre-retrieval) signals for those modes,  
3. Representation selection that **beats strong fixed baselines** (Dense @ Hit@5; Hybrid @ Hit@50) **and** naive always-on fusion (Phase 8 showed 3-way RRF *hurts*),  
4. Clear differentiation from script-only routing (Program A) and from same-script Roman IR (Butt 2025).

Without (2)–(3), the gap collapses to an incremental application of known adaptive IR.

---

## 8. Program B Empirical Motivation

From frozen Phase 14 / phase reports (TRAIN+DEV only; TEST unused):

| Finding | Evidence |
| --- | --- |
| Lexical Method D near floor | n=80 Hit@5 **5/80**; n=51 **4/51** |
| Dense strongest single @ Hit@5 | n=80 **20/80**; n=51 **15/51** |
| Hybrid strongest deployable @ Hit@50 | n=80 **40/80**; n=51 **25/51** |
| NG3 narrow lexical bridge | n=51 Hit@5 **6/51**; unique dual-miss recoveries (e.g. KN035, KN050) |
| Fixed 3-way RRF fails | Phase 8: Hit@5 **11→8** vs Hybrid — **UNSUPPORTED** |
| Cascade / Option B fails or ≡ Hybrid | Phase 10 / 10b |
| Failure taxonomy exists (diagnostic) | R2-B0: ROOM 19, ENT 16, VOCAB 9, RANK 2, NEIGH 1 of 47 Hit@5 failures |
| Large residual dual/all misses | Phase 11 VOCAB dual-misses; Phase 6 Quad-23 four-way misses |

**Motivation for adaptivity:** different representations recover different queries; always-on fusion is not automatically better (Phase 8).  
**Motivation against naive Program C:** many failures are shared across all current experts; routing alone cannot invent missing paraphrase/acronym bridges.

---

## 9. Recovery Complementarity

Computed **read-only** from frozen per-query CSVs (`HYBRID_PER_QUERY.csv`, `R2NG3_PER_QUERY.csv`, `DENSE_PER_QUERY.csv`, Phase 13 scoring CSV). **No new retrieval. No TEST. Query text not printed.**

### 9.1 n=51 Hit@5 (B=BM25, N=NG3, D=Dense, H=Hybrid)

| Pattern (B N D H) | Count |
| --- | ---: |
| All miss `0000` | 29 |
| Dense+Hybrid only `0011` | 7 |
| Dense only (Hybrid miss) `0010` | 7 |
| Other mixed patterns | 8 |

Notable discordances:

| Phenomenon | n | Query IDs (IDs only) |
| --- | ---: | --- |
| Dense Hit@5, BM25 miss | 15 | KN011, KN013, KN016, KN017, KN019, KN029, KN031, KN033, KN034, KN039, KN046, KN048, KN049, KN052, KN053 |
| BM25 Hit@5, Dense miss | 4 | KN004, KN012, KN023, KN038 |
| NG3-only vs BM25∧Dense | 2 | KN035, KN050 |
| Dense Hit@5, Hybrid miss | 7 | KN013, KN019, KN031, KN033, KN039, KN052, KN053 |
| NG3 Hit@5, Hybrid miss | 3 | KN035, KN038, KN050 |
| BM25 Hit@5, Hybrid miss | 2 | KN012, KN038 |

**Oracle / pool upper bounds (n=51 Hit@5):**

| Selector | Hit@5 |
| --- | ---: |
| Hybrid RRF (fixed) | **11/51** |
| Dense alone | **15/51** |
| Union BM25∪Dense | **19/51** |
| Oracle best-of {BM25, NG3, Dense} / Union of three | **21/51** |
| Queries where best single expert > Hybrid | **11** |

→ At Hit@5, **fixed Hybrid is not the oracle**; selecting Dense (or NG3) on some queries has clear headroom.

**Hit@50:** Hybrid **25/51**; Union of three **28/51** (NG3-only KN035, KN050; Dense-only Hybrid-miss KN040). Headroom for *pool* expansion among current experts is **small**.

### 9.2 By frozen `r2_primary` labels (n=51 Hit@5 counts)

| Category | n | BM25 | NG3 | Dense | Hybrid |
| --- | ---: | ---: | ---: | ---: | ---: |
| SUCCESS | 4 | 4 | 3 | 0 | 2 |
| ROOM | 19 | 0 | 1 | 4 | 2 |
| ENT | 16 | 0 | 1 | 7 | 3 |
| VOCAB | 9 | 0 | 1 | 3 | 2 |
| RANK | 2 | 0 | 0 | 1 | 2 |
| NEIGH | 1 | 0 | 0 | 0 | 0 |

Dense recovers more ENT/ROOM than BM25; SUCCESS cases are BM25-favoring (Dense **0/4** Hit@5). This **suggests** specialization aligned with failure modes — but labels were assigned with gold-aware diagnostics, so they are **not** proof that modes are detectable from the query alone.

### 9.3 n=80 confirmatory (Phase 13 scoring, frozen)

| Method | Hit@5 | Hit@50 |
| --- | ---: | ---: |
| BM25 | 5/80 | 13/80 |
| NG3 | 10/80 | 19/80 |
| Dense | **20/80** | 36/80 |
| Hybrid | 17/80 | **40/80** |
| Union B∪N∪D | **28/80** | **49/80** |
| Oracle best-of-3 Hit@5 | **28/80** | — |
| Oracle > Hybrid @ Hit@5 | **13** queries | — |

Dense-only vs BM25 @ Hit@5: **19**; BM25-only: **4**; NG3-only vs both: **4**; Dense-hit Hybrid-miss @ Hit@5: **7**.

### 9.4 Does evidence support “different retrievers specialize in different Roman Urdu failure modes”?

| Verdict | Detail |
| --- | --- |
| **Partial yes (complementarity)** | Clear discordant recoveries BM25↔Dense; NG3 unique dual-misses; oracle ≫ Hybrid at Hit@5 |
| **Weak on taxonomy→routing** | Category table is suggestive; detectability unproven; gold-informed labels |
| **Strong counter on fusion** | Phase 8: always adding NG3 via RRF **harms** Hit@5 — selection must be selective, not “more lists” |
| **Hard ceiling** | **29/51** all-miss @ Hit@5 among these experts — adaptive choice among current reps cannot fix the majority tail |

---

## 10. Threats to Novelty

1. **Crowded adaptive-IR literature** — Reviewers may dismiss “route sparse/dense/hybrid” as Arabzadeh/MoR applied to a new language.  
2. **Butt et al. 2025** — Already frames Roman Urdu IR as a first dataset/baseline story; Program C must not claim “first RU IR.”  
3. **Mixed-script IR (Gupta/FIRE)** — Spelling/transliteration robustness is old; phonetic/char bridges are known.  
4. **Program A script routing** — Easy to confuse with “adaptive.” Must sharply separate script detection from failure-mode representation selection.  
5. **Combination novelty** — Merely stacking known components is weak unless detectability + gains over Dense/Hybrid/oracle-gap closure are shown.  
6. **Label leakage** — Program B failure categories used gold overlap; a detector trained on those labels may not be deployable.  
7. **Small n** — n=51 / n=80 underpowers routing classifiers; risk of overfit “novelty.”  
8. **Phase 8 / 10 negatives** — Empirical record already shows *bad* multi-rep strategies; Program C must explain why selective routing differs.  
9. **Residual paraphrase/acronym gap** — Phase 11 shows cases no current expert recovers; routing cannot create new evidence.  
10. **Venue risk** — Without a crisp mechanism (detectable RU features → representation policy with ablations), the contribution looks empirical-engineering, not methodological.

---

## 11. GO / CONDITIONAL GO / NO-GO

# **CONDITIONAL GO**

---

## 12. Exact Reason for Decision

**Not GO:** The generic adaptive sparse/dense story is already published; Roman Urdu IR already has a 2025 dataset paper and prior CLIR/mode work; Program B already measured the representations. Shipping “a router” as stated would be an incremental combination with high rejection risk.

**Not NO-GO:** Frozen Program B shows **real complementarity** and a large oracle gap at Hit@5 (Hybrid 11 → oracle 21 on n=51; Hybrid 17 → oracle 28 on n=80). Always-on fusion fails (Phase 8), so *selective* use of NG3/Dense/BM25 is empirically motivated. No directly matching **RU failure-aware representation selector for Urdu-script news** was identified in the searched literature.

**CONDITIONAL GO** means: redesign the research question **before** any router/classifier implementation so the contribution is the **detectable Roman Urdu failure/characteristic → representation policy**, with mandatory proofs listed in §13 — not “adaptive retrieval for Roman Urdu” as a slogan.

---

## 13. What Must Be Proven Next

Methodology / diagnostic phase only (still **no TEST**; still **no** full system build until these pass):

1. **Detectability study (TRAIN/DEV only):** Can query-only or cheap pre-retrieval features predict (a) which expert wins, or (b) coarse mode proxies **without** gold-derived labels? Report accuracy vs chance and calibration.  
2. **Oracle gap decomposition:** Separate Hit@5 ranking losses (Dense wins, Hybrid dilutes) from Hit@50 pool gaps (only +3 on n=51). Program C should target the regime where adaptivity has headroom.  
3. **Policy vs fusion:** Preregister comparison to Dense, Hybrid, and (if used) weighted/cascade baselines; explain why Phase 8/10 failure modes are avoided.  
4. **Novelty framing freeze:** Written claim must cite Butt 2025, Gupta 2014, Arabzadeh 2021, MoR 2025, and Program A/B explicitly and state the residual gap in one sentence.  
5. **Negative-result plan:** If detectability ≤ chance or adaptive ≤ Dense/Hybrid on preregistered metrics, **stop** (convert to NO-GO).

---

## 14. What We Must NOT Do Yet

- Implement router / train classifier / feature shop for deployment  
- Implement new representations “because they sound Roman Urdu” without detectability evidence  
- Tune BM25/dense/RRF/cascade parameters for Program C  
- Fuse lists without a selection policy that addresses Phase 8  
- Open or evaluate **TEST**  
- Claim novelty, IEEE acceptance, or “first Roman Urdu IR”  
- Modify Program A or Program B frozen artifacts  
- Treat Program B failure labels as supervised training targets without a leakage analysis  

---

## 15. References

1. Muhammad Umer Tariq Butt, Stalin Varanasi, and Guenter Neumann. 2025. Roman Urdu as a Low-Resource Language: Building the First IR Dataset and Baseline. In *Proceedings of the First Workshop on Advancing NLP for Low-Resource Languages*, pages 82–87, Varna, Bulgaria.  
2. Parth Gupta, Kalika Bali, Rafael E. Banchs, Monojit Choudhury, and Paolo Rosso. 2014. Query Expansion for Mixed-Script Information Retrieval. In *SIGIR ’14*, pages 677–686.  
3. Negar Arabzadeh, Xinyi Yan, and Charles L. A. Clarke. 2021. Predicting Efficiency/Effectiveness Trade-offs for Dense vs. Sparse Retrieval Strategy Selection. In *CIKM ’21*, pages 2862–2866. (Also arXiv:2109.10739.)  
4. MoR: Better Handling Diverse Queries with a Mixture of Sparse, Dense, and Human Retrievers. 2025. In *EMNLP 2025* (ACL Anthology 2025.emnlp-main.601).  
5. LiteGator: lightweight sparse/dense retriever routing with linear SVM (iCAST-ES 2025 proceedings report).  
6. David Carmel and Elad Yom-Tov. 2010. *Estimating the Query Difficulty for Information Retrieval*. Synthesis Lectures on Information Concepts, Retrieval, and Services.  
7. Negar Arabzadeh et al. 2023. Noisy Perturbations for Estimating Query Difficulty in Dense Retrievers. In *CIKM ’23*.  
8. Negar Arabzadeh et al. 2024. Query Performance Prediction: From Fundamentals to Advanced Techniques (ECIR tutorial materials).  
9. Abdul Rafae Khan, Asim Karim, Hassan Sajjad, Faisal Kamiran, and Jia Xu. 2020. A Clustering Framework for Lexical Normalization of Roman Urdu. *Natural Language Engineering*. (UrduPhone / Lex-Var; arXiv:2004.00088.)  
10. DCU@FIRE-2014: Fuzzy Queries with Rule-based Normalization for Mixed Script Information Retrieval. FIRE 2014.  
11. Related phonetic/transliterated text retrieval (Hindi lyrics / Hindex line), ACM / TALLIP literature on query expansion for transliterated text.  
12. Cross-script IR (Arabizi / Romanized Arabic) microblog line (UMass / related reports).  
13. CURE: Collection for Urdu Information Retrieval Evaluation and Ranking (Urdu-script IR benchmark; BM25 baselines) — ICODT / arXiv:2011.00565.  
14. Cross-Lingual Information Retrieval in a Hybrid Query Model… (UIR-21; Urdu/English/Roman-Urdu query modes). *Journal of Computing & Biomedical Informatics*.  
15. Low-resource Roman-Urdu↔Urdu transformer transliteration (e.g. arXiv:2503.21530) — transliteration systems, IR as motivation.  
16. ULTRA Program B Phase 14 Final Report — `experiments/ultra_v2/PHASE14_FINAL_REPORT.md` (frozen empirical SoT).  
17. ULTRA Program B Phase 6 Diagnostics; Phase 5 NG3; Phase 8 3-way RRF; R2-B0 Failure Analysis — frozen complementarity and taxonomy sources used in §§8–9.

---

## Appendix A — Decision summary (one paragraph)

Program C as a vague “adaptive Roman Urdu retrieval” project is **not** ready for implementation: adaptive sparse/dense selection and Roman Urdu IR both already exist. Program B nonetheless shows **complementary recoveries** and an **oracle Hit@5 gap** that fixed Hybrid and naive 3-way fusion do not close. Therefore: **CONDITIONAL GO** — proceed only to a redesigned methodology/diagnostic phase that centers **detectable Roman Urdu query characteristics** and proves gains over Dense/Hybrid with an explicit stop rule; otherwise convert to **NO-GO**.

---

**End of C0 Novelty Gate.**
