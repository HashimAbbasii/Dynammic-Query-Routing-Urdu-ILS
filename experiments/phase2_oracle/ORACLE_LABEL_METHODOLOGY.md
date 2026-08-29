# Oracle label methodology

## Target

Route ∈ {HEADLINE, FULL, MIXED} = which dual-index room is better at **surfacing the source article**.

That is a different question from the protocol (“would a headline be enough for a reader?”). Phase 1 showed those two questions diverge.

## Retrieval

Reuse `validate/dual_index_routing/retrieve.py`:

- Headline: cosine vs `data/headline_embeddings_phase2_5_cache.npy`
- Full: Chroma collection `urdu_news`
- Encoder: paraphrase-multilingual-MiniLM-L12-v2
- Roman queries still go through `transliterate_roman` before search
- top_k search = 20; metrics cutoff = 5

## Scoring

Single relevant id = `source_doc_id`.

- P@5 = 1/5 if source in top 5 else 0
- nDCG@5 = 1 / log2(rank+1) if rank ≤ 5 else 0

## Tie policy (pre-registered)

`MIXED_DELTA = 0.05` on nDCG@5.

Chosen before looking at H001–H040 (those files are not inputs here).
Also MIXED if both indexes score 0 (source not in either top 5).

Margin = |nDCG_headline − nDCG_full|.

## What this is not

Not 400 new human graded judgments.
Not a license to train on H001–H040.
Not an SVM retrain.
