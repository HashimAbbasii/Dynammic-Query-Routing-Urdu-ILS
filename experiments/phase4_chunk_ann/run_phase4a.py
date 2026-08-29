# -*- coding: utf-8 -*-
"""
Phase 4A: corpus-level chunk ANN (not Phase 3 top-15 re-rank).

Eval = Phase 2 dev + internal_val only. Frozen H001-H040 unused. SVM untouched.

Chunking is pre-registered from the encoder limit, not from eval scores:
  suggested 192/32 is invalid because max_seq_length=128 (silent truncation).
  primary = 96 content tokens, overlap 32, stride 64.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sys
import time
from collections import Counter

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

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
ART = os.path.join(OUT, "artifacts")
FIG = os.path.join(OUT, "figures")
CHROMA_DIR = os.path.join(ART, "chroma_chunks")
COLLECTION = "urdu_news_chunks_p4a"

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
MAX_SEQ = 128
CHUNK_SIZE = 96
CHUNK_OVERLAP = 32
STRIDE = CHUNK_SIZE - CHUNK_OVERLAP
N_CANDIDATES = 80
EMBED_BATCH = 64
CHROMA_ADD = 2000
MIXED_DELTA = 0.05
PHASE3_FULL_HIT5 = 0.2564
PHASE3_FULL_NDCG5 = 0.2203
HIT_TOL = 0.03
NDCG_TOL = 0.02


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
        "p75": float(np.percentile(a, 75)),
        "p90": float(np.percentile(a, 90)),
        "p95": float(np.percentile(a, 95)),
        "p99": float(np.percentile(a, 99)),
    }


def n_chunks_for(n_tok):
    if n_tok <= CHUNK_SIZE:
        return 1
    return 1 + int(math.ceil((n_tok - CHUNK_SIZE) / float(STRIDE)))


def chunk_spans(n_tok):
    if n_tok <= 0:
        return [(0, 0)]
    if n_tok <= CHUNK_SIZE:
        return [(0, n_tok)]
    spans = []
    start = 0
    while True:
        end = min(n_tok, start + CHUNK_SIZE)
        spans.append((start, end))
        if end >= n_tok:
            break
        start += STRIDE
    return spans


def token_len(tok, text):
    return len(tok.encode(str(text or ""), add_special_tokens=False, truncation=False))


def chunk_texts(tok, text):
    ids = tok.encode(str(text or ""), add_special_tokens=False, truncation=False)
    spans = chunk_spans(len(ids))
    texts = []
    for a, b in spans:
        texts.append(tok.decode(ids[a:b], skip_special_tokens=True) if b > a else "")
    return texts, spans


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


def load_corpus():
    df = pd.read_csv(CORPUS, encoding="utf-8-sig")
    news = df["News Text"].fillna("").astype(str)
    head = df["Headline"].fillna("").astype(str)
    comb = df["combined_text"].fillna("").astype(str) if "combined_text" in df.columns else (head + " " + news)
    return df, head, news, comb


def rank_of(hits, src):
    for rank, (did, score) in enumerate(hits, 1):
        if int(did) == int(src):
            return rank, float(score)
    return None, None


def dir_size(path):
    if os.path.isfile(path):
        return os.path.getsize(path)
    tot = 0
    if not os.path.isdir(path):
        return 0
    for d, _ds, fs in os.walk(path):
        for fn in fs:
            tot += os.path.getsize(os.path.join(d, fn))
    return tot


def stage_baseline():
    eval_rows = load_eval_rows()
    print("Baseline eval n=%s" % len(eval_rows), flush=True)
    h_ranks, f_ranks = [], []
    t_h, t_f = [], []
    recs = []
    for i, r in enumerate(eval_rows, 1):
        q, _ = transliterate_roman(r["query_text"])
        src = r["source_doc_id"]
        t0 = time.perf_counter()
        hh = search_headlines(q, top_k=15)
        t_h.append(time.perf_counter() - t0)
        t0 = time.perf_counter()
        fh = search_full_content(q, top_k=15)
        t_f.append(time.perf_counter() - t0)
        hr, _ = rank_of(hh, src)
        fr, _ = rank_of(fh, src)
        h_ranks.append(hr if hr else 999)
        f_ranks.append(fr if fr else 999)
        recs.append({
            "query_id": r["query_id"],
            "split": r["split"],
            "language_type": r["language_type"],
            "source_doc_id": src,
            "headline_rank15": h_ranks[-1],
            "full_rank15": f_ranks[-1],
        })
        if i % 20 == 0 or i == len(eval_rows):
            print("  baseline %s/%s" % (i, len(eval_rows)), flush=True)
    m_h = metrics_from_ranks(h_ranks, 5)
    m_f = metrics_from_ranks(f_ranks, 5)
    payload = {
        "eval_n": len(eval_rows),
        "eval_splits": sorted(EVAL_SPLITS),
        "headline_k5": m_h,
        "full_k5": m_f,
        "full_k10": metrics_from_ranks(f_ranks, 10),
        "full_k15": metrics_from_ranks(f_ranks, 15),
        "headline_mean_latency_sec": round(float(np.mean(t_h)), 4),
        "full_mean_latency_sec": round(float(np.mean(t_f)), 4),
        "full_chroma_bytes": dir_size(os.path.join(ROOT, "data", "chromadb")),
        "phase3_full_hit5": PHASE3_FULL_HIT5,
        "phase3_full_ndcg5": PHASE3_FULL_NDCG5,
        "delta_hit5": round(m_f["source_hit_rate"] - PHASE3_FULL_HIT5, 4),
        "delta_ndcg5": round(m_f["ndcg_at_k"] - PHASE3_FULL_NDCG5, 4),
    }
    payload["reproduction_ok"] = (
        abs(payload["delta_hit5"]) <= HIT_TOL and abs(payload["delta_ndcg5"]) <= NDCG_TOL
    )
    os.makedirs(ART, exist_ok=True)
    with open(os.path.join(OUT, "baseline_reproduction.json"), "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    write_csv(
        os.path.join(OUT, "baseline_reproduction.csv"),
        ["system", "k", "source_hit_rate", "P@k_known_item", "nDCG@k", "MRR", "mean_latency_sec", "index_bytes"],
        [
            ["headline_index", 5, m_h["source_hit_rate"], m_h["p_at_k"], m_h["ndcg_at_k"], m_h["mrr"], payload["headline_mean_latency_sec"], dir_size(os.path.join(ROOT, "data", "headline_embeddings_phase2_5_cache.npy"))],
            ["full_index_current", 5, m_f["source_hit_rate"], m_f["p_at_k"], m_f["ndcg_at_k"], m_f["mrr"], payload["full_mean_latency_sec"], payload["full_chroma_bytes"]],
            ["full_index_current", 10, payload["full_k10"]["source_hit_rate"], payload["full_k10"]["p_at_k"], payload["full_k10"]["ndcg_at_k"], payload["full_k10"]["mrr"], payload["full_mean_latency_sec"], payload["full_chroma_bytes"]],
            ["full_index_current", 15, payload["full_k15"]["source_hit_rate"], payload["full_k15"]["p_at_k"], payload["full_k15"]["ndcg_at_k"], payload["full_k15"]["mrr"], payload["full_mean_latency_sec"], payload["full_chroma_bytes"]],
        ],
    )
    with open(os.path.join(ART, "baseline_ranks.json"), "w", encoding="utf-8") as f:
        json.dump(recs, f)
    with open(os.path.join(ART, "eval_rows.json"), "w", encoding="utf-8") as f:
        json.dump(eval_rows, f, ensure_ascii=False)
    print(json.dumps(payload, indent=2), flush=True)
    if not payload["reproduction_ok"]:
        raise SystemExit("Baseline did not match Phase 3. Stop before chunk ANN.")
    return payload, recs, eval_rows


def stage_stats():
    from sentence_transformers import SentenceTransformer

    print("Tokenizer pass over full corpus...", flush=True)
    model = SentenceTransformer(MODEL_NAME)
    tok = model.tokenizer
    _df, _h, _n, comb = load_corpus()
    n = len(comb)
    stats_path = os.path.join(OUT, "corpus_token_lengths.npy")
    if os.path.isfile(stats_path):
        lengths = np.load(stats_path)
        if lengths.shape[0] != n:
            lengths = None
        else:
            print("Loaded cached token lengths n=%s" % n, flush=True)
    else:
        lengths = None
    if lengths is None:
        lengths = np.zeros(n, dtype=np.int32)
        t0 = time.perf_counter()
        for i in range(n):
            lengths[i] = token_len(tok, comb.iloc[i])
            if (i + 1) % 10000 == 0 or (i + 1) == n:
                print("  tokenized %s/%s (%.1f min)" % (i + 1, n, (time.perf_counter() - t0) / 60.0), flush=True)
        np.save(stats_path, lengths)
    nch = np.array([n_chunks_for(int(x)) for x in lengths], dtype=np.int32)
    total_chunks = int(nch.sum())
    raw_bytes = total_chunks * 384 * 4
    md = {
        "n_articles": n,
        "model_name": MODEL_NAME,
        "max_seq_length": int(getattr(model, "max_seq_length", MAX_SEQ) or MAX_SEQ),
        "user_suggested_chunk_tokens": 192,
        "user_suggested_overlap": 32,
        "primary_chunk_tokens": CHUNK_SIZE,
        "primary_overlap": CHUNK_OVERLAP,
        "stride": STRIDE,
        "justification": (
            "Encoder max_seq_length is 128 including special tokens. "
            "A 192-token chunk would be silently truncated to 128, so 192/32 does not test "
            "chunking vs one truncated vector. Content window 96 + CLS/SEP fits in 128. "
            "Overlap 32 is taken from the protocol. Set from the tokenizer limit before indexing; "
            "not tuned on H001-H040 or on eval nDCG."
        ),
        "token_length_combined": summarize(lengths),
        "pct_articles_exceeding_128": round(100.0 * float(np.mean(lengths > 128)), 2),
        "pct_articles_exceeding_96": round(100.0 * float(np.mean(lengths > 96)), 2),
        "chunks_per_article": summarize(nch),
        "total_chunks_estimate": total_chunks,
        "embedding_dim": 384,
        "raw_embedding_bytes_estimate": raw_bytes,
        "raw_embedding_gb_estimate": round(raw_bytes / 1e9, 3),
        "n_chunk_candidates_preregistered": N_CANDIDATES,
        "aggregation": "max_chunk_similarity",
    }
    with open(os.path.join(OUT, "corpus_chunk_stats.json"), "w", encoding="utf-8") as f:
        json.dump(md, f, indent=2)
    s = md["token_length_combined"]
    c = md["chunks_per_article"]
    lines = [
        "# Corpus chunk statistics",
        "",
        "Full cleaned corpus, **before** building the chunk index.",
        "Tokenizer = `%s`. Lengths are content tokens (`add_special_tokens=False`)." % MODEL_NAME,
        "",
        "## Why not 192 / 32?",
        "",
        md["justification"],
        "",
        "## Token length of combined_text (n=%s)" % n,
        "",
        "| stat | tokens |",
        "| --- | ---: |",
    ]
    for k in ("min", "max", "mean", "median", "p75", "p90", "p95", "p99"):
        lines.append("| %s | %.1f |" % (k, s[k]))
    lines += [
        "",
        "- Share of articles > 128 tokens: **%s%%**" % md["pct_articles_exceeding_128"],
        "- Share of articles > 96 tokens: **%s%%**" % md["pct_articles_exceeding_96"],
        "",
        "## Pre-registered plan (96 / 32, stride 64)",
        "",
        "| quantity | value |",
        "| --- | ---: |",
        "| total chunks | %s |" % total_chunks,
        "| mean chunks / article | %.3f |" % c["mean"],
        "| median chunks / article | %.1f |" % c["median"],
        "| p95 chunks / article | %.1f |" % c["p95"],
        "| max chunks / article | %.0f |" % c["max"],
        "| dim | 384 |",
        "| raw embedding store | ~%.2f GB |" % md["raw_embedding_gb_estimate"],
        "",
        "H001–H040 were not used.",
        "",
    ]
    with open(os.path.join(OUT, "CORPUS_CHUNK_STATISTICS.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("total_chunks=%s pct>128=%s gb=%.2f" % (total_chunks, md["pct_articles_exceeding_128"], md["raw_embedding_gb_estimate"]), flush=True)
    return md, lengths, model, tok


def stage_index(lengths, model, tok):
    import chromadb

    os.makedirs(CHROMA_DIR, exist_ok=True)
    _df, _h, _n, comb = load_corpus()
    n = len(comb)
    nch = np.array([n_chunks_for(int(x)) for x in lengths], dtype=np.int32)
    total = int(nch.sum())
    emb_path = os.path.join(ART, "chunk_embeddings.f32")
    aid_path = os.path.join(ART, "chunk_article_ids.npy")
    start_path = os.path.join(ART, "chunk_starts.npy")
    end_path = os.path.join(ART, "chunk_ends.npy")
    prog_path = os.path.join(ART, "index_progress.json")

    emb_mm = np.memmap(emb_path, dtype=np.float32, mode="w+" if not os.path.isfile(emb_path) else "r+", shape=(total, 384))
    if os.path.isfile(aid_path) and np.load(aid_path).shape[0] == total:
        aids = np.load(aid_path)
        starts = np.load(start_path)
        ends = np.load(end_path)
    else:
        aids = np.zeros(total, dtype=np.int32)
        starts = np.zeros(total, dtype=np.int32)
        ends = np.zeros(total, dtype=np.int32)

    start_article = 0
    written = 0
    if os.path.isfile(prog_path):
        prog = json.load(open(prog_path, encoding="utf-8"))
        start_article = int(prog.get("next_article", 0))
        written = int(prog.get("next_chunk", 0))
        print("Resuming at article %s chunk %s" % (start_article, written), flush=True)

    client = chromadb.PersistentClient(path=CHROMA_DIR)
    col = client.get_or_create_collection(name=COLLECTION, metadata={"hnsw:space": "cosine"})
    already = col.count()
    print("Chroma count=%s expected=%s" % (already, total), flush=True)

    buf_ids, buf_emb, buf_meta = [], [], []

    def flush():
        if not buf_ids:
            return
        col.add(ids=buf_ids, embeddings=buf_emb, metadatas=buf_meta)
        buf_ids.clear()
        buf_emb.clear()
        buf_meta.clear()

    skip_chroma_until = already
    t0 = time.perf_counter()
    pending_txt, pending_loc = [], []

    def encode_pending():
        nonlocal written
        if not pending_txt:
            return
        embs = np.asarray(
            model.encode(pending_txt, batch_size=EMBED_BATCH, convert_to_numpy=True, show_progress_bar=False),
            dtype=np.float32,
        )
        k = embs.shape[0]
        emb_mm[written : written + k] = embs
        for j, (art_i, cix, a, b) in enumerate(pending_loc):
            cid = written + j
            aids[cid] = art_i
            starts[cid] = a
            ends[cid] = b
            if cid >= skip_chroma_until:
                buf_ids.append("%s_%s" % (art_i, cix))
                buf_emb.append(embs[j].tolist())
                buf_meta.append({"article_id": int(art_i), "chunk_ix": int(cix), "start": int(a), "end": int(b)})
        written += k
        pending_txt.clear()
        pending_loc.clear()
        if len(buf_ids) >= CHROMA_ADD:
            flush()

    for i in range(start_article, n):
        texts, spans = chunk_texts(tok, comb.iloc[i])
        for j, ((a, b), tx) in enumerate(zip(spans, texts)):
            pending_txt.append(tx)
            pending_loc.append((i, j, a, b))
            if len(pending_txt) >= EMBED_BATCH:
                encode_pending()
        if (i + 1) % 500 == 0 or (i + 1) == n:
            encode_pending()
            flush()
            np.save(aid_path, aids)
            np.save(start_path, starts)
            np.save(end_path, ends)
            emb_mm.flush()
            with open(prog_path, "w", encoding="utf-8") as f:
                json.dump({"next_article": i + 1, "next_chunk": written}, f)
            print("  articles %s/%s chunks=%s chroma=%s (%.1f min)" % (
                i + 1, n, written, col.count(), (time.perf_counter() - t0) / 60.0
            ), flush=True)
    encode_pending()
    flush()
    np.save(aid_path, aids)
    np.save(start_path, starts)
    np.save(end_path, ends)
    emb_mm.flush()
    info = {
        "n_articles": n,
        "n_chunks": int(written),
        "chroma_count": col.count(),
        "chunk_tokens": CHUNK_SIZE,
        "overlap": CHUNK_OVERLAP,
        "ann": "chromadb HNSW",
        "space": "cosine",
        "hnsw_params": "Chroma default HNSW, hnsw:space=cosine; M/ef not overridden",
        "embedding_dim": 384,
        "build_sec": round(time.perf_counter() - t0, 1),
        "chroma_bytes": dir_size(CHROMA_DIR),
        "embedding_memmap_bytes": os.path.getsize(emb_path) if os.path.isfile(emb_path) else 0,
        "metadata_bytes": dir_size(aid_path) + dir_size(start_path) + dir_size(end_path),
    }
    with open(os.path.join(OUT, "index_build.json"), "w", encoding="utf-8") as f:
        json.dump(info, f, indent=2)
    print(json.dumps(info, indent=2), flush=True)
    return info


def search_chunk_ann(col, qemb, n=N_CANDIDATES):
    t0 = time.perf_counter()
    res = col.query(query_embeddings=[qemb], n_results=n, include=["metadatas", "distances"])
    t_ann = time.perf_counter() - t0
    t1 = time.perf_counter()
    best = {}
    chunk_hits = []
    for cid, dist, meta in zip(res["ids"][0], res["distances"][0], res["metadatas"][0]):
        sim = 1.0 - float(dist)
        aid = int(meta["article_id"])
        cix = int(meta["chunk_ix"])
        chunk_hits.append((aid, cix, sim, cid))
        prev = best.get(aid)
        if prev is None or sim > prev[0]:
            best[aid] = (sim, cix, cid)
    ranked = sorted(best.items(), key=lambda x: -x[1][0])
    t_agg = time.perf_counter() - t1
    articles = [(aid, float(sc[0])) for aid, sc in ranked]
    return articles, chunk_hits, t_ann, t_agg


def stage_eval(baseline_recs, eval_rows):
    import chromadb
    from sentence_transformers import SentenceTransformer

    client = chromadb.PersistentClient(path=CHROMA_DIR)
    col = client.get_collection(COLLECTION)
    model = SentenceTransformer(MODEL_NAME)
    full_rank = {r["query_id"]: int(r["full_rank15"]) for r in baseline_recs}
    head_rank = {r["query_id"]: int(r["headline_rank15"]) for r in baseline_recs}

    c_ranks, recs = [], []
    t_emb, t_ann, t_agg, t_tot = [], [], [], []
    n_dom, n_uniq = [], []
    for i, r in enumerate(eval_rows, 1):
        qraw = r["query_text"]
        q, _ = transliterate_roman(qraw)
        src = r["source_doc_id"]
        t0 = time.perf_counter()
        qemb = model.encode(q).tolist()
        te = time.perf_counter() - t0
        articles, chunks, ta, tg = search_chunk_ann(col, qemb, n=N_CANDIDATES)
        tot = time.perf_counter() - t0
        t_emb.append(te); t_ann.append(ta); t_agg.append(tg); t_tot.append(tot)
        cr, cs = rank_of(articles[:15], src)
        c_ranks.append(cr if cr else 999)
        top20 = chunks[:20]
        ctr = Counter(a for a, _i, _s, _c in top20)
        n_uniq.append(len(ctr))
        n_dom.append(max(ctr.values()) if ctr else 0)
        src_chunk_rank = next((rk for rk, (aid, _i, _s, _c) in enumerate(chunks, 1) if aid == src), 999)
        recs.append({
            "query_id": r["query_id"],
            "split": r["split"],
            "language_type": r["language_type"],
            "query_category": r.get("query_category", ""),
            "source_doc_id": src,
            "headline_rank15": head_rank[r["query_id"]],
            "full_rank15": full_rank[r["query_id"]],
            "chunkann_rank15": c_ranks[-1],
            "chunkann_score_if_hit": cs,
            "source_chunk_rank_in_N": src_chunk_rank,
            "n_unique_articles_in_top20_chunks": n_uniq[-1],
            "max_chunks_one_article_top20": n_dom[-1],
            "query_text": qraw[:160],
        })
        if i % 10 == 0 or i == len(eval_rows):
            print("  eval %s/%s" % (i, len(eval_rows)), flush=True)

    m_c5 = metrics_from_ranks(c_ranks, 5)
    f_ranks = [full_rank[r["query_id"]] for r in eval_rows]
    h_ranks = [head_rank[r["query_id"]] for r in eval_rows]
    m_f5 = metrics_from_ranks(f_ranks, 5)
    m_h5 = metrics_from_ranks(h_ranks, 5)
    full_miss = [r for r, fr in zip(recs, f_ranks) if fr > 5]
    recovered = [r for r in full_miss if r["chunkann_rank15"] <= 5]
    full_hit_chunk_miss = [r for r, fr in zip(recs, f_ranks) if fr <= 5 and r["chunkann_rank15"] > 5]
    old_h = [ndcg_at(r, 5) for r in h_ranks]
    old_f = [ndcg_at(r, 5) for r in f_ranks]
    new_f = [ndcg_at(r, 5) for r in c_ranks]
    old_or = [oracle_from_ndcg(a, b) for a, b in zip(old_h, old_f)]
    new_or = [oracle_from_ndcg(a, b) for a, b in zip(old_h, new_f)]
    ceil_old = float(np.mean([max(a, b) for a, b in zip(old_h, old_f)]))
    ceil_new = float(np.mean([max(a, b) for a, b in zip(old_h, new_f)]))
    urdu_mask = [r["language_type"] == "urdu" for r in eval_rows]
    urdu_c = [c for c, m in zip(c_ranks, urdu_mask) if m]
    urdu_f = [f for f, m in zip(f_ranks, urdu_mask) if m]
    urdu_h = [h for h, m in zip(h_ranks, urdu_mask) if m]
    chunk_helps = (m_c5["ndcg_at_k"] > m_f5["ndcg_at_k"] + 1e-6) and (
        metrics_from_ranks(urdu_c, 5)["ndcg_at_k"] >= metrics_from_ranks(urdu_f, 5)["ndcg_at_k"] - 1e-6
    )
    selected = "chunk96_ov32_max_chroma_corpus" if chunk_helps else "full_one_vector_chroma_111k"
    payload = {
        "experiment_id": "phase4a-corpus-chunk-ann-v1",
        "frozen_test_used": False,
        "svm_retrained": False,
        "eval_n": len(eval_rows),
        "chunk_tokens": CHUNK_SIZE,
        "overlap": CHUNK_OVERLAP,
        "n_chunk_candidates": N_CANDIDATES,
        "aggregation": "max",
        "headline_k5": m_h5,
        "full_k5": m_f5,
        "chunkann_k5": m_c5,
        "chunkann_k10": metrics_from_ranks(c_ranks, 10),
        "chunkann_k15": metrics_from_ranks(c_ranks, 15),
        "urdu_only": {
            "n": int(sum(urdu_mask)),
            "headline_k5": metrics_from_ranks(urdu_h, 5),
            "full_k5": metrics_from_ranks(urdu_f, 5),
            "chunkann_k5": metrics_from_ranks(urdu_c, 5),
        },
        "latency_sec": {
            "embed_mean": round(float(np.mean(t_emb)), 4),
            "ann_mean": round(float(np.mean(t_ann)), 4),
            "agg_mean": round(float(np.mean(t_agg)), 4),
            "total_mean": round(float(np.mean(t_tot)), 4),
        },
        "recovery": {
            "full_miss_top5": len(full_miss),
            "chunkann_recovers_among_full_miss": len(recovered),
            "full_hit_chunkann_miss": len(full_hit_chunk_miss),
        },
        "dominance_top20_chunks": {
            "mean_unique_articles": round(float(np.mean(n_uniq)), 3),
            "mean_max_chunks_from_one_article": round(float(np.mean(n_dom)), 3),
        },
        "oracle_ceiling_eval78": {
            "current_mean_max_ndcg5": round(ceil_old, 4),
            "chunkann_as_full_mean_max_ndcg5": round(ceil_new, 4),
            "headline_full_chunk_mean_max_ndcg5": round(float(np.mean([max(a, b, c) for a, b, c in zip(old_h, old_f, new_f)])), 4),
            "delta": round(ceil_new - ceil_old, 4),
            "old_route_counts": {k: old_or.count(k) for k in ("HEADLINE", "FULL", "MIXED")},
            "new_route_counts": {k: new_or.count(k) for k in ("HEADLINE", "FULL", "MIXED")},
        },
        "selected_full_method": selected,
        "selection_rule": "Adopt chunk ANN only if nDCG@5 improves on n=78 and Urdu-only nDCG@5 does not fall.",
    }
    with open(os.path.join(OUT, "phase4a_statistics.json"), "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    with open(os.path.join(OUT, "eval_query_comparison.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(recs[0].keys()))
        w.writeheader()
        w.writerows(recs)
    lat_c = payload["latency_sec"]["total_mean"]
    write_csv(
        os.path.join(OUT, "CHUNK_ANN_COMPARISON.csv"),
        ["system", "hit@5", "nDCG@5", "P@5_known_item", "MRR", "hit@10", "hit@15", "mean_latency_sec"],
        [
            ["headline_index", m_h5["source_hit_rate"], m_h5["ndcg_at_k"], m_h5["p_at_k"], m_h5["mrr"], metrics_from_ranks(h_ranks, 10)["source_hit_rate"], metrics_from_ranks(h_ranks, 15)["source_hit_rate"], ""],
            ["full_one_vector_chroma", m_f5["source_hit_rate"], m_f5["ndcg_at_k"], m_f5["p_at_k"], m_f5["mrr"], metrics_from_ranks(f_ranks, 10)["source_hit_rate"], metrics_from_ranks(f_ranks, 15)["source_hit_rate"], ""],
            ["chunk_ann_96_32_max", m_c5["source_hit_rate"], m_c5["ndcg_at_k"], m_c5["p_at_k"], m_c5["mrr"], payload["chunkann_k10"]["source_hit_rate"], payload["chunkann_k15"]["source_hit_rate"], lat_c],
        ],
    )
    oc = payload["oracle_ceiling_eval78"]
    write_csv(
        os.path.join(OUT, "ORACLE_CEILING_COMPARISON.csv"),
        ["setting", "eval_n", "mean_oracle_nDCG@5", "HEADLINE", "FULL", "MIXED", "note"],
        [
            ["current_indexes", 78, oc["current_mean_max_ndcg5"], oc["old_route_counts"]["HEADLINE"], oc["old_route_counts"]["FULL"], oc["old_route_counts"]["MIXED"], "headline vs one-vector full"],
            ["full_replaced_by_chunk_ann", 78, oc["chunkann_as_full_mean_max_ndcg5"], oc["new_route_counts"]["HEADLINE"], oc["new_route_counts"]["FULL"], oc["new_route_counts"]["MIXED"], "headline vs corpus chunk ANN"],
            ["headline_full_and_chunk_ann", 78, oc["headline_full_chunk_mean_max_ndcg5"], "", "", "", "max nDCG@5 of three rooms"],
        ],
    )
    write_csv(
        os.path.join(OUT, "RECOVERY_ANALYSIS.csv"),
        ["metric", "value"],
        [
            ["full_miss_top5", len(full_miss)],
            ["chunk_ann_finds_source_among_those", len(recovered)],
            ["full_hit_but_chunk_ann_miss", len(full_hit_chunk_miss)],
        ],
    )
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        os.makedirs(FIG, exist_ok=True)
        ks = [5, 10, 15]
        plt.figure(figsize=(7, 4))
        plt.plot(ks, [metrics_from_ranks(h_ranks, k)["source_hit_rate"] for k in ks], marker="o", label="Headline")
        plt.plot(ks, [metrics_from_ranks(f_ranks, k)["source_hit_rate"] for k in ks], marker="o", label="Full one-vector")
        plt.plot(ks, [metrics_from_ranks(c_ranks, k)["source_hit_rate"] for k in ks], marker="o", label="Chunk ANN")
        plt.xlabel("k"); plt.ylabel("Source hit rate")
        plt.title("Phase 4A eval (n=%s): known-item hit@k" % len(eval_rows))
        plt.legend(); plt.grid(True, alpha=0.3); plt.tight_layout()
        plt.savefig(os.path.join(FIG, "hit_at_k.png"), dpi=140); plt.close()
    except Exception as exc:
        print("figure skipped:", exc, flush=True)
    print(json.dumps({
        "full_hit5": m_f5["source_hit_rate"],
        "chunk_hit5": m_c5["source_hit_rate"],
        "full_ndcg5": m_f5["ndcg_at_k"],
        "chunk_ndcg5": m_c5["ndcg_at_k"],
        "recovery": payload["recovery"],
        "latency": payload["latency_sec"],
        "selected": selected,
        "ceiling": payload["oracle_ceiling_eval78"],
    }, indent=2), flush=True)
    return payload


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--stage", default="all", choices=["baseline", "stats", "index", "eval", "all"])
    args = p.parse_args()
    os.makedirs(ART, exist_ok=True)
    os.makedirs(FIG, exist_ok=True)
    np.random.seed(SEED)
    recs = eval_rows = None
    lengths = model = tok = None
    if args.stage in ("baseline", "all"):
        print("=== STAGE baseline ===", flush=True)
        _base, recs, eval_rows = stage_baseline()
    else:
        recs = json.load(open(os.path.join(ART, "baseline_ranks.json"), encoding="utf-8"))
        eval_rows = json.load(open(os.path.join(ART, "eval_rows.json"), encoding="utf-8"))
        base = json.load(open(os.path.join(OUT, "baseline_reproduction.json"), encoding="utf-8"))
        if not base.get("reproduction_ok"):
            raise SystemExit("Stored baseline reproduction failed. Stop.")
    if args.stage in ("stats", "all"):
        print("=== STAGE stats ===", flush=True)
        _md, lengths, model, tok = stage_stats()
    elif args.stage in ("index",):
        lengths = np.load(os.path.join(OUT, "corpus_token_lengths.npy"))
    if args.stage in ("index", "all"):
        print("=== STAGE index ===", flush=True)
        if lengths is None:
            lengths = np.load(os.path.join(OUT, "corpus_token_lengths.npy"))
        if model is None:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer(MODEL_NAME)
            tok = model.tokenizer
        stage_index(lengths, model, tok)
    if args.stage in ("eval", "all"):
        print("=== STAGE eval ===", flush=True)
        if recs is None:
            recs = json.load(open(os.path.join(ART, "baseline_ranks.json"), encoding="utf-8"))
            eval_rows = json.load(open(os.path.join(ART, "eval_rows.json"), encoding="utf-8"))
        stage_eval(recs, eval_rows)


if __name__ == "__main__":
    main()
