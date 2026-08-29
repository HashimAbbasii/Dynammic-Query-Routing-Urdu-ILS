# Phase 4A — corpus-level chunk ANN

**Status:** running / write-up after eval.  
**Does not** retrain the SVM, touch H001–H040, or overwrite Phase 0–3.

## Question

Does a **whole-corpus** chunk ANN (embed every passage, HNSW over all chunks, max-pool to article) beat the current one-vector truncated full index?

Phase 3 only re-ranked Chroma top-15. That is **not** this experiment.

## Eval

Same as Phase 3: Phase 2 `dev` + `internal_val`, **n=78**. Known-item source article. Frozen 40 unused.

## Pre-registered chunking

| | tokens |
| --- | ---: |
| Suggested in the protocol | 192 / overlap 32 |
| **Used** | **96 / overlap 32** (stride 64) |

**Why change before indexing:** `paraphrase-multilingual-MiniLM-L12-v2` has `max_seq_length=128`. A 192-token chunk is truncated to 128, so 192/32 would not isolate “chunking” from “same truncation.” 96 content tokens plus special tokens fit in 128. Overlap 32 is kept from the protocol. Not tuned on eval nDCG or on H001–H040.

Other locked choices: same encoder, cosine, max aggregation, retrieve 80 chunks then unique articles, Chroma HNSW in `artifacts/chroma_chunks/` (not the live `urdu_news` collection).

## Stages

```text
python run_phase4a.py --stage baseline   # must match Phase 3 within tolerance
python run_phase4a.py --stage stats      # full-corpus token lengths
python run_phase4a.py --stage index      # embed all chunks + HNSW (resumable)
python run_phase4a.py --stage eval       # n=78, no frozen 40
```

Adopt chunk ANN only if nDCG@5 rises on n=78 **and** Urdu-only nDCG@5 does not fall.
