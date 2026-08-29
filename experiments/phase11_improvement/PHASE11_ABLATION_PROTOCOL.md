# Phase 11 ablation protocol

Query-side ROMAN expansions/stoplist only.  
Does **not** replace Phase 9. Does **not** load H001–H040. Does **not** create H041+.

## Frozen (unchanged)

- Corpus `data/clean_articles.csv`, SHA-256 `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231`
- Dictionary file 198 keys (not edited)
- Unicode `detect_script`; URDU/MIXED → Urdu BM25; ROMAN → Method D **document** index
- BM25 k1=1.5, b=0.75, top_k=50
- Tokenizer and Method D `romanize_token` on **documents**

## Query-side only (ROMAN detector label)

- M1/M2: **expand** (keep original tokens, append aliases)
- M3: after expansion, drop stoplist tokens from the **query**
- `hai` / `bhi` remain **off**
- Forbidden mappings: diesel, temperature, iphone, football, petrol as new rows

## Pools

| Pool | Use |
|---|---|
| n=78 `dev` + `internal_val` | Hard ExactSource Hit@5 gate (≥ 68/78) |
| Train `roman_urdu` n=64 | Selection diagnostic (Hit@5, nDCG@5, MRR) |

H001–H040 not loaded. No human labels.

## Models

| ID | Transform |
|---|---|
| M0 | none |
| M1 | M1 expansions |
| M2 | M1 + M2 expansions |
| M3 | M1 + M3 stoplist |
| M4 | M1 + M2 + M3 stoplist |

## Acceptance

- M0 must be 68/78.
- M1–M4: n=78 ≥ 68/78 **and** train Roman Hit@5 ≥ M0, else **REJECTED**.
- No retuning after seeing scores.
- Winner among passing M1–M4: max train Roman Hit@5, then nDCG@5, then simpler (M1 > M2 > M3 > M4).
