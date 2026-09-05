# -*- coding: utf-8 -*-
"""
M3-E Phase 1: materialize union pool + system-blind annotation sheet.
Does not annotate. Does not modify frozen qrels or retrieval CSVs.
"""
from __future__ import annotations

import csv
import hashlib
import json
import random
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
R_DEV = ROOT / "experiments" / "post_phase12_development"
M3E = R_DEV / "m3e_evaluation"
CORPUS = ROOT / "data" / "clean_articles.csv"

QUERY_PATH = R_DEV / "queries_r_dev.csv"
M0_TOP50 = R_DEV / "R_TOP50_RETRIEVAL.csv"
M0_TOP5 = R_DEV / "R_TOP5_FOR_ANNOTATION.csv"
QRELS_PATH = R_DEV / "qrels_r_dev.csv"
M2A_PATH = R_DEV / "module2" / "M2-A_TOP50_RETRIEVAL.csv"
M2B_PATH = R_DEV / "module2" / "M2-B_TOP50_RETRIEVAL.csv"
PROTOCOL = M3E / "M3E_UNION_POOL_NAT_PROTOCOL.md"

EXPECTED = {
    "queries_r_dev.csv": "1603b37eeee41fa6270f4e13d185c8eebd4512d025cd5fc67e8a81de9407e75f",
    "R_TOP50_RETRIEVAL.csv": "927a14a25b6f1de2a5c28aabdc2d8cbc0d4336e0b2b437490691a7bff63a2aa2",
    "R_TOP5_FOR_ANNOTATION.csv": "042006bc3232719514a6ca4b638f4e6348415d168294271fe366ff95704b23c5",
    "qrels_r_dev.csv": "506305b5401102a3659d21b69c7a937bcdcde78b21a1409a6a6132255ff37bcb",
}

SHUFFLE_SEED = 20260905


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(1 << 20)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def load_nat_queries():
    rows = []
    with open(QUERY_PATH, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if r["track"] == "NAT":
                rows.append(r)
    return rows


def load_top5(path: Path) -> dict[str, list[int]]:
    by = defaultdict(list)
    with open(path, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if r.get("track") and r["track"] != "NAT":
                continue
            rank = int(r["rank"])
            if rank <= 5:
                by[r["query_id"]].append((rank, int(r["doc_id"])))
    out = {}
    for qid, pairs in by.items():
        out[qid] = [d for _, d in sorted(pairs)]
    return out


def load_qrels():
    labels = {}
    with open(QRELS_PATH, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            labels[(r["query_id"], int(r["doc_id"]))] = {
                "relevance_label": r["relevance_label"],
                "annotator": r.get("annotator", "thesis_author_single"),
                "annotation_date": r.get("annotation_date", ""),
            }
    return labels


def load_detectors_m0():
    det = {}
    with open(M0_TOP50, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if r["query_id"] not in det:
                det[r["query_id"]] = r["detector_label"]
    return det


def snippet(text: str, n: int = 320) -> str:
    t = " ".join((text or "").split())
    return t[:n]


def main():
    M3E.mkdir(parents=True, exist_ok=True)
    failed = []
    hashes = {}
    for name, exp in EXPECTED.items():
        path = {
            "queries_r_dev.csv": QUERY_PATH,
            "R_TOP50_RETRIEVAL.csv": M0_TOP50,
            "R_TOP5_FOR_ANNOTATION.csv": M0_TOP5,
            "qrels_r_dev.csv": QRELS_PATH,
        }[name]
        h = sha256_file(path)
        hashes[name] = h
        if h != exp:
            failed.append(name)
    hashes["M2-A_TOP50_RETRIEVAL.csv"] = sha256_file(M2A_PATH)
    hashes["M2-B_TOP50_RETRIEVAL.csv"] = sha256_file(M2B_PATH)
    hashes["M3E_UNION_POOL_NAT_PROTOCOL.md"] = sha256_file(PROTOCOL)
    if failed:
        raise SystemExit("STOP frozen hash mismatch: %s" % failed)

    nat = load_nat_queries()
    if len(nat) != 50:
        raise SystemExit("STOP NAT count != 50")
    nat_ids = [r["query_id"] for r in nat]
    qtext = {r["query_id"]: r["query_text"] for r in nat}

    m0 = load_top5(M0_TOP50)
    m2a = load_top5(M2A_PATH)
    m2b = load_top5(M2B_PATH)
    qrels = load_qrels()
    det = load_detectors_m0()

    # Sanity: legacy M0 Success@5
    legacy_hits = 0
    for qid in nat_ids:
        labs = [qrels.get((qid, d), {}).get("relevance_label") for d in m0.get(qid, [])]
        if any(x in ("A", "B") for x in labs):
            legacy_hits += 1
    if legacy_hits != 12:
        raise SystemExit("STOP legacy M0 Success@5 = %s/50 (expected 12)" % legacy_hits)

    import pandas as pd
    df = pd.read_csv(CORPUS, encoding="utf-8-sig", usecols=["Index", "Headline", "News Text"])
    head = dict(zip(df["Index"].astype(int), df["Headline"].fillna("").astype(str)))
    body = dict(zip(df["Index"].astype(int), df["News Text"].fillna("").astype(str)))

    pool_rows = []  # provenance
    sheet_rows = []
    new_pairs = []
    carried = 0
    rng = random.Random(SHUFFLE_SEED)

    for qid in nat_ids:
        systems = {
            "M0": m0.get(qid, []),
            "M2-A": m2a.get(qid, []),
            "M2-B": m2b.get(qid, []),
        }
        doc_systems = defaultdict(set)
        for sys, docs in systems.items():
            for d in docs:
                doc_systems[d].add(sys)
        pool_docs = sorted(doc_systems.keys())
        # shuffle for blind sheet
        order = pool_docs[:]
        rng.shuffle(order)
        for pos, did in enumerate(order, 1):
            label_info = qrels.get((qid, did))
            is_carried = label_info is not None
            if is_carried:
                carried += 1
                label_source = "carried_m0"
            else:
                label_source = "needs_new"
                new_pairs.append({
                    "query_id": qid,
                    "query_text": qtext[qid],
                    "doc_id": did,
                    "headline": head.get(did, ""),
                    "snippet": snippet(body.get(did, "")),
                    "detector_label_m0": det.get(qid, ""),
                })
            pool_rows.append({
                "query_id": qid,
                "doc_id": did,
                "systems": "|".join(sorted(doc_systems[did])),
                "in_M0_top5": "M0" in doc_systems[did],
                "in_M2A_top5": "M2-A" in doc_systems[did],
                "in_M2B_top5": "M2-B" in doc_systems[did],
                "label_source_planned": label_source,
                "carried_label": label_info["relevance_label"] if is_carried else "",
            })
            sheet_rows.append({
                "annotation_row_id": "%s_%s" % (qid, did),
                "query_id": qid,
                "query_text": qtext[qid],
                "doc_id": did,
                "headline": head.get(did, ""),
                "snippet": snippet(body.get(did, "")),
                "shuffle_position": pos,
                # blinding: no system/rank/score columns on annotator-facing sheet
            })

    # Write pool provenance (analyst-only; contains system membership)
    pool_csv = M3E / "M3E_POOL_PROVENANCE.csv"
    with open(pool_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(pool_rows[0].keys()))
        w.writeheader()
        w.writerows(pool_rows)

    sheet_csv = M3E / "M3E_ANNOTATION_SHEET.csv"
    with open(sheet_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "annotation_row_id", "query_id", "query_text", "doc_id",
                "headline", "snippet", "shuffle_position",
            ],
        )
        w.writeheader()
        w.writerows(sheet_rows)

    new_jsonl = M3E / "M3E_NEW_PAIRS_FOR_JUDGMENT.jsonl"
    with open(new_jsonl, "w", encoding="utf-8") as f:
        for row in new_pairs:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    # Top5 maps for later scoring
    top5_maps = {
        "M0": {qid: m0.get(qid, []) for qid in nat_ids},
        "M2-A": {qid: m2a.get(qid, []) for qid in nat_ids},
        "M2-B": {qid: m2b.get(qid, []) for qid in nat_ids},
    }
    with open(M3E / "M3E_SYSTEM_TOP5.json", "w", encoding="utf-8") as f:
        json.dump(top5_maps, f, indent=2)

    sizes = [len(set(m0.get(q, [])) | set(m2a.get(q, [])) | set(m2b.get(q, []))) for q in nat_ids]
    manifest = {
        "stage": "m3e_pool_materialization",
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "protocol_file": "M3E_UNION_POOL_NAT_PROTOCOL.md",
        "protocol_sha256": hashes["M3E_UNION_POOL_NAT_PROTOCOL.md"],
        "frozen_input_sha256": hashes,
        "legacy_m0_success_at_5": "%s/50" % legacy_hits,
        "nat_query_count": 50,
        "systems_in_union": ["M0", "M2-A", "M2-B"],
        "depth": 5,
        "shuffle_seed": SHUFFLE_SEED,
        "unique_pool_pairs": len(pool_rows),
        "carried_m0_pairs": carried,
        "new_pairs_to_annotate": len(new_pairs),
        "pool_size_per_query": {
            "min": min(sizes),
            "median": sorted(sizes)[len(sizes) // 2],
            "max": max(sizes),
            "mean": round(sum(sizes) / len(sizes), 2),
        },
        "r080": {
            "in_m0_top5": len(m0.get("R080", [])),
            "in_m2a_top5": len(m2a.get("R080", [])),
            "in_m2b_top5": len(m2b.get("R080", [])),
            "denominator": True,
        },
        "qrels_r_dev_csv_overwrite": False,
        "retrieval_rerun": False,
    }
    with open(M3E / "M3E_POOL_MANIFEST.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print("POOL_OK pairs=%s carried=%s new=%s legacy_m0=%s/50" % (
        len(pool_rows), carried, len(new_pairs), legacy_hits))
    print("SHEET", sheet_csv)
    print("NEW_JSONL", new_jsonl)


if __name__ == "__main__":
    main()
