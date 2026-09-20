# -*- coding: utf-8 -*-
"""HYBRID-RRF: Method-D BM25 ∪ Phase-3 dense, Reciprocal Rank Fusion k=60.

Read-only: M0/phase5, R2-B0 artifacts, Phase-3 embeddings/results.
Does not open benchmark/test/. Does not regenerate document embeddings.
Does not fine-tune, rerank, or try another fusion method.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import pickle
import platform
import sys
import time
from datetime import datetime, timezone

os.environ.setdefault("MKL_THREADING_LAYER", "SEQUENTIAL")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.pop("KMP_DUPLICATE_LIB_OK", None)

import numpy as np  # noqa: E402 — after MKL_THREADING_LAYER

_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(_DIR, "..", "..", ".."))
P5 = os.path.join(ROOT, "experiments", "phase5_roman_urdu")
P3 = os.path.join(ROOT, "experiments", "ultra_v2", "phase3_dense")
BENCH = os.path.join(ROOT, "experiments", "ultra_v2", "benchmark")
TEST_DIR = os.path.abspath(os.path.join(BENCH, "test"))
ART = os.path.join(_DIR, "artifacts")
R2_ART = os.path.join(ROOT, "experiments", "ultra_v2", "phase2_roman", "artifacts")
R2_CACHE = os.path.join(R2_ART, "_index_cache.pkl")
R2_PER_QUERY = os.path.join(R2_ART, "r2_b0_per_query.csv")
R2_FAIL_CSV = os.path.join(ROOT, "experiments", "ultra_v2", "phase2_roman", "R2_B0_FAILURE_ANALYSIS.csv")
P3_PER_QUERY = os.path.join(P3, "DENSE_PER_QUERY.csv")
P3_NPY = os.path.join(P3, "artifacts", "dense_doc_embeddings.npy")
P3_META = os.path.join(P3, "artifacts", "dense_index_meta.json")
PREREG = os.path.join(_DIR, "HYBRID_PREREGISTRATION.md")
ALLOWED_SPLITS = ("train", "dev")
EXPECTED_DICT_SHA = "30c3f61a64ec641abbb3acdbc7a8bcaf197f0238f1bf9e76c2c7ce8e590f86a3"
EXPECTED_CORPUS_SHA = "8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231"
FROZEN_BM25 = {"n": 51, "hit@1_n": 1, "hit@5_n": 4, "hit@10_n": 4, "hit@50_n": 6, "mrr": 0.0375}
FROZEN_DENSE = {"n": 51, "hit@1_n": 5, "hit@5_n": 15, "hit@10_n": 16, "hit@50_n": 22, "mrr": 0.1726}
ROOM_CAT1 = [
    "KN001", "KN006", "KN008", "KN010", "KN011",
    "KN018", "KN037", "KN045", "KN047", "KN050", "KN051",
]
VOCAB_CONTROLS = ["KN017", "KN020", "KN041"]
TOP_K = 50

sys.path.insert(0, _DIR)
sys.path.insert(0, P5)
sys.path.insert(0, P3)
import run_phase5 as p5  # noqa: E402
import dense_retrieval as dr  # noqa: E402
import hybrid_fusion as hf  # noqa: E402

# run_phase5 setdefault's this; keep MKL sequential instead of masking OMP #15.
os.environ.pop("KMP_DUPLICATE_LIB_OK", None)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


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
        raise SystemExit("BLOCKED — DATA SAFETY FAILURE: TEST path forbidden: %s" % ap)


def parse_rank(val: str) -> int:
    s = (val or "").strip()
    if not s:
        return 999
    return int(float(s))


def kn_metrics(ranks: list[int], candidate_depth: int = 50) -> dict:
    n = len(ranks)

    def hit(k: int) -> tuple[int, float]:
        c = sum(1 for r in ranks if r <= k)
        return c, (c / n if n else 0.0)

    h1, p1 = hit(1)
    h5, p5 = hit(5)
    h10, p10 = hit(10)
    h50, p50 = hit(50)
    mrr = (sum((1.0 / r) if r <= candidate_depth else 0.0 for r in ranks) / n) if n else 0.0
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


def rec_rank(rank: int) -> float:
    return (1.0 / rank) if 1 <= rank <= 50 else 0.0


def mcnemar_exact(regressed: int, recovered: int) -> dict:
    """Two-sided exact McNemar from discordant Hit/Miss pairs. Descriptive only."""
    from math import comb

    b, c = int(regressed), int(recovered)
    n = b + c
    if n == 0:
        return {"n_discordant": 0, "regressed": b, "recovered": c, "p_two_sided_exact": 1.0}
    k = min(b, c)
    p = min(1.0, 2.0 * sum(comb(n, i) for i in range(0, k + 1)) * (0.5 ** n))
    return {"n_discordant": n, "regressed": b, "recovered": c, "p_two_sided_exact": round(p, 6)}


def git_identity() -> tuple[str, str]:
    import subprocess

    branch = subprocess.check_output(
        ["git", "branch", "--show-current"], cwd=ROOT, text=True
    ).strip()
    commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    if branch != "research/ultra-v2-strengthening":
        raise SystemExit("BLOCKED — unexpected branch: %s" % branch)
    if commit != "fd54ac9b65c2db93e7e16fbf0c5a40b6a6025be1":
        raise SystemExit("BLOCKED — unexpected HEAD: %s" % commit)
    return branch, commit


def load_roman_kn() -> list[dict]:
    rows = []
    for split in ALLOWED_SPLITS:
        path = os.path.join(BENCH, split, "queries_kn.csv")
        refuse_test_path(path)
        with open(path, encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f):
                if (r.get("split") or "").strip() != split:
                    raise SystemExit("BLOCKED — split mismatch %s" % r.get("query_id"))
                if (r.get("script") or "").strip() != "ROMAN":
                    continue
                text = r["query_text"]
                det = p5.detect_script(text)
                if det != "ROMAN":
                    raise SystemExit("BLOCKED — detector mismatch %s" % r["query_id"])
                src = (r.get("source_doc_id") or "").strip()
                if not src:
                    raise SystemExit("BLOCKED — KN missing source %s" % r["query_id"])
                rows.append({
                    "query_id": r["query_id"],
                    "query_text": text,
                    "split": split,
                    "script": "ROMAN",
                    "source_doc_id": int(src),
                })
    if len(rows) != 51:
        raise SystemExit("BLOCKED — Roman KN n=%s != 51" % len(rows))
    return rows


def load_r2_b0() -> dict[str, dict]:
    refuse_test_path(R2_PER_QUERY)
    out = {}
    with open(R2_PER_QUERY, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            rank = parse_rank(r.get("gold_rank"))
            out[r["query_id"]] = {
                "gold_rank": rank,
                "in_top50": int(r.get("in_top50") or 0),
                "hit@5": int(r.get("hit@5") or 0),
                "source_doc_id": int(r["source_doc_id"]),
            }
    if len(out) != 51:
        raise SystemExit("BLOCKED — R2-B0 n=%s != 51" % len(out))
    return out


def load_dense_pq() -> dict[str, dict]:
    out = {}
    with open(P3_PER_QUERY, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            out[r["query_id"]] = {
                "dense_rank": int(r["dense_rank"]),
                "rank1_doc_id": int(r["dense_rank1_doc_id"]),
                "source_doc_id": int(r["source_doc_id"]),
                "r2_primary": (r.get("r2_primary") or "").strip(),
            }
    if len(out) != 51:
        raise SystemExit("BLOCKED — Phase-3 per-query n=%s != 51" % len(out))
    return out


def load_taxonomy() -> dict[str, str]:
    tax = {}
    with open(R2_FAIL_CSV, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            tax[r["query_id"]] = (r.get("primary") or "").strip()
    return tax


def load_bm25_roman():
    refuse_test_path(p5.CORPUS)
    dict_sha = sha256_file(p5.DICT_PATH)
    if dict_sha != EXPECTED_DICT_SHA:
        raise SystemExit("BLOCKED — dictionary SHA-256 is not the frozen hash")
    corpus_sha = sha256_file(p5.CORPUS)
    if corpus_sha != EXPECTED_CORPUS_SHA:
        raise SystemExit("BLOCKED — corpus SHA-256 mismatch")
    cache_meta = {
        "corpus_sha256": corpus_sha,
        "dict_sha256": dict_sha,
        "k1": p5.BM25_K1,
        "b": p5.BM25_B,
        "tokenizer": p5.TOKEN_RE.pattern,
    }
    if not os.path.isfile(R2_CACHE):
        raise SystemExit("BLOCKED — Method-D cache missing: %s" % R2_CACHE)
    print("loading Method-D cache (read-only)...", flush=True)
    with open(R2_CACHE, "rb") as f:
        blob = pickle.load(f)
    if blob.get("meta") != cache_meta:
        print("cache meta", blob.get("meta"), flush=True)
        print("expected", cache_meta, flush=True)
        raise SystemExit("BLOCKED — BM25 cache meta mismatch; will not rebuild during HYBRID-RRF")
    print("BM25 cache hit", flush=True)
    return blob["roman_bm25"], cache_meta


def load_dense_matrix():
    if not os.path.isfile(P3_NPY) or not os.path.isfile(P3_META):
        raise SystemExit("BLOCKED — Phase-3 dense matrix/meta missing")
    with open(P3_META, encoding="utf-8") as f:
        meta = json.load(f)
    if meta.get("complete") is not True:
        raise SystemExit("BLOCKED — dense index meta incomplete")
    if meta.get("model_id") != dr.MODEL_ID or meta.get("model_revision") != dr.MODEL_REVISION:
        raise SystemExit("BLOCKED — dense meta encoder mismatch: %s" % meta)
    if meta.get("corpus_sha256") != EXPECTED_CORPUS_SHA:
        raise SystemExit("BLOCKED — dense meta corpus SHA mismatch")
    arr = np.load(P3_NPY, mmap_mode="r")
    if tuple(arr.shape) != (111860, 384):
        raise SystemExit("BLOCKED — dense shape %s" % (arr.shape,))
    print("dense npy mmap", tuple(arr.shape), "bytes", os.path.getsize(P3_NPY), flush=True)
    # Copy once so 51 exact cosine searches are not mmap-bound. Do not write the npy.
    return np.array(arr, dtype=np.float32, copy=True), meta


def hybrid_case_flags(b50: int, d50: int, h50: int) -> dict:
    return {
        "A_bm25_success_retained": int(b50 == 1 and h50 == 1),
        "B_dense_success_retained": int(d50 == 1 and h50 == 1),
        "C_bm25_miss_recovered": int(b50 == 0 and h50 == 1),
        "D_dense_miss_recovered": int(d50 == 0 and h50 == 1),
        "E_both_miss": int(b50 == 0 and d50 == 0 and h50 == 0),
        "F_lost_single_system_success": int(h50 == 0 and (b50 == 1 or d50 == 1)),
    }


def main() -> int:
    wall_t0 = time.perf_counter()
    print("label: ULTRA v2 HYBRID-RRF", flush=True)
    print("TEST_accessed: no", flush=True)
    branch, commit = git_identity()
    print("git", branch, commit, flush=True)
    # Frozen RRF identity check (not an extra fusion method).
    _demo = hf.fuse_rrf([(5, 1.0), (3, 0.5)], [(3, 0.9), (7, 0.8)], k=60)
    assert [t[0] for t in _demo] == [3, 5, 7]
    if not os.path.isfile(PREREG):
        raise SystemExit("BLOCKED — HYBRID_PREREGISTRATION.md missing")
    os.makedirs(ART, exist_ok=True)
    refuse_test_path(p5.CORPUS)

    rows = load_roman_kn()
    r2 = load_r2_b0()
    p3 = load_dense_pq()
    tax = load_taxonomy()
    for r in rows:
        if r["query_id"] not in r2 or r["query_id"] not in p3:
            raise SystemExit("BLOCKED — missing baseline row %s" % r["query_id"])
        if r2[r["query_id"]]["source_doc_id"] != r["source_doc_id"]:
            raise SystemExit("BLOCKED — R2 source mismatch %s" % r["query_id"])
        if p3[r["query_id"]]["source_doc_id"] != r["source_doc_id"]:
            raise SystemExit("BLOCKED — P3 source mismatch %s" % r["query_id"])

    t0 = time.perf_counter()
    roman_bm25, cache_meta = load_bm25_roman()
    t_bm25_load = time.perf_counter() - t0

    # --- BM25 reproduction gate (gold rank as stored in R2-B0) ---
    print("reproducing Method-D Top-50...", flush=True)
    t1 = time.perf_counter()
    bm25_hits = {}
    bm25_rank_obs = {}
    bm25_mismatches = []
    for r in rows:
        qtoks = p5.tokenize(r["query_text"])
        hits = roman_bm25.search(qtoks, top_k=TOP_K)
        bm25_hits[r["query_id"]] = hits
        rank = p5.rank_of(hits, r["source_doc_id"])
        bm25_rank_obs[r["query_id"]] = rank
        exp = r2[r["query_id"]]
        if (
            rank != exp["gold_rank"]
            or int(rank <= 50) != exp["in_top50"]
            or int(rank <= 5) != exp["hit@5"]
        ):
            bm25_mismatches.append({
                "query_id": r["query_id"],
                "expected_gold_rank": exp["gold_rank"],
                "observed_gold_rank": rank,
                "expected_in_top50": exp["in_top50"],
                "observed_in_top50": int(rank <= 50),
                "expected_hit@5": exp["hit@5"],
                "observed_hit@5": int(rank <= 5),
                "observed_top5": [int(d) for d, _s in hits[:5]],
            })
    t_bm25_search = time.perf_counter() - t1
    if bm25_mismatches:
        print(json.dumps({"bm25_mismatches": bm25_mismatches}, indent=2), flush=True)
        raise SystemExit("BLOCKED — BM25 gold ranks do not match r2_b0_per_query.csv")
    bm25_m = kn_metrics([bm25_rank_obs[r["query_id"]] for r in rows])
    if (
        bm25_m["hit@1_n"] != FROZEN_BM25["hit@1_n"]
        or bm25_m["hit@5_n"] != FROZEN_BM25["hit@5_n"]
        or bm25_m["hit@10_n"] != FROZEN_BM25["hit@10_n"]
        or bm25_m["hit@50_n"] != FROZEN_BM25["hit@50_n"]
        or abs(bm25_m["mrr"] - FROZEN_BM25["mrr"]) > 1e-4
    ):
        raise SystemExit("BLOCKED — reproduced BM25 aggregates != frozen cells: %s" % bm25_m)
    print("GATE BM25 PASS", bm25_m, flush=True)

    # --- Dense reproduction gate ---
    print("loading Phase-3 document matrix (no regenerate)...", flush=True)
    t2 = time.perf_counter()
    doc_matrix, dense_meta = load_dense_matrix()
    t_npy = time.perf_counter() - t2
    print("loading e5-small for queries only...", flush=True)
    t3 = time.perf_counter()
    model, enc_info = dr.load_encoder()
    t_model = time.perf_counter() - t3
    q_texts = [r["query_text"] for r in rows]
    t4 = time.perf_counter()
    q_vecs = dr.encode_texts(
        model,
        q_texts,
        kind="query",
        prefix_mode=enc_info["prefix_mode"],
        prompt_name=enc_info.get("query_prompt_name"),
        show_progress=False,
    )
    t_qenc = time.perf_counter() - t4
    print("dense query encode n=%s %.2fs prefix_mode=%s" % (len(q_texts), t_qenc, enc_info["prefix_mode"]), flush=True)

    t5 = time.perf_counter()
    dense_hits = {}
    dense_search = {}
    dense_mismatches = []
    for r, qv in zip(rows, q_vecs):
        res = dr.search_query_vec(doc_matrix, qv, r["source_doc_id"], k=TOP_K)
        dense_search[r["query_id"]] = res
        dense_hits[r["query_id"]] = res["topk"]
        exp = p3[r["query_id"]]
        if int(res["gold_rank"]) != int(exp["dense_rank"]) or int(res["rank1_doc_id"]) != int(exp["rank1_doc_id"]):
            dense_mismatches.append({
                "query_id": r["query_id"],
                "expected_gold_rank": exp["dense_rank"],
                "observed_gold_rank": res["gold_rank"],
                "expected_rank1_doc_id": exp["rank1_doc_id"],
                "observed_rank1_doc_id": res["rank1_doc_id"],
                "observed_top5": [int(d) for d, _s in res["topk"][:5]],
            })
    t_dsearch = time.perf_counter() - t5
    if dense_mismatches:
        print(json.dumps({"dense_mismatches": dense_mismatches}, indent=2), flush=True)
        raise SystemExit("BLOCKED — dense ranks/rank-1 ids do not match DENSE_PER_QUERY.csv")
    dense_m = kn_metrics([dense_search[r["query_id"]]["gold_rank"] for r in rows])
    if (
        dense_m["hit@1_n"] != FROZEN_DENSE["hit@1_n"]
        or dense_m["hit@5_n"] != FROZEN_DENSE["hit@5_n"]
        or dense_m["hit@10_n"] != FROZEN_DENSE["hit@10_n"]
        or dense_m["hit@50_n"] != FROZEN_DENSE["hit@50_n"]
        or abs(dense_m["mrr"] - FROZEN_DENSE["mrr"]) > 1e-4
    ):
        raise SystemExit("BLOCKED — reproduced dense aggregates != frozen cells: %s" % dense_m)
    print("GATE DENSE PASS", dense_m, flush=True)

    # --- RRF ---
    print("fusing RRF k=%s..." % hf.RRF_K, flush=True)
    fused1 = {}
    fused_rank1 = {}
    fused_score = {}
    for r in rows:
        fused = hf.fuse_rrf(bm25_hits[r["query_id"]], dense_hits[r["query_id"]], k=hf.RRF_K)
        fused1[r["query_id"]] = fused
        rk, sc = hf.gold_fused_rank(fused, r["source_doc_id"])
        fused_rank1[r["query_id"]] = rk
        fused_score[r["query_id"]] = sc
    # second pass identity
    fused_rank2 = {}
    for r in rows:
        fused = hf.fuse_rrf(bm25_hits[r["query_id"]], dense_hits[r["query_id"]], k=hf.RRF_K)
        rk, _sc = hf.gold_fused_rank(fused, r["source_doc_id"])
        fused_rank2[r["query_id"]] = rk
    if fused_rank1 != fused_rank2:
        raise SystemExit("BLOCKED — RRF ranks not identical on second pass")
    print("RRF rank identity PASS", flush=True)

    hybrid_m = kn_metrics([fused_rank1[r["query_id"]] for r in rows])

    # stats
    union_sizes = []
    overlap_sizes = []
    per_path = os.path.join(_DIR, "HYBRID_PER_QUERY.csv")
    fields = [
        "query_id", "split", "script", "source_doc_id", "r2_primary",
        "query_text",
        "bm25_rank", "dense_rank", "hybrid_rank",
        "bm25_hit@1", "bm25_hit@5", "bm25_hit@10", "bm25_hit@50",
        "dense_hit@1", "dense_hit@5", "dense_hit@10", "dense_hit@50",
        "hybrid_hit@1", "hybrid_hit@5", "hybrid_hit@10", "hybrid_hit@50",
        "bm25_rr", "dense_rr", "hybrid_rr", "hybrid_rrf_score",
        "n_bm25_hits", "n_dense_hits", "n_union", "n_overlap",
        "A_bm25_success_retained", "B_dense_success_retained",
        "C_bm25_miss_recovered", "D_dense_miss_recovered",
        "E_both_miss", "F_lost_single_system_success",
        "room_cat1", "vocab_control",
    ]
    per_rows = []
    with open(per_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            qid = r["query_id"]
            br = bm25_rank_obs[qid]
            drk = int(dense_search[qid]["gold_rank"])
            hr = fused_rank1[qid]
            bhits = bm25_hits[qid]
            dhits = dense_hits[qid]
            bset = {int(d) for d, _s in bhits}
            dset = {int(d) for d, _s in dhits}
            n_union = len(bset | dset)
            n_ov = len(bset & dset)
            union_sizes.append(n_union)
            overlap_sizes.append(n_ov)
            b50 = int(br <= 50)
            d50 = int(drk <= 50)
            h50 = int(hr <= 50)
            flags = hybrid_case_flags(b50, d50, h50)
            primary = tax.get(qid) or p3[qid]["r2_primary"] or ("SUCCESS" if br <= 5 else "")
            row = {
                "query_id": qid,
                "split": r["split"],
                "script": r["script"],
                "source_doc_id": r["source_doc_id"],
                "r2_primary": primary,
                "query_text": r["query_text"],
                "bm25_rank": br if br < 999 else "",
                "dense_rank": drk,
                "hybrid_rank": hr if hr < 999 else "",
                "bm25_hit@1": int(br <= 1),
                "bm25_hit@5": int(br <= 5),
                "bm25_hit@10": int(br <= 10),
                "bm25_hit@50": b50,
                "dense_hit@1": int(drk <= 1),
                "dense_hit@5": int(drk <= 5),
                "dense_hit@10": int(drk <= 10),
                "dense_hit@50": d50,
                "hybrid_hit@1": int(hr <= 1),
                "hybrid_hit@5": int(hr <= 5),
                "hybrid_hit@10": int(hr <= 10),
                "hybrid_hit@50": h50,
                "bm25_rr": round(rec_rank(br), 6),
                "dense_rr": round(rec_rank(drk), 6),
                "hybrid_rr": round(rec_rank(hr), 6),
                "hybrid_rrf_score": "" if fused_score[qid] is None else round(float(fused_score[qid]), 8),
                "n_bm25_hits": len(bhits),
                "n_dense_hits": len(dhits),
                "n_union": n_union,
                "n_overlap": n_ov,
                "room_cat1": int(qid in ROOM_CAT1),
                "vocab_control": int(qid in VOCAB_CONTROLS),
                **flags,
            }
            per_rows.append(row)
            w.writerow(row)

    def trans(src_key: str, k: int) -> dict:
        hh = hm = mh = mm = 0
        hk = "hybrid_hit@%s" % k
        for row in per_rows:
            sh = int(row[src_key]) == 1
            dh = int(row[hk]) == 1
            if sh and dh:
                hh += 1
            elif sh and not dh:
                hm += 1
            elif (not sh) and dh:
                mh += 1
            else:
                mm += 1
        out = {
            "hit_hit": hh,
            "hit_miss": hm,
            "miss_hit": mh,
            "miss_miss": mm,
            "recovered": mh,
            "regressed": hm,
            "n": 51,
        }
        out["mcnemar_exact"] = mcnemar_exact(hm, mh)
        return out

    room1 = [row for row in per_rows if row["query_id"] in ROOM_CAT1]
    vocab = [row for row in per_rows if row["query_id"] in VOCAB_CONTROLS]

    def slice_hit50(group):
        return {
            "n": len(group),
            "bm25_hit@50": sum(int(r["bm25_hit@50"]) for r in group),
            "dense_hit@50": sum(int(r["dense_hit@50"]) for r in group),
            "hybrid_hit@50": sum(int(r["hybrid_hit@50"]) for r in group),
            "bm25_hit@5": sum(int(r["bm25_hit@5"]) for r in group),
            "dense_hit@5": sum(int(r["dense_hit@5"]) for r in group),
            "hybrid_hit@5": sum(int(r["hybrid_hit@5"]) for r in group),
        }

    counts = {
        "A_bm25_success_retained@50": sum(int(r["A_bm25_success_retained"]) for r in per_rows),
        "B_dense_success_retained@50": sum(int(r["B_dense_success_retained"]) for r in per_rows),
        "C_bm25_miss_recovered@50": sum(int(r["C_bm25_miss_recovered"]) for r in per_rows),
        "D_dense_miss_recovered@50": sum(int(r["D_dense_miss_recovered"]) for r in per_rows),
        "E_both_miss@50": sum(int(r["E_both_miss"]) for r in per_rows),
        "F_lost_single_system_success@50": sum(int(r["F_lost_single_system_success"]) for r in per_rows),
        "C_bm25_miss_recovered@5": sum(int(r["bm25_hit@5"] == 0 and r["hybrid_hit@5"] == 1) for r in per_rows),
        "D_dense_miss_recovered@5": sum(int(r["dense_hit@5"] == 0 and r["hybrid_hit@5"] == 1) for r in per_rows),
        "F_lost_bm25_hit5": sum(int(r["bm25_hit@5"] == 1 and r["hybrid_hit@5"] == 0) for r in per_rows),
        "F_lost_dense_hit5": sum(int(r["dense_hit@5"] == 1 and r["hybrid_hit@5"] == 0) for r in per_rows),
        "F_lost_bm25_hit50": sum(int(r["bm25_hit@50"] == 1 and r["hybrid_hit@50"] == 0) for r in per_rows),
        "F_lost_dense_hit50": sum(int(r["dense_hit@50"] == 1 and r["hybrid_hit@50"] == 0) for r in per_rows),
    }

    runtime = {
        "bm25_cache_load_seconds": round(t_bm25_load, 3),
        "bm25_search_seconds": round(t_bm25_search, 3),
        "dense_npy_load_seconds": round(t_npy, 3),
        "encoder_load_seconds": round(t_model, 3),
        "query_embed_seconds": round(t_qenc, 3),
        "dense_search_seconds": round(t_dsearch, 3),
        "device": "cpu",
        "cuda": False,
        "document_embeddings_regenerated": False,
    }

    try:
        import sentence_transformers
        import torch

        packages = {
            "numpy": np.__version__,
            "torch": torch.__version__,
            "sentence_transformers": sentence_transformers.__version__,
        }
    except Exception as exc:  # pragma: no cover
        packages = {"import_error": str(exc)}

    wall = round(time.perf_counter() - wall_t0, 3)
    runtime["wall_seconds"] = wall
    runtime["hardware"] = {
        "device": "cpu",
        "cuda": False,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "cpu_count": os.cpu_count(),
        "python": sys.version.split()[0],
        "packages": packages,
    }

    config = {
        "experiment_id": "HYBRID-RRF",
        "timestamp_utc": utc_now(),
        "branch": branch,
        "commit": commit,
        "test_accessed": False,
        "preregistration_sha256": sha256_file(PREREG),
        "hybrid_fusion_py_sha256": sha256_file(os.path.join(_DIR, "hybrid_fusion.py")),
        "run_hybrid_py_sha256": sha256_file(os.path.join(_DIR, "run_hybrid.py")),
        "r2_b0_per_query_sha256": sha256_file(R2_PER_QUERY),
        "dense_per_query_sha256": sha256_file(P3_PER_QUERY),
        "dense_npy_path": os.path.relpath(P3_NPY, ROOT).replace("\\", "/"),
        "dense_npy_bytes": os.path.getsize(P3_NPY),
        "dense_npy_sha256": sha256_file(P3_NPY),
        "bm25_cache_path": os.path.relpath(R2_CACHE, ROOT).replace("\\", "/"),
        "bm25_cache_bytes": os.path.getsize(R2_CACHE),
        "bm25_implementation": "experiments/phase5_roman_urdu/run_phase5.py",
        "encoder": enc_info,
        "corpus_sha256": cache_meta["corpus_sha256"],
        "dict_sha256": cache_meta["dict_sha256"],
        "rrf_k": hf.RRF_K,
        "candidate_depth": TOP_K,
        "tie_break": "higher RRF, then smaller doc_id",
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "cpu_count": os.cpu_count(),
        "packages": packages,
        "hybrid": True,
        "rerank": False,
        "model_shopping": False,
        "parameter_tuning": False,
        "gold_injection": False,
        "query_rewriting": False,
        "document_embeddings_regenerated": False,
        "gates": {"bm25": "PASS", "dense": "PASS"},
    }
    with open(os.path.join(ART, "hybrid_config.json"), "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
        f.write("\n")

    index_meta = {
        "dense_npy": os.path.relpath(P3_NPY, ROOT).replace("\\", "/"),
        "dense_shape": [111860, 384],
        "dense_meta": dense_meta,
        "bm25_cache_meta": cache_meta,
        "n_docs": 111860,
        "id_mapping": "row index == CSV Index == source_doc_id",
        "document_embeddings_regenerated": False,
    }
    with open(os.path.join(ART, "hybrid_index_meta.json"), "w", encoding="utf-8") as f:
        json.dump(index_meta, f, indent=2)
        f.write("\n")

    rep = {
        "n_queries": 51,
        "union_size_mean": float(sum(union_sizes) / len(union_sizes)),
        "union_size_min": int(min(union_sizes)),
        "union_size_max": int(max(union_sizes)),
        "overlap_mean": float(sum(overlap_sizes) / len(overlap_sizes)),
        "overlap_min": int(min(overlap_sizes)),
        "overlap_max": int(max(overlap_sizes)),
        "rrf_k": hf.RRF_K,
        "note": "Union of Method-D Top-50 and dense Top-50; overlap is |A∩B|.",
    }
    with open(os.path.join(ART, "hybrid_representation_stats.json"), "w", encoding="utf-8") as f:
        json.dump(rep, f, indent=2)
        f.write("\n")

    summary = {
        "experiment_id": "HYBRID-RRF",
        "timestamp_utc": utc_now(),
        "test_accessed": False,
        "gates": {"bm25_gold_rank": "PASS", "dense_gold_rank_and_rank1": "PASS", "rrf_second_pass": "PASS"},
        "frozen_bm25": FROZEN_BM25,
        "frozen_dense": FROZEN_DENSE,
        "reproduced_bm25": bm25_m,
        "reproduced_dense": dense_m,
        "hybrid_rrf": hybrid_m,
        "transition_vs_bm25_top5": trans("bm25_hit@5", 5),
        "transition_vs_bm25_top50": trans("bm25_hit@50", 50),
        "transition_vs_dense_top5": trans("dense_hit@5", 5),
        "transition_vs_dense_top50": trans("dense_hit@50", 50),
        "case_counts": counts,
        "room_cat1": {"ids": ROOM_CAT1, **slice_hit50(room1)},
        "vocab_controls": {"ids": VOCAB_CONTROLS, **slice_hit50(vocab)},
        "runtime": runtime,
        "safety": {
            "test_accessed": False,
            "frozen_m0_modified": False,
            "plos_modified": False,
            "phase3_modified": False,
            "r2_modified": False,
            "query_tuning": False,
            "model_shopping": False,
            "parameter_tuning": False,
            "reranking": False,
            "gold_injection": False,
            "document_embeddings_regenerated": False,
        },
    }
    with open(os.path.join(ART, "hybrid_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print("HYBRID", hybrid_m, flush=True)
    print("cases", counts, flush=True)
    print("ROOM Cat1 hybrid Hit@50", summary["room_cat1"]["hybrid_hit@50"], "/11", flush=True)
    print("EVALUATION COMPLETE", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
