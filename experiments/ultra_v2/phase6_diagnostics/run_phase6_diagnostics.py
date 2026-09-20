# -*- coding: utf-8 -*-
"""ULTRA v2 Phase 6 diagnostics. Read-only analysis of frozen per-query CSVs.

Does not retrieve, does not modify Phase 2/3/4/5/7, does not open TEST.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
from datetime import datetime, timezone

import numpy as np
import pandas as pd

_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(_DIR, "..", "..", ".."))
BENCH = os.path.join(ROOT, "experiments", "ultra_v2", "benchmark")
TEST_DIR = os.path.abspath(os.path.join(BENCH, "test"))
ART = os.path.join(_DIR, "artifacts")
CORPUS = os.path.join(ROOT, "data", "clean_articles.csv")
EXPECTED_CORPUS_SHA = "8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231"
ALLOWED_SPLITS = ("train", "dev")
QUAD23 = [
    "KN002", "KN005", "KN006", "KN008", "KN010", "KN018", "KN020", "KN021",
    "KN022", "KN024", "KN025", "KN026", "KN027", "KN028", "KN032", "KN036",
    "KN037", "KN041", "KN042", "KN044", "KN047", "KN051", "KN054",
]
EXPECTED_CSV_SHA = {
    "bm25": "cc0d31c2b4bb108ea7114811cafe1da68c1f1f4a88db8dd1d4700a5dd9429509",
    "dense": "4875884cbaeecd025df343befc5bccc6c35fc01dda54cff45173b56efab9fdb1",
    "hybrid": "c5174379abc872c2e2e7584b7974a461c32c287270e37f961483d4ead959828a",
    "ng3": "0149bd52dc00d7ace5bb510e17b5789037766ea69886738368e6f546a21ab3e5",
    "p7": "3c2c271e0f5da44f39eff43a5f37e4b1237e0ecf65977230897b0588d69a4711",
}
CSV_PATHS = {
    "bm25": os.path.join(ROOT, "experiments", "ultra_v2", "phase2_roman", "artifacts", "r2_b0_per_query.csv"),
    "dense": os.path.join(ROOT, "experiments", "ultra_v2", "phase3_dense", "DENSE_PER_QUERY.csv"),
    "hybrid": os.path.join(ROOT, "experiments", "ultra_v2", "phase4_hybrid", "HYBRID_PER_QUERY.csv"),
    "ng3": os.path.join(ROOT, "experiments", "ultra_v2", "phase5_ng3", "R2NG3_PER_QUERY.csv"),
    "p7": os.path.join(ROOT, "experiments", "ultra_v2", "phase7_entity_norm", "PHASE7_PER_QUERY.csv"),
}


# Copied verbatim from experiments/phase5_roman_urdu/run_phase5.py
# (function detect_script). Logic not altered. Copied instead of importing
# run_phase5.py so this diagnostic does not execute M0 side effects.
def detect_script(query: str) -> str:
    urdu = sum(1 for c in query if "\u0600" <= c <= "\u06FF")
    latin = sum(1 for c in query if ("A" <= c <= "Z") or ("a" <= c <= "z"))
    if urdu == 0 and latin == 0:
        return "OTHER"
    if urdu > 0 and latin > 0:
        return "MIXED"
    if urdu > 0:
        return "URDU"
    return "ROMAN"


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


def load_csv(path: str) -> dict[str, dict]:
    refuse_test_path(path)
    out = {}
    with open(path, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            out[r["query_id"]] = r
    return out


def parse_flag(row: dict, key: str) -> int:
    return int(float((row.get(key) or "0").strip() or "0"))


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
                rows.append({
                    "query_id": r["query_id"],
                    "query_text": r["query_text"],
                    "split": split,
                    "source_doc_id": int(r["source_doc_id"]),
                })
    if len(rows) != 51:
        raise SystemExit("BLOCKED — Roman KN n=%s != 51" % len(rows))
    return rows


def pair_mcnemar(hits_a: dict[str, int], hits_b: dict[str, int], ids: list[str], a_name: str, b_name: str) -> dict:
    n01 = n10 = hh = mm = 0
    rec_ids = []
    reg_ids = []
    for qid in ids:
        a, b = int(hits_a[qid]), int(hits_b[qid])
        if (not a) and b:
            n01 += 1
            rec_ids.append(qid)
        elif a and (not b):
            n10 += 1
            reg_ids.append(qid)
        elif a and b:
            hh += 1
        else:
            mm += 1
    raw = exact_mcnemar(n01, n10)
    p = float(raw["p_two_sided"])
    n_disc = int(raw["n_discordant"])
    if n_disc == 0:
        verdict = (
            "No discordant pairs; the two methods have identical Hit/Miss patterns. "
            "n=51 is small — this is not proof of no possible difference on a larger set."
        )
    else:
        if n01 > n10:
            direction = "%s has more unique hits than %s (%s vs %s discordant)" % (b_name, a_name, n01, n10)
        elif n10 > n01:
            direction = "%s has more unique hits than %s (%s vs %s discordant)" % (a_name, b_name, n10, n01)
        else:
            direction = "Discordant pairs are balanced (%s vs %s)" % (n01, n10)
        if p < 0.05:
            verdict = (
                "%s. The difference IS statistically significant at p<0.05." % direction
            )
        else:
            verdict = (
                "%s. The difference is NOT statistically significant at p<0.05. "
                "n=51 is small, so treat this as underpowered to detect a difference, "
                "not as proof of no difference." % direction
            )
    return {
        "control": a_name,
        "treatment": b_name,
        "n": len(ids),
        "hit_hit": hh,
        "miss_miss": mm,
        "control_miss_treatment_hit": n01,
        "control_hit_treatment_miss": n10,
        "treatment_unique_hit_ids": rec_ids,
        "control_unique_hit_ids": reg_ids,
        "mcnemar": raw,
        "test_statistic": {
            "discordant_pairs": n_disc,
            "b_control_hit_treatment_miss": n10,
            "c_control_miss_treatment_hit": n01,
        },
        "p_two_sided": p,
        "significant_at_0.05": bool(n_disc > 0 and p < 0.05),
        "verdict": verdict,
    }


def method_recall_row(name: str, h5: dict[str, int], h50: dict[str, int], ids: list[str]) -> dict:
    n = len(ids)
    n5 = sum(h5[q] for q in ids)
    n50 = sum(h50[q] for q in ids)
    miss = sum(1 for q in ids if h50[q] == 0)
    rank = sum(1 for q in ids if h50[q] == 1 and h5[q] == 0)
    return {
        "method": name,
        "n": n,
        "hit@5_n": n5,
        "hit@5_pct": round(100.0 * n5 / n, 2),
        "hit@50_n": n50,
        "hit@50_pct": round(100.0 * n50 / n, 2),
        "hit@50_also_hit@5_n": n5,
        "miss_n": miss,
        "miss_pct": round(100.0 * miss / n, 2),
        "rank_n": rank,
        "rank_pct": round(100.0 * rank / n, 2),
    }


def pct(arr: np.ndarray, q: float) -> float:
    return float(np.percentile(arr, q))


def main() -> int:
    os.makedirs(ART, exist_ok=True)
    print("label: ULTRA v2 PHASE6-DIAGNOSTICS", flush=True)
    print("TEST_accessed: no", flush=True)

    csv_sha = {}
    for key, path in CSV_PATHS.items():
        refuse_test_path(path)
        if not os.path.isfile(path):
            raise SystemExit("BLOCKED — missing frozen CSV %s" % path)
        got = sha256_file(path)
        csv_sha[key] = got
        if got != EXPECTED_CSV_SHA[key]:
            raise SystemExit("BLOCKED — %s CSV SHA-256 mismatch: %s" % (key, got))

    tables = {k: load_csv(p) for k, p in CSV_PATHS.items()}
    queries = load_roman_kn()
    ids = [r["query_id"] for r in queries]
    gold = {r["query_id"]: r["source_doc_id"] for r in queries}
    qtext = {r["query_id"]: r["query_text"] for r in queries}

    for name, tab in tables.items():
        if len(tab) != 51:
            raise SystemExit("BLOCKED — %s n=%s != 51" % (name, len(tab)))
        for qid in ids:
            if qid not in tab:
                raise SystemExit("BLOCKED — %s missing %s" % (name, qid))
            if int(tab[qid]["source_doc_id"]) != gold[qid]:
                raise SystemExit("BLOCKED — gold mismatch %s %s" % (name, qid))
    for qid in QUAD23:
        if qid not in gold:
            raise SystemExit("BLOCKED — quad23 id missing %s" % qid)

    h5 = {
        "bm25": {q: parse_flag(tables["bm25"][q], "hit@5") for q in ids},
        "dense": {q: parse_flag(tables["dense"][q], "dense_hit@5") for q in ids},
        "hybrid": {q: parse_flag(tables["hybrid"][q], "hybrid_hit@5") for q in ids},
        "ng3": {q: parse_flag(tables["ng3"][q], "ng3_hit@5") for q in ids},
        "p7": {q: parse_flag(tables["p7"][q], "p7_hit@5") for q in ids},
    }
    h50 = {
        "bm25": {q: parse_flag(tables["bm25"][q], "in_top50") for q in ids},
        "dense": {q: parse_flag(tables["dense"][q], "dense_hit@50") for q in ids},
        "hybrid": {q: parse_flag(tables["hybrid"][q], "hybrid_hit@50") for q in ids},
        "ng3": {q: parse_flag(tables["ng3"][q], "ng3_hit@50") for q in ids},
        "p7": {q: parse_flag(tables["p7"][q], "p7_hit@50") for q in ids},
    }
    union5 = {
        q: int(h5["bm25"][q] or h5["dense"][q] or h5["ng3"][q]) for q in ids
    }
    union50 = {
        q: int(h50["bm25"][q] or h50["dense"][q] or h50["ng3"][q]) for q in ids
    }

    comparisons = [
        ("BM25", "Dense", h5["bm25"], h5["dense"], h50["bm25"], h50["dense"]),
        ("Dense", "Hybrid", h5["dense"], h5["hybrid"], h50["dense"], h50["hybrid"]),
        ("BM25", "Hybrid", h5["bm25"], h5["hybrid"], h50["bm25"], h50["hybrid"]),
        ("Hybrid", "NG3", h5["hybrid"], h5["ng3"], h50["hybrid"], h50["ng3"]),
        ("Hybrid", "BM25∪Dense∪NG3", h5["hybrid"], union5, h50["hybrid"], union50),
    ]
    sig = {
        "timestamp_utc": utc_now(),
        "n": 51,
        "mcnemar_source": "exact_mcnemar copied verbatim from phase2_roman/run_r2_1_experiment.py",
        "note_n_small": (
            "n=51 is small. Non-significant results are underpowered to detect a "
            "difference, not proof of no difference."
        ),
        "pairs": [],
    }
    for a_name, b_name, a5, b5, a50, b50 in comparisons:
        sig["pairs"].append({
            "pair": "%s vs %s" % (a_name, b_name),
            "hit@5": pair_mcnemar(a5, b5, ids, a_name, b_name),
            "hit@50": pair_mcnemar(a50, b50, ids, a_name, b_name),
        })

    recall_rows = [
        method_recall_row("BM25", h5["bm25"], h50["bm25"], ids),
        method_recall_row("Dense", h5["dense"], h50["dense"], ids),
        method_recall_row("Hybrid", h5["hybrid"], h50["hybrid"], ids),
        method_recall_row("NG3", h5["ng3"], h50["ng3"], ids),
        method_recall_row("Phase7", h5["p7"], h50["p7"], ids),
    ]

    routing_rows = []
    n_roman = 0
    n_fail = 0
    n_quad_fail = 0
    for r in queries:
        pred = detect_script(r["query_text"])
        ok = pred == "ROMAN"
        n_roman += int(ok)
        n_fail += int(not ok)
        in23 = r["query_id"] in QUAD23
        if in23 and not ok:
            n_quad_fail += 1
        routing_rows.append({
            "query_id": r["query_id"],
            "split": r["split"],
            "benchmark_script": "ROMAN",
            "detect_script": pred,
            "pass": int(ok),
            "quad23": int(in23),
            "quad23_routing_pass": int(ok) if in23 else "",
        })

    print("hashing corpus (read-only)...", flush=True)
    corpus_sha = sha256_file(CORPUS)
    if corpus_sha != EXPECTED_CORPUS_SHA:
        raise SystemExit("BLOCKED — corpus SHA-256 mismatch: %s" % corpus_sha)
    print("loading corpus lengths...", flush=True)
    df = pd.read_csv(CORPUS, encoding="utf-8-sig")
    if "combined_text" not in df.columns:
        raise SystemExit("BLOCKED — combined_text missing")
    texts = df["combined_text"].fillna("").astype(str)
    if len(texts) != 111860:
        raise SystemExit("BLOCKED — corpus n=%s != 111860" % len(texts))
    char_len = texts.map(len).to_numpy(dtype=np.int64)
    tok_len = texts.map(lambda s: len(s.split())).to_numpy(dtype=np.int64)
    n_over_512 = int((tok_len > 512).sum())
    length = {
        "timestamp_utc": utc_now(),
        "corpus_path": "data/clean_articles.csv",
        "corpus_sha256": corpus_sha,
        "n_docs": int(len(texts)),
        "text_column": "combined_text",
        "n_empty": int((texts.str.len() == 0).sum()),
        "char_len": {
            "mean": float(char_len.mean()),
            "min": int(char_len.min()),
            "max": int(char_len.max()),
            "p10": pct(char_len, 10),
            "p25": pct(char_len, 25),
            "p50": pct(char_len, 50),
            "p75": pct(char_len, 75),
            "p90": pct(char_len, 90),
            "p95": pct(char_len, 95),
            "p99": pct(char_len, 99),
        },
        "whitespace_tokens": {
            "mean": float(tok_len.mean()),
            "min": int(tok_len.min()),
            "max": int(tok_len.max()),
            "p10": pct(tok_len, 10),
            "p25": pct(tok_len, 25),
            "p50": pct(tok_len, 50),
            "p75": pct(tok_len, 75),
            "p90": pct(tok_len, 90),
            "p95": pct(tok_len, 95),
            "p99": pct(tok_len, 99),
        },
        "exceed_512_whitespace_tokens": {
            "n": n_over_512,
            "pct": round(100.0 * n_over_512 / len(texts), 4),
        },
        "phase3_note": (
            "Phase 3 DENSE-BASELINE did not chunk or average long documents. "
            "It truncated at the encoder max_seq_length=512 (model/subword tokens, "
            "not whitespace tokens). The 512-whitespace-token count is a proxy for "
            "how many articles are long enough that truncation is likely, not an "
            "exact count of XLM-R tokens discarded."
        ),
        "phase4_chunk_npy_used": False,
    }

    with open(os.path.join(ART, "significance_results.json"), "w", encoding="utf-8") as f:
        json.dump(sig, f, indent=2, ensure_ascii=False)
        f.write("\n")
    rec_path = os.path.join(ART, "recall_table.csv")
    with open(rec_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(recall_rows[0].keys()))
        w.writeheader()
        w.writerows(recall_rows)
    route_path = os.path.join(ART, "routing_check.csv")
    with open(route_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(routing_rows[0].keys()))
        w.writeheader()
        w.writerows(routing_rows)
    with open(os.path.join(ART, "length_distribution.json"), "w", encoding="utf-8") as f:
        json.dump(length, f, indent=2, ensure_ascii=False)
        f.write("\n")

    def fmt_pair(block: dict) -> str:
        lines = []
        for cutoff in ("hit@5", "hit@50"):
            d = block[cutoff]
            m = d["mcnemar"]
            lines.append("**%s**" % cutoff)
            lines.append("")
            lines.append("| Item | Value |")
            lines.append("| --- | --- |")
            lines.append("| Control → treatment | %s → %s |" % (d["control"], d["treatment"]))
            lines.append("| Hit–hit / miss–miss | %s / %s |" % (d["hit_hit"], d["miss_miss"]))
            lines.append("| Treatment unique hits (c / n01) | %s |" % d["control_miss_treatment_hit"])
            lines.append("| Control unique hits (b / n10) | %s |" % d["control_hit_treatment_miss"])
            lines.append("| Discordant pairs (test statistic n_b+c) | %s |" % d["test_statistic"]["discordant_pairs"])
            lines.append("| p two-sided (exact McNemar) | %s |" % d["p_two_sided"])
            lines.append("| Significant at p<0.05 | %s |" % ("YES" if d["significant_at_0.05"] else "NO"))
            lines.append("")
            lines.append(d["verdict"])
            if d["treatment_unique_hit_ids"]:
                lines.append("")
                lines.append("Treatment-only hits: %s" % ", ".join(d["treatment_unique_hit_ids"]))
            if d["control_unique_hit_ids"]:
                lines.append("")
                lines.append("Control-only hits: %s" % ", ".join(d["control_unique_hit_ids"]))
            lines.append("")
        return "\n".join(lines)

    rec_md = []
    rec_md.append("| Method | Hit@50 | Of Hit@50, also Hit@5 | MISS (gold outside Top-50) | RANK (in Top-50, outside Top-5) |")
    rec_md.append("| --- | ---: | ---: | ---: | ---: |")
    for row in recall_rows:
        rec_md.append(
            "| %s | %s/51 = %.2f%% | %s/%s | %s/51 = %.2f%% | %s/51 = %.2f%% |"
            % (
                row["method"],
                row["hit@50_n"],
                row["hit@50_pct"],
                row["hit@50_also_hit@5_n"],
                row["hit@50_n"],
                row["miss_n"],
                row["miss_pct"],
                row["rank_n"],
                row["rank_pct"],
            )
        )

    quad_pass = n_quad_fail == 0
    report = """# PHASE6-DIAGNOSTICS — read-only analysis

**Status:** complete  
**Directory:** `experiments/ultra_v2/phase6_diagnostics/`  
**Timestamp (UTC):** %s  
**Population:** Roman KN TRAIN+DEV n=51  
**TEST:** not accessed  
**Retrieval rerun:** none

Frozen Phase 2/3/4/5/7 scripts, configs, and CSVs were read-only inputs. McNemar logic is `exact_mcnemar` copied verbatim from `experiments/ultra_v2/phase2_roman/run_r2_1_experiment.py`. `detect_script` is copied verbatim from `experiments/phase5_roman_urdu/run_phase5.py` (not imported, to avoid M0 import side effects).

---

## Task 1 — Statistical significance (exact McNemar)

n=51 is small. A non-significant p-value is **underpowered to detect a difference**, not proof that the methods are equal.

Paired binary Hit/Miss outcomes. Control miss / treatment hit = n01; control hit / treatment miss = n10. Test statistic = number of discordant pairs; p-value = two-sided exact binomial McNemar from the frozen function.

### BM25 vs Dense

%s
### Dense vs Hybrid

%s
### BM25 vs Hybrid

%s
### Hybrid vs NG3 (NG3 alone)

NG3 is a weak first-stage retriever. This pair is reported because it was requested; it is **not** a fair system-vs-system ranking contest.

%s
### Hybrid vs BM25 ∪ Dense ∪ NG3 (Top-k union)

Union Hit@k = gold in at least one of Method-D BM25, dense, or NG3 at cutoff k. Hybrid is RRF of BM25∪Dense only, so NG3-only golds can appear in the union but not in hybrid. This is a **candidate-pool** comparison, not a fused ranker.

%s
---

## Task 2 — Candidate Recall@50 vs RANK split

Re-tabulated from the frozen per-query CSVs. No retrieval.

%s

Hit@5 implies Hit@50, so “of Hit@50, also Hit@5” equals the Hit@5 count.

MISS is a candidate-generation failure (gold never entered the Top-50 pool). RANK is a ranking failure (gold was in the pool but not in Top-5).

---

## Task 3 — Script routing check

Frozen Unicode detector (`detect_script`): URDU / ROMAN / MIXED / OTHER.

M0 routing (context only, not re-run): URDU/MIXED → Urdu BM25; ROMAN → Method D.

| Check | Result |
| --- | --- |
| n=51 labeled ROMAN by detector | **%s / 51** |
| Detector mismatches vs ROMAN KN population | **%s** |
| Quad-23 dual-miss misroutes | **%s / 23** |
| Overall | **%s** |

All 51 queries, including all 23 four-way misses (KN002, KN005, KN006, KN008, KN010, KN018, KN020, KN021, KN022, KN024, KN025, KN026, KN027, KN028, KN032, KN036, KN037, KN041, KN042, KN044, KN047, KN051, KN054), are detector-ROMAN. Those 23 failures are **retrieval** failures, not script-routing errors.

Per-query flags: `artifacts/routing_check.csv`.

---

## Task 4 — Document length distribution

Corpus: `data/clean_articles.csv`, SHA-256 `%s`, n=%s, column `combined_text`.  
`experiments/phase4_chunk_ann/corpus_token_lengths.npy` was **not** used.

**Character length**

| Percentile | Value |
| --- | ---: |
| p10 | %.1f |
| p25 | %.1f |
| p50 | %.1f |
| p75 | %.1f |
| p90 | %.1f |
| p95 | %.1f |
| p99 | %.1f |
| mean | %.4f |
| min / max | %s / %s |

**Whitespace-token count**

| Percentile | Value |
| --- | ---: |
| p10 | %.1f |
| p25 | %.1f |
| p50 | %.1f |
| p75 | %.1f |
| p90 | %.1f |
| p95 | %.1f |
| p99 | %.1f |
| mean | %.4f |
| min / max | %s / %s |

Documents with **>512 whitespace tokens:** **%s / %s = %.4f%%**.

Phase 3 did **not** chunk or average those documents. It truncated each document at encoder `max_seq_length=512` (subword tokens, not whitespace tokens). The count above is a whitespace proxy for articles long enough that tail truncation is likely.

---

## Safety

| Check | Value |
| --- | --- |
| TEST accessed | NO |
| Frozen Phase 2/3/4/5/7 modified | NO |
| New retrieval / candidate generation | NO |
| Commit / push | NO |
""" % (
        utc_now(),
        fmt_pair(sig["pairs"][0]),
        fmt_pair(sig["pairs"][1]),
        fmt_pair(sig["pairs"][2]),
        fmt_pair(sig["pairs"][3]),
        fmt_pair(sig["pairs"][4]),
        "\n".join(rec_md),
        n_roman,
        n_fail,
        n_quad_fail,
        "PASS" if (n_fail == 0 and quad_pass) else "FAIL",
        corpus_sha,
        length["n_docs"],
        length["char_len"]["p10"],
        length["char_len"]["p25"],
        length["char_len"]["p50"],
        length["char_len"]["p75"],
        length["char_len"]["p90"],
        length["char_len"]["p95"],
        length["char_len"]["p99"],
        length["char_len"]["mean"],
        length["char_len"]["min"],
        length["char_len"]["max"],
        length["whitespace_tokens"]["p10"],
        length["whitespace_tokens"]["p25"],
        length["whitespace_tokens"]["p50"],
        length["whitespace_tokens"]["p75"],
        length["whitespace_tokens"]["p90"],
        length["whitespace_tokens"]["p95"],
        length["whitespace_tokens"]["p99"],
        length["whitespace_tokens"]["mean"],
        length["whitespace_tokens"]["min"],
        length["whitespace_tokens"]["max"],
        length["exceed_512_whitespace_tokens"]["n"],
        length["n_docs"],
        length["exceed_512_whitespace_tokens"]["pct"],
    )

    report_path = os.path.join(_DIR, "PHASE6_DIAGNOSTICS_REPORT.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
        if not report.endswith("\n"):
            f.write("\n")

    print("routing %s/51 ROMAN, quad23 fails %s" % (n_roman, n_quad_fail), flush=True)
    print("length >512 ws-tokens", n_over_512, flush=True)
    print("EVALUATION COMPLETE", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
