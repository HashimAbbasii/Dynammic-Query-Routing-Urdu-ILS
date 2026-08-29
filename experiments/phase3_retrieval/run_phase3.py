# -*- coding: utf-8 -*-
"""Phase 3 full-article retrieval forensics. Eval = Phase 2 dev + internal_val only."""
from __future__ import annotations

import csv
import json
import math
import os
import random
import sys
import time

import numpy as np
import pandas as pd

_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(_DIR, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "validate", "dual_index_routing"))
from retrieve import search_full_content, search_headlines, transliterate_roman  # noqa: E402

SEED = 42
EVAL_SPLITS = {"dev", "internal_val"}
ORACLE_CSV = os.path.join(ROOT, "experiments", "phase2_oracle", "oracle_all.csv")
CORPUS = os.path.join(ROOT, "data", "clean_articles.csv")
OUT = _DIR
FIG = os.path.join(OUT, "figures")
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
MAX_SEQ = 128
CHUNK_TOKENS = 96
CHUNK_OVERLAP = 24
MIXED_DELTA = 0.05
TOP_KS = (5, 10, 15)
JSON_LIST_KEYS = (
    "headline_top5_ids",
    "full_top5_ids",
    "full_top15_ids",
    "full_top15_scores",
    "headline_top5_titles",
    "full_top5_titles",
)


def ndcg_at(rank, k=5):
    if rank is None or rank > k:
        return 0.0
    return 1.0 / math.log2(rank + 1)


def p_at(rank, k=5):
    return (1.0 / k) if (rank is not None and rank <= k) else 0.0


def metrics_from_ranks(ranks, k=5):
    n = len(ranks)
    hits = [1 if (r is not None and r <= k) else 0 for r in ranks]
    return {
        "n": n,
        "source_hit_rate": round(float(np.mean(hits)) if n else 0.0, 4),
        "p_at_k": round(float(np.mean([p_at(r, k) for r in ranks])) if n else 0.0, 4),
        "ndcg_at_k": round(float(np.mean([ndcg_at(r, k) for r in ranks])) if n else 0.0, 4),
        "recall_at_k": round(float(np.mean(hits)) if n else 0.0, 4),
        "mrr": round(float(np.mean([1.0 / r if (r and r < 999) else 0.0 for r in ranks])) if n else 0.0, 4),
    }


def oracle_from_ndcg(h, f, delta=MIXED_DELTA):
    if h == 0.0 and f == 0.0:
        return "MIXED"
    if abs(h - f) < delta:
        return "MIXED"
    return "HEADLINE" if h > f else "FULL"


def summarize(arr):
    a = np.asarray(arr, dtype=float)
    if a.size == 0:
        return {"n": 0}
    return {
        "n": int(a.size),
        "min": float(a.min()),
        "max": float(a.max()),
        "mean": float(a.mean()),
        "median": float(np.median(a)),
        "p90": float(np.percentile(a, 90)),
        "p95": float(np.percentile(a, 95)),
        "p99": float(np.percentile(a, 99)),
    }


def token_len(tokenizer, text):
    return len(tokenizer.encode(str(text or ""), add_special_tokens=True, truncation=False))


def chunk_text(tokenizer, text, size=CHUNK_TOKENS, overlap=CHUNK_OVERLAP):
    ids = tokenizer.encode(str(text or ""), add_special_tokens=False, truncation=False)
    if not ids:
        return [""]
    out = []
    start = 0
    while start < len(ids):
        out.append(tokenizer.decode(ids[start : start + size], skip_special_tokens=True))
        if start + size >= len(ids):
            break
        start += size - overlap
    return out or [""]


def dir_size(path):
    if os.path.isfile(path):
        return os.path.getsize(path)
    tot = 0
    if not os.path.exists(path):
        return 0
    for d, _ds, fs in os.walk(path):
        for fn in fs:
            tot += os.path.getsize(os.path.join(d, fn))
    return tot


def rank_of(hits, src):
    for rank, (did, score) in enumerate(hits, 1):
        if int(did) == int(src):
            return rank, float(score)
    return None, None


def load_eval_rows():
    rows = []
    with open(ORACLE_CSV, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["query_id"].startswith("H"):
                raise RuntimeError("frozen id in oracle csv: %s" % r["query_id"])
            if r["split"] not in EVAL_SPLITS:
                continue
            r["source_doc_id"] = int(r["source_doc_id"])
            rows.append(r)
    return rows


def write_csv(path, header, rows):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def main():
    random.seed(SEED)
    np.random.seed(SEED)
    os.makedirs(FIG, exist_ok=True)
    eval_rows = load_eval_rows()
    print("Phase 3 eval n=%s splits=%s" % (len(eval_rows), sorted(EVAL_SPLITS)), flush=True)

    print("Loading corpus + encoder...", flush=True)
    df = pd.read_csv(CORPUS, encoding="utf-8-sig")
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(MODEL_NAME)
    tok = model.tokenizer
    max_len = int(getattr(model, "max_seq_length", MAX_SEQ) or MAX_SEQ)
    news = df["News Text"].fillna("").astype(str)
    head = df["Headline"].fillna("").astype(str)
    comb = df["combined_text"].fillna("").astype(str) if "combined_text" in df.columns else (head + " " + news)

    char_stats = {
        "headline_chars": summarize(head.str.len()),
        "body_chars": summarize(news.str.len()),
        "combined_chars": summarize(comb.str.len()),
        "combined_words": summarize(comb.str.split().str.len()),
    }
    rng = np.random.RandomState(SEED)
    sample_idx = rng.choice(len(df), size=min(4000, len(df)), replace=False)
    print("Tokenizing length sample n=%s..." % len(sample_idx), flush=True)
    sample_tok = [token_len(tok, comb.iloc[int(i)]) for i in sample_idx]
    src_ids = sorted({r["source_doc_id"] for r in eval_rows})
    src_tok = [token_len(tok, comb.iloc[i]) for i in src_ids]
    trunc_sample = float(np.mean([t > max_len for t in sample_tok]))
    trunc_src = float(np.mean([t > max_len for t in src_tok]))

    print("Querying headline + full indexes at k=15...", flush=True)
    depth_rows = []
    t_head, t_full = [], []
    for i, r in enumerate(eval_rows, 1):
        q = r["query_text"]
        processed, romanized = transliterate_roman(q)
        src = r["source_doc_id"]
        t0 = time.perf_counter()
        h_hits = search_headlines(processed, top_k=15)
        t_head.append(time.perf_counter() - t0)
        t0 = time.perf_counter()
        f_hits = search_full_content(processed, top_k=15)
        t_full.append(time.perf_counter() - t0)
        hr, hs = rank_of(h_hits, src)
        fr, fs = rank_of(f_hits, src)
        depth_rows.append({
            "query_id": r["query_id"],
            "split": r["split"],
            "language_type": r["language_type"],
            "query_category": r["query_category"],
            "creation_method": r["creation_method"],
            "query_text": q,
            "processed_query": processed,
            "roman_dict_changed": int(romanized),
            "source_doc_id": src,
            "source_headline": str(head.iloc[src])[:160],
            "source_body_snippet": str(news.iloc[src])[:220],
            "source_combined_tokens": token_len(tok, comb.iloc[src]),
            "headline_rank15": hr if hr else 999,
            "full_rank15": fr if fr else 999,
            "headline_score_if_hit": hs,
            "full_score_if_hit": fs,
            "headline_top1": str(head.iloc[int(h_hits[0][0])])[:90] if h_hits else "",
            "full_top1": str(head.iloc[int(f_hits[0][0])])[:90] if f_hits else "",
            "headline_top5_ids": [int(d) for d, _ in h_hits[:5]],
            "full_top5_ids": [int(d) for d, _ in f_hits[:5]],
            "full_top15_ids": [int(d) for d, _ in f_hits[:15]],
            "full_top15_scores": [float(s) for _, s in f_hits[:15]],
            "headline_top5_titles": [str(head.iloc[int(d)])[:90] for d, _ in h_hits[:5]],
            "full_top5_titles": [str(head.iloc[int(d)])[:90] for d, _ in f_hits[:5]],
        })
        if i % 10 == 0 or i == len(eval_rows):
            print("  retrieved %s/%s" % (i, len(eval_rows)), flush=True)

    print("Source self-similarity and chunk max-sim...", flush=True)
    q_texts = [rec["processed_query"] for rec in depth_rows]
    h_texts = [str(head.iloc[rec["source_doc_id"]]) for rec in depth_rows]
    f_texts = [str(comb.iloc[rec["source_doc_id"]]) for rec in depth_rows]
    chunk_lists = [chunk_text(tok, comb.iloc[rec["source_doc_id"]]) for rec in depth_rows]
    q_emb = model.encode(q_texts, batch_size=32, convert_to_numpy=True, normalize_embeddings=True)
    h_emb = model.encode(h_texts, batch_size=32, convert_to_numpy=True, normalize_embeddings=True)
    f_emb = model.encode(f_texts, batch_size=16, convert_to_numpy=True, normalize_embeddings=True)
    flat_chunks, n_chunks_src = [], [len(x) for x in chunk_lists]
    for chs in chunk_lists:
        flat_chunks.extend(chs)
    c_emb = model.encode(flat_chunks, batch_size=32, convert_to_numpy=True, normalize_embeddings=True)
    best_chunk = np.zeros(len(eval_rows))
    ptr = 0
    for i, nch in enumerate(n_chunks_src):
        sl = c_emb[ptr : ptr + nch]
        best_chunk[i] = float((sl @ q_emb[i]).max()) if nch else 0.0
        ptr += nch
    cos_h = np.sum(q_emb * h_emb, axis=1)
    cos_f = np.sum(q_emb * f_emb, axis=1)

    print("Chunk re-rank of full-index top-15 (source not injected)...", flush=True)
    t_chunk, chunk_ranks, chunk_might_recover = [], [], []
    for i, rec in enumerate(depth_rows):
        t0 = time.perf_counter()
        cand = rec["full_top15_ids"][:]
        src = rec["source_doc_id"]
        texts, map_c = [], []
        for did in cand:
            for c in chunk_text(tok, comb.iloc[int(did)]):
                texts.append(c)
                map_c.append(int(did))
        emb = model.encode(texts, batch_size=32, convert_to_numpy=True, normalize_embeddings=True)
        best = {}
        for did, s in zip(map_c, emb @ q_emb[i]):
            best[did] = max(best.get(did, -1e9), float(s))
        ordered = sorted(best.items(), key=lambda x: -x[1])
        rank = next((j for j, (did, _s) in enumerate(ordered, 1) if did == src), None)
        t_chunk.append(time.perf_counter() - t0)
        chunk_ranks.append(rank if rank else 999)
        floor15 = min(rec["full_top15_scores"]) if rec["full_top15_scores"] else 0.0
        might = bool(src not in cand and float(best_chunk[i]) > floor15)
        chunk_might_recover.append(int(might))
        rec["chunk_rerank_rank"] = rank if rank else 999
        rec["source_in_full_top15"] = int(src in cand)
        rec["chunk_might_recover_if_indexed"] = int(might)
        rec["full_top15_floor_score"] = round(float(floor15), 4)
        rec["cos_query_source_headline"] = round(float(cos_h[i]), 4)
        rec["cos_query_source_full"] = round(float(cos_f[i]), 4)
        rec["cos_query_source_best_chunk"] = round(float(best_chunk[i]), 4)
        rec["source_n_chunks"] = n_chunks_src[i]
        if (i + 1) % 10 == 0 or (i + 1) == len(depth_rows):
            print("  reranked %s/%s" % (i + 1, len(depth_rows)), flush=True)

    print("Roman dict-off vs dict-on...", flush=True)
    roman_idx = [i for i, r in enumerate(eval_rows) if r["language_type"] == "roman_urdu"]
    roman_off_h, roman_off_f, roman_on_h, roman_on_f = [], [], [], []
    for i in roman_idx:
        q = eval_rows[i]["query_text"]
        src = eval_rows[i]["source_doc_id"]
        processed, _ = transliterate_roman(q)
        roman_on_h.append(rank_of(search_headlines(processed, top_k=15), src)[0] or 999)
        roman_on_f.append(rank_of(search_full_content(processed, top_k=15), src)[0] or 999)
        roman_off_h.append(rank_of(search_headlines(q, top_k=15), src)[0] or 999)
        roman_off_f.append(rank_of(search_full_content(q, top_k=15), src)[0] or 999)

    h_ranks = [r["headline_rank15"] for r in depth_rows]
    f_ranks = [r["full_rank15"] for r in depth_rows]
    urdu_mask = [r["language_type"] == "urdu" for r in depth_rows]
    urdu_h = [h for h, m in zip(h_ranks, urdu_mask) if m]
    urdu_f = [f for f, m in zip(f_ranks, urdu_mask) if m]
    urdu_c = [c for c, m in zip(chunk_ranks, urdu_mask) if m]
    lat_h = round(float(np.mean(t_head)), 4)
    lat_f = round(float(np.mean(t_full)), 4)
    lat_c = round(float(np.mean(t_chunk)), 4)
    old_h = [ndcg_at(r, 5) for r in h_ranks]
    old_f = [ndcg_at(r, 5) for r in f_ranks]
    new_f = [ndcg_at(r, 5) for r in chunk_ranks]
    old_or = [oracle_from_ndcg(a, b) for a, b in zip(old_h, old_f)]
    new_or = [oracle_from_ndcg(a, b) for a, b in zip(old_h, new_f)]
    ceiling_old = float(np.mean([max(a, b) for a, b in zip(old_h, old_f)]))
    ceiling_new = float(np.mean([max(a, b) for a, b in zip(old_h, new_f)]))
    roman = [rec for rec in depth_rows if rec["language_type"] == "roman_urdu"]
    roman_stats = {
        "n": len(roman),
        "dict_changed": int(sum(r["roman_dict_changed"] for r in roman)),
        "full_hit5_dict_on": int(sum(x <= 5 for x in roman_on_f)),
        "headline_hit5_dict_on": int(sum(x <= 5 for x in roman_on_h)),
        "full_hit5_dict_off": int(sum(x <= 5 for x in roman_off_f)),
        "headline_hit5_dict_off": int(sum(x <= 5 for x in roman_off_h)),
        "both_miss5": int(sum(r["full_rank15"] > 5 and r["headline_rank15"] > 5 for r in roman)),
        "mean_cos_full": round(float(np.mean([r["cos_query_source_full"] for r in roman])), 4) if roman else None,
        "mean_cos_headline": round(float(np.mean([r["cos_query_source_headline"] for r in roman])), 4) if roman else None,
        "mean_cos_best_chunk": round(float(np.mean([r["cos_query_source_best_chunk"] for r in roman])), 4) if roman else None,
        "note": "Not used to pick chunk size or to select a retrieval method.",
    }
    both_miss = [r for r in depth_rows if r["headline_rank15"] > 5 and r["full_rank15"] > 5]
    full_wins = [r for r in depth_rows if r["full_rank15"] <= 5 < r["headline_rank15"]]
    head_wins = [r for r in depth_rows if r["headline_rank15"] <= 5 < r["full_rank15"]]
    m_h5 = metrics_from_ranks(h_ranks, 5)
    m_f5 = metrics_from_ranks(f_ranks, 5)
    m_c5 = metrics_from_ranks(chunk_ranks, 5)
    urdu_full_ndcg = metrics_from_ranks(urdu_f, 5)["ndcg_at_k"]
    urdu_chunk_ndcg = metrics_from_ranks(urdu_c, 5)["ndcg_at_k"]
    chunk_helps = (m_c5["ndcg_at_k"] > m_f5["ndcg_at_k"] + 1e-6) and (urdu_chunk_ndcg >= urdu_full_ndcg - 1e-6)
    if chunk_helps:
        selected = "chunk96_overlap24_maxsim_rerank_top15"
        selected_ceiling = round(ceiling_new, 4)
        selection_reason = "Chunk re-rank improved nDCG@5 on n=78 and did not hurt Urdu-only nDCG@5."
    else:
        selected = "full_one_vector_chroma_111k"
        selected_ceiling = round(ceiling_old, 4)
        selection_reason = (
            "Chunk re-rank of Chroma top-15 did not improve known-item nDCG@5, or it hurt Urdu-only nDCG@5. "
            "Keep the simpler one-vector full index."
        )

    payload = {
        "experiment_id": "phase3-full-index-forensics-v1",
        "frozen_test_used": False,
        "svm_retrained": False,
        "eval_n": len(eval_rows),
        "eval_splits": sorted(EVAL_SPLITS),
        "model_name": MODEL_NAME,
        "max_seq_length": max_len,
        "embedding_dim": int(q_emb.shape[1]),
        "chunk_tokens": CHUNK_TOKENS,
        "chunk_overlap": CHUNK_OVERLAP,
        "chunk_size_justification": "Encoder max_seq_length is 128; 200-300 token chunks would still truncate. 96/24 fits the window.",
        "chunk_experiment_scope": "Max-sim over token chunks, re-ranking current full-index top-15 only. Source not injected. Not a 111k chunk ANN.",
        "n_chunk_might_recover_if_full_ann": int(sum(chunk_might_recover)),
        "corpus_length": char_stats,
        "token_length_sample_n4000": summarize(sample_tok),
        "token_length_eval_sources": summarize(src_tok),
        "pct_sample_exceeding_128": round(100 * trunc_sample, 2),
        "pct_eval_sources_exceeding_128": round(100 * trunc_src, 2),
        "self_similarity": {
            "mean_cos_headline": round(float(cos_h.mean()), 4),
            "mean_cos_full_truncated": round(float(cos_f.mean()), 4),
            "mean_cos_best_chunk": round(float(best_chunk.mean()), 4),
            "best_chunk_beats_full": round(float(np.mean(best_chunk > cos_f + 1e-6)), 4),
            "headline_beats_full": round(float(np.mean(cos_h > cos_f + 1e-6)), 4),
        },
        "baseline": {
            "headline": {("k%s" % k): metrics_from_ranks(h_ranks, k) for k in TOP_KS},
            "full": {("k%s" % k): metrics_from_ranks(f_ranks, k) for k in TOP_KS},
            "full_chunk_rerank_top15": {("k%s" % k): metrics_from_ranks(chunk_ranks, k) for k in TOP_KS},
            "urdu_only": {
                "n": int(sum(urdu_mask)),
                "headline_k5": metrics_from_ranks(urdu_h, 5),
                "full_k5": metrics_from_ranks(urdu_f, 5),
                "chunk_k5": metrics_from_ranks(urdu_c, 5),
            },
            "latency_sec": {"headline_mean": lat_h, "full_chroma_mean": lat_f, "chunk_rerank_mean": lat_c},
            "index_bytes": {
                "chroma_urdu_news": dir_size(os.path.join(ROOT, "data", "chromadb")),
                "embeddings_npy": dir_size(os.path.join(ROOT, "data", "embeddings.npy")),
                "headline_cache_npy": dir_size(os.path.join(ROOT, "data", "headline_embeddings_phase2_5_cache.npy")),
            },
        },
        "oracle_ceiling_eval78": {
            "old_mean_max_ndcg5": round(ceiling_old, 4),
            "chunk_rerank_mean_max_ndcg5": round(ceiling_new, 4),
            "delta": round(ceiling_new - ceiling_old, 4),
            "old_route_counts": {k: old_or.count(k) for k in ("HEADLINE", "FULL", "MIXED")},
            "new_route_counts": {k: new_or.count(k) for k in ("HEADLINE", "FULL", "MIXED")},
            "selected_mean_max_ndcg5": selected_ceiling,
        },
        "both_miss_top5": len(both_miss),
        "full_only_hit5": len(full_wins),
        "headline_only_hit5": len(head_wins),
        "roman": roman_stats,
        "selected_full_method": selected,
        "selection_reason": selection_reason,
    }
    with open(os.path.join(OUT, "phase3_statistics.json"), "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    fields = list(depth_rows[0].keys())
    with open(os.path.join(OUT, "eval_query_forensics.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for rec in depth_rows:
            row = dict(rec)
            for k in JSON_LIST_KEYS:
                if k in row:
                    row[k] = json.dumps(row[k], ensure_ascii=False)
            w.writerow(row)

    base_rows = []
    for name, ranks, lat in [
        ("headline_index", h_ranks, lat_h),
        ("full_index_current", f_ranks, lat_f),
        ("full_chunk_rerank_top15", chunk_ranks, lat_c),
    ]:
        for k in TOP_KS:
            m = metrics_from_ranks(ranks, k)
            base_rows.append([name, "dev+internal_val", k, m["source_hit_rate"], m["p_at_k"], m["ndcg_at_k"], m["mrr"], lat])
    for name, ranks in [("headline_index", urdu_h), ("full_index_current", urdu_f), ("full_chunk_rerank_top15", urdu_c)]:
        m = metrics_from_ranks(ranks, 5)
        base_rows.append([name, "urdu_only", 5, m["source_hit_rate"], m["p_at_k"], m["ndcg_at_k"], m["mrr"], ""])
    write_csv(os.path.join(OUT, "BASELINE_RESULTS.csv"), ["system", "subset", "k", "source_hit_rate", "P@k_known_item", "nDCG@k", "MRR", "mean_latency_sec"], base_rows)
    write_csv(
        os.path.join(OUT, "CHUNKING_COMPARISON.csv"),
        ["system", "hit@5", "nDCG@5", "hit@10", "hit@15", "mean_latency_sec", "index_scope"],
        [
            ["full_one_vector_chroma_111k", metrics_from_ranks(f_ranks, 5)["source_hit_rate"], metrics_from_ranks(f_ranks, 5)["ndcg_at_k"], metrics_from_ranks(f_ranks, 10)["source_hit_rate"], metrics_from_ranks(f_ranks, 15)["source_hit_rate"], lat_f, "full_corpus ANN"],
            ["chunk96_overlap24_maxsim_rerank_top15", metrics_from_ranks(chunk_ranks, 5)["source_hit_rate"], metrics_from_ranks(chunk_ranks, 5)["ndcg_at_k"], metrics_from_ranks(chunk_ranks, 10)["source_hit_rate"], metrics_from_ranks(chunk_ranks, 15)["source_hit_rate"], lat_c, "re-rank chroma top-15 only; source not injected"],
        ],
    )
    oc = payload["oracle_ceiling_eval78"]
    write_csv(
        os.path.join(OUT, "ORACLE_CEILING_COMPARISON.csv"),
        ["setting", "eval_n", "mean_oracle_nDCG@5", "HEADLINE", "FULL", "MIXED", "note"],
        [
            ["current_indexes", len(eval_rows), oc["old_mean_max_ndcg5"], oc["old_route_counts"]["HEADLINE"], oc["old_route_counts"]["FULL"], oc["old_route_counts"]["MIXED"], "headline cache vs chroma full"],
            ["full_replaced_by_chunk_rerank", len(eval_rows), oc["chunk_rerank_mean_max_ndcg5"], oc["new_route_counts"]["HEADLINE"], oc["new_route_counts"]["FULL"], oc["new_route_counts"]["MIXED"], "chunk cannot recover source outside chroma top-15"],
        ],
    )
    write_csv(
        os.path.join(OUT, "RETRIEVAL_EXPERIMENTS.csv"),
        ["experiment_id", "hypothesis", "change", "dataset", "metric", "baseline", "treatment", "delta", "used_for_selection", "result"],
        [
            ["E0_baseline", "Record current indexes before any change", "none", "dev+internal_val", "full_nDCG@5", m_f5["ndcg_at_k"], m_f5["ndcg_at_k"], 0.0, "yes_as_baseline", "recorded"],
            ["E0_baseline", "Record current indexes before any change", "none", "dev+internal_val", "headline_nDCG@5", m_h5["ndcg_at_k"], m_h5["ndcg_at_k"], 0.0, "yes_as_baseline", "recorded"],
            ["E1_truncation_selfsim", "Long articles lose query-relevant tail under 128-token encode", "cos(q, headline/full/best-chunk)", "eval sources", "mean_cos_best_chunk_minus_full", round(float(cos_f.mean()), 4), round(float(best_chunk.mean()), 4), round(float(best_chunk.mean() - cos_f.mean()), 4), "diagnostic", "see self_similarity"],
            ["E2_chunk_rerank", "Max-sim chunking of the same top-15 improves known-item ranking", "chunk 96 / overlap 24 / max sim", "dev+internal_val", "nDCG@5", m_f5["ndcg_at_k"], m_c5["ndcg_at_k"], round(m_c5["ndcg_at_k"] - m_f5["ndcg_at_k"], 4), "yes", selected],
            ["E2_chunk_rerank", "Max-sim chunking of the same top-15 improves known-item ranking", "chunk 96 / overlap 24 / max sim", "dev+internal_val", "source_hit@5", m_f5["source_hit_rate"], m_c5["source_hit_rate"], round(m_c5["source_hit_rate"] - m_f5["source_hit_rate"], 4), "yes", selected],
            ["E3_roman_dict", "Letter-map transliteration helps Roman queries against Urdu docs", "dict on vs raw Latin query", "eval roman_urdu only", "full_hit@5_count", roman_stats["full_hit5_dict_off"], roman_stats["full_hit5_dict_on"], roman_stats["full_hit5_dict_on"] - roman_stats["full_hit5_dict_off"], "no", "diagnosis only"],
        ],
    )

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        ks = [5, 10, 15]
        plt.figure(figsize=(7, 4))
        plt.plot(ks, [metrics_from_ranks(h_ranks, k)["source_hit_rate"] for k in ks], marker="o", label="Headline")
        plt.plot(ks, [metrics_from_ranks(f_ranks, k)["source_hit_rate"] for k in ks], marker="o", label="Full (current)")
        plt.plot(ks, [metrics_from_ranks(chunk_ranks, k)["source_hit_rate"] for k in ks], marker="o", label="Full chunk re-rank")
        plt.xlabel("k"); plt.ylabel("Source hit rate"); plt.title("Phase 3 eval (n=%s): known-item hit@k" % len(eval_rows))
        plt.legend(); plt.grid(True, alpha=0.3); plt.tight_layout()
        plt.savefig(os.path.join(FIG, "hit_at_k.png"), dpi=140); plt.close()
        plt.figure(figsize=(7, 4))
        plt.boxplot([cos_h, cos_f, best_chunk], labels=["q·headline", "q·full (trunc 128)", "q·best chunk"])
        plt.ylabel("cosine"); plt.title("Query vs source-article representation"); plt.tight_layout()
        plt.savefig(os.path.join(FIG, "self_similarity.png"), dpi=140); plt.close()
        plt.figure(figsize=(7, 4))
        plt.hist(sample_tok, bins=40, color="#4C78A8")
        plt.axvline(max_len, color="red", linestyle="--", label="max_seq_length=%s" % max_len)
        plt.xlabel("combined_text tokens (sample n=%s)" % len(sample_tok)); plt.ylabel("articles")
        plt.title("Are full articles truncated before embedding?"); plt.legend(); plt.tight_layout()
        plt.savefig(os.path.join(FIG, "truncation_hist.png"), dpi=140); plt.close()
        langs = sorted({r["language_type"] for r in depth_rows})
        h_by = [float(np.mean([x["headline_rank15"] <= 5 for x in depth_rows if x["language_type"] == lg])) for lg in langs]
        f_by = [float(np.mean([x["full_rank15"] <= 5 for x in depth_rows if x["language_type"] == lg])) for lg in langs]
        x = np.arange(len(langs))
        plt.figure(figsize=(7, 4))
        plt.bar(x - 0.18, h_by, 0.35, label="Headline hit@5")
        plt.bar(x + 0.18, f_by, 0.35, label="Full hit@5")
        plt.xticks(x, langs); plt.ylabel("source hit@5"); plt.title("Known-item hit@5 by query language")
        plt.legend(); plt.tight_layout()
        plt.savefig(os.path.join(FIG, "hit_by_language.png"), dpi=140); plt.close()
    except Exception as exc:
        print("figure generation skipped:", exc, flush=True)

    print(json.dumps({
        "eval_n": len(eval_rows),
        "pct_over_128_sample": payload["pct_sample_exceeding_128"],
        "full_hit5": m_f5["source_hit_rate"],
        "headline_hit5": m_h5["source_hit_rate"],
        "chunk_hit5": m_c5["source_hit_rate"],
        "self_sim": payload["self_similarity"],
        "ceiling": payload["oracle_ceiling_eval78"],
        "roman": roman_stats,
        "selected": selected,
    }, indent=2), flush=True)


if __name__ == "__main__":
    main()
