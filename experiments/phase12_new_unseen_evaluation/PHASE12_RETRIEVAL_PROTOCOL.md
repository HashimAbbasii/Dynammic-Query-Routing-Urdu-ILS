# Phase 12 retrieval protocol — frozen M0, one shot

**Status:** EXECUTION (after sealed query files).  
**Official system:** M0. Phase 11 did not replace it.  
**Does not replace:** Phase 9 n=78 ExactSource Hit@5 = 68/78 = 0.8718.

This run evaluates **already sealed** `queries_k.csv` and `queries_u.csv`.  
Do **not** edit those files. Do **not** apply M1–M4. Do **not** label U.

---

## 1. Purpose

| Subset | Question | Gold | This run computes |
|---|---|---|---|
| K001–K040 | Did the **exact** source article land in Top-k? | `source_doc_id` assigned at query creation | ExactSource Hit@1/5/10/50 |
| U001–U040 | Retrieve a frozen Top-50 for later human labels | **none** | Retrieval dump only |

Primary K metric: **ExactSource Hit@5**.  
U Success@5 / P@5 / nDCG / MRR are **forbidden** in this step.

Do not combine K and U into one score.  
Do not compare K to H001–H040.

---

## 2. Frozen M0 (must match Phase 8 / Phase 9)

- Corpus `data/clean_articles.csv`, n=111860  
- SHA-256 `8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231`  
- Dictionary `models/roman_urdu_dict_expanded.json`, 198 keys  
- SHA-256 `30c3f61a64ec641abbb3acdbc7a8bcaf197f0238f1bf9e76c2c7ce8e590f86a3`  
- URDU / MIXED / OTHER → Urdu BM25  
- ROMAN → Method D romanized-document BM25  
- Query tokens: `tokenize(query_text)` only (no spelling expansion)  
- k1=1.5, b=0.75, top_k=50  
- Detector: `run_phase5.detect_script`

---

## 3. Sealed inputs (must match before search)

| File | SHA-256 |
|---|---|
| `queries_k.csv` | `124e452693f98baedf510618240c154df68d56b6b7a37ed085a6512c13d13ff6` |
| `queries_u.csv` | `684fd1e19eddb717f5897d869ef0ca0ed586316c5a7e1d2d23006e0748fc53b9` |

If either hash differs: **STOP**. Do not retrieve.

---

## 4. Preflight

See `PREFLIGHT_CHECKLIST.md`. Implemented in `run_phase12.py`.  
If any check fails: write `artifacts/preflight.json` with `preflight_pass: false` and **exit**.

---

## 5. Retrieval (one pass)

1. Build Urdu and Method D roman indexes from `combined_text` exactly as Phase 10B / Phase 11 M0.  
2. For each K then each U query: detect script on **raw** `query_text`, route, search Top-50.  
3. Persist full Top-50.  
4. Score K ExactSource from `source_doc_id` vs retrieved `doc_id`.  
5. Write U Top-5 with **empty** `relevance_label`.

Forbidden:

- Query rewrite after seeing ranks  
- M1/M2/M3/M4  
- Dictionary / BM25 / routing / Method D edits  
- Opening H001–H040, Phase 10C qrels, `heldout_retrieval_template.csv`  
- Inventing U gold ids  
- Human labels  
- Writing into Phase 9 / 10B / 10C / 11 folders  

---

## 6. Stop

After CSVs and `K_RESULTS.md` / U retrieval stats exist: **STOP**.  
Do not start annotation. Do not tune M0.
