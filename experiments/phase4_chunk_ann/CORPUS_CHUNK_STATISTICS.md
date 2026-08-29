# Corpus chunk statistics

Full cleaned corpus, **before** building the chunk index.
Tokenizer = `paraphrase-multilingual-MiniLM-L12-v2`. Lengths are content tokens (`add_special_tokens=False`).

## Why not 192 / 32?

Encoder max_seq_length is 128 including special tokens. A 192-token chunk would be silently truncated to 128, so 192/32 does not test chunking vs one truncated vector. Content window 96 + CLS/SEP fits in 128. Overlap 32 is taken from the protocol. Set from the tokenizer limit before indexing; not tuned on H001-H040 or on eval nDCG.

## Token length of combined_text (n=111860)

| stat | tokens |
| --- | ---: |
| min | 41.0 |
| max | 9769.0 |
| mean | 369.0 |
| median | 291.0 |
| p75 | 442.0 |
| p90 | 661.0 |
| p95 | 838.0 |
| p99 | 1456.0 |

- Share of articles > 128 tokens: **94.42%**
- Share of articles > 96 tokens: **98.3%**

## Pre-registered plan (96 / 32, stride 64)

| quantity | value |
| --- | ---: |
| total chunks | 644100 |
| mean chunks / article | 5.758 |
| median chunks / article | 5.0 |
| p95 chunks / article | 13.0 |
| max chunks / article | 153 |
| dim | 384 |
| raw embedding store | ~0.99 GB |

H001–H040 were not used.
