# Phase 15 step 1 — local inspection report

**Date:** 2026-10-04  
**Scope:** inspection plus two new files under `experiments/ultra_v2/phase15_granite/`. No TEST files opened. No queries. No Hit@k or other retrieval score. No embedding ran on this machine. No commit.

---

## Result

The frozen Phase 3 corpus file matches the expected SHA-256. Git was clean on branch `ultra-v2-phase15-granite` before these two files were added. That branch name is not `research/ultra-v2-phase15-granite`. The public Hugging Face card for the 311M multilingual R2 encoder was retrieved; the exact task slug returned HTTP 401 and has no public card. A Colab-only pilot script was written. It was not executed here.

### 1. Branch and working tree

| Item | Observed |
| --- | --- |
| Branch requested in the task | `research/ultra-v2-phase15-granite` |
| Branch at inspection | `ultra-v2-phase15-granite` |
| Upstream | `origin/ultra-v2-phase15-granite` (up to date at inspection) |
| HEAD | `3b2e829bf9769d16f9b604ee68d7cc50ce128fa7` |
| Working tree at inspection | clean |
| Same commit also pointed at | `research/ultra-v2-strengthening` |

`research/ultra-v2-phase15-granite` is not a local branch. This is a name mismatch, not a dirty tree. No branch rename was made.

### 2. Corpus

Phase 3 reads one corpus file. `experiments/ultra_v2/phase3_dense/run_dense_baseline.py` imports `experiments/phase5_roman_urdu/run_phase5.py` and hashes `p5.CORPUS`. That path is `data/clean_articles.csv` from the repository root. `DENSE_PREREGISTRATION.md` §4 names the same path. `artifacts/dense_index_meta.json` and `artifacts/dense_config.json` record the same SHA-256.

| Item | Value |
| --- | --- |
| Path | `data/clean_articles.csv` |
| Bytes | 540,050,203 |
| Last write time | 2026-05-24 21:25:37 (local) |
| SHA-256 computed 2026-10-04 | `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231` |
| Expected | `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231` |
| Match | yes |

Header only (no row body read for this check): `Index,Headline,News Text,Category,Date,URL,Source,News length,combined_text`.

The row count was not re-parsed locally. Phase 3's frozen meta says 111,860 rows and text column `combined_text`. The Colab script loads the file and stops if the row count is not 111,860. CSV SHA match is the byte-level check this step required.

No second corpus file is hashed by the Phase 3 runner.

### 3. Model card and config

Metadata only. No weights downloaded.

**Task slug.** `GET https://huggingface.co/api/models/ibm-granite/granite-embedding-multilingual-r2` on 2026-10-04 returned HTTP 401, body `{"error":"Invalid username or password."}`, header `X-Error-Message: Invalid username or password.` No `HF_TOKEN` was set in the environment. That slug did not yield a model card.

**Public 311M repo.** The card that matches the task's "311M" multilingual R2 description is:

- Id: `ibm-granite/granite-embedding-311m-multilingual-r2`
- API `sha` and raw-file `X-Repo-Commit`: `44399559930365213510b1ee2eb15ded83374f0e`
- `lastModified`: `2026-05-18T20:15:41.000Z`
- `gated`: false
- `library_name`: `sentence-transformers`
- Safetensors: `{"parameters":{"BF16":311664384},"total":311664384}`

Quoted from the model card README at that revision:

> Granite-Embedding-311M-Multilingual-R2 is a 311M parameter dense embedding model from the Granite Embeddings collection for high-quality multilingual text embeddings. It produces 768-dimensional vectors with a context length of up to 32,768 tokens.

> License: Apache 2.0

Card architecture table:

| Feature | granite-embedding-311m-multilingual-r2 |
| --- | --- |
| Embedding size | 768 |
| Max. Sequence Length | 32,768 |
| # Parameters | ~311M |

Card Transformers example, on pooling and normalization:

> Perform pooling. granite-embedding-311m-multilingual-r2 uses CLS Pooling

```python
query_embeddings = model_output[0][:, 0]
query_embeddings = torch.nn.functional.normalize(query_embeddings, dim=1)
```

The same example calls `model.encode` / `tokenizer(...)` on the raw query strings. It does not concatenate a `query:` or `passage:` tag. The Sentence Transformers example likewise calls `model.encode(input_queries)` and `model.encode(input_passages)` with no prefix string.

`config_sentence_transformers.json` at the same revision:

```json
"prompts": {"query": "", "document": ""},
"default_prompt_name": null,
"similarity_fn_name": "cosine"
```

`1_Pooling/config.json`:

```json
"word_embedding_dimension": 768,
"pooling_mode_cls_token": true,
"pooling_mode_mean_tokens": false,
"pooling_mode_max_tokens": false,
"pooling_mode_mean_sqrt_len_tokens": false,
"pooling_mode_weightedmean_tokens": false,
"pooling_mode_lasttoken": false,
"include_prompt": false
```

`modules.json` lists Transformer, then Pooling, then `sentence_transformers.models.Normalize`. `2_Normalize/config.json` is not in the repo (HTTP 404). The Normalize class is still declared in `modules.json`.

`sentence_bert_config.json`: `{"max_seq_length": 32768, "do_lower_case": false}`.

`config.json`: `"dtype": "bfloat16"`, `"hidden_size": 768`, `"max_position_embeddings": 32768`, `"classifier_pooling": "cls"`, `"architectures": ["ModernBertModel"]`, `"vocab_size": 262152`.

`tokenizer_config.json`: `"add_bos_token": true`, `"add_eos_token": false`, `"model_max_length": 32768`, `"bos_token": "<bos>"`, `"eos_token": "<eos>"`, `"pad_token": "<pad>"`, `"unk_token": "<unk>"`, `"use_default_system_prompt": false`. No `chat_template` key. No query or document prefix field.

The README does not name a runtime dtype. The config field and the weight shard both say bfloat16. That is the documented storage dtype.

Tokenizer attribution on the card, separate from the Apache 2.0 model license:

> The multilingual tokenizer used by this model is derived from the Gemma 3 tokenizer by Google. ... Use of the Gemma tokenizer is subject to the Gemma Terms of Use.

Urdu (`ur`) is in the card's list of 52 languages with explicit retrieval-pair training. That is a coverage statement on the card, not an ULTRA score.

The Hugging Face blog post (2026-05-14) says the R2 models "require no task-specific instructions". That sentence is not in the model card. The card evidence for prefixes is the empty prompt strings and the examples above.

MTEB numbers appear on the card. They were not used to choose a model, change code, or compute a score in this step.

### 4. Local machine

| Item | Measured |
| --- | --- |
| Machine | Dell Latitude 5430 |
| OS | Windows 11 Pro 10.0.26100 |
| RAM | 16,849,256,448 bytes (15.69 GiB). The stated 16 GB matches this capacity. |
| Free disk on C: | 53,423,063,040 bytes (53.42 GB decimal, 49.76 GiB). The stated ~54 GB matches the decimal figure. |
| GPU | Intel(R) UHD Graphics, driver 32.0.101.7088. A Parsec virtual display adapter is also present. |
| `nvidia-smi` | not installed |
| torch | 2.13.0+cpu, `cuda.is_available()` False, device count 0 |

The script was started once on this machine. It passed the SHA gate and exited on the CUDA check before parsing the CSV or downloading weights. Token-length percentiles, peak VRAM, embedding shape, NaN count, and full-corpus hours are not known yet.

### 5. What the Colab script will do

`step1_pilot_colab.py` re-checks the corpus SHA-256, then stops if CUDA is missing, before it parses the CSV or contacts Hugging Face. On CUDA it loads text with the Phase 3 `combined_text` rule and stops unless there are 111,860 rows. On CUDA it downloads the pinned revision excluding ONNX and OpenVINO files, checks dim 768, max length 32768, empty prompts, and CLS pooling, then tokenizes the full corpus with truncation off (`add_special_tokens=True`). It draws 500 row indices with `random.seed(15)` and `random.sample`, encodes those documents only, in fp16, at candidate `max_length` 32768 and batch size 8, and writes a JSON summary. It does not write the embedding matrix. Output under OneDrive or inside this git repo is refused.

Batch size 8 is not on the model card. A single batch size is required to time an encode. It was not chosen with a retrieval score.

fp16 is the runtime this step asked for. The checkpoint dtype is bfloat16. The script requests float16 and stops if parameters do not land in float16. A Colab T4 does not provide bfloat16 tensor cores; the cast is a pilot runtime choice, not a second model.

---

## Scientific meaning

The corpus bytes are the same object Phase 3 indexed. Phase 15 is still that collection, not a new or filtered one. Nothing here says Granite retrieves better or worse than `intfloat/multilingual-e5-small`.

The encoder identity is the public 311M checkpoint at commit `44399559930365213510b1ee2eb15ded83374f0e`: 768-d CLS vectors, L2-normalized by the published Sentence Transformers stack, 32,768-token ceiling, empty query and document prompts. Phase 3's E5 prefixes (`query: ` / `passage: `) do not transfer. Copying them onto Granite would contradict this card.

Storage dtype is bfloat16. The Colab pilot casts to fp16 because that is the specified T4 run, and it records the dtypes it actually gets. Until that JSON exists, there is no measured truncation rate, VRAM, or hour estimate.

---

## Good / bad

**Good**

- Corpus SHA-256 matches the frozen value. Not blocked on the corpus.
- Working tree was clean at inspection. Existing phase files were not edited.
- Card fields the step asked for are quoted from the revision above, not filled in from memory.
- The script refuses CPU embedding, TEST paths, query encoding, and score computation.

**Bad, or not yet known**

- Branch name does not match `research/ultra-v2-phase15-granite`.
- The literal slug `ibm-granite/granite-embedding-multilingual-r2` did not return a public card (HTTP 401). The script pins the public 311M id instead. Treat that as an identifier flag, not as permission to try a third model.
- Config dtype is bfloat16; the pilot runtime is fp16. Both are recorded. They are not the same dtype.
- Model license on the card is Apache 2.0. The tokenizer is additionally under the Gemma Terms of Use.
- This machine has no CUDA device. The pilot numbers do not exist yet.
- The repo lives under OneDrive (`C:\Users\User\OneDrive\Documents\ULTRA_Project`). A full float32 matrix would be 111,860 × 768 × 4 = 343,633,920 bytes (about 328 MiB), half of that in float16, plus the weight snapshot. Sync can lock or partially replicate those files. Write them outside the synced folder, or exclude them from sync. The pilot script refuses an output directory under OneDrive or inside the git repo.

No leakage path was opened: TEST was not read, queries were not encoded, and no ranking metric was computed. The 500-row draw is a corpus subsample for a timing pilot, not an evaluation set.

---

## Next step

Run `step1_pilot_colab.py` on a Colab T4 with the frozen CSV on local Colab disk. Bring back `step1_pilot_summary.json` only. Do not open TEST. Do not encode queries. Do not compute Hit@k. Do not download a second encoder. Confirm the 311M slug versus the task string before any later step treats the revision as the frozen Phase 15 encoder. Keep any full-corpus matrix out of OneDrive.
