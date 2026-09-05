# -*- coding: utf-8 -*-
"""
R-dev NAT annotation on frozen M0 Top-5 (R051-R100).

Single annotator (thesis author). Does not rerun retrieval.
Reads R_TOP5_FOR_ANNOTATION.csv only; writes qrels_r_dev.csv + manifest.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
from collections import Counter, defaultdict
from datetime import date

_DIR = os.path.dirname(os.path.abspath(__file__))
TOP5 = os.path.join(_DIR, "R_TOP5_FOR_ANNOTATION.csv")
QUERIES = os.path.join(_DIR, "queries_r_dev.csv")
RETRIEVAL_MANIFEST = os.path.join(_DIR, "RETRIEVAL_MANIFEST.json")
OUT_QRELS = os.path.join(_DIR, "qrels_r_dev.csv")
OUT_MANIFEST = os.path.join(_DIR, "ANNOTATION_MANIFEST.json")

EXPECTED_QUERY_SHA = "1603b37eeee41fa6270f4e13d185c8eebd4512d025cd5fc67e8a81de9407e75f"
EXPECTED_TOP5_SHA = "042006bc3232719514a6ca4b638f4e6348415d168294271fe366ff95704b23c5"
ANNOTATOR = "thesis_author_single"
ANNOTATION_DATE = "2026-09-01"
RUBRIC = "experiments/phase12_human_relevance/ANNOTATION_PROTOCOL.md (Phase 7 A-E)"

# query_id -> labels for ranks 1..5 (headline + snippet only; system-blind)
LABELS = {
    "R051": ["A", "D", "D", "D", "D"],
    "R052": ["A", "A", "A", "A", "A"],
    "R053": ["D", "D", "C", "B", "D"],
    "R054": ["A", "B", "B", "B", "C"],
    "R055": ["D", "D", "D", "D", "D"],
    "R056": ["C", "B", "C", "D", "D"],
    "R057": ["D", "D", "C", "D", "D"],
    "R058": ["C", "C", "B", "C", "D"],
    "R059": ["D", "D", "D", "D", "D"],
    "R060": ["D", "D", "D", "D", "D"],
    "R061": ["B", "B", "B", "C", "B"],
    "R062": ["D", "D", "D", "D", "D"],
    "R063": ["D", "D", "D", "D", "D"],
    "R064": ["A", "A", "A", "A", "A"],
    "R065": ["D", "D", "C", "D", "D"],
    "R066": ["D", "D", "D", "D", "D"],
    "R067": ["D", "D", "D", "D", "D"],
    "R068": ["D", "D", "D", "D", "D"],
    "R069": ["C", "D", "D", "C", "D"],
    "R070": ["D", "D", "D", "D", "D"],
    "R071": ["D", "D", "D", "D", "D"],
    "R072": ["D", "D", "D", "D", "D"],
    "R073": ["D", "D", "D", "D", "D"],
    "R074": ["D", "D", "D", "C", "B"],
    "R075": ["D", "D", "D", "D", "D"],
    "R076": ["D", "C", "C", "D", "D"],
    "R077": ["D", "D", "D", "D", "D"],
    "R078": ["D", "D", "D", "D", "D"],
    "R079": ["D", "D", "D", "D", "D"],
    "R081": ["D", "D", "D", "D", "D"],
    "R082": ["D", "D", "D", "D", "D"],
    "R083": ["D", "D", "D", "D", "D"],
    "R084": ["D", "D", "D", "D", "D"],
    "R085": ["C", "C", "D", "D", "C"],
    "R086": ["A", "A", "A", "A", "D"],
    "R087": ["D", "B", "C", "C", "D"],
    "R088": ["D", "D", "D", "D", "D"],
    "R089": ["D", "D", "D", "D", "D"],
    "R090": ["D", "D", "D", "D", "D"],
    "R091": ["D", "D", "D", "D", "D"],
    "R092": ["D", "D", "D", "C", "D"],
    "R093": ["D", "D", "D", "D", "D"],
    "R094": ["D", "D", "D", "D", "D"],
    "R095": ["D", "C", "D", "D", "C"],
    "R096": ["B", "C", "C", "C", "C"],
    "R097": ["D", "D", "D", "D", "D"],
    "R098": ["D", "D", "D", "D", "D"],
    "R099": ["D", "D", "D", "D", "D"],
    "R100": ["D", "D", "D", "D", "C"],
}


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(1024 * 1024)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def main():
    q_sha = sha256_file(QUERIES)
    t5_sha = sha256_file(TOP5)
    if q_sha != EXPECTED_QUERY_SHA:
        raise RuntimeError("queries_r_dev SHA mismatch: %s" % q_sha)
    if t5_sha != EXPECTED_TOP5_SHA:
        raise RuntimeError("R_TOP5 SHA mismatch: %s" % t5_sha)

    nat_rows = []
    with open(TOP5, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if r["track"] == "NAT":
                nat_rows.append(r)

    by_q = defaultdict(list)
    for r in nat_rows:
        by_q[r["query_id"]].append(r)

    qrels = []
    for qid in sorted(by_q):
        rows = sorted(by_q[qid], key=lambda x: int(x["rank"]))
        if qid not in LABELS:
            raise RuntimeError("missing labels for %s" % qid)
        labs = LABELS[qid]
        if len(labs) != len(rows):
            raise RuntimeError(
                "label count mismatch %s: labels=%s rows=%s"
                % (qid, len(labs), len(rows))
            )
        for r, lab in zip(rows, labs):
            qrels.append({
                "query_id": qid,
                "doc_id": int(r["doc_id"]),
                "rank": int(r["rank"]),
                "relevance_label": lab,
                "annotator": ANNOTATOR,
                "annotation_date": ANNOTATION_DATE,
            })

    fields = [
        "query_id", "doc_id", "rank", "relevance_label",
        "annotator", "annotation_date",
    ]
    with open(OUT_QRELS, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(qrels)

    # Success@5: >=1 A or B in available Top-5 per NAT query (50 total incl. zero-hit)
    success_ids = []
    for qid in ["R%03d" % i for i in range(51, 101)]:
        labs = [x["relevance_label"] for x in qrels if x["query_id"] == qid]
        if any(x in ("A", "B") for x in labs):
            success_ids.append(qid)

    zero_hit = ["R080"]
    short_hit = {
        qid: len(by_q[qid])
        for qid in by_q
        if len(by_q[qid]) < 5
    }

    ret_man = {}
    if os.path.isfile(RETRIEVAL_MANIFEST):
        with open(RETRIEVAL_MANIFEST, encoding="utf-8") as f:
            ret_man = json.load(f)

    qrels_sha = sha256_file(OUT_QRELS)
    manifest = {
        "experiment_id": "post_phase12_r_dev",
        "stage": "NAT_annotation_only",
        "annotation_protocol": RUBRIC,
        "annotation_date": ANNOTATION_DATE,
        "annotator_count": 1,
        "annotator_mode": "single_annotator_r_dev",
        "annotators": [ANNOTATOR],
        "adjudication_occurred": False,
        "inter_annotator_agreement": None,
        "system_blind": True,
        "queries_r_dev_sha256": q_sha,
        "m0_top5_sha256": t5_sha,
        "m0_retrieval_manifest": "RETRIEVAL_MANIFEST.json",
        "m0_retrieval_pass_count": ret_man.get("retrieval_pass_count", 1),
        "retrieval_rerun": False,
        "nat_query_count": 50,
        "nat_queries_annotated": sorted(by_q.keys()) + zero_hit,
        "nat_judgments_available": len(qrels),
        "nat_judgments_expected_if_full_top5": 250,
        "zero_result_nat_queries": zero_hit,
        "short_top5_nat_queries": short_hit,
        "label_counts": dict(Counter(x["relevance_label"] for x in qrels)),
        "m0_nat_success_at_5": {
            "hits": len(success_ids),
            "n": 50,
            "rate": round(len(success_ids) / 50, 4),
            "successful_query_ids": success_ids,
        },
        "metrics_computed": ["Success@5"],
        "metrics_not_computed": [
            "KI_Hit@5", "nDCG", "MRR", "P@5",
            "candidate_comparison", "Module_1", "Module_2",
        ],
        "qrels_file": "qrels_r_dev.csv",
        "qrels_sha256": qrels_sha,
        "qrels_rows": len(qrels),
        "deviations": [
            "Single annotator used (thesis author); dual annotation not available.",
            "R080: zero M0 hits — no qrels rows (preserved as retrieved).",
            "R066/R083: 29 hits returned; Top-5 preserved from sealed retrieval.",
        ],
        "candidate_modules_evaluated": False,
        "retrieval_modified": False,
        "stopped_after_annotation": True,
    }
    with open(OUT_MANIFEST, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print("qrels_rows=%s" % len(qrels))
    print("Success@5=%s/50=%.4f" % (len(success_ids), len(success_ids) / 50))
    print("label_counts=%s" % dict(Counter(x["relevance_label"] for x in qrels)))
    print("qrels_sha256=%s" % qrels_sha)


if __name__ == "__main__":
    main()
