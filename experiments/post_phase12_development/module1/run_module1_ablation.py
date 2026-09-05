# -*- coding: utf-8 -*-
"""
Module 1 R-dev ablation: one retrieval pass per candidate.

Does not modify M0, dictionary, queries, qrels, or M0 retrieval artifacts.
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

import numpy as np
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
from candidates import CANDIDATES, get_roman_token_fn  # noqa: E402

TOP_K = 50
QUERY_PATH = R_DEV / "queries_r_dev.csv"
M0_TOP50 = R_DEV / "R_TOP50_RETRIEVAL.csv"
QRELS_PATH = R_DEV / "qrels_r_dev.csv"
EXPECTED_QUERY_SHA = "1603b37eeee41fa6270f4e13d185c8eebd4512d025cd5fc67e8a81de9407e75f"
EXPECTED_M0_TOP50_SHA = "927a14a25b6f1de2a5c28aabdc2d8cbc0d4336e0b2b437490691a7bff63a2aa2"
EXPECTED_QRELS_SHA = "506305b5401102a3659d21b69c7a937bcdcde78b21a1409a6a6132255ff37bcb"
M0_NAT_SUCCESS = 12
CANDIDATE_IDS = ["M1-A", "M1-B", "M1-C"]


def sha256_file(path):
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
    """query_id -> source_rank (KI), top5 docs (NAT), runtime detector."""
    by_q = defaultdict(list)
    with open(M0_TOP50, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            by_q[r["query_id"]].append(r)
    ki_src_rank = {}
    nat_top5 = {}
    m0_det = {}
    for qid, rows in by_q.items():
        rows = sorted(rows, key=lambda x: int(x["rank"]))
        m0_det[qid] = rows[0]["detector_label"]
        if rows[0]["track"] == "KI":
            src = int(rows[0]["source_doc_id"])
            ki_src_rank[qid] = p5.rank_of(
                [(int(r["doc_id"]), float(r["bm25_score"])) for r in rows],
                src,
            )
        else:
            nat_top5[qid] = [int(r["doc_id"]) for r in rows if int(r["rank"]) <= 5]
    return ki_src_rank, nat_top5, m0_det


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


def build_indexes(fwd, rev):
    df = pd.read_csv(p5.CORPUS, encoding="utf-8-sig")
    if "combined_text" in df.columns:
        texts = df["combined_text"].fillna("").astype(str).tolist()
    else:
        texts = (
            df["Headline"].fillna("").astype(str)
            + " "
            + df["News Text"].fillna("").astype(str)
        ).tolist()
    headlines = df["Headline"].fillna("").astype(str)
    news = df["News Text"].fillna("").astype(str) if "News Text" in df.columns else pd.Series([""] * len(df))
    urdu_docs, roman_docs = [], []
    for text in texts:
        utoks = p5.tokenize(text)
        rtoks = [t for t in (p5.romanize_token(t, rev) for t in utoks) if t]
        urdu_docs.append(utoks)
        roman_docs.append(rtoks)
    return p5.BM25(urdu_docs), p5.BM25(roman_docs), headlines, news


def retrieve_candidate(queries, candidate_id, urdu_bm25, roman_bm25, fwd):
    roman_fn = get_roman_token_fn(candidate_id)
    per_q = {}
    top50_rows = []
    for r in queries:
        qid = r["query_id"]
        qtext = r["query_text"]
        track = r["track"]
        det = p5.detect_script(qtext)
        if det == "ROMAN":
            qtoks = roman_fn(qtext, fwd)
            path = "roman_bm25_method_D"
            hits = roman_bm25.search(qtoks, top_k=TOP_K)
        else:
            qtoks = p5.tokenize(qtext)
            path = "urdu_bm25"
            hits = urdu_bm25.search(qtoks, top_k=TOP_K)
        src = r["source_doc_id"]
        src_rank = p5.rank_of(hits, src) if track == "KI" and src != "" else None
        top5_docs = [int(d) for d, _ in hits[:5]]
        per_q[qid] = {
            "detector_label": det,
            "retrieval_path": path,
            "source_rank": src_rank,
            "top5_docs": top5_docs,
            "n_hits": len(hits),
        }
        for rank, (did, score) in enumerate(hits, 1):
            top50_rows.append({
                "experiment_id": "post_phase12_module1_%s" % candidate_id,
                "candidate_id": candidate_id,
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
    return per_q, top50_rows


def eval_candidate(per_q, queries, qrels, m0_ki_rank, m0_nat_top5, m0_det):
    ki_ids = [r["query_id"] for r in queries if r["track"] == "KI"]
    nat_ids = [r["query_id"] for r in queries if r["track"] == "NAT"]

    cand_ki_rank = {q: per_q[q]["source_rank"] for q in ki_ids if per_q[q]["source_rank"] is not None}
    cand_nat_top5 = {q: per_q[q]["top5_docs"] for q in nat_ids}

    ki_h, ki_n = ki_hit5(cand_ki_rank, ki_ids)
    nat_h, nat_n, nat_hit_list = nat_success(cand_nat_top5, qrels, nat_ids)
    m0_ki_h, _ = ki_hit5(m0_ki_rank, ki_ids)
    m0_nat_h, _, _ = nat_success(m0_nat_top5, qrels, nat_ids)

    def ki_hit(rank_map, q):
        return rank_map.get(q, 999) <= 5

    def nat_hit(top5_map, q):
        labels = qrels.get(q, {})
        return any(labels.get(d) in ("A", "B") for d in top5_map.get(q, []))

    ki_imp, ki_worse, ki_same = compare_queries(
        ki_ids, m0_ki_rank, cand_ki_rank, ki_hit
    )
    nat_imp, nat_worse, nat_same = compare_queries(
        nat_ids,
        {q: nat_hit(m0_nat_top5, q) for q in nat_ids},
        {q: nat_hit(cand_nat_top5, q) for q in nat_ids},
        lambda m, q: m[q],
    )

    def script_ki(script):
        sub = [q for q in ki_ids if m0_det.get(q) == script]
        if not sub:
            return {"n": 0, "m0_hits": 0, "cand_hits": 0, "m0_rate": None, "cand_rate": None}
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
            return {"n": 0, "m0_hits": 0, "cand_hits": 0, "m0_rate": None, "cand_rate": None}
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

    return {
        "ki": {
            "m0": {"hits": m0_ki_h, "n": ki_n, "rate": round(m0_ki_h / ki_n, 4)},
            "candidate": {"hits": ki_h, "n": ki_n, "rate": round(ki_h / ki_n, 4)},
            "delta": round(ki_h / ki_n - m0_ki_h / ki_n, 4),
            "improved": ki_imp,
            "worsened": ki_worse,
            "unchanged": ki_same,
            "by_script": {s: script_ki(s) for s in ("URDU", "ROMAN", "MIXED")},
        },
        "nat": {
            "m0": {"hits": m0_nat_h, "n": nat_n, "rate": round(m0_nat_h / nat_n, 4)},
            "candidate": {"hits": nat_h, "n": nat_n, "rate": round(nat_h / nat_n, 4)},
            "delta": round(nat_h / nat_n - m0_nat_h / nat_n, 4),
            "improved": nat_imp,
            "worsened": nat_worse,
            "unchanged": nat_same,
            "by_script": {s: script_nat(s) for s in ("URDU", "ROMAN", "MIXED")},
            "evaluation_note": "Pool-based: frozen qrels label M0 Top-5 docs only",
        },
    }


def write_results_md(all_results, m0_ki, m0_nat):
    lines = [
        "# Module 1 R-dev ablation results",
        "",
        "Candidate interventions on **ROMAN branch only**. M0 baseline from frozen artifacts.",
        "",
        "## M0 baseline (frozen)",
        "",
        "| Track | Metric | Result |",
        "| --- | --- | --- |",
        "| KI | ExactSource Hit@5 | %s/50 = %.2f%% |" % (m0_ki["hits"], 100 * m0_ki["rate"]),
        "| NAT | Success@5 (frozen qrels) | %s/50 = %.2f%% |" % (m0_nat["hits"], 100 * m0_nat["rate"]),
        "",
    ]
    for cid in CANDIDATE_IDS:
        res = all_results[cid]
        meta = CANDIDATES[cid]
        lines.extend([
            "## %s — %s" % (cid, meta["name"]),
            "",
            meta["description"],
            "",
            "| | KI Hit@5 | NAT Success@5 |",
            "| --- | --- | --- |",
            "| M0 | %s/50 | %s/50 |" % (res["ki"]["m0"]["hits"], res["nat"]["m0"]["hits"]),
            "| Candidate | %s/50 | %s/50 |" % (res["ki"]["candidate"]["hits"], res["nat"]["candidate"]["hits"]),
            "| Delta | %+.0f | %+.0f |" % (
                res["ki"]["candidate"]["hits"] - res["ki"]["m0"]["hits"],
                res["nat"]["candidate"]["hits"] - res["nat"]["m0"]["hits"],
            ),
            "",
            "**KI script strata (Hit@5):** %s" % json.dumps(res["ki"]["by_script"], ensure_ascii=False),
            "",
            "**NAT script strata (Success@5):** %s" % json.dumps(res["nat"]["by_script"], ensure_ascii=False),
            "",
            "KI improved: %s | worsened: %s | unchanged: %s"
            % (len(res["ki"]["improved"]), len(res["ki"]["worsened"]), len(res["ki"]["unchanged"])),
            "",
            "NAT improved: %s | worsened: %s | unchanged: %s"
            % (len(res["nat"]["improved"]), len(res["nat"]["worsened"]), len(res["nat"]["unchanged"])),
            "",
        ])
    lines.append("No generalization claims. R-dev development only.")
    with open(_DIR / "MODULE1_RESULTS.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    q_sha = sha256_file(QUERY_PATH)
    m0_sha = sha256_file(M0_TOP50)
    qrels_sha = sha256_file(QRELS_PATH)
    if q_sha != EXPECTED_QUERY_SHA:
        raise RuntimeError("query SHA mismatch")
    if m0_sha != EXPECTED_M0_TOP50_SHA:
        raise RuntimeError("M0 top50 SHA mismatch")
    if qrels_sha != EXPECTED_QRELS_SHA:
        raise RuntimeError("qrels SHA mismatch")

    queries = load_queries()
    qrels = load_qrels()
    m0_ki_rank, m0_nat_top5, m0_det = load_m0_ranks()
    m0_ki_h, ki_n = ki_hit5(m0_ki_rank, [r["query_id"] for r in queries if r["track"] == "KI"])
    m0_nat_h, nat_n, _ = nat_success(m0_nat_top5, qrels, [r["query_id"] for r in queries if r["track"] == "NAT"])

    fwd = p5.load_roman_dict()
    rev = p5.load_reverse_roman(fwd)
    t0 = time.perf_counter()
    urdu_bm25, roman_bm25, _, _ = build_indexes(fwd, rev)
    index_s = time.perf_counter() - t0

    all_results = {}
    manifest = {
        "experiment_id": "post_phase12_module1_ablation",
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "git_commit": git_commit(),
        "queries_r_dev_sha256": q_sha,
        "m0_top50_sha256": m0_sha,
        "qrels_sha256": qrels_sha,
        "m0_code_path": "experiments/phase5_roman_urdu/run_phase5.py",
        "module1_code": "experiments/post_phase12_development/module1/",
        "normalization_package": "src/roman_urdu_normalization/",
        "bm25_k1": 1.5,
        "bm25_b": 0.75,
        "top_k": TOP_K,
        "routing_unchanged": True,
        "m0_modified": False,
        "dictionary_modified": False,
        "candidates": {},
        "m0_baseline": {
            "ki_exactsource_hit_at_5": {"hits": m0_ki_h, "n": ki_n, "rate": round(m0_ki_h / ki_n, 4)},
            "nat_success_at_5": {"hits": m0_nat_h, "n": nat_n, "rate": round(m0_nat_h / nat_n, 4)},
        },
        "index_build_seconds": round(index_s, 2),
    }

    for cid in CANDIDATE_IDS:
        t1 = time.perf_counter()
        per_q, top50_rows = retrieve_candidate(queries, cid, urdu_bm25, roman_bm25, fwd)
        search_s = time.perf_counter() - t1
        out_csv = _DIR / ("%s_TOP50_RETRIEVAL.csv" % cid)
        fields = [
            "experiment_id", "candidate_id", "query_id", "query_text", "track",
            "source_doc_id", "detector_label", "retrieval_path", "rank", "doc_id",
            "bm25_score", "n_hits_returned",
        ]
        with open(out_csv, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(top50_rows)
        out_sha = sha256_file(out_csv)
        metrics = eval_candidate(per_q, queries, qrels, m0_ki_rank, m0_nat_top5, m0_det)
        all_results[cid] = metrics
        manifest["candidates"][cid] = {
            "name": CANDIDATES[cid]["name"],
            "description": CANDIDATES[cid]["description"],
            "uses_dictionary": CANDIDATES[cid]["uses_dictionary"],
            "retrieval_output": str(out_csv.name),
            "retrieval_sha256": out_sha,
            "search_seconds": round(search_s, 2),
            "metrics": metrics,
        }
        print(
            "%s KI=%s/50 NAT=%s/50 delta_ki=%+.0f delta_nat=%+.0f"
            % (
                cid,
                metrics["ki"]["candidate"]["hits"],
                metrics["nat"]["candidate"]["hits"],
                metrics["ki"]["candidate"]["hits"] - metrics["ki"]["m0"]["hits"],
                metrics["nat"]["candidate"]["hits"] - metrics["nat"]["m0"]["hits"],
            ),
            flush=True,
        )

    write_results_md(
        all_results,
        {"hits": m0_ki_h, "n": ki_n, "rate": m0_ki_h / ki_n},
        {"hits": m0_nat_h, "n": nat_n, "rate": m0_nat_h / nat_n},
    )
    with open(_DIR / "MODULE1_MANIFEST.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print("MODULE1 ABLATION COMPLETE", flush=True)


if __name__ == "__main__":
    main()
