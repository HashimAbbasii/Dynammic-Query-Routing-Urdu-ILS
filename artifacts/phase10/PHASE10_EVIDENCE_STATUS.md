# Phase 10A — held-out retrieval evidence status

**Date:** 2026-08-27  
**Scope:** Locate and reconstruct evidence for a later human-relevance evaluation of H001–H040.  
**This phase does not label A/B/C/D.** No BM25 rerun. No Phase 9 rerun. No gold `source_doc_id`. Frozen retrieval unmodified.

**Conclusion:** Query text, detector label, retrieval path, and **rank-1** document content are recovered. **Top-5 rankings are not recoverable** from saved Phase 9 artifacts. A valid Top-5 human-relevance evaluation is **not possible** until ranks 2–5 of the official Phase 9 lists exist. Reconstructing those ranks would require a second retrieval pass, which Phase 8 protocol forbids.

---

## 1. What was asked for vs what exists

| Item | Status |
|---|---|
| Query text for H001–H040 | **Recovered** |
| Detector label | **Recovered** (Phase 9 CSV) |
| Retrieval path | **Recovered** (Phase 9 CSV) |
| Top-5 document IDs | **Not recovered** — only rank 1 was saved |
| Headlines for those IDs | **Recovered for rank 1 only** |
| Article text / snippet | **Recovered for rank 1 only** (500-char snippet) |
| Target 40 × 5 = 200 rows | **Not met** — 40 rows written |

Written file: `artifacts/phase10/HELD_OUT_RETRIEVAL_DETAILS.csv` (40 rows, rank = 1).

---

## 2. Where H001–H040 query text comes from

**Source of record:** `validate/dual_index_routing/labels/heldout_traps.py`

Each `HELDOUT_TRAPS` tuple is:

`(query_id, trap_type, script, category, query, gold)`

- `query` is the actual query string used at retrieval time.
- `gold` is the SHORT/LONG **routing-trap** label, **not** a document ID.

Phase 9 `run_phase9.py` loads this list (`load_queries()` → `item[4]` as `"query"`) and searches with that string. No other query file was used for the official run.

Same strings also appear in:

- `validate/dual_index_routing/labels/heldout_trap_sheet.csv` (`query` column)
- `validate/dual_index_routing/labels/heldout_retrieval_template.csv` (`query` column)

Those copies match the trap file. They were **not** used as Phase 9 gold or as Phase 9 rankings.

---

## 3. Where Top-50 IDs were generated

**In memory only**, inside `experiments/phase9_heldout_evaluation/run_phase9.py`.

Relevant sequence:

1. Rebuild Urdu BM25 and Method D romanized BM25 on `data/clean_articles.csv` (row index = `doc_id`).
2. For each H001–H040 query: `detect_script` → route to `urdu_bm25` or `roman_bm25_method_D`.
3. `hits = index.search(qtoks, top_k=50)`  (`TOP_K = 50`).
4. `top_ids = [int(did) for did, _s in hits]`.

The full `top_ids` list (and scores) existed only in that loop. They were **not** pickled, JSON-dumped, or written to disk.

What **was** written per query in `HELD_OUT_PER_QUERY.csv`:

- `detector_label`
- `retrieval_path`
- `n_hits_returned` = `len(top_ids)`
- `top1_doc_id` = `top_ids[0]` only

**`top1_doc_id` was the only rank saved.** Ranks 2–50 were discarded after the print line.

Phase 9 outputs on disk:

| File | Contains rankings? |
|---|---|
| `experiments/phase9_heldout_evaluation/HELD_OUT_PER_QUERY.csv` | Rank 1 ID only |
| `experiments/phase9_heldout_evaluation/artifacts/official_metrics.json` | Aggregate metrics, `top_k: 50`; no doc IDs |
| `experiments/phase9_heldout_evaluation/artifacts/preflight.json` | Hash / n_docs / versions; no rankings |
| `experiments/phase9_heldout_evaluation/PHASE9_RESULTS.md` | Detector/path summary; no Top-5 IDs |

No `*.pkl`, ranking CSV, or Top-50 dump exists under `experiments/phase9_heldout_evaluation/`.

---

## 4. Files inspected and rejected as Phase 9 Top-5

### `validate/dual_index_routing/labels/heldout_retrieval_template.csv`

This file **does** contain Top-5 IDs and headlines for H001–H040, plus older relevance strings. It is **not** the frozen Phase 9 run.

- Modes are `HEADLINE` and `FULL_CONTENT` (MiniLM / earlier dual-index export), not `urdu_bm25` / `roman_bm25_method_D`.
- For H001 rank 1, Phase 9 BM25 returned `doc_id=77997`. The template HEADLINE rank 1 is `2612`; FULL_CONTENT rank 1 is `60810`. Different system, different lists.
- It already contains relevance labels. Phase 10A must not treat those as gold and must not copy those rows into the evidence CSV.

**Not used.**

### Other held-out files

- `heldout_classification.json` / `.txt` — routing classification, not BM25 ranks.
- `heldout_routed_p5.json` / `.txt` — older P@5 routing experiment, not Phase 9.
- `heldout_trap_sheet.csv` — query metadata + SHORT/LONG student gold; no retrieval IDs.
- `HELD_OUT_FROZEN.txt` — freeze note, not rankings.
- Phase 6 `RANK_DEPTH_ANALYSIS.csv` — QTRN_* development queries, not H001–H040.

---

## 5. Corpus lookup (rank-1 IDs only)

Allowed use: map **already-retrieved** Phase 9 document IDs to headline and news text.

- Corpus: `data/clean_articles.csv` (frozen; article ID = 0-based row index).
- Lookup keys: the 40 `top1_doc_id` values from `HELD_OUT_PER_QUERY.csv`.
- Fields: `Headline`, first 500 characters of `News Text` (newlines collapsed).

No corpus search, no alternate document selection, no reranking.

All 40 IDs resolved. Helper used only for this join: `experiments/phase10a_evidence/_recover_rank1.py`.

---

## 6. Incomplete lists even in the original run

`n_hits_returned` shows the original Top-50 was not always length 50:

| Query | `n_hits_returned` | Implication |
|---|---|---|
| H027 | 8 | Ranks 1–5 existed in memory; only rank 1 was saved |
| H036 | 1 | Official list has **only one** document; a Top-5 sheet for H036 would have 1 row even if logging had been complete |
| All other H001–H040 | 50 | Ranks 2–5 existed in memory; only rank 1 was saved |

---

## 7. Why a BM25 replay is not reconstruction

Re-running `index.search(..., top_k=50)` would be a **second retrieval pass**, not recovery of the saved official lists.

Phase 8 `FINAL_EVALUATION_PROTOCOL.md`:

- Preamble: one held-out run; **does not authorize a second test pass**.
- §17: no re-running with a “fix”; changing ranks invalidates the official run. A logging bug that **does not change ranks** may be noted.

The missing Top-5 IDs are a **logging omission**, not a retrieval bug. Replaying BM25 would generate **new** rank lists. Even with identical code, NumPy `argpartition` / tie order is not guaranteed to reproduce the original in-memory Top-50. Protocol does not treat a replay as the official run.

**Not done.** Phase 9 was not rerun. Frozen BM25 / routing / queries were not changed.

---

## 8. Evidence file produced

`artifacts/phase10/HELD_OUT_RETRIEVAL_DETAILS.csv`

Required columns present:

`query_id`, `query_text`, `detector_label`, `retrieval_path`, `rank`, `doc_id`, `headline`, `news_text_or_snippet`

Extra columns (status only):

- `n_hits_returned_phase9` — from the official CSV
- `ranks_2_to_5_recovered` — always `0`

Row count: **40** (one rank-1 row per query), not 200.

---

## 9. Is Phase 10 human relevance evaluation now possible?

**No — not a valid Top-5 evaluation.**

A judge would have:

- All 40 query strings
- Detector and path
- Only the **first** retrieved document (headline + snippet)
- No ranks 2, 3, 4, or 5 of the frozen Phase 9 lists

Human P@5 / nDCG@5 / “relevant in Top-5” **cannot** be computed from rank-1 alone without inventing the missing four documents.

What **is** possible with current evidence (if a later protocol asks):

- Rank-1-only inspection (40 judgments), clearly labelled as incomplete vs Top-5
- That is **not** the Phase 10 design requested (40 × 5)

**Missing items that block Top-5 evaluation:**

1. Phase 9 `top_ids[1:5]` for 39 queries (H036 has no ranks 2–5 even in the original list).
2. Optionally ranks 6–50 (not required for k=5).
3. Original BM25 scores (not required for relevance labeling if IDs exist).

---

## 10. Stop

No A/B/C/D labels were assigned.  
No gold documents were chosen.  
No MiniLM template rows were copied.  
No second Phase 9 pass.

To make Top-5 human evaluation possible later, a **new sealed protocol** would have to authorize either:

- a logging-only reconstruction that is declared **not** to replace the official Phase 9 known-item table, or
- an explicit second retrieval dump whose rank lists are treated as a **new** artifact (not as a silent rewrite of Phase 9).

That decision is out of scope for Phase 10A.
