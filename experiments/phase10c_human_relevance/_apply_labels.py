# -*- coding: utf-8 -*-
"""Apply Phase 10C human labels to the frozen 10B Top-5 dump. No retrieval."""
from __future__ import annotations

import csv
import os
from collections import Counter, defaultdict

_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(_DIR, "..", ".."))
SRC = os.path.join(ROOT, "experiments", "phase10b_frozen_dump", "TOP5_FOR_ANNOTATION.csv")
OUT = os.path.join(_DIR, "HELD_OUT_QRELS.csv")

# One label per Top-5 (or fewer) row, in CSV order within each query.
LABELS = {
    "H001": list("CCCCC"),
    "H002": list("BBCBB"),
    "H003": list("DDDBD"),
    "H004": list("AAAAB"),
    "H005": list("BBCBB"),
    "H006": list("BBBCB"),
    "H007": list("DDDDD"),
    "H008": list("CDDDC"),
    "H009": list("CCCCB"),
    "H010": list("DDDDD"),
    "H011": list("DDBDD"),
    "H012": list("CCCCA"),
    "H013": list("CCBCC"),
    "H014": list("BDDDD"),
    "H015": list("DDDDD"),
    "H016": list("DDDDD"),
    "H017": list("ADDDD"),
    "H018": list("AAAAA"),
    "H019": list("ACCAC"),
    "H020": list("DDDDD"),
    "H021": list("DDCDD"),
    "H022": list("AACAD"),
    "H023": list("AABBB"),
    "H024": list("CCCCC"),
    "H025": list("DDDDD"),
    "H026": list("BDDDD"),
    "H027": list("DDDDD"),
    "H028": list("DDDDD"),
    "H029": list("DDDDD"),
    "H030": list("CDDDB"),
    "H031": list("CCCCB"),
    "H032": list("DDAAB"),
    "H033": list("BABBB"),
    "H034": list("AABDD"),
    "H035": list("BCAAC"),
    "H036": list("D"),
    "H037": list("CCBBB"),
    "H038": list("BBBCB"),
    "H039": list("BBBCB"),
    "H040": list("DDDCC"),
}

TEMPORAL_MARKERS = ("آج", "aaj", "موجودہ", "mojooda")


def asks_today(q: str) -> int:
    ql = q.lower()
    for m in TEMPORAL_MARKERS:
        if m.lower() in ql or m in q:
            return 1
    return 0


def main():
    rows = list(csv.DictReader(open(SRC, encoding="utf-8")))
    assert len(rows) == 196, len(rows)
    grouped = defaultdict(list)
    for r in rows:
        grouped[r["query_id"]].append(r)
    out_rows = []
    for qid in ["H%03d" % i for i in range(1, 41)]:
        labs = LABELS[qid]
        items = grouped[qid]
        assert len(items) == len(labs), (qid, len(items), len(labs))
        qt = items[0]["query_text"]
        today = asks_today(qt)
        for r, lab in zip(items, labs):
            assert (r.get("relevance_label") or "").strip() == ""
            rec = dict(r)
            rec["relevance_label"] = lab
            rec["query_asks_today"] = today
            rec["experiment_id"] = "phase10b_frozen_dump"
            out_rows.append(rec)
    fields = [
        "experiment_id",
        "query_id",
        "query_text",
        "detector_label",
        "retrieval_path",
        "rank",
        "doc_id",
        "bm25_score",
        "headline",
        "news_text_or_snippet",
        "n_hits_returned",
        "relevance_label",
        "query_asks_today",
    ]
    os.makedirs(_DIR, exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(out_rows)

    dist = Counter(r["relevance_label"] for r in out_rows)
    by_q = defaultdict(list)
    for r in out_rows:
        by_q[r["query_id"]].append(r)
    n_success = 0
    p5_cons = []
    p5_var = []
    all_d = []
    for qid in ["H%03d" % i for i in range(1, 41)]:
        labs = [x["relevance_label"] for x in by_q[qid]]
        n_hits = int(by_q[qid][0]["n_hits_returned"])
        n_a = labs.count("A")
        if any(x in ("A", "B") for x in labs):
            n_success += 1
        p5_cons.append(n_a / 5.0)
        p5_var.append(n_a / float(min(5, n_hits)))
        if labs and all(x == "D" for x in labs):
            all_d.append(qid)
    temporal_q = sorted({r["query_id"] for r in out_rows if int(r["query_asks_today"]) == 1})
    print("rows", len(out_rows))
    print("dist", dict(dist))
    print("success", n_success, n_success / 40)
    print("p5_cons", sum(p5_cons) / 40)
    print("p5_var", sum(p5_var) / 40)
    print("all_d", len(all_d), all_d)
    print("temporal", len(temporal_q), temporal_q)


if __name__ == "__main__":
    main()
