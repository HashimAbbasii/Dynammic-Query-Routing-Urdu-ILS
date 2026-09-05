# Post-Phase-12 research development set (R-dev) — construction protocol

**Status:** REVISED AND FROZEN FOR QUERY AUTHORING (protocol/documentation only).  
**Branch:** `research/post-phase12`  
**Version:** 2.0 (post scientific review)

**Purpose:** Define a scientifically valid **new** development set for tuning and ablating candidate retrieval interventions **before** any future unseen test.

This document does **not** claim retrieval improvement. It does **not** replace frozen official results. R-dev is **not** a Module 1 benchmark.

---

## 0. Evaluation hierarchy

```text
FROZEN HISTORICAL (never tune on; never reuse queries)
├── Phase 2 QTRN dev + internal_val (n=78) → official 87.18% ExactSource Hit@5
├── H001–H040 → diagnostic human baseline (62.5% Success@5); no source_doc_id
├── K001–K040 → sealed known-item test (67.50% ExactSource Hit@5)
└── U001–U040 → sealed naturalistic test (57.50% Success@5)

NEW RESEARCH
├── R-dev (this protocol) → development / ablation / tuning
└── Future unseen test (separate protocol; hidden until final evaluation)
```

---

## 1. R-dev lifecycle (mandatory sequence)

```text
Protocol finalized
        ↓
Queries authored
        ↓
Leakage / overlap checks
        ↓
R-dev sealed (SEAL.json checksums; no retrieval yet)
        ↓
M0 retrieval dump (one pass)
        ↓
NAT annotation (on M0 Top-5 only; system-blind)
        ↓
R-dev frozen (queries + M0 dump + qrels locked)
        ↓
Candidate development / ablation (M0 vs candidates on R-dev)
        ↓
Candidate method frozen
        ↓
NEW unseen test constructed (disjoint from R-dev and all historical pools)
        ↓
One-shot final evaluation
```

**Information flow rules**

| Stage | Allowed use of outcomes |
| --- | --- |
| R-dev | Tuning, ablation, component selection, threshold choice |
| Future unseen test | Final generalization claims only |
| Frozen K / U / Phase 2 | Historical reporting only; never tuning |

- R-dev outcomes **may** be used for tuning.
- R-dev outcomes **must not** be used to alter the final unseen test (query text, quotas, or source selection).
- The unseen test remains **completely hidden** until final evaluation.
- If the retrieval system changes materially after R-dev tuning, R-dev is **burned** for that new system; a **new** development set is required before further tuning.

---

## 2. Set definition

| Property | Value |
| --- | --- |
| **Name** | Post-Phase-12 Research Development Set (**R-dev**) |
| **Query ids** | `R001` … `R100` (single namespace) |
| **Location (when created)** | `experiments/post_phase12_development/` |
| **Total size** | **100 queries** |

### 2.1 KI / NAT split

| Split | Preferred | Fallback (annotation budget strictly limited) |
| --- | --- | --- |
| **Track 1 — Known-item (KI)** | **50** | **60** |
| **Track 2 — Naturalistic (NAT)** | **50** | **40** |
| **Total** | **100** | **100** |

**Preferred:** 50 KI + 50 NAT (~250 Top-5 human labels for NAT).  
**Fallback:** 60 KI + 40 NAT (~200 labels) — acceptable only when annotation capacity is capped at ~200 judgments.

Do **not** merge Track 1 Hit@5 with Track 2 Success@5 into one headline number.

| Track | Gold | Primary metric (later) |
| --- | --- | --- |
| KI | `source_doc_id` assigned at creation | ExactSource Hit@5 |
| NAT | Human A/B/C/D/E on M0 Top-5 | Success@5 |

---

## 3. Script distribution policy

### 3.1 No exact script quotas

Do **not** impose fixed per-track script counts (e.g., “exactly 28 Urdu KI queries”). Authors write naturally; script is assigned **post-hoc** using frozen M0 `detect_script` (Unicode script counts in `experiments/phase5_roman_urdu/run_phase5.py`).

Record final counts in `SEAL.json` after authoring. Do **not** rewrite queries after authoring to satisfy script targets.

### 3.2 Prospective minimum coverage floors (combined R-dev)

These are **prospective** design targets checked **after** natural authorship, not quotas to force by editing:

| Script | Minimum floor (100-query set) |
| --- | ---: |
| URDU | ≥ 12 |
| ROMAN | ≥ 12 |
| MIXED | ≥ 3 |

If natural authorship produces counts **below** a floor, **document the shortfall** in `MANIFEST.json` and report script-stratified results with caution. Do **not** manipulate query text post hoc to hit floors.

### 3.3 Roman cap (prospective anti-overfitting safeguard)

**Roman queries must not exceed 45% of the total R-dev set** (≤ 45 of 100).

**Justification (required wording):** This cap prevents R-dev from degenerating into a Roman-normalization or Roman-only benchmark during candidate ablation. It preserves Urdu and mixed-script coverage so collateral damage and routing effects remain measurable across future modules.

**This cap must NOT be justified as:** “Roman performed badly in Phase 12, therefore we need more Roman queries.” Aggregate Phase 12 script breakdown may motivate **investigating** Roman robustness in analysis, but it must **not** drive oversampling of Roman queries during construction.

If natural authorship exceeds 45% Roman, **document and report** rather than deleting Roman queries to satisfy the cap unless supervisor-approved protocol amendment is recorded.

---

## 4. Module-neutral design

R-dev is **not** a Module 1 normalization benchmark. It must remain suitable for later testing of:

- Roman Urdu normalization (Module 1)
- Character n-gram retrieval
- Lexical hybrid retrieval
- Semantic retrieval / fallback
- Query-type-aware retrieval
- Script-aware routing
- Adaptive retrieval

**Safeguards against normalization-only design**

- Do **not** oversample informal spelling, elongated Roman, or lexical-mismatch phenomena beyond the tier proportions in §5.
- Urdu and MIXED queries are **mandatory regression monitors** in all ablation reports.
- NAT queries are document-blind and not normalization-targeted.
- Phenomena coverage spans entities, temporal factoids, explanatory questions, and mixed script — not spelling variation alone.

---

## 5. Track 1 — Known-item (KI) construction

### 5.1 Why R-dev KI differs from Phase 2 / K

| Aspect | Phase 2 / K001–K040 | R-dev KI |
| --- | --- | --- |
| Role | Official or sealed **test** pools | **Development** pool for forward tuning |
| Query style | Predominantly title-like / `title_roman` templates | **Tiered** human authoring with lexical mismatch and body factoids |
| Overlap risk | Already used in M0 history | Must use **new** source articles and new query ids |
| Difficulty | Title overlap → high BM25 ceiling | T2/T3 deliberately reduce trivial headline matching |
| Machine romanization | Phase 2 `title_roman` strings common | **Forbidden** as primary query form |

R-dev KI is known-item with automatic gold, but it is **not** a duplicate of the 87.18% evaluation design.

### 5.2 Three-tier construction (required)

| Tier | Share of KI | Method | Human requirement |
| --- | --- | --- | --- |
| **T1 — Human-edited title paraphrase** | ~30% | Start from source headline; shorten/rephrase; **no verbatim copy** | Human edit mandatory (may begin from draft) |
| **T2 — Lead/body-informed lexical mismatch** | ~40% | Author reads lead/body; writes query using **different wording** than headline while targeting same article | Full human authoring |
| **T3 — Body factoid** | ~30% | Author reads article; writes specific fact question answerable by that article | Full human authoring |

**Tier counts (preferred 50 KI):** T1 ≈ 15, T2 ≈ 20, T3 ≈ 15.  
**Tier counts (fallback 60 KI):** T1 ≈ 18, T2 ≈ 24, T3 ≈ 18.

Tag each row: `creation_method` = `t1_title_paraphrase` | `t2_lexical_mismatch` | `t3_body_factoid`.

### 5.3 Absolute bans during KI authoring

- No verbatim headline copying
- No retrieval (BM25, Method D, Chroma, MiniLM, or any ranker)
- No embeddings or semantic search to pick “good” articles or queries
- No query selection based on observed or expected retrieval behavior
- No use of `title_roman` machine strings as the final query
- No `source_doc_id` from QTRN, K, or other historical evaluation pools

### 5.4 Source document sampling

1. **Eligible population:** `Index` ∉ {QTRN sources} ∪ {K sources}; non-empty `Headline` after strip; headline length ≥ 12 characters.  
2. **Stratify** by corpus `Category` (Sports; Business & Economics; Entertainment; Science & Technology).  
3. **Equal per bucket:** preferred 50 KI → **12–13 articles per category** (record exact counts in manifest); fallback 60 KI → **15 per category**.  
4. **Fixed random seed** recorded in `MANIFEST.json` (not tuned).  
5. **Unique sources:** no duplicate `source_doc_id` within R-dev KI.  
6. Assign `source_doc_id = Index` **before** any retrieval.  
7. R-dev KI source ids **must not** be reused in the future unseen test.

---

## 6. Track 2 — Naturalistic (NAT) construction

### 6.1 Protocol: information-need-first, document-blind authorship

NAT queries represent **realistic user information needs**. They are **not** covert known-item queries.

### 6.2 Author requirements (strict)

NAT authors **must not**:

- access `data/clean_articles.csv` (or any corpus export) while writing
- access article titles or article bodies
- access Phase 12 queries (`queries_k.csv`, `queries_u.csv`)
- access Phase 12 failure analyses or per-query retrieval reports
- access any retrieval outputs
- write queries intended to retrieve a known document
- use BM25, embeddings, or search to phrase or validate queries

NAT authors **should**:

- write queries as a bilingual Pakistani news user might type
- vary need types (factoid, explanatory, named entity, short/long)
- include organic Roman Urdu, Urdu script, and mixed script where natural — without forcing script quotas

`source_doc_id` is **always empty** for NAT.

### 6.3 Author identity

| Priority | Author | Condition |
| --- | --- | --- |
| **Preferred** | Independent author **not** involved in Phase 12 failure analysis | Document name/role in manifest |
| **Fallback** | Thesis author | Permitted only with **written authorship firewall** (§10) and **documented supervisor oversight** |

Query construction and annotation are **separate stages** performed by processes that satisfy §6.2 and §7 respectively.

### 6.4 NAT phenomena guidance (not forced balance)

Pre-register **minimum phenomenon counts** as authoring goals, not post-hoc edits:

- ≥ 4 temporal factoids (markers such as `آج`, `aaj`, `موجودہ`, `mojooda`, `kal`, `کل`, `latest`, `current`, `recent`, `upcoming` — extend list in manifest)
- Mix of short, medium, and long queries
- Named-entity and explanatory queries included
- Category diversity by author intent (not equal corpus-category quotas)

Do **not** copy or paraphrase sealed U001–U040 strings.

---

## 7. Human annotation protocol (NAT only)

Reuse Phase 12 **A/B/C/D/E** scheme for comparability (`experiments/phase12_human_relevance/ANNOTATION_PROTOCOL.md`, Phase 7 rubric).

### 7.1 Label definitions

| Code | Meaning |
| --- | --- |
| A | Directly satisfies the need |
| B | Same occasion/event but incomplete |
| C | Topically related, not the asked need |
| D | Not relevant |
| E | Ambiguous (headline + snippet insufficient) |

### 7.2 Annotators

| Level | Requirement |
| --- | --- |
| **Minimum** | 1 trained annotator |
| **Recommended** | 2 annotators on all NAT queries, **or** 2 annotators on a **predefined stratified subsample** for agreement measurement |

### 7.3 Independence and blinding

- Annotations are **independent** before adjudication (no discussion until both complete, or subsample complete).
- Annotators see **`query_text` + retrieved headline + snippet only**.
- Annotators **must not** know which retrieval system produced the results (**system-blind**).
- **First annotation pass:** M0 Top-5 dump only, **after** R-dev seal and **before** candidate tuning.
- **Candidate-specific annotation** after seeing candidate results requires a **separate pre-registered protocol** — not default R-dev practice.

### 7.4 Disagreement resolution

- Pre-register: supervisor adjudicates A/B and B/C borderline cases.
- Report **Cohen’s κ** (or equivalent) on double-annotated queries or subsample.
- Single-annotator R-dev is acceptable for MS development if limitation is documented.

### 7.5 qrels and Success@5

**File:** `qrels_r_dev.csv` (created after M0 retrieval, not during query authoring)

| Column | Description |
| --- | --- |
| `query_id` | R id (NAT rows only) |
| `doc_id` | Corpus `Index` |
| `rank` | 1–5 |
| `relevance_label` | A / B / C / D / E |
| `annotator` | Annotator id |
| `annotation_date` | ISO date |

**Success@5** = (# NAT queries with ≥1 **A or B** in retrieved Top-5) / (NAT n).

Secondary metrics (report separately): conservative P@5, optional graded nDCG@5 — same definitions as Phase 12 U protocol.

Track 1 uses `source_doc_id` only; no qrels.

---

## 8. Difficulty and metadata taxonomy (pre-retrieval only)

### 8.1 Allowed labels (assign at query creation or by rule)

| Field | Rule |
| --- | --- |
| `script` | Post-hoc M0 `detect_script` |
| `length_bin` | short ≤5 tokens; medium 6–12; long ≥13 |
| `need_type` | factoid / explanatory / named_entity / navigational (author) |
| `temporal` | 0/1 from pre-registered marker list |
| `category` | sports / business / entertainment / science/tech / general (author intent for NAT; corpus category for KI source) |
| `creation_method` | tier tag for KI; `human_naturalistic` for NAT |
| `phenomena_tags` | Multi-label from fixed enum (see `experiments/post_phase12_development/SCHEMA.md`) |

### 8.2 Rejected / deferred labels

| Label | Status |
| --- | --- |
| `retrieval_hard` | **Rejected** — requires retrieval outcomes |
| `normalization_sensitive` | **Rejected** — becomes outcome-defined after Module 1 |
| `ambiguous` (retrieval-derived) | **Rejected** at creation — annotator E at judgment time only |
| `morphology_heavy` | **Rejected** if subjective; no reproducible rule |

### 8.3 Why retrieval-derived labels are prohibited during development

Labels that depend on M0 or candidate retrieval outcomes (e.g., “hard because rank > 5”) encode the current system into the dataset definition. That converts contamination detection into **retrieval optimization** and invalidates ablation on R-dev. Difficulty for analysis may be reported **post hoc** in experiment reports, but must not be used to select queries or tune candidates.

---

## 9. Category and phenomena coverage

| Dimension | KI | NAT |
| --- | --- | --- |
| Corpus category (4 buckets) | **Equal source sampling** per §5.4 | Author diversity guideline; **no forced equal quotas** |
| Phenomena (entity, temporal, explanatory, mixed script) | Via tier design + tags | Pre-registered **minimum counts** as goals (§6.4) |
| Informal Roman / spelling variation | Minority share; NAT only if organic | Not dominant share of set |

Do not force artificial balance that misrepresents real query distributions.

---

## 10. Leakage and overlap control

Distinguish **contamination detection** (required before seal) from **retrieval optimization** (forbidden).

### 10.1 Existing checks (mandatory)

Tooling: `experiments/post_phase12_development/overlap_check.py` (and extensions documented in manifest).

- Exact normalized duplicate vs historical pools (leakage normalization in `experiments/phase2_oracle/textnorm.py`)
- Near-duplicate: Jaccard ≥ 0.75 vs sealed/historical queries
- Comparison against H, K, U, QTRN, T, SVM-training strings
- Forbidden `source_doc_id` (QTRN ∪ K historical ids)

### 10.2 Additional safeguards (mandatory or diagnostic)

| Safeguard | Type | Action |
| --- | --- | --- |
| No duplicate KI `source_doc_id` within R-dev | **Block** | Fix before seal |
| No R-dev KI source ids in future unseen test | **Block** | Enforced at unseen-test construction |
| Headline–query token overlap diagnostic (KI) | **Diagnostic** | Report in manifest; flag verbatim/near-verbatim headline copy |
| Author attestation (signed statement) | **Process** | Record in `MANIFEST.json` |
| Semantic similarity vs historical queries | **Warning only** | May flag paraphrase leakage; **no auto-reject** on similarity alone |
| No query editing after retrieval | **Block** | Burn set if violated |
| Seal R-dev (`SEAL.json`) before any retrieval | **Block** | Checksums recorded first |

### 10.3 Authorship firewall (NAT fallback author)

Thesis author writing NAT must sign attestation confirming:

- No access to corpus, sealed query files, or Phase 12 failure materials during NAT drafting
- No retrieval or search tools used to craft queries
- Supervisor oversight documented

**Forbidden files during NAT authoring (non-exhaustive):**

- `experiments/phase12_new_unseen_evaluation/queries_*.csv`
- `experiments/phase12_human_relevance/U_*.csv`, `PHASE12_HUMAN_RESULTS.md`
- `experiments/phase12_new_unseen_evaluation/K_RESULTS.md`, `U_RETRIEVAL_STATS.md`
- Per-query failure inventories in any phase report
- `data/clean_articles.csv`

---

## 11. Historical pools (read-only reference)

| Pool | n | Reuse for R-dev? |
| --- | ---: | --- |
| Phase 2 QTRN (all splits) | 260 | **No** |
| Phase 2 dev + internal_val | 78 | **No** (official 87.18%) |
| H001–H040 | 40 | **No** |
| K001–K040 | 40 | **No** |
| U001–U040 | 40 | **No** |
| SVM training strings | 409 | **No** (overlap blocked) |

**Used source documents (forbidden for new KI gold):** QTRN 260 ids ∪ K 40 ids = **300 ids** (disjoint).

---

## 12. Future unseen test (not created here)

Construct **only after** a candidate method is frozen on R-dev:

| Property | Rule |
| --- | --- |
| Namespace | Not H / K / U / QTRN / R (e.g. `S001`–`S080`) |
| Size | Recommend 40 KI + 40 NAT (separate protocol) |
| Construction | Same rules as R-dev; **disjoint** query text and source articles |
| Overlap | Must pass overlap checker vs R-dev **and** all frozen pools |
| Retrieval | One shot per frozen system version |
| Claims | Final generalization claims **only** from this set |

R-dev outcomes must **not** influence unseen-test query wording or source selection.

---

## 13. Files and next stage

### 13.1 Created when query authoring begins (not yet)

- `experiments/post_phase12_development/queries_r_dev.csv`
- `experiments/post_phase12_development/MANIFEST.json`
- `experiments/post_phase12_development/SEAL.json`

### 13.2 Created after seal and retrieval (later tasks)

- M0 Top-50 / Top-5 retrieval dumps
- `qrels_r_dev.csv`

### 13.3 Not in scope of this protocol

- Running BM25, Method D, MiniLM, or any metric
- Tuning Module 1 or any candidate
- Creating future unseen test queries

---

## 14. Approval and sign-off before query authoring

Do **not** create `queries_r_dev.csv` until:

1. **Split confirmed:** 50 KI + 50 NAT (preferred) or 60/40 fallback documented.  
2. **NAT author:** independent author assigned **or** thesis author + signed firewall + supervisor oversight.  
3. **Annotation plan:** minimum 1 annotator; recommended 2 or subsample dual-annotation.  
4. **KI tier plan:** tier counts for chosen KI n recorded in manifest template.  
5. **Supervisor sign-off** on this protocol v2.0.

---

## 15. Candidate evaluation linkage (after R-dev frozen — not now)

When R-dev exists and is frozen, future modules may compare M0 vs candidates on R-dev with:

- **Primary Module 1 analysis:** ROMAN queries (descriptive; wide CIs expected)
- **Co-primary guardrail:** Urdu and MIXED must not regress on Hit@5 / Success@5
- **Separate reporting:** KI ExactSource vs NAT Success@5

No retrieval experiment until R-dev is sealed.
