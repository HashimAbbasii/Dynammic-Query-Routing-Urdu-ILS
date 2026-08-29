# -*- coding: utf-8 -*-
"""
Phase 12: frozen M0 retrieval on sealed K001-K040 and U001-U040.

Does not modify M0. Does not load H001-H040. Does not apply M1-M4.
Does not label U. Does not overwrite Phase 9/10/11 files.
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
P9 = os.path.join(ROOT, "experiments", "phase9_heldout_evaluation")
MANIFEST8 = os.path.join(ROOT, "experiments", "phase8_final_freeze", "FINAL_SYSTEM_MANIFEST.json")
ART = os.path.join(_DIR, "artifacts")
EXPERIMENT_ID = "phase12_new_unseen_evaluation"
TOP_K = 50
SNIP = 500
EXPECTED_CORPUS_SHA = "8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231"
EXPECTED_DICT_SHA = "30c3f61a64ec641abbb3acdbc7a8bcaf197f0238f1bf9e76c2c7ce8e590f86a3"
EXPECTED_K_SHA = "124e452693f98baedf510618240c154df68d56b6b7a37ed085a6512c13d13ff6"
EXPECTED_U_SHA = "684fd1e19eddb717f5897d869ef0ca0ed586316c5a7e1d2d23006e0748fc53b9"
EXPECTED_N = 111860
EXPECTED_DICT = 198
K_PATH = os.path.join(_DIR, "queries_k.csv")
U_PATH = os.path.join(_DIR, "queries_u.csv")

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


def load_k():
    rows = []
    with open(K_PATH, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            rows.append(r)
    ids = [r["query_id"] for r in rows]
    if ids != ["K%03d" % i for i in range(1, 41)]:
        raise RuntimeError("K ids not K001-K040 in order: %s" % ids)
    if len(ids) != len(set(ids)):
        raise RuntimeError("duplicate K ids")
    for r in rows:
        if str(r["query_id"]).startswith("H"):
            raise RuntimeError("H id in K file: %s" % r["query_id"])
        sid = int(r["source_doc_id"])
        if sid < 0 or sid > 111859:
            raise RuntimeError("K source_doc_id out of range: %s" % r)
        r["source_doc_id"] = sid
        r["query_text"] = r["query_text"]
    return rows


def load_u():
    with open(U_PATH, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fields = list(reader.fieldnames or [])
        if "source_doc_id" in fields:
            raise RuntimeError("U file must not contain source_doc_id")
        rows = list(reader)
    ids = [r["query_id"] for r in rows]
    if ids != ["U%03d" % i for i in range(1, 41)]:
        raise RuntimeError("U ids not U001-U040 in order: %s" % ids)
    if len(ids) != len(set(ids)):
        raise RuntimeError("duplicate U ids")
    for r in rows:
        if str(r["query_id"]).startswith("H"):
            raise RuntimeError("H id in U file: %s" % r["query_id"])
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

    k_exists = os.path.isfile(K_PATH)
    u_exists = os.path.isfile(U_PATH)
    if not k_exists:
        failed.append("queries_k_missing")
    if not u_exists:
        failed.append("queries_u_missing")

    k_hash = sha256_file(K_PATH) if k_exists else ""
    u_hash = sha256_file(U_PATH) if u_exists else ""
    k_hash_ok = k_hash == EXPECTED_K_SHA
    u_hash_ok = u_hash == EXPECTED_U_SHA
    if not k_hash_ok:
        failed.append("queries_k_sha256_mismatch")
    if not u_hash_ok:
        failed.append("queries_u_sha256_mismatch")

    k_rows, u_rows = [], []
    k_load_ok = u_load_ok = False
    try:
        k_rows = load_k()
        k_load_ok = True
    except Exception as e:
        failed.append("queries_k_invalid")
        notes.append("k_load: %s" % e)
    try:
        u_rows = load_u()
        u_load_ok = True
    except Exception as e:
        failed.append("queries_u_invalid")
        notes.append("u_load: %s" % e)

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

    out_abs = os.path.abspath(_DIR)
    p9_abs = os.path.abspath(P9)
    isolated = out_abs != p9_abs and os.path.commonpath([out_abs, p9_abs]) != p9_abs
    if not isolated:
        failed.append("output_not_isolated_from_phase9")
    if not os.path.isdir(P9):
        notes.append("phase9_dir_missing_but_not_required_for_search")

    # Confirm sealed query texts are used as-is (hash already covers bytes).
    query_text_unchanged = k_hash_ok and u_hash_ok

    ok = len(failed) == 0
    checks = {
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "experiment_id": EXPERIMENT_ID,
        "official_system": "M0",
        "m1_m4_applied": False,
        "h001_h040_loaded": False,
        "phase10c_qrels_loaded": False,
        "heldout_template_loaded": False,
        "phase11_transformations_applied": False,
        "python": sys.version,
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "queries_k_path": K_PATH,
        "queries_u_path": U_PATH,
        "queries_k_exists": k_exists,
        "queries_u_exists": u_exists,
        "queries_k_sha256": k_hash,
        "queries_k_sha256_expected": EXPECTED_K_SHA,
        "queries_k_hash_ok": k_hash_ok,
        "queries_u_sha256": u_hash,
        "queries_u_sha256_expected": EXPECTED_U_SHA,
        "queries_u_hash_ok": u_hash_ok,
        "query_text_unchanged": query_text_unchanged,
        "k_ids_ok": k_load_ok,
        "u_ids_ok": u_load_ok,
        "n_k": len(k_rows),
        "n_u": len(u_rows),
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
        "routing_ok": routing_ok,
        "phase5_code_paths_ok": code_ok,
        "output_dir": out_abs,
        "phase9_dir": p9_abs,
        "output_isolated_from_phase9": isolated,
        "will_overwrite_phase9": False,
        "will_overwrite_phase10b": False,
        "will_overwrite_phase10c": False,
        "will_overwrite_phase11": False,
        "phase8_freeze_intact": True,
        "architecture_unchanged": True,
        "no_test_tuning": True,
        "no_u_relevance_labels": True,
        "failed_checks": failed,
        "notes": notes,
        "preflight_pass": ok,
    }
    with open(os.path.join(ART, "preflight.json"), "w", encoding="utf-8") as f:
        json.dump(checks, f, indent=2)
    print("PREFLIGHT", "PASS" if ok else "FAIL", json.dumps({
        "failed": failed,
        "k_hash_ok": k_hash_ok,
        "u_hash_ok": u_hash_ok,
        "corpus_hash_ok": hash_ok,
        "dict_sha_ok": dict_sha_ok,
        "k1b_ok": k1b_ok,
        "isolated": isolated,
    }), flush=True)
    return checks, k_rows, u_rows


def hit_at(ranks, k):
    n = len(ranks)
    n_hit = sum(1 for r in ranks if r is not None and r <= k)
    return n_hit, n, (n_hit / n) if n else 0.0


def write_k_results(path, payload):
    lines = [
        "# Phase 12 K results — ExactSource known-item (frozen M0)",
        "",
        "New independent known-item evaluation on **K001–K040**.",
        "Does **not** replace Phase 9 development/validation ExactSource Hit@5 = 68/78 = 0.8718.",
        "Does **not** measure human relevance. Do not mix with U.",
        "",
        "## Preflight and freeze",
        "",
        "| | |",
        "| --- | --- |",
        "| preflight | **%s** |" % ("PASS" if payload["preflight_pass"] else "FAIL"),
        "| official system | M0 |",
        "| corpus SHA-256 | `%s` |" % payload["corpus_sha256"],
        "| n_docs | %s |" % payload["n_docs"],
        "| dictionary SHA-256 | `%s` |" % payload["dict_sha256"],
        "| dictionary keys | %s |" % payload["dict_keys"],
        "| BM25 k1 / b | %s / %s |" % (payload["k1"], payload["b"]),
        "| top_k | %s |" % payload["top_k"],
        "| routing | URDU/MIXED → urdu_bm25; ROMAN → roman_bm25_method_D |",
        "| M1–M4 applied | no |",
        "| H001–H040 used | no |",
        "",
        "## Queries",
        "",
        "| | |",
        "| --- | --- |",
        "| n | %s |" % payload["n_queries"],
        "| detector counts | %s |" % json.dumps(payload["detector_counts"], ensure_ascii=False),
        "| retrieval-path counts | %s |" % json.dumps(payload["path_counts"], ensure_ascii=False),
        "| n_hits_returned distribution | %s |" % json.dumps(payload["n_hits_distribution"]),
        "",
        "## ExactSource metrics (primary = Hit@5)",
        "",
        "| Metric | Hits | n | Rate |",
        "| --- | ---: | ---: | ---: |",
        "| ExactSource Hit@1 | %s | %s | %.4f = %.2f%% |" % (
            payload["hit1_num"], payload["n_queries"], payload["hit1"], 100 * payload["hit1"]
        ),
        "| **ExactSource Hit@5** | **%s** | **%s** | **%.4f = %.2f%%** |" % (
            payload["hit5_num"], payload["n_queries"], payload["hit5"], 100 * payload["hit5"]
        ),
        "| ExactSource Hit@10 | %s | %s | %.4f = %.2f%% |" % (
            payload["hit10_num"], payload["n_queries"], payload["hit10"], 100 * payload["hit10"]
        ),
        "| ExactSource Hit@50 | %s | %s | %.4f = %.2f%% |" % (
            payload["hit50_num"], payload["n_queries"], payload["hit50"], 100 * payload["hit50"]
        ),
        "",
        "Valid claim: “On the sealed known-item set K001–K040, frozen M0 ExactSource Hit@5 = %s/40.”"
        % payload["hit5_num"],
        "",
        "Invalid: treating this number as human Success@5, as unseen H001–H040 accuracy, or as a replacement for 68/78.",
        "",
        "## Per-query source rank",
        "",
        "| query_id | detector | path | n_hits | source_doc_id | source_rank | Hit@5 |",
        "| --- | --- | --- | ---: | ---: | ---: | --- |",
    ]
    for r in payload["per_query"]:
        rk = r["source_rank"]
        rk_s = str(rk) if rk < 999 else "not_in_top50"
        lines.append(
            "| %s | %s | %s | %s | %s | %s | %s |"
            % (
                r["query_id"],
                r["detector_label"],
                r["retrieval_path"],
                r["n_hits_returned"],
                r["source_doc_id"],
                rk_s,
                "yes" if rk <= 5 else "no",
            )
        )
    miss5 = [r["query_id"] for r in payload["per_query"] if r["source_rank"] > 5]
    miss50 = [r["query_id"] for r in payload["per_query"] if r["source_rank"] >= 999]
    lines.extend([
        "",
        "## Misses",
        "",
        "Not in Top-5 (Hit@5 misses): %s" % (", ".join(miss5) if miss5 else "none"),
        "",
        "Not in Top-50: %s" % (", ".join(miss50) if miss50 else "none"),
        "",
        "This list is complete. Successful queries are not singled out.",
        "",
        "## Stop",
        "",
        "K retrieval scored. Do not tune M0 on these misses. Do not start U annotation in this step.",
        "",
    ])
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def write_u_stats(path, payload):
    lines = [
        "# Phase 12 U retrieval statistics (frozen M0 dump)",
        "",
        "Naturalistic sealed set **U001–U040**. **No** gold documents. **No** human labels.",
        "Do **not** report Success@5, P@5, nDCG, MRR, or any guessed relevance score.",
        "",
        "| | |",
        "| --- | --- |",
        "| queries processed | %s |" % payload["n_queries"],
        "| detector counts | %s |" % json.dumps(payload["detector_counts"], ensure_ascii=False),
        "| retrieval-path counts | %s |" % json.dumps(payload["path_counts"], ensure_ascii=False),
        "| n_hits_returned distribution | %s |" % json.dumps(payload["n_hits_distribution"]),
        "| Top-50 rows | %s |" % payload["n_top50_rows"],
        "| Top-5 annotation rows | %s |" % payload["n_top5_rows"],
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


def search_one(qtext, urdu_bm25, roman_bm25):
    det, path, which, qtoks = route_m0(qtext)
    index = roman_bm25 if which == "roman" else urdu_bm25
    hits = index.search(qtoks, top_k=TOP_K)
    return det, path, hits


def main():
    os.makedirs(ART, exist_ok=True)
    checks, k_queries, u_queries = preflight()
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

    k50_rows = []
    k_per = []
    t_search = time.perf_counter()
    for r in k_queries:
        q = r["query_text"]
        src = r["source_doc_id"]
        det, path, hits = search_one(q, urdu_bm25, roman_bm25)
        n_hits = len(hits)
        src_rank = p5.rank_of(hits, src)
        k_per.append({
            "query_id": r["query_id"],
            "query_text": q,
            "source_doc_id": src,
            "detector_label": det,
            "retrieval_path": path,
            "n_hits_returned": n_hits,
            "source_rank": src_rank,
        })
        for rank, (did, score) in enumerate(hits, 1):
            k50_rows.append({
                "experiment_id": EXPERIMENT_ID,
                "query_id": r["query_id"],
                "query_text": q,
                "source_doc_id": src,
                "detector_label": det,
                "retrieval_path": path,
                "rank": rank,
                "doc_id": int(did),
                "bm25_score": float(score),
                "n_hits_returned": n_hits,
            })
        print(
            "%s detector=%s path=%s n_hits=%s source_rank=%s"
            % (r["query_id"], det, path, n_hits, src_rank if src_rank < 999 else "miss50"),
            flush=True,
        )

    u50_rows = []
    u5_rows = []
    u_per = []
    for r in u_queries:
        q = r["query_text"]
        det, path, hits = search_one(q, urdu_bm25, roman_bm25)
        n_hits = len(hits)
        u_per.append({
            "query_id": r["query_id"],
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
                "detector_label": det,
                "retrieval_path": path,
                "rank": rank,
                "doc_id": did,
                "bm25_score": float(score),
                "headline": str(headlines[did]),
                "news_text_or_snippet": clip(str(news[did])),
                "n_hits_returned": n_hits,
            }
            u50_rows.append(rec)
            if rank <= 5:
                rec5 = dict(rec)
                rec5["relevance_label"] = ""
                u5_rows.append(rec5)
        print(
            "%s detector=%s path=%s n_hits=%s"
            % (r["query_id"], det, path, n_hits),
            flush=True,
        )
    search_s = time.perf_counter() - t_search

    ranks = [x["source_rank"] for x in k_per]
    h1n, _, h1 = hit_at(ranks, 1)
    h5n, _, h5 = hit_at(ranks, 5)
    h10n, _, h10 = hit_at(ranks, 10)
    h50n, _, h50 = hit_at(ranks, 50)

    k_hits_dist = dict(Counter(int(x["n_hits_returned"]) for x in k_per))
    u_hits_dist = dict(Counter(int(x["n_hits_returned"]) for x in u_per))
    u_short = [x["query_id"] for x in u_per if int(x["n_hits_returned"]) < 5]
    u_empty = [x["query_id"] for x in u_per if int(x["n_hits_returned"]) == 0]

    k50_path = os.path.join(_DIR, "K_TOP50_RETRIEVAL.csv")
    u50_path = os.path.join(_DIR, "U_TOP50_RETRIEVAL.csv")
    u5_path = os.path.join(_DIR, "U_TOP5_FOR_ANNOTATION.csv")
    k_fields = [
        "experiment_id", "query_id", "query_text", "source_doc_id",
        "detector_label", "retrieval_path", "rank", "doc_id", "bm25_score",
        "n_hits_returned",
    ]
    u50_fields = [
        "experiment_id", "query_id", "query_text", "detector_label",
        "retrieval_path", "rank", "doc_id", "bm25_score", "headline",
        "news_text_or_snippet", "n_hits_returned",
    ]
    u5_fields = u50_fields + ["relevance_label"]
    with open(k50_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=k_fields)
        w.writeheader()
        w.writerows(k50_rows)
    with open(u50_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=u50_fields)
        w.writeheader()
        w.writerows(u50_rows)
    with open(u5_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=u5_fields)
        w.writeheader()
        w.writerows(u5_rows)

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    commit = git_commit()
    k_payload = {
        "preflight_pass": True,
        "corpus_sha256": checks["corpus_sha256"],
        "n_docs": EXPECTED_N,
        "dict_sha256": checks["dict_sha256"],
        "dict_keys": checks["dict_keys"],
        "k1": 1.5,
        "b": 0.75,
        "top_k": TOP_K,
        "n_queries": 40,
        "detector_counts": dict(Counter(x["detector_label"] for x in k_per)),
        "path_counts": dict(Counter(x["retrieval_path"] for x in k_per)),
        "n_hits_distribution": k_hits_dist,
        "hit1_num": h1n,
        "hit1": h1,
        "hit5_num": h5n,
        "hit5": h5,
        "hit10_num": h10n,
        "hit10": h10,
        "hit50_num": h50n,
        "hit50": h50,
        "per_query": k_per,
    }
    write_k_results(os.path.join(_DIR, "K_RESULTS.md"), k_payload)

    u_payload = {
        "n_queries": 40,
        "detector_counts": dict(Counter(x["detector_label"] for x in u_per)),
        "path_counts": dict(Counter(x["retrieval_path"] for x in u_per)),
        "n_hits_distribution": u_hits_dist,
        "n_top50_rows": len(u50_rows),
        "n_top5_rows": len(u5_rows),
        "n_short_lists": len(u_short),
        "n_empty_lists": len(u_empty),
        "short_query_ids": u_short,
    }
    write_u_stats(os.path.join(_DIR, "U_RETRIEVAL_STATS.md"), u_payload)

    manifest = {
        "experiment_id": EXPERIMENT_ID,
        "official_system": "M0",
        "replaces_phase9": False,
        "timestamp_utc": ts,
        "git_commit": commit,
        "preflight_pass": True,
        "corpus_sha256": checks["corpus_sha256"],
        "dict_sha256": checks["dict_sha256"],
        "dict_keys": checks["dict_keys"],
        "n_docs": EXPECTED_N,
        "bm25_k1": 1.5,
        "bm25_b": 0.75,
        "top_k": TOP_K,
        "m0_modified": False,
        "m1_m4_applied": False,
        "h001_h040_used": False,
        "phase10c_qrels_used": False,
        "heldout_template_used": False,
        "queries_k_sha256": checks["queries_k_sha256"],
        "queries_u_sha256": checks["queries_u_sha256"],
        "tokenize_seconds": round(tokenize_s, 2),
        "search_seconds": round(search_s, 2),
        "k_exactsource_hit@1": {"hits": h1n, "n": 40, "rate": round(h1, 4)},
        "k_exactsource_hit@5": {"hits": h5n, "n": 40, "rate": round(h5, 4)},
        "k_exactsource_hit@10": {"hits": h10n, "n": 40, "rate": round(h10, 4)},
        "k_exactsource_hit@50": {"hits": h50n, "n": 40, "rate": round(h50, 4)},
        "k_detector_counts": k_payload["detector_counts"],
        "k_path_counts": k_payload["path_counts"],
        "u_detector_counts": u_payload["detector_counts"],
        "u_path_counts": u_payload["path_counts"],
        "u_n_top50_rows": len(u50_rows),
        "u_n_top5_rows": len(u5_rows),
        "u_n_short_lists": len(u_short),
        "u_relevance_labels_written": False,
        "phase9_dev_val_hit@5_unchanged": "68/78=0.8718",
        "stopped_after_retrieval": True,
        "annotation_started": False,
    }
    with open(os.path.join(ART, "run_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print("K ExactSource Hit@5 = %s/40 = %.4f" % (h5n, h5), flush=True)
    print("U top50_rows=%s top5_rows=%s short=%s" % (len(u50_rows), len(u5_rows), u_short), flush=True)
    print("PHASE 12 RETRIEVAL COMPLETE. STOPPED. NO ANNOTATION.", flush=True)


if __name__ == "__main__":
    main()
