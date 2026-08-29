# -*- coding: utf-8 -*-
"""
Phase 6: residual known-item diagnosis of the frozen Phase 5 script-aware policy.

Does not change routing, BM25, Method D, or previous phase files.
H001-H040 unused. No RRF / fusion / reranker / SVM.
"""
from __future__ import annotations

import csv
import json
import math
import os
import sys
import time
from collections import Counter, defaultdict

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(_DIR, "..", ".."))
P5_DIR = os.path.join(ROOT, "experiments", "phase5_roman_urdu")
sys.path.insert(0, P5_DIR)
sys.path.insert(0, os.path.join(ROOT, "validate", "dual_index_routing"))
import run_phase5 as p5  # noqa: E402
from retrieve import search_headlines, transliterate_roman  # noqa: E402

OUT = _DIR
ART = os.path.join(OUT, "artifacts")
FIG = os.path.join(OUT, "figures")
EXPECTED_HIT5 = 0.8718
EXPECTED_MISSES = 10
HEADLINE_HIT5 = 0.4487
HIT_TOL = 0.0002
TOP_K = 50
URDU_STOP = {
    "کا", "کے", "کی", "نے", "سے", "میں", "ہے", "ہیں", "اور", "یہ", "وہ", "کو", "پر",
    "کا", "تو", "بھی", "جو", "یا", "ایک", "اس", "ان", "کہ", "تھا", "تھی", "تھے",
    "ہوا", "ہوئی", "گیا", "گئی", "کر", "کیا", "ہو", "نہ", "نہیں", "والے", "والی",
    "pakistan", "news", "update", "the", "a", "of", "in", "to", "and", "ka", "ke",
    "ki", "ne", "se", "mein", "hai", "aur", "ko",
}


def write_csv(path, header, rows):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def depth_bucket(rank):
    if rank is None or rank >= 999:
        return "MISS_50"
    if rank <= 5:
        return "TOP_5"
    if rank <= 10:
        return "RANK_6_10"
    if rank <= 20:
        return "RANK_11_20"
    if rank <= 50:
        return "RANK_21_50"
    return "MISS_50"


def jaccard(a, b):
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def coverage(qtoks, dtoks):
    if not qtoks:
        return 0.0
    ds = set(dtoks)
    return sum(1 for t in qtoks if t in ds) / len(qtoks)


def content_tokens(toks):
    return [t for t in toks if len(t) >= 3 and t not in URDU_STOP]


def clip(s, n=180):
    s = (s or "").replace("\n", " ").strip()
    return s if len(s) <= n else s[: n - 1] + "…"


def main():
    os.makedirs(ART, exist_ok=True)
    os.makedirs(FIG, exist_ok=True)
    print("=== Phase 6 residual diagnosis ===", flush=True)

    eval_rows = p5.load_eval_rows()
    assert len(eval_rows) == 78, len(eval_rows)
    for r in eval_rows:
        if r["query_id"].startswith("H"):
            raise RuntimeError("frozen id: %s" % r["query_id"])

    fwd = p5.load_roman_dict()
    rev = p5.load_reverse_roman(fwd)

    print("loading corpus...", flush=True)
    df = pd.read_csv(p5.CORPUS, encoding="utf-8-sig")
    if "combined_text" in df.columns:
        texts = df["combined_text"].fillna("").astype(str).tolist()
    else:
        texts = (df["Headline"].fillna("").astype(str) + " " + df["News Text"].fillna("").astype(str)).tolist()
    headlines = df["Headline"].fillna("").astype(str).tolist()
    bodies = df["News Text"].fillna("").astype(str).tolist() if "News Text" in df.columns else [""] * len(df)

    print("tokenize + romanize...", flush=True)
    t0 = time.perf_counter()
    urdu_docs, roman_docs = [], []
    for i, text in enumerate(texts):
        utoks = p5.tokenize(text)
        rtoks = [p5.romanize_token(t, rev) for t in utoks]
        rtoks = [t for t in rtoks if t]
        urdu_docs.append(utoks)
        roman_docs.append(rtoks)
        if (i + 1) % 20000 == 0:
            print("  %s/%s" % (i + 1, len(texts)), flush=True)
    print("tokenize %.1fs" % (time.perf_counter() - t0), flush=True)

    urdu_bm25 = p5.BM25(urdu_docs)
    roman_bm25 = p5.BM25(roman_docs)
    print("indexes ready urdu_terms=%s roman_terms=%s" % (len(urdu_bm25.idf), len(roman_bm25.idf)), flush=True)

    def search_both(q, src):
        u_rank, _ = p5.search_rank(urdu_bm25, p5.tokenize(q), src, top_k=TOP_K)
        qtoks_r = [p5.romanize_token(t, rev) for t in p5.tokenize(q)]
        qtoks_r = [t for t in qtoks_r if t]
        r_rank, _ = p5.search_rank(roman_bm25, qtoks_r if any(p5.has_urdu(q) for _ in [0]) else p5.tokenize(q), src, top_k=TOP_K)
        # Method D uses the original roman query tokens (not romanize_token on latin)
        return u_rank, r_rank

    recs = []
    sa_ranks, hl_ranks, raw_ranks, roman_ranks = [], [], [], []
    print("evaluating n=78...", flush=True)
    for i, r in enumerate(eval_rows, 1):
        q = r["query_text"]
        src = r["source_doc_id"]
        lang = r["language_type"]
        u_rank, _lat = p5.search_rank(urdu_bm25, p5.tokenize(q), src, top_k=TOP_K)
        d_qtoks = p5.tokenize(q)  # Method D: original tokens on roman index
        d_rank, _ = p5.search_rank(roman_bm25, d_qtoks, src, top_k=TOP_K)
        qh, _ = transliterate_roman(q)
        hh = search_headlines(qh, top_k=TOP_K)
        h_rank = p5.rank_of(hh, src)
        if lang == "roman_urdu":
            sa = d_rank
        else:
            sa = u_rank
        rec = {
            "query_id": r["query_id"],
            "split": r["split"],
            "query_type": lang,
            "query": q,
            "source_doc_id": src,
            "script_aware_rank": sa,
            "headline_rank": h_rank,
            "raw_bm25_rank": u_rank,
            "roman_bm25_rank": d_rank,
            "source_headline": headlines[src],
            "source_body": bodies[src],
        }
        recs.append(rec)
        sa_ranks.append(sa)
        hl_ranks.append(h_rank)
        raw_ranks.append(u_rank)
        roman_ranks.append(d_rank)
        if i % 20 == 0 or i == 78:
            print("  %s/78" % i, flush=True)

    m_sa = p5.metrics_from_ranks(sa_ranks)
    m_hl = p5.metrics_from_ranks(hl_ranks)
    print("script-aware Hit@5=%s nDCG@5=%s MRR=%s" % (m_sa["hit@5"], m_sa["ndcg@5"], m_sa["mrr"]), flush=True)
    print("headline Hit@5=%s" % m_hl["hit@5"], flush=True)

    repro = {
        "expected_hit@5": EXPECTED_HIT5,
        "observed_hit@5": m_sa["hit@5"],
        "expected_misses": EXPECTED_MISSES,
        "observed_misses": int(sum(1 for x in sa_ranks if x > 5)),
        "headline_expected_hit@5": HEADLINE_HIT5,
        "headline_observed_hit@5": m_hl["hit@5"],
        "ndcg@5": m_sa["ndcg@5"],
        "mrr": m_sa["mrr"],
        "reproduced": abs(m_sa["hit@5"] - EXPECTED_HIT5) <= HIT_TOL and int(sum(1 for x in sa_ranks if x > 5)) == EXPECTED_MISSES,
    }
    with open(os.path.join(ART, "reproduction.json"), "w", encoding="utf-8") as f:
        json.dump(repro, f, indent=2)
    if not repro["reproduced"]:
        print("STOP: Phase 5 not reproduced: %s" % repro, flush=True)
        sys.exit(2)
    print("Phase 5 reproduced.", flush=True)

    misses = [r for r in recs if r["script_aware_rank"] > 5]
    hits = [r for r in recs if r["script_aware_rank"] <= 5]
    assert len(misses) == 10, len(misses)

    # Top lists for misses (script-aware room + headline)
    miss_details = []
    for r in misses:
        q, src, lang = r["query"], r["source_doc_id"], r["query_type"]
        if lang == "roman_urdu":
            hits_sa = roman_bm25.search(p5.tokenize(q), top_k=TOP_K)
        else:
            hits_sa = urdu_bm25.search(p5.tokenize(q), top_k=TOP_K)
        qh, _ = transliterate_roman(q)
        hits_hl = search_headlines(qh, top_k=TOP_K)
        top5_sa = []
        for did, score in hits_sa[:5]:
            top5_sa.append({
                "doc_id": int(did),
                "score": float(score),
                "headline": headlines[int(did)],
                "is_source": int(did) == int(src),
            })
        top5_hl = []
        for did, score in hits_hl[:5]:
            top5_hl.append({
                "doc_id": int(did),
                "score": float(score),
                "headline": headlines[int(did)],
                "is_source": int(did) == int(src),
            })
        qtoks = p5.tokenize(q)
        htoks = p5.tokenize(headlines[src])
        btoks = p5.tokenize(texts[src])
        cq, ch, cb = content_tokens(qtoks), content_tokens(htoks), content_tokens(btoks)
        miss_details.append({
            **{k: r[k] for k in r if k != "source_body"},
            "source_body_clip": clip(r["source_body"], 400),
            "top5_script_aware": top5_sa,
            "top5_headline": top5_hl,
            "q_len_tokens": len(qtoks),
            "headline_jaccard": round(jaccard(qtoks, htoks), 4),
            "body_jaccard": round(jaccard(qtoks, btoks), 4),
            "headline_coverage": round(coverage(qtoks, htoks), 4),
            "body_coverage": round(coverage(qtoks, btoks), 4),
            "content_headline_jaccard": round(jaccard(cq, ch), 4),
            "content_body_jaccard": round(jaccard(cq, cb), 4),
            "content_headline_coverage": round(coverage(cq, ch), 4),
            "content_body_coverage": round(coverage(cq, cb), 4),
            "overlap_headline": " ".join(sorted(set(cq) & set(ch))),
            "overlap_body": " ".join(sorted(list(set(cq) & set(cb)))[:20]),
        })

    with open(os.path.join(ART, "miss_details.json"), "w", encoding="utf-8") as f:
        json.dump(miss_details, f, ensure_ascii=False, indent=2)

    # Inventory (all 78)
    inv = []
    for r in recs:
        roman_col = r["roman_bm25_rank"] if r["query_type"] in ("roman_urdu", "mixed") else ""
        inv.append([
            r["query_id"], r["split"], r["query_type"], r["query"], r["source_doc_id"],
            r["script_aware_rank"], r["headline_rank"], r["raw_bm25_rank"], roman_col,
        ])
    write_csv(
        os.path.join(OUT, "RESIDUAL_QUERY_INVENTORY.csv"),
        ["query_id", "split", "query_type", "query", "source_doc_id",
         "script_aware_rank", "headline_rank", "raw_bm25_rank", "roman_bm25_rank_if_applicable"],
        inv,
    )

    def split_counts(rows):
        c = Counter()
        for r in rows:
            c[(r["split"], r["query_type"])] += 1
        return c

    mc = split_counts(misses)
    write_csv(
        os.path.join(OUT, "RESIDUAL_SPLIT_SUMMARY.csv"),
        ["split", "query_type", "n_misses", "miss_ids"],
        [
            [spl, lang, mc[(spl, lang)],
             ",".join(r["query_id"] for r in misses if r["split"] == spl and r["query_type"] == lang)]
            for spl in ("dev", "internal_val")
            for lang in ("urdu", "roman_urdu", "mixed")
            if mc[(spl, lang)]
        ] + [
            ["dev", "ALL", sum(1 for r in misses if r["split"] == "dev"),
             ",".join(r["query_id"] for r in misses if r["split"] == "dev")],
            ["internal_val", "ALL", sum(1 for r in misses if r["split"] == "internal_val"),
             ",".join(r["query_id"] for r in misses if r["split"] == "internal_val")],
            ["all", "urdu", sum(1 for r in misses if r["query_type"] == "urdu"),
             ",".join(r["query_id"] for r in misses if r["query_type"] == "urdu")],
            ["all", "roman_urdu", sum(1 for r in misses if r["query_type"] == "roman_urdu"),
             ",".join(r["query_id"] for r in misses if r["query_type"] == "roman_urdu")],
            ["all", "mixed", sum(1 for r in misses if r["query_type"] == "mixed"),
             ",".join(r["query_id"] for r in misses if r["query_type"] == "mixed")],
            ["all", "ALL", 10, ",".join(r["query_id"] for r in misses)],
        ],
    )

    depth_rows = []
    sa_buckets, hl_buckets = Counter(), Counter()
    for r in misses:
        sb, hb = depth_bucket(r["script_aware_rank"]), depth_bucket(r["headline_rank"])
        sa_buckets[sb] += 1
        hl_buckets[hb] += 1
        depth_rows.append([
            r["query_id"], r["split"], r["query_type"],
            r["script_aware_rank"], sb, r["headline_rank"], hb,
            int(r["script_aware_rank"] <= 50), int(r["headline_rank"] <= 50),
        ])
    write_csv(
        os.path.join(OUT, "RANK_DEPTH_ANALYSIS.csv"),
        ["query_id", "split", "query_type", "script_aware_rank", "script_aware_bucket",
         "headline_rank", "headline_bucket", "source_in_sa_top50", "source_in_hl_top50"],
        depth_rows,
    )

    # Complementarity on all 78 (oracle, not a system)
    n = 78
    sa_hit = sum(1 for r in recs if r["script_aware_rank"] <= 5)
    hl_hit = sum(1 for r in recs if r["headline_rank"] <= 5)
    both = sum(1 for r in recs if r["script_aware_rank"] <= 5 and r["headline_rank"] <= 5)
    union = sum(1 for r in recs if r["script_aware_rank"] <= 5 or r["headline_rank"] <= 5)
    hl_only = sum(1 for r in recs if r["headline_rank"] <= 5 and r["script_aware_rank"] > 5)
    sa_only = sum(1 for r in recs if r["script_aware_rank"] <= 5 and r["headline_rank"] > 5)
    both_miss = sum(1 for r in recs if r["script_aware_rank"] > 5 and r["headline_rank"] > 5)
    room_rows = []
    for r in recs:
        sa_m, hl_m = r["script_aware_rank"] > 5, r["headline_rank"] > 5
        if (not sa_m) and (not hl_m):
            lab = "BOTH_HIT"
        elif sa_m and (not hl_m):
            lab = "HEADLINE_RECOVERS"
        elif (not sa_m) and hl_m:
            lab = "SCRIPT_AWARE_RECOVERS"
        else:
            lab = "BOTH_MISS"
        if r["script_aware_rank"] > 5:
            room_rows.append([
                r["query_id"], r["split"], r["query_type"], r["script_aware_rank"], r["headline_rank"], lab,
            ])
    write_csv(
        os.path.join(OUT, "ROOM_COMPLEMENTARITY.csv"),
        ["query_id", "split", "query_type", "script_aware_rank", "headline_rank", "class"],
        room_rows + [
            ["_SUMMARY_n78", "", "", sa_hit, hl_hit, "sa_hits / hl_hits"],
            ["_SUMMARY_headline_only", "", "", hl_only, "", "HEADLINE_RECOVERS among 78"],
            ["_SUMMARY_script_aware_only", "", "", sa_only, "", "SCRIPT_AWARE_RECOVERS among 78"],
            ["_SUMMARY_overlap", "", "", both, "", "both Hit@5"],
            ["_SUMMARY_union_oracle", "", "", union, round(union / n, 4), "NOT a deployed system"],
            ["_SUMMARY_both_miss", "", "", both_miss, "", "both miss Top-5"],
        ],
    )

    # Lexical overlap: all 78, flag miss
    lex_rows = []
    miss_ov, hit_ov = [], []
    for r in recs:
        qtoks = p5.tokenize(r["query"])
        src = r["source_doc_id"]
        htoks = p5.tokenize(headlines[src])
        btoks = p5.tokenize(texts[src])
        cq, ch, cb = content_tokens(qtoks), content_tokens(htoks), content_tokens(btoks)
        row_stats = {
            "is_miss": int(r["script_aware_rank"] > 5),
            "q_len": len(qtoks),
            "headline_jaccard": jaccard(qtoks, htoks),
            "body_jaccard": jaccard(qtoks, btoks),
            "headline_coverage": coverage(qtoks, htoks),
            "body_coverage": coverage(qtoks, btoks),
            "content_headline_coverage": coverage(cq, ch),
            "content_body_coverage": coverage(cq, cb),
            "content_headline_jaccard": jaccard(cq, ch),
            "content_body_jaccard": jaccard(cq, cb),
        }
        if row_stats["is_miss"]:
            miss_ov.append(row_stats)
        else:
            hit_ov.append(row_stats)
        lex_rows.append([
            r["query_id"], r["split"], r["query_type"], row_stats["is_miss"], row_stats["q_len"],
            round(row_stats["headline_jaccard"], 4), round(row_stats["body_jaccard"], 4),
            round(row_stats["headline_coverage"], 4), round(row_stats["body_coverage"], 4),
            round(row_stats["content_headline_jaccard"], 4), round(row_stats["content_body_jaccard"], 4),
            round(row_stats["content_headline_coverage"], 4), round(row_stats["content_body_coverage"], 4),
            " ".join(sorted(set(cq) & set(ch)))[:120],
        ])
    write_csv(
        os.path.join(OUT, "LEXICAL_OVERLAP_ANALYSIS.csv"),
        ["query_id", "split", "query_type", "is_script_aware_miss", "query_n_tokens",
         "headline_jaccard", "body_jaccard", "headline_coverage", "body_coverage",
         "content_headline_jaccard", "content_body_jaccard",
         "content_headline_coverage", "content_body_coverage", "content_overlap_headline"],
        lex_rows,
    )

    def mean_key(rows, k):
        return round(float(np.mean([x[k] for x in rows])) if rows else 0.0, 4)

    lex_summary = {
        "miss_n": len(miss_ov),
        "hit_n": len(hit_ov),
        "miss_mean_q_len": mean_key(miss_ov, "q_len"),
        "hit_mean_q_len": mean_key(hit_ov, "q_len"),
        "miss_mean_headline_coverage": mean_key(miss_ov, "headline_coverage"),
        "hit_mean_headline_coverage": mean_key(hit_ov, "headline_coverage"),
        "miss_mean_body_coverage": mean_key(miss_ov, "body_coverage"),
        "hit_mean_body_coverage": mean_key(hit_ov, "body_coverage"),
        "miss_mean_content_headline_coverage": mean_key(miss_ov, "content_headline_coverage"),
        "hit_mean_content_headline_coverage": mean_key(hit_ov, "content_headline_coverage"),
        "miss_mean_content_body_coverage": mean_key(miss_ov, "content_body_coverage"),
        "hit_mean_content_body_coverage": mean_key(hit_ov, "content_body_coverage"),
        "miss_mean_headline_jaccard": mean_key(miss_ov, "headline_jaccard"),
        "hit_mean_headline_jaccard": mean_key(hit_ov, "headline_jaccard"),
    }
    with open(os.path.join(ART, "lexical_summary.json"), "w", encoding="utf-8") as f:
        json.dump(lex_summary, f, indent=2)

    # Top-result dump CSV (human taxonomy filled after inspection)
    top_rows = []
    for d in miss_details:
        sa_heads = " || ".join("%s [%s]" % (clip(x["headline"], 80), x["doc_id"]) for x in d["top5_script_aware"])
        hl_heads = " || ".join("%s [%s]" % (clip(x["headline"], 80), x["doc_id"]) for x in d["top5_headline"])
        top_rows.append([
            d["query_id"], d["split"], d["query_type"], d["query"], d["source_doc_id"],
            clip(d["source_headline"], 160), d["script_aware_rank"], d["headline_rank"],
            sa_heads, hl_heads,
            d["content_headline_coverage"], d["content_body_coverage"],
        ])
    write_csv(
        os.path.join(OUT, "TOP_RESULT_ERROR_ANALYSIS.csv"),
        ["query_id", "split", "query_type", "query", "source_doc_id", "source_headline",
         "script_aware_rank", "headline_rank", "top5_script_aware_headlines",
         "top5_headline_room_headlines", "content_headline_coverage", "content_body_coverage"],
        top_rows,
    )

    # Figures (quantitative only; taxonomy figure written after human labels if present)
    fig, ax = plt.subplots(figsize=(7, 4))
    order = ["TOP_5", "RANK_6_10", "RANK_11_20", "RANK_21_50", "MISS_50"]
    ax.bar([x.replace("_", " ") for x in order], [sa_buckets[b] for b in order], color="#3b6ea5")
    ax.set_title("Script-aware rank depth (10 misses)")
    ax.set_ylabel("count")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "rank_depth_script_aware.png"), dpi=140)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 4))
    labels = ["Headline only\n(recovers miss)", "Both miss", "Script-aware only\n(among 78)"]
    ax.bar(labels, [hl_only, both_miss, sa_only], color=["#c47b2b", "#8b3a3a", "#3b6ea5"])
    ax.set_title("Room complementarity (oracle, not deployed)")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "room_complementarity.png"), dpi=140)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6.5, 4))
    xs = ["headline coverage", "body coverage", "content headline cov.", "content body cov."]
    miss_y = [lex_summary["miss_mean_headline_coverage"], lex_summary["miss_mean_body_coverage"],
              lex_summary["miss_mean_content_headline_coverage"], lex_summary["miss_mean_content_body_coverage"]]
    hit_y = [lex_summary["hit_mean_headline_coverage"], lex_summary["hit_mean_body_coverage"],
             lex_summary["hit_mean_content_headline_coverage"], lex_summary["hit_mean_content_body_coverage"]]
    x = np.arange(len(xs))
    ax.bar(x - 0.2, miss_y, 0.4, label="10 misses", color="#8b3a3a")
    ax.bar(x + 0.2, hit_y, 0.4, label="68 hits", color="#3b6ea5")
    ax.set_xticks(x)
    ax.set_xticklabels(xs, rotation=15, ha="right")
    ax.set_ylim(0, 1)
    ax.set_title("Mean lexical overlap: misses vs hits")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "lexical_overlap.png"), dpi=140)
    plt.close(fig)

    with open(os.path.join(ART, "phase6_quant.json"), "w", encoding="utf-8") as f:
        json.dump({
            "reproduction": repro,
            "lexical": lex_summary,
            "complementarity": {
                "sa_hit": sa_hit, "hl_hit": hl_hit, "both": both, "union": union,
                "union_hit@5": round(union / n, 4), "headline_only": hl_only,
                "script_aware_only": sa_only, "both_miss": both_miss,
            },
            "sa_buckets": dict(sa_buckets),
            "hl_buckets_on_misses": dict(hl_buckets),
            "miss_ids": [r["query_id"] for r in misses],
            "dev_misses": [r["query_id"] for r in misses if r["split"] == "dev"],
            "val_misses": [r["query_id"] for r in misses if r["split"] == "internal_val"],
        }, f, indent=2)

    print("Wrote quantitative CSVs. Inspect artifacts/miss_details.json then fill taxonomy.", flush=True)
    print("misses=%s" % [r["query_id"] for r in misses], flush=True)


if __name__ == "__main__":
    main()
