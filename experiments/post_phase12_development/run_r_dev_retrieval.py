# -*- coding: utf-8 -*-
"""
Post-Phase-12 R-dev: frozen M0 retrieval on sealed queries_r_dev.csv.

One retrieval pass only. Does not modify M0, Method D, dictionary, or queries.
Does not compute Hit@5, Success@5, nDCG, MRR, or any performance metric.
Does not create qrels or annotations.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime, timezone

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

import numpy as np
import pandas as pd

_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(_DIR, "..", ".."))
P5 = os.path.join(ROOT, "experiments", "phase5_roman_urdu")
MANIFEST8 = os.path.join(ROOT, "experiments", "phase8_final_freeze", "FINAL_SYSTEM_MANIFEST.json")
ART = os.path.join(_DIR, "artifacts")
EXPERIMENT_ID = "post_phase12_r_dev"
TOP_K = 50
SNIP = 500
QUERY_PATH = os.path.join(_DIR, "queries_r_dev.csv")
EXPECTED_QUERY_SHA = "1603b37eeee41fa6270f4e13d185c8eebd4512d025cd5fc67e8a81de9407e75f"
EXPECTED_CORPUS_SHA = "8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231"
EXPECTED_DICT_SHA = "30c3f61a64ec641abbb3acdbc7a8bcaf197f0238f1bf9e76c2c7ce8e590f86a3"
EXPECTED_N = 111860
EXPECTED_DICT = 198
EXPECTED_QUERY_COUNT = 100

# retrieve.py lives under archived validate/; run_phase5 expects ROOT/validate/...
ARCHIVE_VALIDATE = os.path.join(
    ROOT, "archive", "historical_experiments", "validate", "dual_index_routing"
)
sys.path.insert(0, ARCHIVE_VALIDATE)
sys.path.insert(0, P5)
import run_phase5 as p5  # noqa: E402


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(1024 * 1024)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def clip(s):
    s = (s or "").replace("\r", " ").replace("\n", " ").strip()
    return s if len(s) <= SNIP else s[: SNIP - 1] + "…"


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
            rows.append(r)
    ids = [r["query_id"] for r in rows]
    if ids != ["R%03d" % i for i in range(1, EXPECTED_QUERY_COUNT + 1)]:
        raise RuntimeError("query ids not R001-R100 in order: %s" % ids)
    if len(ids) != len(set(ids)):
        raise RuntimeError("duplicate query ids")
    for r in rows:
        if r["track"] not in ("KI", "NAT"):
            raise RuntimeError("invalid track for %s: %s" % (r["query_id"], r["track"]))
        if r["track"] == "KI":
            if not str(r.get("source_doc_id", "")).strip():
                raise RuntimeError("KI missing source_doc_id: %s" % r["query_id"])
            r["source_doc_id"] = int(r["source_doc_id"])
        else:
            if str(r.get("source_doc_id", "")).strip():
                raise RuntimeError("NAT must not have source_doc_id: %s" % r["query_id"])
            r["source_doc_id"] = ""
    return rows


def route_m0(query_text):
    """Frozen M0: raw tokenize, no M1-M4."""
    det = p5.detect_script(query_text)
    qtoks = p5.tokenize(query_text)
    if det == "ROMAN":
        return det, "roman_bm25_method_D", "roman", qtoks
    return det, "urdu_bm25", "urdu", qtoks


def preflight():
    os.makedirs(ART, exist_ok=True)
    failed = []
    notes = []

    corpus = os.path.join(ROOT, "data", "clean_articles.csv")
    dpath = os.path.join(ROOT, "models", "roman_urdu_dict_expanded.json")

    q_exists = os.path.isfile(QUERY_PATH)
    if not q_exists:
        failed.append("queries_r_dev_missing")

    q_hash = sha256_file(QUERY_PATH) if q_exists else ""
    q_hash_ok = q_hash == EXPECTED_QUERY_SHA
    if not q_hash_ok:
        failed.append("queries_r_dev_sha256_mismatch")

    q_rows = []
    q_load_ok = False
    try:
        q_rows = load_queries()
        q_load_ok = True
        if len(q_rows) != EXPECTED_QUERY_COUNT:
            failed.append("query_count_mismatch")
    except Exception as e:
        failed.append("queries_r_dev_invalid")
        notes.append("query_load: %s" % e)

    corpus_exists = os.path.isfile(corpus)
    if not corpus_exists:
        failed.append("corpus_missing")
    c_hash = sha256_file(corpus) if corpus_exists else ""
    n_rows = int(len(pd.read_csv(corpus, encoding="utf-8-sig", usecols=[0]))) if corpus_exists else 0
    hash_ok = c_hash == EXPECTED_CORPUS_SHA
    n_ok = n_rows == EXPECTED_N
    if not hash_ok:
        failed.append("corpus_sha256_mismatch")
    if not n_ok:
        failed.append("corpus_n_docs_mismatch")

    dict_exists = os.path.isfile(dpath)
    if not dict_exists:
        failed.append("dictionary_missing")
    n_keys = 0
    d_hash = ""
    if dict_exists:
        with open(dpath, encoding="utf-8") as f:
            n_keys = len(json.load(f))
        d_hash = sha256_file(dpath)
    dict_keys_ok = n_keys == EXPECTED_DICT
    dict_sha_ok = d_hash == EXPECTED_DICT_SHA
    if not dict_keys_ok:
        failed.append("dictionary_key_count_mismatch")
    if not dict_sha_ok:
        failed.append("dictionary_sha256_mismatch")

    man = {}
    if os.path.isfile(MANIFEST8):
        with open(MANIFEST8, encoding="utf-8") as f:
            man = json.load(f)
    else:
        failed.append("phase8_manifest_missing")

    k1b_ok = (
        man.get("bm25_k1") == p5.BM25_K1 == 1.5
        and man.get("bm25_b") == p5.BM25_B == 0.75
    )
    topk_ok = TOP_K == 50 == getattr(p5, "TOP_K", None) == man.get("top_k", 50)
    routing_ok = man.get("routing") == {
        "URDU": "urdu_bm25",
        "ROMAN": "roman_bm25_method_D",
        "MIXED": "urdu_bm25",
    }
    if not k1b_ok:
        failed.append("bm25_k1_b_mismatch")
    if not topk_ok:
        failed.append("top_k_mismatch")
    if not routing_ok:
        failed.append("routing_mismatch")

    code_ok = all(
        callable(getattr(p5, name, None))
        for name in (
            "detect_script",
            "tokenize",
            "romanize_token",
            "load_roman_dict",
            "load_reverse_roman",
        )
    ) and hasattr(p5, "BM25") and callable(getattr(p5.BM25, "search", None))
    if not code_ok:
        failed.append("phase5_code_paths_missing")

    ok = len(failed) == 0
    checks = {
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "experiment_id": EXPERIMENT_ID,
        "official_system": "M0",
        "m0_code_path": "experiments/phase5_roman_urdu/run_phase5.py",
        "m1_m4_applied": False,
        "module1_applied": False,
        "module2_applied": False,
        "embeddings_used": False,
        "semantic_retrieval_used": False,
        "queries_r_dev_path": QUERY_PATH,
        "queries_r_dev_exists": q_exists,
        "queries_r_dev_sha256": q_hash,
        "queries_r_dev_sha256_expected": EXPECTED_QUERY_SHA,
        "queries_r_dev_hash_ok": q_hash_ok,
        "query_text_unchanged": q_hash_ok,
        "query_ids_ok": q_load_ok,
        "n_queries": len(q_rows),
        "corpus_path": corpus,
        "corpus_exists": corpus_exists,
        "corpus_sha256": c_hash,
        "corpus_sha256_expected": EXPECTED_CORPUS_SHA,
        "corpus_hash_ok": hash_ok,
        "corpus_n_rows": n_rows,
        "corpus_n_ok": n_ok,
        "dict_path": dpath,
        "dict_keys": n_keys,
        "dict_keys_ok": dict_keys_ok,
        "dict_sha256": d_hash,
        "dict_sha256_expected": EXPECTED_DICT_SHA,
        "dict_sha_ok": dict_sha_ok,
        "manifest_k1": man.get("bm25_k1"),
        "manifest_b": man.get("bm25_b"),
        "code_k1": p5.BM25_K1,
        "code_b": p5.BM25_B,
        "k1b_ok": k1b_ok,
        "top_k": TOP_K,
        "topk_ok": topk_ok,
        "routing": man.get("routing"),
        "routing_ok": routing_ok,
        "phase5_code_paths_ok": code_ok,
        "retrieval_pass_count": 1,
        "failed_checks": failed,
        "notes": notes,
        "preflight_pass": ok,
    }
    with open(os.path.join(ART, "preflight.json"), "w", encoding="utf-8") as f:
        json.dump(checks, f, indent=2)
    print("PREFLIGHT", "PASS" if ok else "FAIL", json.dumps({
        "failed": failed,
        "query_hash_ok": q_hash_ok,
        "corpus_hash_ok": hash_ok,
        "dict_sha_ok": dict_sha_ok,
        "k1b_ok": k1b_ok,
    }), flush=True)
    return checks, q_rows


def search_one(qtext, urdu_bm25, roman_bm25):
    det, path, which, qtoks = route_m0(qtext)
    index = roman_bm25 if which == "roman" else urdu_bm25
    hits = index.search(qtoks, top_k=TOP_K)
    return det, path, hits


def write_retrieval_stats(path, payload):
    lines = [
        "# R-dev M0 retrieval statistics (frozen dump only)",
        "",
        "Sealed development set **R001–R100**. **No** performance metrics computed.",
        "Do **not** report Hit@5, ExactSource Hit@5, Success@5, P@5, nDCG, or MRR from this step.",
        "",
        "| | |",
        "| --- | --- |",
        "| queries processed | %s |" % payload["n_queries"],
        "| track counts | %s |" % json.dumps(payload["track_counts"], ensure_ascii=False),
        "| detector counts (M0 runtime) | %s |" % json.dumps(payload["detector_counts"], ensure_ascii=False),
        "| retrieval-path counts | %s |" % json.dumps(payload["path_counts"], ensure_ascii=False),
        "| n_hits_returned distribution | %s |" % json.dumps(payload["n_hits_distribution"]),
        "| Top-50 rows | %s |" % payload["n_top50_rows"],
        "| Top-5 rows | %s |" % payload["n_top5_rows"],
        "| queries with n_hits_returned < 5 | %s |" % payload["n_short_lists"],
        "| queries with n_hits_returned = 0 | %s |" % payload["n_empty_lists"],
        "",
        "Queries with fewer than 5 hits: %s"
        % (", ".join(payload["short_query_ids"]) if payload["short_query_ids"] else "none"),
        "",
        "`relevance_label` is empty on all Top-5 rows. Annotation is a later approved step.",
        "",
    ]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    os.makedirs(ART, exist_ok=True)
    checks, queries = preflight()
    if not checks["preflight_pass"]:
        print("STOP: preflight failed. No retrieval.", flush=True)
        print("failed_checks=%s" % checks["failed_checks"], flush=True)
        sys.exit(2)

    fwd = p5.load_roman_dict()
    rev = p5.load_reverse_roman(fwd)
    print("loading corpus...", flush=True)
    df = pd.read_csv(p5.CORPUS, encoding="utf-8-sig")
    if "combined_text" in df.columns:
        texts = df["combined_text"].fillna("").astype(str).tolist()
    else:
        texts = (
            df["Headline"].fillna("").astype(str)
            + " "
            + df["News Text"].fillna("").astype(str)
        ).tolist()
    if len(texts) != EXPECTED_N:
        print("STOP: corpus row count changed after preflight: %s" % len(texts), flush=True)
        sys.exit(2)
    headlines = df["Headline"].fillna("").astype(str)
    news = df["News Text"].fillna("").astype(str) if "News Text" in df.columns else pd.Series([""] * len(df))

    t0 = time.perf_counter()
    urdu_docs, roman_docs = [], []
    for i, text in enumerate(texts):
        utoks = p5.tokenize(text)
        rtoks = [t for t in (p5.romanize_token(t, rev) for t in utoks) if t]
        urdu_docs.append(utoks)
        roman_docs.append(rtoks)
        if (i + 1) % 20000 == 0:
            print("  tokenize %s/%s" % (i + 1, len(texts)), flush=True)
    tokenize_s = time.perf_counter() - t0
    print("tokenize %.1fs" % tokenize_s, flush=True)
    urdu_bm25 = p5.BM25(urdu_docs)
    roman_bm25 = p5.BM25(roman_docs)
    print("indexes ready (M0 / Method D documents unchanged)", flush=True)

    top50_rows = []
    top5_rows = []
    per_query = []
    t_search = time.perf_counter()
    for r in queries:
        q = r["query_text"]
        track = r["track"]
        src = r["source_doc_id"]
        det, path, hits = search_one(q, urdu_bm25, roman_bm25)
        n_hits = len(hits)
        per_query.append({
            "query_id": r["query_id"],
            "track": track,
            "detector_label": det,
            "retrieval_path": path,
            "n_hits_returned": n_hits,
        })
        for rank, (did, score) in enumerate(hits, 1):
            did = int(did)
            rec = {
                "experiment_id": EXPERIMENT_ID,
                "query_id": r["query_id"],
                "query_text": q,
                "track": track,
                "source_doc_id": src,
                "detector_label": det,
                "retrieval_path": path,
                "rank": rank,
                "doc_id": did,
                "bm25_score": float(score),
                "headline": str(headlines[did]),
                "news_text_or_snippet": clip(str(news[did])),
                "n_hits_returned": n_hits,
                "top_k_tier": "top50",
            }
            top50_rows.append(rec)
            if rank <= 5:
                rec5 = dict(rec)
                rec5["top_k_tier"] = "top5"
                rec5["relevance_label"] = ""
                top5_rows.append(rec5)
        print(
            "%s track=%s detector=%s path=%s n_hits=%s"
            % (r["query_id"], track, det, path, n_hits),
            flush=True,
        )
    search_s = time.perf_counter() - t_search

    hits_dist = dict(Counter(int(x["n_hits_returned"]) for x in per_query))
    short_ids = [x["query_id"] for x in per_query if int(x["n_hits_returned"]) < 5]
    empty_ids = [x["query_id"] for x in per_query if int(x["n_hits_returned"]) == 0]

    top50_path = os.path.join(_DIR, "R_TOP50_RETRIEVAL.csv")
    top5_path = os.path.join(_DIR, "R_TOP5_FOR_ANNOTATION.csv")
    top50_fields = [
        "experiment_id", "query_id", "query_text", "track", "source_doc_id",
        "detector_label", "retrieval_path", "rank", "doc_id", "bm25_score",
        "headline", "news_text_or_snippet", "n_hits_returned", "top_k_tier",
    ]
    top5_fields = top50_fields + ["relevance_label"]
    with open(top50_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=top50_fields)
        w.writeheader()
        w.writerows(top50_rows)
    with open(top5_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=top5_fields)
        w.writeheader()
        w.writerows(top5_rows)

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    commit = git_commit()
    top50_sha = sha256_file(top50_path)
    top5_sha = sha256_file(top5_path)

    stats_payload = {
        "n_queries": len(queries),
        "track_counts": dict(Counter(x["track"] for x in per_query)),
        "detector_counts": dict(Counter(x["detector_label"] for x in per_query)),
        "path_counts": dict(Counter(x["retrieval_path"] for x in per_query)),
        "n_hits_distribution": hits_dist,
        "n_top50_rows": len(top50_rows),
        "n_top5_rows": len(top5_rows),
        "n_short_lists": len(short_ids),
        "n_empty_lists": len(empty_ids),
        "short_query_ids": short_ids,
    }
    write_retrieval_stats(os.path.join(_DIR, "R_RETRIEVAL_STATS.md"), stats_payload)

    manifest = {
        "experiment_id": EXPERIMENT_ID,
        "stage": "M0_retrieval_only",
        "official_system": "M0",
        "m0_code_path": "experiments/phase5_roman_urdu/run_phase5.py",
        "timestamp_utc": ts,
        "git_commit": commit,
        "preflight_pass": True,
        "retrieval_pass_count": 1,
        "exactly_one_retrieval_pass": True,
        "queries_r_dev_sha256": checks["queries_r_dev_sha256"],
        "queries_r_dev_sha256_expected": EXPECTED_QUERY_SHA,
        "queries_r_dev_hash_ok": checks["queries_r_dev_hash_ok"],
        "n_queries_requested": EXPECTED_QUERY_COUNT,
        "n_queries_retrieved": len(per_query),
        "corpus_path": checks["corpus_path"],
        "corpus_sha256": checks["corpus_sha256"],
        "corpus_n_docs": EXPECTED_N,
        "dict_path": checks["dict_path"],
        "dict_sha256": checks["dict_sha256"],
        "dict_keys": checks["dict_keys"],
        "bm25_k1": 1.5,
        "bm25_b": 0.75,
        "top_k_internal": TOP_K,
        "top5_extracted": True,
        "routing": checks["routing"],
        "detect_script_function": "experiments/phase5_roman_urdu/run_phase5.py::detect_script",
        "m0_modified": False,
        "module1_applied": False,
        "module2_applied": False,
        "embeddings_used": False,
        "semantic_retrieval_used": False,
        "chroma_used": False,
        "minilm_used": False,
        "metrics_computed": False,
        "qrels_created": False,
        "annotation_started": False,
        "track_counts": stats_payload["track_counts"],
        "detector_counts": stats_payload["detector_counts"],
        "path_counts": stats_payload["path_counts"],
        "n_hits_distribution": hits_dist,
        "n_top50_rows": len(top50_rows),
        "n_top5_rows": len(top5_rows),
        "output_files": {
            "R_TOP50_RETRIEVAL.csv": {
                "path": top50_path,
                "sha256": top50_sha,
                "rows": len(top50_rows),
            },
            "R_TOP5_FOR_ANNOTATION.csv": {
                "path": top5_path,
                "sha256": top5_sha,
                "rows": len(top5_rows),
            },
        },
        "tokenize_seconds": round(tokenize_s, 2),
        "search_seconds": round(search_s, 2),
        "stopped_after_retrieval": True,
    }
    manifest_path = os.path.join(_DIR, "RETRIEVAL_MANIFEST.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print("n_queries=%s top50_rows=%s top5_rows=%s" % (len(per_query), len(top50_rows), len(top5_rows)), flush=True)
    print("R_TOP50 sha256=%s" % top50_sha, flush=True)
    print("R_TOP5 sha256=%s" % top5_sha, flush=True)
    print("R-DEV M0 RETRIEVAL COMPLETE. STOPPED. NO METRICS. NO ANNOTATION.", flush=True)


if __name__ == "__main__":
    main()
