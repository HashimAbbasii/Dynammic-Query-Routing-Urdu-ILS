# ULTRA v2 benchmark slots

**Collection status:** `ultra-v2-benchmark-v0` query files exist. TEST is sealed. No retrieval.

| Split | Path | Use |
| --- | --- | --- |
| TRAIN | `train/` | Development and debugging |
| DEV | `dev/` | All model/parameter/fusion/reranker/threshold selection |
| TEST | `test/` | Sealed confirmatory evaluation only |

Filenames:

- `queries_kn.csv`
- `queries_nl.csv`
- `test/seal.json` (TEST only)

Schemas: `../evaluation/schemas/`  
Rules: `../PROTOCOL.md`  
Validate: `python experiments/ultra_v2/scripts/validate_benchmark.py`

Do not copy QTRN, K, U, or H into these folders.
