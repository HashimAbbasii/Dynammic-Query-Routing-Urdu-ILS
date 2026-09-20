# ULTRA v2 Phase 1 protocol

**Status:** COLLECTED / VALIDATED / TEST SEALED. Phase 2 Roman lexical experiments **STOPPED** (negative result on TRAIN/DEV). No TEST retrieval. No Phase 3.  
**Authoritative document** for the genuine unseen benchmark.  
**Branch:** `research/ultra-v2-strengthening`  
**Does not modify** frozen M0, PLOS results, QTRN, K, U, or H.

If a later idea is dense retrieval, dictionary expansion, fusion, reranking, a new corpus, or chasing 80%: **Bro, this is outside our roadmap. Let's stay on track.**

---

## 1. Research objective

ULTRA v2 must demonstrate that any improvement over frozen M0 **survives genuinely unseen evaluation**.

Phase 12 K/U answered that question for **frozen M0 only**. Those sets are not unseen for v2 because:

| Fact | Consequence |
| --- | --- |
| K and U were sealed, retrieved, labeled, and published | The research team has seen ranks, scripts, and scores |
| K Roman Hit@5 and U Roman/Mixed Success@5 are known | Script-specific failure modes are public |
| Miss lists exist (K not-in-50; U all-D / no A/B) | Mining them for Phase 2 rules is test leakage |
| Annotator 1 wrote U and judged U | Author–judge contamination for that set |
| Phase 12 protocol already said: if the system changes, K/U are burned | ULTRA v2 **is** a system-change program |

Therefore a **new** benchmark is required. The ~80% figure is an aspiration, not a hypothesis test and not a stopping rule.

Frozen PLOS numbers stay historical. They are never rewritten and never averaged into a v2 headline.

---

## 2. Two evaluation tracks

Never average Track KN and Track NL into one unexplained score.

### Track KN — known-item

**Research question:** Can the system retrieve the **intended article**?

| Item | Definition |
| --- | --- |
| Gold | `source_doc_id` assigned at query creation |
| Primary metric | ExactSource Hit@5 |
| Secondary | ExactSource Hit@1, Hit@10, Hit@50 (= Candidate Recall@50), MRR |

Success on KN means the source row is in the cutoff. It does **not** mean the result was useful to a human in a graded sense.

### Track NL — naturalistic

**Research question:** Does the result **satisfy the user’s information need**?

| Item | Definition |
| --- | --- |
| Gold | Human A–E labels on **pooled** candidates. No `source_doc_id` |
| Primary metric | Success@5 = at least one **A or B** in the system’s Top-5 |
| Secondary | P@5, nDCG_useful@5, nDCG_topical@5, MRR (first A/B), Candidate Recall@50 |

Do **not** compute ExactSource Hit@5 on NL. Do **not** compute Success@5 as the primary KN metric.

---

## 3. Script strata

Both tracks record Unicode script **after writing**, using the same detector family as M0 (`URDU` / `ROMAN` / `MIXED` / `OTHER`).

| Stratum | Policy |
| --- | --- |
| Urdu | Required. Native-script needs. |
| Roman Urdu | **Oversampled on purpose.** Declared sampling decision: Roman is a documented M0 weakness. This is **not** a claim about real-world query prevalence. No population search-log evidence is in this repository. |
| Mixed | Genuine user-like mixing only (e.g. Latin named entity + Urdu need). **Do not** glue English templates to balance a table. **Do not** reuse `Pakistan news update`. |

`OTHER` (no Urdu letters, no Latin letters) is allowed if it occurs but is not a target quota.

Minimum **planning** cell sizes (not results): see §15. Mixed cells below the planned minimum are reported as **descriptive**, not as population rates.

---

## 4. Information-need categories

These are **sampling and analysis slices**, not a requirement that every category have equal n. Categories **may overlap**. A query has one **primary** `intent_type` plus optional flags.

**Primary `intent_type` (exactly one):**

| Value | Meaning |
| --- | --- |
| `factoid` | One requested slot (who / when / price / score) |
| `explanatory` | Why / how / effects |
| `entity_person` | Person, team, or named organization as the need |
| `location` | Place-centric need |
| `event` | A specific occasion or incident |
| `topical` | Broader topic without a single slot |

**Orthogonal fields (not extra intent classes invented after results):**

| Field | Values |
| --- | --- |
| `length_bin` | `short` (≤5 whitespace tokens), `medium` (6–12), `long` (13+) |
| `ambiguous` | `0` or `1` — writer marks genuine ambiguity of the need |

Do **not** add new category labels after seeing retrieval scores. Length is not an intent type; it is recorded separately so “short” and “long” from the planning list are not forced into `intent_type`.

---

## 5. Query construction

The infrastructure step created no query text. Collection on 2026-09-09 followed the rules below. The rules remain binding for any later amendment.

### 5.1 Shared bans

Forbidden while writing KN or NL:

- Opening H001–H040, K001–K040, U001–U040, Phase 10C/12 qrels, or Phase 11 token inventories **for inspiration**
- Copying or paraphrasing those strings
- Writing from listed historical misses
- Running BM25, dense search, or corpus keyword search to “find a good article” for NL
- Rewriting after seeing ranks
- Designing queries to make M0 or v2 look strong
- Extending ID namespaces `QTRN_*`, `H*`, `K###`, `U###`

New IDs must be `KN###` and `NL###` (zero-padded, unique across the v2 benchmark).

### 5.2 Track KN

1. Sample a corpus row whose `Index` is **not** a source used by QTRN, K, or any KN already accepted. Exclude H-linked ids if any are later mapped to corpus rows.
2. The writer **may read** the article (required to assign `source_doc_id`).
3. Write a user-like information need for **that** article. Not a copied headline. Not a shortened headline.
4. Assign `source_doc_id` **now**. Never after retrieval.
5. Unique `source_doc_id` per accepted KN query.
6. Compute `headline_overlap` (defined below). Reject if the query fails the overlap rule.
7. Do not run retrieval to accept or reject the source.

**Pre-registered headline-overlap rule**

Let \(Q\) and \(H\) be token sets from the same tokenizer as M0: lowercase matches of `[\u0600-\u06FF]+|[A-Za-z0-9]+`.

\[
\mathrm{headline\_overlap} = \frac{|Q \cap H|}{|Q|}
\]

If \(|Q|=0\), reject the query.

**Reject if `headline_overlap` ≥ 0.50.**

This is a **protocol constant**, not a parameter to tune on DEV scores. Rationale: overlap is the fraction of **query** tokens that already appear in the headline. A shortened headline typically scores near 1.0. Jaccard \(|Q\cap H|/|Q\cup H|\) would let long queries pass even when they still paste the full title; query-coverage is stricter for that failure mode. The 0.50 threshold is a pre-registered starting rule from the Phase 0 audit. Changing it requires a protocol amendment **before** collection, not after seeing Hit@5.

Roman KN queries must be ordinary Roman Urdu of the **need**, not Method D attack strings and not character-table traps.

### 5.3 Track NL

1. Write a genuine bilingual Pakistani news information need.
2. **No** `source_doc_id`.
3. **No** corpus search to find an answer article.
4. Fill script and intent quotas from the collection plan (§15), without forcing Mixed.
5. Query author does **not** tune retrieval systems.

Reject NL drafts that are hidden known-item title copies, duplicates of another KN/NL string, or near-copies of historical U/K needs (same slot + same entity + same constraint). Corpus-level repetition of a famous entity is **not** automatically leakage; copying an inspected U/K **wording or need recipe** is.

---

## 6. Independent authorship and judging

| Role | Rule |
| --- | --- |
| Query writer | Does not inspect system rankings. Does not rewrite after retrieval. |
| Retrieval developer | Does not write TEST queries. Does not judge NL as sole official annotator of queries they wrote. |
| Official NL judge | Not the sole query author. ≥2 independent judges where feasible. |

**Resource limitation (documented):** a master’s project may have few people. If one person must write **and** help judge:

1. **Time separation:** judging happens only after queries are sealed and retrieval dumps exist.
2. **Process separation:** a second judge labels the same pooled set; official Success@5 uses **adjudicated** labels, not author-only labels.
3. Author labels, if collected, are stored as `annotator=author` and are **not** the official primary.

PLOS U used Annotator 1 as author and official judge, with A2 as reliability only. ULTRA v2 must not repeat author-only official labels.

---

## 7. TRAIN / DEV / TEST

Planning split of the **new** collection (not a split of K/U):

| Split | Planning share | Allowed use |
| --- | --- | --- |
| TRAIN | ~40% | Prototypes, failure taxonomy drafts, normalization experiments, debugging, exploratory analysis |
| DEV | ~20% | **All** selection: models, parameters, fusion, reranker, thresholds, dictionary/normalization rules |
| TEST | ~40% | Sealed. Hashed. No tuning. Scored only at pre-registered phase gates and final freeze |

Do not force these percentages if annotation budget cannot support them. If the budget is tight, collect TRAIN+DEV first and seal TEST as a **second wave** so early Phase 2 sketches cannot see TEST.

**QTRN** may be used only as `legacy_m0_dev` sanity checks. It is **not** v2 TRAIN for reported selection decisions.

**K / U / H** are not TRAIN, DEV, or TEST for v2.

---

## 8. TEST sealing and no-peek

Infrastructure: `scripts/seal_test.py` hashes an **explicitly supplied** TEST directory. It does **not** create queries. Every top-level file except `README.md` and `seal.json` is hashed, in sorted filename order. `aggregate_sha256` covers only those file hashes (not timestamp, `created_by`, or notes). `scripts/verify_test_seal.py` recomputes hashes and fails on missing, modified, or **added** data files. Future official eval must refuse to score TEST if the seal mismatches.

A hash does **not** stop a researcher from opening a file. The **operational no-peek rule** is:

After TEST is sealed:

- Do not inspect TEST query text while developing Phases 2–6
- Do not inspect TEST failures
- Do not mine TEST for dictionary entries or normalization rules
- Do not select models, fusion, rerankers, or thresholds on TEST
- Do not rewrite TEST queries
- Do not add queries to compensate for poor TEST scores

If a TEST query is inspected after sealing, set `status=contaminated` and **exclude it from confirmatory claims**. Record the incident in `REGISTRY.md`.

---

## 9. Annotation (summary)

Full text: `annotation/ANNOTATION_GUIDELINES.md`.

Labels follow PLOS A–E (not a 0–3 replacement):

| Code | Official name | Useful for Success@5? |
| --- | --- | --- |
| A | RELEVANT — need satisfied | Yes |
| B | PARTIALLY_RELEVANT — useful with limitation | Yes |
| C | TOPICALLY_RELATED — wrong slot | No |
| D | NOT_RELEVANT | No |
| E | AMBIGUOUS — cannot decide from allowed evidence | No |

**Why E is not “irrelevant”:** irrelevance is **D**. Relabeling E as irrelevant would duplicate D and remove the ambiguity channel required for genuine NL ambiguity (§10). That is a protocol choice, not a metric tweak.

**Success boundary:** `{A,B}` vs `{C,D,E}`. Adjudicate that boundary. Exact A vs B may remain for secondary analysis.

KN primary scoring does not need A–E. Optional graded labels on non-source KN hits are **not** the primary KN metric.

---

## 10. Ambiguous NL queries

Ambiguity can be a property of the **need**, not a retrieval bug (`QAMB`).

Protocol:

1. Writer sets `ambiguous=1` when the need has more than one plausible interpretation.
2. Writer records short `interpretation_notes` (no gold documents).
3. Judges label **per interpretation** when a document is relevant to one valid reading and not another (`interpretation_id`).
4. Query-level Success@5 = 1 if **any** valid interpretation has ≥1 A or B in the system Top-5 (unless a later amendment requires a primary interpretation only — that amendment must precede TEST scoring).
5. Report the `ambiguous=1` slice separately. Do not hide it inside the headline Success@5 without a footnote.

Do not automatically punish a system for returning a document that honestly matches an unintended but valid reading.

---

## 11. Pooling (NL)

Do **not** retrieve in Phase 1. When retrieval exists:

The NL candidate pool for judging is the **union** of Top-50 documents from:

- Frozen M0
- Each v2 system under comparison
- Optionally **one** additional baseline if pre-registered in the registry **before** seeing scores (e.g. Urdu-only BM25)

Judge the pool (or a documented depth cap) **before** treating a system’s Top-5 as fully labeled for Recall@50. Unjudged documents outside the pool are unknown, not D.

---

## 12. Two-stage retrieval reporting

```text
Candidate generation → Top-50 → Candidate Recall@50
Final ranking        → Top-5  → Hit@5 / Success@5
```

| Track | Candidate Recall@50 |
| --- | --- |
| KN | 1 iff `source_doc_id` is in that system’s Top-50 |
| NL | 1 iff at least one **A or B** pooled document is in that system’s Top-50 |

Relevant for NL recall = **A or B**. C does not count.

A reranker **cannot** recover a document that never entered its Top-50. Phase 6 must report Recall@50 and Top-5 separately. Hiding MISS behind RANK is a protocol violation.

---

## 13. Metrics

### KN

| Role | Metric | Definition |
| --- | --- | --- |
| Primary | ExactSource Hit@5 | 1 iff source rank ≤ 5 |
| Secondary | Hit@1, Hit@10, Hit@50 | Same with cutoff 1 / 10 / 50 |
| Secondary | MRR | \(1/r\) for source rank \(r\); 0 if not in list |

Known-item nDCG, if reported, uses binary gain on the source only. It is **not** mixed with NL nDCG.

### NL

| Role | Metric | Definition |
| --- | --- | --- |
| Primary | Success@5 | 1 iff ≥1 A or B in that system’s Top-5 |
| Secondary | Conservative P@5 | (count of **A** in Top-5) / 5, then mean over queries |
| Secondary | nDCG_useful@5 | gains A=3, B=1, C=D=E=0 |
| Secondary | nDCG_topical@5 | gains A=3, B=2, C=1, D=E=0 (**secondary**; can look strong on C-only lists) |
| Secondary | MRR | \(1/r\) of first A or B; 0 if none |
| Secondary | Recall@50 | as §12 |

**nDCG_topical@5 is not a usefulness claim.** PLOS U nDCG used C=1 and could reach 1.0 with Success@5 = 0. That must not be the v2 primary.

**Aggregation:** micro = unweighted mean over queries (primary). Script/intent slices = descriptive unless cell size meets §15. Do not average KN Hit@5 with NL Success@5. Do not cite 87.18% as a v2 result. Do not treat 80% as a pass/fail threshold.

---

## 14. Statistical plan

Pre-registered **before** TEST scores exist.

**Primary comparison:** a named v2 system vs frozen M0, paired at the **query** unit.

- KN family: ExactSource Hit@5
- NL family: Success@5  

Two families, not one averaged p-value.

| Element | Choice |
| --- | --- |
| Confidence | 95% Wilson or Clopper–Pearson on single proportions; bootstrap percentile CI on paired delta (10,000 resamples) |
| Binary paired test | McNemar on hit/success tables |
| Effect size | Absolute percentage-point difference and discordant pair counts |
| Rank metrics | Wilcoxon signed-rank only if pre-registered for that secondary metric; do not switch tests after seeing p |
| Multiple comparisons | Holm–Bonferroni within each secondary family |
| Small cells | Script slices with n_Mixed below planning minimum are **descriptive** |
| Non-emphasis | Do not headline “significance” when the delta CI includes 0, when n is below the minimum viable set, or when Top-5 moves but Recall@50 does not (likely RANK jitter) |

Do **not** choose a test because it is significant. Do **not** enlarge TEST after seeing a disappointing delta.

---

## 15. Sample size (planning, not a result)

n=40 cannot resolve a ~10 pp paired gain (PLOS U already showed wide intervals).

| Target | Rough n (queries, both tracks combined unless noted) | Role |
| --- | --- | --- |
| Precision | Wilson half-width ~0.07 at p≈0.60 needs n≈200 per **primary track** | Why 40 is not enough |
| Paired 10 pp | Order of 200 binary paired observations is a planning minimum for a 10 pp Success@5/Hit@5 shift | DEV+TEST together still split |
| Mixed stratum | Prefer ≥30 Mixed in the **ideal** set; ≥12 in **minimum viable** (descriptive if smaller) | Rare genuine Mixed |
| Annotation | NL pooling × judges × depth dominates cost; KN ExactSource is cheap | Workload |

**Minimum viable (planning):** about **200+** queries total (example: ~80–100 KN + ~100–120 NL), with Roman oversampled, Mixed not forced to 1/3, TRAIN/DEV/TEST respected even if TEST is a second wave.

**Ideal (planning):** about **400–500** queries, enough for script slices and a sealed TEST near 40%.

These are **planning targets**, not a requirement that the paper contain 500 rows. Do not inflate n after poor TEST performance to “get significance.”

Annotation workload example (order of magnitude, not a quote): NL Top-5 only × 120 queries × 2 judges ≈ 1,200 labels; pooled Top-50 is far larger and must be capped or sampled with a pre-registered rule.

---

## 16. Leakage

### Forbidden as v2 TEST (and not for DEV selection presented as unseen)

- QTRN (`QTRN_001`–`QTRN_260`)
- H001–H040
- K001–K040
- U001–U040
- Phase 11 token inventories
- Inspected miss lists
- Rewritten historical queries
- Queries designed from historical failures

### Indirect leakage

A new ID is not enough if the need is essentially a copied U/K recipe (same entity + same slot + same constraint). Example: rewriting U004’s dollar-rate need with a new ID is still leakage.

### Corpus overlap (not automatically leakage)

The same 111,860-article collection **is** the retrieval corpus. Repeated famous entities can appear in TRAIN and TEST. Leakage is **query wording, inspected needs, failure mining, and test-based tuning**, not the mere existence of “Babar” in the news.

---

## 17. Failure taxonomy

One **primary** label per failed query. Optional secondary tag allowed. Do not grow past this list without a protocol amendment.

| Code | Name |
| --- | --- |
| QAMB | Query ambiguity / underspecification |
| ROOM | Wrong retrieval room / script routing |
| NORM | Normalization or spelling mismatch |
| VOCAB | Vocabulary / semantic gap |
| ENT | Entity collision or wrong entity |
| NEIGH | Topical neighbour / wrong slot |
| MISS | Relevant document absent from Top-50 |
| RANK | In Top-50 but not Top-5 |
| TEMP | Temporal / “today” mismatch |

Draft the taxonomy on TRAIN. Freeze labels before TEST scoring. Do not invent classes to explain TEST after the fact.

---

## 18. Experiment registry

Every future run is logged in `REGISTRY.md` (template). Negative results stay. No silent retries. Candidate-stage and final-stage metrics are both required.

---

## 19. M0 and PLOS protection

- Do not edit `experiments/phase5_roman_urdu/run_phase5.py` in place.
- Do not modify Phase 12 query files, qrels, or official result markdown.
- Do not modify `results/` or `Papers/PLOS_ONE/` as part of v2 development.
- Future M0 scoring on the **new** benchmark imports frozen code as a baseline.

---

## 20. Phase 1 stop

This protocol and infrastructure originally did **not** authorize query collection. Collection started only after explicit human review (2026-09-09). Benchmark `ultra-v2-benchmark-v0` is now collected, validated, and TEST-sealed. See `REGISTRY.md`.

Do not begin Phase 2 from this document. Do not inspect sealed TEST query text during later development.
