# ULTRA v2 data dictionary

Field definitions for benchmark files. Query text lives only in `benchmark/{train,dev,test}/queries_*.csv`.

Canonical CSV templates: `evaluation/schemas/*.header.csv`  
JSON Schema: `evaluation/schemas/*.schema.json`

Tokenizer for `headline_overlap`: the frozen M0 pattern `[\u0600-\u06FF]+|[A-Za-z0-9]+`, lowercased (`experiments/phase5_roman_urdu/run_phase5.py` — import only, do not edit). `length_bin` uses whitespace-token count of `query_text` (protocol § length bins), not the M0 tokenizer.

---

## 1. KN query (`queries_kn.csv`)

| Field | Required | Type | Allowed values | Why |
| --- | --- | --- | --- | --- |
| `query_id` | yes | string | `KN` + 3+ digits, unique, e.g. `KN001` | Stable identifier. Must not be `K001`, `QTRN_*`, `H*`, `U*` |
| `track` | yes | string | `KN` | Distinguishes files if concatenated |
| `script` | yes | string | `URDU`, `ROMAN`, `MIXED`, `OTHER` | Detector label **after writing**, not a forced target |
| `intent_type` | yes | string | `factoid`, `explanatory`, `entity_person`, `location`, `event`, `topical` | Primary analysis slice |
| `length_bin` | yes | string | `short`, `medium`, `long` | ≤5 / 6–12 / ≥13 whitespace tokens of `query_text` |
| `ambiguous` | yes | int | `0`, `1` | Writer-marked need ambiguity |
| `query_text` | yes | string | non-empty | The query |
| `source_doc_id` | yes | int | corpus `Index` in `[0, 111859]` | Known-item gold; assigned at creation |
| `source_article_hash_or_identifier` | yes | string | `index:<id>` or SHA-256 of source row fields | Survives reordering debates; default `index:<source_doc_id>` |
| `headline_overlap` | yes | float | `[0, 1]` | Query-coverage vs source headline; reject if ≥ 0.50 |
| `writer_id` | yes | string | opaque id, e.g. `W1` | Authorship without putting names in public dumps if desired |
| `creation_timestamp` | yes | string | ISO-8601 UTC | Provenance |
| `split` | yes | string | `train`, `dev`, `test` | Leakage control |
| `status` | yes | string | `draft`, `accepted`, `sealed`, `contaminated` | `contaminated` = peeked TEST or protocol breach |
| `notes` | no | string | free text | Construction notes; no retrieval scores |
| `interpretation_notes` | no | string | free text | If `ambiguous=1` |

`source_doc_id` must be unique among **accepted** KN rows.

---

## 2. NL query (`queries_nl.csv`)

| Field | Required | Type | Allowed values | Why |
| --- | --- | --- | --- | --- |
| `query_id` | yes | string | `NL` + 3+ digits, unique | Must not collide with historical `U*` |
| `track` | yes | string | `NL` | |
| `script` | yes | string | `URDU`, `ROMAN`, `MIXED`, `OTHER` | Detector after writing |
| `intent_type` | yes | string | same as KN | Primary slice |
| `length_bin` | yes | string | `short`, `medium`, `long` | |
| `ambiguous` | yes | int | `0`, `1` | |
| `query_text` | yes | string | non-empty | **No gold document** |
| `writer_id` | yes | string | opaque id | |
| `creation_timestamp` | yes | string | ISO-8601 UTC | |
| `split` | yes | string | `train`, `dev`, `test` | |
| `status` | yes | string | `draft`, `accepted`, `sealed`, `contaminated` | |
| `notes` | no | string | | |
| `interpretation_notes` | no | string | | Required if `ambiguous=1` at acceptance |

**Forbidden:** non-empty `source_doc_id` on NL. If the column exists, it must be blank.

---

## 3. Retrieval dump (`retrieval.csv`)

Produced **later** by evaluation runners. Not generated in Phase 1.

| Field | Required | Type | Why |
| --- | --- | --- | --- |
| `run_id` | yes | string | Registry experiment id |
| `system_id` | yes | string | e.g. `m0_frozen`, `v2_…` |
| `query_id` | yes | string | KN or NL id |
| `rank` | yes | int | 1-based |
| `doc_id` | yes | int | corpus `Index` |
| `score` | yes | float | System score |
| `n_hits_returned` | yes | int | Length of returned list (≤50) |

Official depth: persist Top-50. Final metrics use Top-5 from this list.

---

## 4. NL / optional KN qrels (`qrels.csv`)

| Field | Required | Type | Allowed | Why |
| --- | --- | --- | --- | --- |
| `query_id` | yes | string | | |
| `doc_id` | yes | int | | |
| `annotator_id` | yes | string | not `author` alone for official NL | |
| `label` | yes | string | `A`,`B`,`C`,`D`,`E` | |
| `interpretation_id` | no | string | `I1`, `I2`, … | Ambiguous NL |
| `official` | yes | int | `0`, `1` | Official adjudicated row = 1 |
| `adjudicated` | yes | int | `0`, `1` | |

---

## 5. Seal manifest (`seal.json`)

See `evaluation/schemas/seal_manifest.schema.json`. Produced by `scripts/seal_test.py`.

---

## 6. Historical IDs (never reuse)

| Pattern | Meaning |
| --- | --- |
| `QTRN_*` | Phase 2 known-item pool |
| `H001`–`H040` | Trap / diagnostic |
| `K001`–`K040` | Phase 12 known-item |
| `U001`–`U040` | Phase 12 naturalistic |

Validator rejects these as `query_id` in v2 files.
