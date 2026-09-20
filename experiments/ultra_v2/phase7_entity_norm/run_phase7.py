# -*- coding: utf-8 -*-
"""PHASE7-LETTERNAME: query-side letter-name expansion + frozen Method-D BM25.

Does not edit Phase 3/4/5 artifacts, M0, or TEST. Does not fuse or rerank.
Does not download Wikidata. Gazetteer is the 26-letter table only.
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
PREREG = os.path.join(_DIR, "PHASE7_PREREGISTRATION.md")
B0_CACHE = os.path.join(P2, "artifacts", "_index_cache.pkl")
B0_PER = os.path.join(P2, "artifacts", "r2_b0_per_query.csv")
DENSE_PER = os.path.join(P3, "DENSE_PER_QUERY.csv")
HYBRID_PER = os.path.join(P4, "HYBRID_PER_QUERY.csv")
NG3_PER = os.path.join(P5NG, "R2NG3_PER_QUERY.csv")
ALLOWED_SPLITS = ("train", "dev")
EXPECTED_DICT_SHA = "30c3f61a64ec641abbb3acdbc7a8bcaf197f0238f1bf9e76c2c7ce8e590f86a3"
EXPECTED_CORPUS_SHA = "8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231"
FROZEN_BM25 = {"n": 51, "hit@1_n": 1, "hit@5_n": 4, "hit@10_n": 4, "hit@50_n": 6, "mrr": 0.0375}
FROZEN_DENSE = {"n": 51, "hit@1_n": 5, "hit@5_n": 15, "hit@10_n": 16, "hit@50_n": 22, "mrr": 0.1726}
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
import run_phase5 as p5  # noqa: E402
import letter_name as ln  # noqa: E402

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
    with open(os.path.join(ART, "phase7_blocked.json"), "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(json.dumps(payload, indent=2, ensure_ascii=False), flush=True)


def main() -> int:
    wall_t0 = time.perf_counter()
    print("label: ULTRA v2 PHASE7-LETTERNAME", flush=True)
    print("TEST_accessed: no", flush=True)
    branch, commit = git_identity()
    print("git", branch, commit, flush=True)
    if not os.path.isfile(PREREG):
        raise SystemExit("BLOCKED — PHASE7_PREREGISTRATION.md missing")
    assert len(ln.LETTER_URDU) == 26
    bbc = ln.expand_token("bbc", p5.naive_roman_word, set())
    assert bbc == ["bi", "bi", "si"], bbc
    os.makedirs(ART, exist_ok=True)
    refuse_test_path(p5.CORPUS)
    refuse_test_path(p5.DICT_PATH)

    dict_sha = sha256_file(p5.DICT_PATH)
    if dict_sha != EXPECTED_DICT_SHA:
        write_blocked({"decision": "BLOCKED", "reason": "dictionary SHA mismatch", "got": dict_sha})
        raise SystemExit("BLOCKED — dictionary SHA-256 mismatch")
    corpus_sha = sha256_file(p5.CORPUS)
    if corpus_sha != EXPECTED_CORPUS_SHA:
        write_blocked({"decision": "BLOCKED", "reason": "corpus SHA mismatch", "got": corpus_sha})
        raise SystemExit("BLOCKED — corpus SHA-256 mismatch")

    fwd = p5.load_roman_dict()
    dict_keys = {k.lower() for k in fwd}
    if len(dict_keys) != 198:
        write_blocked({"decision": "BLOCKED", "reason": "dict key count != 198", "n": len(dict_keys)})
        raise SystemExit("BLOCKED — dictionary key count")

    rows = load_roman_kn()
    qids = [r["query_id"] for r in rows]
    b0 = load_csv(B0_PER)
    dense = load_csv(DENSE_PER)
    hybrid = load_csv(HYBRID_PER)
    ng3 = load_csv(NG3_PER)
    if not (len(b0) == len(dense) == len(hybrid) == len(ng3) == 51):
        write_blocked({"decision": "BLOCKED", "reason": "frozen CSV n != 51"})
        raise SystemExit("BLOCKED — frozen per-query n != 51")

    id_mismatch = []
    for r in rows:
        qid = r["query_id"]
        gold = r["source_doc_id"]
        for name, tab, gkey in (
            ("b0", b0, "source_doc_id"),
            ("dense", dense, "source_doc_id"),
            ("hybrid", hybrid, "source_doc_id"),
            ("ng3", ng3, "source_doc_id"),
        ):
            if qid not in tab or int(tab[qid][gkey]) != gold:
                id_mismatch.append({"query_id": qid, "file": name})
    if id_mismatch:
        write_blocked({"decision": "BLOCKED", "reason": "query/gold mismatch", "mismatches": id_mismatch})
        raise SystemExit("BLOCKED — query list / gold IDs do not match Phase 3/4/5")

    for qid in QUAD23 + ROOM_CAT1:
        if qid not in set(qids):
            write_blocked({"decision": "BLOCKED", "reason": "missing frozen slice id", "id": qid})
            raise SystemExit("BLOCKED — missing slice id %s" % qid)

    if not os.path.isfile(B0_CACHE):
        write_blocked({"decision": "BLOCKED", "reason": "Method-D cache missing"})
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
        write_blocked({"decision": "BLOCKED", "reason": "BM25 cache meta mismatch"})
        raise SystemExit("BLOCKED — BM25 cache meta mismatch")
    roman_bm25 = blob["roman_bm25"]
    print("BM25 cache hit", flush=True)

    letter_roman = {k: p5.naive_roman_word(v) for k, v in ln.LETTER_URDU.items()}

    t_s = time.perf_counter()
    bm25_mismatches = []
    per_rows = []
    p7_ranks = []
    bm25_ranks = []
    n_queries_expanded = 0
    for r in rows:
        qid = r["query_id"]
        qtoks = p5.tokenize(r["query_text"])
        exp, n_exp = ln.expand_tokens(qtoks, p5.naive_roman_word, dict_keys)
        if n_exp:
            n_queries_expanded += 1
        chits = roman_bm25.search(qtoks, top_k=TOP_K)
        phits = roman_bm25.search(exp, top_k=TOP_K)
        cr = p5.rank_of(chits, r["source_doc_id"])
        pr = p5.rank_of(phits, r["source_doc_id"])
        pr2 = p5.rank_of(roman_bm25.search(exp, top_k=TOP_K), r["source_doc_id"])
        if pr != pr2:
            write_blocked({"decision": "BLOCKED", "reason": "search not identical on repeat", "query_id": qid})
            raise SystemExit("BLOCKED — search not identical")
        exp_b = parse_rank(b0[qid].get("gold_rank"))
        if cr != exp_b:
            bm25_mismatches.append({"query_id": qid, "expected": exp_b, "observed": cr})
        drk = int(dense[qid]["dense_rank"])
        nrk = parse_rank(ng3[qid].get("ng3_rank"))
        hrk = parse_rank(hybrid[qid].get("hybrid_rank"))
        bm25_ranks.append(cr)
        p7_ranks.append(pr)
        per_rows.append({
            "query_id": qid,
            "split": r["split"],
            "script": "ROMAN",
            "source_doc_id": r["source_doc_id"],
            "query_text": r["query_text"],
            "query_tokens": " ".join(qtoks),
            "expanded_tokens": " ".join(exp),
            "n_tokens_expanded": n_exp,
            "bm25_rank": cr if cr < 999 else "",
            "dense_rank": drk,
            "ng3_rank": nrk if nrk < 999 else "",
            "hybrid_rank": hrk if hrk < 999 else "",
            "p7_rank": pr if pr < 999 else "",
            "bm25_hit@1": int(cr <= 1),
            "bm25_hit@5": int(cr <= 5),
            "bm25_hit@10": int(cr <= 10),
            "bm25_hit@50": int(cr <= 50),
            "dense_hit@50": int(drk <= 50),
            "ng3_hit@50": int(nrk <= 50),
            "hybrid_hit@50": int(hrk <= 50),
            "p7_hit@1": int(pr <= 1),
            "p7_hit@5": int(pr <= 5),
            "p7_hit@10": int(pr <= 10),
            "p7_hit@50": int(pr <= 50),
            "bm25_rr": round(rec_rank(cr), 6),
            "p7_rr": round(rec_rank(pr), 6),
            "quad23": int(qid in QUAD23),
            "p7_recovered_quad23": int(qid in QUAD23 and pr <= 50),
            "room_cat1": int(qid in ROOM_CAT1),
        })
    search_sec = time.perf_counter() - t_s
    if bm25_mismatches:
        write_blocked({
            "decision": "BLOCKED",
            "reason": "Method-D gold ranks do not match r2_b0_per_query.csv",
            "mismatches": bm25_mismatches,
        })
        raise SystemExit("BLOCKED — BM25 gold ranks do not match r2_b0")

    bm25_m = kn_metrics(bm25_ranks)
    p7_m = kn_metrics(p7_ranks)
    dense_m = kn_metrics([int(dense[q]["dense_rank"]) for q in qids])
    ng3_m = kn_metrics([parse_rank(ng3[q].get("ng3_rank")) for q in qids])
    if (
        bm25_m["hit@50_n"] != FROZEN_BM25["hit@50_n"]
        or bm25_m["hit@5_n"] != FROZEN_BM25["hit@5_n"]
        or abs(bm25_m["mrr"] - FROZEN_BM25["mrr"]) > 1e-4
    ):
        write_blocked({"decision": "BLOCKED", "reason": "BM25 aggregates != frozen", "got": bm25_m})
        raise SystemExit("BLOCKED — reproduced BM25 != frozen cells")
    if dense_m["hit@50_n"] != FROZEN_DENSE["hit@50_n"]:
        write_blocked({"decision": "BLOCKED", "reason": "dense CSV aggregates != frozen"})
        raise SystemExit("BLOCKED — dense frozen CSV mismatch")
    print("GATE BM25 PASS", bm25_m, flush=True)
    print("GATE query/gold vs Phase 3/4/5 PASS", flush=True)

    p7_h50 = {row["query_id"]: int(row["p7_hit@50"]) for row in per_rows}
    b_h50 = {row["query_id"]: int(row["bm25_hit@50"]) for row in per_rows}
    d_h50 = {row["query_id"]: int(row["dense_hit@50"]) for row in per_rows}
    n_h50 = {row["query_id"]: int(row["ng3_hit@50"]) for row in per_rows}

    rec23 = [q for q in QUAD23 if p7_h50[q] == 1]
    remain23 = [q for q in QUAD23 if p7_h50[q] == 0]
    room_p7 = [q for q in ROOM_CAT1 if p7_h50[q] == 1]
    lost_bm25 = [row["query_id"] for row in per_rows if row["bm25_hit@50"] == 1 and row["p7_hit@50"] == 0]
    gain_bm25 = [row["query_id"] for row in per_rows if row["bm25_hit@50"] == 0 and row["p7_hit@50"] == 1]

    csv_path = os.path.join(_DIR, "PHASE7_PER_QUERY.csv")
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(per_rows[0].keys()))
        w.writeheader()
        w.writerows(per_rows)

    wall = round(time.perf_counter() - wall_t0, 3)
    runtime = {
        "search_seconds": round(search_sec, 3),
        "wall_seconds": wall,
        "device": "cpu",
        "cuda": False,
        "hardware": {
            "platform": platform.platform(),
            "processor": platform.processor(),
            "cpu_count": os.cpu_count(),
            "python": sys.version.split()[0],
        },
    }
    config = {
        "experiment_id": "PHASE7-LETTERNAME",
        "timestamp_utc": utc_now(),
        "branch": branch,
        "commit": commit,
        "test_accessed": False,
        "preregistration_sha256": sha256_file(PREREG),
        "letter_name_py_sha256": sha256_file(os.path.join(_DIR, "letter_name.py")),
        "run_py_sha256": sha256_file(os.path.join(_DIR, "run_phase7.py")),
        "corpus_sha256": corpus_sha,
        "dict_sha256": dict_sha,
        "letter_urdu": ln.LETTER_URDU,
        "letter_roman_naive_roman_word": letter_roman,
        "acronym_regex": ln.ACRONYM_RE.pattern,
        "token_rule": "len 2-4 [a-z], not in 198-key dict, then per-letter naive_roman_word",
        "wikidata": False,
        "document_reprocessed": False,
        "fusion": False,
        "rerank": False,
        "parameter_tuning": False,
        "gates": {
            "corpus_sha": "PASS",
            "query_gold_vs_phase3_4_5": "PASS",
            "bm25_vs_r2_b0": "PASS",
            "search_repeat": "PASS",
        },
    }
    with open(os.path.join(ART, "phase7_config.json"), "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
        f.write("\n")

    summary = {
        "experiment_id": "PHASE7-LETTERNAME",
        "timestamp_utc": utc_now(),
        "test_accessed": False,
        "gates": config["gates"],
        "frozen_bm25": FROZEN_BM25,
        "reproduced_bm25": bm25_m,
        "phase7_lettername": p7_m,
        "dense_from_frozen_csv": {
            "hit@50_n": dense_m["hit@50_n"],
            "hit@5_n": dense_m["hit@5_n"],
            "mrr": dense_m["mrr"],
        },
        "ng3_from_frozen_csv": {
            "hit@50_n": ng3_m["hit@50_n"],
            "mrr": ng3_m["mrr"],
        },
        "n_queries_with_expansion": n_queries_expanded,
        "overlap_hit50": {
            "p7_vs_bm25": trans_hit50(p7_h50, b_h50, qids),
            "p7_vs_dense": trans_hit50(p7_h50, d_h50, qids),
            "p7_vs_ng3": trans_hit50(p7_h50, n_h50, qids),
        },
        "quad23": {
            "n": 23,
            "ids": QUAD23,
            "p7_recovered": rec23,
            "p7_recovered_n": len(rec23),
            "p7_remaining": remain23,
        },
        "room_cat1": {
            "ids": ROOM_CAT1,
            "bm25_hit@50": 0,
            "dense_hit@50": 3,
            "hybrid_hit@50": 3,
            "ng3_hit@50": 1,
            "p7_hit@50": len(room_p7),
            "p7_ids": room_p7,
        },
        "vs_bm25": {"recovered": gain_bm25, "regressed": lost_bm25},
        "runtime": runtime,
        "safety": {
            "test_accessed": False,
            "gazetteer_from_benchmark": False,
            "wikidata": False,
            "phase3_4_5_modified": False,
            "fusion": False,
            "reranking": False,
            "parameter_tuning": False,
        },
    }
    with open(os.path.join(ART, "phase7_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print("P7", p7_m, flush=True)
    print("expanded_queries", n_queries_expanded, "/51", flush=True)
    print("quad23 recovered", rec23, "%s/23" % len(rec23), flush=True)
    print("ROOM Cat1 P7", len(room_p7), "/11", room_p7, flush=True)
    print("EVALUATION COMPLETE", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
