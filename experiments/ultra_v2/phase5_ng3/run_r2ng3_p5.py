# -*- coding: utf-8 -*-
"""Phase 5: reproduce frozen R2-NG3 once; gate ranks; then dual-miss comparison.

Read-only: phase2 ng3_matching.py, R2_NG3_PER_QUERY.csv, r2_b0, Phase 3/4 CSVs,
experiments/phase5_roman_urdu/run_phase5.py.
Does not overwrite Phase-2 R2-NG3 artifacts. Does not open benchmark/test/.
Does not change n, try raw-Urdu grams, TF-IDF, fusion, or reranking.
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
from collections import Counter
from datetime import datetime, timezone

os.environ.setdefault("MKL_THREADING_LAYER", "SEQUENTIAL")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.pop("KMP_DUPLICATE_LIB_OK", None)

_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(_DIR, "..", "..", ".."))
P5 = os.path.join(ROOT, "experiments", "phase5_roman_urdu")
P2 = os.path.join(ROOT, "experiments", "ultra_v2", "phase2_roman")
P3 = os.path.join(ROOT, "experiments", "ultra_v2", "phase3_dense")
P4 = os.path.join(ROOT, "experiments", "ultra_v2", "phase4_hybrid")
BENCH = os.path.join(ROOT, "experiments", "ultra_v2", "benchmark")
TEST_DIR = os.path.abspath(os.path.join(BENCH, "test"))
ART = os.path.join(_DIR, "artifacts")
PREREG = os.path.join(_DIR, "R2NG3_PREREGISTRATION.md")
B0_CACHE = os.path.join(P2, "artifacts", "_index_cache.pkl")
B0_PER = os.path.join(P2, "artifacts", "r2_b0_per_query.csv")
NG3_FROZEN = os.path.join(P2, "R2_NG3_PER_QUERY.csv")
NG3_HELPER = os.path.join(P2, "ng3_matching.py")
DENSE_PER = os.path.join(P3, "DENSE_PER_QUERY.csv")
HYBRID_PER = os.path.join(P4, "HYBRID_PER_QUERY.csv")
ALLOWED_SPLITS = ("train", "dev")
EXPECTED_DICT_SHA = "30c3f61a64ec641abbb3acdbc7a8bcaf197f0238f1bf9e76c2c7ce8e590f86a3"
EXPECTED_CORPUS_SHA = "8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231"
EXPECTED_MD_STREAM_SHA = "323a07b46e2377b5ec807006c2efd06f9b1ae19a65f1389d22f32b435ca0c3fb"
EXPECTED_NG3_STREAM_SHA = "1ab004bb26e9231827137020808ca008981648d62a834755af5779454d8c553d"
FROZEN_BM25 = {"n": 51, "hit@1_n": 1, "hit@5_n": 4, "hit@10_n": 4, "hit@50_n": 6, "mrr": 0.0375}
FROZEN_DENSE = {"n": 51, "hit@1_n": 5, "hit@5_n": 15, "hit@10_n": 16, "hit@50_n": 22, "mrr": 0.1726}
FROZEN_HYBRID = {"n": 51, "hit@1_n": 3, "hit@5_n": 11, "hit@10_n": 19, "hit@50_n": 25, "mrr": 0.1422}
ROOM_CAT1 = [
    "KN001", "KN006", "KN008", "KN010", "KN011",
    "KN018", "KN037", "KN045", "KN047", "KN050", "KN051",
]
VOCAB_CONTROLS = ["KN017", "KN020", "KN041"]
TOP_K = 50

sys.path.insert(0, _DIR)
sys.path.insert(0, P5)
sys.path.insert(0, P2)
import run_phase5 as p5  # noqa: E402
import ng3_matching as ng3  # noqa: E402

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
    path = os.path.join(ART, "r2ng3_blocked.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(json.dumps(payload, indent=2, ensure_ascii=False), flush=True)


def trans_hit50(a_hits: dict[str, int], b_hits: dict[str, int], ids: list[str]) -> dict:
    hh = hm = mh = mm = 0
    for qid in ids:
        a = int(a_hits[qid])
        b = int(b_hits[qid])
        if a and b:
            hh += 1
        elif a and not b:
            hm += 1
        elif (not a) and b:
            mh += 1
        else:
            mm += 1
    return {
        "hit_hit": hh,
        "a_hit_b_miss": hm,
        "a_miss_b_hit": mh,
        "miss_miss": mm,
        "n": len(ids),
    }


def main() -> int:
    wall_t0 = time.perf_counter()
    print("label: ULTRA v2 R2-NG3-P5-REPRO", flush=True)
    print("TEST_accessed: no", flush=True)
    branch, commit = git_identity()
    print("git", branch, commit, flush=True)
    if not os.path.isfile(PREREG):
        raise SystemExit("BLOCKED — R2NG3_PREREGISTRATION.md missing")
    if not os.path.isfile(NG3_HELPER):
        raise SystemExit("BLOCKED — frozen ng3_matching.py missing")
    helper_txt = open(NG3_HELPER, encoding="utf-8").read()
    if "hunterian" in helper_txt.lower():
        raise SystemExit("BLOCKED — hunterian mentioned in ng3_matching.py")
    assert ng3.N == 3
    assert ng3.char3_grams("world") == ["wor", "orl", "rld"]
    assert ng3.char3_grams("orld") == ["orl", "rld"]
    assert ng3.char3_grams("ke") == ["ke"]
    assert p5.BM25_K1 == 1.5 and p5.BM25_B == 0.75
    os.makedirs(ART, exist_ok=True)
    refuse_test_path(p5.CORPUS)
    refuse_test_path(p5.DICT_PATH)

    dict_sha = sha256_file(p5.DICT_PATH)
    if dict_sha != EXPECTED_DICT_SHA:
        write_blocked({"decision": "BLOCKED", "reason": "dictionary SHA mismatch", "got": dict_sha})
        raise SystemExit("BLOCKED — dictionary SHA-256 is not the frozen hash")
    corpus_sha = sha256_file(p5.CORPUS)
    if corpus_sha != EXPECTED_CORPUS_SHA:
        write_blocked({"decision": "BLOCKED", "reason": "corpus SHA mismatch", "got": corpus_sha})
        raise SystemExit("BLOCKED — corpus SHA-256 mismatch")

    rows = load_roman_kn()
    qids = [r["query_id"] for r in rows]
    frozen_ng3 = load_csv(NG3_FROZEN)
    b0 = load_csv(B0_PER)
    dense = load_csv(DENSE_PER)
    hybrid = load_csv(HYBRID_PER)
    if len(frozen_ng3) != 51 or len(b0) != 51 or len(dense) != 51 or len(hybrid) != 51:
        write_blocked({
            "decision": "BLOCKED",
            "reason": "frozen per-query n != 51",
            "n": {
                "ng3": len(frozen_ng3),
                "b0": len(b0),
                "dense": len(dense),
                "hybrid": len(hybrid),
            },
        })
        raise SystemExit("BLOCKED — frozen per-query file n != 51")

    id_mismatches = []
    for r in rows:
        qid = r["query_id"]
        if qid not in frozen_ng3 or qid not in b0 or qid not in dense or qid not in hybrid:
            id_mismatches.append({"query_id": qid, "missing_from": "a frozen CSV"})
            continue
        gold = r["source_doc_id"]
        ng_gold = int(frozen_ng3[qid]["gold_doc_id"])
        b0_gold = int(b0[qid]["source_doc_id"])
        d_gold = int(dense[qid]["source_doc_id"])
        h_gold = int(hybrid[qid]["source_doc_id"])
        if not (gold == ng_gold == b0_gold == d_gold == h_gold):
            id_mismatches.append({
                "query_id": qid,
                "benchmark": gold,
                "ng3": ng_gold,
                "b0": b0_gold,
                "dense": d_gold,
                "hybrid": h_gold,
            })
    if id_mismatches:
        write_blocked({
            "decision": "BLOCKED",
            "reason": "query/gold identity mismatch vs Phase 2/3/4",
            "mismatches": id_mismatches,
        })
        raise SystemExit("BLOCKED — query list / gold IDs do not match Phase 3/4")

    dual_from_components = []
    dual_from_hybrid = []
    for r in rows:
        qid = r["query_id"]
        b50 = int(parse_rank(b0[qid].get("gold_rank")) <= 50)
        d50 = int(int(dense[qid]["dense_rank"]) <= 50)
        if b50 == 0 and d50 == 0:
            dual_from_components.append(qid)
        if int(hybrid[qid].get("E_both_miss") or 0) == 1:
            dual_from_hybrid.append(qid)
    if dual_from_components != dual_from_hybrid or len(dual_from_components) != 25:
        write_blocked({
            "decision": "BLOCKED",
            "reason": "dual-miss set mismatch",
            "from_bm25_and_dense": dual_from_components,
            "from_hybrid_E_both_miss": dual_from_hybrid,
        })
        raise SystemExit("BLOCKED — dual-miss set is not the frozen 25")

    if not os.path.isfile(B0_CACHE):
        write_blocked({"decision": "BLOCKED", "reason": "Method-D cache missing", "path": B0_CACHE})
        raise SystemExit("BLOCKED — Method-D cache missing")
    print("loading Method-D cache (read-only)...", flush=True)
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
        write_blocked({"decision": "BLOCKED", "reason": "BM25 cache meta mismatch", "got": blob.get("meta")})
        raise SystemExit("BLOCKED — BM25 cache meta mismatch")
    control_bm25 = blob["roman_bm25"]
    print("BM25 cache hit", flush=True)

    import pandas as pd

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
    n_docs = len(texts)
    if n_docs != 111860:
        write_blocked({"decision": "BLOCKED", "reason": "n_docs != 111860", "got": n_docs})
        raise SystemExit("BLOCKED — corpus size %s" % n_docs)

    fwd = p5.load_roman_dict()
    rev = p5.load_reverse_roman(fwd)
    gold_needed = {r["source_doc_id"] for r in rows}
    control_gold: dict[int, list[str]] = {}
    ng3_docs: list[list[str]] = []
    stats = Counter()
    md_hasher = hashlib.sha256()
    ng3_hasher = hashlib.sha256()
    print("Method D tokenize + NG3 expand (n=3, token-internal)...", flush=True)
    t_tok = time.perf_counter()
    for i, text in enumerate(texts):
        utoks = p5.tokenize(text)
        md = [t for t in (p5.romanize_token(tok, rev) for tok in utoks) if t]
        feats = ng3.expand_tokens(md)
        ng3_docs.append(feats)
        stats["md_tokens"] += len(md)
        stats["ng3_features"] += len(feats)
        stats["short_passthrough"] += sum(1 for t in md if 0 < len(t) < 3)
        md_hasher.update((" ".join(md) + "\n").encode("utf-8"))
        ng3_hasher.update((" ".join(feats) + "\n").encode("utf-8"))
        if i in gold_needed:
            control_gold[i] = md
        if (i + 1) % 20000 == 0:
            print("  tokenize %s/%s" % (i + 1, n_docs), flush=True)
    tokenize_sec = time.perf_counter() - t_tok
    md_sha = md_hasher.hexdigest()
    ng3_sha = ng3_hasher.hexdigest()
    print("tokenize+expand %.1fs features=%s" % (tokenize_sec, stats["ng3_features"]), flush=True)
    if md_sha != EXPECTED_MD_STREAM_SHA or ng3_sha != EXPECTED_NG3_STREAM_SHA:
        write_blocked({
            "decision": "BLOCKED",
            "reason": "NG3 feature/token stream SHA mismatch vs frozen Phase-2 representation",
            "expected_md": EXPECTED_MD_STREAM_SHA,
            "observed_md": md_sha,
            "expected_ng3": EXPECTED_NG3_STREAM_SHA,
            "observed_ng3": ng3_sha,
        })
        raise SystemExit("BLOCKED — NG3 representation stream does not match Phase 2")

    print("build NG3 BM25 k1=1.5 b=0.75...", flush=True)
    t_b = time.perf_counter()
    ng3_bm25 = p5.BM25(ng3_docs, k1=1.5, b=0.75)
    build_sec = time.perf_counter() - t_b
    print("ng3 BM25 %.1fs terms=%s" % (build_sec, len(ng3_bm25.idf)), flush=True)

    print("search + rank gate vs R2_NG3_PER_QUERY.csv...", flush=True)
    t_s = time.perf_counter()
    bm25_mismatches = []
    ng3_mismatches = []
    bm25_hits: dict[str, list] = {}
    ng3_hits: dict[str, list] = {}
    bm25_rank_obs: dict[str, int] = {}
    ng3_rank_obs: dict[str, int] = {}
    ng3_rank_repeat: dict[str, int] = {}
    per_rows = []
    for r in rows:
        qid = r["query_id"]
        qtoks = p5.tokenize(r["query_text"])
        q3 = ng3.expand_tokens(qtoks)
        chits = control_bm25.search(qtoks, top_k=TOP_K)
        nhits = ng3_bm25.search(q3, top_k=TOP_K)
        nhits2 = ng3_bm25.search(q3, top_k=TOP_K)
        cr = p5.rank_of(chits, r["source_doc_id"])
        nr = p5.rank_of(nhits, r["source_doc_id"])
        nr2 = p5.rank_of(nhits2, r["source_doc_id"])
        bm25_hits[qid] = chits
        ng3_hits[qid] = nhits
        bm25_rank_obs[qid] = cr
        ng3_rank_obs[qid] = nr
        ng3_rank_repeat[qid] = nr2
        exp_b = parse_rank(b0[qid].get("gold_rank"))
        if cr != exp_b:
            bm25_mismatches.append({
                "query_id": qid,
                "expected_gold_rank": exp_b,
                "observed_gold_rank": cr,
            })
        fr = frozen_ng3[qid]
        exp_n = parse_rank(fr.get("ng3_rank"))
        exp_hits = {
            "ng3_hit1": int(fr["ng3_hit1"]),
            "ng3_hit5": int(fr["ng3_hit5"]),
            "ng3_hit10": int(fr["ng3_hit10"]),
            "ng3_hit50": int(fr["ng3_hit50"]),
        }
        obs_hits = {
            "ng3_hit1": int(nr <= 1),
            "ng3_hit5": int(nr <= 5),
            "ng3_hit10": int(nr <= 10),
            "ng3_hit50": int(nr <= 50),
        }
        if nr != exp_n or obs_hits != exp_hits:
            ng3_mismatches.append({
                "query_id": qid,
                "expected_ng3_rank": exp_n,
                "observed_ng3_rank": nr,
                "expected_hits": exp_hits,
                "observed_hits": obs_hits,
                "observed_top5": [int(d) for d, _s in nhits[:5]],
            })
        gold_md = control_gold[r["source_doc_id"]]
        shared = sorted(ng3.feature_set(qtoks) & ng3.feature_set(gold_md))
        bset = {int(d) for d, _s in chits}
        nset = {int(d) for d, _s in nhits}
        drk = int(dense[qid]["dense_rank"])
        hrk = parse_rank(hybrid[qid].get("hybrid_rank"))
        b50 = int(cr <= 50)
        d50 = int(drk <= 50)
        h50 = int(hrk <= 50)
        n50 = int(nr <= 50)
        per_rows.append({
            "query_id": qid,
            "split": r["split"],
            "script": "ROMAN",
            "source_doc_id": r["source_doc_id"],
            "query_text": r["query_text"],
            "bm25_rank": cr if cr < 999 else "",
            "dense_rank": drk,
            "hybrid_rank": hrk if hrk < 999 else "",
            "ng3_rank": nr if nr < 999 else "",
            "bm25_hit@1": int(cr <= 1),
            "bm25_hit@5": int(cr <= 5),
            "bm25_hit@10": int(cr <= 10),
            "bm25_hit@50": b50,
            "dense_hit@1": int(drk <= 1),
            "dense_hit@5": int(drk <= 5),
            "dense_hit@10": int(drk <= 10),
            "dense_hit@50": d50,
            "hybrid_hit@1": int(hybrid[qid]["hybrid_hit@1"]),
            "hybrid_hit@5": int(hybrid[qid]["hybrid_hit@5"]),
            "hybrid_hit@10": int(hybrid[qid]["hybrid_hit@10"]),
            "hybrid_hit@50": h50,
            "ng3_hit@1": int(nr <= 1),
            "ng3_hit@5": int(nr <= 5),
            "ng3_hit@10": int(nr <= 10),
            "ng3_hit@50": n50,
            "bm25_rr": round(rec_rank(cr), 6),
            "dense_rr": round(rec_rank(drk), 6),
            "hybrid_rr": round(rec_rank(hrk), 6),
            "ng3_rr": round(rec_rank(nr), 6),
            "dual_miss_bm25_dense": int(qid in dual_from_components),
            "ng3_recovered_dual_miss": int(qid in dual_from_components and n50 == 1),
            "ng3_only_vs_bm25_dense": int(n50 == 1 and b50 == 0 and d50 == 0),
            "n_bm25_hits": len(chits),
            "n_ng3_hits": len(nhits),
            "n_bm25_ng3_union": len(bset | nset),
            "n_bm25_ng3_overlap": len(bset & nset),
            "ng3_q_features": len(q3),
            "ng3_overlap_gold": len(shared),
            "shared_trigrams_sample": " ".join(shared[:20]),
            "room_cat1": int(qid in ROOM_CAT1),
            "vocab_control": int(qid in VOCAB_CONTROLS),
        })
    search_sec = time.perf_counter() - t_s

    if ng3_rank_obs != ng3_rank_repeat:
        write_blocked({"decision": "BLOCKED", "reason": "NG3 search not identical on second pass"})
        raise SystemExit("BLOCKED — NG3 ranks not identical on second pass")
    if bm25_mismatches:
        write_blocked({
            "decision": "BLOCKED",
            "reason": "Method-D gold ranks do not match r2_b0_per_query.csv",
            "mismatches": bm25_mismatches,
        })
        raise SystemExit("BLOCKED — BM25 gold ranks do not match r2_b0_per_query.csv")
    if ng3_mismatches:
        write_blocked({
            "decision": "BLOCKED",
            "reason": "NG3 gold ranks/hits do not match R2_NG3_PER_QUERY.csv",
            "mismatches": ng3_mismatches,
        })
        raise SystemExit("BLOCKED — NG3 ranks do not match frozen R2_NG3_PER_QUERY.csv")

    bm25_m = kn_metrics([bm25_rank_obs[q] for q in qids])
    ng3_m = kn_metrics([ng3_rank_obs[q] for q in qids])
    dense_m = kn_metrics([int(dense[q]["dense_rank"]) for q in qids])
    hybrid_m = kn_metrics([parse_rank(hybrid[q].get("hybrid_rank")) for q in qids])
    if (
        bm25_m["hit@1_n"] != FROZEN_BM25["hit@1_n"]
        or bm25_m["hit@5_n"] != FROZEN_BM25["hit@5_n"]
        or bm25_m["hit@50_n"] != FROZEN_BM25["hit@50_n"]
        or abs(bm25_m["mrr"] - FROZEN_BM25["mrr"]) > 1e-4
    ):
        write_blocked({"decision": "BLOCKED", "reason": "reproduced BM25 aggregates != frozen", "got": bm25_m})
        raise SystemExit("BLOCKED — reproduced BM25 aggregates != frozen cells")
    if (
        dense_m["hit@50_n"] != FROZEN_DENSE["hit@50_n"]
        or dense_m["hit@5_n"] != FROZEN_DENSE["hit@5_n"]
        or abs(dense_m["mrr"] - FROZEN_DENSE["mrr"]) > 1e-4
    ):
        write_blocked({"decision": "BLOCKED", "reason": "dense frozen CSV aggregates != official cells", "got": dense_m})
        raise SystemExit("BLOCKED — dense frozen CSV does not match official Phase-3 cells")
    if hybrid_m["hit@50_n"] != FROZEN_HYBRID["hit@50_n"]:
        write_blocked({"decision": "BLOCKED", "reason": "hybrid frozen CSV Hit@50 != official", "got": hybrid_m})
        raise SystemExit("BLOCKED — hybrid frozen CSV does not match official Phase-4 cells")
    print("GATE BM25 PASS", bm25_m, flush=True)
    print("GATE NG3 vs R2_NG3_PER_QUERY.csv PASS", ng3_m, flush=True)
    print("GATE query/gold vs Phase 3/4 PASS", flush=True)

    bm25_h50 = {q: int(bm25_rank_obs[q] <= 50) for q in qids}
    dense_h50 = {q: int(int(dense[q]["dense_rank"]) <= 50) for q in qids}
    hybrid_h50 = {q: int(parse_rank(hybrid[q].get("hybrid_rank")) <= 50) for q in qids}
    ng3_h50 = {q: int(ng3_rank_obs[q] <= 50) for q in qids}

    dual_recovered = [q for q in dual_from_components if ng3_h50[q] == 1]
    dual_remain = [q for q in dual_from_components if ng3_h50[q] == 0]
    ng3_only = [q for q in qids if ng3_h50[q] == 1 and bm25_h50[q] == 0 and dense_h50[q] == 0]
    room_ng3 = [q for q in ROOM_CAT1 if ng3_h50[q] == 1]
    room_dense = [q for q in ROOM_CAT1 if dense_h50[q] == 1]
    room_bm25 = [q for q in ROOM_CAT1 if bm25_h50[q] == 1]
    room_hybrid = [q for q in ROOM_CAT1 if hybrid_h50[q] == 1]
    ng3_lost_bm25 = [q for q in qids if bm25_h50[q] == 1 and ng3_h50[q] == 0]
    ng3_gain_bm25 = [q for q in qids if bm25_h50[q] == 0 and ng3_h50[q] == 1]

    overlap_sizes = [int(p["n_bm25_ng3_overlap"]) for p in per_rows]
    union_sizes = [int(p["n_bm25_ng3_union"]) for p in per_rows]

    csv_path = os.path.join(_DIR, "R2NG3_PER_QUERY.csv")
    fields = list(per_rows[0].keys())
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(per_rows)

    packages = {}
    try:
        import numpy as np

        packages["numpy"] = np.__version__
    except Exception as exc:
        packages["numpy_error"] = str(exc)

    wall = round(time.perf_counter() - wall_t0, 3)
    runtime = {
        "tokenize_expand_seconds": round(tokenize_sec, 3),
        "ng3_bm25_build_seconds": round(build_sec, 3),
        "search_seconds": round(search_sec, 3),
        "wall_seconds": wall,
        "device": "cpu",
        "cuda": False,
        "document_embeddings_regenerated": False,
        "hardware": {
            "platform": platform.platform(),
            "processor": platform.processor(),
            "cpu_count": os.cpu_count(),
            "python": sys.version.split()[0],
            "packages": packages,
        },
    }

    config = {
        "experiment_id": "R2-NG3-P5-REPRO",
        "timestamp_utc": utc_now(),
        "branch": branch,
        "commit": commit,
        "test_accessed": False,
        "preregistration_sha256": sha256_file(PREREG),
        "run_py_sha256": sha256_file(os.path.join(_DIR, "run_r2ng3_p5.py")),
        "ng3_matching_py_sha256": sha256_file(NG3_HELPER),
        "frozen_r2_ng3_per_query_sha256": sha256_file(NG3_FROZEN),
        "r2_b0_per_query_sha256": sha256_file(B0_PER),
        "dense_per_query_sha256": sha256_file(DENSE_PER),
        "hybrid_per_query_sha256": sha256_file(HYBRID_PER),
        "n_gram": 3,
        "token_boundary_policy": "A_within_existing_tokens",
        "document_representation": "frozen Method D romanize_token then char-3-grams",
        "query_representation": "frozen tokenize then char-3-grams; no dictionary",
        "bm25_k1": 1.5,
        "bm25_b": 0.75,
        "candidate_depth": 50,
        "r2_1_hunterian_used": False,
        "raw_urdu_ngrams": False,
        "tfidf": False,
        "parameter_tuning": False,
        "corpus_sha256": corpus_sha,
        "dict_sha256": dict_sha,
        "method_d_token_stream_sha256": md_sha,
        "ng3_feature_stream_sha256": ng3_sha,
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "gates": {
            "corpus_sha": "PASS",
            "query_gold_vs_phase3_4": "PASS",
            "dual_miss_n25": "PASS",
            "bm25_vs_r2_b0": "PASS",
            "ng3_vs_R2_NG3_PER_QUERY": "PASS",
            "feature_stream_sha": "PASS",
        },
    }
    with open(os.path.join(ART, "r2ng3_config.json"), "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
        f.write("\n")

    rep = {
        "n_docs": n_docs,
        "method_d_tokens": stats["md_tokens"],
        "ng3_features": stats["ng3_features"],
        "short_passthrough_tokens": stats["short_passthrough"],
        "ng3_vocabulary_terms": len(ng3_bm25.idf),
        "method_d_token_stream_sha256": md_sha,
        "ng3_feature_stream_sha256": ng3_sha,
        "bm25_ng3_candidate_overlap_mean": float(sum(overlap_sizes) / len(overlap_sizes)),
        "bm25_ng3_candidate_overlap_min": int(min(overlap_sizes)),
        "bm25_ng3_candidate_overlap_max": int(max(overlap_sizes)),
        "bm25_ng3_union_mean": float(sum(union_sizes) / len(union_sizes)),
        "n_gram": 3,
        "hunterian_used": False,
    }
    with open(os.path.join(ART, "r2ng3_representation_stats.json"), "w", encoding="utf-8") as f:
        json.dump(rep, f, indent=2)
        f.write("\n")

    summary = {
        "experiment_id": "R2-NG3-P5-REPRO",
        "timestamp_utc": utc_now(),
        "test_accessed": False,
        "gates": config["gates"],
        "frozen_bm25": FROZEN_BM25,
        "frozen_dense": FROZEN_DENSE,
        "frozen_hybrid": FROZEN_HYBRID,
        "reproduced_bm25": bm25_m,
        "reproduced_ng3": ng3_m,
        "dense_from_frozen_csv": dense_m,
        "hybrid_from_frozen_csv": hybrid_m,
        "overlap_hit50": {
            "ng3_vs_bm25": trans_hit50(ng3_h50, bm25_h50, qids),
            "ng3_vs_dense": trans_hit50(ng3_h50, dense_h50, qids),
            "ng3_vs_hybrid": trans_hit50(ng3_h50, hybrid_h50, qids),
        },
        "ng3_only_vs_bm25_and_dense": ng3_only,
        "dual_miss": {
            "n": 25,
            "ids": dual_from_components,
            "ng3_recovered": dual_recovered,
            "ng3_recovered_n": len(dual_recovered),
            "ng3_remaining_miss": dual_remain,
        },
        "room_cat1": {
            "ids": ROOM_CAT1,
            "bm25_hit@50": len(room_bm25),
            "dense_hit@50": len(room_dense),
            "hybrid_hit@50": len(room_hybrid),
            "ng3_hit@50": len(room_ng3),
            "bm25_ids": room_bm25,
            "dense_ids": room_dense,
            "hybrid_ids": room_hybrid,
            "ng3_ids": room_ng3,
        },
        "vs_bm25": {
            "ng3_recovered_bm25_miss@50": ng3_gain_bm25,
            "ng3_lost_bm25_hit@50": ng3_lost_bm25,
        },
        "runtime": runtime,
        "safety": {
            "test_accessed": False,
            "phase2_ng3_overwritten": False,
            "phase3_modified": False,
            "phase4_modified": False,
            "frozen_m0_modified": False,
            "parameter_tuning": False,
            "raw_urdu_ngrams": False,
            "tfidf": False,
            "n_changed": False,
            "fusion": False,
            "reranking": False,
        },
    }
    with open(os.path.join(ART, "r2ng3_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print("NG3", ng3_m, flush=True)
    print("dual-miss recovered", dual_recovered, "%s/25" % len(dual_recovered), flush=True)
    print("ROOM Cat1 NG3", len(room_ng3), "/11", room_ng3, flush=True)
    print("EVALUATION COMPLETE", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
