# -*- coding: utf-8 -*-
"""ULTRA v2 Phase 2 Roman experiments on TRAIN/DEV KN only.

Imports frozen M0 from experiments/phase5_roman_urdu/run_phase5.py.
Does not edit M0. Refuses TEST. Does not invent NL qrels. No dense retrieval.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import pickle
import sys
import time
from collections import Counter
from datetime import datetime, timezone

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(_DIR, "..", "..", ".."))
P5 = os.path.join(ROOT, "experiments", "phase5_roman_urdu")
BENCH = os.path.join(ROOT, "experiments", "ultra_v2", "benchmark")
TEST_DIR = os.path.join(BENCH, "test")
ART = os.path.join(_DIR, "artifacts")
CACHE = os.path.join(ART, "_index_cache.pkl")
SEAL = os.path.join(TEST_DIR, "seal.json")
EXPECTED_SEAL = "48610601209c3723a7252bb9a197d8fbbece18640e0bf7aef972884816ab46c4"
EXPECTED_DICT_SHA = "30c3f61a64ec641abbb3acdbc7a8bcaf197f0238f1bf9e76c2c7ce8e590f86a3"
ALLOWED_SPLITS = ("train", "dev")
TOP_K = 50

sys.path.insert(0, P5)
import run_phase5 as p5  # noqa: E402

sys.path.insert(0, _DIR)
from query_treatments import (  # noqa: E402
    alias_tables,
    treatment_b0,
    treatment_r21,
    treatment_r23,
)


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
    """Forbid TEST query files. seal.json / README.md are hash/docs only."""
    ap = os.path.abspath(path)
    td = os.path.abspath(TEST_DIR)
    if ap == td or ap.startswith(td + os.sep):
        name = os.path.basename(ap).lower()
        if name in {"seal.json", "readme.md"}:
            return
        raise SystemExit("REFUSED: TEST path is forbidden: %s" % ap)


def confirm_seal() -> str:
    refuse_test_path(SEAL)
    with open(SEAL, encoding="utf-8") as f:
        man = json.load(f)
    got = man.get("aggregate_sha256") or ""
    if got != EXPECTED_SEAL:
        raise SystemExit("STOP: TEST seal aggregate_sha256 mismatch (no TEST queries were opened)")
    return got


def route_m0(query_text: str) -> tuple[str, str]:
    det = p5.detect_script(query_text)
    if det == "ROMAN":
        return det, "roman"
    return det, "urdu"


def kn_metrics(ranks: list[int]) -> dict:
    n = len(ranks)
    if n == 0:
        return {"n": 0, "hit@1": 0.0, "hit@5": 0.0, "hit@10": 0.0, "hit@50": 0.0, "mrr": 0.0,
                "hit@1_n": 0, "hit@5_n": 0, "hit@10_n": 0, "hit@50_n": 0}

    def hit(k: int) -> tuple[int, float]:
        c = sum(1 for r in ranks if r <= k)
        return c, c / n

    h1, p1 = hit(1)
    h5, p5 = hit(5)
    h10, p10 = hit(10)
    h50, p50 = hit(50)
    mrr = sum((1.0 / r) if r < 999 else 0.0 for r in ranks) / n
    return {
        "n": n,
        "hit@1": round(p1, 4),
        "hit@5": round(p5, 4),
        "hit@10": round(p10, 4),
        "hit@50": round(p50, 4),
        "mrr": round(mrr, 4),
        "hit@1_n": h1,
        "hit@5_n": h5,
        "hit@10_n": h10,
        "hit@50_n": h50,
    }


def load_kn_rows() -> list[dict]:
    rows = []
    for split in ALLOWED_SPLITS:
        path = os.path.join(BENCH, split, "queries_kn.csv")
        refuse_test_path(path)
        with open(path, encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f):
                if (r.get("split") or "").strip() != split:
                    raise SystemExit("split field mismatch in %s id=%s" % (path, r.get("query_id")))
                rows.append({
                    "query_id": r["query_id"],
                    "query_text": r["query_text"],
                    "script": r["script"],
                    "intent_type": r["intent_type"],
                    "split": split,
                    "source_doc_id": int(r["source_doc_id"]),
                })
    return rows


def build_or_load_indexes():
    os.makedirs(ART, exist_ok=True)
    corpus_path = p5.CORPUS
    dict_path = p5.DICT_PATH
    refuse_test_path(corpus_path)
    dict_sha = sha256_file(dict_path)
    if dict_sha != EXPECTED_DICT_SHA:
        raise SystemExit("STOP: dictionary SHA-256 is not the frozen publication hash")
    corpus_sha = sha256_file(corpus_path)
    meta = {
        "corpus_sha256": corpus_sha,
        "dict_sha256": dict_sha,
        "k1": p5.BM25_K1,
        "b": p5.BM25_B,
        "tokenizer": p5.TOKEN_RE.pattern,
    }
    if os.path.isfile(CACHE):
        print("loading index cache...", flush=True)
        with open(CACHE, "rb") as f:
            blob = pickle.load(f)
        if blob.get("meta") == meta:
            print("index cache hit", flush=True)
            return blob["urdu_bm25"], blob["roman_bm25"], blob["fwd"], blob["rev"], meta
        print("index cache stale; rebuilding", flush=True)

    import pandas as pd

    fwd = p5.load_roman_dict()
    rev = p5.load_reverse_roman(fwd)
    print("loading corpus...", flush=True)
    df = pd.read_csv(corpus_path, encoding="utf-8-sig")
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
    print("indexes ready urdu_terms=%s roman_terms=%s" % (len(urdu_bm25.idf), len(roman_bm25.idf)), flush=True)
    blob = {
        "meta": meta,
        "fwd": fwd,
        "rev": rev,
        "urdu_bm25": urdu_bm25,
        "roman_bm25": roman_bm25,
    }
    with open(CACHE, "wb") as f:
        pickle.dump(blob, f, protocol=pickle.HIGHEST_PROTOCOL)
    print("wrote", CACHE, flush=True)
    return urdu_bm25, roman_bm25, fwd, rev, meta


def apply_treatment(name: str, qtoks: list[str], tables: dict) -> list[str]:
    if name == "R2-B0":
        return treatment_b0(qtoks)
    if name == "R2-1":
        return treatment_r21(qtoks, tables["canonical"], tables["variant"])
    if name == "R2-3":
        return treatment_r23(qtoks, tables["canonical"], tables["siblings"], tables["variant"])
    raise SystemExit("unknown experiment %s" % name)


def search_kn(row: dict, treatment: str, urdu_bm25, roman_bm25, tables: dict):
    q = row["query_text"]
    det, which = route_m0(q)
    qtoks = p5.tokenize(q)
    if which == "roman":
        qtoks = apply_treatment(treatment, qtoks, tables)
        hits = roman_bm25.search(qtoks, top_k=TOP_K)
    else:
        hits = urdu_bm25.search(qtoks, top_k=TOP_K)
    rank = p5.rank_of(hits, row["source_doc_id"])
    return det, which, qtoks, rank


def slice_metrics(rows: list[dict], ranks: list[int], pred) -> dict:
    sub = [rk for r, rk in zip(rows, ranks) if pred(r)]
    return kn_metrics(sub)


def classify_train_roman_failure(row: dict, rank: int, qtoks: list[str], roman_src_toks: set[str],
                                 canonical: dict[str, str], variant: dict[str, str]) -> tuple[str, str]:
    """Mechanical primary (MISS/RANK) plus a cheap secondary from token overlap."""
    if rank >= 999:
        primary = "MISS"
    elif rank > 5:
        primary = "RANK"
    else:
        return "OK", ""
    qset = set(qtoks)
    overlap = qset & roman_src_toks
    folded = {variant.get(t, canonical.get(t, t)) for t in qtoks}
    folded |= {canonical.get(variant.get(t, t), variant.get(t, t)) for t in qtoks}
    sibling_hit = bool(folded & roman_src_toks) and not overlap
    if sibling_hit:
        secondary = "NORM"
    elif not overlap:
        secondary = "VOCAB"
    else:
        secondary = "RANK" if primary == "RANK" else "VOCAB"
    return primary, secondary


def compare_hit5(base: list[int], treat: list[int]) -> dict:
    imp = unch = deg = 0
    for a, b in zip(base, treat):
        ah, bh = a <= 5, b <= 5
        if bh and not ah:
            imp += 1
        elif ah and not bh:
            deg += 1
        else:
            unch += 1
    return {"improved": imp, "unchanged": unch, "degraded": deg, "total": len(base)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ULTRA v2 Phase 2 Roman KN experiments (TRAIN/DEV only).")
    parser.add_argument(
        "--experiments",
        default="R2-B0,R2-1,R2-3",
        help="Comma list from R2-B0,R2-1,R2-3. R2-2 is documented as vacuous and is not run.",
    )
    parser.add_argument(
        "--splits",
        default="train,dev",
        help="Allowed: train,dev. test is refused.",
    )
    args = parser.parse_args(argv)

    splits = tuple(s.strip() for s in args.splits.split(",") if s.strip())
    if "test" in splits:
        print("status: REFUSED")
        print("error: TEST split is forbidden")
        return 2
    for s in splits:
        if s not in ALLOWED_SPLITS:
            print("status: FAIL unknown split", s)
            return 2

    experiments = [e.strip() for e in args.experiments.split(",") if e.strip()]
    if "R2-2" in experiments:
        print("status: FAIL")
        print("error: R2-2 is vacuous for Method D BM25; omit it (see AUDIT.md)")
        return 2
    for e in experiments:
        if e not in {"R2-B0", "R2-1", "R2-3"}:
            print("status: FAIL unknown experiment", e)
            return 2

    print("label: ULTRA v2 development experiment", flush=True)
    print("TEST_forbidden: yes", flush=True)
    seal = confirm_seal()
    print("test_seal_aggregate_sha256:", seal, flush=True)

    rows = [r for r in load_kn_rows() if r["split"] in splits]
    print("kn_rows:", len(rows), "splits:", splits, flush=True)

    urdu_bm25, roman_bm25, fwd, rev, meta = build_or_load_indexes()
    canonical, siblings = alias_tables(fwd)
    tables = {
        "canonical": canonical,
        "siblings": siblings,
        "variant": dict(p5._VARIANT_TO_DICT_KEY),
    }
    multi = {k: v for k, v in siblings.items() if len(v) > 1}
    with open(os.path.join(ART, "dict_alias_groups.json"), "w", encoding="utf-8") as f:
        json.dump({"n_groups_with_aliases": len(multi), "groups": multi}, f, ensure_ascii=False, indent=2)

    per_exp_ranks: dict[str, list[int]] = {}
    per_exp_rows: list[dict] = []
    qtoks_b0: dict[str, list[str]] = {}

    for exp in experiments:
        print("running", exp, flush=True)
        ranks = []
        for r in rows:
            det, which, qtoks, rank = search_kn(r, exp, urdu_bm25, roman_bm25, tables)
            ranks.append(rank)
            if exp == "R2-B0":
                qtoks_b0[r["query_id"]] = qtoks
            per_exp_rows.append({
                "experiment_id": exp,
                "query_id": r["query_id"],
                "split": r["split"],
                "script": r["script"],
                "detector": det,
                "path": which,
                "intent_type": r["intent_type"],
                "source_doc_id": r["source_doc_id"],
                "rank": rank if rank < 999 else "",
                "miss50": int(rank >= 999),
                "hit@5": int(rank <= 5),
                "qtoks": " ".join(qtoks),
            })
        per_exp_ranks[exp] = ranks
        print("  done", exp, kn_metrics(ranks), flush=True)

    def pack(exp: str) -> dict:
        ranks = per_exp_ranks[exp]
        out = {
            "all_kn": kn_metrics(ranks),
            "train": slice_metrics(rows, ranks, lambda r: r["split"] == "train"),
            "dev": slice_metrics(rows, ranks, lambda r: r["split"] == "dev"),
            "roman": slice_metrics(rows, ranks, lambda r: r["script"] == "ROMAN"),
            "roman_train": slice_metrics(rows, ranks, lambda r: r["script"] == "ROMAN" and r["split"] == "train"),
            "roman_dev": slice_metrics(rows, ranks, lambda r: r["script"] == "ROMAN" and r["split"] == "dev"),
            "urdu": slice_metrics(rows, ranks, lambda r: r["script"] == "URDU"),
            "mixed": slice_metrics(rows, ranks, lambda r: r["script"] == "MIXED"),
        }
        if "R2-B0" in per_exp_ranks and exp != "R2-B0":
            base = per_exp_ranks["R2-B0"]
            out["vs_B0_hit@5_all"] = compare_hit5(base, ranks)
            roman_idx = [i for i, r in enumerate(rows) if r["script"] == "ROMAN"]
            out["vs_B0_hit@5_roman"] = compare_hit5(
                [base[i] for i in roman_idx],
                [ranks[i] for i in roman_idx],
            )
            out["vs_B0_hit@5_roman_train"] = compare_hit5(
                [base[i] for i in roman_idx if rows[i]["split"] == "train"],
                [ranks[i] for i in roman_idx if rows[i]["split"] == "train"],
            )
            out["vs_B0_hit@5_roman_dev"] = compare_hit5(
                [base[i] for i in roman_idx if rows[i]["split"] == "dev"],
                [ranks[i] for i in roman_idx if rows[i]["split"] == "dev"],
            )
        return out

    summary = {
        "label": "ULTRA v2 development experiment",
        "not_a_plos_result": True,
        "test_used": False,
        "test_seal_aggregate_sha256": seal,
        "nl_evaluation": "pending official pooled annotation; no qrels",
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "index_meta": meta,
        "n_dict_keys": len(fwd),
        "n_alias_families": len(multi),
        "experiments": {e: pack(e) for e in experiments},
    }

    fail_rows = []
    if "R2-B0" in per_exp_ranks:
        # Source roman tokens for TRAIN Roman failures only (no TEST).
        src_needed = {r["source_doc_id"] for r, rk in zip(rows, per_exp_ranks["R2-B0"])
                      if r["split"] == "train" and r["script"] == "ROMAN" and rk > 5}
        src_roman = {}
        if src_needed:
            import pandas as pd
            df = pd.read_csv(p5.CORPUS, encoding="utf-8-sig")
            if "combined_text" in df.columns:
                texts = df["combined_text"].fillna("").astype(str)
            else:
                texts = df["Headline"].fillna("").astype(str) + " " + df["News Text"].fillna("").astype(str)
            for did in src_needed:
                utoks = p5.tokenize(str(texts.iloc[int(did)]))
                src_roman[did] = set(t for t in (p5.romanize_token(t, rev) for t in utoks) if t)
        for r, rk in zip(rows, per_exp_ranks["R2-B0"]):
            if r["split"] != "train" or r["script"] != "ROMAN" or rk <= 5:
                continue
            qtoks = qtoks_b0[r["query_id"]]
            primary, secondary = classify_train_roman_failure(
                r, rk, qtoks, src_roman.get(r["source_doc_id"], set()),
                canonical, tables["variant"],
            )
            fail_rows.append({
                "query_id": r["query_id"],
                "rank": rk if rk < 999 else "miss50",
                "primary": primary,
                "secondary": secondary,
            })
        counts = Counter((fr["primary"], fr["secondary"]) for fr in fail_rows)
        summary["train_roman_b0_failures"] = {
            "n": len(fail_rows),
            "taxonomy_counts": {("%s/%s" % k): v for k, v in counts.items()},
            "rows": fail_rows,
        }

    os.makedirs(ART, exist_ok=True)
    with open(os.path.join(ART, "phase2_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    with open(os.path.join(ART, "phase2_per_query.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(per_exp_rows[0].keys()) if per_exp_rows else ["experiment_id"])
        w.writeheader()
        w.writerows(per_exp_rows)

    print("wrote", os.path.join(ART, "phase2_summary.json"), flush=True)
    print("nl_evaluation: pending official pooled annotation", flush=True)
    print("status: DONE", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
