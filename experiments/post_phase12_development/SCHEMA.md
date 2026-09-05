# R-dev schema (Post-Phase-12 development set)

**Status:** Schema only. No query rows committed yet.

## File: `queries_r_dev.csv`

| Column | Required | Description |
| --- | --- | --- |
| `query_id` | yes | `R001` … `R100` (or approved n) |
| `track` | yes | `KI` (known-item) or `NAT` (naturalistic) |
| `query_text` | yes | Raw user query string |
| `script` | yes | `URDU` / `ROMAN` / `MIXED` / `OTHER` — from M0 `detect_script` after writing |
| `need_type` | yes | `factoid` / `explanatory` / `named_entity` / `navigational` |
| `length_bin` | yes | `short` / `medium` / `long` |
| `category` | yes | `sports` / `business` / `entertainment` / `science/tech` / `general` |
| `temporal` | yes | `0` or `1` |
| `source_doc_id` | KI only | Corpus `Index`; **empty** for NAT |
| `article_category` | KI only | Corpus category of source row |
| `creation_method` | yes | e.g. `title_paraphrase`, `lead_informed`, `roman_chat_style`, `human_naturalistic` |
| `phenomena_tags` | optional | Pipe-separated: `spelling_variation`, `entity`, `mixed_script`, `lexical_mismatch`, `temporal`, `short`, `long`, `english_loanword` |
| `notes` | optional | Audit trail; no retrieval ranks |

## File: `MANIFEST.json`

| Field | Description |
| --- | --- |
| `experiment_id` | `post_phase12_r_dev` |
| `protocol_version` | Git hash or doc version |
| `random_seed` | For Track 1 article sampling |
| `eligible_population_rule` | Text definition of eligible corpus rows |
| `excluded_source_ids` | Counts from QTRN, K, etc. |
| `author` | Who wrote queries |
| `retrieval_before_seal` | must be `false` |
| `overlap_check_passed` | set after checker runs |

## File: `SEAL.json` (before retrieval)

| Field | Description |
| --- | --- |
| `queries_r_dev_sha256` | Checksum of query file |
| `query_count` | Total n |
| `track_counts` | KI / NAT |
| `detector_counts` | URDU / ROMAN / MIXED / OTHER |

## File: `qrels_r_dev.csv` (Track 2 only, after retrieval)

| Column | Description |
| --- | --- |
| `query_id` | R id |
| `doc_id` | Retrieved corpus id |
| `rank` | 1–5 |
| `relevance_label` | A / B / C / D / E |
| `annotator` | id |
| `annotation_date` | ISO date |

Track 1 does not use qrels; it uses `source_doc_id` only.

## Script labeling rule

Reuse frozen M0 detector logic (Unicode counts):

- Urdu letters present and Latin absent → `URDU`
- Latin present and Urdu absent → `ROMAN`
- Both present → `MIXED`
- Neither → `OTHER`

Record detector function path in manifest for reproducibility.
