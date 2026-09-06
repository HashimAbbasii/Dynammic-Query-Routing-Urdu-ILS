#!/usr/bin/env python3
"""Stage 0: mechanical miss taxonomy from frozen dumps. No retrieval. No tuning."""
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P12 = ROOT / "experiments" / "phase12_new_unseen_evaluation"
RDEV = ROOT / "experiments" / "post_phase12_development"
OUT = RDEV / "stage0_error_taxonomy_counts.json"
OUT_CSV = RDEV / "stage0_error_taxonomy_rows.csv"


def ki_bucket(rank) -> str:
    if rank is None:
        return "ABSENT"
    if 1 <= rank <= 5:
        return "HIT"
    if 6 <= rank <= 50:
        return "RANK"
    return "ABSENT"


def parse_rank(val: str):
    v = (val or "").strip().lower()
    if v in {"", "not_in_top50", "none", "na"}:
        return None
    try:
        return int(v)
    except ValueError:
        return None


def load_k_from_md() -> list[dict]:
    path = P12 / "K_RESULTS.md"
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| K"):
            continue
        parts = [p.strip() for p in line.strip("|").split("|")]
        if len(parts) < 7 or not parts[0].startswith("K"):
            continue
        qid, det, path_name, _nh, _src, rank_s, hit = parts[:7]
        rank = parse_rank(rank_s)
        rows.append(
            {
                "set": "K",
                "query_id": qid,
                "script": det,
                "path": path_name,
                "ki_bucket": ki_bucket(rank),
                "source_rank": rank_s,
                "hit5": hit.lower() == "yes",
            }
        )
    return rows


def load_u() -> list[dict]:
    det = {}
    with (P12 / "U_TOP50_RETRIEVAL.csv").open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if row["query_id"] not in det:
                det[row["query_id"]] = {
                    "script": row["detector_label"],
                    "path": row["retrieval_path"],
                    "query_text": row["query_text"],
                }
    human = ROOT / "experiments" / "phase12_human_relevance" / "PHASE12_HUMAN_RESULTS.md"
    rows = []
    in_table = False
    for line in human.read_text(encoding="utf-8").splitlines():
        if line.startswith("| ID |"):
            in_table = True
            continue
        if in_table and line.startswith("| U"):
            parts = [p.strip() for p in line.strip("|").split("|")]
            qid = parts[0]
            labs = parts[2:7]
            succ = parts[7].lower() == "yes"
            n_ab = sum(x in {"A", "B"} for x in labs)
            n_c = sum(x == "C" for x in labs)
            n_d = sum(x == "D" for x in labs)
            if succ:
                nat = "NAT_OK"
            elif n_d == 5:
                nat = "NAT_FAIL_ALL_D"
            elif n_c == 5:
                nat = "NAT_FAIL_ALL_C"
            else:
                nat = "NAT_FAIL_NO_AB"
            meta = det[qid]
            rows.append(
                {
                    "set": "U",
                    "query_id": qid,
                    "script": meta["script"],
                    "path": meta["path"],
                    "ki_bucket": "",
                    "nat_bucket": nat,
                    "success5": succ,
                    "labels": "".join(labs),
                    "query_text": meta["query_text"],
                }
            )
        elif in_table and line.startswith("## "):
            break
    return rows


def load_r_ki() -> list[dict]:
    queries = {}
    with (RDEV / "queries_r_dev.csv").open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if row["track"] == "KI":
                queries[row["query_id"]] = row
    ranks = defaultdict(list)
    with (RDEV / "R_TOP50_RETRIEVAL.csv").open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if row["track"] != "KI":
                continue
            ranks[row["query_id"]].append(row)
    out = []
    for qid, q in queries.items():
        src = str(q["source_doc_id"]).strip()
        hits = ranks[qid]
        det = hits[0]["detector_label"] if hits else q["script"]
        path = hits[0]["retrieval_path"] if hits else ""
        found = None
        for h in hits:
            if str(h["doc_id"]).strip() == src:
                found = int(h["rank"])
                break
        bucket = ki_bucket(found)
        out.append(
            {
                "set": "R-KI",
                "query_id": qid,
                "script": det,
                "path": path,
                "ki_bucket": bucket,
                "source_rank": "" if found is None else str(found),
                "hit5": found is not None and found <= 5,
                "query_text": q["query_text"],
            }
        )
    return out


def load_r_nat() -> list[dict]:
    queries = {}
    with (RDEV / "queries_r_dev.csv").open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if row["track"] == "NAT":
                queries[row["query_id"]] = row
    labs = defaultdict(list)
    with (RDEV / "qrels_r_dev.csv").open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            labs[row["query_id"]].append(row["relevance_label"])
    det = {}
    with (RDEV / "R_TOP50_RETRIEVAL.csv").open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if row["track"] == "NAT" and row["query_id"] not in det:
                det[row["query_id"]] = {
                    "script": row["detector_label"],
                    "path": row["retrieval_path"],
                    "n_hits": int(row["n_hits_returned"]),
                }
    out = []
    for qid, q in queries.items():
        L = labs.get(qid, [])
        meta = det.get(qid, {"script": q["script"], "path": "", "n_hits": 0})
        n_hits = meta["n_hits"]
        if n_hits == 0:
            nat = "NAT_ZERO_HITS"
            succ = False
        elif not L:
            nat = "NAT_UNLABELED"
            succ = False
        else:
            succ = any(x in {"A", "B"} for x in L)
            if succ:
                nat = "NAT_OK"
            elif all(x == "D" for x in L) and len(L) >= min(5, n_hits):
                nat = "NAT_FAIL_ALL_D"
            elif all(x == "C" for x in L):
                nat = "NAT_FAIL_ALL_C"
            else:
                nat = "NAT_FAIL_NO_AB"
        out.append(
            {
                "set": "R-NAT",
                "query_id": qid,
                "script": meta["script"],
                "path": meta["path"],
                "ki_bucket": "",
                "nat_bucket": nat,
                "success5": succ,
                "n_labels": len(L),
                "query_text": q["query_text"],
            }
        )
    return out


def summarize(rows: list[dict], set_name: str, bucket_key: str):
    sub = [r for r in rows if r["set"] == set_name]
    c = Counter((r["script"], r[bucket_key]) for r in sub)
    return {
        "n": len(sub),
        "by_script_bucket": {f"{s}|{b}": n for (s, b), n in sorted(c.items())},
    }


def main():
    k = load_k_from_md()
    u = load_u()
    rki = load_r_ki()
    rnat = load_r_nat()
    payload = {
        "note": "Mechanical buckets from frozen dumps. Not a new official metric. Do not tune M0.",
        "K": {
            "official_hit5": "27/40",
            **summarize(k, "K", "ki_bucket"),
            "roman_absent": sum(1 for r in k if r["script"] == "ROMAN" and r["ki_bucket"] == "ABSENT"),
            "roman_rank": sum(1 for r in k if r["script"] == "ROMAN" and r["ki_bucket"] == "RANK"),
            "roman_hit": sum(1 for r in k if r["script"] == "ROMAN" and r["ki_bucket"] == "HIT"),
            "urdu_absent": sum(1 for r in k if r["script"] == "URDU" and r["ki_bucket"] == "ABSENT"),
            "urdu_rank": sum(1 for r in k if r["script"] == "URDU" and r["ki_bucket"] == "RANK"),
            "urdu_hit": sum(1 for r in k if r["script"] == "URDU" and r["ki_bucket"] == "HIT"),
        },
        "U": {
            "official_success5": "23/40",
            **summarize(u, "U", "nat_bucket"),
        },
        "R_KI": {
            "m0_hit5_expected": "19/50",
            "hit5": sum(1 for r in rki if r["hit5"]),
            **summarize(rki, "R-KI", "ki_bucket"),
        },
        "R_NAT": {
            "m0_success5_expected": "12/50",
            "success5": sum(1 for r in rnat if r.get("success5")),
            **summarize(rnat, "R-NAT", "nat_bucket"),
        },
    }
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    fieldnames = [
        "set",
        "query_id",
        "script",
        "path",
        "ki_bucket",
        "nat_bucket",
        "source_rank",
        "hit5",
        "success5",
        "labels",
        "n_labels",
        "query_text",
    ]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for row in k + u + rki + rnat:
            w.writerow(row)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    print("wrote", OUT)
    print("wrote", OUT_CSV)


if __name__ == "__main__":
    main()
