# -*- coding: utf-8 -*-
"""
M1-D controlled ablation: exactly one retrieval pass on sealed R-dev.

Layer A + conservative repeated-character normalization (ROMAN branch only).
Does not modify frozen inputs or overwrite M0 / M1-A/B/C artifacts.
"""
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

_DIR = Path(__file__).resolve().parent
ROOT = _DIR.parents[2]
R_DEV = ROOT / "experiments" / "post_phase12_development"
P5 = ROOT / "experiments" / "phase5_roman_urdu"
ARCHIVE_VALIDATE = ROOT / "archive" / "historical_experiments" / "validate" / "dual_index_routing"

sys.path.insert(0, str(ARCHIVE_VALIDATE))
sys.path.insert(0, str(P5))
sys.path.insert(0, str(_DIR))
sys.path.insert(0, str(ROOT))

import run_phase5 as p5  # noqa: E402
from candidates import LAYER_A_REPEAT, roman_query_tokens_m1d  # noqa: E402
from run_module1_ablation import (  # noqa: E402
    TOP_K,
    build_indexes,
    eval_candidate,
    ki_hit5,
    load_m0_ranks,
    load_qrels,
    load_queries,
    nat_success,
    sha256_file,
)

CANDIDATE_ID = "M1-D"
QUERY_PATH = R_DEV / "queries_r_dev.csv"
SEAL_PATH = R_DEV / "SEAL.json"
M0_TOP50 = R_DEV / "R_TOP50_RETRIEVAL.csv"
M0_TOP5 = R_DEV / "R_TOP5_FOR_ANNOTATION.csv"
QRELS_PATH = R_DEV / "qrels_r_dev.csv"
DICT_PATH = ROOT / "models" / "roman_urdu_dict_expanded.json"

EXPECTED = {
    "queries_r_dev.csv": "1603b37eeee41fa6270f4e13d185c8eebd4512d025cd5fc67e8a81de9407e75f",
    "R_TOP50_RETRIEVAL.csv": "927a14a25b6f1de2a5c28aabdc2d8cbc0d4336e0b2b437490691a7bff63a2aa2",
    "R_TOP5_FOR_ANNOTATION.csv": "042006bc3232719514a6ca4b638f4e6348415d168294271fe366ff95704b23c5",
    "qrels_r_dev.csv": "506305b5401102a3659d21b69c7a937bcdcde78b21a1409a6a6132255ff37bcb",
    "roman_urdu_dict_expanded.json": "30c3f61a64ec641abbb3acdbc7a8bcaf197f0238f1bf9e76c2c7ce8e590f86a3",
}


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


def preflight():
    checks = {"failed": [], "files": {}}
    paths = {
        "queries_r_dev.csv": QUERY_PATH,
        "SEAL.json": SEAL_PATH,
        "R_TOP50_RETRIEVAL.csv": M0_TOP50,
        "R_TOP5_FOR_ANNOTATION.csv": M0_TOP5,
        "qrels_r_dev.csv": QRELS_PATH,
        "roman_urdu_dict_expanded.json": DICT_PATH,
    }
    for name, path in paths.items():
        h = sha256_file(path) if path.exists() else ""
        exp = EXPECTED.get(name)
        ok = h == exp if exp else True
        checks["files"][name] = {"path": str(path), "sha256": h, "expected": exp, "ok": ok}
        if exp and not ok:
            checks["failed"].append("%s_sha_mismatch" % name)

    with open(SEAL_PATH, encoding="utf-8") as f:
        seal = json.load(f)
    if seal.get("queries_r_dev_sha256") != EXPECTED["queries_r_dev.csv"]:
        checks["failed"].append("seal_query_sha_mismatch")

    queries = load_queries()
    if len(queries) != 100:
        checks["failed"].append("query_count_not_100")
    ki_n = sum(1 for q in queries if q["track"] == "KI")
    nat_n = sum(1 for q in queries if q["track"] == "NAT")
    if ki_n != 50:
        checks["failed"].append("ki_count_not_50")
    if nat_n != 50:
        checks["failed"].append("nat_count_not_50")

    checks["query_count"] = len(queries)
    checks["ki_count"] = ki_n
    checks["nat_count"] = nat_n
    checks["preflight_pass"] = len(checks["failed"]) == 0
    return checks, queries


def audit_roman_transforms(queries):
    """Count ROMAN queries whose token sequence changes under M1-D."""
    changed, unchanged, non_roman = [], [], 0
    details = []
    for r in queries:
        qid = r["query_id"]
        qtext = r["query_text"]
        det = p5.detect_script(qtext)
        if det != "ROMAN":
            non_roman += 1
            continue
        raw_toks = p5.tokenize(qtext)
        m1d_toks = roman_query_tokens_m1d(qtext)
        if raw_toks != m1d_toks:
            changed.append(qid)
            details.append({
                "query_id": qid,
                "track": r["track"],
                "m0_tokens": raw_toks,
                "m1d_tokens": m1d_toks,
            })
        else:
            unchanged.append(qid)
    return {
        "roman_query_count": len(changed) + len(unchanged),
        "roman_changed_count": len(changed),
        "roman_unchanged_count": len(unchanged),
        "roman_changed_query_ids": changed,
        "roman_unchanged_query_ids": unchanged,
        "urdu_mixed_transform_count": non_roman,
        "change_details": details,
    }


def retrieve_m1d(queries, urdu_bm25, roman_bm25):
    per_q = {}
    top50_rows = []
    urdu_mixed_paths = 0
    roman_paths = 0
    for r in queries:
        qid = r["query_id"]
        qtext = r["query_text"]
        track = r["track"]
        det = p5.detect_script(qtext)
        if det == "ROMAN":
            qtoks = roman_query_tokens_m1d(qtext)
            path = "roman_bm25_method_D"
            hits = roman_bm25.search(qtoks, top_k=TOP_K)
            roman_paths += 1
        else:
            qtoks = p5.tokenize(qtext)
            path = "urdu_bm25"
            hits = urdu_bm25.search(qtoks, top_k=TOP_K)
            urdu_mixed_paths += 1
        src = r["source_doc_id"]
        src_rank = p5.rank_of(hits, src) if track == "KI" and src != "" else None
        top5_docs = [int(d) for d, _ in hits[:5]]
        per_q[qid] = {
            "detector_label": det,
            "retrieval_path": path,
            "source_rank": src_rank,
            "top5_docs": top5_docs,
            "n_hits": len(hits),
            "query_tokens": qtoks,
        }
        for rank, (did, score) in enumerate(hits, 1):
            top50_rows.append({
                "experiment_id": "post_phase12_module1_M1-D",
                "candidate_id": CANDIDATE_ID,
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
    return per_q, top50_rows, {
        "queries_processed": len(queries),
        "roman_path_count": roman_paths,
        "urdu_mixed_path_count": urdu_mixed_paths,
    }


def compare_rankings_m0(queries, top50_rows):
    all_qids = [r["query_id"] for r in queries]
    m0_by = defaultdict(list)
    with open(M0_TOP50, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            m0_by[r["query_id"]].append((int(r["rank"]), int(r["doc_id"])))
    m1_by = defaultdict(list)
    for r in top50_rows:
        m1_by[r["query_id"]].append((int(r["rank"]), int(r["doc_id"])))
    changed, unchanged = [], []
    for qid in all_qids:
        m0 = sorted(m0_by.get(qid, []))
        m1 = sorted(m1_by.get(qid, []))
        if m0 != m1:
            changed.append(qid)
        else:
            unchanged.append(qid)
    return changed, unchanged


def append_results_md(metrics, transform_audit, ranking_audit):
    path = _DIR / "MODULE1_RESULTS.md"
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    if "## M1-D —" not in existing:
        block = [
            "",
            "## M1-D — Layer A + repeated-character normalization",
            "",
            (
                "Layer A plus collapse ASCII letter runs of 3+ to maximum 2 consecutive "
                "(`NormalizationConfig.repeated_character_normalization=True`, "
                "`min_run_to_collapse=3`, `max_identical_letter_run=2`)."
            ),
            "",
            "| | KI Hit@5 | NAT Success@5 |",
            "| --- | --- | --- |",
            "| M0 | %s/50 | %s/50 |" % (metrics["ki"]["m0"]["hits"], metrics["nat"]["m0"]["hits"]),
            "| M1-D | %s/50 | %s/50 |" % (metrics["ki"]["candidate"]["hits"], metrics["nat"]["candidate"]["hits"]),
            "| Delta | %+.0f | %+.0f |" % (
                metrics["ki"]["candidate"]["hits"] - metrics["ki"]["m0"]["hits"],
                metrics["nat"]["candidate"]["hits"] - metrics["nat"]["m0"]["hits"],
            ),
            "",
            "**KI script strata (Hit@5):** %s" % json.dumps(metrics["ki"]["by_script"], ensure_ascii=False),
            "",
            "**NAT script strata (Success@5):** %s" % json.dumps(metrics["nat"]["by_script"], ensure_ascii=False),
            "",
            "Roman queries with token change: %s / %s"
            % (transform_audit["roman_changed_count"], transform_audit["roman_query_count"]),
            "",
            "Ranking lists changed vs M0: %s / 100" % len(ranking_audit["changed_query_ids"]),
            "",
            "KI improved: %s | worsened: %s | unchanged: %s"
            % (len(metrics["ki"]["improved"]), len(metrics["ki"]["worsened"]), len(metrics["ki"]["unchanged"])),
            "",
            "NAT improved: %s | worsened: %s | unchanged: %s"
            % (len(metrics["nat"]["improved"]), len(metrics["nat"]["worsened"]), len(metrics["nat"]["unchanged"])),
            "",
        ]
        with open(path, "a", encoding="utf-8") as f:
            f.write("\n".join(block))


def postflight_verify():
    out = {"files": {}, "all_ok": True}
    for name, exp in EXPECTED.items():
        path = {
            "queries_r_dev.csv": QUERY_PATH,
            "R_TOP50_RETRIEVAL.csv": M0_TOP50,
            "R_TOP5_FOR_ANNOTATION.csv": M0_TOP5,
            "qrels_r_dev.csv": QRELS_PATH,
            "roman_urdu_dict_expanded.json": DICT_PATH,
        }[name]
        h = sha256_file(path)
        ok = h == exp
        out["files"][name] = {"sha256": h, "expected": exp, "ok": ok}
        if not ok:
            out["all_ok"] = False
    return out


def main():
    pre, queries = preflight()
    if not pre["preflight_pass"]:
        print("STOP preflight failed:", pre["failed"], flush=True)
        sys.exit(2)
    print("PREFLIGHT PASS", json.dumps({
        "queries": pre["query_count"],
        "ki": pre["ki_count"],
        "nat": pre["nat_count"],
    }), flush=True)

    transform_audit = audit_roman_transforms(queries)
    qrels = load_qrels()
    m0_ki_rank, m0_nat_top5, m0_det = load_m0_ranks()

    fwd = p5.load_roman_dict()
    rev = p5.load_reverse_roman(fwd)
    t0 = time.perf_counter()
    urdu_bm25, roman_bm25, _, _ = build_indexes(fwd, rev)
    index_s = time.perf_counter() - t0

    t1 = time.perf_counter()
    per_q, top50_rows, run_info = retrieve_m1d(queries, urdu_bm25, roman_bm25)
    search_s = time.perf_counter() - t1

    ranking_changed, ranking_unchanged = compare_rankings_m0(queries, top50_rows)
    ranking_audit = {
        "changed_query_ids": ranking_changed,
        "unchanged_query_ids": ranking_unchanged,
        "changed_count": len(ranking_changed),
        "unchanged_count": len(ranking_unchanged),
    }

    out_csv = _DIR / "M1-D_TOP50_RETRIEVAL.csv"
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
    post = postflight_verify()
    if not post["all_ok"]:
        print("STOP postflight frozen hash mismatch", post["files"], flush=True)
        sys.exit(2)

    manifest = {
        "experiment_id": "post_phase12_module1_M1-D",
        "candidate_id": CANDIDATE_ID,
        "hypothesis": "Repeated-character normalization improves ROMAN retrieval on R-dev",
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "git_commit": git_commit(),
        "retrieval_pass_count": 1,
        "exactly_one_retrieval_pass": True,
        "preflight": pre,
        "postflight_frozen_integrity": post,
        "transformation_definition": {
            "layer_a": "NFKC, lowercase, punctuation spacing, whitespace",
            "repeated_character_normalization": True,
            "min_run_to_collapse": LAYER_A_REPEAT.min_run_to_collapse,
            "max_identical_letter_run": LAYER_A_REPEAT.max_identical_letter_run,
            "rule": "Collapse ASCII letter runs of 3+ to max 2 consecutive (not 1)",
            "apply_after": "detect_script(raw_query)",
            "apply_when": "detector_label == ROMAN",
            "apply_before": "roman_bm25_method_D search",
            "urdu_mixed_unchanged": True,
            "implementation": "src.roman_urdu_normalization.NormalizationConfig + normalize_roman_urdu",
        },
        "frozen_inputs_sha256": EXPECTED,
        "m0_top50_sha256": EXPECTED["R_TOP50_RETRIEVAL.csv"],
        "qrels_sha256": EXPECTED["qrels_r_dev.csv"],
        "output_retrieval_sha256": out_sha,
        "output_file": "M1-D_TOP50_RETRIEVAL.csv",
        "bm25_k1": 1.5,
        "bm25_b": 0.75,
        "top_k": TOP_K,
        "index_build_seconds": round(index_s, 2),
        "search_seconds": round(search_s, 2),
        "roman_transform_audit": {
            k: transform_audit[k]
            for k in transform_audit
            if k != "change_details"
        },
        "roman_token_change_details": transform_audit["change_details"],
        "ranking_audit": ranking_audit,
        "run_info": run_info,
        "metrics": metrics,
        "m0_modified": False,
        "dictionary_modified": False,
        "qrels_modified": False,
        "queries_modified": False,
    }
    with open(_DIR / "M1-D_MANIFEST.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    append_results_md(metrics, transform_audit, ranking_audit)

    print(
        "M1-D KI=%s/50 NAT=%s/50 delta_ki=%+.0f delta_nat=%+.0f"
        % (
            metrics["ki"]["candidate"]["hits"],
            metrics["nat"]["candidate"]["hits"],
            metrics["ki"]["candidate"]["hits"] - metrics["ki"]["m0"]["hits"],
            metrics["nat"]["candidate"]["hits"] - metrics["nat"]["m0"]["hits"],
        ),
        flush=True,
    )
    print(
        "roman_changed=%s/%s ranking_changed=%s/100"
        % (
            transform_audit["roman_changed_count"],
            transform_audit["roman_query_count"],
            ranking_audit["changed_count"],
        ),
        flush=True,
    )
    print("M1-D COMPLETE", flush=True)


if __name__ == "__main__":
    main()
