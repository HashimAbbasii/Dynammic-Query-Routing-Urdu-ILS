# ULTRA v2 Phase 1 scripts

Run from the **repository root**.

| Script | Role |
| --- | --- |
| `validate_benchmark.py` | Schema and leakage-firewall checks on CSVs. Does **not** write queries. |
| `build_collected_benchmark.py` | Writes TRAIN/DEV/TEST CSVs from the authored query lists. No retrieval. |
| `seal_test.py` | SHA-256 seal of an explicit TEST directory. Does **not** create a test set. |
| `verify_test_seal.py` | Recompute hashes vs a seal manifest. Non-zero on mismatch. |

```text
python experiments/ultra_v2/scripts/validate_benchmark.py
python experiments/ultra_v2/scripts/seal_test.py --input experiments/ultra_v2/benchmark/test --output experiments/ultra_v2/benchmark/test/seal.json --version ultra-v2-benchmark-v0
python experiments/ultra_v2/scripts/verify_test_seal.py --seal experiments/ultra_v2/benchmark/test/seal.json
```

Current collection yields `PASS`. TEST is sealed; `verify_test_seal.py` yields `MATCH`.

`validate_benchmark.py` always applies the QTRN/K/U/H string copy firewall when query rows exist (opt out only with `--skip-historical-duplicates`). KN `source_doc_id` values that already belong to QTRN or Phase 12 K are rejected. If `data/clean_articles.csv` is present, KN `headline_overlap` is recomputed with the M0 tokenizer.

`verify_test_seal.py` fails if a data file is added, deleted, or changed. `README.md` is not hashed. Metadata in `seal.json` does not change `aggregate_sha256`.

Stdlib only. No retrieval. No BM25. No corpus upload.
