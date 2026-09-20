# Phase 13 Step 2 — validation report

**Date (UTC):** 2026-09-20  
**Command:** `python experiments/ultra_v2/scripts/validate_benchmark.py --root experiments/ultra_v2/phase13_population/validation_bench`

## Scope

Validation bench contains **TRAIN + DEV only** (existing v2 KN/NL plus 29 Phase 13 drafts).  
No TEST directory was created or opened.

## Result

**status: PASS**

| Check | Value |
|---|---|
| kn_rows | 83 (54 existing + 29 new) |
| nl_rows | 66 |
| unique_ids | 149 |
| blocked_historical_source_ids | 300 |
| headline_overlap_recompute | corpus_headlines 111860; all accepted < 0.50 |
| historical_query_strings | 380; no copies |
| Phase 13 rejects this round | 0 |

## New batch

| Item | Value |
|---|---|
| IDs | KN091–KN119 |
| script | ROMAN (all) |
| split | train 19 / dev 10 |
| writer_id | LLM1 (LLM-drafted; pending Hashim naturalness review) |
| status | accepted (collection status; not yet merged to live benchmark) |

## Sampling

- Seed: `20260920`
- Eligible corpus rows after blocklist: 111444
- Round-1 sample size: 40 (stratified by Category)
- Drafts written only against those fixed `source_doc_id`s
- First 29 drafts that passed §5 checks kept (target ~80 total Roman KN with prior 51)
