# -*- coding: utf-8 -*-
"""
After heldout_retrieval_template.csv is judged, compute P@5 for
always-headline / always-full / theta150 / wordcount / svm_v2.

Uses protocol gold in heldout_traps.py only to choose the SVM/wordcount
ROOM. Relevance must come from the filled template (not UNJUDGED).
Does not train.
"""
from __future__ import annotations

import csv
import json
import math
import os
import sys
from collections import defaultdict

_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _DIR)
sys.path.insert(0, os.path.join(_DIR, "labels"))
from heldout_traps import HELDOUT_TRAPS  # noqa: E402
from router import decide  # noqa: E402

TEMPLATE = os.path.join(_DIR, "labels", "heldout_retrieval_template.csv")
OUT_JSON = os.path.join(_DIR, "labels", "heldout_routed_p5.json")
OUT_TXT = os.path.join(_DIR, "labels", "heldout_routed_p5.txt")
REL = {"relevant": 1.0, "partially relevant": 0.5, "not relevant": 0.0}
SYSTEMS = ["always_headline", "always_full", "theta150", "wordcount", "svm_v2"]


def p_at_5(xs):
    top = xs[:5]
    return sum(top) / len(top) if top else None


def ndcg_at_5(xs):
    def dcg(v):
        return sum((2 ** r - 1) / math.log2(i + 2) for i, r in enumerate(v[:5]))

    d, ideal = dcg(xs), dcg(sorted(xs, reverse=True))
    return 0.0 if ideal == 0 else d / ideal


def main():
    with open(TEMPLATE, encoding="utf-8-sig") as f:
        raw = list(csv.DictReader(f))
    unjudged = sum(1 for r in raw if (r.get("relevance") or "").strip().upper() in ("", "UNJUDGED"))
    if unjudged:
        print(f"{unjudged} rows still UNJUDGED in {TEMPLATE}")
        print("Fill relevance (Relevant / Partially relevant / Not relevant), then re-run.")
        sys.exit(2)

    lists = defaultdict(list)
    for r in raw:
        key = (r["query_id"], r["retrieval_mode"])
        lists[key].append(r)
    for key in lists:
        lists[key].sort(key=lambda x: int(x["rank"]))

    gold = {t[0]: t[5].upper() for t in HELDOUT_TRAPS}
    qmap = {t[0]: t[4] for t in HELDOUT_TRAPS}

    summary = {s: {"P@5": [], "nDCG@5": [], "H": 0, "F": 0} for s in SYSTEMS}
    per_q = []
    for qid, query in qmap.items():
        row = {"query_id": qid, "query": query}
        for s in SYSTEMS:
            d = decide(query, s)
            mode = d["mode"]
            graded = []
            for it in lists.get((qid, mode), [])[:5]:
                graded.append(REL[(it["relevance"] or "").strip().lower()])
            p5, nd = p_at_5(graded), ndcg_at_5(graded)
            summary[s]["P@5"].append(p5)
            summary[s]["nDCG@5"].append(nd)
            summary[s]["H" if mode == "HEADLINE" else "F"] += 1
            row[s] = {"label": d["label"], "mode": mode, "P@5": p5, "nDCG@5": nd}
        per_q.append(row)

    def mean(xs):
        xs = [x for x in xs if x is not None]
        return sum(xs) / len(xs) if xs else None

    out = {
        "n": len(qmap),
        "gold_room_from_protocol": gold,
        "summary": {
            s: {
                "mean_P@5": mean(summary[s]["P@5"]),
                "mean_nDCG@5": mean(summary[s]["nDCG@5"]),
                "n_headline": summary[s]["H"],
                "n_full": summary[s]["F"],
            }
            for s in SYSTEMS
        },
        "per_query": per_q,
    }
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    lines = ["FROZEN HELD-OUT ROUTED P@5", f"n={len(qmap)}", ""]
    lines.append(f"{'system':20} {'P@5':>8} {'nDCG@5':>8} {'->H':>5} {'->F':>5}")
    for s in SYSTEMS:
        sm = out["summary"][s]
        lines.append(
            f"{s:20} {sm['mean_P@5']:.4f} {sm['mean_nDCG@5']:.4f} "
            f"{sm['n_headline']:5d} {sm['n_full']:5d}"
        )
    text = "\n".join(lines) + "\n"
    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write(text)
    print(text)


if __name__ == "__main__":
    main()
