# -*- coding: utf-8 -*-
"""
Evaluate dual-index *routing* on Phase 2.5 human judgments (ranks 1-5).

Does not re-run Chroma. For each query, existing HEADLINE and FULL_CONTENT
ranked lists are already judged. This script only asks: if a router picks
one of those two modes, what P@5 / nDCG@5 / MRR does the user get?

Systems compared:
  always_headline, always_full, theta150, wordcount, svm_v2

Judged depth is 5. P@10/P@15 are NOT reported.
"""
from __future__ import annotations

import csv
import json
import math
import os
import sys
from collections import defaultdict

_DIR = os.path.dirname(os.path.abspath(__file__))
if _DIR not in sys.path:
    sys.path.insert(0, _DIR)
from router import decide

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
JUDGMENTS = os.path.join(
    REPO_ROOT, "validate", "phase2_5", "human_judgments", "human_judgments.csv"
)
OUT_JSON = os.path.join(os.path.dirname(__file__), "routed_p5_results.json")
OUT_TXT = os.path.join(os.path.dirname(__file__), "routed_p5_results.txt")

REL_MAP = {
    "relevant": 1.0,
    "partially relevant": 0.5,
    "not relevant": 0.0,
}
SYSTEMS = [
    "always_headline",
    "always_full",
    "theta150",
    "wordcount",
    "svm_v2",
]


def precision_at_k(graded, k):
    top = graded[:k]
    if not top:
        return None
    return sum(top) / len(top)


def reciprocal_rank(graded):
    for i, rel in enumerate(graded, 1):
        if rel > 0:
            return 1.0 / i
    return 0.0


def ndcg_at_k(graded, k):
    def dcg(xs):
        return sum((2 ** rel - 1) / math.log2(i + 2) for i, rel in enumerate(xs[:k]))
    d = dcg(graded)
    ideal = dcg(sorted(graded, reverse=True))
    if ideal == 0:
        return 0.0
    return d / ideal


def load_mode_lists(path):
    with open(path, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    groups = defaultdict(list)
    qinfo = {}
    for r in rows:
        mode = r["retrieval_mode"]
        if mode not in ("HEADLINE", "FULL_CONTENT"):
            continue
        qid = r["query_id"]
        groups[(qid, mode)].append(r)
        qinfo[qid] = {
            "query": r["query"],
            "word_count": int(r["word_count"]),
            "script": r["script"],
            "tag": r.get("tag", ""),
        }
    lists = {}
    for key, items in groups.items():
        items.sort(key=lambda x: int(x["rank"]))
        graded = []
        for it in items:
            rel = REL_MAP.get((it.get("relevance") or "").strip().lower())
            if rel is None:
                continue
            graded.append(rel)
        lists[key] = graded[:5]
    return qinfo, lists


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def main():
    qinfo, lists = load_mode_lists(JUDGMENTS)
    qids = sorted(qinfo)
    per_system = {s: {"P@5": [], "nDCG@5": [], "MRR": [], "n_headline": 0, "n_full": 0} for s in SYSTEMS}
    per_query = []

    for qid in qids:
        q = qinfo[qid]["query"]
        row = {
            "query_id": qid,
            "query": q,
            "word_count": qinfo[qid]["word_count"],
            "script": qinfo[qid]["script"],
            "tag": qinfo[qid]["tag"],
        }
        for s in SYSTEMS:
            d = decide(q, s)
            mode = d["mode"]
            graded = lists.get((qid, mode), [])
            p5 = precision_at_k(graded, 5)
            nd = ndcg_at_k(graded, 5)
            mrr = reciprocal_rank(graded)
            per_system[s]["P@5"].append(p5)
            per_system[s]["nDCG@5"].append(nd)
            per_system[s]["MRR"].append(mrr)
            if mode == "HEADLINE":
                per_system[s]["n_headline"] += 1
            else:
                per_system[s]["n_full"] += 1
            row[s] = {
                "label": d["label"],
                "mode": mode,
                "confidence": d["confidence"],
                "P@5": p5,
                "nDCG@5": nd,
                "MRR": mrr,
            }
        per_query.append(row)

    summary = {}
    for s in SYSTEMS:
        summary[s] = {
            "n_queries": len(qids),
            "n_routed_headline": per_system[s]["n_headline"],
            "n_routed_full": per_system[s]["n_full"],
            "mean_P@5": mean(per_system[s]["P@5"]),
            "mean_nDCG@5": mean(per_system[s]["nDCG@5"]),
            "mean_MRR": mean(per_system[s]["MRR"]),
        }

    # Paired wins: svm vs wordcount / theta150 / always_full / always_headline on P@5
    def paired(a, b):
        a_better = b_better = tie = 0
        for row in per_query:
            pa, pb = row[a]["P@5"], row[b]["P@5"]
            if pa is None or pb is None:
                continue
            if pa > pb:
                a_better += 1
            elif pb > pa:
                b_better += 1
            else:
                tie += 1
        return {"left_better": a_better, "right_better": b_better, "tie": tie}

    comparisons = {
        "svm_v2 vs wordcount P@5": paired("svm_v2", "wordcount"),
        "svm_v2 vs theta150 P@5": paired("svm_v2", "theta150"),
        "svm_v2 vs always_headline P@5": paired("svm_v2", "always_headline"),
        "svm_v2 vs always_full P@5": paired("svm_v2", "always_full"),
        "wordcount vs theta150 P@5": paired("wordcount", "theta150"),
    }

    report = {
        "judgments_path": JUDGMENTS,
        "n_queries": len(qids),
        "judged_depth": 5,
        "note": "Reuse Phase 2.5 human judgments. Router only selects HEADLINE vs FULL_CONTENT list. No P@15.",
        "summary": summary,
        "paired_P@5": comparisons,
        "per_query": per_query,
    }

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    lines = []
    lines.append("DUAL-INDEX ROUTING EVALUATION (Phase 2.5 judgments, depth 5)")
    lines.append(f"n_queries = {len(qids)}")
    lines.append("")
    lines.append(f"{'system':20} {'P@5':>8} {'nDCG@5':>8} {'MRR':>8} {'->H':>5} {'->F':>5}")
    for s in SYSTEMS:
        sm = summary[s]
        lines.append(
            f"{s:20} {sm['mean_P@5']:.4f} {sm['mean_nDCG@5']:.4f} {sm['mean_MRR']:.4f} "
            f"{sm['n_routed_headline']:5d} {sm['n_routed_full']:5d}"
        )
    lines.append("")
    lines.append("Paired P@5 (left better / right better / tie)")
    for k, v in comparisons.items():
        lines.append(f"  {k}: {v['left_better']} / {v['right_better']} / {v['tie']}")
    text = "\n".join(lines) + "\n"
    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write(text)
    print(text)
    print(f"Wrote {OUT_JSON}")


if __name__ == "__main__":
    main()
