# -*- coding: utf-8 -*-
"""PHASE10-CASCADE-B: title-triggered Hybrid-first cascade (Option B).

Does not edit Phase 2–9, M0, or TEST. Does not inject terms into Hybrid BM25.
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

import numpy as np  # noqa: E402

_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(_DIR, "..", "..", ".."))
P5 = os.path.join(ROOT, "experiments", "phase5_roman_urdu")
P2 = os.path.join(ROOT, "experiments", "ultra_v2", "phase2_roman")
P3 = os.path.join(ROOT, "experiments", "ultra_v2", "phase3_dense")
P4 = os.path.join(ROOT, "experiments", "ultra_v2", "phase4_hybrid")
P5NG = os.path.join(ROOT, "experiments", "ultra_v2", "phase5_ng3")
P9 = os.path.join(ROOT, "experiments", "ultra_v2", "phase9_entity_resource")
BENCH = os.path.join(ROOT, "experiments", "ultra_v2", "benchmark")
TEST_DIR = os.path.abspath(os.path.join(BENCH, "test"))
ART = os.path.join(_DIR, "artifacts")
PREREG = os.path.join(_DIR, "PHASE10_PREREGISTRATION.md")
B0_CACHE = os.path.join(P2, "artifacts", "_index_cache.pkl")
B0_PER = os.path.join(P2, "artifacts", "r2_b0_per_query.csv")
DENSE_PER = os.path.join(P3, "DENSE_PER_QUERY.csv")
HYBRID_PER = os.path.join(P4, "HYBRID_PER_QUERY.csv")
NG3_PER = os.path.join(P5NG, "R2NG3_PER_QUERY.csv")
P3_NPY = os.path.join(P3, "artifacts", "dense_doc_embeddings.npy")
P3_META = os.path.join(P3, "artifacts", "dense_index_meta.json")
TITLE_CSV = os.path.join(P9, "artifacts", "bilingual_titles.csv")
P9_SCORED = os.path.join(P9, "artifacts", "phase9_scored_results.csv")

ALLOWED_SPLITS = ("train", "dev")
EXPECTED_DICT_SHA = "30c3f61a64ec641abbb3acdbc7a8bcaf197f0238f1bf9e76c2c7ce8e590f86a3"
EXPECTED_CORPUS_SHA = "8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231"
EXPECTED_TITLE_CSV_SHA = "7686f02d5bb2110eb4cccc7cdbd326324e4f7fa5e4dd34d7125a76d7795cf55d"
EXPECTED_MD_STREAM_SHA = "323a07b46e2377b5ec807006c2efd06f9b1ae19a65f1389d22f32b435ca0c3fb"
EXPECTED_NG3_STREAM_SHA = "1ab004bb26e9231827137020808ca008981648d62a834755af5779454d8c553d"
FROZEN_BM25 = {"n": 51, "hit@1_n": 1, "hit@5_n": 4, "hit@10_n": 4, "hit@50_n": 6, "mrr": 0.0375}
FROZEN_DENSE = {"n": 51, "hit@1_n": 5, "hit@5_n": 15, "hit@10_n": 16, "hit@50_n": 22, "mrr": 0.1726}
FROZEN_HYBRID = {"n": 51, "hit@1_n": 3, "hit@5_n": 11, "hit@10_n": 19, "hit@50_n": 25, "mrr": 0.1422}
FROZEN_NG3 = {"n": 51, "hit@1_n": 3, "hit@5_n": 6, "hit@10_n": 6, "hit@50_n": 8, "mrr": 0.075}
FROZEN_TRIGGER = frozenset({
    "KN006", "KN014", "KN018", "KN021", "KN022", "KN023", "KN027", "KN028",
    "KN029", "KN030", "KN031", "KN033", "KN034", "KN035", "KN037", "KN043",
    "KN044", "KN045", "KN047", "KN049", "KN051", "KN053",
})
ORACLE_HYBRID_MISS = frozenset({
    "KN002", "KN005", "KN006", "KN008", "KN010", "KN018", "KN020", "KN021",
    "KN022", "KN024", "KN025", "KN026", "KN027", "KN028", "KN032", "KN035",
    "KN036", "KN037", "KN040", "KN041", "KN042", "KN044", "KN047", "KN050",
    "KN051", "KN054",
})
ROOM_CAT1 = [
    "KN001", "KN006", "KN008", "KN010", "KN011",
    "KN018", "KN037", "KN045", "KN047", "KN050", "KN051",
]
QUAD23 = [
    "KN002", "KN005", "KN006", "KN008", "KN010", "KN018", "KN020", "KN021",
    "KN022", "KN024", "KN025", "KN026", "KN027", "KN028", "KN032", "KN036",
    "KN037", "KN041", "KN042", "KN044", "KN047", "KN051", "KN054",
]
TOP_K = 50

sys.path.insert(0, _DIR)
sys.path.insert(0, P5)
sys.path.insert(0, P4)
sys.path.insert(0, P3)
sys.path.insert(0, P2)
sys.path.insert(0, P9)
import run_phase5 as p5  # noqa: E402
import hybrid_fusion as hf  # noqa: E402
import dense_retrieval as dr  # noqa: E402
import ng3_matching as ng3  # noqa: E402
from match_rule import (  # noqa: E402
    add_dotted_initialism_aliases,
    load_common_english,
    match_spans,
    norm_en,
    tokenize,
    ur_token_key,
)
import cascade_b as cb  # noqa: E402

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
    h5, p5_ = hit(5)
    h10, p10 = hit(10)
    h50, p50 = hit(50)
    mrr = (sum((1.0 / r) if r <= candidate_depth else 0.0 for r in ranks) / n) if n else 0.0
    return {
        "n": n,
        "hit@1_n": h1,
        "hit@1": round(p1, 4),
        "hit@5_n": h5,
        "hit@5": round(p5_, 4),
        "hit@10_n": h10,
        "hit@10": round(p10, 4),
        "hit@50_n": h50,
        "hit@50": round(p50, 4),
        "mrr": round(mrr, 4),
    }


def metrics_match(got: dict, frozen: dict) -> bool:
    for k in ("hit@1_n", "hit@5_n", "hit@10_n", "hit@50_n"):
        if got[k] != frozen[k]:
            return False
    return abs(got["mrr"] - frozen["mrr"]) <= 1e-4


def rec_rank(rank: int) -> float:
    return (1.0 / rank) if 1 <= rank <= 50 else 0.0


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


def load_title_indexes(path: str) -> tuple[dict, dict, int]:
    idx = {}
    ur_key = {}
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
                ur_key.setdefault(ck, []).append(entry)
    for rec in idx.values():
        del rec["orig_set"]
    n_alias = add_dotted_initialism_aliases(idx)
    return idx, ur_key, n_alias


def expand_p9_tokens(qtoks: list[str], hits: list[dict], rev: dict) -> list[str]:
    out = list(qtoks)
    for h in hits:
        for ur in h["ur_titles"]:
            for tok in tokenize(ur):
                lat = p5.romanize_token(tok, rev)
                if lat:
                    out.append(lat)
    return out


def trans_hit50(a: dict[str, int], b: dict[str, int], ids: list[str]) -> dict:
    hh = hm = mh = mm = 0
    for qid in ids:
        aa, bb = int(a[qid]), int(b[qid])
        if aa and bb:
            hh += 1
        elif aa and not bb:
            hm += 1
        elif (not aa) and bb:
            mh += 1
        else:
            mm += 1
    return {"hit_hit": hh, "a_hit_b_miss": hm, "a_miss_b_hit": mh, "miss_miss": mm, "n": len(ids)}


def write_blocked(payload: dict) -> None:
    os.makedirs(ART, exist_ok=True)
    with open(os.path.join(ART, "phase10_blocked.json"), "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(json.dumps(payload, indent=2, ensure_ascii=False), flush=True)


def main() -> int:
    wall_t0 = time.perf_counter()
    print("label: ULTRA v2 PHASE10-CASCADE-B", flush=True)
    print("TEST_accessed: no", flush=True)
    branch, commit = git_identity()
    print("git", branch, commit, flush=True)
    if not os.path.isfile(PREREG):
        raise SystemExit("BLOCKED — PHASE10_PREREGISTRATION.md missing")
    prereg_sha = sha256_file(PREREG)
    os.makedirs(ART, exist_ok=True)
    with open(os.path.join(ART, "phase10_prereg_sha256.txt"), "w", encoding="ascii") as f:
        f.write(prereg_sha + "\n")
    print("prereg_sha", prereg_sha, flush=True)

    refuse_test_path(p5.CORPUS)
    refuse_test_path(p5.DICT_PATH)
    refuse_test_path(TITLE_CSV)

    dict_sha = sha256_file(p5.DICT_PATH)
    if dict_sha != EXPECTED_DICT_SHA:
        write_blocked({"decision": "BLOCKED", "reason": "dictionary SHA mismatch", "got": dict_sha})
        raise SystemExit("BLOCKED — dictionary SHA mismatch")
    corpus_sha = sha256_file(p5.CORPUS)
    if corpus_sha != EXPECTED_CORPUS_SHA:
        write_blocked({"decision": "BLOCKED", "reason": "corpus SHA mismatch", "got": corpus_sha})
        raise SystemExit("BLOCKED — corpus SHA mismatch")
    title_sha = sha256_file(TITLE_CSV)
    if title_sha != EXPECTED_TITLE_CSV_SHA:
        write_blocked({"decision": "BLOCKED", "reason": "title CSV SHA mismatch", "got": title_sha})
        raise SystemExit("BLOCKED — title CSV SHA mismatch")
    load_common_english()

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
                write_blocked({"decision": "BLOCKED", "reason": "query/gold mismatch", "id": qid})
                raise SystemExit("BLOCKED — query/gold mismatch")

    # --- BM25 ---
    if not os.path.isfile(B0_CACHE):
        raise SystemExit("BLOCKED — Method-D cache missing")
    print("loading Method-D cache...", flush=True)
    with open(B0_CACHE, "rb") as f:
        blob = pickle.load(f)
    want_meta = {
        "corpus_sha256": corpus_sha,
        "dict_sha256": dict_sha,
        "k1": p5.BM25_K1,
        "b": p5.BM25_B,
        "tokenizer": p5.TOKEN_RE.pattern,
    }
    if blob.get("meta") != want_meta:
        raise SystemExit("BLOCKED — BM25 cache meta mismatch")
    roman_bm25 = blob["roman_bm25"]
    print("reproducing Method-D Top-50...", flush=True)
    bm25_hits = {}
    bm25_rank_obs = {}
    for r in rows:
        qtoks = p5.tokenize(r["query_text"])
        hits = roman_bm25.search(qtoks, top_k=TOP_K)
        bm25_hits[r["query_id"]] = hits
        bm25_rank_obs[r["query_id"]] = p5.rank_of(hits, r["source_doc_id"])
        if bm25_rank_obs[r["query_id"]] != parse_rank(b0[r["query_id"]].get("gold_rank")):
            raise SystemExit("BLOCKED — BM25 rank mismatch %s" % r["query_id"])
    bm25_m = kn_metrics([bm25_rank_obs[q] for q in ids])
    if not metrics_match(bm25_m, FROZEN_BM25):
        raise SystemExit("BLOCKED — BM25 aggregates != frozen")
    print("GATE BM25 PASS", bm25_m, flush=True)

    # --- Dense ---
    print("loading dense matrix + encoder...", flush=True)
    with open(P3_META, encoding="utf-8") as f:
        dmeta = json.load(f)
    if dmeta.get("complete") is not True:
        raise SystemExit("BLOCKED — dense incomplete")
    if dmeta.get("corpus_sha256") != EXPECTED_CORPUS_SHA:
        raise SystemExit("BLOCKED — dense corpus SHA")
    arr = np.load(P3_NPY, mmap_mode="r")
    doc_matrix = np.array(arr, dtype=np.float32, copy=True)
    model, enc_info = dr.load_encoder()
    q_vecs = dr.encode_texts(
        model,
        [r["query_text"] for r in rows],
        kind="query",
        prefix_mode=enc_info["prefix_mode"],
        prompt_name=enc_info.get("query_prompt_name"),
        show_progress=False,
    )
    dense_hits = {}
    dense_rank_obs = {}
    for r, qv in zip(rows, q_vecs):
        res = dr.search_query_vec(doc_matrix, qv, r["source_doc_id"], k=TOP_K)
        dense_hits[r["query_id"]] = res["topk"]
        dense_rank_obs[r["query_id"]] = int(res["gold_rank"])
        if int(res["gold_rank"]) != int(dense[r["query_id"]]["dense_rank"]):
            raise SystemExit("BLOCKED — dense rank mismatch %s" % r["query_id"])
        if int(res["rank1_doc_id"]) != int(dense[r["query_id"]]["dense_rank1_doc_id"]):
            raise SystemExit("BLOCKED — dense rank1 mismatch %s" % r["query_id"])
    dense_m = kn_metrics([dense_rank_obs[q] for q in ids])
    if not metrics_match(dense_m, FROZEN_DENSE):
        raise SystemExit("BLOCKED — dense aggregates != frozen")
    print("GATE DENSE PASS", dense_m, flush=True)

    # --- Hybrid ---
    print("fusing Hybrid RRF k=60...", flush=True)
    hybrid_lists = {}
    hybrid_rank_obs = {}
    for r in rows:
        fused = hf.fuse_rrf(bm25_hits[r["query_id"]], dense_hits[r["query_id"]], k=hf.RRF_K)
        # convert to (doc_id, rrf_score) for Option B
        hybrid_lists[r["query_id"]] = [(did, sc) for did, sc, _rb, _rd in fused[:TOP_K]]
        rk, _sc = hf.gold_fused_rank(fused, r["source_doc_id"])
        hybrid_rank_obs[r["query_id"]] = rk
        if rk != parse_rank(hybrid[r["query_id"]].get("hybrid_rank")):
            raise SystemExit("BLOCKED — hybrid rank mismatch %s" % r["query_id"])
    hybrid_m = kn_metrics([hybrid_rank_obs[q] for q in ids])
    if not metrics_match(hybrid_m, FROZEN_HYBRID):
        raise SystemExit("BLOCKED — hybrid aggregates != frozen")
    print("GATE HYBRID PASS", hybrid_m, flush=True)

    # --- NG3 ---
    print("building frozen NG3 representation...", flush=True)
    import pandas as pd

    df = pd.read_csv(p5.CORPUS, encoding="utf-8-sig")
    texts = df["combined_text"].fillna("").astype(str).tolist()
    if len(texts) != 111860:
        raise SystemExit("BLOCKED — corpus size")
    fwd = p5.load_roman_dict()
    rev = p5.load_reverse_roman(fwd)
    ng3_docs: list[list[str]] = []
    md_hasher = hashlib.sha256()
    ng3_hasher = hashlib.sha256()
    for i, text in enumerate(texts):
        utoks = p5.tokenize(text)
        md = [t for t in (p5.romanize_token(tok, rev) for tok in utoks) if t]
        feats = ng3.expand_tokens(md)
        ng3_docs.append(feats)
        md_hasher.update((" ".join(md) + "\n").encode("utf-8"))
        ng3_hasher.update((" ".join(feats) + "\n").encode("utf-8"))
        if (i + 1) % 20000 == 0:
            print("  tokenize %s/%s" % (i + 1, len(texts)), flush=True)
    if md_hasher.hexdigest() != EXPECTED_MD_STREAM_SHA or ng3_hasher.hexdigest() != EXPECTED_NG3_STREAM_SHA:
        raise SystemExit("BLOCKED — NG3 stream SHA mismatch")
    ng3_bm25 = p5.BM25(ng3_docs, k1=1.5, b=0.75)
    ng3_hits = {}
    ng3_rank_obs = {}
    for r in rows:
        q3 = ng3.expand_tokens(p5.tokenize(r["query_text"]))
        nhits = ng3_bm25.search(q3, top_k=TOP_K)
        ng3_hits[r["query_id"]] = nhits
        nr = p5.rank_of(nhits, r["source_doc_id"])
        ng3_rank_obs[r["query_id"]] = nr
        if nr != parse_rank(ng3_tab[r["query_id"]].get("ng3_rank")):
            raise SystemExit("BLOCKED — NG3 rank mismatch %s" % r["query_id"])
    ng3_m = kn_metrics([ng3_rank_obs[q] for q in ids])
    if not metrics_match(ng3_m, FROZEN_NG3):
        raise SystemExit("BLOCKED — NG3 aggregates != frozen")
    print("GATE NG3 PASS", ng3_m, flush=True)

    # --- Phase 9 title index + trigger + P9 lists ---
    print("loading Phase-9 title indexes...", flush=True)
    en_index, ur_index, n_alias = load_title_indexes(TITLE_CSV)
    print("en_keys=%s aliases=%s" % (len(en_index), n_alias), flush=True)

    triggered = set()
    p9_hits = {}
    p9_n_en = {}
    p9_spans = {}
    for r in rows:
        qid = r["query_id"]
        qtoks = tokenize(r["query_text"])
        hits = match_spans(qtoks, en_index, ur_index)
        p9_n_en[qid] = len(hits)
        p9_spans[qid] = " | ".join(h["span"] for h in hits)
        if hits:
            triggered.add(qid)
            exp = expand_p9_tokens(qtoks, hits, rev)
            p9_hits[qid] = roman_bm25.search(exp, top_k=TOP_K)
        else:
            p9_hits[qid] = []
    if triggered != FROZEN_TRIGGER:
        write_blocked({
            "decision": "BLOCKED",
            "reason": "trigger set mismatch",
            "expected": sorted(FROZEN_TRIGGER),
            "observed": sorted(triggered),
            "extra": sorted(triggered - FROZEN_TRIGGER),
            "missing": sorted(FROZEN_TRIGGER - triggered),
        })
        raise SystemExit("BLOCKED — trigger set != frozen 22 IDs")
    print("GATE TRIGGER PASS n=%s" % len(triggered), flush=True)

    # Optional: P9 Hit@50 gate vs scored CSV if present
    if os.path.isfile(P9_SCORED):
        p9_tab = load_csv(P9_SCORED)
        for r in rows:
            qid = r["query_id"]
            pr = p5.rank_of(p9_hits[qid], r["source_doc_id"]) if p9_hits[qid] else 999
            # only compare when triggered (non-triggered P9 list empty → not comparable to scored P9)
            if qid in triggered:
                exp = parse_rank(p9_tab[qid].get("p9_rank"))
                if pr != exp:
                    write_blocked({
                        "decision": "BLOCKED",
                        "reason": "P9 list rank != phase9_scored_results",
                        "query_id": qid,
                        "expected": exp,
                        "observed": pr,
                    })
                    raise SystemExit("BLOCKED — P9 standalone rank mismatch %s" % qid)
        print("GATE P9-LIST vs scored CSV PASS", flush=True)

    # --- Option B ---
    print("applying Option B cascade...", flush=True)
    p10_ranks = []
    hybrid_ranks = []
    per_rows = []
    for r in rows:
        qid = r["query_id"]
        trig = qid in triggered
        ranked = cb.option_b_fuse(
            hybrid_lists[qid],
            p9_hits[qid] if trig else None,
            ng3_hits[qid] if trig else None,
            triggered=trig,
        )
        # repeat identity check
        ranked2 = cb.option_b_fuse(
            hybrid_lists[qid],
            p9_hits[qid] if trig else None,
            ng3_hits[qid] if trig else None,
            triggered=trig,
        )
        if [d for d, _ in ranked] != [d for d, _ in ranked2]:
            raise SystemExit("BLOCKED — Option B not identical on repeat %s" % qid)
        pr = cb.gold_rank(ranked, r["source_doc_id"])
        hr = hybrid_rank_obs[qid]
        # non-triggered: output Top-50 doc sequence must equal Hybrid Top-50
        # (gold ranks may be >50 for Hybrid misses; compare list identity, not rank ints)
        if not trig:
            if [int(d) for d, _ in ranked] != [int(d) for d, _ in hybrid_lists[qid][:TOP_K]]:
                raise SystemExit("BLOCKED — non-trigger changed Hybrid Top-50 list %s" % qid)
        p10_ranks.append(pr)
        hybrid_ranks.append(hr)
        # cascade fill diagnostics
        h40 = {int(d) for d, _ in hybrid_lists[qid][:40]}
        fill_ids = [int(d) for d, _ in ranked[40:]]
        n_cascade_new = sum(1 for d in fill_ids if d not in {int(x) for x, _ in hybrid_lists[qid][:50]})
        per_rows.append({
            "query_id": qid,
            "split": r["split"],
            "script": "ROMAN",
            "source_doc_id": r["source_doc_id"],
            "query_text": r["query_text"],
            "triggered": int(trig),
            "n_en_hits": p9_n_en[qid],
            "spans": p9_spans[qid],
            "oracle_hybrid_miss": int(qid in ORACLE_HYBRID_MISS),
            "bm25_rank": bm25_rank_obs[qid] if bm25_rank_obs[qid] < 999 else "",
            "dense_rank": dense_rank_obs[qid] if dense_rank_obs[qid] < 999 else "",
            "ng3_rank": ng3_rank_obs[qid] if ng3_rank_obs[qid] < 999 else "",
            "hybrid_rank": hr if hr < 999 else "",
            "p10_rank": pr if pr < 999 else "",
            "bm25_hit@50": int(bm25_rank_obs[qid] <= 50),
            "dense_hit@50": int(dense_rank_obs[qid] <= 50),
            "ng3_hit@50": int(ng3_rank_obs[qid] <= 50),
            "hybrid_hit@1": int(hr <= 1),
            "hybrid_hit@5": int(hr <= 5),
            "hybrid_hit@10": int(hr <= 10),
            "hybrid_hit@50": int(hr <= 50),
            "p10_hit@1": int(pr <= 1),
            "p10_hit@5": int(pr <= 5),
            "p10_hit@10": int(pr <= 10),
            "p10_hit@50": int(pr <= 50),
            "hybrid_rr": round(rec_rank(hr), 6),
            "p10_rr": round(rec_rank(pr), 6),
            "n_cascade_fill_outside_hybrid50": n_cascade_new,
            "quad23": int(qid in QUAD23),
            "room_cat1": int(qid in ROOM_CAT1),
            "p10_recovered_hybrid_miss50": int(hr > 50 and pr <= 50),
            "p10_regressed_hybrid_hit50": int(hr <= 50 and pr > 50),
            "p10_regressed_hybrid_hit5": int(hr <= 5 and pr > 5),
        })

    p10_m = kn_metrics(p10_ranks)
    # decision
    p10_h50 = {row["query_id"]: int(row["p10_hit@50"]) for row in per_rows}
    h_h50 = {row["query_id"]: int(row["hybrid_hit@50"]) for row in per_rows}
    gain = [row["query_id"] for row in per_rows if row["p10_recovered_hybrid_miss50"] == 1]
    lost50 = [row["query_id"] for row in per_rows if row["p10_regressed_hybrid_hit50"] == 1]
    lost5 = [row["query_id"] for row in per_rows if row["p10_regressed_hybrid_hit5"] == 1]
    room_p10 = [q for q in ROOM_CAT1 if p10_h50[q] == 1]
    room_h = [q for q in ROOM_CAT1 if h_h50[q] == 1]
    quad_p10 = [q for q in QUAD23 if p10_h50[q] == 1]

    if len(gain) >= 3 and len(lost5) == 0 and p10_m["hit@5_n"] >= hybrid_m["hit@5_n"]:
        decision = "PHASE10 SUPPORTED"
    elif len(gain) >= 1 or p10_m["hit@50_n"] > hybrid_m["hit@50_n"]:
        decision = "PHASE10 PARTIALLY SUPPORTED"
    elif len(lost50) or len(lost5) or p10_m["hit@50_n"] < hybrid_m["hit@50_n"]:
        decision = "PHASE10 UNSUPPORTED"
    else:
        decision = "PHASE10 UNSUPPORTED"

    csv_path = os.path.join(_DIR, "PHASE10_PER_QUERY.csv")
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(per_rows[0].keys()))
        w.writeheader()
        w.writerows(per_rows)
    scored = os.path.join(ART, "phase10_scored_results.csv")
    with open(scored, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(per_rows[0].keys()))
        w.writeheader()
        w.writerows(per_rows)
    scored_sha = sha256_file(scored)
    with open(os.path.join(ART, "phase10_scored_results.sha256"), "w", encoding="ascii") as f:
        f.write(scored_sha + "\n")

    wall = round(time.perf_counter() - wall_t0, 3)
    config = {
        "experiment_id": "PHASE10-CASCADE-B",
        "timestamp_utc": utc_now(),
        "branch": branch,
        "commit": commit,
        "preregistration_sha256": prereg_sha,
        "hybrid_keep": cb.HYBRID_KEEP,
        "cascade_slots": cb.CASCADE_SLOTS,
        "rrf_k": cb.RRF_K,
        "fusion": "option_b_hybrid_first",
        "trigger": "phase9_v2_title_hit_ge1",
        "test_accessed": False,
        "gates": {
            "bm25": "PASS",
            "dense": "PASS",
            "hybrid": "PASS",
            "ng3": "PASS",
            "trigger_set": "PASS",
            "option_b_repeat": "PASS",
        },
    }
    with open(os.path.join(ART, "phase10_config.json"), "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
        f.write("\n")

    summary = {
        "experiment_id": "PHASE10-CASCADE-B",
        "timestamp_utc": utc_now(),
        "decision": decision,
        "test_accessed": False,
        "preregistration_sha256": prereg_sha,
        "scored_csv_sha256": scored_sha,
        "gates": config["gates"],
        "frozen_hybrid": FROZEN_HYBRID,
        "reproduced_hybrid": hybrid_m,
        "phase10_cascade_b": p10_m,
        "n_triggered": len(triggered),
        "triggered_ids": sorted(triggered),
        "oracle_diagnostic": {
            "label": "NON_DEPLOYABLE_CEILING_ONLY",
            "n": len(ORACLE_HYBRID_MISS),
            "ids": sorted(ORACLE_HYBRID_MISS),
            "trigger_intersect_n": len(triggered & ORACLE_HYBRID_MISS),
            "trigger_intersect_ids": sorted(triggered & ORACLE_HYBRID_MISS),
            "note": "Not Phase 10's scored result. Deployable metrics are phase10_cascade_b vs hybrid.",
        },
        "overlap_hit50": {
            "p10_vs_hybrid": trans_hit50(p10_h50, h_h50, ids),
        },
        "vs_hybrid": {
            "recovered_hit50": gain,
            "regressed_hit50": lost50,
            "regressed_hit5": lost5,
        },
        "room_cat1": {
            "hybrid_hit@50": len(room_h),
            "hybrid_ids": room_h,
            "p10_hit@50": len(room_p10),
            "p10_ids": room_p10,
        },
        "quad23": {
            "p10_hit@50_n": len(quad_p10),
            "p10_ids": quad_p10,
        },
        "runtime_wall_seconds": wall,
        "safety": {
            "test_accessed": False,
            "query_injection_into_hybrid_bm25": False,
            "option_a_full_rrf": False,
            "oracle_used_as_trigger": False,
            "phase2_9_modified": False,
        },
    }
    with open(os.path.join(ART, "phase10_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print("P10", p10_m, flush=True)
    print("HYBRID", hybrid_m, flush=True)
    print("recovered_hybrid_miss50", gain, flush=True)
    print("regressed_hit50", lost50, "regressed_hit5", lost5, flush=True)
    print("ROOM P10", len(room_p10), room_p10, flush=True)
    print("decision", decision, flush=True)
    print("scored_sha", scored_sha, flush=True)
    print("EVALUATION COMPLETE", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
