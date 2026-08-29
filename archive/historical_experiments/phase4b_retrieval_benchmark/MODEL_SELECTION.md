# Phase 4B — model selection (registered before scoring)

This choice is **not** based on n=78 retrieval scores. H001–H040 were not used.

## Environment constraint (to be filled at runtime)

See `hardware.json` written by `run_phase4b.py`. This machine previously ran Phase 4A encoding on **CPU** (no CUDA). Full-corpus indexing must stay within that budget.

## Rejected (not run)

| Model | Why not |
| --- | --- |
| MiniLM with `max_seq_length` raised | Same 128-trained weights; silent quality drop, not a new encoder |
| `bge-m3` / GTE-Qwen / e5-large | Too heavy for CPU full-corpus (111,860 docs) in this phase |
| Ten-way model sweep | Forbidden: would be post-hoc selection on the same 78 queries |
| Chunking this encoder | Would confound “longer context” with “chunk ANN” (already Phase 4A) |

## Selected: `intfloat/multilingual-e5-small`

| Property | Value |
| --- | --- |
| Hugging Face id | `intfloat/multilingual-e5-small` |
| Role | Retrieval encoder (E5), not a generative LLM |
| Max sequence length | **512** tokens (4× current MiniLM 128) |
| Embedding dim | **384** (same width as current MiniLM) |
| Similarity | Cosine on L2-normalised vectors |
| Prefixes | `query: …` / `passage: …` (E5 protocol, fixed) |
| Weights | Open; sentence-transformers compatible |
| Document text | `Headline + News Text` (`combined_text`), **one vector per article**, no extra chunking |

### Why this one

1. **Multilingual / Urdu:** E5-multilingual is trained for retrieval across 100+ languages, including Arabic-script languages; Urdu is in-scope for this encoder class.
2. **Longer effective context:** 512 tokens vs MiniLM 128. Phase 3: median article ~291 tokens, ~95% exceed 128. A 512-token encoder covers the median and a large fraction of the body that MiniLM truncates.
3. **Retrieval behaviour:** Contrastive retrieval training (not only STS), which matches the known-item task better than a generic STS MiniLM.
4. **Cost:** Small variant (384-d) is the only long-context option likely to finish a full 111,860-doc pass on CPU in this session. Base/large would be a different experiment.
5. **Controlled contrast:** Same one-vector-per-article setup as Old Full. Isolates encoder+context, not fusion or chunking.
6. **Reproducible:** Fixed HF id, no fine-tuning, no n=78 hyperparameter search.

### What this is not

It is **not** 8k-token “true full document” encoding. Articles longer than 512 tokens are still truncated. Phase 3 p90 was ~661 tokens, so truncation remains for the tail. The question is whether **512 vs 128** moves known-item retrieval.

## Feasibility result (this machine)

CPU only, 12 cores. Prototype 400 docs: **2.3 docs/s**, **13.5 h** extrapolated for 111,860 articles. The 4-hour gate **failed**. Full e5-small index was **not** built. The model was **not** replaced after the gate.
