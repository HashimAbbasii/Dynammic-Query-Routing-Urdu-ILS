# -*- coding: utf-8 -*-
"""Phase 12 U human labels + metrics. No retrieval. Reads frozen Top-5 only."""
from __future__ import annotations

import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOP5 = ROOT / "experiments/phase12_new_unseen_evaluation/U_TOP5_FOR_ANNOTATION.csv"
QUERIES = ROOT / "experiments/phase12_new_unseen_evaluation/queries_u.csv"
OUT = ROOT / "experiments/phase12_human_relevance"
ART = OUT / "artifacts"

# query_id -> labels for ranks 1-5 (Phase 7 A-E + Phase 12 temporal type-of-fact)
LABELS = {
    "U001": ["A", "B", "B", "B", "C"],
    "U002": ["A", "D", "D", "D", "D"],
    "U003": ["A", "A", "A", "C", "B"],
    "U004": ["D", "D", "D", "D", "D"],
    "U005": ["A", "A", "A", "A", "A"],
    "U006": ["D", "D", "D", "D", "D"],
    "U007": ["D", "B", "C", "C", "C"],
    "U008": ["D", "D", "D", "D", "D"],
    "U009": ["C", "B", "C", "C", "B"],
    "U010": ["D", "D", "D", "D", "D"],
    "U011": ["A", "A", "A", "A", "A"],
    "U012": ["A", "D", "D", "C", "A"],
    "U013": ["A", "A", "A", "A", "A"],
    "U014": ["D", "D", "D", "D", "D"],
    "U015": ["C", "C", "B", "D", "B"],
    "U016": ["D", "D", "D", "D", "D"],
    "U017": ["B", "C", "B", "C", "D"],
    "U018": ["C", "C", "C", "D", "D"],
    "U019": ["B", "A", "A", "B", "A"],
    "U020": ["D", "D", "D", "D", "D"],
    "U021": ["C", "C", "C", "B", "C"],
    "U022": ["D", "C", "C", "B", "B"],
    "U023": ["B", "D", "B", "D", "D"],
    "U024": ["D", "B", "C", "C", "C"],
    "U025": ["C", "C", "B", "C", "C"],
    "U026": ["D", "D", "D", "D", "D"],
    "U027": ["B", "B", "B", "B", "C"],
    "U028": ["D", "D", "D", "D", "D"],
    "U029": ["A", "A", "A", "A", "A"],
    "U030": ["A", "A", "A", "A", "A"],
    "U031": ["A", "C", "C", "A", "A"],
    "U032": ["D", "D", "D", "D", "D"],
    "U033": ["A", "B", "D", "D", "C"],
    "U034": ["D", "D", "D", "D", "D"],
    "U035": ["C", "C", "C", "C", "D"],
    "U036": ["C", "B", "A", "D", "A"],
    "U037": ["C", "C", "C", "C", "C"],
    "U038": ["C", "C", "C", "C", "C"],
    "U039": ["C", "C", "C", "C", "C"],
    "U040": ["D", "D", "D", "D", "D"],
}

GAINS = {"A": 3, "B": 2, "C": 1, "D": 0, "E": 0}
TEMPORAL_MARKERS = ("آج", "aaj", "موجودہ", "mojooda")


def dcg(gains):
    s = 0.0
    for i, g in enumerate(gains, 1):
        s += g / math.log2(i + 1)
    return s


def ndcg5(labels):
    gains = [GAINS[x] for x in labels]
    actual = dcg(gains)
    ideal = dcg(sorted(gains, reverse=True))
    if ideal <= 0:
        return 0.0
    return actual / ideal


def first_ab(labels):
    for i, lab in enumerate(labels, 1):
        if lab in ("A", "B"):
            return i
    return None


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ART.mkdir(parents=True, exist_ok=True)

    qmeta = {}
    with QUERIES.open(encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            qmeta[r["query_id"]] = r

    rows = list(csv.DictReader(TOP5.open(encoding="utf-8-sig", newline="")))
    if len(rows) != 200:
        raise SystemExit("expected 200 top-5 rows, got %s" % len(rows))
    for r in rows:
        if (r.get("relevance_label") or "").strip():
            raise SystemExit("frozen dump already labeled; abort")

    qrels = []
    by_q = defaultdict(list)
    for r in rows:
        by_q[r["query_id"]].append(r)

    for qid in ["U%03d" % i for i in range(1, 41)]:
        labs = LABELS[qid]
        items = sorted(by_q[qid], key=lambda x: int(x["rank"]))
        if len(items) != 5:
            raise SystemExit("%s has %s rows" % (qid, len(items)))
        if len(labs) != 5:
            raise SystemExit("%s labels %s" % (qid, labs))
        qtext = items[0]["query_text"]
        temporal = int(any(m in qtext.split() for m in TEMPORAL_MARKERS))
        for rec, lab in zip(items, labs):
            qrels.append({
                "experiment_id": "phase12_human_relevance",
                "retrieval_experiment_id": "phase12_new_unseen_evaluation",
                "query_id": qid,
                "query_text": rec["query_text"],
                "need_type": qmeta[qid]["need_type"],
                "length_bin": qmeta[qid]["length_bin"],
                "script_intended": qmeta[qid]["script_intended"],
                "detector_label": rec["detector_label"],
                "retrieval_path": rec["retrieval_path"],
                "category": qmeta[qid]["category"],
                "query_asks_today": temporal,
                "rank": int(rec["rank"]),
                "doc_id": rec["doc_id"],
                "bm25_score": rec["bm25_score"],
                "headline": rec["headline"],
                "news_text_or_snippet": rec["news_text_or_snippet"],
                "n_hits_returned": rec["n_hits_returned"],
                "relevance_label": lab,
            })

    qrel_path = OUT / "U_QRELS.csv"
    fields = list(qrels[0].keys())
    with qrel_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(qrels)

    per = []
    for qid in ["U%03d" % i for i in range(1, 41)]:
        labs = LABELS[qid]
        n_a = labs.count("A")
        n_hits = int(by_q[qid][0]["n_hits_returned"])
        denom = min(5, n_hits)
        ab = first_ab(labs)
        meta = qmeta[qid]
        rec = qrels[[i for i, x in enumerate(qrels) if x["query_id"] == qid][0]]
        per.append({
            "query_id": qid,
            "query_text": meta["query_text"],
            "need_type": meta["need_type"],
            "length_bin": meta["length_bin"],
            "script": rec["detector_label"],
            "path": rec["retrieval_path"],
            "category": meta["category"],
            "temporal": rec["query_asks_today"],
            "labels": "".join(labs),
            "r1": labs[0], "r2": labs[1], "r3": labs[2], "r4": labs[3], "r5": labs[4],
            "n_A": n_a,
            "success@5": int(ab is not None),
            "first_AB_rank": ab if ab is not None else "",
            "p5_cons": n_a / 5.0,
            "p5_var": n_a / float(denom),
            "ndcg@5": ndcg5(labs),
            "rr": (1.0 / ab) if ab else 0.0,
            "n_hits_returned": n_hits,
        })

    n = 40
    success_n = sum(p["success@5"] for p in per)
    metrics = {
        "experiment_id": "phase12_human_relevance",
        "n_queries": n,
        "n_docs_labeled": 200,
        "gain_mapping": {"A": 3, "B": 2, "C": 1, "D": 0, "E": 0},
        "success@5": {"hits": success_n, "n": n, "rate": round(success_n / n, 4)},
        "conservative_p@5": round(sum(p["p5_cons"] for p in per) / n, 4),
        "variable_p@5": round(sum(p["p5_var"] for p in per) / n, 4),
        "ndcg@5": round(sum(p["ndcg@5"] for p in per) / n, 4),
        "mrr": round(sum(p["rr"] for p in per) / n, 4),
        "label_counts": dict(Counter(r["relevance_label"] for r in qrels)),
        "all_D_queries": [p["query_id"] for p in per if p["labels"] == "DDDDD"],
        "fail_no_AB": [p["query_id"] for p in per if p["success@5"] == 0],
        "h001_h040_used": False,
        "phase10c_qrels_used": False,
        "retrieval_rerun": False,
        "m0_modified": False,
        "exactsource_hit@5_not_computed": True,
    }

    def rate(ids):
        sub = [p for p in per if p["query_id"] in ids]
        if not sub:
            return None
        s = sum(x["success@5"] for x in sub)
        return {"hits": s, "n": len(sub), "rate": round(s / len(sub), 4)}

    def group(key):
        buckets = defaultdict(list)
        for p in per:
            buckets[p[key]].append(p["query_id"])
        return {k: rate(v) for k, v in sorted(buckets.items())}

    metrics["breakdown_script"] = group("script")
    metrics["breakdown_need_type"] = group("need_type")
    metrics["breakdown_length"] = group("length_bin")
    metrics["breakdown_temporal"] = {
        "temporal": rate([p["query_id"] for p in per if p["temporal"] == 1]),
        "non_temporal": rate([p["query_id"] for p in per if p["temporal"] == 0]),
    }

    with (ART / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)

    pq_path = OUT / "U_PER_QUERY.csv"
    pq_fields = [
        "query_id", "query_text", "need_type", "length_bin", "script", "path",
        "category", "temporal", "r1", "r2", "r3", "r4", "r5", "success@5",
        "first_AB_rank", "n_A", "p5_cons", "ndcg@5", "rr",
    ]
    with pq_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=pq_fields, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(per)

    print(json.dumps(metrics, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
