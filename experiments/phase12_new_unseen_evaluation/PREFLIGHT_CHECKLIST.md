# Phase 12 preflight checklist

All items must be **true** before any BM25 search.  
Implemented in `run_phase12.py`. If any check fails: **STOP**, do not search, write `artifacts/preflight.json` with `preflight_pass: false`.

## Sealed queries

- [ ] `queries_k.csv` exists
- [ ] `queries_u.csv` exists
- [ ] K SHA-256 = `124e452693f98baedf510618240c154df68d56b6b7a37ed085a6512c13d13ff6`
- [ ] U SHA-256 = `684fd1e19eddb717f5897d869ef0ca0ed586316c5a7e1d2d23006e0748fc53b9`
- [ ] IDs K001–K040 present exactly once, in order
- [ ] IDs U001–U040 present exactly once, in order
- [ ] Every K row has a valid `source_doc_id` in `[0, 111859]`
- [ ] U file has **no** `source_doc_id` column
- [ ] No H001–H040 ids in either file

## Corpus and freeze

- [ ] `data/clean_articles.csv` exists
- [ ] SHA-256 = `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231`
- [ ] `n_docs` = 111860
- [ ] `models/roman_urdu_dict_expanded.json` has 198 keys
- [ ] Dictionary SHA-256 = `30c3f61a64ec641abbb3acdbc7a8bcaf197f0238f1bf9e76c2c7ce8e590f86a3`
- [ ] Phase 8 manifest `bm25_k1` = 1.5 and `bm25_b` = 0.75
- [ ] `run_phase5.BM25_K1` = 1.5 and `BM25_B` = 0.75
- [ ] `top_k` = 50

## Frozen code paths (M0)

- [ ] `experiments/phase5_roman_urdu/run_phase5.py` importable
- [ ] `detect_script`, `tokenize`, `romanize_token`, `load_roman_dict`, `load_reverse_roman`, `BM25.search` present
- [ ] Routing: URDU/MIXED → Urdu BM25; ROMAN → Method D roman BM25
- [ ] No M1–M4 transforms loaded or applied

## Isolation / forbidden inputs

- [ ] Output directory is `experiments/phase12_new_unseen_evaluation/`
- [ ] Phase 9 folder will not be written
- [ ] Phase 10B / 10C / 11 files will not be overwritten
- [ ] H001–H040 not loaded
- [ ] Phase 10C qrels not loaded
- [ ] `heldout_retrieval_template.csv` not loaded
- [ ] `transformations.json` (Phase 11) not applied

## After a pass

Retrieval may run **once**. Queries must not be edited if scores look low.
