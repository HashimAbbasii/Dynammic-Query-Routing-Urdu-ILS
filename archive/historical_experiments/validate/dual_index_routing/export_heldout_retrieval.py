# -*- coding: utf-8 -*-
"""
Export HEADLINE vs FULL_CONTENT top-5 lists for the frozen held-out 40.

Does not train. Does not judge relevance. Student (or a later judge) fills
the relevance column.

40 queries x 2 rooms x 5 ranks = 400 rows.
"""
from __future__ import annotations

import csv
import os
import sys

_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _DIR)
sys.path.insert(0, os.path.join(_DIR, "labels"))

from heldout_traps import HELDOUT_TRAPS  # noqa: E402
from retrieve import (  # noqa: E402
    FULL_CONTENT,
    HEADLINE,
    search_full_content,
    search_headlines,
    transliterate_roman,
    _ensure_indexes,
    _format_hits,
)

OUT = os.path.join(_DIR, "labels", "heldout_retrieval_template.csv")
TOP_K = 5


def main():
    _ensure_indexes()
    fields = [
        "query_id",
        "query",
        "script",
        "word_count",
        "trap_type",
        "retrieval_mode",
        "rank",
        "doc_id",
        "doc_headline",
        "doc_category",
        "score",
        "relevance",
    ]
    rows = []
    for qid, trap_type, script, category, query, gold in HELDOUT_TRAPS:
        processed, _ = transliterate_roman(query)
        n = len(query.split())
        for mode, search in (
            (HEADLINE, search_headlines),
            (FULL_CONTENT, search_full_content),
        ):
            hits = _format_hits(search(processed, top_k=TOP_K))
            for h in hits:
                rows.append(
                    {
                        "query_id": qid,
                        "query": query,
                        "script": script,
                        "word_count": n,
                        "trap_type": trap_type,
                        "retrieval_mode": mode,
                        "rank": h["rank"],
                        "doc_id": h["doc_id"],
                        "doc_headline": h["headline"],
                        "doc_category": h["category"],
                        "score": f"{h['score']:.6f}",
                        "relevance": "UNJUDGED",
                    }
                )
        print(qid, "exported")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {len(rows)} rows to {OUT}")


if __name__ == "__main__":
    main()
