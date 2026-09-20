# -*- coding: utf-8 -*-
"""R2-NG3: character 3-gram BM25 over frozen Method D tokens. TRAIN/DEV only.

Does not edit M0, dictionary, R2-B0/C0/R2-1 artifacts. Does not access TEST.
Does not import or use hunterian_ascii_positional_v1.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
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
TEST_DIR = os.path.abspath(os.path.join(BENCH, "test"))
ART = os.path.join(_DIR, "artifacts")
B0_CACHE = os.path.join(ART, "_index_cache.pkl")
B0_PER = os.path.join(ART, "r2_b0_per_query.csv")
C0_CSV = os.path.join(_DIR, "R2_C0_REPRESENTATION_AUDIT.csv")
EXPECTED_DICT_SHA = "30c3f61a64ec641abbb3acdbc7a8bcaf197f0238f1bf9e76c2c7ce8e590f86a3"
EXPECTED_CORPUS_SHA = "8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231"
ALLOWED_SPLITS = ("train", "dev")
TOP_K = 50
HIT_K = 5
ROOM1 = [
    "KN001", "KN006", "KN008", "KN010", "KN011", "KN018",
    "KN037", "KN045", "KN047", "KN050", "KN051",
]
NEG_VOCAB = ("KN017", "KN020", "KN041")
NEG_SPLIT = ("KN006", "KN047", "KN051")
EXPECTED_HITS = {"KN004": 1, "KN012": 5, "KN023": 3, "KN038": 3}
EXPECTED_RANK = {"KN014": 44, "KN048": 42}
EXPECTED_BASELINE = {
    "n": 51, "hit@1_n": 1, "hit@5_n": 4, "hit@10_n": 4, "hit@50_n": 6, "mrr": 0.0375,
}

sys.path.insert(0, P5)
sys.path.insert(0, _DIR)
import run_phase5 as p5  # noqa: E402
import ng3_matching as ng3  # noqa: E402

assert ng3.N == 3
assert ng3.char3_grams("world") == ["wor", "orl", "rld"]
assert ng3.char3_grams("orld") == ["orl", "rld"]
assert ng3.char3_grams("ke") == ["ke"]
assert "hunterian" not in open(os.path.join(_DIR, "ng3_matching.py"), encoding="utf-8").read()


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
        raise SystemExit("REFUSED: TEST path is forbidden for R2-NG3: %s" % ap)


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


def status_of(rank: int) -> str:
    if rank <= HIT_K:
        return "HIT"
    if rank <= TOP_K:
        return "RANK"
    return "MISS"


def exact_mcnemar(n01: int, n10: int) -> dict:
    n = n01 + n10
    if n == 0:
        return {"n_discordant": 0, "p_two_sided": 1.0, "note": "no discordant pairs"}
    k = min(n01, n10)
    p = 0.0
    for i in range(0, k + 1):
        p += math.comb(n, i)
    p = min(1.0, 2.0 * p * (0.5 ** n))
    return {
        "n_discordant": n,
        "n01_recovered": n01,
        "n10_regressed": n10,
        "p_two_sided": round(p, 6),
    }


def load_roman_kn() -> list[dict]:
    rows = []
    for split in ALLOWED_SPLITS:
        path = os.path.join(BENCH, split, "queries_kn.csv")
        refuse_test_path(path)
        with open(path, encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f):
                if (r.get("split") or "").strip() != split:
                    raise SystemExit("split mismatch %s" % r.get("query_id"))
                if (r.get("script") or "").strip() != "ROMAN":
                    continue
                text = r["query_text"]
                if p5.detect_script(text) != "ROMAN":
                    raise SystemExit("detector mismatch %s" % r["query_id"])
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


def load_csv_map(path: str, key: str = "query_id") -> dict[str, dict]:
    refuse_test_path(path)
    out = {}
    with open(path, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            out[r[key]] = r
    return out


def main() -> int:
    print("R2-NG3 CHARACTER 3-GRAM MATCHING", flush=True)
    print("H1: 3-grams over frozen Method D tokens recover some ROOM Cat1 into Top-50", flush=True)
    print("n=3 token-internal; hunterian unused; TEST_accessed=no", flush=True)

    assert p5.BM25_K1 == 1.5
    assert p5.BM25_B == 0.75
    assert TOP_K == 50 and HIT_K == 5
    assert ng3.N == 3
    refuse_test_path(p5.CORPUS)
    refuse_test_path(p5.DICT_PATH)
    dict_sha = sha256_file(p5.DICT_PATH)
    if dict_sha != EXPECTED_DICT_SHA:
        raise SystemExit("STOP: dictionary SHA mismatch")
    corpus_sha = sha256_file(p5.CORPUS)
    if corpus_sha != EXPECTED_CORPUS_SHA:
        raise SystemExit("STOP: corpus SHA mismatch")

    rows = load_roman_kn()
    if len(rows) != 51:
        raise SystemExit("expected 51 Roman KN, got %s" % len(rows))
    ids = [r["query_id"] for r in rows]
    if sorted(ROOM1) != ROOM1:
        raise SystemExit("ROOM1 list order must remain the pre-registered order")
    for qid in ROOM1 + list(NEG_VOCAB) + list(EXPECTED_HITS) + list(EXPECTED_RANK):
        if qid not in ids:
            raise SystemExit("missing query %s" % qid)

    b0 = load_csv_map(B0_PER)
    c0 = load_csv_map(C0_CSV)
    fwd = p5.load_roman_dict()
    rev = p5.load_reverse_roman(fwd)
    assert len(fwd) == 198

    if not os.path.isfile(B0_CACHE):
        raise SystemExit("STOP: missing R2-B0 index cache for CONTROL")
    with open(B0_CACHE, "rb") as f:
        blob = pickle.load(f)
    want_meta = {
        "corpus_sha256": corpus_sha,
        "dict_sha256": dict_sha,
        "k1": 1.5,
        "b": 0.75,
        "tokenizer": p5.TOKEN_RE.pattern,
    }
    if blob.get("meta") != want_meta:
        raise SystemExit("STOP: R2-B0 cache meta mismatch")
    control_bm25 = blob["roman_bm25"]
    print("CONTROL cache hit (frozen Method D exact-token BM25)", flush=True)

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
    print("docs=%s" % n_docs, flush=True)

    gold_needed = {r["source_doc_id"] for r in rows}
    control_gold: dict[int, list[str]] = {}
    ng3_docs: list[list[str]] = []
    stats = Counter()
    md_hasher = hashlib.sha256()
    ng3_hasher = hashlib.sha256()
    t0 = time.perf_counter()
    print("Method D tokenize + NG3 expand...", flush=True)
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
    tokenize_sec = time.perf_counter() - t0
    print("tokenize+expand %.1fs features=%s" % (tokenize_sec, stats["ng3_features"]), flush=True)

    print("build NG3 BM25...", flush=True)
    t1 = time.perf_counter()
    ng3_bm25 = p5.BM25(ng3_docs, k1=1.5, b=0.75)
    build_sec = time.perf_counter() - t1
    print("ng3 BM25 %.1fs terms=%s" % (build_sec, len(ng3_bm25.idf)), flush=True)

    control_ranks = []
    ng3_ranks = []
    ng3_ranks_repeat = []
    per = []
    for r in rows:
        qtoks = p5.tokenize(r["query_text"])
        q3 = ng3.expand_tokens(qtoks)
        chits = control_bm25.search(qtoks, top_k=TOP_K)
        nhits = ng3_bm25.search(q3, top_k=TOP_K)
        nhits2 = ng3_bm25.search(q3, top_k=TOP_K)
        cr = p5.rank_of(chits, r["source_doc_id"])
        nr = p5.rank_of(nhits, r["source_doc_id"])
        nr2 = p5.rank_of(nhits2, r["source_doc_id"])
        control_ranks.append(cr)
        ng3_ranks.append(nr)
        ng3_ranks_repeat.append(nr2)
        b0r = b0[r["query_id"]]
        b0_rank = 999 if b0r["gold_rank"] == "" else int(b0r["gold_rank"])
        if cr != b0_rank:
            raise SystemExit("BASELINE RANK MISMATCH %s got=%s file=%s" % (r["query_id"], cr, b0_rank))
        if r["query_id"] in EXPECTED_HITS and cr != EXPECTED_HITS[r["query_id"]]:
            raise SystemExit("success rank mismatch %s" % r["query_id"])
        if r["query_id"] in EXPECTED_RANK and cr != EXPECTED_RANK[r["query_id"]]:
            raise SystemExit("RANK case mismatch %s" % r["query_id"])
        gold_md = control_gold[r["source_doc_id"]]
        qset = ng3.feature_set(qtoks)
        gset = ng3.feature_set(gold_md)
        shared = sorted(qset & gset)
        c0r = c0.get(r["query_id"], {})
        primary = c0r.get("primary") or ("SUCCESS" if cr <= HIT_K else "")
        bstat = status_of(cr)
        tstat = status_of(nr)
        rec = int(cr > TOP_K and nr <= TOP_K)
        reg = int(cr <= TOP_K and nr > TOP_K)
        per.append({
            "query_id": r["query_id"],
            "split": r["split"],
            "query_script": "ROMAN",
            "gold_doc_id": r["source_doc_id"],
            "baseline_rank": cr if cr < 999 else "",
            "baseline_hit1": int(cr <= 1),
            "baseline_hit5": int(cr <= HIT_K),
            "baseline_hit10": int(cr <= 10),
            "baseline_hit50": int(cr <= TOP_K),
            "ng3_rank": nr if nr < 999 else "",
            "ng3_hit1": int(nr <= 1),
            "ng3_hit5": int(nr <= HIT_K),
            "ng3_hit10": int(nr <= 10),
            "ng3_hit50": int(nr <= TOP_K),
            "baseline_status": bstat,
            "treatment_status": tstat,
            "recovered": rec,
            "regressed": reg,
            "rank_delta": "" if (cr >= 999 and nr >= 999) else (
                (999 if nr >= 999 else nr) - (999 if cr >= 999 else cr)
            ),
            "primary_slice": int(r["query_id"] in ROOM1),
            "negative_control": (
                "vocab" if r["query_id"] in NEG_VOCAB
                else ("split_acronym" if r["query_id"] in NEG_SPLIT else "")
            ),
            "failure_category_if_known": primary,
            "ng3_q_features": len(q3),
            "ng3_overlap_gold": len(shared),
            "shared_trigrams_sample": " ".join(shared[:20]),
        })

    if ng3_ranks != ng3_ranks_repeat:
        raise SystemExit("STOP: NG3 search not deterministic on repeat")

    ctrl = kn_metrics(control_ranks)
    if (
        ctrl["n"] != EXPECTED_BASELINE["n"]
        or ctrl["hit@1_n"] != EXPECTED_BASELINE["hit@1_n"]
        or ctrl["hit@5_n"] != EXPECTED_BASELINE["hit@5_n"]
        or ctrl["hit@10_n"] != EXPECTED_BASELINE["hit@10_n"]
        or ctrl["hit@50_n"] != EXPECTED_BASELINE["hit@50_n"]
        or ctrl["mrr"] != EXPECTED_BASELINE["mrr"]
    ):
        raise SystemExit("BASELINE METRIC MISMATCH %s" % ctrl)
    print("baseline reproduction: PASS", ctrl, flush=True)

    trt = kn_metrics(ng3_ranks)
    id_to = {p["query_id"]: p for p in per}

    def slice_hit50(qids: list[str]) -> dict:
        rs = []
        for q in qids:
            v = id_to[q]["ng3_rank"]
            rs.append(999 if v == "" else int(v))
        h = sum(1 for x in rs if x <= TOP_K)
        b = sum(1 for q in qids if id_to[q]["baseline_hit50"])
        return {"n": len(qids), "baseline_hit50_n": b, "treatment_hit50_n": h}

    room1_s = slice_hit50(ROOM1)
    recovered = [p["query_id"] for p in per if p["recovered"]]
    regressed = [p["query_id"] for p in per if p["regressed"]]
    room1_rec = [q for q in ROOM1 if id_to[q]["recovered"]]
    room1_remain = [q for q in ROOM1 if not id_to[q]["ng3_hit50"]]
    trans = Counter((p["baseline_status"], p["treatment_status"]) for p in per)
    miss_b = sum(1 for p in per if not p["baseline_hit50"])
    miss_t = sum(1 for p in per if not p["ng3_hit50"])
    n01 = sum(1 for p in per if p["ng3_hit50"] > p["baseline_hit50"])
    n10 = sum(1 for p in per if p["ng3_hit50"] < p["baseline_hit50"])

    def split_m(split: str) -> tuple[dict, dict]:
        cr = [rk for r, rk in zip(rows, control_ranks) if r["split"] == split]
        nr = [rk for r, rk in zip(rows, ng3_ranks) if r["split"] == split]
        return kn_metrics(cr), kn_metrics(nr)

    train_c, train_t = split_m("train")
    dev_c, dev_t = split_m("dev")

    room1_detail = []
    for q in ROOM1:
        p = id_to[q]
        room1_detail.append({
            "query_id": q,
            "baseline_rank": p["baseline_rank"],
            "ng3_rank": p["ng3_rank"],
            "recovered": p["recovered"],
            "baseline_in50": p["baseline_hit50"],
            "ng3_in50": p["ng3_hit50"],
            "ng3_overlap_gold": p["ng3_overlap_gold"],
            "shared_trigrams_sample": p["shared_trigrams_sample"],
        })

    neg = {}
    for q in NEG_VOCAB:
        p = id_to[q]
        neg[q] = {
            "category": p["failure_category_if_known"],
            "baseline_rank": p["baseline_rank"],
            "ng3_rank": p["ng3_rank"],
            "baseline_hit50": p["baseline_hit50"],
            "ng3_hit50": p["ng3_hit50"],
            "ng3_overlap_gold": p["ng3_overlap_gold"],
        }

    os.makedirs(ART, exist_ok=True)
    config = {
        "experiment_id": "R2-NG3",
        "n_gram": 3,
        "token_boundary_policy": "A_within_existing_tokens",
        "short_token_policy": "len<3 keep token as single feature",
        "document_representation": "frozen Method D romanize_token then char-3-grams",
        "r2_1_hunterian_used": False,
        "query_representation": "frozen tokenize then char-3-grams; no dictionary",
        "bm25_k1": 1.5,
        "bm25_b": 0.75,
        "candidate_depth": 50,
        "official_cutoff": 5,
        "primary_endpoint": "ExactSource Hit@50 on ROOM Category 1 n=11",
        "primary_slice_ids": ROOM1,
        "negative_controls_vocab": list(NEG_VOCAB),
        "negative_controls_split": list(NEG_SPLIT),
        "dictionary_sha256": dict_sha,
        "corpus_sha256": corpus_sha,
        "method_d_token_stream_sha256": md_hasher.hexdigest(),
        "ng3_feature_stream_sha256": ng3_hasher.hexdigest(),
        "test_accessed": False,
        "git_branch": "research/ultra-v2-strengthening",
        "git_commit": "fd54ac9b65c2db93e7e16fbf0c5a40b6a6025be1",
    }
    summary = {
        "experiment_id": "R2-NG3",
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "test_accessed": False,
        "baseline_reproduction": "PASS",
        "search_repeat_identical": True,
        "control_metrics": {"train": train_c, "dev": dev_c, "train+dev": ctrl},
        "treatment_metrics": {"train": train_t, "dev": dev_t, "train+dev": trt},
        "primary_room_cat1": {
            "n": 11,
            "baseline_hit50_n": 0,
            "treatment_hit50_n": room1_s["treatment_hit50_n"],
            "absolute_change_n": room1_s["treatment_hit50_n"] - 0,
            "recovered": room1_rec,
            "remaining_misses": room1_remain,
            "detail": room1_detail,
        },
        "candidate_generation": {
            "baseline_outside_top50": miss_b,
            "treatment_outside_top50": miss_t,
            "recovered": recovered,
            "regressed": regressed,
            "net_hit50_n": trt["hit@50_n"] - ctrl["hit@50_n"],
        },
        "transitions": {("%s->%s" % k): v for k, v in sorted(trans.items())},
        "negative_controls_vocab": neg,
        "mcnemar_hit50": exact_mcnemar(n01, n10),
        "tokenize_expand_sec": round(tokenize_sec, 2),
        "bm25_build_sec": round(build_sec, 2),
        "n_docs": n_docs,
        "python": sys.version.split()[0],
    }
    rep_stats = {
        "n_docs": n_docs,
        "method_d_tokens": stats["md_tokens"],
        "ng3_features": stats["ng3_features"],
        "short_passthrough_tokens": stats["short_passthrough"],
        "ng3_vocabulary_terms": len(ng3_bm25.idf),
        "method_d_token_stream_sha256": md_hasher.hexdigest(),
        "ng3_feature_stream_sha256": ng3_hasher.hexdigest(),
        "hunterian_used": False,
        "n_gram": 3,
    }
    with open(os.path.join(ART, "r2_ng3_config.json"), "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
    with open(os.path.join(ART, "r2_ng3_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    with open(os.path.join(ART, "r2_ng3_representation_stats.json"), "w", encoding="utf-8") as f:
        json.dump(rep_stats, f, indent=2)
    out_csv = os.path.join(_DIR, "R2_NG3_PER_QUERY.csv")
    fields = list(per[0].keys())
    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(per)

    print("PRIMARY ROOM cat1 Hit@50 0/11 -> %s/11 recovered=%s" % (
        room1_s["treatment_hit50_n"], room1_rec), flush=True)
    print("ALL51 control", ctrl, "treatment", trt, flush=True)
    print("outside50", miss_b, "->", miss_t, "recovered", recovered, "regressed", regressed, flush=True)
    print("neg", neg, flush=True)
    print("status: R2-NG3 RETRIEVAL DONE", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
