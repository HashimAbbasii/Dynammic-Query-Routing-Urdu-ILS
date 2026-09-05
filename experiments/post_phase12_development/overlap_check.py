# -*- coding: utf-8 -*-
"""Leakage / overlap checker for the Post-Phase-12 R-dev query pool.

Detects contamination against sealed and historical query pools.
For dataset construction only — NOT for retrieval optimization.

Does not modify M0, sealed CSVs, or official results.
"""
from __future__ import annotations

import argparse
import ast
import csv
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PHASE2 = ROOT / "experiments" / "phase2_oracle"
sys.path.insert(0, str(PHASE2))

from textnorm import jaccard, normalize_query  # noqa: E402

NEAR_DUP_JACCARD = 0.75


@dataclass
class SealedPool:
    name: str
    queries: list[tuple[str, str]] = field(default_factory=list)  # (id, text)
    source_doc_ids: set[int] = field(default_factory=set)


def _read_csv_queries(path: Path, id_col: str, text_col: str) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    with path.open(encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            qid = (row.get(id_col) or "").strip()
            text = (row.get(text_col) or "").strip()
            if qid and text:
                out.append((qid, text))
    return out


def _read_source_ids(path: Path, col: str = "source_doc_id") -> set[int]:
    ids: set[int] = set()
    with path.open(encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            v = (row.get(col) or "").strip()
            if v.isdigit():
                ids.add(int(v))
    return ids


def _load_training_queries(path: Path) -> list[tuple[str, str]]:
    if not path.is_file():
        return []
    content = path.read_text(encoding="utf-8")
    start = content.find("training_queries = [")
    if start < 0:
        return []
    blob = content[start + len("training_queries = ") :]
    data = ast.literal_eval(blob)
    out: list[tuple[str, str]] = []
    for i, item in enumerate(data, 1):
        if isinstance(item, (list, tuple)):
            text = str(item[0])
        else:
            text = str(item)
        if text.strip():
            out.append((f"TRAIN_{i:03d}", text))
    return out


def _load_heldout_traps() -> list[tuple[str, str]]:
    path = ROOT / "archive" / "historical_experiments" / "validate" / "dual_index_routing" / "labels" / "heldout_traps.py"
    if not path.is_file():
        return []
    ns: dict = {}
    exec(path.read_text(encoding="utf-8"), ns)  # noqa: S102 — trusted local freeze artifact
    traps = ns.get("HELDOUT_TRAPS") or []
    return [(row[0], row[4]) for row in traps if len(row) >= 5]


def load_sealed_pools() -> list[SealedPool]:
    pools: list[SealedPool] = []

    oracle = ROOT / "experiments" / "phase2_oracle" / "oracle_all.csv"
    if oracle.is_file():
        p = SealedPool("QTRN")
        p.queries = _read_csv_queries(oracle, "query_id", "query_text")
        p.source_doc_ids = _read_source_ids(oracle)
        pools.append(p)

    k_path = ROOT / "experiments" / "phase12_new_unseen_evaluation" / "queries_k.csv"
    if k_path.is_file():
        p = SealedPool("K")
        p.queries = _read_csv_queries(k_path, "query_id", "query_text")
        p.source_doc_ids = _read_source_ids(k_path)
        pools.append(p)

    u_path = ROOT / "experiments" / "phase12_new_unseen_evaluation" / "queries_u.csv"
    if u_path.is_file():
        p = SealedPool("U")
        p.queries = _read_csv_queries(u_path, "query_id", "query_text")
        pools.append(p)

    h_queries = _load_heldout_traps()
    if h_queries:
        pools.append(SealedPool("H", queries=h_queries))

    trap_csv = ROOT / "archive" / "historical_experiments" / "validate" / "dual_index_routing" / "labels" / "trap_label_sheet.csv"
    if trap_csv.is_file():
        pools.append(SealedPool("T", queries=_read_csv_queries(trap_csv, "query_id", "query")))

    train = _load_training_queries(ROOT / "data" / "training_queries_real.py")
    if train:
        pools.append(SealedPool("SVM_TRAIN", queries=train))

    return pools


def forbidden_source_ids(pools: list[SealedPool]) -> set[int]:
    out: set[int] = set()
    for p in pools:
        out |= p.source_doc_ids
    return out


def check_candidates(
    rows: list[dict],
    *,
    pools: list[SealedPool] | None = None,
    near_dup_threshold: float = NEAR_DUP_JACCARD,
) -> dict:
    pools = pools or load_sealed_pools()
    forbidden_ids = forbidden_source_ids(pools)

    sealed_texts: list[tuple[str, str, str]] = []
    for p in pools:
        for qid, text in p.queries:
            sealed_texts.append((p.name, qid, text))

    blocked_norms = {normalize_query(text) for _, _, text in sealed_texts}
    blocked_norms.discard("")

    issues: list[dict] = []
    seen_norm: dict[str, str] = {}
    seen_ids: set[str] = set()

    for row in rows:
        qid = (row.get("query_id") or "").strip()
        text = (row.get("query_text") or row.get("query") or "").strip()
        track = (row.get("track") or "").strip().upper()
        src = (row.get("source_doc_id") or "").strip()

        if not qid:
            issues.append({"reason": "missing_query_id", "row": row})
            continue
        if qid in seen_ids:
            issues.append({"reason": "duplicate_query_id", "query_id": qid})
        seen_ids.add(qid)

        for prefix in ("H", "K", "U", "QTRN"):
            if qid.startswith(prefix):
                issues.append({"reason": "forbidden_id_prefix", "query_id": qid, "prefix": prefix})

        norm = normalize_query(text)
        if not norm:
            issues.append({"reason": "empty_query_text", "query_id": qid})
            continue

        if norm in blocked_norms:
            issues.append({"reason": "exact_normalized_match", "query_id": qid, "norm": norm})

        if norm in seen_norm:
            issues.append(
                {
                    "reason": "duplicate_within_candidate_pool",
                    "query_id": qid,
                    "other_id": seen_norm[norm],
                }
            )
        else:
            seen_norm[norm] = qid

        for pool_name, sealed_id, sealed_text in sealed_texts:
            jac = jaccard(text, sealed_text)
            if jac >= near_dup_threshold:
                issues.append(
                    {
                        "reason": "near_duplicate",
                        "query_id": qid,
                        "against_pool": pool_name,
                        "against_id": sealed_id,
                        "jaccard": round(jac, 4),
                    }
                )

        if src.isdigit():
            doc_id = int(src)
            if doc_id in forbidden_ids:
                issues.append(
                    {
                        "reason": "forbidden_source_doc_id",
                        "query_id": qid,
                        "source_doc_id": doc_id,
                    }
                )
            if track == "NAT":
                issues.append(
                    {
                        "reason": "source_doc_id_on_naturalistic_track",
                        "query_id": qid,
                        "source_doc_id": doc_id,
                    }
                )

    return {
        "ok": len(issues) == 0,
        "n_candidates": len(rows),
        "n_issues": len(issues),
        "issues": issues,
        "n_sealed_queries": sum(len(p.queries) for p in pools),
        "n_forbidden_source_doc_ids": len(forbidden_ids),
        "near_dup_jaccard_threshold": near_dup_threshold,
        "pools_loaded": [p.name for p in pools],
    }


def _load_candidate_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def main() -> int:
    parser = argparse.ArgumentParser(description="Check R-dev draft queries for leakage.")
    parser.add_argument("csv", type=Path, help="Candidate queries CSV (draft)")
    parser.add_argument("--json", action="store_true", help="Print full JSON report")
    args = parser.parse_args()

    if not args.csv.is_file():
        print(f"ERROR: file not found: {args.csv}", file=sys.stderr)
        return 2

    rows = _load_candidate_csv(args.csv)
    report = check_candidates(rows)

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"Candidates: {report['n_candidates']}")
        print(f"Sealed queries indexed: {report['n_sealed_queries']}")
        print(f"Forbidden source_doc_ids: {report['n_forbidden_source_doc_ids']}")
        print(f"OK: {report['ok']}")
        if report["issues"]:
            print(f"Issues: {report['n_issues']}")
            for issue in report["issues"][:20]:
                line = json.dumps(issue, ensure_ascii=False)
                try:
                    print(f"  - {line}")
                except UnicodeEncodeError:
                    print(f"  - {line.encode('ascii', 'backslashreplace').decode('ascii')}")
            if report["n_issues"] > 20:
                print(f"  ... and {report['n_issues'] - 20} more")

    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
