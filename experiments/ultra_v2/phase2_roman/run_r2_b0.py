# -*- coding: utf-8 -*-
"""R2-B0: frozen Method D baseline on v2 Roman KN TRAIN/DEV only.

Imports experiments/phase5_roman_urdu/run_phase5.py read-only.
Does not edit M0. Does not access benchmark/test/. Does not score NL.
Does not apply R2-1/R2-3 treatments.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import pickle
import sys
import time
from datetime import datetime, timezone

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(_DIR, "..", "..", ".."))
P5 = os.path.join(ROOT, "experiments", "phase5_roman_urdu")
BENCH = os.path.join(ROOT, "experiments", "ultra_v2", "benchmark")
TEST_DIR = os.path.abspath(os.path.join(BENCH, "test"))
ART = os.path.join(_DIR, "artifacts")
CACHE = os.path.join(ART, "_index_cache.pkl")
EXPECTED_DICT_SHA = "30c3f61a64ec641abbb3acdbc7a8bcaf197f0238f1bf9e76c2c7ce8e590f86a3"
ALLOWED_SPLITS = ("train", "dev")
TOP_K = 50
HIT_K = 5

sys.path.insert(0, P5)
import run_phase5 as p5  # noqa: E402


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(1024 * 1024)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def refuse_test_path(path: str) -> None:
    ap = os.path.abspath(path)
    if ap == TEST_DIR or ap.startswith(TEST_DIR + os.sep):
        raise SystemExit("REFUSED: TEST path is forbidden for R2-B0: %s" % ap)


def kn_metrics(ranks: list[int]) -> dict:
    n = len(ranks)

    def hit(k: int) -> tuple[int, float]:
        c = sum(1 for r in ranks if r <= k)
        return c, (c / n if n else 0.0)

    h1, p1 = hit(1)
    h5, p5 = hit(5)
    h10, p10 = hit(10)
    h50, p50 = hit(50)
    mrr = (sum((1.0 / r) if r < 999 else 0.0 for r in ranks) / n) if n else 0.0
    return {
        "n": n,
        "hit@1_n": h1,
        "hit@1": round(p1, 4),
        "hit@5_n": h5,
        "hit@5": round(p5, 4),
        "hit@10_n": h10,
        "hit@10": round(p10, 4),
        "hit@50_n": h50,
        "hit@50": round(p50, 4),
        "mrr": round(mrr, 4),
    }


def fail_category(rank: int) -> str:
    if rank <= HIT_K:
        return "SUCCESS"
    if rank <= TOP_K:
        return "RANK"
    return "VOCAB/MISS"


def load_roman_kn() -> list[dict]:
    rows = []
    for split in ALLOWED_SPLITS:
        path = os.path.join(BENCH, split, "queries_kn.csv")
        refuse_test_path(path)
        with open(path, encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f):
                if (r.get("split") or "").strip() != split:
                    raise SystemExit("split mismatch %s %s" % (path, r.get("query_id")))
                if (r.get("script") or "").strip() != "ROMAN":
                    continue
                text = r["query_text"]
                det = p5.detect_script(text)
                if det != "ROMAN":
                    raise SystemExit("detector mismatch %s meta=ROMAN det=%s" % (r["query_id"], det))
                src = (r.get("source_doc_id") or "").strip()
                if not src:
                    raise SystemExit("KN missing source %s" % r["query_id"])
                rows.append({
                    "query_id": r["query_id"],
                    "query_text": text,
                    "split": split,
                    "script": "ROMAN",
                    "source_doc_id": int(src),
                })
    return rows


def count_roman_nl() -> dict[str, int]:
    out = {"train": 0, "dev": 0}
    for split in ALLOWED_SPLITS:
        path = os.path.join(BENCH, split, "queries_nl.csv")
        refuse_test_path(path)
        with open(path, encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f):
                if (r.get("script") or "").strip() == "ROMAN":
                    if (r.get("source_doc_id") or "").strip():
                        raise SystemExit("NL has source_doc_id %s" % r.get("query_id"))
                    out[split] += 1
    return out


def build_or_load_indexes():
    os.makedirs(ART, exist_ok=True)
    refuse_test_path(p5.CORPUS)
    dict_sha = sha256_file(p5.DICT_PATH)
    if dict_sha != EXPECTED_DICT_SHA:
        raise SystemExit("STOP: dictionary SHA-256 is not the frozen publication hash")
    corpus_sha = sha256_file(p5.CORPUS)
    cache_meta = {
        "corpus_sha256": corpus_sha,
        "dict_sha256": dict_sha,
        "k1": p5.BM25_K1,
        "b": p5.BM25_B,
        "tokenizer": p5.TOKEN_RE.pattern,
    }
    meta = {**cache_meta, "top_k": TOP_K}
    if os.path.isfile(CACHE):
        print("loading index cache...", flush=True)
        with open(CACHE, "rb") as f:
            blob = pickle.load(f)
        if blob.get("meta") == cache_meta:
            print("index cache hit", flush=True)
            return blob["urdu_bm25"], blob["roman_bm25"], blob["fwd"], blob["rev"], meta
        print("index cache stale; rebuilding", flush=True)

    import pandas as pd

    fwd = p5.load_roman_dict()
    rev = p5.load_reverse_roman(fwd)
    print("loading corpus...", flush=True)
    df = pd.read_csv(p5.CORPUS, encoding="utf-8-sig")
    if "combined_text" in df.columns:
        texts = df["combined_text"].fillna("").astype(str).tolist()
    else:
        texts = (
            df["Headline"].fillna("").astype(str)
            + " "
            + df["News Text"].fillna("").astype(str)
        ).tolist()
    print("docs=%s tokenize+romanize..." % len(texts), flush=True)
    t0 = time.perf_counter()
    urdu_docs, roman_docs = [], []
    for i, text in enumerate(texts):
        utoks = p5.tokenize(text)
        rtoks = [t for t in (p5.romanize_token(t, rev) for t in utoks) if t]
        urdu_docs.append(utoks)
        roman_docs.append(rtoks)
        if (i + 1) % 20000 == 0:
            print("  tokenize %s/%s" % (i + 1, len(texts)), flush=True)
    print("tokenize %.1fs" % (time.perf_counter() - t0), flush=True)
    urdu_bm25 = p5.BM25(urdu_docs)
    roman_bm25 = p5.BM25(roman_docs)
    blob = {
        "meta": cache_meta,
        "fwd": fwd,
        "rev": rev,
        "urdu_bm25": urdu_bm25,
        "roman_bm25": roman_bm25,
    }
    with open(CACHE, "wb") as f:
        pickle.dump(blob, f, protocol=pickle.HIGHEST_PROTOCOL)
    return urdu_bm25, roman_bm25, fwd, rev, meta


def corpus_text(did: int) -> str:
    import pandas as pd

    df = pd.read_csv(p5.CORPUS, encoding="utf-8-sig")
    if "combined_text" in df.columns:
        texts = df["combined_text"].fillna("").astype(str)
    else:
        texts = df["Headline"].fillna("").astype(str) + " " + df["News Text"].fillna("").astype(str)
    return str(texts.iloc[int(did)])


def mechanics_check(row: dict, qtoks: list[str], hits: list, rank: int, rev: dict, roman_bm25) -> dict:
    gold = row["source_doc_id"]
    gold_utoks = p5.tokenize(corpus_text(gold))
    gold_rtoks = [t for t in (p5.romanize_token(t, rev) for t in gold_utoks) if t]
    qset = set(qtoks)
    gset = set(gold_rtoks)
    matched = sorted(qset & gset)
    in_index = sorted(t for t in qset if t in roman_bm25.post)
    top = [{"rank": i, "doc_id": int(did), "score": float(score)} for i, (did, score) in enumerate(hits[:5], 1)]
    return {
        "query_id": row["query_id"],
        "split": row["split"],
        "source_doc_id": gold,
        "category": fail_category(rank),
        "gold_rank": rank if rank < 999 else None,
        "query_tokens": qtoks,
        "query_tokens_in_roman_index": in_index,
        "gold_roman_token_count": len(gold_rtoks),
        "matching_terms_query_and_gold_roman": matched,
        "n_matching_terms": len(matched),
        "retrieved_top5": top,
        "n_hits_returned": len(hits),
        "note": "Method D: query tokens as typed; gold tokens are document-side romanization.",
    }


def main() -> int:
    print("label: ULTRA v2 development experiment R2-B0", flush=True)
    print("TEST_accessed: no", flush=True)
    print("treatments: none", flush=True)

    rows = load_roman_kn()
    nl = count_roman_nl()
    print("roman_kn", len(rows), "train", sum(1 for r in rows if r["split"] == "train"),
          "dev", sum(1 for r in rows if r["split"] == "dev"), flush=True)
    print("roman_nl_train", nl["train"], "roman_nl_dev", nl["dev"], "nl_scored: no", flush=True)

    _urdu_bm25, roman_bm25, fwd, rev, meta = build_or_load_indexes()
    del _urdu_bm25  # Roman KN only; Urdu index unused

    per_rows = []
    ranks: list[int] = []
    hit_lists: dict[str, list] = {}
    qtoks_map: dict[str, list[str]] = {}
    for r in rows:
        qtoks = p5.tokenize(r["query_text"])
        hits = roman_bm25.search(qtoks, top_k=TOP_K)
        rank = p5.rank_of(hits, r["source_doc_id"])
        cat = fail_category(rank)
        ranks.append(rank)
        hit_lists[r["query_id"]] = hits
        qtoks_map[r["query_id"]] = qtoks
        per_rows.append({
            "experiment_id": "R2-B0",
            "query_id": r["query_id"],
            "split": r["split"],
            "script": "ROMAN",
            "source_doc_id": r["source_doc_id"],
            "query_tokens": " ".join(qtoks),
            "gold_rank": rank if rank < 999 else "",
            "in_top50": int(rank <= TOP_K),
            "hit@5": int(rank <= HIT_K),
            "category": cat,
        })

    def slice_ranks(split: str | None) -> list[int]:
        if split is None:
            return ranks
        return [rk for r, rk in zip(rows, ranks) if r["split"] == split]

    train_m = kn_metrics(slice_ranks("train"))
    dev_m = kn_metrics(slice_ranks("dev"))
    all_m = kn_metrics(ranks)
    n_success = all_m["hit@5_n"]
    n_rank = sum(1 for x in ranks if HIT_K < x <= TOP_K)
    n_miss = sum(1 for x in ranks if x > TOP_K)
    if n_success + n_rank + n_miss != len(rows):
        raise SystemExit("taxonomy does not partition n")

    checks = []
    picks = []
    for want in ("SUCCESS", "RANK", "VOCAB/MISS"):
        for r, rk in zip(rows, ranks):
            if fail_category(rk) == want:
                picks.append(r)
                break
    for r in picks:
        checks.append(mechanics_check(
            r,
            qtoks_map[r["query_id"]],
            hit_lists[r["query_id"]],
            p5.rank_of(hit_lists[r["query_id"]], r["source_doc_id"]),
            rev,
            roman_bm25,
        ))

    os.makedirs(ART, exist_ok=True)
    config = {
        "experiment_id": "R2-B0",
        "label": "ULTRA v2 development experiment",
        "not_a_plos_result": True,
        "method": "frozen Method D",
        "m0_module": "experiments/phase5_roman_urdu/run_phase5.py",
        "m0_edited": False,
        "detector": "detect_script (Urdu U+0600-U+06FF vs ASCII letters)",
        "routing": "ROMAN -> romanized-document BM25 (Method D)",
        "query_representation": "tokenize(query) as typed; no dictionary on query",
        "document_representation": "romanize_token: reverse-dict first key else naive_roman_word",
        "dictionary_path": os.path.relpath(p5.DICT_PATH, ROOT).replace("\\", "/"),
        "dictionary_n_keys": len(fwd),
        "bm25_implementation": "run_phase5.BM25",
        "candidate_depth": TOP_K,
        "official_cutoff": HIT_K,
        "test_accessed": False,
        "nl_scored": False,
        **meta,
    }
    summary = {
        "experiment_id": "R2-B0",
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "test_accessed": False,
        "nl_evaluation": "pending official pooled annotation; not scored",
        "data": {
            "train_roman_kn": train_m["n"],
            "dev_roman_kn": dev_m["n"],
            "traindev_roman_kn": all_m["n"],
            "train_roman_nl": nl["train"],
            "dev_roman_nl": nl["dev"],
            "test": "not accessed",
        },
        "metrics": {"train": train_m, "dev": dev_m, "train+dev": all_m},
        "taxonomy": {
            "SUCCESS": n_success,
            "RANK": n_rank,
            "VOCAB/MISS": n_miss,
            "sum": n_success + n_rank + n_miss,
            "n": len(rows),
        },
        "config": config,
    }
    with open(os.path.join(ART, "r2_b0_config.json"), "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
    with open(os.path.join(ART, "r2_b0_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    with open(os.path.join(ART, "r2_b0_mechanics_check.json"), "w", encoding="utf-8") as f:
        json.dump(checks, f, indent=2, ensure_ascii=False)
    fields = list(per_rows[0].keys())
    with open(os.path.join(ART, "r2_b0_per_query.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(per_rows)
    fail_fields = ["query_id", "split", "source_doc_id", "gold_rank", "in_top50", "category"]
    fails = [r for r in per_rows if r["category"] != "SUCCESS"]
    with open(os.path.join(ART, "r2_b0_failures.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fail_fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(fails)

    print("train", train_m, flush=True)
    print("dev", dev_m, flush=True)
    print("train+dev", all_m, flush=True)
    print("taxonomy SUCCESS", n_success, "RANK", n_rank, "VOCAB/MISS", n_miss, flush=True)
    print("mechanics_checks", [c["query_id"] for c in checks], flush=True)
    print("status: R2-B0 DONE", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
