# -*- coding: utf-8 -*-
"""PHASE8-3WAY-RRF: unweighted RRF k=60 of BM25 + Dense + NG3 Top-50.

Does not edit Phase 2–7, M0, or TEST. Does not tune k or weights.
Does not regenerate dense document embeddings.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import pickle
import platform
import sys
import time
from datetime import datetime, timezone

os.environ.setdefault("MKL_THREADING_LAYER", "SEQUENTIAL")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.pop("KMP_DUPLICATE_LIB_OK", None)

import numpy as np  # noqa: E402

_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(_DIR, "..", "..", ".."))
P5 = os.path.join(ROOT, "experiments", "phase5_roman_urdu")
P2 = os.path.join(ROOT, "experiments", "ultra_v2", "phase2_roman")
P3 = os.path.join(ROOT, "experiments", "ultra_v2", "phase3_dense")
P4 = os.path.join(ROOT, "experiments", "ultra_v2", "phase4_hybrid")
P5NG = os.path.join(ROOT, "experiments", "ultra_v2", "phase5_ng3")
BENCH = os.path.join(ROOT, "experiments", "ultra_v2", "benchmark")
TEST_DIR = os.path.abspath(os.path.join(BENCH, "test"))
ART = os.path.join(_DIR, "artifacts")
PREREG = os.path.join(_DIR, "PHASE8_PREREGISTRATION.md")
B0_CACHE = os.path.join(P2, "artifacts", "_index_cache.pkl")
B0_PER = os.path.join(P2, "artifacts", "r2_b0_per_query.csv")
DENSE_PER = os.path.join(P3, "DENSE_PER_QUERY.csv")
HYBRID_PER = os.path.join(P4, "HYBRID_PER_QUERY.csv")
NG3_PER = os.path.join(P5NG, "R2NG3_PER_QUERY.csv")
P3_NPY = os.path.join(P3, "artifacts", "dense_doc_embeddings.npy")
P3_META = os.path.join(P3, "artifacts", "dense_index_meta.json")
ALLOWED_SPLITS = ("train", "dev")
EXPECTED_DICT_SHA = "30c3f61a64ec641abbb3acdbc7a8bcaf197f0238f1bf9e76c2c7ce8e590f86a3"
EXPECTED_CORPUS_SHA = "8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231"
EXPECTED_MD_STREAM_SHA = "323a07b46e2377b5ec807006c2efd06f9b1ae19a65f1389d22f32b435ca0c3fb"
EXPECTED_NG3_STREAM_SHA = "1ab004bb26e9231827137020808ca008981648d62a834755af5779454d8c553d"
EXPECTED_CSV_SHA = {
    "bm25": "cc0d31c2b4bb108ea7114811cafe1da68c1f1f4a88db8dd1d4700a5dd9429509",
    "dense": "4875884cbaeecd025df343befc5bccc6c35fc01dda54cff45173b56efab9fdb1",
    "hybrid": "c5174379abc872c2e2e7584b7974a461c32c287270e37f961483d4ead959828a",
    "ng3": "0149bd52dc00d7ace5bb510e17b5789037766ea69886738368e6f546a21ab3e5",
}
FROZEN_BM25 = {"n": 51, "hit@1_n": 1, "hit@5_n": 4, "hit@10_n": 4, "hit@50_n": 6, "mrr": 0.0375}
FROZEN_DENSE = {"n": 51, "hit@1_n": 5, "hit@5_n": 15, "hit@10_n": 16, "hit@50_n": 22, "mrr": 0.1726}
FROZEN_HYBRID = {"n": 51, "hit@1_n": 3, "hit@5_n": 11, "hit@10_n": 19, "hit@50_n": 25, "mrr": 0.1422}
FROZEN_NG3 = {"n": 51, "hit@1_n": 3, "hit@5_n": 6, "hit@10_n": 6, "hit@50_n": 8, "mrr": 0.075}
ROOM_CAT1 = [
    "KN001", "KN006", "KN008", "KN010", "KN011",
    "KN018", "KN037", "KN045", "KN047", "KN050", "KN051",
]
QUAD23 = [
    "KN002", "KN005", "KN006", "KN008", "KN010", "KN018", "KN020", "KN021",
    "KN022", "KN024", "KN025", "KN026", "KN027", "KN028", "KN032", "KN036",
    "KN037", "KN041", "KN042", "KN044", "KN047", "KN051", "KN054",
]
UNION3_ONLY = ["KN035", "KN040", "KN050"]
TOP_K = 50

sys.path.insert(0, _DIR)
sys.path.insert(0, P5)
sys.path.insert(0, P2)
sys.path.insert(0, P3)
sys.path.insert(0, P4)
import run_phase5 as p5  # noqa: E402
import ng3_matching as ng3  # noqa: E402
import dense_retrieval as dr  # noqa: E402
import hybrid_fusion as hf  # noqa: E402
import fusion_3way as f3  # noqa: E402

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


def parse_rank(val: object) -> int:
    s = "" if val is None else str(val).strip()
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


# Copied verbatim from experiments/ultra_v2/phase2_roman/run_r2_1_experiment.py
# (function exact_mcnemar). Logic not altered.
def exact_mcnemar(n01: int, n10: int) -> dict:
    """Exact McNemar two-sided test on discordant pairs.

    n01: control miss, treatment hit
    n10: control hit, treatment miss
    """
    n = n01 + n10
    if n == 0:
        return {"n_discordant": 0, "p_two_sided": 1.0, "note": "no discordant pairs"}
    k = min(n01, n10)
    # two-sided exact binomial
    p = 0.0
    for i in range(0, k + 1):
        p += math.comb(n, i)
    p = min(1.0, 2.0 * p * (0.5 ** n))
    return {
        "n_discordant": n,
        "n_control_miss_treatment_hit": n01,
        "n_control_hit_treatment_miss": n10,
        "p_two_sided": round(p, 6),
        "note": "exact McNemar (binomial, two-sided)",
    }


def pair_mcnemar(hits_a: dict[str, int], hits_b: dict[str, int], ids: list[str]) -> dict:
    n01 = n10 = 0
    rec, reg = [], []
    for qid in ids:
        a, b = int(hits_a[qid]), int(hits_b[qid])
        if (not a) and b:
            n01 += 1
            rec.append(qid)
        elif a and (not b):
            n10 += 1
            reg.append(qid)
    raw = exact_mcnemar(n01, n10)
    return {
        "n01_control_miss_treatment_hit": n01,
        "n10_control_hit_treatment_miss": n10,
        "recovered_ids": rec,
        "regressed_ids": reg,
        "mcnemar": raw,
        "p_two_sided": raw["p_two_sided"],
        "significant_at_0.05": bool(raw["n_discordant"] > 0 and raw["p_two_sided"] < 0.05),
    }


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
                if p5.detect_script(text) != "ROMAN":
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


def load_csv(path: str) -> dict[str, dict]:
    refuse_test_path(path)
    out = {}
    with open(path, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            out[r["query_id"]] = r
    return out


def write_blocked(payload: dict) -> None:
    os.makedirs(ART, exist_ok=True)
    with open(os.path.join(ART, "phase8_blocked.json"), "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(json.dumps(payload, indent=2, ensure_ascii=False), flush=True)


def metrics_match(got: dict, exp: dict) -> bool:
    return (
        got["hit@1_n"] == exp["hit@1_n"]
        and got["hit@5_n"] == exp["hit@5_n"]
        and got["hit@10_n"] == exp["hit@10_n"]
        and got["hit@50_n"] == exp["hit@50_n"]
        and abs(got["mrr"] - exp["mrr"]) <= 1e-4
    )


def main() -> int:
    wall_t0 = time.perf_counter()
    print("label: ULTRA v2 PHASE8-3WAY-RRF", flush=True)
    print("TEST_accessed: no", flush=True)
    branch, commit = git_identity()
    print("git", branch, commit, flush=True)
    if not os.path.isfile(PREREG):
        raise SystemExit("BLOCKED — PHASE8_PREREGISTRATION.md missing")
    demo2 = hf.fuse_rrf([(5, 1.0), (3, 0.5)], [(3, 0.9), (7, 0.8)], k=60)
    assert [t[0] for t in demo2] == [3, 5, 7]
    demo3 = f3.fuse_rrf_3(
        [(5, 1.0), (3, 0.5)],
        [(3, 0.9), (7, 0.8)],
        [(7, 1.0), (9, 0.4)],
        k=60,
    )
    assert [t[0] for t in demo3] == [3, 7, 5, 9]
    os.makedirs(ART, exist_ok=True)
    refuse_test_path(p5.CORPUS)
    refuse_test_path(p5.DICT_PATH)

    csv_paths = {"bm25": B0_PER, "dense": DENSE_PER, "hybrid": HYBRID_PER, "ng3": NG3_PER}
    csv_sha = {}
    for key, path in csv_paths.items():
        refuse_test_path(path)
        got = sha256_file(path)
        csv_sha[key] = got
        if got != EXPECTED_CSV_SHA[key]:
            write_blocked({"decision": "BLOCKED", "reason": "%s CSV SHA mismatch" % key, "got": got})
            raise SystemExit("BLOCKED — %s CSV SHA-256 mismatch" % key)

    dict_sha = sha256_file(p5.DICT_PATH)
    if dict_sha != EXPECTED_DICT_SHA:
        write_blocked({"decision": "BLOCKED", "reason": "dictionary SHA mismatch", "got": dict_sha})
        raise SystemExit("BLOCKED — dictionary SHA-256 mismatch")
    corpus_sha = sha256_file(p5.CORPUS)
    if corpus_sha != EXPECTED_CORPUS_SHA:
        write_blocked({"decision": "BLOCKED", "reason": "corpus SHA mismatch", "got": corpus_sha})
        raise SystemExit("BLOCKED — corpus SHA-256 mismatch")

    rows = load_roman_kn()
    ids = [r["query_id"] for r in rows]
    b0 = load_csv(B0_PER)
    dense = load_csv(DENSE_PER)
    hybrid = load_csv(HYBRID_PER)
    ng3_tab = load_csv(NG3_PER)
    if not (len(b0) == len(dense) == len(hybrid) == len(ng3_tab) == 51):
        write_blocked({"decision": "BLOCKED", "reason": "frozen CSV n != 51"})
        raise SystemExit("BLOCKED — frozen per-query n != 51")
    for r in rows:
        qid = r["query_id"]
        gold = r["source_doc_id"]
        for name, tab in (("b0", b0), ("dense", dense), ("hybrid", hybrid), ("ng3", ng3_tab)):
            if qid not in tab or int(tab[qid]["source_doc_id"]) != gold:
                write_blocked({"decision": "BLOCKED", "reason": "query/gold mismatch", "id": qid, "file": name})
                raise SystemExit("BLOCKED — query/gold mismatch")
    for qid in QUAD23 + ROOM_CAT1 + UNION3_ONLY:
        if qid not in set(ids):
            raise SystemExit("BLOCKED — missing slice id %s" % qid)

    if not os.path.isfile(B0_CACHE):
        write_blocked({"decision": "BLOCKED", "reason": "Method-D cache missing"})
        raise SystemExit("BLOCKED — Method-D cache missing")
    print("loading Method-D cache (read-only)...", flush=True)
    t0 = time.perf_counter()
    with open(B0_CACHE, "rb") as f:
        blob = pickle.load(f)
    t_bm25_load = time.perf_counter() - t0
    want_meta = {
        "corpus_sha256": corpus_sha,
        "dict_sha256": dict_sha,
        "k1": p5.BM25_K1,
        "b": p5.BM25_B,
        "tokenizer": p5.TOKEN_RE.pattern,
    }
    if blob.get("meta") != want_meta:
        write_blocked({"decision": "BLOCKED", "reason": "BM25 cache meta mismatch"})
        raise SystemExit("BLOCKED — BM25 cache meta mismatch")
    roman_bm25 = blob["roman_bm25"]
    print("BM25 cache hit", flush=True)

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
        exp = parse_rank(b0[r["query_id"]].get("gold_rank"))
        if rank != exp:
            bm25_mismatches.append({"query_id": r["query_id"], "expected": exp, "observed": rank})
    t_bm25_search = time.perf_counter() - t1
    if bm25_mismatches:
        write_blocked({"decision": "BLOCKED", "reason": "BM25 ranks != r2_b0", "mismatches": bm25_mismatches})
        raise SystemExit("BLOCKED — BM25 gold ranks do not match r2_b0_per_query.csv")
    bm25_m = kn_metrics([bm25_rank_obs[q] for q in ids])
    if not metrics_match(bm25_m, FROZEN_BM25):
        write_blocked({"decision": "BLOCKED", "reason": "BM25 aggregates != frozen", "got": bm25_m})
        raise SystemExit("BLOCKED — reproduced BM25 != frozen cells")
    print("GATE BM25 PASS", bm25_m, flush=True)

    print("loading Phase-3 document matrix (no regenerate)...", flush=True)
    t2 = time.perf_counter()
    if not os.path.isfile(P3_NPY) or not os.path.isfile(P3_META):
        raise SystemExit("BLOCKED — Phase-3 dense matrix/meta missing")
    with open(P3_META, encoding="utf-8") as f:
        dmeta = json.load(f)
    if dmeta.get("complete") is not True:
        raise SystemExit("BLOCKED — dense index meta incomplete")
    if dmeta.get("model_id") != dr.MODEL_ID or dmeta.get("model_revision") != dr.MODEL_REVISION:
        raise SystemExit("BLOCKED — dense meta encoder mismatch")
    if dmeta.get("corpus_sha256") != EXPECTED_CORPUS_SHA:
        raise SystemExit("BLOCKED — dense meta corpus SHA mismatch")
    arr = np.load(P3_NPY, mmap_mode="r")
    if tuple(arr.shape) != (111860, 384):
        raise SystemExit("BLOCKED — dense shape %s" % (arr.shape,))
    doc_matrix = np.array(arr, dtype=np.float32, copy=True)
    t_npy = time.perf_counter() - t2
    print("loading e5-small for queries only...", flush=True)
    t3 = time.perf_counter()
    model, enc_info = dr.load_encoder()
    t_model = time.perf_counter() - t3
    t4 = time.perf_counter()
    q_vecs = dr.encode_texts(
        model,
        [r["query_text"] for r in rows],
        kind="query",
        prefix_mode=enc_info["prefix_mode"],
        prompt_name=enc_info.get("query_prompt_name"),
        show_progress=False,
    )
    t_qenc = time.perf_counter() - t4
    print("dense query encode n=51 %.2fs" % t_qenc, flush=True)
    t5 = time.perf_counter()
    dense_hits = {}
    dense_rank_obs = {}
    dense_mismatches = []
    for r, qv in zip(rows, q_vecs):
        res = dr.search_query_vec(doc_matrix, qv, r["source_doc_id"], k=TOP_K)
        dense_hits[r["query_id"]] = res["topk"]
        dense_rank_obs[r["query_id"]] = int(res["gold_rank"])
        exp = dense[r["query_id"]]
        if int(res["gold_rank"]) != int(exp["dense_rank"]) or int(res["rank1_doc_id"]) != int(exp["dense_rank1_doc_id"]):
            dense_mismatches.append({"query_id": r["query_id"], "obs": res["gold_rank"]})
    t_dsearch = time.perf_counter() - t5
    if dense_mismatches:
        write_blocked({"decision": "BLOCKED", "reason": "dense ranks != DENSE_PER_QUERY", "n": len(dense_mismatches)})
        raise SystemExit("BLOCKED — dense ranks/rank-1 ids do not match DENSE_PER_QUERY.csv")
    dense_m = kn_metrics([dense_rank_obs[q] for q in ids])
    if not metrics_match(dense_m, FROZEN_DENSE):
        write_blocked({"decision": "BLOCKED", "reason": "dense aggregates != frozen", "got": dense_m})
        raise SystemExit("BLOCKED — reproduced dense != frozen cells")
    print("GATE DENSE PASS", dense_m, flush=True)

    print("building frozen NG3 representation (n=3, Method-D tokens)...", flush=True)
    import pandas as pd

    df = pd.read_csv(p5.CORPUS, encoding="utf-8-sig")
    texts = df["combined_text"].fillna("").astype(str).tolist()
    if len(texts) != 111860:
        raise SystemExit("BLOCKED — corpus size %s" % len(texts))
    fwd = p5.load_roman_dict()
    rev = p5.load_reverse_roman(fwd)
    ng3_docs: list[list[str]] = []
    md_hasher = hashlib.sha256()
    ng3_hasher = hashlib.sha256()
    t_tok = time.perf_counter()
    for i, text in enumerate(texts):
        utoks = p5.tokenize(text)
        md = [t for t in (p5.romanize_token(tok, rev) for tok in utoks) if t]
        feats = ng3.expand_tokens(md)
        ng3_docs.append(feats)
        md_hasher.update((" ".join(md) + "\n").encode("utf-8"))
        ng3_hasher.update((" ".join(feats) + "\n").encode("utf-8"))
        if (i + 1) % 20000 == 0:
            print("  tokenize %s/%s" % (i + 1, len(texts)), flush=True)
    tokenize_sec = time.perf_counter() - t_tok
    if md_hasher.hexdigest() != EXPECTED_MD_STREAM_SHA or ng3_hasher.hexdigest() != EXPECTED_NG3_STREAM_SHA:
        write_blocked({"decision": "BLOCKED", "reason": "NG3 feature stream SHA mismatch"})
        raise SystemExit("BLOCKED — NG3 representation stream does not match Phase 2")
    print("tokenize+expand %.1fs" % tokenize_sec, flush=True)
    print("build NG3 BM25 k1=1.5 b=0.75...", flush=True)
    t_b = time.perf_counter()
    ng3_bm25 = p5.BM25(ng3_docs, k1=1.5, b=0.75)
    t_ng3_build = time.perf_counter() - t_b
    print("ng3 BM25 %.1fs" % t_ng3_build, flush=True)

    t_s = time.perf_counter()
    ng3_hits = {}
    ng3_rank_obs = {}
    ng3_mismatches = []
    for r in rows:
        qtoks = p5.tokenize(r["query_text"])
        q3 = ng3.expand_tokens(qtoks)
        nhits = ng3_bm25.search(q3, top_k=TOP_K)
        ng3_hits[r["query_id"]] = nhits
        nr = p5.rank_of(nhits, r["source_doc_id"])
        ng3_rank_obs[r["query_id"]] = nr
        exp_n = parse_rank(ng3_tab[r["query_id"]].get("ng3_rank"))
        if nr != exp_n:
            ng3_mismatches.append({"query_id": r["query_id"], "expected": exp_n, "observed": nr})
    t_ng3_search = time.perf_counter() - t_s
    if ng3_mismatches:
        write_blocked({"decision": "BLOCKED", "reason": "NG3 ranks != R2NG3_PER_QUERY", "mismatches": ng3_mismatches})
        raise SystemExit("BLOCKED — NG3 gold ranks do not match R2NG3_PER_QUERY.csv")
    ng3_m = kn_metrics([ng3_rank_obs[q] for q in ids])
    if not metrics_match(ng3_m, FROZEN_NG3):
        write_blocked({"decision": "BLOCKED", "reason": "NG3 aggregates != frozen", "got": ng3_m})
        raise SystemExit("BLOCKED — reproduced NG3 != frozen cells")
    print("GATE NG3 PASS", ng3_m, flush=True)

    print("2-way Hybrid sanity (Phase-4 fuse_rrf k=60)...", flush=True)
    hybrid_mismatches = []
    hybrid_rank_obs = {}
    for r in rows:
        fused2 = hf.fuse_rrf(bm25_hits[r["query_id"]], dense_hits[r["query_id"]], k=hf.RRF_K)
        rk, _sc = hf.gold_fused_rank(fused2, r["source_doc_id"])
        hybrid_rank_obs[r["query_id"]] = rk
        exp_h = parse_rank(hybrid[r["query_id"]].get("hybrid_rank"))
        if rk != exp_h:
            hybrid_mismatches.append({"query_id": r["query_id"], "expected": exp_h, "observed": rk})
    if hybrid_mismatches:
        write_blocked({"decision": "BLOCKED", "reason": "2-way RRF != HYBRID_PER_QUERY", "mismatches": hybrid_mismatches})
        raise SystemExit("BLOCKED — 2-way RRF gold ranks do not match HYBRID_PER_QUERY.csv")
    hybrid_m = kn_metrics([hybrid_rank_obs[q] for q in ids])
    if not metrics_match(hybrid_m, FROZEN_HYBRID):
        write_blocked({"decision": "BLOCKED", "reason": "hybrid aggregates != frozen", "got": hybrid_m})
        raise SystemExit("BLOCKED — reproduced 2-way hybrid != frozen cells")
    print("GATE 2-WAY HYBRID PASS", hybrid_m, flush=True)

    print("fusing 3-way RRF k=%s..." % f3.RRF_K, flush=True)
    fused_rank = {}
    fused_score = {}
    fused_lists = {}
    for r in rows:
        fused = f3.fuse_rrf_3(
            bm25_hits[r["query_id"]],
            dense_hits[r["query_id"]],
            ng3_hits[r["query_id"]],
            k=f3.RRF_K,
        )
        fused_lists[r["query_id"]] = fused
        rk, sc = f3.gold_fused_rank(fused, r["source_doc_id"])
        fused_rank[r["query_id"]] = rk
        fused_score[r["query_id"]] = sc
    fused_rank2 = {}
    for r in rows:
        fused = f3.fuse_rrf_3(
            bm25_hits[r["query_id"]],
            dense_hits[r["query_id"]],
            ng3_hits[r["query_id"]],
            k=f3.RRF_K,
        )
        rk, _sc = f3.gold_fused_rank(fused, r["source_doc_id"])
        fused_rank2[r["query_id"]] = rk
    if fused_rank != fused_rank2:
        write_blocked({"decision": "BLOCKED", "reason": "3-way RRF not identical on repeat"})
        raise SystemExit("BLOCKED — 3-way RRF ranks not identical on second pass")
    print("3-way RRF rank identity PASS", flush=True)

    p8_m = kn_metrics([fused_rank[q] for q in ids])
    print("P8", p8_m, flush=True)

    h5 = {
        "bm25": {q: int(bm25_rank_obs[q] <= 5) for q in ids},
        "dense": {q: int(dense_rank_obs[q] <= 5) for q in ids},
        "hybrid": {q: int(hybrid_rank_obs[q] <= 5) for q in ids},
        "ng3": {q: int(ng3_rank_obs[q] <= 5) for q in ids},
        "p8": {q: int(fused_rank[q] <= 5) for q in ids},
    }
    h50 = {
        "bm25": {q: int(bm25_rank_obs[q] <= 50) for q in ids},
        "dense": {q: int(dense_rank_obs[q] <= 50) for q in ids},
        "hybrid": {q: int(hybrid_rank_obs[q] <= 50) for q in ids},
        "ng3": {q: int(ng3_rank_obs[q] <= 50) for q in ids},
        "p8": {q: int(fused_rank[q] <= 50) for q in ids},
    }
    mcn_h5 = pair_mcnemar(h5["hybrid"], h5["p8"], ids)
    mcn_h50 = pair_mcnemar(h50["hybrid"], h50["p8"], ids)
    rec23 = [q for q in QUAD23 if h50["p8"][q] == 1]
    room_p8 = [q for q in ROOM_CAT1 if h50["p8"][q] == 1]
    vs_h_gain50 = [q for q in ids if h50["hybrid"][q] == 0 and h50["p8"][q] == 1]
    vs_h_loss50 = [q for q in ids if h50["hybrid"][q] == 1 and h50["p8"][q] == 0]
    vs_h_gain5 = [q for q in ids if h5["hybrid"][q] == 0 and h5["p8"][q] == 1]
    vs_h_loss5 = [q for q in ids if h5["hybrid"][q] == 1 and h5["p8"][q] == 0]

    per_rows = []
    for r in rows:
        qid = r["query_id"]
        br, drk, nr, hr, p8r = bm25_rank_obs[qid], dense_rank_obs[qid], ng3_rank_obs[qid], hybrid_rank_obs[qid], fused_rank[qid]
        bset = {int(d) for d, _s in bm25_hits[qid]}
        dset = {int(d) for d, _s in dense_hits[qid]}
        nset = {int(d) for d, _s in ng3_hits[qid]}
        per_rows.append({
            "query_id": qid,
            "split": r["split"],
            "script": "ROMAN",
            "source_doc_id": r["source_doc_id"],
            "query_text": r["query_text"],
            "bm25_rank": br if br < 999 else "",
            "dense_rank": drk,
            "ng3_rank": nr if nr < 999 else "",
            "hybrid2_rank": hr if hr < 999 else "",
            "p8_rank": p8r if p8r < 999 else "",
            "bm25_hit@5": int(br <= 5),
            "dense_hit@5": int(drk <= 5),
            "ng3_hit@5": int(nr <= 5),
            "hybrid2_hit@5": int(hr <= 5),
            "p8_hit@5": int(p8r <= 5),
            "bm25_hit@50": int(br <= 50),
            "dense_hit@50": int(drk <= 50),
            "ng3_hit@50": int(nr <= 50),
            "hybrid2_hit@50": int(hr <= 50),
            "p8_hit@50": int(p8r <= 50),
            "p8_rr": round(rec_rank(p8r), 6),
            "p8_rrf_score": "" if fused_score[qid] is None else round(float(fused_score[qid]), 8),
            "n_union3": len(bset | dset | nset),
            "n_triple_overlap": len(bset & dset & nset),
            "quad23": int(qid in QUAD23),
            "p8_recovered_quad23": int(qid in QUAD23 and p8r <= 50),
            "room_cat1": int(qid in ROOM_CAT1),
            "union3_only_phase6": int(qid in UNION3_ONLY),
        })

    csv_path = os.path.join(_DIR, "PHASE8_PER_QUERY.csv")
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(per_rows[0].keys()))
        w.writeheader()
        w.writerows(per_rows)

    wall = round(time.perf_counter() - wall_t0, 3)
    runtime = {
        "bm25_cache_load_seconds": round(t_bm25_load, 3),
        "bm25_search_seconds": round(t_bm25_search, 3),
        "dense_npy_load_seconds": round(t_npy, 3),
        "encoder_load_seconds": round(t_model, 3),
        "query_encode_seconds": round(t_qenc, 3),
        "dense_search_seconds": round(t_dsearch, 3),
        "ng3_tokenize_seconds": round(tokenize_sec, 3),
        "ng3_bm25_build_seconds": round(t_ng3_build, 3),
        "ng3_search_seconds": round(t_ng3_search, 3),
        "wall_seconds": wall,
        "device": "cpu",
        "cuda": False,
        "hardware": {
            "platform": platform.platform(),
            "processor": platform.processor(),
            "cpu_count": os.cpu_count(),
            "python": sys.version.split()[0],
            "numpy": np.__version__,
        },
    }
    config = {
        "experiment_id": "PHASE8-3WAY-RRF",
        "timestamp_utc": utc_now(),
        "branch": branch,
        "commit": commit,
        "test_accessed": False,
        "preregistration_sha256": sha256_file(PREREG),
        "rrf_k": f3.RRF_K,
        "n_inputs": 3,
        "weights": None,
        "csv_sha256": csv_sha,
        "corpus_sha256": corpus_sha,
        "dict_sha256": dict_sha,
        "method_d_token_stream_sha256": EXPECTED_MD_STREAM_SHA,
        "ng3_feature_stream_sha256": EXPECTED_NG3_STREAM_SHA,
        "gates": {
            "csv_sha_vs_phase6": "PASS",
            "corpus_sha": "PASS",
            "query_gold": "PASS",
            "bm25_vs_r2_b0": "PASS",
            "dense_vs_DENSE_PER_QUERY": "PASS",
            "ng3_vs_R2NG3_PER_QUERY": "PASS",
            "ng3_stream_sha": "PASS",
            "hybrid2_vs_HYBRID_PER_QUERY": "PASS",
            "rrf3_repeat": "PASS",
        },
        "document_embeddings_regenerated": False,
        "parameter_tuning": False,
    }
    with open(os.path.join(ART, "phase8_config.json"), "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
        f.write("\n")

    summary = {
        "experiment_id": "PHASE8-3WAY-RRF",
        "timestamp_utc": utc_now(),
        "test_accessed": False,
        "gates": config["gates"],
        "frozen": {
            "bm25": FROZEN_BM25,
            "dense": FROZEN_DENSE,
            "hybrid2": FROZEN_HYBRID,
            "ng3": FROZEN_NG3,
        },
        "phase8_3way_rrf": p8_m,
        "mcnemar_vs_hybrid2": {"hit@5": mcn_h5, "hit@50": mcn_h50},
        "vs_hybrid2": {
            "hit@5_recovered": vs_h_gain5,
            "hit@5_regressed": vs_h_loss5,
            "hit@50_recovered": vs_h_gain50,
            "hit@50_regressed": vs_h_loss50,
        },
        "quad23": {"n": 23, "p8_recovered": rec23, "p8_recovered_n": len(rec23)},
        "room_cat1": {
            "bm25": 0, "dense": 3, "hybrid2": 3, "ng3": 1,
            "p8": len(room_p8), "p8_ids": room_p8,
        },
        "union3_only_phase6_ranks": {q: fused_rank[q] if fused_rank[q] < 999 else None for q in UNION3_ONLY},
        "runtime": runtime,
        "safety": {
            "test_accessed": False,
            "k_tuned": False,
            "weights": False,
            "phase2_7_modified": False,
            "rerank": False,
        },
    }
    with open(os.path.join(ART, "phase8_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print("McNemar vs hybrid2 Hit@5", mcn_h5["p_two_sided"], "Hit@50", mcn_h50["p_two_sided"], flush=True)
    print("quad23", rec23, len(rec23), "/23", flush=True)
    print("ROOM", len(room_p8), "/11", room_p8, flush=True)
    print("vs hybrid50 recovered", vs_h_gain50, "regressed", vs_h_loss50, flush=True)
    print("EVALUATION COMPLETE", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
