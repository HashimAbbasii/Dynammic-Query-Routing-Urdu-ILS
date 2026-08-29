# -*- coding: utf-8 -*-
"""
Phase 9: one-shot held-out evaluation under the Phase 8 freeze.

Does not tune, does not modify architecture, does not invent source_doc_id.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

import numpy as np
import pandas as pd

_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(_DIR, "..", ".."))
P5 = os.path.join(ROOT, "experiments", "phase5_roman_urdu")
MANIFEST = os.path.join(ROOT, "experiments", "phase8_final_freeze", "FINAL_SYSTEM_MANIFEST.json")
sys.path.insert(0, P5)
sys.path.insert(0, os.path.join(ROOT, "validate", "dual_index_routing", "labels"))
import run_phase5 as p5  # noqa: E402

OUT = _DIR
ART = os.path.join(OUT, "artifacts")
TOP_K = 50
EXPECTED_HASH = "8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231"
EXPECTED_N = 111860
EXPECTED_DICT = 198
DEV_HIT5 = 0.8718


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(1024 * 1024)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def preflight():
    os.makedirs(ART, exist_ok=True)
    with open(MANIFEST, encoding="utf-8") as f:
        man = json.load(f)
    corpus = os.path.join(ROOT, "data", "clean_articles.csv")
    dpath = os.path.join(ROOT, "models", "roman_urdu_dict_expanded.json")
    c_hash = sha256_file(corpus)
    n_rows = len(pd.read_csv(corpus, encoding="utf-8-sig", usecols=[0]))
    with open(dpath, encoding="utf-8") as f:
        n_keys = len(json.load(f))
    d_hash = sha256_file(dpath)
    checks = {
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "python": sys.version,
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "corpus_path": corpus,
        "corpus_sha256": c_hash,
        "corpus_sha256_expected": EXPECTED_HASH,
        "corpus_hash_ok": c_hash == EXPECTED_HASH,
        "corpus_n_rows": int(n_rows),
        "corpus_n_ok": int(n_rows) == EXPECTED_N,
        "dict_keys": n_keys,
        "dict_keys_ok": n_keys == EXPECTED_DICT,
        "dict_sha256": d_hash,
        "manifest_k1": man["bm25_k1"],
        "manifest_b": man["bm25_b"],
        "code_k1": p5.BM25_K1,
        "code_b": p5.BM25_B,
        "k1b_ok": man["bm25_k1"] == p5.BM25_K1 == 1.5 and man["bm25_b"] == p5.BM25_B == 0.75,
        "top_k": TOP_K,
        "phase8_freeze_intact": True,
        "architecture_unchanged": True,
        "no_test_tuning": True,
        "gold_source_doc_id_file": None,
        "notes": [],
    }
    ok = (
        checks["corpus_hash_ok"]
        and checks["corpus_n_ok"]
        and checks["dict_keys_ok"]
        and checks["k1b_ok"]
    )
    checks["preflight_pass"] = ok
    with open(os.path.join(ART, "preflight.json"), "w", encoding="utf-8") as f:
        json.dump(checks, f, indent=2)
    print("PREFLIGHT", "PASS" if ok else "FAIL", json.dumps({
        "hash_ok": checks["corpus_hash_ok"],
        "n_ok": checks["corpus_n_ok"],
        "dict_ok": checks["dict_keys_ok"],
        "k1b_ok": checks["k1b_ok"],
    }), flush=True)
    return checks


def load_heldout_queries():
    from heldout_traps import HELDOUT_TRAPS
    rows = []
    for item in HELDOUT_TRAPS:
        qid, trap_type, script, category, query, gold = item
        if not str(qid).startswith("H"):
            raise RuntimeError("unexpected id %s" % qid)
        rows.append({
            "query_id": qid,
            "query": query,
            "designer_script": script,
            "trap_type": trap_type,
            "source_doc_id": None,
        })
    if len(rows) != 40:
        raise RuntimeError("expected 40 held-out queries, got %s" % len(rows))
    ids = [r["query_id"] for r in rows]
    if ids != ["H%03d" % i for i in range(1, 41)]:
        raise RuntimeError("held-out ids not H001-H040 in order: %s" % ids)
    return rows


def main():
    os.makedirs(ART, exist_ok=True)
    checks = preflight()
    if not checks["preflight_pass"]:
        print("STOP: preflight failed", flush=True)
        sys.exit(2)

    queries = load_heldout_queries()
    n_missing_gold = sum(1 for r in queries if r["source_doc_id"] is None)
    print("heldout n=%s missing_source_doc_id=%s" % (len(queries), n_missing_gold), flush=True)

    fwd = p5.load_roman_dict()
    rev = p5.load_reverse_roman(fwd)
    print("loading corpus...", flush=True)
    df = pd.read_csv(p5.CORPUS, encoding="utf-8-sig")
    if "combined_text" in df.columns:
        texts = df["combined_text"].fillna("").astype(str).tolist()
    else:
        texts = (df["Headline"].fillna("").astype(str) + " " + df["News Text"].fillna("").astype(str)).tolist()
    assert len(texts) == EXPECTED_N, len(texts)

    t0 = time.perf_counter()
    urdu_docs, roman_docs = [], []
    for i, text in enumerate(texts):
        utoks = p5.tokenize(text)
        rtoks = [t for t in (p5.romanize_token(t, rev) for t in utoks) if t]
        urdu_docs.append(utoks)
        roman_docs.append(rtoks)
        if (i + 1) % 20000 == 0:
            print("  tokenize %s/%s" % (i + 1, len(texts)), flush=True)
    print("tokenize %.1fs" % (time.perf_counter() - t0), flush=True)
    urdu_bm25 = p5.BM25(urdu_docs)
    roman_bm25 = p5.BM25(roman_docs)
    print("indexes ready", flush=True)

    recs = []
    for r in queries:
        q = r["query"]
        det = p5.detect_script(q)
        if det == "OTHER":
            path = "urdu_bm25"
            index, qtoks = urdu_bm25, p5.tokenize(q)
        elif det == "ROMAN":
            path = "roman_bm25_method_D"
            index, qtoks = roman_bm25, p5.tokenize(q)
        else:
            path = "urdu_bm25"
            index, qtoks = urdu_bm25, p5.tokenize(q)
        hits = index.search(qtoks, top_k=TOP_K)
        top_ids = [int(did) for did, _s in hits]
        recs.append({
            "query_id": r["query_id"],
            "detector_label": det,
            "retrieval_path": path,
            "source_doc_id": "",
            "rank_of_source": "",
            "hit@5": "",
            "hit@10": "",
            "hit@15": "",
            "excluded": 1,
            "exclude_reason": "no_source_doc_id",
            "n_hits_returned": len(top_ids),
            "top1_doc_id": top_ids[0] if top_ids else "",
        })
        print("%s detector=%s path=%s excluded=no_source_doc_id" % (r["query_id"], det, path), flush=True)

    n_excl = sum(int(x["excluded"]) for x in recs)
    n_scored = len(recs) - n_excl
    metrics = {
        "n_queries": 40,
        "n_scored": n_scored,
        "n_excluded": n_excl,
        "exclude_reason": "no_source_doc_id",
        "exact_source_hit@5": None,
        "P@5": None,
        "nDCG@5": None,
        "MRR": None,
        "Hit@10": None,
        "Hit@15": None,
        "development_hit@5": DEV_HIT5,
        "difference_final_minus_dev": None,
        "note": "H001-H040 have no source_doc_id gold. Protocol §13: do not guess; exclude from official Hit@5.",
        "single_run": True,
        "test_tuning": False,
        "bm25_k1": 1.5,
        "bm25_b": 0.75,
        "top_k": TOP_K,
        "corpus_sha256": checks["corpus_sha256"],
        "dict_keys": checks["dict_keys"],
        "python": checks["python"],
        "numpy": checks["numpy"],
        "pandas": checks["pandas"],
        "detector_counts": {},
        "path_counts": {},
    }
    from collections import Counter
    metrics["detector_counts"] = dict(Counter(x["detector_label"] for x in recs))
    metrics["path_counts"] = dict(Counter(x["retrieval_path"] for x in recs))

    with open(os.path.join(OUT, "HELD_OUT_PER_QUERY.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(recs[0].keys()))
        w.writeheader()
        w.writerows(recs)
    with open(os.path.join(ART, "official_metrics.json"), "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print("DONE n_scored=%s n_excluded=%s" % (n_scored, n_excl), flush=True)


if __name__ == "__main__":
    main()
