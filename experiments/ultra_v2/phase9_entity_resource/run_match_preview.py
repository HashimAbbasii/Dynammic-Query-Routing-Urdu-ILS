# -*- coding: utf-8 -*-
"""Matching-only preview for PHASE9-WPTITLES. No BM25, no scoring, no TEST."""
from __future__ import annotations

import csv
import json
import os
import shutil
import sys

_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(_DIR, "..", "..", ".."))
ART = os.path.join(_DIR, "artifacts")
CSV_PATH = os.path.join(ART, "bilingual_titles.csv")
BENCH = os.path.join(ROOT, "experiments", "ultra_v2", "benchmark")
EXPECTED_N = 51
EXPECTED_CSV_SHA = "7686f02d5bb2110eb4cccc7cdbd326324e4f7fa5e4dd34d7125a76d7795cf55d"

sys.path.insert(0, _DIR)
from match_rule import (  # noqa: E402
    add_dotted_initialism_aliases,
    load_common_english,
    match_spans,
    norm_en,
    tokenize,
    ur_token_key,
)


def sha256_file(path: str) -> str:
    import hashlib

    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(1024 * 1024)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def load_indexes(path: str) -> tuple[dict, dict, int]:
    idx = {}
    ur_compact = {}
    with open(path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            en = row["en_title"]
            ur = row["ur_title"]
            key = norm_en(en)
            rec = idx.get(key)
            if rec is None:
                rec = {"originals": [], "orig_set": set(), "entries": []}
                idx[key] = rec
            if en not in rec["orig_set"]:
                rec["orig_set"].add(en)
                rec["originals"].append(en)
            entry = {"ur_title": ur, "row_type": row["row_type"], "en_title": en}
            rec["entries"].append(entry)
            ck = ur_token_key(ur)
            if ck:
                ur_compact.setdefault(ck, []).append(entry)
    for rec in idx.values():
        del rec["orig_set"]
    n_alias = add_dotted_initialism_aliases(idx)
    return idx, ur_compact, n_alias


def load_roman_kn_train_dev() -> list[dict]:
    rows = []
    for split in ("train", "dev"):
        path = os.path.join(BENCH, split, "queries_kn.csv")
        with open(path, encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                if (r.get("script") or "").upper() != "ROMAN":
                    continue
                if (r.get("split") or split).lower() not in ("train", "dev"):
                    continue
                rows.append(
                    {
                        "query_id": r["query_id"],
                        "split": r.get("split") or split,
                        "query_text": r["query_text"],
                    }
                )
    rows.sort(key=lambda r: r["query_id"])
    return rows


def _archive_v1_preview() -> None:
    src_csv = os.path.join(ART, "phase9_match_preview.csv")
    dst_csv = os.path.join(ART, "phase9_match_preview_v1.csv")
    src_js = os.path.join(ART, "phase9_match_preview_summary.json")
    dst_js = os.path.join(ART, "phase9_match_preview_summary_v1.json")
    if os.path.isfile(src_csv) and not os.path.isfile(dst_csv):
        shutil.copy2(src_csv, dst_csv)
    if os.path.isfile(src_js) and not os.path.isfile(dst_js):
        shutil.copy2(src_js, dst_js)


def main() -> int:
    got = sha256_file(CSV_PATH)
    if got != EXPECTED_CSV_SHA:
        print("BLOCKED csv sha mismatch", got)
        return 2
    n_words = len(load_common_english())
    _archive_v1_preview()
    print("load title index", flush=True)
    en_index, ur_compact, n_alias = load_indexes(CSV_PATH)
    print(f"en keys={len(en_index)} ur_compact={len(ur_compact)} dotted_aliases={n_alias} wordlist={n_words}", flush=True)
    queries = load_roman_kn_train_dev()
    if len(queries) != EXPECTED_N:
        print(f"BLOCKED expected n={EXPECTED_N} got {len(queries)}")
        return 2
    preview_rows = []
    per_query = []
    n_with_hit = 0
    for q in queries:
        toks = tokenize(q["query_text"])
        hits = match_spans(toks, en_index, ur_compact)
        if hits:
            n_with_hit += 1
        n_ur = sum(len(h["ur_titles"]) for h in hits)
        per_query.append(
            {
                "query_id": q["query_id"],
                "split": q["split"],
                "n_tokens": len(toks),
                "n_en_hits": len(hits),
                "n_ur_expansions": n_ur,
                "spans": [h["span"] for h in hits],
                "en_titles": [h["en_title"] for h in hits],
            }
        )
        if not hits:
            preview_rows.append(
                {
                    "query_id": q["query_id"],
                    "split": q["split"],
                    "query_text": q["query_text"],
                    "span": "",
                    "en_title": "",
                    "ur_titles": "",
                    "span_len": 0,
                }
            )
            continue
        for h in hits:
            preview_rows.append(
                {
                    "query_id": q["query_id"],
                    "split": q["split"],
                    "query_text": q["query_text"],
                    "span": h["span"],
                    "en_title": h["en_title"],
                    "ur_titles": " | ".join(h["ur_titles"]),
                    "span_len": h["length"],
                }
            )
    out_csv = os.path.join(ART, "phase9_match_preview.csv")
    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["query_id", "split", "query_text", "span", "span_len", "en_title", "ur_titles"],
        )
        w.writeheader()
        w.writerows(preview_rows)
    summary = {
        "n_queries": len(queries),
        "n_queries_with_ge1_hit": n_with_hit,
        "n_queries_zero_hit": len(queries) - n_with_hit,
        "max_en_hits_on_a_query": max(p["n_en_hits"] for p in per_query),
        "max_ur_expansions_on_a_query": max(p["n_ur_expansions"] for p in per_query),
        "csv_sha256_checked": got,
        "retrieval_run": False,
        "match_rule_version": "v2_nogo_correction",
        "n_wordlist": n_words,
        "n_dotted_initialism_aliases": n_alias,
    }
    with open(os.path.join(ART, "phase9_match_preview_summary.json"), "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "per_query": per_query}, f, ensure_ascii=False, indent=2)
    print(json.dumps(summary, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
