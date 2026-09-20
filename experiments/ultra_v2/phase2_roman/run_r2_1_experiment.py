# -*- coding: utf-8 -*-
"""R2-1: controlled document-side fallback romanization experiment.

TRAIN/DEV Roman KN only. Does not access TEST. Does not edit M0, dictionary,
R2-B0 artifacts, or R2-C0 artifacts. Query side unchanged.

CONTROL: Method D romanize_token (reverse-dict first key else naive_roman_word)
TREATMENT: same reverse-dict first key else hunterian_ascii_positional_v1
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
EXPECTED_BASELINE = {
    "n": 51,
    "hit@1_n": 1,
    "hit@5_n": 4,
    "hit@10_n": 4,
    "hit@50_n": 6,
    "mrr": 0.0375,
}
NEGATIVE_CONTROLS = ("KN017", "KN020", "KN041")
GENERIC_DIAGNOSTIC = [
    "پاکستان", "حکومت", "کراچی", "اخبار", "دوست", "کتاب", "وقت", "وزیر",
    "اور", "ہے", "میں", "دو", "ہو", "ایک", "یہ", "وہ", "کام", "لوگ",
]

sys.path.insert(0, P5)
sys.path.insert(0, _DIR)
import run_phase5 as p5  # noqa: E402
import fallback_roman_v1 as fb  # noqa: E402


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(1024 * 1024)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def refuse_test_path(path: str) -> None:
    ap = os.path.abspath(path)
    if ap == TEST_DIR or ap.startswith(TEST_DIR + os.sep):
        raise SystemExit("REFUSED: TEST path is forbidden for R2-1: %s" % ap)


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
                det = p5.detect_script(text)
                if det != "ROMAN":
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


def load_b0_ranks() -> dict[str, dict]:
    refuse_test_path(B0_PER)
    out = {}
    with open(B0_PER, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            out[r["query_id"]] = r
    return out


def load_c0_rows() -> dict[str, dict]:
    refuse_test_path(C0_CSV)
    out = {}
    with open(C0_CSV, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            out[r["query_id"]] = r
    return out


def room_category_1_ids(c0: dict[str, dict]) -> list[str]:
    ids = [
        qid for qid, r in c0.items()
        if r.get("primary") == "ROOM" and str(r.get("cand_cat")) == "1"
    ]
    ids.sort()
    if len(ids) != 11:
        raise SystemExit("R2-C0 ROOM Category 1 must have n=11, got %s %s" % (len(ids), ids))
    return ids


def control_romanize(tok: str, rev: dict) -> str:
    return p5.romanize_token(tok, rev)


def treatment_romanize(tok: str, rev: dict) -> tuple[str, str]:
    """Return (latin, path) with path in {dict, fallback, latin}."""
    if p5.has_urdu(tok):
        lat = rev.get(tok)
        if lat:
            return lat.lower(), "dict"
        return fb.fallback_roman(tok), "fallback"
    return tok.lower(), "latin"


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


def slice_ranks(rows: list[dict], ranks: list[int], split: str | None) -> list[int]:
    if split is None:
        return ranks
    return [rk for r, rk in zip(rows, ranks) if r["split"] == split]


def main() -> int:
    print("R2-1 CONTROLLED FALLBACK ROMANIZATION", flush=True)
    print("H1: replacing only document-side fallback romanization increases ROOM Category 1 Hit@50", flush=True)
    print("TEST_accessed: no", flush=True)

    assert p5.BM25_K1 == 1.5
    assert p5.BM25_B == 0.75
    assert TOP_K == 50
    assert HIT_K == 5
    rom_src = open(os.path.join(_DIR, "fallback_roman_v1.py"), encoding="utf-8").read()
    for banned in ("KN001", "KN017", "QTRN", "K001", "U001"):
        if banned in rom_src:
            raise SystemExit("STOP: benchmark identifier %s found in romanizer" % banned)

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
        raise SystemExit("expected 51 Roman KN TRAIN+DEV, got %s" % len(rows))
    b0 = load_b0_ranks()
    c0 = load_c0_rows()
    room1 = room_category_1_ids(c0)
    gold_ids = {r["source_doc_id"] for r in rows}

    fwd = p5.load_roman_dict()
    rev = p5.load_reverse_roman(fwd)
    assert len(fwd) == 198

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

    # Pre-retrieval romanizer diagnostic: generic linguistic list + corpus
    # documents at fixed offsets that are not KN gold sources.
    diag_docs = []
    for idx in (0, 250, 2500, 25000, 50000):
        if 0 <= idx < n_docs and idx not in gold_ids:
            toks = p5.tokenize(texts[idx])[:12]
            diag_docs.append({"doc_index": idx, "tokens": toks})
    diag_rows = []
    for w in GENERIC_DIAGNOSTIC:
        ctrl = p5.naive_roman_word(w)
        tr = fb.fallback_roman(w)
        diag_rows.append({"token": w, "control_fallback": ctrl, "treatment_fallback": tr, "changed": ctrl != tr})
    for block in diag_docs:
        for w in block["tokens"]:
            if not p5.has_urdu(w):
                continue
            if w in rev:
                continue
            ctrl = p5.naive_roman_word(w)
            tr = fb.fallback_roman(w)
            diag_rows.append({
                "token": w,
                "control_fallback": ctrl,
                "treatment_fallback": tr,
                "changed": ctrl != tr,
                "doc_index": block["doc_index"],
            })
    # determinism
    for w in GENERIC_DIAGNOSTIC:
        if fb.fallback_roman(w) != fb.fallback_roman(w):
            raise SystemExit("nondeterministic romanizer")
    empty_diag = sum(1 for r in diag_rows if r["token"] and not r["treatment_fallback"])
    diag_path = os.path.join(ART, "r2_1_romanizer_diagnostic.json")
    os.makedirs(ART, exist_ok=True)
    with open(diag_path, "w", encoding="utf-8") as f:
        json.dump({
            "romanizer": fb.romanizer_config(),
            "generic_n": len(GENERIC_DIAGNOSTIC),
            "empty_treatment_outputs": empty_diag,
            "n_compared": len(diag_rows),
            "n_changed": sum(1 for r in diag_rows if r["changed"]),
            "rows": diag_rows[:80],
        }, f, ensure_ascii=False, indent=2)
    print("diagnostic wrote", diag_path, "changed", sum(1 for r in diag_rows if r["changed"]), flush=True)

    control_bm25 = None
    if os.path.isfile(B0_CACHE):
        print("loading frozen R2-B0 index cache for CONTROL (read-only)...", flush=True)
        with open(B0_CACHE, "rb") as f:
            blob = pickle.load(f)
        cache_meta = blob.get("meta") or {}
        want_meta = {
            "corpus_sha256": corpus_sha,
            "dict_sha256": dict_sha,
            "k1": 1.5,
            "b": 0.75,
            "tokenizer": p5.TOKEN_RE.pattern,
        }
        if cache_meta != want_meta:
            print("index cache meta mismatch; CONTROL will be rebuilt in memory (not written to R2-B0 files)", flush=True)
        else:
            control_bm25 = blob["roman_bm25"]
            print("CONTROL cache hit", flush=True)

    print("tokenize + treatment romanize...", flush=True)
    t0 = time.perf_counter()
    control_gold: dict[int, list[str]] = {}
    gold_needed = {r["source_doc_id"] for r in rows}
    treatment_docs: list[list[str]] = []
    stats = Counter()
    fallback_out_ctrl: Counter[str] = Counter()
    fallback_out_trt: Counter[str] = Counter()
    len_ctrl = []
    len_trt = []
    dict_mismatch = 0
    for i, text in enumerate(texts):
        utoks = p5.tokenize(text)
        ctoks = []
        ttoks = []
        for tok in utoks:
            c = control_romanize(tok, rev)
            t, path = treatment_romanize(tok, rev)
            stats[path] += 1
            stats["total"] += 1
            if path == "dict":
                if t != (rev.get(tok) or "").lower():
                    dict_mismatch += 1
                expected_c = (rev.get(tok) or "").lower()
                if c != expected_c:
                    dict_mismatch += 1
            if path == "fallback":
                fallback_out_ctrl[c] += 1
                fallback_out_trt[t] += 1
                if c:
                    len_ctrl.append(len(c))
                if t:
                    len_trt.append(len(t))
                if c != t:
                    stats["fallback_changed"] += 1
                if not t:
                    stats["treatment_empty_fallback"] += 1
            if c:
                ctoks.append(c)
            if t:
                ttoks.append(t)
        if i in gold_needed:
            control_gold[i] = ctoks
        treatment_docs.append(ttoks)
        if (i + 1) % 20000 == 0:
            print("  tokenize %s/%s" % (i + 1, n_docs), flush=True)
    if dict_mismatch:
        raise SystemExit("reverse-dictionary path diverged: %s" % dict_mismatch)
    tokenize_sec = time.perf_counter() - t0
    print("tokenize %.1fs fallback_changed=%s" % (tokenize_sec, stats["fallback_changed"]), flush=True)

    if control_bm25 is None:
        print("rebuild CONTROL BM25 in memory (will not write r2_b0 artifacts)...", flush=True)
        rebuild_control_docs = []
        for text in texts:
            utoks = p5.tokenize(text)
            rebuild_control_docs.append([t for t in (p5.romanize_token(tok, rev) for tok in utoks) if t])
        control_bm25 = p5.BM25(rebuild_control_docs, k1=1.5, b=0.75)
        del rebuild_control_docs
    print("build TREATMENT BM25...", flush=True)
    t2 = time.perf_counter()
    treatment_bm25 = p5.BM25(treatment_docs, k1=1.5, b=0.75)
    print("treatment %.1fs" % (time.perf_counter() - t2), flush=True)

    # Baseline reproduction against expected totals and frozen R2-B0 per-query ranks
    control_ranks = []
    treatment_ranks = []
    per = []
    for r in rows:
        qtoks = p5.tokenize(r["query_text"])
        chits = control_bm25.search(qtoks, top_k=TOP_K)
        thits = treatment_bm25.search(qtoks, top_k=TOP_K)
        cr = p5.rank_of(chits, r["source_doc_id"])
        tr = p5.rank_of(thits, r["source_doc_id"])
        control_ranks.append(cr)
        treatment_ranks.append(tr)
        b0r = b0[r["query_id"]]
        b0_rank = 999 if b0r["gold_rank"] == "" else int(b0r["gold_rank"])
        if cr != b0_rank:
            raise SystemExit(
                "BASELINE MISMATCH %s reproduced_rank=%s r2_b0_rank=%s STOP"
                % (r["query_id"], cr, b0_rank)
            )
        c0r = c0[r["query_id"]]
        primary = c0r.get("primary") or ("SUCCESS" if int(b0r["hit@5"]) else "")
        cand_cat = c0r.get("cand_cat")
        gold_c = set(control_gold[r["source_doc_id"]])
        gold_t = set(treatment_docs[r["source_doc_id"]])
        qset = set(qtoks)
        rec = int(cr > TOP_K and tr <= TOP_K)
        reg = int(cr <= TOP_K and tr > TOP_K)
        if cr > TOP_K and tr > TOP_K:
            cand_change = "unchanged_miss"
        elif cr <= TOP_K and tr <= TOP_K:
            if tr < cr:
                cand_change = "rank_improvement"
            elif tr > cr:
                cand_change = "rank_regression"
            else:
                cand_change = "unchanged_rank"
        elif rec:
            cand_change = "recovered"
        else:
            cand_change = "regressed"
        per.append({
            "query_id": r["query_id"],
            "split": r["split"],
            "script": "ROMAN",
            "category": primary,
            "r2c0_cand_cat": cand_cat,
            "source_doc_id": r["source_doc_id"],
            "baseline_rank": cr if cr < 999 else "",
            "treatment_rank": tr if tr < 999 else "",
            "baseline_hit1": int(cr <= 1),
            "treatment_hit1": int(tr <= 1),
            "baseline_hit5": int(cr <= 5),
            "treatment_hit5": int(tr <= 5),
            "baseline_hit10": int(cr <= 10),
            "treatment_hit10": int(tr <= 10),
            "baseline_hit50": int(cr <= 50),
            "treatment_hit50": int(tr <= 50),
            "baseline_mrr": round(0.0 if cr >= 999 else 1.0 / cr, 6),
            "treatment_mrr": round(0.0 if tr >= 999 else 1.0 / tr, 6),
            "gold_candidate_baseline": int(cr <= TOP_K),
            "gold_candidate_treatment": int(tr <= TOP_K),
            "recovered": rec,
            "regressed": reg,
            "cand_change": cand_change,
            "baseline_overlap": len(qset & gold_c),
            "treatment_overlap": len(qset & gold_t),
            "overlap_delta": len(qset & gold_t) - len(qset & gold_c),
            "new_matching_terms": " ".join(sorted((qset & gold_t) - gold_c)),
            "lost_matching_terms": " ".join(sorted((qset & gold_c) - gold_t)),
        })

    ctrl_all = kn_metrics(control_ranks)
    if (
        ctrl_all["n"] != EXPECTED_BASELINE["n"]
        or ctrl_all["hit@1_n"] != EXPECTED_BASELINE["hit@1_n"]
        or ctrl_all["hit@5_n"] != EXPECTED_BASELINE["hit@5_n"]
        or ctrl_all["hit@10_n"] != EXPECTED_BASELINE["hit@10_n"]
        or ctrl_all["hit@50_n"] != EXPECTED_BASELINE["hit@50_n"]
        or ctrl_all["mrr"] != EXPECTED_BASELINE["mrr"]
    ):
        raise SystemExit("BASELINE METRIC MISMATCH reproduced=%s expected=%s" % (ctrl_all, EXPECTED_BASELINE))
    print("baseline reproduction: PASS", ctrl_all, flush=True)

    trt_all = kn_metrics(treatment_ranks)
    train_c = kn_metrics(slice_ranks(rows, control_ranks, "train"))
    train_t = kn_metrics(slice_ranks(rows, treatment_ranks, "train"))
    dev_c = kn_metrics(slice_ranks(rows, control_ranks, "dev"))
    dev_t = kn_metrics(slice_ranks(rows, treatment_ranks, "dev"))

    def subset_hit50(ids: list[str], ranks: list[int]) -> dict:
        id_to_rank = {r["query_id"]: rk for r, rk in zip(rows, ranks)}
        rs = [id_to_rank[i] for i in ids]
        n = len(rs)
        h = sum(1 for x in rs if x <= TOP_K)
        return {"n": n, "hit@50_n": h, "hit@50": round(h / n if n else 0.0, 4)}

    room1_c = subset_hit50(room1, control_ranks)
    room1_t = subset_hit50(room1, treatment_ranks)

    recovered = [p for p in per if p["recovered"]]
    regressed = [p for p in per if p["regressed"]]
    hit50_improved = sum(1 for p in per if p["treatment_hit50"] > p["baseline_hit50"])
    hit50_regressed = sum(1 for p in per if p["treatment_hit50"] < p["baseline_hit50"])
    hit50_unchanged = 51 - hit50_improved - hit50_regressed
    mcnemar_all = exact_mcnemar(hit50_improved, hit50_regressed)

    room1_imp = sum(1 for p in per if p["query_id"] in room1 and p["treatment_hit50"] > p["baseline_hit50"])
    room1_reg = sum(1 for p in per if p["query_id"] in room1 and p["treatment_hit50"] < p["baseline_hit50"])
    mcnemar_room1 = exact_mcnemar(room1_imp, room1_reg)

    by_cat: dict[str, dict] = {}
    for p in per:
        cat = p["category"]
        d = by_cat.setdefault(cat, {"n": 0, "b_hit50": 0, "t_hit50": 0, "b_hit5": 0, "t_hit5": 0, "recovered": 0, "regressed": 0})
        d["n"] += 1
        d["b_hit50"] += p["baseline_hit50"]
        d["t_hit50"] += p["treatment_hit50"]
        d["b_hit5"] += p["baseline_hit5"]
        d["t_hit5"] += p["treatment_hit5"]
        d["recovered"] += p["recovered"]
        d["regressed"] += p["regressed"]

    neg = {}
    for qid in NEGATIVE_CONTROLS:
        row = next(p for p in per if p["query_id"] == qid)
        neg[qid] = {
            "category": row["category"],
            "baseline_rank": row["baseline_rank"],
            "treatment_rank": row["treatment_rank"],
            "baseline_hit50": row["baseline_hit50"],
            "treatment_hit50": row["treatment_hit50"],
            "overlap_delta": row["overlap_delta"],
        }

    # remaining ROOM cat1 failures
    room1_remain = [
        p["query_id"] for p in per
        if p["query_id"] in room1 and not p["treatment_hit50"]
    ]
    room1_recovered = [p["query_id"] for p in per if p["query_id"] in room1 and p["recovered"]]

    git_branch = "research/ultra-v2-strengthening"
    git_commit = "fd54ac9b65c2db93e7e16fbf0c5a40b6a6025be1"

    code_hash = sha256_file(os.path.join(_DIR, "run_r2_1_experiment.py"))
    romanizer_hash = sha256_file(os.path.join(_DIR, "fallback_roman_v1.py"))

    hasher = hashlib.sha256()
    n_tok = 0
    for doc in treatment_docs:
        line = " ".join(doc) + "\n"
        hasher.update(line.encode("utf-8"))
        n_tok += len(doc)
    rep_hash = hasher.hexdigest()
    rep_manifest = {
        "experiment_id": "R2-1",
        "corpus": "data/clean_articles.csv",
        "n_docs": n_docs,
        "n_treatment_tokens": n_tok,
        "tokenizer": p5.TOKEN_RE.pattern,
        "romanizer": fb.romanizer_config(),
        "dict_sha256": dict_sha,
        "corpus_sha256": corpus_sha,
        "canonical_form": "utf-8 lines of space-joined tokens, one document per line, SHA-256 of that byte stream",
        "representation_sha256": rep_hash,
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    rep_path = os.path.join(ART, "r2_1_representation_manifest.json")
    with open(rep_path, "w", encoding="utf-8") as f:
        json.dump(rep_manifest, f, indent=2)

    mean = lambda xs: round(sum(xs) / len(xs), 4) if xs else None
    total = max(stats["total"], 1)
    attribution = {
        "total_tokens": stats["total"],
        "dictionary_first_key_tokens": stats["dict"],
        "fallback_tokens": stats["fallback"],
        "latin_tokens": stats["latin"],
        "pct_fallback": round(100.0 * stats["fallback"] / total, 4),
        "pct_dictionary": round(100.0 * stats["dict"] / total, 4),
        "fallback_changed_vs_control": stats["fallback_changed"],
        "unique_fallback_outputs_control": len(fallback_out_ctrl),
        "unique_fallback_outputs_treatment": len(fallback_out_trt),
        "treatment_empty_fallback": stats["treatment_empty_fallback"],
        "avg_fallback_len_control": mean(len_ctrl),
        "avg_fallback_len_treatment": mean(len_trt),
        "reverse_dict_mismatches": 0,
    }

    primary = {
        "metric": "Hit@50 on R2-C0 ROOM Category 1",
        "room_category_1_ids": room1,
        "baseline": room1_c,
        "treatment": room1_t,
        "absolute_change_n": room1_t["hit@50_n"] - room1_c["hit@50_n"],
        "absolute_change_pp": round(100.0 * (room1_t["hit@50"] - room1_c["hit@50"]), 2),
        "newly_recovered": room1_recovered,
        "regressions": [p["query_id"] for p in per if p["query_id"] in room1 and p["regressed"]],
        "remaining_failures": room1_remain,
    }

    config = {
        "experiment_id": "R2-1",
        "experiment_name": "Controlled document-side fallback Roman representation",
        "git_branch": git_branch,
        "git_commit": git_commit,
        "dataset_split": "TRAIN+DEV Roman KN only",
        "benchmark_version": "ultra-v2-benchmark-v0",
        "test_status": "NOT ACCESSED",
        "dictionary_path": "models/roman_urdu_dict_expanded.json",
        "dictionary_sha256": dict_sha,
        "corpus_sha256": corpus_sha,
        "bm25_k1": 1.5,
        "bm25_b": 0.75,
        "candidate_depth": 50,
        "official_cutoff": 5,
        "query_representation": "tokenize(query) as typed; unchanged",
        "document_representation_control": "romanize_token: reverse-dict first key else naive_roman_word",
        "document_representation_treatment": "reverse-dict first key else hunterian_ascii_positional_v1",
        "fallback_romanizer": fb.romanizer_config(),
        "random_seed": None,
        "primary_metric": "Hit@50 on R2-C0 ROOM Category 1 (n=11)",
        "negative_controls": list(NEGATIVE_CONTROLS),
        "code_hashes": {
            "run_r2_1_experiment.py": code_hash,
            "fallback_roman_v1.py": romanizer_hash,
        },
        "representation_artifact": os.path.relpath(rep_path, ROOT).replace("\\", "/"),
        "representation_artifact_sha256": rep_hash,
        "test_accessed": False,
        "m0_edited": False,
        "dictionary_edited": False,
        "r2_b0_outputs_written": False,
        "r2_c0_outputs_written": False,
    }

    summary = {
        "experiment_id": "R2-1",
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "test_accessed": False,
        "baseline_reproduction": "PASS",
        "hypothesis": (
            "Replacing only the current document-side fallback romanization with a "
            "deterministic principled Latin/Roman representation will increase "
            "gold-document candidate inclusion for Roman Urdu KN queries, especially "
            "ROOM Category 1 failures, without changing query representation, routing, "
            "BM25 parameters, dictionary behavior, or benchmark data."
        ),
        "control_metrics": {"train": train_c, "dev": dev_c, "train+dev": ctrl_all},
        "treatment_metrics": {"train": train_t, "dev": dev_t, "train+dev": trt_all},
        "primary": primary,
        "category_analysis": by_cat,
        "negative_controls": neg,
        "candidate_generation": {
            "recovered": [p["query_id"] for p in recovered],
            "regressed": [p["query_id"] for p in regressed],
            "hit50_improved": hit50_improved,
            "hit50_unchanged": hit50_unchanged,
            "hit50_regressed": hit50_regressed,
            "net_hit50_n": trt_all["hit@50_n"] - ctrl_all["hit@50_n"],
        },
        "mcnemar_hit50_all": mcnemar_all,
        "mcnemar_hit50_room_cat1": mcnemar_room1,
        "representation_attribution": attribution,
        "tokenize_sec": round(tokenize_sec, 2),
        "n_docs": n_docs,
    }

    with open(os.path.join(ART, "r2_1_config.json"), "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
    with open(os.path.join(ART, "r2_1_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    with open(os.path.join(ART, "r2_1_representation_stats.json"), "w", encoding="utf-8") as f:
        json.dump(attribution, f, indent=2)
    out_csv = os.path.join(_DIR, "R2_1_PER_QUERY.csv")
    fields = list(per[0].keys())
    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(per)

    print("PRIMARY ROOM cat1 Hit@50", room1_c, "->", room1_t, flush=True)
    print("TRAIN+DEV control", ctrl_all, "treatment", trt_all, flush=True)
    print("recovered", [p["query_id"] for p in recovered], flush=True)
    print("regressed", [p["query_id"] for p in regressed], flush=True)
    print("negative", neg, flush=True)
    print("mcnemar_all", mcnemar_all, flush=True)
    print("status: R2-1 RETRIEVAL DONE", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
