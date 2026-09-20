# R2-B0 reproducibility notes

**Experiment:** R2-B0 frozen Method D on ultra-v2-benchmark-v0 Roman KN TRAIN+DEV.  
**Not a PLOS result. TEST is not used.**

## Command

From the repository root:

```text
python experiments/ultra_v2/phase2_roman/run_r2_b0.py
```

The runner refuses any path under `experiments/ultra_v2/benchmark/test/`.

## Inputs

| Input | Role |
| --- | --- |
| `experiments/ultra_v2/benchmark/train/queries_kn.csv` | TRAIN KN; ROMAN rows only |
| `experiments/ultra_v2/benchmark/dev/queries_kn.csv` | DEV KN; ROMAN rows only |
| `experiments/ultra_v2/benchmark/train/queries_nl.csv` | Roman NL count only; not scored |
| `experiments/ultra_v2/benchmark/dev/queries_nl.csv` | Roman NL count only; not scored |
| `data/clean_articles.csv` | Corpus for Method D index |
| `models/roman_urdu_dict_expanded.json` | Reverse map on documents only |
| `experiments/phase5_roman_urdu/run_phase5.py` | Frozen import |

## Expected hashes

- Dictionary SHA-256: `30c3f61a64ec641abbb3acdbc7a8bcaf197f0238f1bf9e76c2c7ce8e590f86a3`
- Corpus SHA-256: `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231`

## Outputs (do not mix with other experiment files)

- `artifacts/r2_b0_config.json`
- `artifacts/r2_b0_summary.json`
- `artifacts/r2_b0_per_query.csv`
- `artifacts/r2_b0_failures.csv`
- `artifacts/r2_b0_mechanics_check.json`

Index cache `artifacts/_index_cache.pkl` is gitignored. It stores frozen tokenized BM25 objects; it is not a publication artifact.

## Independent result (2026-09-11)

Roman KN TRAIN+DEV n=51: Hit@5 4/51, Hit@50 6/51, MRR 0.0375.  
SUCCESS 4, RANK 2, VOCAB/MISS 45.
