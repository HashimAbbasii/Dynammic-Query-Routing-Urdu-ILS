# -*- coding: utf-8 -*-
"""Phase 13 Step 3 — confirmatory scoring on frozen Roman KN n=80.

Reuses frozen method modules/parameters. Writes ONLY under phase13_population/.
Does not overwrite Phase 2–12 artifacts. Does not open TEST.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import pickle
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "experiments" / "phase5_roman_urdu"))
sys.path.insert(0, str(ROOT / "experiments" / "ultra_v2" / "phase2_roman"))
sys.path.insert(0, str(ROOT / "experiments" / "ultra_v2" / "phase3_dense"))
sys.path.insert(0, str(ROOT / "experiments" / "ultra_v2" / "phase4_hybrid"))
sys.path.insert(0, str(ROOT / "experiments" / "ultra_v2" / "phase9_entity_resource"))
sys.path.insert(0, str(ROOT / "experiments" / "ultra_v2" / "phase10_cascade"))

import run_phase5 as p5  # noqa: E402
import ng3_matching as ng3  # noqa: E402
import dense_retrieval as dr  # noqa: E402
import hybrid_fusion as hf  # noqa: E402
from match_rule import (  # noqa: E402
    tokenize as p9_tokenize,
    norm_en,
    match_spans,
    add_dotted_initialism_aliases,
    ur_token_key,
    load_common_english,
)
from cascade_b import option_b_fuse, gold_rank as cascade_gold_rank  # noqa: E402
from cascade_b10b import option_b10b_fuse  # noqa: E402

BENCH = ROOT / "experiments" / "ultra_v2" / "benchmark"
TEST_DIR = (BENCH / "test").resolve()
ART = Path(__file__).resolve().parent / "artifacts" / "scoring"
PREREG = Path(__file__).resolve().parent / "PHASE13_SCORING_PREREGISTRATION.md"
PREREG_SHA_FILE = Path(__file__).resolve().parent / "artifacts" / "phase13_scoring_prereg_sha256.txt"
EXPECTED_PREREG_SHA = "55788660c5d1f6d9d55399d82ed722733ab64097704fb23084fd77b1b39b912a"

B0_CACHE = ROOT / "experiments" / "ultra_v2" / "phase2_roman" / "artifacts" / "_index_cache.pkl"
DENSE_NPY = ROOT / "experiments" / "ultra_v2" / "phase3_dense" / "artifacts" / "dense_doc_embeddings.npy"
DENSE_META = ROOT / "experiments" / "ultra_v2" / "phase3_dense" / "artifacts" / "dense_index_meta.json"
TITLE_CSV = ROOT / "experiments" / "ultra_v2" / "phase9_entity_resource" / "artifacts" / "bilingual_titles.csv"

EXPECTED_DICT_SHA = "30c3f61a64ec641abbb3acdbc7a8bcaf197f0238f1bf9e76c2c7ce8e590f86a3"
EXPECTED_CORPUS_SHA = "8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231"
EXPECTED_TITLE_CSV_SHA = "7686f02d5bb2110eb4cccc7cdbd326324e4f7fa5e4dd34d7125a76d7795cf55d"
EXPECTED_MD_STREAM_SHA = "323a07b46e2377b5ec807006c2efd06f9b1ae19a65f1389d22f32b435ca0c3fb"
EXPECTED_NG3_STREAM_SHA = "1ab004bb26e9231827137020808ca008981648d62a834755af5779454d8c553d"

TOP_K = 50

# Frozen n=51 aggregates (prereg §4)
FROZEN_N51 = {
    "bm25": {"hit@1_n": 1, "hit@5_n": 4, "hit@10_n": 4, "hit@50_n": 6, "mrr": 0.0375},
    "dense": {"hit@1_n": 5, "hit@5_n": 15, "hit@10_n": 16, "hit@50_n": 22, "mrr": 0.1726},
    "ng3": {"hit@1_n": 3, "hit@5_n": 6, "hit@10_n": 6, "hit@50_n": 8, "mrr": 0.075},
    "hybrid": {"hit@1_n": 3, "hit@5_n": 11, "hit@10_n": 19, "hit@50_n": 25, "mrr": 0.1422},
    "phase9": {"hit@1_n": 1, "hit@5_n": 5, "hit@10_n": 6, "hit@50_n": 10, "mrr": 0.0478},
    "phase10": {"hit@1_n": 3, "hit@5_n": 11, "hit@10_n": 19, "hit@50_n": 24, "mrr": 0.1418},
    "phase10b": {"hit@1_n": 3, "hit@5_n": 11, "hit@10_n": 19, "hit@50_n": 25, "mrr": 0.1422},
}


def refuse_test(path: Path | str) -> None:
    p = Path(path).resolve()
    if p == TEST_DIR or TEST_DIR in p.parents or "benchmark\\test" in str(p).lower() or "benchmark/test" in str(p).replace("\\", "/"):
        raise SystemExit("REFUSED — TEST path: %s" % p)


def sha256_file(path: Path | str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(1024 * 1024)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def kn_metrics(ranks: list[int]) -> dict:
    n = len(ranks)
    def hit(k):
        return sum(1 for r in ranks if r <= k)
    mrr = 0.0
    for r in ranks:
        if r <= TOP_K:
            mrr += 1.0 / r
    return {
        "n": n,
        "hit@1_n": hit(1),
        "hit@1": round(hit(1) / n, 4) if n else 0.0,
        "hit@5_n": hit(5),
        "hit@5": round(hit(5) / n, 4) if n else 0.0,
        "hit@10_n": hit(10),
        "hit@10": round(hit(10) / n, 4) if n else 0.0,
        "hit@50_n": hit(50),
        "hit@50": round(hit(50) / n, 4) if n else 0.0,
        "mrr": round(mrr / n, 4) if n else 0.0,
    }


def metrics_match(obs: dict, exp: dict, tol: float = 1e-4) -> bool:
    for k in ("hit@1_n", "hit@5_n", "hit@10_n", "hit@50_n"):
        if int(obs[k]) != int(exp[k]):
            return False
    if abs(float(obs["mrr"]) - float(exp["mrr"])) > tol:
        return False
    return True


def load_roman_kn() -> list[dict]:
    rows = []
    for split in ("train", "dev"):
        path = BENCH / split / "queries_kn.csv"
        refuse_test(path)
        with path.open(encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f):
                if (r.get("script") or "").strip() != "ROMAN":
                    continue
                if p5.detect_script(r["query_text"]) != "ROMAN":
                    raise SystemExit("detector mismatch %s" % r["query_id"])
                rows.append({
                    "query_id": r["query_id"],
                    "query_text": r["query_text"],
                    "split": split,
                    "source_doc_id": int(r["source_doc_id"]),
                    "writer_id": (r.get("writer_id") or "").strip(),
                    "cohort": "phase13" if int(r["query_id"][2:]) >= 91 else "original",
                })
    return rows


def expand_p9_tokens(qtoks: list[str], hits: list[dict], rev: dict) -> list[str]:
    out = list(qtoks)
    for h in hits:
        for ur in h["ur_titles"]:
            for tok in p9_tokenize(ur):
                lat = p5.romanize_token(tok, rev)
                if lat:
                    out.append(lat)
    return out


def load_title_indexes(path: Path) -> tuple[dict, dict]:
    idx: dict = {}
    ur_key: dict = {}
    with path.open(encoding="utf-8", newline="") as f:
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
    add_dotted_initialism_aliases(idx)
    return idx, ur_key


def main() -> int:
    wall0 = time.perf_counter()
    ART.mkdir(parents=True, exist_ok=True)
    print("label: ULTRA v2 PHASE13-SCORING n=80", flush=True)
    print("TEST_accessed: no", flush=True)

    prereg_sha = sha256_file(PREREG)
    if prereg_sha != EXPECTED_PREREG_SHA:
        raise SystemExit("BLOCKED — prereg SHA mismatch got=%s" % prereg_sha)
    printed = PREREG_SHA_FILE.read_text(encoding="ascii").strip()
    if printed != EXPECTED_PREREG_SHA:
        raise SystemExit("BLOCKED — prereg sha file mismatch")

    refuse_test(p5.CORPUS)
    dict_sha = sha256_file(p5.DICT_PATH)
    corpus_sha = sha256_file(p5.CORPUS)
    if dict_sha != EXPECTED_DICT_SHA or corpus_sha != EXPECTED_CORPUS_SHA:
        raise SystemExit("BLOCKED — dict/corpus SHA")
    title_sha = sha256_file(TITLE_CSV)
    if title_sha != EXPECTED_TITLE_CSV_SHA:
        raise SystemExit("BLOCKED — title CSV SHA")

    rows = load_roman_kn()
    if len(rows) != 80:
        raise SystemExit("BLOCKED — expected 80 Roman KN, got %s" % len(rows))
    orig = [r for r in rows if r["cohort"] == "original"]
    new29 = [r for r in rows if r["cohort"] == "phase13"]
    if len(orig) != 51 or len(new29) != 29:
        raise SystemExit("BLOCKED — cohort sizes %s/%s" % (len(orig), len(new29)))
    ids80 = [r["query_id"] for r in rows]
    ids51 = [r["query_id"] for r in orig]
    ids29 = [r["query_id"] for r in new29]
    print("loaded roman KN n=80 (orig=%s new=%s)" % (len(orig), len(new29)), flush=True)

    # --- BM25 ---
    print("Method-D BM25...", flush=True)
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
    bm25_hits: dict[str, list] = {}
    ranks: dict[str, dict[str, int]] = {qid: {} for qid in ids80}
    for r in rows:
        qtoks = p5.tokenize(r["query_text"])
        hits = roman_bm25.search(qtoks, top_k=TOP_K)
        bm25_hits[r["query_id"]] = hits
        ranks[r["query_id"]]["bm25"] = p5.rank_of(hits, r["source_doc_id"])

    # --- Dense ---
    print("Dense e5-small (frozen doc matrix + query encode)...", flush=True)
    with open(DENSE_META, encoding="utf-8") as f:
        dmeta = json.load(f)
    if dmeta.get("complete") is not True or dmeta.get("corpus_sha256") != EXPECTED_CORPUS_SHA:
        raise SystemExit("BLOCKED — dense meta")
    doc_matrix = np.array(np.load(DENSE_NPY, mmap_mode="r"), dtype=np.float32, copy=True)
    model, enc_info = dr.load_encoder()
    q_vecs = dr.encode_texts(
        model,
        [r["query_text"] for r in rows],
        kind="query",
        prefix_mode=enc_info["prefix_mode"],
        prompt_name=enc_info.get("query_prompt_name"),
        show_progress=False,
    )
    dense_hits: dict[str, list] = {}
    for r, qv in zip(rows, q_vecs):
        res = dr.search_query_vec(doc_matrix, qv, r["source_doc_id"], k=TOP_K)
        dense_hits[r["query_id"]] = [(int(d), float(s)) for d, s in res["topk"]]
        ranks[r["query_id"]]["dense"] = int(res["gold_rank"])

    # --- Hybrid ---
    print("Hybrid RRF k=60...", flush=True)
    hybrid_hits: dict[str, list] = {}
    for r in rows:
        qid = r["query_id"]
        fused = hf.fuse_rrf(bm25_hits[qid], dense_hits[qid], k=hf.RRF_K)
        hybrid_hits[qid] = [(int(d), float(sc)) for d, sc, _a, _b in fused[:TOP_K]]
        gr = 999
        for i, tup in enumerate(fused[:TOP_K], 1):
            if int(tup[0]) == r["source_doc_id"]:
                gr = i
                break
        ranks[qid]["hybrid"] = gr

    # --- NG3 ---
    print("NG3 representation + BM25 (frozen stream SHA gate)...", flush=True)
    import pandas as pd
    df = pd.read_csv(p5.CORPUS, encoding="utf-8-sig")
    if "combined_text" in df.columns:
        texts = df["combined_text"].fillna("").astype(str).tolist()
    else:
        texts = (df["Headline"].fillna("").astype(str) + " " + df["News Text"].fillna("").astype(str)).tolist()
    if len(texts) != 111860:
        raise SystemExit("BLOCKED — n_docs")
    fwd = p5.load_roman_dict()
    rev = p5.load_reverse_roman(fwd)
    ng3_docs: list[list[str]] = []
    md_hasher = hashlib.sha256()
    ng3_hasher = hashlib.sha256()
    t0 = time.perf_counter()
    for i, text in enumerate(texts):
        utoks = p5.tokenize(text)
        md = [t for t in (p5.romanize_token(tok, rev) for tok in utoks) if t]
        feats = ng3.expand_tokens(md)
        ng3_docs.append(feats)
        md_hasher.update((" ".join(md) + "\n").encode("utf-8"))
        ng3_hasher.update((" ".join(feats) + "\n").encode("utf-8"))
        if (i + 1) % 20000 == 0:
            print("  ng3 tokenize %s/%s" % (i + 1, len(texts)), flush=True)
    if md_hasher.hexdigest() != EXPECTED_MD_STREAM_SHA or ng3_hasher.hexdigest() != EXPECTED_NG3_STREAM_SHA:
        raise SystemExit("BLOCKED — NG3 stream SHA mismatch")
    print("ng3 tokenize %.1fs" % (time.perf_counter() - t0), flush=True)
    ng3_bm25 = p5.BM25(ng3_docs, k1=1.5, b=0.75)
    ng3_hits: dict[str, list] = {}
    for r in rows:
        q3 = ng3.expand_tokens(p5.tokenize(r["query_text"]))
        nhits = ng3_bm25.search(q3, top_k=TOP_K)
        ng3_hits[r["query_id"]] = nhits
        ranks[r["query_id"]]["ng3"] = p5.rank_of(nhits, r["source_doc_id"])

    # --- Phase 9 ---
    print("Phase 9 title expansion...", flush=True)
    load_common_english()
    en_index, ur_index = load_title_indexes(TITLE_CSV)
    p9_hits: dict[str, list] = {}
    n_en: dict[str, int] = {}
    for r in rows:
        qid = r["query_id"]
        qtoks = p9_tokenize(r["query_text"])
        hits = match_spans(qtoks, en_index, ur_index)
        n_en[qid] = len(hits)
        exp = expand_p9_tokens(qtoks, hits, rev)
        phits = roman_bm25.search(exp, top_k=TOP_K)
        p9_hits[qid] = phits
        ranks[qid]["phase9"] = p5.rank_of(phits, r["source_doc_id"])

    # --- Phase 10 / 10b ---
    print("Phase 10 / 10b cascades...", flush=True)
    for r in rows:
        qid = r["query_id"]
        triggered = n_en[qid] >= 1
        p10 = option_b_fuse(hybrid_hits[qid], p9_hits[qid], ng3_hits[qid], triggered)
        p10b = option_b10b_fuse(hybrid_hits[qid], p9_hits[qid], ng3_hits[qid], triggered)
        rk = cascade_gold_rank(p10, r["source_doc_id"])
        rkb = cascade_gold_rank(p10b, r["source_doc_id"])
        ranks[qid]["phase10"] = rk if rk <= TOP_K else 999
        ranks[qid]["phase10b"] = rkb if rkb <= TOP_K else 999
        ranks[qid]["triggered"] = int(triggered)

    methods = ["bm25", "dense", "ng3", "hybrid", "phase9", "phase10", "phase10b"]

    def slice_metrics(id_list: list[str]) -> dict[str, dict]:
        out = {}
        for m in methods:
            out[m] = kn_metrics([ranks[q][m] for q in id_list])
        return out

    m80 = slice_metrics(ids80)
    m51 = slice_metrics(ids51)
    m29 = slice_metrics(ids29)

    # Consistency gate
    gate_ok = True
    gate_detail = {}
    for m, exp in FROZEN_N51.items():
        ok = metrics_match(m51[m], exp)
        gate_detail[m] = {"ok": ok, "observed": m51[m], "expected": exp}
        if not ok:
            gate_ok = False
            print("GATE FAIL", m, m51[m], "!=", exp, flush=True)
    if not gate_ok:
        blocked = {"decision": "BLOCKED", "reason": "n=51 subset mismatch vs frozen", "detail": gate_detail}
        (ART / "phase13_scoring_blocked.json").write_text(
            json.dumps(blocked, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        raise SystemExit("BLOCKED — n=51 consistency gate failed")
    print("GATE n=51 PASS for all methods", flush=True)

    # Per-query CSV
    pq_path = ART / "PHASE13_SCORING_PER_QUERY.csv"
    fields = [
        "query_id", "split", "cohort", "source_doc_id", "query_text", "triggered",
        "bm25_rank", "dense_rank", "ng3_rank", "hybrid_rank", "phase9_rank", "phase10_rank", "phase10b_rank",
    ]
    for m in methods:
        for k in (1, 5, 10, 50):
            fields.append("%s_hit@%s" % (m, k))
    with pq_path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            qid = r["query_id"]
            row = {
                "query_id": qid,
                "split": r["split"],
                "cohort": r["cohort"],
                "source_doc_id": r["source_doc_id"],
                "query_text": r["query_text"],
                "triggered": ranks[qid].get("triggered", 0),
            }
            for m in methods:
                rk = ranks[qid][m]
                row["%s_rank" % m] = rk if rk < 999 else ""
                for k in (1, 5, 10, 50):
                    row["%s_hit@%s" % (m, k)] = int(rk <= k)
            w.writerow(row)

    summary = {
        "experiment_id": "PHASE13-SCORING",
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "test_accessed": False,
        "preregistration_sha256": prereg_sha,
        "n_roman_kn": 80,
        "n_original": 51,
        "n_phase13": 29,
        "gates": {"n51_consistency": "PASS", "corpus_sha": "PASS", "dict_sha": "PASS", "ng3_stream_sha": "PASS"},
        "metrics_n80": m80,
        "metrics_n51_subset": m51,
        "metrics_n29_new": m29,
        "frozen_n51_expected": FROZEN_N51,
        "wall_sec": round(time.perf_counter() - wall0, 1),
        "method_disclosure": "n=29 LLM-drafted human-reviewed (LLM1); n=51 human-written (W1)",
        "retuning": False,
    }
    sum_path = ART / "phase13_scoring_summary.json"
    sum_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # SHA-256 outputs
    sha_map = {
        "PHASE13_SCORING_PER_QUERY.csv": sha256_file(pq_path),
        "phase13_scoring_summary.json": sha256_file(sum_path),
        "PHASE13_SCORING_PREREGISTRATION.md": prereg_sha,
    }
    (ART / "phase13_scoring_sha256.json").write_text(
        json.dumps(sha_map, indent=2) + "\n", encoding="utf-8"
    )

    # Human-readable report
    lines = [
        "# Phase 13 Scoring Report",
        "",
        "**Decision:** CONFIRMATORY COMPLETE (n=51 consistency PASS)",
        "**TEST accessed:** no",
        "**Retuning:** no",
        "",
        "## n=80 (full frozen population)",
        "",
        "| Method | Hit@1 | Hit@5 | Hit@10 | Hit@50 | MRR |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    labels = {
        "bm25": "Method-D BM25",
        "dense": "Dense e5-small",
        "ng3": "NG3",
        "hybrid": "Hybrid RRF",
        "phase9": "Phase 9",
        "phase10": "Phase 10 cascade",
        "phase10b": "Phase 10b",
    }
    for m in methods:
        x = m80[m]
        lines.append(
            "| %s | %s/%s | %s/%s | %s/%s | %s/%s | %.4f |"
            % (labels[m], x["hit@1_n"], x["n"], x["hit@5_n"], x["n"], x["hit@10_n"], x["n"], x["hit@50_n"], x["n"], x["mrr"])
        )
    lines += ["", "## n=51 subset (must = frozen)", ""]
    lines.append("| Method | Hit@1/5/10/50_n | MRR | vs frozen |")
    lines.append("|---|---|---:|---|")
    for m in methods:
        x = m51[m]
        e = FROZEN_N51[m]
        lines.append(
            "| %s | %s/%s/%s/%s | %.4f | MATCH |"
            % (labels[m], x["hit@1_n"], x["hit@5_n"], x["hit@10_n"], x["hit@50_n"], x["mrr"])
        )
    lines += ["", "## n=29 Phase-13-only (descriptive)", ""]
    lines.append("| Method | Hit@1 | Hit@5 | Hit@10 | Hit@50 | MRR |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for m in methods:
        x = m29[m]
        lines.append(
            "| %s | %s/%s | %s/%s | %s/%s | %s/%s | %.4f |"
            % (labels[m], x["hit@1_n"], x["n"], x["hit@5_n"], x["n"], x["hit@10_n"], x["n"], x["hit@50_n"], x["n"], x["mrr"])
        )
    lines += ["", "## SHA-256", ""]
    for k, v in sha_map.items():
        lines.append("- `%s`: `%s`" % (k, v))
    (ART / "PHASE13_SCORING_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps({"n80": {m: m80[m] for m in methods}, "n51_ok": True, "n29": {m: m29[m] for m in methods}}, indent=2), flush=True)
    print("done wall_sec=%.1f" % (time.perf_counter() - wall0), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
