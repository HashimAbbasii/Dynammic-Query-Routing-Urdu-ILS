# Module 1 ablation on sealed R-dev

**Status:** Candidate intervention evaluation (not frozen M0).

## Objective

Test whether Roman-query surface normalization improves retrieval on R-dev without regressing Urdu or MIXED paths.

## Frozen inputs (read-only)

| Artifact | SHA-256 (sealed) |
| --- | --- |
| `queries_r_dev.csv` | `1603b37eeee41fa6270f4e13d185c8eebd4512d025cd5fc67e8a81de9407e75f` |
| `R_TOP50_RETRIEVAL.csv` (M0) | `927a14a25b6f1de2a5c28aabdc2d8cbc0d4336e0b2b437490691a7bff63a2aa2` |
| `qrels_r_dev.csv` | `506305b5401102a3659d21b69c7a937bcdcde78b21a1409a6a6132255ff37bcb` |

M0 baseline: KI ExactSource Hit@5 from frozen Top-50; NAT Success@5 = 12/50 from frozen qrels on M0 Top-5.

## M0 routing (unchanged)

1. `detect_script(raw query)` → URDU / ROMAN / MIXED / OTHER
2. URDU or MIXED → Urdu BM25 on **raw** tokenization
3. ROMAN → Method D roman BM25 on query tokens (latin, post-intervention for candidates)

BM25: k1=1.5, b=0.75, top_k=50. Corpus and dictionary frozen.

## Candidates

| ID | Name | ROMAN-branch intervention |
| --- | --- | --- |
| **M1-A** | Conservative normalization | Layer A only: NFKC, lowercase, punctuation→space, whitespace (`NormalizationConfig` defaults) |
| **M1-B** | Dictionary-assisted | M1-A + map tokens through frozen `_VARIANT_TO_DICT_KEY` aliases; if canonical form is a dict **key**, use that key (198-key resource, read-only) |
| **M1-C** | Conservative + dictionary | Identical to M1-B (Layer A + closed alias table + dict-key canonicalization) |

Module 1 does **not** apply Method C grapheme→Urdu rewrite or vowel deletion.

## NAT evaluation with frozen qrels

Judgments label M0 Top-5 documents only. For candidates:

**Success@5** = (# NAT queries where candidate Top-5 contains ≥1 doc with qrel label A or B) / 50.

Documents outside the M0 judgment pool are not relabeled. This is a conservative pool-based comparison documented in the manifest.

## Guardrails

- Urdu and MIXED queries: **identical** to M0 (no query transform).
- No BM25 retuning, no routing change, no dictionary edit, no M0 file edits.

## Outputs

Per candidate: Top-50 CSV, JSON experiment record, aggregated in `MODULE1_RESULTS.md` and `MODULE1_MANIFEST.json`.
