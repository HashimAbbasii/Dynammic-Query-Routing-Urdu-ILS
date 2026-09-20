# TEST

Planning share: ~40% of the new collection (`PROTOCOL.md` §7–8).

**Sealed. Hashed. No peek during Phases 2–6.**

When files exist, seal with:

```text
python experiments/ultra_v2/scripts/seal_test.py --input experiments/ultra_v2/benchmark/test --output experiments/ultra_v2/benchmark/test/seal.json --version ultra-v2-benchmark-v0
```

Verify:

```text
python experiments/ultra_v2/scripts/verify_test_seal.py --seal experiments/ultra_v2/benchmark/test/seal.json
```

If a query is inspected after sealing, set `status=contaminated` and exclude it from confirmatory claims.

A hash does not physically prevent opening files. The no-peek rule is operational (`PROTOCOL.md` §8). Extra data files after sealing fail verification. `README.md` may change without breaking the content hash.

Files: `queries_kn.csv` (36), `queries_nl.csv` (44), `seal.json`. Query-row `status=sealed`. Do not inspect query text during Phases 2–6.

Seal version: `ultra-v2-benchmark-v0`  
`aggregate_sha256`: `48610601209c3723a7252bb9a197d8fbbece18640e0bf7aef972884816ab46c4`  
Verification: `python experiments/ultra_v2/scripts/verify_test_seal.py --seal experiments/ultra_v2/benchmark/test/seal.json` → `MATCH`.
