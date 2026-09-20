# ULTRA v2 experiment registry

Template plus Phase 1 **collection** log. **No retrieval experiments have been run.** Do not fill metric fields until a later evaluation phase.

Negative results stay. Do not delete a block because the metric moved the wrong way. Do not silently retry the same idea under a new id without pointing at the previous id.

Candidate-stage metrics and final-stage metrics are both mandatory when retrieval is run.

Official eval on TEST requires a valid seal (`scripts/verify_test_seal.py`).

---

## How to log

1. Allocate `experiment_id` (`U2E###`).
2. Fill the block **before** looking at TEST (DEV logs may exist first).
3. After the run, fill metrics, statistics, interpretation, and **decision**.
4. If stop condition hits, say so. Do not keep adding variants.

---

## Template

```text
### Experiment ID
U2E___

### Date
YYYY-MM-DD

### Research question


### Hypothesis


### Dataset version
ultra-v2-benchmark-v0 (or later)

### Split
train | dev | test | train+dev
TEST used? yes/no
Seal verified? yes/no/na

### System version


### Model


### Parameters


### Code commit


### Changes
(vs previous experiment id)

### Candidate-stage metrics
Recall@50 (KN):
Recall@50 (NL):
Notes:

### Final-stage metrics
KN ExactSource Hit@1 / @5 / @10 / @50:
KN MRR:
NL Success@5:
NL P@5:
NL nDCG_useful@5:
NL nDCG_topical@5:
NL MRR:

### Statistical analysis
Paired vs M0:
Delta (pp):
95% CI:
McNemar / bootstrap:
Holm applied?:

### Interpretation


### Decision
adopt | reject | freeze | diagnostic-only

### Stop condition
hit? yes/no
which gate?:

### Negative result
yes/no
(if yes, keep this block anyway)

### Notes
Peeked TEST? no
Contaminated query ids:
```

---

## Benchmark collection log

### Benchmark ID
ultra-v2-benchmark-v0

### Date
2026-09-09

### Research question
Can future ULTRA v2 retrieval improvements be measured on a genuinely unseen, independent KN+NL benchmark that does not reuse QTRN/H/K/U needs?

### Benchmark purpose
Independent evaluation instrument for later phases. Not optimized for or against frozen M0. No target Hit@5 or Success@5.

### Split
TRAIN 80 (40%) / DEV 40 (20%) / TEST 80 (40%). One collection wave; TEST sealed immediately after validation.

### Collection status
complete (TRAIN+DEV accepted; TEST sealed)

### Query counts
KN 90; NL 110; total 200.
TRAIN: KN 36 + NL 44 = 80.
DEV: KN 18 + NL 22 = 40.
TEST: KN 36 + NL 44 = 80.

### Script distribution
ROMAN 142 (declared oversampling; M0 detector labels all Latin-only text as ROMAN, so this stratum includes Roman Urdu and English civic queries).
URDU 56.
MIXED 2 (genuine Latin named-entity/acronym + Urdu need; not quota-filled templates).
OTHER 0.

### Intent distribution
KN: event 28, factoid 23, entity_person 17, topical 11, explanatory 9, location 2.
NL: factoid 35, explanatory 32, topical 14, event 13, location 12, entity_person 4.

### Length / ambiguity (descriptive)
length_bin: medium 159, long 41, short 0. Short cells were not forced by rewriting.
ambiguous: KN 0/90; NL 1/110 (interpretation_notes present).

### Validation status
`python experiments/ultra_v2/scripts/validate_benchmark.py` → PASS.
kn_rows 90; nl_rows 110; unique_ids 200; qrel_rows 0.

### Leakage-check status
Historical ID firewall: pass (no QTRN/H/K/U IDs).
Historical query-string firewall: pass (380 historical strings checked; no exact/whitespace copies).
Duplicate query text: pass.
KN source uniqueness: 90/90 unique; none in the 300 blocked QTRN+K source IDs.
Headline overlap: recomputed on 111,860 corpus headlines; all KN < 0.50 (observed max 0.25).
No retrieval was run during construction.

### TEST seal
sealed: yes
contaminated: no
benchmark_version: ultra-v2-benchmark-v0
aggregate_sha256: 48610601209c3723a7252bb9a197d8fbbece18640e0bf7aef972884816ab46c4
verify_test_seal.py: MATCH
files hashed: queries_kn.csv, queries_nl.csv

### Relevant commit
Uncommitted working tree on `research/ultra-v2-strengthening`. Parent HEAD `fd54ac9` (identical to frozen `publication/plos-one-final` at collection start). No commit/push performed (not authorized).

### Decisions
1. Roman oversampled on purpose; not a prevalence claim.
2. MIXED not manufactured to fill a quota.
3. No short-query rewriting to hit a length cell.
4. Same writer (`W1`) authored all items; official NL A–E labels are **not** collected in this step; a second judge is required later.
5. Collection used one wave (TRAIN+DEV+TEST) then sealed TEST; two-wave collection was optional, not mandatory.

### Negative findings
None for integrity validation. No retrieval metrics exist to report.

### Stop condition / status
Phase 1 collection gate: complete. Phase 2 Roman lexical strengthening: **STOPPED** (negative result). TEST no-peek rule remains in force.

### Notes
Peeked TEST after sealing? no.
Contaminated query ids: none.
Writer is not the official NL judge.

---

## Retrieval experiment log

All entries below are **ULTRA v2 development experiments**. They are not PLOS results. TEST was not used.

### Experiment ID
R2-B0

### Date
2026-09-09

### Research question
RQ2: What is frozen M0 / Method D ExactSource performance on v2 TRAIN/DEV KN?

### Hypothesis
None (reproduction / baseline). No claim that Roman normalization will help.

### Dataset
ultra-v2-benchmark-v0 KN TRAIN+DEV (n=54). TEST sealed, unused.

### Split
train+dev. TEST used? no. Seal verified? yes (`48610601209c3723a7252bb9a197d8fbbece18640e0bf7aef972884816ab46c4`).

### Baseline
This run **is** the baseline: frozen Method D, query as typed.

### Treatment
None.

### Parameters
k1=1.5, b=0.75, Top-50, M0 tokenizer, dict 198 keys SHA `30c3f61a64ec641abbb3acdbc7a8bcaf197f0238f1bf9e76c2c7ce8e590f86a3`.

### Code commit
Uncommitted working tree on `research/ultra-v2-strengthening`. Parent `fd54ac9`. Runner: `experiments/ultra_v2/phase2_roman/run_r2.py`. Frozen M0 imported, not edited.

### Metrics (KN ExactSource; not PLOS)
All KN n=54: Hit@1 3/54, Hit@5 7/54 (0.1296), Hit@10 7/54, Hit@50 9/54 (0.1667), MRR 0.0786.
Roman n=51: Hit@5 4/51 (0.0784), Hit@50 6/51 (0.1176).
Roman TRAIN n=33: Hit@5 3/33. Roman DEV n=18: Hit@5 1/18.
Urdu n=3: Hit@5 3/3.

### TRAIN Roman failures
n=30 Hit@5 misses: 29 MISS, 1 RANK (KN014 rank 44).
DEV Roman Hit@5 misses n=17: 16 MISS, 1 RANK (KN048 rank 42).
Full ID lists: `phase2_roman/R2_B0.md`.

### NL
Pending official pooled annotation. No qrels. Not scored.

### Interpretation
On genuine v2 information-need KN queries, Method D candidate recall is low. Historical title_roman strength does not transfer. Urdu-script items on this slice remain retrievable.

### Leakage status
TEST not inspected, not tuned, not scored. Historical K/U not used as development queries.

### Decision
Keep as development baseline. Do not treat as a publication headline.

### Stop condition
No.

### Negative result
Baseline only.

---

### Experiment ID
R2-2

### Date
2026-09-09

### Research question
Does preserving unknown Roman tokens improve Method D?

### Hypothesis
Audit: BM25 already skips missing terms; drop vs preserve is identical.

### Dataset / split
Not run as a retriever (vacuous for this scorer).

### Decision
reject (inapplicable). Recorded so it is not silently retried.

### Negative result
yes — no distinct experiment exists under Method D BM25.

---

### Experiment ID
R2-1

### Date
2026-09-09

### Research question
RQ2: Does folding query tokens onto reverse-dictionary canonical keys (plus frozen Method C’s five aliases) improve Roman KN without regressions?

### Hypothesis
Documents emit the first JSON key (`kya` vs `kiya`). Canonical fold should reduce NORM misses.

### Dataset
Same KN TRAIN+DEV as R2-B0. TEST unused.

### Baseline
R2-B0

### Treatment
Query-side only, ROMAN path: dict sibling → canonical key; Method C aliases then canonical; other tokens preserved.

### Parameters
Closed tables only. No new dictionary rows. No BM25 retune.

### Metrics vs B0 Hit@5
improved 0 / unchanged 54 / degraded 0.
Roman: 0 / 51 / 0.
Hit@5 unchanged 7/54. Roman Hit@50 6→5 (KN014 rank 44 → miss50).
12/51 Roman queries actually changed tokens.

### Interpretation
The hypothesized NORM mechanism was not the TRAIN failure mode (0 NORM). Folding `kya→kiya` did not raise Hit@5 and removed the only RANK item from Top-50.

### Leakage status
Rules from frozen JSON order + Method C table, not from TEST or K/U misses.

### Decision
reject

### Stop condition
Hit? yes — no meaningful improvement; one candidate-set regression. Do not add ad-hoc keys.

### Negative result
yes

---

### Experiment ID
R2-3

### Date
2026-09-09

### Research question
Does bounded sibling-key expansion improve Roman KN after R2-1?

### Hypothesis
Union of 2–3 keys per Urdu value may recover non-canonical spellings.

### Dataset
Same KN TRAIN+DEV. TEST unused.

### Baseline
R2-B0

### Treatment
ROMAN path: expand to all frozen sibling keys; unbounded generators forbidden.

### Metrics vs B0 Hit@5
improved 0 / unchanged 54 / degraded 0.
Same Hit@50 regression as R2-1 (KN014).

### Interpretation
Query explosion of function-word families (`ne/ny`, `se/sy`, `kya/kiya`) did not create Hit@5 gains.

### Decision
reject

### Stop condition
yes — further lexical variants would be score-chasing.

### Negative result
yes

---

_No further Phase 2 Roman lexical experiments. Phase 3 was not started._

