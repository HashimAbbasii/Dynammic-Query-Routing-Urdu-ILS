#!/usr/bin/env python3
"""Phase1: population comparison + lexical overlap. No TEST. Read-only corpus/queries."""
from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
CORPUS = ROOT / "data" / "clean_articles.csv"
ORACLE = ROOT / "experiments" / "phase2_oracle" / "oracle_all.csv"
K_PATH = ROOT / "experiments" / "phase12_new_unseen_evaluation" / "queries_k.csv"
U_PATH = ROOT / "experiments" / "phase12_new_unseen_evaluation" / "queries_u.csv"
P13 = (
    ROOT
    / "experiments"
    / "ultra_v2"
    / "phase13_population"
    / "artifacts"
    / "scoring"
    / "PHASE13_SCORING_PER_QUERY.csv"
)
FD = ROOT / "experiments" / "ieee_adaptive" / "FAILURE_DECOMPOSITION_PER_QUERY.csv"
C2A = ROOT / "experiments" / "ieee_adaptive" / "C2A_CASE_ANNOTATIONS.csv"


def script_label(q: str) -> str:
    ur = sum(1 for c in q if "\u0600" <= c <= "\u06ff")
    lat = sum(1 for c in q if ("A" <= c <= "Z") or ("a" <= c <= "z"))
    if ur and lat:
        return "MIXED"
    if ur:
        return "URDU"
    if lat:
        return "ROMAN"
    return "OTHER"


def toks(s: str) -> list[str]:
    s = s or ""
    return re.findall(r"[A-Za-z0-9]+|[\u0600-\u06FF]+", s.lower())


def coverage_overlap(q: str, h: str) -> float:
    qt = set(toks(q))
    if not qt:
        return 0.0
    ht = set(toks(h))
    return len(qt & ht) / len(qt)


def jaccard(q: str, h: str) -> float:
    qt = set(toks(q))
    ht = set(toks(h))
    if not qt and not ht:
        return 0.0
    return len(qt & ht) / len(qt | ht)


def load_heads() -> dict[int, str]:
    heads: dict[int, str] = {}
    with CORPUS.open(encoding="utf-8", errors="replace", newline="") as f:
        for row in csv.DictReader(f):
            raw = row.get("Index") or row.get("index")
            try:
                idx = int(raw)
            except (TypeError, ValueError):
                continue
            heads[idx] = row.get("Headline") or row.get("headline") or ""
    return heads


def summarize(name: str, rows: list[dict]) -> dict:
    ov = [r["_cov"] for r in rows]
    jac = [r["_jac"] for r in rows]
    scripts = Counter(r["_script"] for r in rows)
    return {
        "name": name,
        "n": len(rows),
        "scripts": dict(scripts),
        "mean_query_coverage_vs_headline": round(sum(ov) / len(ov), 4) if ov else None,
        "median_query_coverage_vs_headline": round(sorted(ov)[len(ov) // 2], 4) if ov else None,
        "pct_cov_ge_0.5": round(100 * sum(1 for x in ov if x >= 0.5) / len(ov), 2) if ov else None,
        "pct_cov_eq_0": round(100 * sum(1 for x in ov if x == 0.0) / len(ov), 2) if ov else None,
        "mean_jaccard": round(sum(jac) / len(jac), 4) if jac else None,
        "mean_q_tokens": round(sum(r["_qlen"] for r in rows) / len(rows), 2) if rows else None,
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    heads = load_heads()
    print("heads", len(heads))

    # --- Population A: n=78 oracle ---
    ora = list(csv.DictReader(ORACLE.open(encoding="utf-8-sig")))
    print("oracle cols", list(ora[0].keys())[:20])
    # Prefer split tags if present
    split_key = None
    for k in ("split", "set", "pool", "partition", "group"):
        if k in ora[0]:
            split_key = k
            break
    if split_key:
        print("split counts", Counter(r[split_key] for r in ora))
    # language / script fields
    for k in ora[0]:
        if "lang" in k.lower() or "script" in k.lower() or "type" in k.lower():
            print("field", k, Counter(r[k] for r in ora).most_common(8))

    # Identify query and gold columns
    qcol = next(
        c
        for c in ("query_text", "query", "q", "question", "title_roman", "roman_query")
        if c in ora[0]
    )
    # Often source_doc_id
    gcol = next(
        c
        for c in ("source_doc_id", "doc_id", "gold_id", "article_id", "id")
        if c in ora[0]
    )
    print("qcol", qcol, "gcol", gcol)

    # Filter to n=78: development docs say Phase 2 dev + internal_val
    if split_key and any(
        str(r[split_key]).lower() in ("dev", "internal_val", "internal-val", "val")
        for r in ora
    ):
        pool = [
            r
            for r in ora
            if str(r[split_key]).lower()
            in ("dev", "internal_val", "internal-val", "val", "development")
        ]
        if len(pool) != 78:
            # try explicit n=78 file subset markers
            pool = ora
            print("WARN split filter size", len(pool), "falling back inspection")
    else:
        pool = ora

    # If still not 78, look for flag
    if len(pool) != 78:
        for k in ora[0]:
            vals = Counter(r[k] for r in ora)
            if 78 in vals.values() or any(v == 78 for v in vals.values()):
                print("candidate 78-field", k, vals.most_common(10))

    print("pool_n_before", len(pool))
    # DEVELOPMENT_RESULTS: Phase 2 dev + internal_val n=78 from oracle_all
    # Read FINAL_EVALUATION_PROTOCOL for ID list if needed
    pop_a = []
    for r in pool:
        try:
            gid = int(float(r[gcol]))
        except Exception:
            continue
        q = r[qcol]
        h = heads.get(gid, "")
        pop_a.append(
            {
                "query_id": r.get("query_id") or r.get("id") or r.get("qid") or "",
                "population": "A_n78_dev",
                "query_text": q,
                "_script": script_label(q),
                "_cov": coverage_overlap(q, h),
                "_jac": jaccard(q, h),
                "_qlen": len(toks(q)),
                "source_doc_id": gid,
                "language_type": r.get("language_type") or r.get("script") or "",
                "title_roman_flag": r.get("title_roman") or r.get("is_title_roman") or "",
            }
        )
    # If too many, try filter language_type / known Phase2
    print("pop_a_n", len(pop_a), summarize("A", pop_a))

    # Save oracle field dump for manual filter
    Path(OUT / "oracle_schema_probe.json").write_text(
        json.dumps(
            {
                "n_rows": len(ora),
                "columns": list(ora[0].keys()),
                "split_key": split_key,
                "split_counts": dict(Counter(r[split_key] for r in ora)) if split_key else None,
                "pop_a_n": len(pop_a),
            },
            indent=2,
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
