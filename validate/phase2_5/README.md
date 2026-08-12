# Phase 2.5 — §4 Empirical Retrieval Validation

> **PROVENANCE: NEW CONSTRUCTION.** This entire `validation/phase2_5/`
> directory is being created for the first time in this audit session. No
> equivalent files existed anywhere in the GitHub repository history
> (verified via `git log --all --diff-filter=A`, zero hits on any branch).
> The design below matches the specification already agreed in the prior
> audit conversation; nothing here has been executed yet.

## Purpose

`docs/labeling_guidelines.md` §4 (bare single-clause event statements with
no explicit reasoning marker) is currently **unresolved / empirically
unvalidated**. The guideline provisionally defaults these to LONG, but that
default is a guess, not evidence.

Phase 2.5 exists to empirically test that default against real retrieval
behavior on the actual corpus: does a §4-style query actually need
article-body content to be answered well, or does headline-level
information suffice?

## Files

| File | Status |
|---|---|
| `pilot_queries.json` | Created this session. 33 queries: 5w=4, 6w=6, 7w=9, 8w=6, 9w=4 (29 §4-focused) + 4 anchor queries (one per already-solid Rule 1-4). 18 Urdu / 15 Roman Urdu. Categories limited to the four actually present in the corpus: Business & Economics, Sports, Entertainment, Science & Technology. |
| `01_run_retrieval_and_export_judgment_template.py` | Created this session. Syntax-checked, smoke-tested. **Not executed against the real corpus** — corpus absent in this environment. |
| `02_compute_metrics_from_judgments.py` | Created this session. Syntax-checked, smoke-tested. **Not executed** — no judgment data exists yet. |
| `README.md` | This file. |

## Methodology

1. Each pilot query carries a `pre_registered_hypothesis` — a prediction
   only, not a gold label. It must not be edited after seeing results.
2. Run retrieval (headline-only, full-content, hybrid-if-available) against
   the real corpus using the **existing** implementation in
   `validate/phase4_retrieval_verification.py` — no new retrieval system is
   being built.
3. Export top-15 results per query per mode as an unjudged template.
4. A human reviewer judges relevance.
5. Compute P@5, P@10, P@15, MRR, nDCG@15, bucketed by word count / script /
   category, and cross-tabulate against the pre-registered hypotheses.
6. Report the conclusion honestly: SHORT, LONG, query-dependent, or
   INCONCLUSIVE. Do not force a universal rule. Do not pick whichever
   answer makes V3 training easier.

## Current status

- Corpus (`data/clean_articles.csv`, `data/embeddings.npy`,
  `data/chromadb/`) is **not present** in this sandboxed environment
  (expected — it's gitignored).
- **No retrieval has been run. No judgment data exists. No metrics have
  been computed.** Nothing in this directory contains fabricated or
  simulated results.
- This experiment must be run on the local machine that has the real
  corpus.
