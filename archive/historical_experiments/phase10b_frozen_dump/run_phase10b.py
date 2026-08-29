# -*- coding: utf-8 -*-
"""
Phase 10B: frozen-system retrieval dump on H001-H040.

Diagnostic replay. Does not replace Phase 9. Does not score Hit@5.
Does not label relevance. Does not tune. Does not change architecture.
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
P9_CSV = os.path.join(P9, "HELD_OUT_PER_QUERY.csv")
P9_RUNNER = os.path.join(P9, "run_phase9.py")
MANIFEST8 = os.path.join(ROOT, "experiments", "phase8_final_freeze", "FINAL_SYSTEM_MANIFEST.json")
PHASE10A_CSV = os.path.join(ROOT, "artifacts", "phase10", "HELD_OUT_RETRIEVAL_DETAILS.csv")
LABELS = os.path.join(ROOT, "validate", "dual_index_routing", "labels")
ART = os.path.join(_DIR, "artifacts")
EXPERIMENT_ID = "phase10b_frozen_dump"
TOP_K = 50
EXPECTED_HASH = "8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231"
EXPECTED_N = 111860
EXPECTED_DICT = 198
SNIP = 500

sys.path.insert(0, P5)
sys.path.insert(0, LABELS)
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
        })
    if len(rows) != 40:
        raise RuntimeError("expected 40 held-out queries, got %s" % len(rows))
    ids = [r["query_id"] for r in rows]
    if ids != ["H%03d" % i for i in range(1, 41)]:
        raise RuntimeError("held-out ids not H001-H040 in order: %s" % ids)
    return rows


def preflight():
    os.makedirs(ART, exist_ok=True)
    failed = []
    notes = []

    corpus = os.path.join(ROOT, "data", "clean_articles.csv")
    dpath = os.path.join(ROOT, "models", "roman_urdu_dict_expanded.json")

    corpus_exists = os.path.isfile(corpus)
    if not corpus_exists:
        failed.append("corpus_missing")

    c_hash = sha256_file(corpus) if corpus_exists else ""
    n_rows = int(len(pd.read_csv(corpus, encoding="utf-8-sig", usecols=[0]))) if corpus_exists else 0

    dict_exists = os.path.isfile(dpath)
    if not dict_exists:
        failed.append("dictionary_missing")
    n_keys = 0
    d_hash = ""
    if dict_exists:
        with open(dpath, encoding="utf-8") as f:
            n_keys = len(json.load(f))
        d_hash = sha256_file(dpath)

    man = {}
    if os.path.isfile(MANIFEST8):
        with open(MANIFEST8, encoding="utf-8") as f:
            man = json.load(f)
    else:
        failed.append("phase8_manifest_missing")

    hash_ok = c_hash == EXPECTED_HASH
    n_ok = n_rows == EXPECTED_N
    dict_ok = n_keys == EXPECTED_DICT
    k1b_ok = (
        man.get("bm25_k1") == p5.BM25_K1 == 1.5
        and man.get("bm25_b") == p5.BM25_B == 0.75
    )
    topk_ok = TOP_K == 50 == getattr(p5, "TOP_K", None) == man.get("top_k", 50)

    if not hash_ok:
        failed.append("corpus_sha256_mismatch")
    if not n_ok:
        failed.append("corpus_n_docs_mismatch")
    if not dict_ok:
        failed.append("dictionary_key_count_mismatch")
    if not k1b_ok:
        failed.append("bm25_k1_b_mismatch")
    if not topk_ok:
        failed.append("top_k_mismatch")

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
    if not os.path.isfile(P9_RUNNER):
        failed.append("phase9_runner_missing")
    if not os.path.isfile(P9_CSV):
        failed.append("phase9_per_query_csv_missing")

    query_ok = False
    query_err = ""
    try:
        qrows = load_heldout_queries()
        query_ok = len(qrows) == 40
    except Exception as e:
        query_err = str(e)
        qrows = []
    if not query_ok:
        failed.append("heldout_traps_unavailable")
        notes.append(query_err)

    out_abs = os.path.abspath(_DIR)
    p9_abs = os.path.abspath(P9)
    isolated = out_abs != p9_abs and os.path.commonpath([out_abs, p9_abs]) != p9_abs
    if not isolated:
        failed.append("output_not_isolated_from_phase9")

    phase10a_protected = os.path.abspath(PHASE10A_CSV) != os.path.abspath(
        os.path.join(_DIR, "HELD_OUT_RETRIEVAL_DETAILS.csv")
    )
    if not phase10a_protected:
        failed.append("would_overwrite_phase10a")
    if not os.path.isfile(PHASE10A_CSV):
        notes.append("phase10a_csv_missing_but_not_required_for_dump")

    writes_phase9 = False
    if writes_phase9:
        failed.append("would_write_phase9")

    ok = len(failed) == 0
    checks = {
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "experiment_id": EXPERIMENT_ID,
        "replaces_phase9": False,
        "python": sys.version,
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "corpus_path": corpus,
        "corpus_exists": corpus_exists,
        "corpus_sha256": c_hash,
        "corpus_sha256_expected": EXPECTED_HASH,
        "corpus_hash_ok": hash_ok,
        "corpus_n_rows": n_rows,
        "corpus_n_ok": n_ok,
        "dict_path": dpath,
        "dict_keys": n_keys,
        "dict_keys_ok": dict_ok,
        "dict_sha256": d_hash,
        "manifest_k1": man.get("bm25_k1"),
        "manifest_b": man.get("bm25_b"),
        "code_k1": p5.BM25_K1,
        "code_b": p5.BM25_B,
        "k1b_ok": k1b_ok,
        "top_k": TOP_K,
        "topk_ok": topk_ok,
        "phase5_code_paths_ok": code_ok,
        "phase9_runner_exists": os.path.isfile(P9_RUNNER),
        "phase9_csv_exists": os.path.isfile(P9_CSV),
        "heldout_traps_ok": query_ok,
        "n_heldout_queries": len(qrows) if query_ok else 0,
        "output_dir": out_abs,
        "phase9_dir": p9_abs,
        "output_isolated_from_phase9": isolated,
        "will_overwrite_phase9": False,
        "will_overwrite_phase10a": False,
        "phase10a_csv": PHASE10A_CSV,
        "phase8_freeze_intact": True,
        "architecture_unchanged": True,
        "no_test_tuning": True,
        "no_ir_quality_metrics": True,
        "no_relevance_labels": True,
        "failed_checks": failed,
        "notes": notes,
        "preflight_pass": ok,
    }
    with open(os.path.join(ART, "preflight.json"), "w", encoding="utf-8") as f:
        json.dump(checks, f, indent=2)
    print("PREFLIGHT", "PASS" if ok else "FAIL", json.dumps({
        "failed": failed,
        "hash_ok": hash_ok,
        "n_ok": n_ok,
        "dict_ok": dict_ok,
        "k1b_ok": k1b_ok,
        "isolated": isolated,
    }), flush=True)
    return checks, qrows if query_ok else []


def write_results_md(path, payload):
    lines = [
        "# PHASE 10B RESULTS — frozen-system retrieval dump",
        "",
        "Diagnostic dump only. **Not** a Phase 9 rewrite. **Not** an ExactSource Hit@5 evaluation.",
        "No A/B/C/D/E labels. No P@5 / Success@5 / nDCG@5. H001–H040 official Hit@5 remains **undefined**.",
        "",
        "## Experiment",
        "",
        "| | |",
        "| --- | --- |",
        "| experiment_id | `%s` |" % payload["experiment_id"],
        "| replaces_phase9 | no |",
        "| queries | H001–H040 (n=%s) |" % payload["n_queries"],
        "| corpus SHA-256 | `%s` |" % payload["corpus_sha256"],
        "| n_docs | %s |" % payload["n_docs"],
        "| dictionary keys | %s |" % payload["dict_keys"],
        "| BM25 k1 / b | %s / %s |" % (payload["k1"], payload["b"]),
        "| top_k | %s |" % payload["top_k"],
        "| Python | %s |" % payload["python_short"],
        "| NumPy | %s |" % payload["numpy"],
        "| pandas | %s |" % payload["pandas"],
        "| git commit | %s |" % (payload["git_commit"] or "unavailable"),
        "| timestamp UTC | %s |" % payload["timestamp_utc"],
        "",
        "## Preflight",
        "",
        "Preflight **%s**. Retrieval ran only after a pass." % (
            "PASS" if payload["preflight_pass"] else "FAIL"
        ),
        "",
        "## Detector and path counts",
        "",
        "Detector: %s" % json.dumps(payload["detector_counts"], ensure_ascii=False),
        "",
        "Path: %s" % json.dumps(payload["path_counts"], ensure_ascii=False),
        "",
        "## Hits returned",
        "",
        "| | |",
        "| --- | --- |",
        "| queries processed | %s |" % payload["n_queries"],
        "| total retrieved rows (Top-50 dump) | %s |" % payload["n_top50_rows"],
        "| Top-5 annotation rows | %s |" % payload["n_top5_rows"],
        "| queries with n_hits_returned < 5 | %s |" % payload["n_short_lists"],
        "",
        "n_hits_returned distribution: %s" % json.dumps(payload["n_hits_distribution"]),
        "",
        "Queries with fewer than 5 hits: %s" % (
            ", ".join(payload["short_query_ids"]) if payload["short_query_ids"] else "none"
        ),
        "",
        "## Rank-1 vs Phase 9",
        "",
        "| | |",
        "| --- | --- |",
        "| match | %s / %s |" % (payload["n_rank1_match"], payload["n_queries"]),
        "| mismatch | %s |" % payload["n_rank1_mismatch"],
        "",
    ]
    if payload["n_rank1_mismatch"] == 0:
        lines.append("Rank-1 replay identity is **verified** (40/40).")
        lines.append("")
        lines.append(
            "This does **not** prove that ranks 2–50 equal the discarded Phase 9 lists. "
            "It confirms that the frozen replay’s first hit matches the only rank Phase 9 saved."
        )
    else:
        lines.append("Rank-1 mismatches (not rerun; not corrected):")
        lines.append("")
        for m in payload["mismatches"]:
            lines.append(
                "- %s: Phase 9 `%s` vs 10B `%s` (10B score=%s). %s"
                % (
                    m["query_id"],
                    m["phase9_top1_doc_id"],
                    m["phase10b_top1_doc_id"],
                    m["phase10b_bm25_score"],
                    m["mismatch_note"],
                )
            )
        lines.append("")
        lines.append("Phase 9 is **not** declared invalid. 10B lists are the diagnostic dump.")
    lines.extend([
        "",
        "## Artifacts",
        "",
        "- `experiments/phase10b_frozen_dump/artifacts/preflight.json`",
        "- `experiments/phase10b_frozen_dump/artifacts/run_manifest.json`",
        "- `experiments/phase10b_frozen_dump/TOP50_RETRIEVAL.csv`",
        "- `experiments/phase10b_frozen_dump/TOP5_FOR_ANNOTATION.csv`",
        "- `experiments/phase10b_frozen_dump/RANK1_VS_PHASE9.csv`",
        "",
        "Phase 9 files were not written. Phase 10A `HELD_OUT_RETRIEVAL_DETAILS.csv` was not overwritten.",
        "",
        "## Explicitly not reported",
        "",
        "H001–H040 Hit@5, P@5, Success@5, nDCG@5, MRR, human relevance, ~80%, A/B/C/D/E labels.",
        "",
        "Development ExactSource Hit@5 on n=78 remains **0.8718**. That number is not a held-out H score.",
        "",
        "## Stop",
        "",
        "Phase 10B complete. Do not start Phase 10C in this run. Do not tune on H001–H040.",
        "",
    ])
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
    print("indexes ready", flush=True)

    top50_rows = []
    top5_rows = []
    per_query = []
    t_search = time.perf_counter()
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
        n_hits = len(hits)
        per_query.append({
            "query_id": r["query_id"],
            "query_text": q,
            "detector_label": det,
            "retrieval_path": path,
            "n_hits_returned": n_hits,
            "top1_doc_id": int(hits[0][0]) if hits else "",
            "top1_score": float(hits[0][1]) if hits else "",
        })
        for rank, (did, score) in enumerate(hits, 1):
            did = int(did)
            score = float(score)
            rec50 = {
                "experiment_id": EXPERIMENT_ID,
                "query_id": r["query_id"],
                "query_text": q,
                "detector_label": det,
                "retrieval_path": path,
                "rank": rank,
                "doc_id": did,
                "bm25_score": score,
                "n_hits_returned": n_hits,
            }
            top50_rows.append(rec50)
            if rank <= 5:
                top5_rows.append({
                    "experiment_id": EXPERIMENT_ID,
                    "query_id": r["query_id"],
                    "query_text": q,
                    "detector_label": det,
                    "retrieval_path": path,
                    "rank": rank,
                    "doc_id": did,
                    "bm25_score": score,
                    "headline": str(headlines[did]),
                    "news_text_or_snippet": clip(str(news[did])),
                    "n_hits_returned": n_hits,
                    "relevance_label": "",
                })
        print(
            "%s detector=%s path=%s n_hits=%s"
            % (r["query_id"], det, path, n_hits),
            flush=True,
        )
    search_s = time.perf_counter() - t_search

    p9_map = {}
    with open(P9_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            p9_map[row["query_id"]] = row

    cmp_rows = []
    mismatches = []
    n_match = 0
    for pq in per_query:
        qid = pq["query_id"]
        p9 = p9_map.get(qid, {})
        p9_id = p9.get("top1_doc_id", "")
        b_id = "" if pq["top1_doc_id"] == "" else str(int(pq["top1_doc_id"]))
        p9_id_s = str(p9_id).strip()
        match = p9_id_s != "" and b_id != "" and int(p9_id_s) == int(b_id)
        if match:
            n_match += 1
            note = ""
        else:
            note = (
                "Replay rank-1 differs from the saved Phase 9 top1_doc_id. "
                "No rerun. No preferred list chosen. Possible argpartition/tie order; "
                "Phase 9 scores were not saved so score-equality cannot be verified."
            )
            mismatches.append({
                "query_id": qid,
                "phase9_top1_doc_id": p9_id_s,
                "phase10b_top1_doc_id": b_id,
                "phase10b_bm25_score": pq["top1_score"],
                "mismatch_note": note,
            })
        cmp_rows.append({
            "query_id": qid,
            "phase9_top1_doc_id": p9_id_s,
            "phase10b_top1_doc_id": b_id,
            "phase10b_bm25_score": pq["top1_score"],
            "phase9_score_available": 0,
            "match": int(match),
            "n_hits_returned_phase9": p9.get("n_hits_returned", ""),
            "n_hits_returned_phase10b": pq["n_hits_returned"],
            "detector_label": pq["detector_label"],
            "retrieval_path": pq["retrieval_path"],
            "mismatch_note": note,
        })

    n_mismatch = len(per_query) - n_match
    n_hits_dist = dict(Counter(int(x["n_hits_returned"]) for x in per_query))
    short_ids = [x["query_id"] for x in per_query if int(x["n_hits_returned"]) < 5]

    top50_path = os.path.join(_DIR, "TOP50_RETRIEVAL.csv")
    top5_path = os.path.join(_DIR, "TOP5_FOR_ANNOTATION.csv")
    cmp_path = os.path.join(_DIR, "RANK1_VS_PHASE9.csv")
    with open(top50_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(top50_rows[0].keys()))
        w.writeheader()
        w.writerows(top50_rows)
    with open(top5_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(top5_rows[0].keys()))
        w.writeheader()
        w.writerows(top5_rows)
    with open(cmp_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(cmp_rows[0].keys()))
        w.writeheader()
        w.writerows(cmp_rows)

    py_short = sys.version.split()[0]
    commit = git_commit()
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    det_counts = dict(Counter(x["detector_label"] for x in per_query))
    path_counts = dict(Counter(x["retrieval_path"] for x in per_query))

    run_manifest = {
        "experiment_id": EXPERIMENT_ID,
        "replaces_phase9": False,
        "purpose": "frozen_system_retrieval_dump",
        "timestamp_utc": ts,
        "git_commit": commit,
        "corpus_path": "data/clean_articles.csv",
        "corpus_sha256": checks["corpus_sha256"],
        "n_docs": EXPECTED_N,
        "dict_keys": EXPECTED_DICT,
        "dict_sha256": checks["dict_sha256"],
        "bm25_k1": 1.5,
        "bm25_b": 0.75,
        "top_k": TOP_K,
        "code_entry_bm25": "experiments/phase5_roman_urdu/run_phase5.py::BM25",
        "code_entry_detector": "experiments/phase5_roman_urdu/run_phase5.py::detect_script",
        "code_entry_romanizer": "experiments/phase5_roman_urdu/run_phase5.py::romanize_token",
        "query_source": "validate/dual_index_routing/labels/heldout_traps.py::HELDOUT_TRAPS.query",
        "python": checks["python"],
        "numpy": checks["numpy"],
        "pandas": checks["pandas"],
        "tokenize_seconds": round(tokenize_s, 3),
        "search_seconds": round(search_s, 3),
        "n_queries": len(per_query),
        "n_top50_rows": len(top50_rows),
        "n_top5_rows": len(top5_rows),
        "detector_counts": det_counts,
        "path_counts": path_counts,
        "n_rank1_match_vs_phase9": n_match,
        "n_rank1_mismatch_vs_phase9": n_mismatch,
        "ir_quality_metrics_computed": False,
        "relevance_labels_assigned": False,
        "phase9_files_modified": False,
        "phase10a_file_modified": False,
    }
    with open(os.path.join(ART, "run_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(run_manifest, f, indent=2)

    write_results_md(
        os.path.join(_DIR, "PHASE10B_RESULTS.md"),
        {
            "experiment_id": EXPERIMENT_ID,
            "n_queries": len(per_query),
            "corpus_sha256": checks["corpus_sha256"],
            "n_docs": EXPECTED_N,
            "dict_keys": EXPECTED_DICT,
            "k1": 1.5,
            "b": 0.75,
            "top_k": TOP_K,
            "python_short": py_short,
            "numpy": checks["numpy"],
            "pandas": checks["pandas"],
            "git_commit": commit,
            "timestamp_utc": ts,
            "preflight_pass": True,
            "detector_counts": det_counts,
            "path_counts": path_counts,
            "n_top50_rows": len(top50_rows),
            "n_top5_rows": len(top5_rows),
            "n_short_lists": len(short_ids),
            "n_hits_distribution": {str(k): v for k, v in sorted(n_hits_dist.items())},
            "short_query_ids": short_ids,
            "n_rank1_match": n_match,
            "n_rank1_mismatch": n_mismatch,
            "mismatches": mismatches,
        },
    )
    print(
        "DONE experiment_id=%s n_queries=%s n_top50=%s n_top5=%s rank1_match=%s/%s"
        % (EXPERIMENT_ID, len(per_query), len(top50_rows), len(top5_rows), n_match, len(per_query)),
        flush=True,
    )


if __name__ == "__main__":
    main()
