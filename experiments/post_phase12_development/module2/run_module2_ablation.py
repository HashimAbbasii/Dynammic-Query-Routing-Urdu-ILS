# -*- coding: utf-8 -*-
"""
Module 2 R-dev ablation: exactly one retrieval pass each for M2-A and M2-B.

Does not modify M0, Method D, dictionary, queries, qrels, or Module 1 artifacts.
Does not stack Module 1 transforms.
Does not tune after seeing results.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import subprocess
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

import pandas as pd

_DIR = Path(__file__).resolve().parent
ROOT = _DIR.parents[2]
P5 = ROOT / "experiments" / "phase5_roman_urdu"
ARCHIVE_VALIDATE = ROOT / "archive" / "historical_experiments" / "validate" / "dual_index_routing"
R_DEV = ROOT / "experiments" / "post_phase12_development"

sys.path.insert(0, str(ARCHIVE_VALIDATE))
sys.path.insert(0, str(P5))
sys.path.insert(0, str(_DIR))
sys.path.insert(0, str(ROOT))

import run_phase5 as p5  # noqa: E402
from candidates import (  # noqa: E402
    BM25_B,
    BM25_K1,
    CANDIDATES,
    RRF_K,
    TOP_K,
    char_wb_3grams,
    rrf_fuse,
)

QUERY_PATH = R_DEV / "queries_r_dev.csv"
M0_TOP50 = R_DEV / "R_TOP50_RETRIEVAL.csv"
QRELS_PATH = R_DEV / "qrels_r_dev.csv"
DICT_PATH = ROOT / "models" / "roman_urdu_dict_expanded.json"
CORPUS_PATH = ROOT / "data" / "clean_articles.csv"
M0_CODE = P5 / "run_phase5.py"

EXPECTED = {
    "queries_r_dev.csv": "1603b37eeee41fa6270f4e13d185c8eebd4512d025cd5fc67e8a81de9407e75f",
    "R_TOP50_RETRIEVAL.csv": "927a14a25b6f1de2a5c28aabdc2d8cbc0d4336e0b2b437490691a7bff63a2aa2",
    "qrels_r_dev.csv": "506305b5401102a3659d21b69c7a937bcdcde78b21a1409a6a6132255ff37bcb",
    "roman_urdu_dict_expanded.json": "30c3f61a64ec641abbb3acdbc7a8bcaf197f0238f1bf9e76c2c7ce8e590f86a3",
    "clean_articles.csv": "8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231",
}

M0_KI_HITS = 19
M0_NAT_HITS = 12
CANDIDATE_IDS = ["M2-A", "M2-B"]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(1024 * 1024)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def git_commit():
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return out.strip()
    except Exception:
        return None


def load_queries():
    rows = []
    with open(QUERY_PATH, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            r["source_doc_id"] = int(r["source_doc_id"]) if r.get("source_doc_id", "").strip() else ""
            rows.append(r)
    return rows


def load_qrels():
    by_q = defaultdict(dict)
    with open(QRELS_PATH, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            by_q[r["query_id"]][int(r["doc_id"])] = r["relevance_label"]
    return by_q


def load_m0_ranks():
    by_q = defaultdict(list)
    with open(M0_TOP50, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            by_q[r["query_id"]].append(r)
    ki_src_rank = {}
    nat_top5 = {}
    m0_det = {}
    m0_ranking = {}
    for qid, rows in by_q.items():
        rows = sorted(rows, key=lambda x: int(x["rank"]))
        m0_det[qid] = rows[0]["detector_label"]
        ranking = [(int(r["rank"]), int(r["doc_id"])) for r in rows]
        m0_ranking[qid] = ranking
        if rows[0]["track"] == "KI":
            src = int(rows[0]["source_doc_id"])
            ki_src_rank[qid] = p5.rank_of(
                [(int(r["doc_id"]), float(r["bm25_score"])) for r in rows],
                src,
            )
        else:
            nat_top5[qid] = [int(r["doc_id"]) for r in rows if int(r["rank"]) <= 5]
    return ki_src_rank, nat_top5, m0_det, m0_ranking


def preflight(queries):
    failed = []
    files = {
        "queries_r_dev.csv": QUERY_PATH,
        "R_TOP50_RETRIEVAL.csv": M0_TOP50,
        "qrels_r_dev.csv": QRELS_PATH,
        "roman_urdu_dict_expanded.json": DICT_PATH,
        "clean_articles.csv": CORPUS_PATH,
    }
    hashes = {}
    for name, path in files.items():
        h = sha256_file(path)
        hashes[name] = h
        if h != EXPECTED[name]:
            failed.append("%s_sha_mismatch" % name)

    if len(queries) != 100:
        failed.append("query_count_not_100")
    ki_n = sum(1 for q in queries if q["track"] == "KI")
    nat_n = sum(1 for q in queries if q["track"] == "NAT")
    if ki_n != 50:
        failed.append("ki_count_not_50")
    if nat_n != 50:
        failed.append("nat_count_not_50")

    # Verify M0 baselines from frozen Top-50 + qrels
    m0_ki_rank, m0_nat_top5, m0_det, _ = load_m0_ranks()
    ki_ids = [q["query_id"] for q in queries if q["track"] == "KI"]
    nat_ids = [q["query_id"] for q in queries if q["track"] == "NAT"]
    # R080 may be absent from Top-50 (zero hits)
    for qid in nat_ids:
        m0_nat_top5.setdefault(qid, [])
        if qid not in m0_det:
            # recover detector from query text via M0 detector for strata; store separately
            pass
    ki_hits = sum(1 for q in ki_ids if m0_ki_rank.get(q, 999) <= 5)
    nat_hits = 0
    qrels = load_qrels()
    for qid in nat_ids:
        labels = qrels.get(qid, {})
        if any(labels.get(d) in ("A", "B") for d in m0_nat_top5.get(qid, [])):
            nat_hits += 1
    if ki_hits != M0_KI_HITS:
        failed.append("m0_ki_baseline_mismatch_%s" % ki_hits)
    if nat_hits != M0_NAT_HITS:
        failed.append("m0_nat_baseline_mismatch_%s" % nat_hits)

    # Schema check for M2-B
    df_head = pd.read_csv(CORPUS_PATH, encoding="utf-8-sig", nrows=1)
    cols = set(df_head.columns)
    if "Headline" not in cols or "News Text" not in cols:
        failed.append("headline_body_schema_missing")
    if "Index" not in cols:
        failed.append("index_column_missing")

    return {
        "failed": failed,
        "preflight_pass": len(failed) == 0,
        "hashes": hashes,
        "query_count": len(queries),
        "ki_count": ki_n,
        "nat_count": nat_n,
        "m0_ki_hits": ki_hits,
        "m0_nat_hits": nat_hits,
    }


def romanize_text_tokens(text: str, rev: dict) -> str:
    toks = p5.tokenize(text)
    rtoks = [t for t in (p5.romanize_token(t, rev) for t in toks) if t]
    return " ".join(rtoks)


def build_m2a_indexes(rev: dict):
    print("M2-A: loading corpus...", flush=True)
    import numpy as np
    df = pd.read_csv(CORPUS_PATH, encoding="utf-8-sig")
    if not bool((df["Index"].values == np.arange(len(df))).all()):
        raise RuntimeError("Corpus Index is not contiguous row position; STOP")
    headlines = df["Headline"].fillna("").astype(str)
    bodies = df["News Text"].fillna("").astype(str)
    combined = (headlines + " " + bodies).tolist()

    print("M2-A: building Urdu char_wb 3-gram docs...", flush=True)
    t0 = time.perf_counter()
    urdu_docs = []
    for i, text in enumerate(combined):
        urdu_docs.append(char_wb_3grams(text))
        if (i + 1) % 20000 == 0:
            print("  urdu char docs %s/%s" % (i + 1, len(combined)), flush=True)
    print("M2-A: Urdu char docs %.1fs" % (time.perf_counter() - t0), flush=True)

    print("M2-A: building Roman Method-D char_wb 3-gram docs...", flush=True)
    t1 = time.perf_counter()
    roman_docs = []
    for i, text in enumerate(combined):
        roman_str = romanize_text_tokens(text, rev)
        roman_docs.append(char_wb_3grams(roman_str))
        if (i + 1) % 20000 == 0:
            print("  roman char docs %s/%s" % (i + 1, len(combined)), flush=True)
    print("M2-A: Roman char docs %.1fs" % (time.perf_counter() - t1), flush=True)

    print("M2-A: building BM25 indexes...", flush=True)
    t2 = time.perf_counter()
    urdu_bm25 = p5.BM25(urdu_docs, k1=BM25_K1, b=BM25_B)
    roman_bm25 = p5.BM25(roman_docs, k1=BM25_K1, b=BM25_B)
    print("M2-A: BM25 build %.1fs" % (time.perf_counter() - t2), flush=True)
    return urdu_bm25, roman_bm25


def build_m2b_indexes(rev: dict):
    print("M2-B: loading corpus...", flush=True)
    df = pd.read_csv(CORPUS_PATH, encoding="utf-8-sig")
    import numpy as np
    if not bool((df["Index"].values == np.arange(len(df))).all()):
        raise RuntimeError("Corpus Index is not contiguous row position; STOP")
    headlines = df["Headline"].fillna("").astype(str).tolist()
    bodies = df["News Text"].fillna("").astype(str).tolist()
    empty_h = sum(1 for h in headlines if not h.strip())
    empty_b = sum(1 for b in bodies if not b.strip())
    if empty_h or empty_b:
        raise RuntimeError("Empty headline/body unexpected: h=%s b=%s; STOP" % (empty_h, empty_b))

    print("M2-B: tokenizing headline/body (Urdu + Method D roman)...", flush=True)
    t0 = time.perf_counter()
    u_head, u_body, r_head, r_body = [], [], [], []
    for i in range(len(headlines)):
        uh = p5.tokenize(headlines[i])
        ub = p5.tokenize(bodies[i])
        rh = [t for t in (p5.romanize_token(t, rev) for t in uh) if t]
        rb = [t for t in (p5.romanize_token(t, rev) for t in ub) if t]
        u_head.append(uh)
        u_body.append(ub)
        r_head.append(rh)
        r_body.append(rb)
        if (i + 1) % 20000 == 0:
            print("  tokenize %s/%s" % (i + 1, len(headlines)), flush=True)
    print("M2-B: tokenize %.1fs" % (time.perf_counter() - t0), flush=True)

    print("M2-B: building 4 BM25 indexes...", flush=True)
    t1 = time.perf_counter()
    indexes = {
        "urdu_headline": p5.BM25(u_head, k1=BM25_K1, b=BM25_B),
        "urdu_body": p5.BM25(u_body, k1=BM25_K1, b=BM25_B),
        "roman_headline": p5.BM25(r_head, k1=BM25_K1, b=BM25_B),
        "roman_body": p5.BM25(r_body, k1=BM25_K1, b=BM25_B),
    }
    print("M2-B: BM25 build %.1fs" % (time.perf_counter() - t1), flush=True)
    return indexes


def query_tokens_m2a(qtext: str, det: str, rev: dict) -> list[str]:
    if det == "ROMAN":
        roman_str = romanize_text_tokens(qtext, rev)
        return char_wb_3grams(roman_str)
    return char_wb_3grams(qtext)


def query_tokens_m2b_word(qtext: str, det: str, rev: dict) -> list[str]:
    toks = p5.tokenize(qtext)
    if det == "ROMAN":
        return [t for t in (p5.romanize_token(t, rev) for t in toks) if t]
    return toks


def retrieve_m2a(queries, urdu_bm25, roman_bm25, rev):
    per_q = {}
    top50_rows = []
    path_counts = Counter()
    for r in queries:
        qid = r["query_id"]
        qtext = r["query_text"]
        track = r["track"]
        det = p5.detect_script(qtext)
        qtoks = query_tokens_m2a(qtext, det, rev)
        if det == "ROMAN":
            path = "roman_char3gram_bm25_method_D"
            hits = roman_bm25.search(qtoks, top_k=TOP_K)
        else:
            path = "urdu_char3gram_bm25"
            hits = urdu_bm25.search(qtoks, top_k=TOP_K)
        path_counts[path] += 1
        src = r["source_doc_id"]
        src_rank = p5.rank_of(hits, src) if track == "KI" and src != "" else None
        top5_docs = [int(d) for d, _ in hits[:5]]
        per_q[qid] = {
            "detector_label": det,
            "retrieval_path": path,
            "source_rank": src_rank,
            "top5_docs": top5_docs,
            "n_hits": len(hits),
            "ranking": [(i + 1, int(d)) for i, (d, _) in enumerate(hits)],
        }
        for rank, (did, score) in enumerate(hits, 1):
            top50_rows.append({
                "experiment_id": "post_phase12_module2_M2-A",
                "candidate_id": "M2-A",
                "query_id": qid,
                "query_text": qtext,
                "track": track,
                "source_doc_id": src,
                "detector_label": det,
                "retrieval_path": path,
                "rank": rank,
                "doc_id": int(did),
                "bm25_score": float(score),
                "n_hits_returned": len(hits),
            })
    return per_q, top50_rows, dict(path_counts)


def retrieve_m2b(queries, indexes, rev):
    per_q = {}
    top50_rows = []
    path_counts = Counter()
    for r in queries:
        qid = r["query_id"]
        qtext = r["query_text"]
        track = r["track"]
        det = p5.detect_script(qtext)
        qtoks = query_tokens_m2b_word(qtext, det, rev)
        if det == "ROMAN":
            h_hits = indexes["roman_headline"].search(qtoks, top_k=TOP_K)
            b_hits = indexes["roman_body"].search(qtoks, top_k=TOP_K)
            path = "roman_headline_body_rrf_method_D"
        else:
            h_hits = indexes["urdu_headline"].search(qtoks, top_k=TOP_K)
            b_hits = indexes["urdu_body"].search(qtoks, top_k=TOP_K)
            path = "urdu_headline_body_rrf"
        path_counts[path] += 1
        hits = rrf_fuse([h_hits, b_hits], k=RRF_K, top_k=TOP_K)
        src = r["source_doc_id"]
        src_rank = p5.rank_of(hits, src) if track == "KI" and src != "" else None
        top5_docs = [int(d) for d, _ in hits[:5]]
        per_q[qid] = {
            "detector_label": det,
            "retrieval_path": path,
            "source_rank": src_rank,
            "top5_docs": top5_docs,
            "n_hits": len(hits),
            "ranking": [(i + 1, int(d)) for i, (d, _) in enumerate(hits)],
            "headline_n_hits": len(h_hits),
            "body_n_hits": len(b_hits),
        }
        for rank, (did, score) in enumerate(hits, 1):
            top50_rows.append({
                "experiment_id": "post_phase12_module2_M2-B",
                "candidate_id": "M2-B",
                "query_id": qid,
                "query_text": qtext,
                "track": track,
                "source_doc_id": src,
                "detector_label": det,
                "retrieval_path": path,
                "rank": rank,
                "doc_id": int(did),
                "bm25_score": float(score),
                "n_hits_returned": len(hits),
            })
    return per_q, top50_rows, dict(path_counts)


def nat_success(top5_by_q, qrels, nat_ids):
    hits = []
    for qid in nat_ids:
        labels = qrels.get(qid, {})
        docs = top5_by_q.get(qid, [])
        ok = any(labels.get(d) in ("A", "B") for d in docs)
        hits.append(ok)
    return sum(hits), len(nat_ids), hits


def ki_hit5(src_ranks, ki_ids):
    hits = sum(1 for q in ki_ids if src_ranks.get(q, 999) <= 5)
    return hits, len(ki_ids)


def compare_queries(ids, m0_metric, cand_metric, hit_fn):
    improved, worsened, unchanged = [], [], []
    for q in ids:
        m0_hit = hit_fn(m0_metric, q)
        c_hit = hit_fn(cand_metric, q)
        if c_hit and not m0_hit:
            improved.append(q)
        elif m0_hit and not c_hit:
            worsened.append(q)
        else:
            unchanged.append(q)
    return improved, worsened, unchanged


def eval_candidate(per_q, queries, qrels, m0_ki_rank, m0_nat_top5, m0_det, m0_ranking):
    ki_ids = [r["query_id"] for r in queries if r["track"] == "KI"]
    nat_ids = [r["query_id"] for r in queries if r["track"] == "NAT"]

    # Ensure NAT ids missing from M0 dump (zero-hit) exist
    for qid in nat_ids:
        m0_nat_top5.setdefault(qid, [])

    # Fill detector for any query missing from M0 dump using runtime detect on query text
    for r in queries:
        qid = r["query_id"]
        if qid not in m0_det:
            m0_det[qid] = p5.detect_script(r["query_text"])

    cand_ki_rank = {q: per_q[q]["source_rank"] for q in ki_ids if per_q[q]["source_rank"] is not None}
    # Missing source_rank => treat as 999
    for q in ki_ids:
        if q not in cand_ki_rank:
            cand_ki_rank[q] = 999
    cand_nat_top5 = {q: per_q[q]["top5_docs"] for q in nat_ids}

    ki_h, ki_n = ki_hit5(cand_ki_rank, ki_ids)
    nat_h, nat_n, _ = nat_success(cand_nat_top5, qrels, nat_ids)
    m0_ki_h, _ = ki_hit5(m0_ki_rank, ki_ids)
    m0_nat_h, _, _ = nat_success(m0_nat_top5, qrels, nat_ids)

    def ki_hit(rank_map, q):
        return rank_map.get(q, 999) <= 5

    def nat_hit(top5_map, q):
        labels = qrels.get(q, {})
        return any(labels.get(d) in ("A", "B") for d in top5_map.get(q, []))

    ki_imp, ki_worse, ki_same = compare_queries(ki_ids, m0_ki_rank, cand_ki_rank, ki_hit)
    nat_imp, nat_worse, nat_same = compare_queries(
        nat_ids,
        {q: nat_hit(m0_nat_top5, q) for q in nat_ids},
        {q: nat_hit(cand_nat_top5, q) for q in nat_ids},
        lambda m, q: m[q],
    )

    ranking_changed, ranking_unchanged = [], []
    for r in queries:
        qid = r["query_id"]
        m0 = m0_ranking.get(qid, [])
        cand = per_q[qid]["ranking"]
        if m0 != cand:
            ranking_changed.append(qid)
        else:
            ranking_unchanged.append(qid)

    def script_ki(script):
        sub = [q for q in ki_ids if m0_det.get(q) == script]
        if not sub:
            return {"n": 0, "m0_hits": 0, "cand_hits": 0, "m0_rate": None, "cand_rate": None, "delta": None}
        m0h = sum(1 for q in sub if m0_ki_rank.get(q, 999) <= 5)
        ch = sum(1 for q in sub if cand_ki_rank.get(q, 999) <= 5)
        n = len(sub)
        return {
            "n": n,
            "m0_hits": m0h,
            "cand_hits": ch,
            "m0_rate": round(m0h / n, 4),
            "cand_rate": round(ch / n, 4),
            "delta": round(ch / n - m0h / n, 4),
        }

    def script_nat(script):
        sub = [q for q in nat_ids if m0_det.get(q) == script]
        if not sub:
            return {"n": 0, "m0_hits": 0, "cand_hits": 0, "m0_rate": None, "cand_rate": None, "delta": None}
        m0h = sum(1 for q in sub if nat_hit(m0_nat_top5, q))
        ch = sum(1 for q in sub if nat_hit(cand_nat_top5, q))
        n = len(sub)
        return {
            "n": n,
            "m0_hits": m0h,
            "cand_hits": ch,
            "m0_rate": round(m0h / n, 4),
            "cand_rate": round(ch / n, 4),
            "delta": round(ch / n - m0h / n, 4),
        }

    # Source-rank distribution for KI
    def rank_bucket(rank):
        if rank is None or rank >= 999:
            return "miss_or_absent"
        if rank <= 5:
            return "1-5"
        if rank <= 10:
            return "6-10"
        if rank <= 50:
            return "11-50"
        return "gt50"

    src_dist = Counter(rank_bucket(cand_ki_rank.get(q, 999)) for q in ki_ids)
    m0_src_dist = Counter(rank_bucket(m0_ki_rank.get(q, 999)) for q in ki_ids)

    return {
        "ki": {
            "m0": {"hits": m0_ki_h, "n": ki_n, "rate": round(m0_ki_h / ki_n, 4)},
            "candidate": {"hits": ki_h, "n": ki_n, "rate": round(ki_h / ki_n, 4)},
            "delta": round(ki_h / ki_n - m0_ki_h / ki_n, 4),
            "delta_hits": ki_h - m0_ki_h,
            "improved": ki_imp,
            "worsened": ki_worse,
            "unchanged": ki_same,
            "by_script": {s: script_ki(s) for s in ("URDU", "ROMAN", "MIXED")},
            "source_rank_distribution_candidate": dict(src_dist),
            "source_rank_distribution_m0": dict(m0_src_dist),
        },
        "nat": {
            "m0": {"hits": m0_nat_h, "n": nat_n, "rate": round(m0_nat_h / nat_n, 4)},
            "candidate": {"hits": nat_h, "n": nat_n, "rate": round(nat_h / nat_n, 4)},
            "delta": round(nat_h / nat_n - m0_nat_h / nat_n, 4),
            "delta_hits": nat_h - m0_nat_h,
            "improved": nat_imp,
            "worsened": nat_worse,
            "unchanged": nat_same,
            "by_script": {s: script_nat(s) for s in ("URDU", "ROMAN", "MIXED")},
            "evaluation_note": "Pool-based: frozen qrels label M0 Top-5 docs only",
        },
        "ranking": {
            "changed_query_ids": ranking_changed,
            "unchanged_query_ids": ranking_unchanged,
            "changed_count": len(ranking_changed),
            "unchanged_count": len(ranking_unchanged),
        },
    }


def write_csv(path: Path, rows):
    fields = [
        "experiment_id", "candidate_id", "query_id", "query_text", "track",
        "source_doc_id", "detector_label", "retrieval_path", "rank", "doc_id",
        "bm25_score", "n_hits_returned",
    ]
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def write_manifest(cid, metrics, path_counts, out_csv, pre, build_s, search_s, impl_files):
    post_hashes = {name: sha256_file(path) for name, path in {
        "queries_r_dev.csv": QUERY_PATH,
        "R_TOP50_RETRIEVAL.csv": M0_TOP50,
        "qrels_r_dev.csv": QRELS_PATH,
        "roman_urdu_dict_expanded.json": DICT_PATH,
        "clean_articles.csv": CORPUS_PATH,
    }.items()}
    frozen_ok = all(post_hashes[k] == EXPECTED[k] for k in EXPECTED)
    manifest = {
        "experiment_id": "post_phase12_module2_%s" % cid,
        "candidate_id": cid,
        "name": CANDIDATES[cid]["name"],
        "description": CANDIDATES[cid]["description"],
        "params": CANDIDATES[cid]["params"],
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "git_commit": git_commit(),
        "retrieval_pass_count": 1,
        "exactly_one_retrieval_pass": True,
        "m1_stacking": False,
        "embeddings_used": False,
        "neural_reranker_used": False,
        "preflight": pre,
        "postflight_frozen_hashes": post_hashes,
        "frozen_integrity_ok": frozen_ok,
        "frozen_inputs_sha256": EXPECTED,
        "m0_code_sha256": sha256_file(M0_CODE),
        "implementation_file_hashes": {p.name: sha256_file(p) for p in impl_files},
        "output_file": out_csv.name,
        "output_retrieval_sha256": sha256_file(out_csv),
        "n_queries": pre["query_count"],
        "n_retrieved_rows": sum(1 for _ in open(out_csv, encoding="utf-8")) - 1,
        "routing_path_counts": path_counts,
        "index_build_seconds": round(build_s, 2),
        "search_seconds": round(search_s, 2),
        "metrics": metrics,
        "m0_modified": False,
        "dictionary_modified": False,
        "qrels_modified": False,
        "queries_modified": False,
        "method_d_modified": False,
    }
    with open(_DIR / ("%s_MANIFEST.json" % cid), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    return manifest


def write_results_md(all_metrics, all_manifests):
    def cell(hits, n):
        return "%s/%s" % (hits, n)

    def dhit(m):
        return "%+d" % m["ki"]["delta_hits"] if "delta_hits" in m["ki"] else "—"

    lines = [
        "# Module 2 R-dev ablation results",
        "",
        "Pre-specified lexical retrieval candidates. M0 baseline from frozen artifacts.",
        "No Module 1 stacking. No embeddings. No post-hoc parameter changes.",
        "",
        "## A. M0 frozen baseline",
        "",
        "| Track | Metric | Result |",
        "| --- | --- | --- |",
        "| KI | ExactSource Hit@5 | 19/50 = 38.00% |",
        "| NAT | Success@5 (frozen M0-pool qrels) | 12/50 = 24.00% |",
        "",
        "NAT note: qrels label M0 Top-5 documents only; R080 remains in the NAT denominator.",
        "",
    ]

    for cid in CANDIDATE_IDS:
        m = all_metrics[cid]
        lines.extend([
            "## %s — %s" % (cid, "B" if cid == "M2-B" else "A" if cid == "M2-A" else cid),
            "",
            CANDIDATES[cid]["description"],
            "",
            "| | KI Hit@5 | NAT Success@5 |",
            "| --- | --- | --- |",
            "| M0 | %s/50 | %s/50 |" % (m["ki"]["m0"]["hits"], m["nat"]["m0"]["hits"]),
            "| Candidate | %s/50 | %s/50 |" % (m["ki"]["candidate"]["hits"], m["nat"]["candidate"]["hits"]),
            "| Delta (hits) | %+d | %+d |" % (m["ki"]["delta_hits"], m["nat"]["delta_hits"]),
            "",
            "KI improved: %s | worsened: %s | unchanged: %s"
            % (len(m["ki"]["improved"]), len(m["ki"]["worsened"]), len(m["ki"]["unchanged"])),
            "",
            "NAT improved: %s | worsened: %s | unchanged: %s"
            % (len(m["nat"]["improved"]), len(m["nat"]["worsened"]), len(m["nat"]["unchanged"])),
            "",
            "Ranking lists changed vs M0: %s / 100" % m["ranking"]["changed_count"],
            "",
            "KI source-rank distribution (candidate): %s"
            % json.dumps(m["ki"]["source_rank_distribution_candidate"], ensure_ascii=False),
            "",
            "KI source-rank distribution (M0): %s"
            % json.dumps(m["ki"]["source_rank_distribution_m0"], ensure_ascii=False),
            "",
        ])

    # Summary tables
    lines.extend([
        "## D–F. Comparison tables",
        "",
        "| Candidate | Track | Overall | URDU | ROMAN | MIXED | Δ hits vs M0 |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ])
    for cid in ["M0"] + CANDIDATE_IDS:
        if cid == "M0":
            m = all_metrics["M2-A"]  # use shared m0 numbers
            ki_s = m["ki"]["by_script"]
            nat_s = m["nat"]["by_script"]
            lines.append(
                "| M0 | KI ExactSource@5 | 19/50 | %s | %s | %s | — |"
                % (
                    cell(ki_s["URDU"]["m0_hits"], ki_s["URDU"]["n"]),
                    cell(ki_s["ROMAN"]["m0_hits"], ki_s["ROMAN"]["n"]),
                    cell(ki_s["MIXED"]["m0_hits"], ki_s["MIXED"]["n"]),
                )
            )
            lines.append(
                "| M0 | NAT Success@5 | 12/50 | %s | %s | %s | — |"
                % (
                    cell(nat_s["URDU"]["m0_hits"], nat_s["URDU"]["n"]),
                    cell(nat_s["ROMAN"]["m0_hits"], nat_s["ROMAN"]["n"]),
                    cell(nat_s["MIXED"]["m0_hits"], nat_s["MIXED"]["n"]),
                )
            )
        else:
            m = all_metrics[cid]
            ki_s = m["ki"]["by_script"]
            nat_s = m["nat"]["by_script"]
            lines.append(
                "| %s | KI ExactSource@5 | %s/50 | %s | %s | %s | %+d |"
                % (
                    cid,
                    m["ki"]["candidate"]["hits"],
                    cell(ki_s["URDU"]["cand_hits"], ki_s["URDU"]["n"]),
                    cell(ki_s["ROMAN"]["cand_hits"], ki_s["ROMAN"]["n"]),
                    cell(ki_s["MIXED"]["cand_hits"], ki_s["MIXED"]["n"]),
                    m["ki"]["delta_hits"],
                )
            )
            lines.append(
                "| %s | NAT Success@5 | %s/50 | %s | %s | %s | %+d |"
                % (
                    cid,
                    m["nat"]["candidate"]["hits"],
                    cell(nat_s["URDU"]["cand_hits"], nat_s["URDU"]["n"]),
                    cell(nat_s["ROMAN"]["cand_hits"], nat_s["ROMAN"]["n"]),
                    cell(nat_s["MIXED"]["cand_hits"], nat_s["MIXED"]["n"]),
                    m["nat"]["delta_hits"],
                )
            )

    lines.extend([
        "",
        "| Candidate | KI improved | KI worsened | KI unchanged | NAT improved | NAT worsened | NAT unchanged | Ranking lists changed |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ])
    for cid in CANDIDATE_IDS:
        m = all_metrics[cid]
        lines.append(
            "| %s | %s | %s | %s | %s | %s | %s | %s |"
            % (
                cid,
                len(m["ki"]["improved"]),
                len(m["ki"]["worsened"]),
                len(m["ki"]["unchanged"]),
                len(m["nat"]["improved"]),
                len(m["nat"]["worsened"]),
                len(m["nat"]["unchanged"]),
                m["ranking"]["changed_count"],
            )
        )

    # Regression / interpretation filled after we know results — write placeholders then
    # the runner appends interpretation based on metrics.
    lines.extend(["", "## I. Regression analysis", ""])
    for cid in CANDIDATE_IDS:
        m = all_metrics[cid]
        lines.append("### %s" % cid)
        for script in ("URDU", "MIXED", "ROMAN"):
            ki = m["ki"]["by_script"][script]
            nat = m["nat"]["by_script"][script]
            lines.append(
                "- KI %s: M0 %s/%s → cand %s/%s (Δ hits %+d)"
                % (
                    script,
                    ki["m0_hits"], ki["n"],
                    ki["cand_hits"], ki["n"],
                    ki["cand_hits"] - ki["m0_hits"],
                )
            )
            lines.append(
                "- NAT %s: M0 %s/%s → cand %s/%s (Δ hits %+d)"
                % (
                    script,
                    nat["m0_hits"], nat["n"],
                    nat["cand_hits"], nat["n"],
                    nat["cand_hits"] - nat["m0_hits"],
                )
            )
        lines.append("")

    lines.extend([
        "## J. Interpretation",
        "",
        "See scientific decision below. R-dev only; no generalization claim.",
        "",
        "## K. Scientific decision",
        "",
    ])

    decisions = []
    for cid in CANDIDATE_IDS:
        m = all_metrics[cid]
        ki_delta = m["ki"]["delta_hits"]
        urdu_reg = m["ki"]["by_script"]["URDU"]["cand_hits"] - m["ki"]["by_script"]["URDU"]["m0_hits"]
        mixed_reg = m["ki"]["by_script"]["MIXED"]["cand_hits"] - m["ki"]["by_script"]["MIXED"]["m0_hits"]
        nat_urdu_reg = m["nat"]["by_script"]["URDU"]["cand_hits"] - m["nat"]["by_script"]["URDU"]["m0_hits"]
        nat_mixed_reg = m["nat"]["by_script"]["MIXED"]["cand_hits"] - m["nat"]["by_script"]["MIXED"]["m0_hits"]
        material_reg = (urdu_reg < 0) or (mixed_reg < 0) or (nat_urdu_reg < 0) or (nat_mixed_reg < 0)
        if ki_delta > 0 and not material_reg:
            decisions.append("%s: promising lexical candidate (KI +%d; no URDU/MIXED hit regression)." % (cid, ki_delta))
        elif ki_delta > 0 and material_reg:
            decisions.append(
                "%s: aggregate KI +%d but **not** unconditional improvement (URDU/MIXED regression present)."
                % (cid, ki_delta)
            )
        elif ki_delta == 0 and m["nat"]["delta_hits"] == 0:
            decisions.append("%s: null on R-dev under the pre-specified configuration." % cid)
        else:
            decisions.append(
                "%s: KI Δ=%+d, NAT Δ=%+d; see strata for trade-offs."
                % (cid, ki_delta, m["nat"]["delta_hits"])
            )
    for d in decisions:
        lines.append("- " + d)
    lines.extend([
        "",
        "Do not combine M2-A and M2-B. Do not invent M2-C/D without a new pre-registration.",
        "Do not claim future unseen performance from R-dev.",
        "",
    ])

    path = _DIR / "MODULE2_RESULTS.md"
    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    queries = load_queries()
    pre = preflight(queries)
    if not pre["preflight_pass"]:
        print("STOP preflight failed:", pre["failed"], flush=True)
        sys.exit(2)
    print("PREFLIGHT PASS", json.dumps({
        "queries": pre["query_count"],
        "ki": pre["ki_count"],
        "nat": pre["nat_count"],
        "m0_ki": pre["m0_ki_hits"],
        "m0_nat": pre["m0_nat_hits"],
    }), flush=True)

    qrels = load_qrels()
    m0_ki_rank, m0_nat_top5, m0_det, m0_ranking = load_m0_ranks()
    for qid in [q["query_id"] for q in queries if q["track"] == "NAT"]:
        m0_nat_top5.setdefault(qid, [])

    fwd = p5.load_roman_dict()
    rev = p5.load_reverse_roman(fwd)

    all_metrics = {}
    all_manifests = {}
    impl_files = [
        _DIR / "candidates.py",
        _DIR / "run_module2_ablation.py",
        _DIR / "MODULE2_PROTOCOL.md",
    ]

    # ---- M2-A ----
    print("=== M2-A START ===", flush=True)
    t_build = time.perf_counter()
    urdu_a, roman_a = build_m2a_indexes(rev)
    build_a = time.perf_counter() - t_build
    t_search = time.perf_counter()
    per_a, rows_a, paths_a = retrieve_m2a(queries, urdu_a, roman_a, rev)
    search_a = time.perf_counter() - t_search
    out_a = _DIR / "M2-A_TOP50_RETRIEVAL.csv"
    write_csv(out_a, rows_a)
    metrics_a = eval_candidate(per_a, queries, qrels, m0_ki_rank, m0_nat_top5, m0_det, m0_ranking)
    man_a = write_manifest("M2-A", metrics_a, paths_a, out_a, pre, build_a, search_a, impl_files)
    all_metrics["M2-A"] = metrics_a
    all_manifests["M2-A"] = man_a
    print(
        "M2-A KI=%s/50 NAT=%s/50 delta_ki=%+d delta_nat=%+d ranking_changed=%s"
        % (
            metrics_a["ki"]["candidate"]["hits"],
            metrics_a["nat"]["candidate"]["hits"],
            metrics_a["ki"]["delta_hits"],
            metrics_a["nat"]["delta_hits"],
            metrics_a["ranking"]["changed_count"],
        ),
        flush=True,
    )
    # Free large indexes before M2-B
    del urdu_a, roman_a, per_a, rows_a

    # ---- M2-B ----
    print("=== M2-B START ===", flush=True)
    t_build = time.perf_counter()
    indexes_b = build_m2b_indexes(rev)
    build_b = time.perf_counter() - t_build
    t_search = time.perf_counter()
    per_b, rows_b, paths_b = retrieve_m2b(queries, indexes_b, rev)
    search_b = time.perf_counter() - t_search
    out_b = _DIR / "M2-B_TOP50_RETRIEVAL.csv"
    write_csv(out_b, rows_b)
    metrics_b = eval_candidate(per_b, queries, qrels, m0_ki_rank, m0_nat_top5, m0_det, m0_ranking)
    man_b = write_manifest("M2-B", metrics_b, paths_b, out_b, pre, build_b, search_b, impl_files)
    all_metrics["M2-B"] = metrics_b
    all_manifests["M2-B"] = man_b
    print(
        "M2-B KI=%s/50 NAT=%s/50 delta_ki=%+d delta_nat=%+d ranking_changed=%s"
        % (
            metrics_b["ki"]["candidate"]["hits"],
            metrics_b["nat"]["candidate"]["hits"],
            metrics_b["ki"]["delta_hits"],
            metrics_b["nat"]["delta_hits"],
            metrics_b["ranking"]["changed_count"],
        ),
        flush=True,
    )

    # Postflight frozen integrity
    for name, exp in EXPECTED.items():
        path = {
            "queries_r_dev.csv": QUERY_PATH,
            "R_TOP50_RETRIEVAL.csv": M0_TOP50,
            "qrels_r_dev.csv": QRELS_PATH,
            "roman_urdu_dict_expanded.json": DICT_PATH,
            "clean_articles.csv": CORPUS_PATH,
        }[name]
        h = sha256_file(path)
        if h != exp:
            print("STOP postflight frozen hash mismatch", name, flush=True)
            sys.exit(2)

    write_results_md(all_metrics, all_manifests)
    print("MODULE2 COMPLETE", flush=True)


if __name__ == "__main__":
    main()
