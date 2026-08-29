# -*- coding: utf-8 -*-
import json
from pathlib import Path

import pandas as pd

root = Path(__file__).resolve().parents[2]
miss = json.loads(
    (root / "experiments/phase6_residual_diagnosis/artifacts/miss_details.json").read_text(encoding="utf-8")
)
df = pd.read_csv(root / "data/clean_articles.csv", encoding="utf-8-sig")
head = df["Headline"].fillna("").astype(str)
body = df["News Text"].fillna("").astype(str)
out = {}
for m in miss:
    pack = {
        "query_id": m["query_id"],
        "split": m["split"],
        "query_type": m["query_type"],
        "query": m["query"],
        "gold_source_id": m["source_doc_id"],
        "gold_source_rank": m["script_aware_rank"],
        "gold_headline": m["source_headline"],
        "gold_body": str(body[int(m["source_doc_id"])]).replace("\n", " ")[:500],
        "top5": [],
    }
    for i, t in enumerate(m["top5_script_aware"], 1):
        did = int(t["doc_id"])
        pack["top5"].append({
            "rank": i,
            "doc_id": did,
            "headline": str(head[did]),
            "body": str(body[did]).replace("\n", " ")[:450],
        })
    out[m["query_id"]] = pack

art = Path(__file__).resolve().parent / "artifacts"
art.mkdir(parents=True, exist_ok=True)
(art / "annotation_units.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

dev = ["QTRN_168", "QTRN_170", "QTRN_189", "QTRN_225"]
for qid in dev:
    p = out[qid]
    print("=" * 70)
    print(qid, p["query_type"], "gold", p["gold_source_id"], "rank", p["gold_source_rank"])
    print("Q:", p["query"])
    print("GOLD H:", p["gold_headline"])
    print("GOLD B:", p["gold_body"][:300])
    for t in p["top5"]:
        print("  r%s [%s] %s" % (t["rank"], t["doc_id"], t["headline"]))
        print("   ", t["body"][:240])
