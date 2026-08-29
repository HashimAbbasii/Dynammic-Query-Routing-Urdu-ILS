# Architecture audit — full-article retrieval

**Experiment:** Phase 3  
**Rule:** no SVM retrain, no edits to H001–H040, no RRF, no new router.  
**Inspection date:** 23 Aug 2026.  
**Code inspected, not assumed.**

## 1. Article preprocessing

| Step | Location | What it does |
| --- | --- | --- |
| Load raw CSV | `notebooks/01_preprocessing.ipynb` | `data/urdu_news.csv`, UTF-8-SIG, `encoding_errors='replace'` |
| Column names | same | `Index, Headline, News Text, Category, Date, URL, Source, News length` |
| Null drop | same | `df.dropna(); reset_index(drop=True)` → **111,860** rows |
| Combine fields | same | `combined_text = Headline + ' ' + News Text` |
| Save | same | `data/clean_articles.csv` |

There is **no** Unicode NFC/NFKC, no Arabic/Persian character folding, no diacritic strip, no stopword removal, no stemming, and no length clipping at this stage.

## 2. Article cleaning

Cleaning is limited to dropping null rows. HTML, punctuation, English tokens, digits, and duplicate near-matches are left as in the source dump.

## 3. Text normalization

**Documents:** none beyond concatenation.  
**Queries:** `transliterate_roman()` in `validate/dual_index_routing/retrieve.py` only.  
Phase 2 `experiments/phase2_oracle/textnorm.py` is for **leakage checks**, not retrieval (`"Do not use for retrieval."`).

## 4. Urdu normalization

None. Ye/he/kaf variants, tatweel, and diacritics are not canonicalized.

## 5. Roman Urdu handling

| Path | Function | Behaviour |
| --- | --- | --- |
| Live retrieve | `transliterate_roman` | If Urdu-script ratio ≥ 0.3, leave query. Else whitespace-split lookup in `models/roman_urdu_dict_expanded.json`. Unknown tokens stay Latin. |
| Notebook 05 | `transliterate_roman_urdu` | Dictionary + optional `difflib` fuzzy match (cutoff 0.75, words ≥ 3 chars). **Not** wired into `retrieve.py`. |

Documents were embedded as native Urdu script. Romanization is **query-only**.

## 6. Tokenization

WordPiece/SentencePiece of `paraphrase-multilingual-MiniLM-L12-v2` (HuggingFace tokenizer attached to SentenceTransformer). No custom Urdu tokenizer. No whitespace tokenizer for retrieval.

## 7–11. Embedding generation

| Item | Value | Evidence |
| --- | --- | --- |
| Model | `paraphrase-multilingual-MiniLM-L12-v2` | `notebooks/02_embeddings.ipynb`, `retrieve.py` |
| Dimension | 384 | notebook print; `embeddings.npy` shape `(111860, 384)` |
| `max_seq_length` | **128** | notebook: `Model max sequence length: 128` |
| Truncation | left-to-right, first 128 tokens | Sentence-Transformers default; no override |
| Batching (index) | `batch_size=64` | `model.encode(df['combined_text'].tolist(), batch_size=64, ...)` |
| Full-article input | entire `combined_text` string, then truncated by the encoder | one vector per row |
| Headline input | `Headline` only | `data/headline_embeddings_phase2_5_cache.npy` |
| Chunking at index time | **none** | confirmed |

**Answer to “what does the encoder actually see?”**  
For a long article: **the headline plus the start of the body, cut at 128 tokens.** The rest of the article is discarded before the transformer.

## 12–14. ChromaDB

| Item | Value | File |
| --- | --- | --- |
| Path | `data/chromadb` | `retrieve.py` `CHROMA_PATH` |
| Collection | `urdu_news` | `notebooks/03_chromadb.ipynb` |
| Space | cosine (`hnsw:space: cosine`) | create_collection metadata |
| Other HNSW params | **not set** (Chroma defaults: M, ef_construction, ef_search) | same notebook |
| IDs | string row index `"0"` … `"111859"` | `batch_ids = [str(j) for j in range(i, batch_end)]` |
| Stored documents | `combined_text` | display only |
| Stored embeddings | precomputed `data/embeddings.npy` | not encoded at add-time |
| Add batch | 1000 | notebook |
| Count | 111,860 | notebook verification |

## 15–18. Retrieval

| Item | Headline room | Full room |
| --- | --- | --- |
| Function | `search_headlines` | `search_full_content` |
| Query embed | `sem_model.encode(query)` | same, `.tolist()` for Chroma |
| Search | brute-force cosine vs NumPy cache (`sklearn.metrics.pairwise.cosine_similarity`) | `collection.query(query_embeddings=..., n_results=top_k)` |
| Score | cosine similarity | `sim ≈ 1 - distance` |
| Default `top_k` | 15 in retrieve.py; Phase 2 oracle used 20 | same |
| Metadata filter | **none** | **none** |
| L2-normalize flag | not passed (`normalize_embeddings` default False) | same |

Phase 2 known-item labels used `top_k=20` then cut at 5. Phase 3 re-queries at **15** so hit@5/@10/@15 share one list.

## 19. Document IDs

Chroma IDs = pandas row index after `reset_index(drop=True)`. `source_doc_id` in Phase 2 oracle CSVs is this integer. `df.iloc[doc_id]` must be the article.

## 20. Article-to-chunk mapping

**None.** No chunk table, no parent-id metadata.

## 21. Deduplication

Only null-row drop. Near-duplicate headlines can exist as separate IDs.

## 22–23. Truncation / max tokens

Effective limit = **128 tokens** (model), not a character cap in our code. Special tokens count toward the 128.

**Measured (Phase 3):** sample n=4,000 combined_text token lengths: min 57, mean 367, median 295, p90 652, p95 814, p99 1,378, max 5,379. **95.35%** exceed 128 tokens. Eval source articles: **94.87%** exceed 128 (mean 421, median 355). Bodies: mean 1,267 characters, max 36,198. Headlines: mean 52 characters, max 200 — titles usually fit in 128 tokens; full articles do not.

## 24. Batching

Index-time encode: 64. Chroma add: 1000. Query-time: one query embedding per request.

## 25. Headline vs full normalization difference

Same encoder, **different strings**:

- Headline: title only (usually < 128 tokens → little truncation).
- Full: `Headline + ' ' + News Text` then truncate to 128 → title + lead, **not** a whole-document vector.

Query-side Roman dictionary is applied to **both** rooms equally. It is **not** applied to documents.

## Hybrid / lights (out of Phase 3 scope)

`search_hybrid` mixes min-max-normalized headline and full scores (`alpha=0.5`). `expand_query` appends a few Urdu/English filler words. Phase 3 does not enable RRF, confidence routing, or a new router.

## Disk footprint (measured)

| Artifact | Size |
| --- | --- |
| `data/clean_articles.csv` | 540.1 MB |
| `data/embeddings.npy` | 171.8 MB |
| `data/headline_embeddings_phase2_5_cache.npy` | 171.8 MB |
| `data/chromadb/` | ~3.75 GB |

## Implications going into the experiments (now measured)

1. **95.35%** of articles (sample n=4,000) exceed 128 tokens. The full index is a **lead-paragraph index**, not a whole-document index.
2. 96-token chunks with overlap 24 fit the encoder; 200–300 token chunks would still truncate. That config was tested as **top-15 re-rank only**.
3. Roman queries are query-only dictionary maps; documents stay Urdu script. Those rows were not used to select a method.
