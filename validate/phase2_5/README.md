# Phase 2.5 — Empirical Retrieval Validation for the 5–6 Word Gap

## Purpose

The training-data audit found **zero training examples in the 5–6 word
range**, sitting between the established SHORT region (2–4 words) and
the established LONG region (7–19 words). Before creating any V3
training data for this range, we need empirical evidence for whether
5–6 word bare-event queries behave like SHORT (headline retrieval is
sufficient) or LONG (full article content retrieval is meaningfully
better) queries — or whether the answer is query-dependent.

Phase 2.5 does **not** train, retrain, or modify anything. It only runs
retrieval and reports what happened.

## Location note

The original task brief referred to `validation/phase2_5/`. The actual
directory in this repository is `validate/phase2_5/` (matching the
existing `validate/` folder that already holds `phase3_retrieval_verification.py`
and `phase4_retrieval_verification.py`). This audit session kept the
existing location rather than creating a second, parallel folder.

## Files

| File | Status |
|---|---|
| `pilot_queries.json` | **Pre-existing, unmodified.** 33 queries: 5w=4, 6w=6, 7w=9, 8w=6, 9w=4 (29 §4 bare-event queries) + 4 anchor queries. 18 Urdu / 15 Roman Urdu. Categories limited to the 4 actually present in the corpus. Per the task brief's hard rule, this file was used exactly as-is and not edited. |
| `01_run_retrieval_and_export_judgment_template.py` | **Rewritten this session.** The version already in the repo before this session only printed a description of what it would do and never actually implemented the retrieval calls — see "What was wrong with the existing infrastructure" below. This version is a real, runnable implementation, smoke-tested against a synthetic corpus (see below). Still not run against the real corpus (absent in this sandbox). |
| `02_compute_metrics_from_judgments.py` | **Rewritten this session.** Same issue as above — the previous version had correct metric math (P@k/MRR/nDCG formulas) but never actually loaded, grouped, or aggregated judgment data, and never implemented the SHORT/LONG/QUERY-DEPENDENT decision logic. Rewritten and smoke-tested end-to-end (with synthetic random judgments, clearly marked as smoke-test-only, never treated as real evidence). |
| `README.md` | This file. |

## What was wrong with the existing Phase 2.5 infrastructure

Before this session, both scripts in this directory were **skeletons**:
they checked whether the corpus was present, printed a paragraph
describing what they *would* do, and stopped. They did not import
`chromadb`/`sentence-transformers`, did not call any retrieval function,
did not build a judgment template, and did not compute any metric. This
was disclosed honestly in the file headers (they said "not wired up
further"), so nothing was fabricated — but the infrastructure Phase 2.5
depends on did not actually exist yet. It's been implemented for real in
this session.

## A real methodological problem found while inspecting the existing retrieval code

`notebooks/04_retrieval.ipynb` defines `ultra_retrieve()` with a
docstring claiming it uses "CLS pooling on headlines" for short queries
and "mean pooling on full content" for long queries. **The function body
never actually does this** — it always encodes the query the same way
and always queries the single existing ChromaDB collection, whose
documents are `combined_text` (Headline + article body), per
`notebooks/02_embeddings.ipynb` and `notebooks/03_chromadb.ipynb`. No
headline-only semantic index has ever existed in this codebase. The only
genuinely headline-scoped retrieval that pre-existed (in
`validate/phase3_retrieval_verification.py` and
`validate/phase4_retrieval_verification.py`) is **TF-IDF keyword search**
over the Headline column — a different retrieval *method* (lexical), not
just a different content *scope*, from the full-content semantic search.
Comparing those two head-to-head would confound method with scope: a
result showing "full-content wins" could just mean "semantic beats
TF-IDF," which says nothing about whether 5–6 word queries specifically
need article body content.

**Fix implemented in `01_run_retrieval_and_export_judgment_template.py`:**
the script now builds a genuine headline-only *semantic* index (encoding
the Headline column with the same `paraphrase-multilingual-MiniLM-L12-v2`
model already used for the full-content embeddings, cached to
`data/headline_embeddings_phase2_5_cache.npy` on first run) so that
HEADLINE vs. FULL_CONTENT is an apples-to-apples comparison: same
method, different content scope. The pre-existing TF-IDF headline search
is still exported (as `HEADLINE_KEYWORD_TFIDF`) for completeness, but is
explicitly excluded from the default SHORT/LONG decision logic in script
02, with the reasoning documented in both scripts' headers.

Also note: `docs/labeling_guidelines.md`, referenced by the original
version of this README as the source of the "§4" rule and the "Rule
1–4" anchor categories, **does not exist anywhere in this repository**
(checked via `git log --all` and a full-repo search). The §4 label and
Rule 1–4 names are used consistently in `pilot_queries.json` and
`validate/phase4_retrieval_verification.py`'s comments, so the rules
themselves clearly exist somewhere (this thesis's actual documentation,
kept outside git, or a prior chat), but the file is not in this repo. If
you have it, add it — the pilot's `rule_type` fields currently rely on
you knowing what "§4" and "Rule1–4" mean.

## Methodology

1. Each pilot query carries a `pre_registered_hypothesis` — a prediction
   only, never a gold label. Script 1 does not use it for anything
   except passthrough into the export; script 2 only ever compares
   retrieval evidence *against* it, never edits it.
2. Retrieval modes run per query, top-15 each:
   - `HEADLINE` — semantic search against headline-only embeddings (new,
     built by this session's script; see above)
   - `FULL_CONTENT` — semantic search against the existing ChromaDB
     collection (`combined_text` embeddings)
   - `HYBRID` — 0.5/0.5 normalized fusion of the two semantic scores
     above
   - `HEADLINE_KEYWORD_TFIDF` — the pre-existing TF-IDF headline search,
     exported as a diagnostic only (not part of the primary decision)
3. Output is an **unjudged** template — every row's `relevance` column
   says `UNJUDGED`. A human (you) fills in `Relevant` / `Partially
   relevant` / `Not relevant` per row. Category match is never treated
   as relevance.
4. Queries whose `category` does not exist anywhere in the corpus are
   flagged `invalid_no_corpus_match` and excluded from metrics — not
   counted as retrieval failures.
5. Rankings where all top-15 scores are identical or zero are flagged
   `tied_or_zero_similarity_flag` for scrutiny.
6. After judgments exist, script 2 computes P@5, P@10, P@15, MRR,
   nDCG@15 per query per mode, aggregates by retrieval mode / word count
   / script (Urdu vs. Roman) / query type (bare-event vs. anchor), and
   applies a fixed, disclosed decision rule (see script 02's docstring)
   to classify the 5w and 6w bare-event buckets as `SHORT`, `LONG`, or
   `QUERY-DEPENDENT / INCONCLUSIVE` — separately per script, and combined.
   `INSUFFICIENT_DATA` is reported honestly if too few queries in a
   bucket have complete judgments.

## Reproducibility

`01_run_retrieval_and_export_judgment_template.py` writes
`run_metadata.json` alongside `judgment_template.csv`, recording: corpus
CSV SHA-256 and row count, embeddings shape, ChromaDB collection name
and document count, embedding model name, device, pilot-queries file
SHA-256, timestamps, and Python/platform info — enough for another
researcher (or you, six months from now) to confirm exactly what was run
against what.

## Current status

- Corpus (`data/clean_articles.csv`, `data/embeddings.npy`,
  `data/chromadb/`) is **not present** in this sandboxed audit
  environment (expected — it's gitignored). Nothing in this session
  fabricated, simulated, or guessed at retrieval results.
- Both scripts are now real, runnable implementations, verified with a
  logic smoke test against a synthetic 200-row corpus and mocked
  `chromadb`/`sentence-transformers` (to check control flow, DataFrame
  handling, and CSV/JSON export shapes without needing the real 500MB
  model or the real corpus). The smoke test is **not** evidence about
  the actual research question — it used random synthetic text and
  random synthetic relevance judgments purely to confirm the code runs
  without crashing and produces the right output shape.
- **No real retrieval has been run. No real judgment data exists. No
  real metrics have been computed. No SHORT/LONG/QUERY-DEPENDENT
  conclusion has been reached.**

## How to run this for real

On the machine with the real corpus, from the repo root:

```bash
pip install pandas numpy chromadb sentence-transformers scikit-learn torch

python validate/phase2_5/01_run_retrieval_and_export_judgment_template.py
# -> produces validate/phase2_5/judgment_template.csv (all relevance = UNJUDGED)
# -> produces validate/phase2_5/run_metadata.json

# Open judgment_template.csv, fill in the `relevance` column for every
# row with: Relevant / Partially relevant / Not relevant
# (do NOT use category match as a shortcut for relevance)

PHASE2_5_JUDGMENTS_PATH=validate/phase2_5/judgment_template.csv \
    python validate/phase2_5/02_compute_metrics_from_judgments.py
# -> prints the full breakdown and decision
# -> writes validate/phase2_5/phase2_5_metrics_report.json
```

Bring back to the next session:
- `validate/phase2_5/judgment_template.csv` (with judgments filled in)
- `validate/phase2_5/run_metadata.json`
- `validate/phase2_5/phase2_5_metrics_report.json`

The first run will take longer than later ones — encoding all corpus
headlines for the new headline-only semantic index is a one-time cost,
cached to `data/headline_embeddings_phase2_5_cache.npy` (gitignored,
like the other large `data/*.npy` files).
