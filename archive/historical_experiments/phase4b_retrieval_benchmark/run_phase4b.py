# -*- coding: utf-8 -*-
"""
Phase 4B: retrieval-room benchmark.
Eval = Phase 2 dev + internal_val (n=78). H001-H040 unused. SVM untouched.
No RRF, reranker, or fusion system.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import sys
import time
from collections import defaultdict

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

import numpy as np
import pandas as pd

_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(_DIR, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "validate", "dual_index_routing"))
sys.path.insert(0, os.path.join(ROOT, "experiments", "phase4_chunk_ann"))
from retrieve import search_full_content, search_headlines, transliterate_roman  # noqa: E402
import run_phase4a as p4a  # noqa: E402

SEED = 42
EVAL_SPLITS = {"dev", "internal_val"}
ORACLE_CSV = os.path.join(ROOT, "experiments", "phase2_oracle", "oracle_all.csv")
CORPUS = os.path.join(ROOT, "data", "clean_articles.csv")
OUT = _DIR
ART = os.path.join(OUT, "artifacts")
FIG = os.path.join(OUT, "figures")

REC_HIT = {"headline": 0.4487, "full": 0.2564, "chunk": 0.2821}
REC_NDCG = {"headline": 0.4009, "full": 0.2203, "chunk": 0.2362}
HIT_TOL, NDCG_TOL = 0.03, 0.02
BM25_K1, BM25_B = 1.5, 0.75
TOKEN_RE = re.compile(r"[\u0600-\u06FF]+|[A-Za-z0-9]+", re.UNICODE)
LONG_MODEL = "intfloat/multilingual-e5-small"
LONG_MAX_SEQ = 512
PROTO_N = 400
MAX_EMBED_HOURS = 4.0
MIXED_DELTA = 0.05


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


def tokenize(text):
    return TOKEN_RE.findall((text or "").lower())


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


def by_lang(rows, ranks):
    out = {}
    for lang in ("urdu", "roman_urdu", "mixed"):
        rs = [rk for r, rk in zip(rows, ranks) if r.get("language_type") == lang]
        if rs:
            m = metrics_from_ranks(rs, 5)
            out[lang] = m
    return out


def hardware():
    info = {"cuda": False, "gpu": "cpu", "cpu_count": os.cpu_count()}
    try:
        import torch
        info["cuda"] = bool(torch.cuda.is_available())
        info["gpu"] = torch.cuda.get_device_name(0) if info["cuda"] else "cpu"
        info["torch"] = torch.__version__
    except Exception as exc:
        info["torch_error"] = str(exc)
    os.makedirs(ART, exist_ok=True)
    with open(os.path.join(ART, "hardware.json"), "w", encoding="utf-8") as f:
        json.dump(info, f, indent=2)
    return info


def load_corpus_texts():
    df = pd.read_csv(CORPUS, encoding="utf-8-sig")
    news = df["News Text"].fillna("").astype(str)
    head = df["Headline"].fillna("").astype(str)
    comb = df["combined_text"].fillna("").astype(str) if "combined_text" in df.columns else (head + " " + news)
    return df, head, news, comb


class BM25:
    def __init__(self, tokenized_docs, k1=BM25_K1, b=BM25_B):
        self.k1, self.b = k1, b
        self.N = len(tokenized_docs)
        self.dl = np.array([max(len(d), 1) for d in tokenized_docs], dtype=np.float32)
        self.avgdl = float(self.dl.mean())
        dfreq = defaultdict(int)
        post = defaultdict(list)
        for i, toks in enumerate(tokenized_docs):
            tf = defaultdict(int)
            for t in toks:
                tf[t] += 1
            for t, c in tf.items():
                dfreq[t] += 1
                post[t].append((i, c))
        self.post = {
            t: (np.array([p[0] for p in v], dtype=np.int32), np.array([p[1] for p in v], dtype=np.float32))
            for t, v in post.items()
        }
        self.idf = {t: math.log((self.N - n + 0.5) / (n + 0.5) + 1.0) for t, n in dfreq.items()}

    def search(self, qtoks, top_k=15):
        scores = np.zeros(self.N, dtype=np.float32)
        for t in set(qtoks):
            if t not in self.post:
                continue
            ids, tfs = self.post[t]
            idf = self.idf[t]
            dl = self.dl[ids]
            denom = tfs + self.k1 * (1.0 - self.b + self.b * dl / self.avgdl)
            scores[ids] += idf * (tfs * (self.k1 + 1.0) / denom)
        k = min(top_k, self.N)
        part = np.argpartition(-scores, k)[:k]
        idx = part[np.argsort(-scores[part])]
        return [(int(i), float(scores[i])) for i in idx if scores[i] > 0][:top_k]


def stage_reproduce(eval_rows):
    print("=== reproduce existing rooms n=%s ===" % len(eval_rows), flush=True)
    import chromadb
    from sentence_transformers import SentenceTransformer

    client = chromadb.PersistentClient(path=p4a.CHROMA_DIR)
    col = client.get_collection(p4a.COLLECTION)
    mini = SentenceTransformer(p4a.MODEL_NAME)

    h_ranks, f_ranks, c_ranks = [], [], []
    t_h, t_f, t_c = [], [], []
    recs = []
    for i, r in enumerate(eval_rows, 1):
        q, _ = transliterate_roman(r["query_text"])
        src = r["source_doc_id"]
        t0 = time.perf_counter()
        hh = search_headlines(q, top_k=15)
        t_h.append(time.perf_counter() - t0)
        t0 = time.perf_counter()
        ff = search_full_content(q, top_k=15)
        t_f.append(time.perf_counter() - t0)
        t0 = time.perf_counter()
        qemb = mini.encode(q).tolist()
        arts, _ch, _ta, _tg = p4a.search_chunk_ann(col, qemb, n=p4a.N_CANDIDATES)
        t_c.append(time.perf_counter() - t0)
        hr, _ = rank_of(hh, src)
        fr, _ = rank_of(ff, src)
        cr, _ = rank_of(arts[:15], src)
        h_ranks.append(hr if hr else 999)
        f_ranks.append(fr if fr else 999)
        c_ranks.append(cr if cr else 999)
        recs.append({
            "query_id": r["query_id"],
            "split": r["split"],
            "language_type": r["language_type"],
            "query_text": r["query_text"],
            "source_doc_id": src,
            "headline_rank": h_ranks[-1],
            "full_rank": f_ranks[-1],
            "chunk_rank": c_ranks[-1],
        })
        if i % 10 == 0 or i == len(eval_rows):
            print("  reproduce %s/%s" % (i, len(eval_rows)), flush=True)

    mh = metrics_from_ranks(h_ranks, 5)
    mf = metrics_from_ranks(f_ranks, 5)
    mc = metrics_from_ranks(c_ranks, 5)
    payload = {
        "eval_n": len(eval_rows),
        "headline": mh,
        "old_full": mf,
        "chunk_ann": mc,
        "headline_mean_latency_sec": round(float(np.mean(t_h)), 4),
        "full_mean_latency_sec": round(float(np.mean(t_f)), 4),
        "chunk_mean_latency_sec": round(float(np.mean(t_c)), 4),
        "delta_hit": {
            "headline": round(mh["source_hit_rate"] - REC_HIT["headline"], 4),
            "full": round(mf["source_hit_rate"] - REC_HIT["full"], 4),
            "chunk": round(mc["source_hit_rate"] - REC_HIT["chunk"], 4),
        },
        "delta_ndcg": {
            "headline": round(mh["ndcg_at_k"] - REC_NDCG["headline"], 4),
            "full": round(mf["ndcg_at_k"] - REC_NDCG["full"], 4),
            "chunk": round(mc["ndcg_at_k"] - REC_NDCG["chunk"], 4),
        },
    }
    payload["reproduction_ok"] = all(
        abs(payload["delta_hit"][k]) <= HIT_TOL and abs(payload["delta_ndcg"][k]) <= NDCG_TOL
        for k in ("headline", "full", "chunk")
    )
    write_csv(
        os.path.join(OUT, "BASELINE_REPRODUCTION.csv"),
        ["system", "hit@5", "P@5", "nDCG@5", "MRR", "mean_latency_sec", "delta_hit", "delta_ndcg"],
        [
            ["headline", mh["source_hit_rate"], mh["p_at_k"], mh["ndcg_at_k"], mh["mrr"], payload["headline_mean_latency_sec"], payload["delta_hit"]["headline"], payload["delta_ndcg"]["headline"]],
            ["old_full", mf["source_hit_rate"], mf["p_at_k"], mf["ndcg_at_k"], mf["mrr"], payload["full_mean_latency_sec"], payload["delta_hit"]["full"], payload["delta_ndcg"]["full"]],
            ["chunk_ann", mc["source_hit_rate"], mc["p_at_k"], mc["ndcg_at_k"], mc["mrr"], payload["chunk_mean_latency_sec"], payload["delta_hit"]["chunk"], payload["delta_ndcg"]["chunk"]],
        ],
    )
    with open(os.path.join(ART, "dense_ranks.json"), "w", encoding="utf-8") as f:
        json.dump(recs, f, ensure_ascii=False)
    with open(os.path.join(ART, "reproduce.json"), "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(json.dumps(payload, indent=2), flush=True)
    if not payload["reproduction_ok"]:
        raise SystemExit("STOP: reproduction mismatch.")
    return recs, h_ranks, f_ranks, c_ranks, payload


def stage_bm25(eval_rows):
    print("=== BM25 k1=%s b=%s ===" % (BM25_K1, BM25_B), flush=True)
    _df, _h, _n, comb = load_corpus_texts()
    t0 = time.perf_counter()
    toks = [tokenize(t) for t in comb]
    idx = BM25(toks)
    build_s = time.perf_counter() - t0
    print("BM25 indexed %s docs in %.1f s avgdl=%.1f" % (idx.N, build_s, idx.avgdl), flush=True)
    ranks, lats, recs = [], [], []
    for i, r in enumerate(eval_rows, 1):
        qtoks = tokenize(r["query_text"])
        t1 = time.perf_counter()
        hits = idx.search(qtoks, top_k=15)
        lats.append(time.perf_counter() - t1)
        rk, sc = rank_of(hits, r["source_doc_id"])
        ranks.append(rk if rk else 999)
        recs.append({
            "query_id": r["query_id"],
            "language_type": r["language_type"],
            "bm25_rank": ranks[-1],
            "n_query_tokens": len(qtoks),
            "n_query_tokens_in_vocab": sum(1 for t in set(qtoks) if t in idx.idf),
        })
        if i % 20 == 0 or i == len(eval_rows):
            print("  bm25 %s/%s" % (i, len(eval_rows)), flush=True)
    m = metrics_from_ranks(ranks, 5)
    lang = by_lang(eval_rows, ranks)
    payload = {
        "k1": BM25_K1,
        "b": BM25_B,
        "doc_field": "combined_text (Headline + News Text)",
        "tokenizer": "Urdu unicode letters + [A-Za-z0-9], lowercased, no stemming, no transliteration",
        "n_docs": idx.N,
        "avgdl": round(idx.avgdl, 2),
        "build_sec": round(build_s, 1),
        "metrics_k5": m,
        "mean_latency_sec": round(float(np.mean(lats)), 4),
        "by_language": lang,
        "tuned_on_eval": False,
    }
    write_csv(
        os.path.join(OUT, "BM25_RESULTS.csv"),
        ["subset", "n", "hit@5", "P@5", "nDCG@5", "MRR", "mean_latency_sec"],
        [["all", m["n"], m["source_hit_rate"], m["p_at_k"], m["ndcg_at_k"], m["mrr"], payload["mean_latency_sec"]]]
        + [[k, v["n"], v["source_hit_rate"], v["p_at_k"], v["ndcg_at_k"], v["mrr"], ""] for k, v in lang.items()],
    )
    with open(os.path.join(ART, "bm25_ranks.json"), "w", encoding="utf-8") as f:
        json.dump(recs, f, ensure_ascii=False)
    with open(os.path.join(ART, "bm25.json"), "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(json.dumps({"bm25": m, "lang": {k: v["source_hit_rate"] for k, v in lang.items()}}, indent=2), flush=True)
    return ranks, payload


def stage_longctx(eval_rows, hw):
    from sentence_transformers import SentenceTransformer

    print("=== long-context %s ===" % LONG_MODEL, flush=True)
    _df, _h, _n, comb = load_corpus_texts()
    n = len(comb)
    device = "cuda" if hw.get("cuda") else "cpu"
    model = SentenceTransformer(LONG_MODEL, device=device)
    model.max_seq_length = LONG_MAX_SEQ

    proto_n = min(PROTO_N, n)
    texts = ["passage: " + str(comb.iloc[i]) for i in range(proto_n)]
    t0 = time.perf_counter()
    _ = model.encode(texts, batch_size=16, show_progress_bar=True, normalize_embeddings=True)
    proto_s = time.perf_counter() - t0
    dps = proto_n / max(proto_s, 1e-6)
    eta_h = (n / dps) / 3600.0
    feas = {
        "model": LONG_MODEL,
        "device": device,
        "proto_n": proto_n,
        "proto_sec": round(proto_s, 1),
        "docs_per_sec": round(dps, 2),
        "extrapolated_full_hours": round(eta_h, 2),
        "max_seq_length": LONG_MAX_SEQ,
        "embedding_dim": int(model.get_sentence_embedding_dimension()),
        "raw_embedding_gb": round(n * int(model.get_sentence_embedding_dimension()) * 4 / 1e9, 3),
        "feasible": eta_h <= MAX_EMBED_HOURS,
        "gate_hours": MAX_EMBED_HOURS,
    }
    with open(os.path.join(ART, "longctx_feasibility.json"), "w", encoding="utf-8") as f:
        json.dump(feas, f, indent=2)
    print(json.dumps(feas, indent=2), flush=True)
    if not feas["feasible"]:
        print("STOP: full-corpus long-context embed not feasible on this machine.", flush=True)
        return None, feas

    emb_path = os.path.join(ART, "longctx_embeddings.f32")
    prog_path = os.path.join(ART, "longctx_progress.json")
    dim = int(model.get_sentence_embedding_dimension())
    mode = "r+" if os.path.isfile(emb_path) and os.path.getsize(emb_path) == n * dim * 4 else "w+"
    mm = np.memmap(emb_path, dtype=np.float32, mode=mode, shape=(n, dim))
    start = 0
    if os.path.isfile(prog_path):
        start = int(json.load(open(prog_path, encoding="utf-8")).get("next", 0))
        print("resuming longctx at %s" % start, flush=True)
    t0 = time.perf_counter()
    bs = 32
    for i in range(start, n, bs):
        j = min(n, i + bs)
        batch = ["passage: " + str(comb.iloc[k]) for k in range(i, j)]
        mm[i:j] = model.encode(batch, batch_size=bs, show_progress_bar=False, normalize_embeddings=True)
        if j % 2000 == 0 or j == n:
            mm.flush()
            json.dump({"next": j}, open(prog_path, "w", encoding="utf-8"))
            print("  embed %s/%s (%.1f min)" % (j, n, (time.perf_counter() - t0) / 60.0), flush=True)
    mm.flush()
    embed_s = time.perf_counter() - t0

    ranks, lats, recs = [], [], []
    mat = np.asarray(mm)
    for i, r in enumerate(eval_rows, 1):
        q = "query: " + r["query_text"]
        t1 = time.perf_counter()
        qemb = model.encode(q, normalize_embeddings=True)
        sims = mat @ qemb
        idx = np.argpartition(-sims, 15)[:15]
        idx = idx[np.argsort(-sims[idx])]
        hits = [(int(j), float(sims[j])) for j in idx]
        lats.append(time.perf_counter() - t1)
        rk, sc = rank_of(hits, r["source_doc_id"])
        ranks.append(rk if rk else 999)
        recs.append({"query_id": r["query_id"], "longctx_rank": ranks[-1], "longctx_score_if_hit": sc})
        if i % 20 == 0 or i == len(eval_rows):
            print("  longctx eval %s/%s" % (i, len(eval_rows)), flush=True)

    m = metrics_from_ranks(ranks, 5)
    lang = by_lang(eval_rows, ranks)
    payload = {
        "model": LONG_MODEL,
        "max_seq_length": LONG_MAX_SEQ,
        "embedding_dim": dim,
        "device": device,
        "n_docs": n,
        "embed_sec": round(embed_s, 1),
        "index_bytes": os.path.getsize(emb_path),
        "metrics_k5": m,
        "mean_latency_sec": round(float(np.mean(lats)), 4),
        "by_language": lang,
        "feasibility": feas,
    }
    write_csv(
        os.path.join(OUT, "LONG_CONTEXT_RESULTS.csv"),
        ["subset", "n", "hit@5", "P@5", "nDCG@5", "MRR", "mean_latency_sec"],
        [["all", m["n"], m["source_hit_rate"], m["p_at_k"], m["ndcg_at_k"], m["mrr"], payload["mean_latency_sec"]]]
        + [[k, v["n"], v["source_hit_rate"], v["p_at_k"], v["ndcg_at_k"], v["mrr"], ""] for k, v in lang.items()],
    )
    with open(os.path.join(ART, "longctx_ranks.json"), "w", encoding="utf-8") as f:
        json.dump(recs, f, ensure_ascii=False)
    with open(os.path.join(ART, "longctx.json"), "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(json.dumps({"longctx": m}, indent=2), flush=True)
    return ranks, payload


def stage_report(eval_rows, h_ranks, f_ranks, c_ranks, b_ranks, l_ranks, repro, bm25, longctx, hw):
    rooms = {"headline": h_ranks, "old_full": f_ranks, "chunk_ann": c_ranks, "bm25": b_ranks}
    if l_ranks is not None:
        rooms["long_context"] = l_ranks
    mets = {k: metrics_from_ranks(v, 5) for k, v in rooms.items()}
    nd = {k: [ndcg_at(None if r >= 999 else r, 5) for r in v] for k, v in rooms.items()}
    lat = {
        "headline": repro["headline_mean_latency_sec"],
        "old_full": repro["full_mean_latency_sec"],
        "chunk_ann": repro["chunk_mean_latency_sec"],
        "bm25": bm25["mean_latency_sec"],
    }
    if longctx and l_ranks is not None:
        lat["long_context"] = longctx["mean_latency_sec"]

    write_csv(
        os.path.join(OUT, "RETRIEVAL_COMPARISON.csv"),
        ["system", "hit@5", "P@5", "nDCG@5", "MRR"],
        [[k, mets[k]["source_hit_rate"], mets[k]["p_at_k"], mets[k]["ndcg_at_k"], mets[k]["mrr"]] for k in rooms],
    )
    write_csv(os.path.join(OUT, "LATENCY_COMPARISON.csv"), ["system", "mean_query_latency_sec"], [[k, lat[k]] for k in lat])

    lang_rows = []
    for lang in ("urdu", "roman_urdu", "mixed"):
        for k, v in rooms.items():
            rs = [rk for r, rk in zip(eval_rows, v) if r.get("language_type") == lang]
            if not rs:
                continue
            m = metrics_from_ranks(rs, 5)
            lang_rows.append([lang, k, m["n"], m["source_hit_rate"], m["p_at_k"], m["ndcg_at_k"], m["mrr"]])
    write_csv(os.path.join(OUT, "LANGUAGE_COMPARISON.csv"), ["language_type", "system", "n", "hit@5", "P@5", "nDCG@5", "MRR"], lang_rows)
    write_csv(os.path.join(OUT, "URDU_COMPARISON.csv"), ["language_type", "system", "n", "hit@5", "P@5", "nDCG@5", "MRR"], [x for x in lang_rows if x[0] == "urdu"])
    write_csv(os.path.join(OUT, "ROMAN_URDU_COMPARISON.csv"), ["language_type", "system", "n", "hit@5", "P@5", "nDCG@5", "MRR"], [x for x in lang_rows if x[0] == "roman_urdu"])

    def ceil_of(keys):
        return round(float(np.mean([max(nd[k][i] for k in keys) for i in range(len(eval_rows))])), 4)

    oracle_specs = [
        ("headline+old_full", ["headline", "old_full"]),
        ("headline+chunk_ann", ["headline", "chunk_ann"]),
        ("headline+bm25", ["headline", "bm25"]),
    ]
    if l_ranks is not None:
        oracle_specs.append(("headline+long_context", ["headline", "long_context"]))
    oracle_specs.append(("all_rooms", list(rooms)))
    o_rows = [[name, len(eval_rows), ceil_of(keys), ",".join(keys)] for name, keys in oracle_specs]
    write_csv(os.path.join(OUT, "ORACLE_COMPARISON.csv"), ["setting", "n", "mean_oracle_nDCG@5", "rooms"], o_rows)

    header = ["query_id", "split", "language_type", "source_doc_id", "query_text",
              "headline_rank", "full_rank", "chunk_rank", "bm25_rank"]
    if l_ranks is not None:
        header.append("longctx_rank")
    header += ["best_room", "headline_miss5", "bm25_hit_headline_miss", "chunk_hit_headline_miss", "longctx_hit_headline_miss"]
    qrows = []
    for i, r in enumerate(eval_rows):
        scores = {k: nd[k][i] for k in rooms}
        best = max(scores, key=scores.get)
        if scores[best] == 0:
            best = "none"
        row = [r["query_id"], r["split"], r["language_type"], r["source_doc_id"], r["query_text"][:160],
               h_ranks[i], f_ranks[i], c_ranks[i], b_ranks[i]]
        if l_ranks is not None:
            row.append(l_ranks[i])
        row += [
            best,
            int(h_ranks[i] > 5),
            int(b_ranks[i] <= 5 and h_ranks[i] > 5),
            int(c_ranks[i] <= 5 and h_ranks[i] > 5),
            int((l_ranks[i] <= 5 and h_ranks[i] > 5) if l_ranks is not None else 0),
        ]
        qrows.append(row)
    write_csv(os.path.join(OUT, "QUERY_LEVEL_COMPARISON.csv"), header, qrows)

    store = [
        ["headline_cache", dir_size(os.path.join(ROOT, "data", "headline_embeddings_phase2_5_cache.npy"))],
        ["old_full_chroma", dir_size(os.path.join(ROOT, "data", "chromadb"))],
        ["chunk_ann_chroma", dir_size(p4a.CHROMA_DIR)],
        ["bm25_in_memory_only", 0],
    ]
    if longctx and l_ranks is not None:
        store.append(["longctx_memmap", longctx["index_bytes"]])
    write_csv(os.path.join(OUT, "STORAGE_COMPARISON.csv"), ["artifact", "bytes"], store)

    def uniq(rr):
        return sum(1 for i in range(len(eval_rows)) if rr[i] <= 5 and h_ranks[i] > 5)

    summary = {
        "eval_n": len(eval_rows),
        "frozen_test_used": False,
        "svm_retrained": False,
        "metrics": mets,
        "latency_sec": lat,
        "oracle_ndcg5": {name: ceil_of(keys) for name, keys in oracle_specs},
        "unique_hit5_when_headline_misses": {
            "bm25": uniq(b_ranks),
            "chunk_ann": uniq(c_ranks),
            "old_full": uniq(f_ranks),
            "long_context": uniq(l_ranks) if l_ranks is not None else None,
        },
        "longctx_ran": l_ranks is not None,
        "hardware": hw,
    }
    with open(os.path.join(ART, "phase4b_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        os.makedirs(FIG, exist_ok=True)
        names = list(rooms)
        xs = np.arange(len(names))
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(xs - 0.2, [mets[k]["source_hit_rate"] for k in names], 0.4, label="Hit@5")
        ax.bar(xs + 0.2, [mets[k]["ndcg_at_k"] for k in names], 0.4, label="nDCG@5")
        ax.set_xticks(xs)
        ax.set_xticklabels(names, rotation=20)
        ax.set_ylabel("known-item score")
        ax.set_title("Phase 4B n=78 retrieval rooms (not H001-H040)")
        ax.legend()
        ax.grid(True, axis="y", alpha=0.3)
        fig.tight_layout()
        fig.savefig(os.path.join(FIG, "room_comparison.png"), dpi=140)
        plt.close()
        fig, ax = plt.subplots(figsize=(7, 3.8))
        ax.barh([x[0] for x in o_rows], [x[2] for x in o_rows])
        ax.set_xlabel("mean oracle nDCG@5")
        ax.set_title("Phase 4B oracle ceilings (n=78)")
        fig.tight_layout()
        fig.savefig(os.path.join(FIG, "oracle_ceilings.png"), dpi=140)
        plt.close()
    except Exception as exc:
        print("figures skipped:", exc, flush=True)
    return summary


def write_markdown(summary, repro, longctx):
    mets = summary["metrics"]
    lines = [
        "# PHASE 4B RESULTS",
        "",
        "Eval = Phase 2 **dev + internal_val**, **n=78**, known-item `source_doc_id`.",
        "**H001–H040 unused.** SVM not retrained. No RRF / reranker as a system.",
        "Known-item P@5 = 0.2 × Hit@5. This is not human graded relevance.",
        "",
        "## Baseline reproduction",
        "",
        "| System | Hit@5 | P@5 | nDCG@5 | MRR | latency (s) |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for k, lab in (("headline", "Headline"), ("old_full", "Old Full"), ("chunk_ann", "Chunk ANN")):
        m = mets[k]
        lines.append("| %s | %.4f | %.4f | %.4f | %.4f | %.4f |" % (
            lab, m["source_hit_rate"], m["p_at_k"], m["ndcg_at_k"], m["mrr"], summary["latency_sec"][k]))
    lines += ["", "Reproduction matched Phase 4A: **%s**." % repro["reproduction_ok"], "", "## BM25", ""]
    m = mets["bm25"]
    lines += [
        "| Hit@5 | P@5 | nDCG@5 | MRR | latency |",
        "| ---: | ---: | ---: | ---: | ---: |",
        "| %.4f | %.4f | %.4f | %.4f | %.4f s |" % (
            m["source_hit_rate"], m["p_at_k"], m["ndcg_at_k"], m["mrr"], summary["latency_sec"]["bm25"]),
        "",
        "Okapi BM25 k1=1.5 b=0.75 on `combined_text`. No stemming, no roman transliteration, not tuned on n=78.",
        "",
        "## Long-context",
        "",
    ]
    lc = mets.get("long_context")
    if lc and longctx and summary["longctx_ran"]:
        lines += [
            "| Model | Context | Dim | Hit@5 | P@5 | nDCG@5 | MRR | latency | index |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
            "| `%s` | %s | %s | %.4f | %.4f | %.4f | %.4f | %.4f s | %.2f GB |" % (
                LONG_MODEL, LONG_MAX_SEQ, longctx["embedding_dim"], lc["source_hit_rate"], lc["p_at_k"],
                lc["ndcg_at_k"], lc["mrr"], summary["latency_sec"]["long_context"], longctx["index_bytes"] / 1e9),
        ]
    else:
        lines.append("Full-corpus long-context index **not built** (feasibility gate). See `artifacts/longctx_feasibility.json`.")
    lines += ["", "## Oracle nDCG@5", ""]
    for k, v in summary["oracle_ndcg5"].items():
        lines.append("- %s: **%.4f**" % (k, v))
    lines += ["", "## Unique Hit@5 when Headline misses", json.dumps(summary["unique_hit5_when_headline_misses"], indent=2), ""]
    with open(os.path.join(OUT, "PHASE4B_RESULTS.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", default="all", choices=["all", "reproduce", "bm25", "longctx", "report"])
    args = ap.parse_args()
    os.makedirs(ART, exist_ok=True)
    os.makedirs(FIG, exist_ok=True)
    np.random.seed(SEED)
    hw = hardware()
    eval_rows = load_eval_rows()
    print("eval n=%s hw=%s" % (len(eval_rows), hw), flush=True)

    h_ranks = f_ranks = c_ranks = b_ranks = l_ranks = None
    repro = bm25 = longctx = None

    if args.stage in ("all", "reproduce"):
        _recs, h_ranks, f_ranks, c_ranks, repro = stage_reproduce(eval_rows)
    else:
        recs = json.load(open(os.path.join(ART, "dense_ranks.json"), encoding="utf-8"))
        repro = json.load(open(os.path.join(ART, "reproduce.json"), encoding="utf-8"))
        if not repro.get("reproduction_ok"):
            raise SystemExit("Stored reproduction failed.")
        h_ranks = [r["headline_rank"] for r in recs]
        f_ranks = [r["full_rank"] for r in recs]
        c_ranks = [r["chunk_rank"] for r in recs]

    if args.stage in ("all", "bm25"):
        b_ranks, bm25 = stage_bm25(eval_rows)
    elif args.stage == "report":
        bm25 = json.load(open(os.path.join(ART, "bm25.json"), encoding="utf-8"))
        b_ranks = [r["bm25_rank"] for r in json.load(open(os.path.join(ART, "bm25_ranks.json"), encoding="utf-8"))]

    if args.stage in ("all", "longctx"):
        l_ranks, longctx = stage_longctx(eval_rows, hw)
    elif args.stage == "report":
        lp = os.path.join(ART, "longctx.json")
        if os.path.isfile(lp):
            longctx = json.load(open(lp, encoding="utf-8"))
            l_ranks = [r["longctx_rank"] for r in json.load(open(os.path.join(ART, "longctx_ranks.json"), encoding="utf-8"))]

    if args.stage in ("all", "report"):
        summary = stage_report(eval_rows, h_ranks, f_ranks, c_ranks, b_ranks, l_ranks, repro, bm25, longctx, hw)
        write_markdown(summary, repro, longctx)
        print(json.dumps({"metrics": summary["metrics"], "oracle": summary["oracle_ndcg5"]}, indent=2), flush=True)


if __name__ == "__main__":
    main()
