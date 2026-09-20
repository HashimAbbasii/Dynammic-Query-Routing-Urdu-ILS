# -*- coding: utf-8 -*-
"""DENSE-BASELINE: zero-shot multilingual dense retrieval on ULTRA v2 TRAIN/DEV.

Does not open benchmark/test/ query files.
Does not edit frozen M0, R2 artifacts, PLOS, or the dictionary.
Does not fine-tune, hybridize, or rerank.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import platform
import re
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from math import comb

# One OpenMP runtime: MKL sequential, Torch keeps Intel OpenMP.
# Do not set KMP_DUPLICATE_LIB_OK (that only hides two libiomp5md.dll copies).
os.environ.setdefault("MKL_THREADING_LAYER", "SEQUENTIAL")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(_DIR, "..", "..", ".."))
P5 = os.path.join(ROOT, "experiments", "phase5_roman_urdu")
BENCH = os.path.join(ROOT, "experiments", "ultra_v2", "benchmark")
TEST_DIR = os.path.abspath(os.path.join(BENCH, "test"))
ART = os.path.join(_DIR, "artifacts")
R2_ART = os.path.join(ROOT, "experiments", "ultra_v2", "phase2_roman", "artifacts")
R2_FAIL_CSV = os.path.join(ROOT, "experiments", "ultra_v2", "phase2_roman", "R2_B0_FAILURE_ANALYSIS.csv")
R2_PER_QUERY = os.path.join(R2_ART, "r2_b0_per_query.csv")
PREREG = os.path.join(_DIR, "DENSE_PREREGISTRATION.md")
ALLOWED_SPLITS = ("train", "dev")
ID_RE = re.compile(r"^(KN|NL)\d{3}$")
FORBIDDEN_ID_RE = re.compile(r"^(QTRN|H\d|K\d{3}$|U\d)")
ROOM_CAT1 = [
    "KN001", "KN006", "KN008", "KN010", "KN011",
    "KN018", "KN037", "KN045", "KN047", "KN050", "KN051",
]
VOCAB_CONTROLS = ["KN017", "KN020", "KN041"]
FROZEN_BASELINE = {
    "n": 51,
    "hit@1_n": 1,
    "hit@5_n": 4,
    "hit@10_n": 4,
    "hit@50_n": 6,
    "mrr": 0.0375,
}

sys.path.insert(0, P5)
import run_phase5 as p5  # noqa: E402

import dense_retrieval as dr  # noqa: E402


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def refuse_test_path(path: str) -> None:
    ap = os.path.abspath(path)
    if ap == TEST_DIR or ap.startswith(TEST_DIR + os.sep):
        raise SystemExit("BLOCKED — DATA SAFETY FAILURE: TEST path forbidden: %s" % ap)


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(1024 * 1024)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


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


def mcnemar_exact(b: int, c: int) -> float:
    """Two-sided exact McNemar (binomial) on discordant pairs. b=B-hit D-miss, c=B-miss D-hit."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(comb(n, i) for i in range(0, k + 1))
    p = min(1.0, 2.0 * tail / (2 ** n))
    return p


def parse_rank(val: str) -> int:
    s = (val or "").strip()
    if not s:
        return 999
    return int(float(s))


def load_authorized_queries() -> tuple[list[dict], dict]:
    """Load TRAIN/DEV KN (all scripts, scored) and NL (IDs only). Never TEST."""
    kn_rows: list[dict] = []
    nl_ids = {"train": [], "dev": []}
    safety = {
        "forbidden_ids": [],
        "id_pattern_failures": [],
        "script_mismatches": [],
        "split_mismatches": [],
        "test_paths_opened": False,
        "qtrn": 0,
        "historical_h": 0,
        "historical_k": 0,
        "historical_u": 0,
    }
    for split in ALLOWED_SPLITS:
        kn_path = os.path.join(BENCH, split, "queries_kn.csv")
        nl_path = os.path.join(BENCH, split, "queries_nl.csv")
        refuse_test_path(kn_path)
        refuse_test_path(nl_path)
        with open(kn_path, encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f):
                qid = (r.get("query_id") or "").strip()
                if not ID_RE.match(qid) or not qid.startswith("KN"):
                    safety["id_pattern_failures"].append(qid)
                if FORBIDDEN_ID_RE.match(qid) or qid.startswith("QTRN") or re.match(r"^H\d", qid):
                    safety["forbidden_ids"].append(qid)
                if (r.get("split") or "").strip() != split:
                    safety["split_mismatches"].append(qid)
                text = r["query_text"]
                meta_script = (r.get("script") or "").strip()
                det = p5.detect_script(text)
                if det != meta_script:
                    safety["script_mismatches"].append("%s meta=%s det=%s" % (qid, meta_script, det))
                src = (r.get("source_doc_id") or "").strip()
                if not src:
                    raise SystemExit("BLOCKED — KN missing source_doc_id %s" % qid)
                kn_rows.append({
                    "query_id": qid,
                    "query_text": text,
                    "split": split,
                    "script": meta_script,
                    "script_detector": det,
                    "source_doc_id": int(src),
                    "track": "KN",
                })
        with open(nl_path, encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f):
                qid = (r.get("query_id") or "").strip()
                if not ID_RE.match(qid) or not qid.startswith("NL"):
                    safety["id_pattern_failures"].append(qid)
                if FORBIDDEN_ID_RE.match(qid) or qid.startswith("QTRN"):
                    safety["forbidden_ids"].append(qid)
                if (r.get("split") or "").strip() != split:
                    safety["split_mismatches"].append(qid)
                if (r.get("source_doc_id") or "").strip():
                    raise SystemExit("BLOCKED — NL has source_doc_id %s" % qid)
                nl_ids[split].append(qid)
    if safety["forbidden_ids"] or safety["id_pattern_failures"] or safety["script_mismatches"] or safety["split_mismatches"]:
        print(json.dumps(safety, indent=2), flush=True)
        raise SystemExit("BLOCKED — DATA SAFETY FAILURE")
    roman_kn = [r for r in kn_rows if r["script"] == "ROMAN"]
    if len(roman_kn) != 51:
        raise SystemExit("BLOCKED — Roman KN TRAIN+DEV n=%s != 51" % len(roman_kn))
    return kn_rows, {
        "kn_train": sum(1 for r in kn_rows if r["split"] == "train"),
        "kn_dev": sum(1 for r in kn_rows if r["split"] == "dev"),
        "kn_total": len(kn_rows),
        "roman_kn": len(roman_kn),
        "nl_train": len(nl_ids["train"]),
        "nl_dev": len(nl_ids["dev"]),
        "nl_scored": False,
        "safety": safety,
        "script_counts": {"%s/%s" % k: v for k, v in Counter((r["script"], r["split"]) for r in kn_rows).items()},
        "kn_script_totals": dict(Counter(r["script"] for r in kn_rows)),
    }


def load_r2_b0() -> dict[str, dict]:
    refuse_test_path(R2_PER_QUERY)
    out = {}
    with open(R2_PER_QUERY, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            qid = r["query_id"]
            rank = parse_rank(r.get("gold_rank"))
            out[qid] = {
                "query_id": qid,
                "split": r["split"],
                "script": r["script"],
                "source_doc_id": int(r["source_doc_id"]),
                "baseline_rank": rank,
                "baseline_hit@1": int(rank <= 1),
                "baseline_hit@5": int(rank <= 5),
                "baseline_hit@10": int(rank <= 10),
                "baseline_hit@50": int(rank <= 50),
            }
    if len(out) != 51:
        raise SystemExit("BLOCKED — R2-B0 per-query n=%s != 51" % len(out))
    ranks = [v["baseline_rank"] for v in out.values()]
    m = kn_metrics(ranks)
    if (
        m["hit@1_n"] != FROZEN_BASELINE["hit@1_n"]
        or m["hit@5_n"] != FROZEN_BASELINE["hit@5_n"]
        or m["hit@10_n"] != FROZEN_BASELINE["hit@10_n"]
        or m["hit@50_n"] != FROZEN_BASELINE["hit@50_n"]
        or abs(m["mrr"] - FROZEN_BASELINE["mrr"]) > 1e-4
    ):
        raise SystemExit("BLOCKED — R2-B0 artifact does not reproduce frozen cells: %s" % m)
    return out


def load_taxonomy() -> dict[str, str]:
    tax = {}
    with open(R2_FAIL_CSV, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            tax[r["query_id"]] = (r.get("primary") or "").strip()
    return tax


def fail_side(rank: int) -> str:
    if rank <= 5:
        return "HIT@5"
    if rank <= 50:
        return "RANK"
    return "MISS"


def main() -> int:
    print("label: ULTRA v2 DENSE-BASELINE", flush=True)
    print("TEST_accessed: no", flush=True)
    if not os.path.isfile(PREREG):
        raise SystemExit("BLOCKED — DENSE_PREREGISTRATION.md missing")
    os.makedirs(ART, exist_ok=True)
    refuse_test_path(p5.CORPUS)

    kn_rows, pop = load_authorized_queries()
    print(
        "KN train/dev", pop["kn_total"],
        "Roman", pop["roman_kn"],
        "NL train", pop["nl_train"],
        "NL dev", pop["nl_dev"],
        "nl_scored: no",
        flush=True,
    )
    print("KN scripts", pop["kn_script_totals"], flush=True)

    baseline = load_r2_b0()
    taxonomy = load_taxonomy()
    print("R2-B0 frozen cells reproduced from artifact", flush=True)

    corpus_sha = sha256_file(p5.CORPUS)
    if corpus_sha != dr.EXPECTED_CORPUS_SHA:
        raise SystemExit("BLOCKED — corpus SHA-256 mismatch")

    model, enc_info = dr.load_encoder()
    loaded_rev = dr.MODEL_REVISION
    try:
        # sentence-transformers / huggingface may expose revision on model card
        card = getattr(model, "model_card_data", None)
        enc_info["st_model_card_present"] = card is not None
    except Exception:
        enc_info["st_model_card_present"] = False
    enc_info["loaded_revision"] = loaded_rev

    texts, rep_stats = dr.load_corpus_texts(p5.CORPUS)
    for r in kn_rows:
        if r["source_doc_id"] < 0 or r["source_doc_id"] >= len(texts):
            raise SystemExit("BLOCKED — gold id out of corpus %s" % r["query_id"])

    config = {
        "experiment_id": "DENSE-BASELINE",
        "timestamp_utc_start": utc_now(),
        "test_accessed": False,
        "preregistration_sha256": sha256_file(PREREG),
        "dense_retrieval_py_sha256": sha256_file(os.path.join(_DIR, "dense_retrieval.py")),
        "run_dense_baseline_py_sha256": sha256_file(os.path.join(_DIR, "run_dense_baseline.py")),
        "corpus_sha256": corpus_sha,
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "encoder": enc_info,
        "population": {k: v for k, v in pop.items() if k != "safety"},
        "top_k": dr.TOP_K,
        "hit_k": dr.HIT_K,
        "hybrid": False,
        "rerank": False,
        "finetune": False,
        "model_shopping": False,
        "parameter_tuning": False,
        "gold_injection": False,
        "query_rewriting": False,
        "nl_scored": False,
        "baseline_artifact": os.path.relpath(R2_PER_QUERY, ROOT).replace("\\", "/"),
    }
    with open(os.path.join(ART, "dense_config.json"), "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
        f.write("\n")
    with open(os.path.join(ART, "dense_representation_stats.json"), "w", encoding="utf-8") as f:
        json.dump(rep_stats, f, indent=2)
        f.write("\n")

    t_index = time.perf_counter()
    doc_matrix = dr.load_or_build_doc_matrix(
        model,
        texts,
        enc_info,
        os.path.join(ART, "dense_doc_embeddings.npy"),
        os.path.join(ART, "dense_embed_progress.json"),
        corpus_sha,
        os.path.join(ART, "dense_index_meta.json"),
    )
    index_sec = time.perf_counter() - t_index
    print("doc matrix", tuple(doc_matrix.shape), "index_or_load %.1fs" % index_sec, flush=True)

    # Embed authorized KN TRAIN/DEV queries (not NL, not TEST).
    t_q = time.perf_counter()
    q_texts = [r["query_text"] for r in kn_rows]
    q_vecs = dr.encode_texts(
        model,
        q_texts,
        kind="query",
        prefix_mode=enc_info["prefix_mode"],
        prompt_name=enc_info.get("query_prompt_name"),
        show_progress=False,
    )
    q_embed_sec = time.perf_counter() - t_q
    print("query embed n=%s %.2fs" % (len(q_texts), q_embed_sec), flush=True)

    t_search = time.perf_counter()
    results_pass1 = []
    for r, qv in zip(kn_rows, q_vecs):
        results_pass1.append(dr.search_query_vec(doc_matrix, qv, r["source_doc_id"], k=dr.TOP_K))
    search_sec = time.perf_counter() - t_search

    # Second search pass: re-encode queries and recompute ranks (reproducibility).
    t_q2 = time.perf_counter()
    q_vecs2 = dr.encode_texts(
        model,
        q_texts,
        kind="query",
        prefix_mode=enc_info["prefix_mode"],
        prompt_name=enc_info.get("query_prompt_name"),
        show_progress=False,
    )
    q2_sec = time.perf_counter() - t_q2
    ranks1 = [x["gold_rank"] for x in results_pass1]
    ranks2 = []
    sims_match = True
    for r, qv, a in zip(kn_rows, q_vecs2, results_pass1):
        b = dr.search_query_vec(doc_matrix, qv, r["source_doc_id"], k=dr.TOP_K)
        ranks2.append(b["gold_rank"])
        if b["gold_rank"] != a["gold_rank"]:
            sims_match = False
    rank_identity = ranks1 == ranks2
    print("reproducibility rank_identity=%s vec_close=%s" % (
        rank_identity,
        bool(np_allclose := __import__("numpy").allclose(q_vecs, q_vecs2, atol=1e-6)),
    ), flush=True)
    if not rank_identity:
        disagree = [
            kn_rows[i]["query_id"] for i, (a, b) in enumerate(zip(ranks1, ranks2)) if a != b
        ]
        print("BLOCKED — ranks not identical on second search", disagree[:20], flush=True)
        raise SystemExit("BLOCKED — reproducibility failure")

    roman_rows = [r for r in kn_rows if r["script"] == "ROMAN"]
    roman_idx = [i for i, r in enumerate(kn_rows) if r["script"] == "ROMAN"]

    per_query_path = os.path.join(_DIR, "DENSE_PER_QUERY.csv")
    fields = [
        "query_id", "split", "script", "source_doc_id", "r2_primary",
        "baseline_rank", "baseline_hit@1", "baseline_hit@5", "baseline_hit@10", "baseline_hit@50",
        "dense_rank", "dense_hit@1", "dense_hit@5", "dense_hit@10", "dense_hit@50",
        "dense_gold_similarity", "dense_rank1_similarity", "dense_rank1_doc_id",
        "dense_recovered_baseline_miss50", "dense_lost_baseline_hit50",
        "dense_recovered_baseline_miss5", "dense_lost_baseline_hit5",
        "dense_fail_side", "room_cat1", "vocab_control",
    ]
    per_rows = []
    with open(per_query_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for i in roman_idx:
            r = kn_rows[i]
            d = results_pass1[i]
            b = baseline[r["query_id"]]
            if b["source_doc_id"] != r["source_doc_id"]:
                raise SystemExit("BLOCKED — source mismatch %s" % r["query_id"])
            drank = int(d["gold_rank"])
            brank = int(b["baseline_rank"])
            row = {
                "query_id": r["query_id"],
                "split": r["split"],
                "script": r["script"],
                "source_doc_id": r["source_doc_id"],
                "r2_primary": taxonomy.get(r["query_id"], "SUCCESS" if brank <= 5 else ""),
                "baseline_rank": brank if brank < 999 else "",
                "baseline_hit@1": b["baseline_hit@1"],
                "baseline_hit@5": b["baseline_hit@5"],
                "baseline_hit@10": b["baseline_hit@10"],
                "baseline_hit@50": b["baseline_hit@50"],
                "dense_rank": drank,
                "dense_hit@1": int(drank <= 1),
                "dense_hit@5": int(drank <= 5),
                "dense_hit@10": int(drank <= 10),
                "dense_hit@50": int(drank <= 50),
                "dense_gold_similarity": round(float(d["gold_similarity"]), 6),
                "dense_rank1_similarity": round(float(d["rank1_similarity"]), 6),
                "dense_rank1_doc_id": d["rank1_doc_id"],
                "dense_recovered_baseline_miss50": int(b["baseline_hit@50"] == 0 and drank <= 50),
                "dense_lost_baseline_hit50": int(b["baseline_hit@50"] == 1 and drank > 50),
                "dense_recovered_baseline_miss5": int(b["baseline_hit@5"] == 0 and drank <= 5),
                "dense_lost_baseline_hit5": int(b["baseline_hit@5"] == 1 and drank > 5),
                "dense_fail_side": fail_side(drank),
                "room_cat1": int(r["query_id"] in ROOM_CAT1),
                "vocab_control": int(r["query_id"] in VOCAB_CONTROLS),
            }
            if row["r2_primary"] == "":
                row["r2_primary"] = "SUCCESS" if b["baseline_hit@5"] else ("RANK" if b["baseline_hit@50"] else "UNKNOWN")
            per_rows.append(row)
            w.writerow(row)

    roman_dense_ranks = [int(results_pass1[i]["gold_rank"]) for i in roman_idx]
    dense_m = kn_metrics(roman_dense_ranks)
    base_m = kn_metrics([baseline[kn_rows[i]["query_id"]]["baseline_rank"] for i in roman_idx])

    def transition(k: int) -> dict:
        hh = hm = mh = mm = 0
        for row in per_rows:
            bh = row["baseline_rank"] != "" and int(row["baseline_rank"] or 999) <= k if row["baseline_rank"] != "" else False
            # baseline_hit already stored
            key = "baseline_hit@%s" % k if k in (1, 5, 10, 50) else None
            if key:
                bh = bool(row[key])
            dh = row["dense_rank"] <= k
            if bh and dh:
                hh += 1
            elif bh and not dh:
                hm += 1
            elif (not bh) and dh:
                mh += 1
            else:
                mm += 1
        return {
            "hit_hit": hh,
            "hit_miss": hm,
            "miss_hit": mh,
            "miss_miss": mm,
            "n": hh + hm + mh + mm,
            "recovered": mh,
            "regressed": hm,
        }

    trans5 = transition(5)
    trans50 = transition(50)

    # Taxonomy comparison (frozen labels; SUCCESS for R2-B0 Hit@5).
    by_cat = defaultdict(list)
    for row in per_rows:
        cat = row["r2_primary"] or "UNKNOWN"
        by_cat[cat].append(row)

    def cat_block(rows: list[dict]) -> dict:
        n = len(rows)
        b50 = sum(int(r["baseline_hit@50"]) for r in rows)
        d50 = sum(int(r["dense_hit@50"]) for r in rows)
        rec = sum(int(r["dense_recovered_baseline_miss50"]) for r in rows)
        reg = sum(int(r["dense_lost_baseline_hit50"]) for r in rows)
        b5 = sum(int(r["baseline_hit@5"]) for r in rows)
        d5 = sum(int(r["dense_hit@5"]) for r in rows)
        return {
            "n": n,
            "baseline_hit@50": b50,
            "dense_hit@50": d50,
            "recovered_hit@50": rec,
            "regressed_hit@50": reg,
            "baseline_hit@5": b5,
            "dense_hit@5": d5,
        }

    cat_table = {cat: cat_block(rows) for cat, rows in sorted(by_cat.items())}
    room1_rows = [r for r in per_rows if r["query_id"] in ROOM_CAT1]
    vocab_rows = [r for r in per_rows if r["query_id"] in VOCAB_CONTROLS]
    other_rows = [r for r in per_rows if r["r2_primary"] not in ("ROOM", "ENT", "VOCAB")]

    # Script strata for all KN TRAIN/DEV.
    script_metrics = {}
    for script in ("URDU", "ROMAN", "MIXED", "OTHER"):
        idxs = [i for i, r in enumerate(kn_rows) if r["script"] == script]
        script_metrics[script] = kn_metrics(
            [int(results_pass1[i]["gold_rank"]) for i in idxs]
        ) if idxs else {"n": 0}

    # Mechanical dense failure split on Roman n=51.
    n_hit5 = dense_m["hit@5_n"]
    n_rank = sum(1 for rk in roman_dense_ranks if 5 < rk <= 50)
    n_miss = sum(1 for rk in roman_dense_ranks if rk > 50)

    b_hit50 = [int(r["baseline_hit@50"]) for r in per_rows]
    d_hit50 = [int(r["dense_hit@50"]) for r in per_rows]
    b_hit5 = [int(r["baseline_hit@5"]) for r in per_rows]
    d_hit5 = [int(r["dense_hit@5"]) for r in per_rows]
    # McNemar: b = baseline 1 dense 0; c = baseline 0 dense 1
    def discord(bhits, dhits):
        b = sum(1 for x, y in zip(bhits, dhits) if x == 1 and y == 0)
        c = sum(1 for x, y in zip(bhits, dhits) if x == 0 and y == 1)
        return b, c, mcnemar_exact(b, c)

    disc50 = discord(b_hit50, d_hit50)
    disc5 = discord(b_hit5, d_hit5)

    import psutil  # optional

    mem_mb = None
    try:
        proc = psutil.Process(os.getpid())
        mem_mb = round(proc.memory_info().rss / (1024 * 1024), 1)
    except Exception:
        try:
            import resource
            mem_mb = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1)
        except Exception:
            mem_mb = None

    summary = {
        "experiment_id": "DENSE-BASELINE",
        "timestamp_utc": utc_now(),
        "test_accessed": False,
        "nl_evaluation": "pending official pooled annotation; not scored",
        "model": {
            "id": dr.MODEL_ID,
            "revision": dr.MODEL_REVISION,
            "dim": dr.EMBED_DIM,
            "max_seq_length": dr.MAX_SEQ_LENGTH,
            "prefix_mode": enc_info["prefix_mode"],
        },
        "data": pop,
        "baseline_frozen": FROZEN_BASELINE,
        "baseline_reproduced_from_artifact": base_m,
        "metrics_roman_kn_traindev": dense_m,
        "metrics_roman_kn_train": kn_metrics(
            [int(results_pass1[i]["gold_rank"]) for i, r in enumerate(kn_rows) if r["script"] == "ROMAN" and r["split"] == "train"]
        ),
        "metrics_roman_kn_dev": kn_metrics(
            [int(results_pass1[i]["gold_rank"]) for i, r in enumerate(kn_rows) if r["script"] == "ROMAN" and r["split"] == "dev"]
        ),
        "metrics_kn_by_script": script_metrics,
        "dense_mechanical": {
            "hit@5": n_hit5,
            "rank_in50_out5": n_rank,
            "miss50": n_miss,
            "n": 51,
        },
        "transition_top5": trans5,
        "transition_top50": trans50,
        "taxonomy": cat_table,
        "room_cat1": {
            "ids": ROOM_CAT1,
            "n": len(room1_rows),
            **cat_block(room1_rows),
            "per_query": [
                {
                    "query_id": r["query_id"],
                    "dense_rank": r["dense_rank"],
                    "dense_hit@50": r["dense_hit@50"],
                    "baseline_hit@50": r["baseline_hit@50"],
                }
                for r in room1_rows
            ],
        },
        "vocab_controls": {
            "ids": VOCAB_CONTROLS,
            "n": len(vocab_rows),
            **cat_block(vocab_rows),
            "per_query": [
                {
                    "query_id": r["query_id"],
                    "dense_rank": r["dense_rank"],
                    "dense_hit@50": r["dense_hit@50"],
                    "dense_hit@5": r["dense_hit@5"],
                    "rank1_doc_id": r["dense_rank1_doc_id"],
                    "note": "VOCAB negative control; do not claim as romanization recovery",
                }
                for r in vocab_rows
            ],
        },
        "other_categories_collapsed": cat_block(other_rows),
        "mcnemar_exact": {
            "hit@50_baseline_hit_dense_miss": disc50[0],
            "hit@50_baseline_miss_dense_hit": disc50[1],
            "hit@50_p": round(disc50[2], 6),
            "hit@5_baseline_hit_dense_miss": disc5[0],
            "hit@5_baseline_miss_dense_hit": disc5[1],
            "hit@5_p": round(disc5[2], 6),
            "note": "n=51; p-values are descriptive only",
        },
        "reproducibility": {
            "second_query_encode_rank_identity": rank_identity,
            "second_query_encode_allclose_1e-6": bool(__import__("numpy").allclose(q_vecs, q_vecs2, atol=1e-6)),
            "second_query_embed_seconds": round(q2_sec, 3),
        },
        "runtime": {
            "index_or_load_seconds": round(index_sec, 2),
            "query_embed_seconds": round(q_embed_sec, 3),
            "search_seconds": round(search_sec, 3),
            "rss_mb": mem_mb,
            "device": "cpu",
            "cuda": False,
        },
        "safety": {
            "test_accessed": False,
            "frozen_m0_modified": False,
            "plos_modified": False,
            "historical_r2_modified": False,
            "query_tuning": False,
            "model_shopping": False,
            "parameter_tuning": False,
            "hybrid": False,
            "reranking": False,
            "gold_injection": False,
            "data_leakage_detected": False,
        },
    }
    with open(os.path.join(ART, "dense_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
        f.write("\n")

    # All-KN ranks (secondary) — not mixed into primary n=51 table.
    kn_all_path = os.path.join(ART, "dense_kn_all_scripts_per_query.csv")
    with open(kn_all_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["query_id", "split", "script", "source_doc_id", "dense_rank", "dense_hit@5", "dense_hit@50", "gold_similarity"],
        )
        w.writeheader()
        for r, d in zip(kn_rows, results_pass1):
            w.writerow({
                "query_id": r["query_id"],
                "split": r["split"],
                "script": r["script"],
                "source_doc_id": r["source_doc_id"],
                "dense_rank": d["gold_rank"],
                "dense_hit@5": int(d["gold_rank"] <= 5),
                "dense_hit@50": int(d["gold_rank"] <= 50),
                "gold_similarity": round(float(d["gold_similarity"]), 6),
            })

    print("PRIMARY Roman KN n=51", dense_m, flush=True)
    print("ROOM Cat1 Hit@50", summary["room_cat1"]["dense_hit@50"], "/", summary["room_cat1"]["n"], flush=True)
    print("transition@50", trans50, flush=True)
    print("EVALUATION COMPLETE", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
