# -*- coding: utf-8 -*-
"""Phase 10A: recover Phase 9 evidence only. No BM25 rerun. No labels."""
from __future__ import annotations

import csv
import os
import sys

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "validate", "dual_index_routing", "labels"))
from heldout_traps import HELDOUT_TRAPS  # noqa: E402

P9 = os.path.join(ROOT, "experiments", "phase9_heldout_evaluation", "HELD_OUT_PER_QUERY.csv")
CORPUS = os.path.join(ROOT, "data", "clean_articles.csv")
OUT_DIR = os.path.join(ROOT, "artifacts", "phase10")
OUT_CSV = os.path.join(OUT_DIR, "HELD_OUT_RETRIEVAL_DETAILS.csv")
SNIP = 500


def clip(s):
    s = (s or "").replace("\r", " ").replace("\n", " ").strip()
    return s if len(s) <= SNIP else s[: SNIP - 1] + "…"


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    qmap = {item[0]: item[4] for item in HELDOUT_TRAPS}
    df = pd.read_csv(CORPUS, encoding="utf-8-sig")
    head = df["Headline"].fillna("").astype(str)
    news = df["News Text"].fillna("").astype(str) if "News Text" in df.columns else pd.Series([""] * len(df))

    rows = []
    with open(P9, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            qid = r["query_id"]
            did = int(r["top1_doc_id"]) if r["top1_doc_id"] else None
            if did is None:
                continue
            rows.append({
                "query_id": qid,
                "query_text": qmap[qid],
                "detector_label": r["detector_label"],
                "retrieval_path": r["retrieval_path"],
                "rank": 1,
                "doc_id": did,
                "headline": str(head[did]),
                "news_text_or_snippet": clip(str(news[did])),
                "n_hits_returned_phase9": r["n_hits_returned"],
                "ranks_2_to_5_recovered": 0,
            })
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print("wrote %s rows=%s" % (OUT_CSV, len(rows)))


if __name__ == "__main__":
    main()
