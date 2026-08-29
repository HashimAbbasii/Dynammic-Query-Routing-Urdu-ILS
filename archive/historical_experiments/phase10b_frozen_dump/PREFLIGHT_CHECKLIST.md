# Phase 10B preflight checklist

All items must be **true** before any BM25 search.  
Implemented in `run_phase10b.py`. If any check fails: **STOP**, do not search, write `artifacts/preflight.json` with `preflight_pass: false`.

## Corpus and freeze

- [ ] `data/clean_articles.csv` exists
- [ ] SHA-256 = `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231`
- [ ] `n_docs` = 111860
- [ ] `models/roman_urdu_dict_expanded.json` has 198 keys
- [ ] Phase 8 manifest `bm25_k1` = 1.5 and `bm25_b` = 0.75
- [ ] `run_phase5.BM25_K1` = 1.5 and `BM25_B` = 0.75
- [ ] `top_k` = 50

## Frozen code paths

- [ ] `experiments/phase5_roman_urdu/run_phase5.py` importable
- [ ] `detect_script`, `tokenize`, `romanize_token`, `load_roman_dict`, `load_reverse_roman`, `BM25` present
- [ ] `BM25.search` present
- [ ] Phase 9 runner exists (read-only reference): `experiments/phase9_heldout_evaluation/run_phase9.py`
- [ ] Phase 9 per-query CSV exists for rank-1 comparison: `HELD_OUT_PER_QUERY.csv`

## Queries

- [ ] `validate/dual_index_routing/labels/heldout_traps.py` loads
- [ ] Exactly 40 IDs `H001`–`H040` in order
- [ ] Search uses only the `query` field (no rewrite)

## Output isolation

- [ ] Output directory is `experiments/phase10b_frozen_dump/`
- [ ] Output directory is **not** `experiments/phase9_heldout_evaluation/`
- [ ] Script will not write into the Phase 9 folder
- [ ] Script will not write `artifacts/phase10/HELD_OUT_RETRIEVAL_DETAILS.csv`
- [ ] Phase 10A recovery file is left untouched

## Forbidden during this run

- [ ] No dictionary edits
- [ ] No BM25 / tokenizer / Method D / routing changes
- [ ] No `heldout_retrieval_template.csv`
- [ ] No `source_doc_id` invention
- [ ] No A/B/C/D/E labels
- [ ] No Hit@5 / P@5 / nDCG / Success@5 on H001–H040
