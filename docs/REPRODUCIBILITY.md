# Reproducibility (frozen M0)

Official retrieval is **M0**. Implementation paths were not relocated.

Independent reproduction steps, environment pins, and data-access limits: **`REPRODUCE.md`** at the repository root.

The article-text corpus is **not** in git. SHA-256 of the frozen local file:

| Artifact | Path | SHA-256 |
| --- | --- | --- |
| Corpus | `data/clean_articles.csv` (gitignored) | `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231` |
| Dictionary | `models/roman_urdu_dict_expanded.json` | `30c3f61a64ec641abbb3acdbc7a8bcaf197f0238f1bf9e76c2c7ce8e590f86a3` |

## Code

- `experiments/phase5_roman_urdu/run_phase5.py` — `detect_script`, Urdu BM25, Method D
- `experiments/phase2_oracle/run_phase2_pipeline.py` — Method D character table
- `experiments/phase12_new_unseen_evaluation/run_phase12.py` — sealed K/U retrieval runner

See `src/README.md` for the same map.

## Freeze and evaluation evidence

- `experiments/phase8_final_freeze/FINAL_SYSTEM_MANIFEST.json`
- `experiments/phase9_heldout_evaluation/`
- `experiments/phase11_improvement/`
- `experiments/phase12_new_unseen_evaluation/` (`queries_k.csv`, `queries_u.csv`, `SEAL.json`, Top-50 dumps)
- `experiments/phase12_human_relevance/` (`U_QRELS.csv`, `U_PER_QUERY.csv`)

## Official metrics (do not recompute here)

See `results/FINAL_RESULTS.md`. Interpretation: `docs/FINAL_EXPERIMENTAL_RESULTS_ANALYSIS.md`.
