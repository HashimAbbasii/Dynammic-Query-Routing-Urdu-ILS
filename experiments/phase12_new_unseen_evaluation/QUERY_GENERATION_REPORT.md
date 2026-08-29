# Phase 12 query generation report

**Status:** SEALED BEFORE RETRIEVAL  
**Official system:** M0 (unchanged)  
**Experiment:** `phase12_new_unseen_evaluation`

This step created the new unseen query files and sealed them. It did **not** run retrieval, BM25, MiniLM, or any ranker. It did **not** create labels. It did **not** modify M0, the dictionary, routing, or Method D.

## Files sealed

| File | SHA-256 |
|---|---|
| `queries_k.csv` | `124e452693f98baedf510618240c154df68d56b6b7a37ed085a6512c13d13ff6` |
| `queries_u.csv` | `684fd1e19eddb717f5897d869ef0ca0ed586316c5a7e1d2d23006e0748fc53b9` |

Recorded in `SEAL.json` with `status = SEALED_BEFORE_RETRIEVAL`.

## Counts

- 40 K queries created (`K001`–`K040`)
- 40 U queries created (`U001`–`U040`)
- Total = 80
- Unique K `source_doc_id` values = **40 / 40**
- No shared `source_doc_id` among K queries
- U file has **no** `source_doc_id` column

## Random seed and eligible population

- **Random seed:** `120260827`
- **Eligible population:** rows in `data/clean_articles.csv` with non-empty Headline (strip, length ≥ 12) whose Index is **not** a Phase 2 `QTRN_*` `source_doc_id` from `experiments/phase2_oracle/oracle_all.csv`
- QTRN source ids excluded: **260**
- Eligible n: **111574**
- Sampling: `random.Random(120260827)`, stratified by Category bucket with quota 8 (sports / business / entertainment / science/tech / general)
- Corpus Category has only Sports, Business & Economics, Entertainment, Science & Technology (no General). General quota = 0; remaining 8 slots filled from leftover eligible pool with the same RNG
- K vs QTRN `source_doc_id` overlap after write: **none**
- All 40 K ids exist in the corpus Index column

K queries were written from the sampled article headline (lead only if the headline was truncated/ambiguous). Source ids were assigned **at creation**. No BM25 check was used to accept or reject a K query.

U queries were written from pre-registered naturalistic quotas. No corpus search was used to find answers. No hidden gold documents were assigned.

## K category distribution (`article_category`)

| Category | n |
|---|---|
| business | 11 |
| entertainment | 11 |
| sports | 10 |
| science/tech | 8 |
| general | 0 (none in corpus Category) |

## K script distribution (Unicode detector, counts only)

| Detector | n |
|---|---|
| URDU | 28 |
| ROMAN | 12 |
| MIXED | 0 |

Target was ~22 Urdu / ~12 Roman / MIXED only if mixed script occurred naturally. MIXED was **not** forced. The 12 Roman queries are ordinary Roman Urdu of the selected headline, not character-table traps and not Method D attack strings.

## U category distribution

| Category | n |
|---|---|
| sports | 8 |
| business | 8 |
| entertainment | 8 |
| science/tech | 8 |
| general | 8 |

## U script distribution

Intended quotas and detector counts match:

| Script | n |
|---|---|
| URDU | 18 |
| ROMAN | 18 |
| MIXED | 4 |

## U need_type distribution

| need_type | n |
|---|---|
| factoid | 14 |
| explanatory | 14 |
| named_entity | 12 |

## U length distribution

Whitespace token bins from the sealed protocol (short ≤5, medium 6–12, long 13+):

| length_bin | n |
|---|---|
| short | 12 |
| medium | 16 |
| long | 12 |

## Temporal U factoids

Exactly **4**:

- U001 `آج`
- U002 `aaj`
- U003 `موجودہ`
- U004 `mojooda`

These are ordinary information needs. They were not written to attack Method D.

## Duplicate check

- No exact duplicate strings inside K
- No exact duplicate strings inside U
- No exact duplicate strings across K and U
- Near-paraphrase pairs inside U were avoided (e.g. university-research vs internet-speed kept as different needs)
- H001–H040 were **not** used as a duplicate comparison source

## Contamination / freeze compliance

| Rule | Result |
|---|---|
| H001–H040 used for wording or selection | **false** (not opened for design) |
| Phase 10C qrels used | **false** |
| `heldout_retrieval_template.csv` used | **false** |
| Phase 11 H-failure mining used | **false** |
| Retrieval / BM25 / MiniLM / index search | **not performed** |
| Labels created | **none** |
| M0 / dictionary / routing / Method D modified | **false** |
| Queries modified after seeing results | **n/a** (no results) |
| `run_phase12.py` written | **no** |
| Phase 9 / 10B / 10C / 11 files modified | **no** |

## What this seal does **not** claim

This report contains **no** Hit@5, Success@5, P@5, nDCG, or MRR. Those metrics are invalid until a later approved frozen-M0 retrieval (and, for U, human labels).

The development/validation known-item result remains:

ExactSource Hit@5 = 68/78 = 0.8718 on the Phase 2 n=78 set.

That number is **not** a Phase 12 result.

---

**PHASE 12 QUERY SET SEALED. RETRIEVAL NOT PERFORMED.**
