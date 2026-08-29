# -*- coding: utf-8 -*-
"""
validate/phase2_5/02_compute_metrics_from_judgments.py

PHASE 2.5 -- computes retrieval metrics from HUMAN-PROVIDED relevance
judgments and applies the pre-agreed SHORT / LONG / QUERY-DEPENDENT
decision logic to the 5-6 word bare-event region. Does NOT touch the
SVM, training labels, or any V2/V3 training process.

Run only AFTER a human has filled in the `relevance` column in the CSV
produced by 01_run_retrieval_and_export_judgment_template.py
(judgment_template.csv), replacing "UNJUDGED" with one of:
    Relevant
    Partially relevant
    Not relevant

Usage:
    PHASE2_5_JUDGMENTS_PATH=/path/to/judged.csv \
        python validate/phase2_5/02_compute_metrics_from_judgments.py

This script has NOT been executed against real judgment data in this
session -- no judgments exist yet, because Phase 2.5 retrieval has not
been run against the real corpus. No metrics or conclusions in this file
are fabricated or pre-filled.

DECISION LOGIC (Step 8 of the project brief, made concrete/auditable):
For each word-count bucket (5w, 6w -- the buckets under investigation --
and also 7w/8w/9w for context) and separately for each script (Urdu /
Roman Urdu, per Step 9), this script compares mean nDCG@15 for the
HEADLINE mode vs. the FULL_CONTENT mode across the queries in that
bucket that have valid, complete judgments:

  - LONG   if FULL_CONTENT's mean nDCG@15 exceeds HEADLINE's by more than
           DECISION_THRESHOLD, AND at least DECISION_MAJORITY_FRACTION of
           the individual queries in the bucket individually favor
           FULL_CONTENT (not just the mean).
  - SHORT  same test, reversed.
  - QUERY-DEPENDENT / INCONCLUSIVE otherwise -- including when the mean
           difference is small, or the mean favors one mode but
           individual queries disagree (that disagreement IS the
           query-dependent finding, not noise to explain away).
  - INSUFFICIENT_DATA if fewer than MIN_QUERIES_FOR_DECISION judged
           queries exist in the bucket.

These thresholds are constants below, not hidden -- change them and
re-run if you want to argue for a different sensitivity, but do not
tune them post-hoc based on which answer they produce for the actual
data; pick them and record the choice before looking at the numbers.

By default, only the primary semantic modes (HEADLINE, FULL_CONTENT,
HYBRID) feed the decision logic. HEADLINE_KEYWORD_TFIDF is reported
separately as a diagnostic, since it differs in retrieval *method*
(lexical) as well as content *scope* from FULL_CONTENT (semantic),
which would confound the SHORT/LONG question -- see script 01's
docstring for the full explanation of this issue in the pre-existing
codebase.
"""

import csv
import json
import math
import os
import sys
from collections import defaultdict

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PHASE2_5_DIR = os.path.join(REPO_ROOT, "validate", "phase2_5")
DEFAULT_METRICS_OUTPUT = os.path.join(PHASE2_5_DIR, "phase2_5_metrics_report.json")

REL_MAP = {
    "relevant": 1.0,
    "partially relevant": 0.5,
    "not relevant": 0.0,
}

PRIMARY_MODES = ["HEADLINE", "FULL_CONTENT", "HYBRID"]
DIAGNOSTIC_MODES = ["HEADLINE_KEYWORD_TFIDF"]

WORD_BUCKETS_OF_INTEREST = ["5", "6"]  # the actual unresolved research question
WORD_BUCKETS_FOR_CONTEXT = ["7", "8", "9"]

# Decision thresholds -- fixed here, before looking at real results.
DECISION_THRESHOLD = 0.05          # min mean nDCG@15 gap to call a direction
DECISION_MAJORITY_FRACTION = 0.70  # fraction of individual queries that must agree
MIN_QUERIES_FOR_DECISION = 3       # below this, INSUFFICIENT_DATA regardless of gap


# ---------------------------------------------------------------------
# Metric primitives
# ---------------------------------------------------------------------
def precision_at_k(graded_relevance, k):
    top = graded_relevance[:k]
    if not top:
        return None
    return sum(top) / len(top)


def reciprocal_rank(graded_relevance):
    for i, rel in enumerate(graded_relevance, 1):
        if rel > 0:
            return 1.0 / i
    return 0.0


def dcg_at_k(graded_relevance, k):
    return sum(
        (2 ** rel - 1) / math.log2(i + 2)
        for i, rel in enumerate(graded_relevance[:k])
    )


def ndcg_at_k(graded_relevance, k):
    dcg = dcg_at_k(graded_relevance, k)
    ideal = dcg_at_k(sorted(graded_relevance, reverse=True), k)
    if ideal == 0:
        return 0.0
    return dcg / ideal


def compute_metrics_for_ranked_list(graded_relevance):
    return {
        "P@5": precision_at_k(graded_relevance, 5),
        "P@10": precision_at_k(graded_relevance, 10),
        "P@15": precision_at_k(graded_relevance, 15),
        "MRR": reciprocal_rank(graded_relevance),
        "nDCG@15": ndcg_at_k(graded_relevance, 15),
    }


# ---------------------------------------------------------------------
# Loading + validation
# ---------------------------------------------------------------------
def load_judgments(path):
    with open(path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    required = {
        "query_id", "query", "word_count", "script", "rule_type", "tag",
        "category", "pre_registered_hypothesis", "retrieval_mode", "rank",
        "doc_id", "score", "invalid_no_corpus_match",
        "tied_or_zero_similarity_flag", "relevance",
    }
    missing_cols = required - set(rows[0].keys()) if rows else required
    if missing_cols:
        print(f"ERROR: judgment file is missing required columns: {missing_cols}")
        sys.exit(1)
    return rows


def build_ranked_lists(rows):
    """
    Group rows into {(query_id, mode): [(rank, graded_relevance_or_None), ...]}
    sorted by rank. Also returns per-query static info and invalid/unjudged
    tracking.
    """
    groups = defaultdict(list)
    query_info = {}
    for r in rows:
        key = (r["query_id"], r["retrieval_mode"])
        rel_raw = r["relevance"].strip()
        rel_key = rel_raw.lower()
        graded = REL_MAP.get(rel_key, None)  # None if UNJUDGED or unrecognized
        groups[key].append((int(r["rank"]), rel_raw, graded))

        if r["query_id"] not in query_info:
            query_info[r["query_id"]] = {
                "query": r["query"],
                "word_count": r["word_count"],
                "script": r["script"],
                "rule_type": r["rule_type"],
                "tag": r["tag"],
                "category": r["category"],
                "pre_registered_hypothesis": r["pre_registered_hypothesis"],
                "invalid_no_corpus_match": r["invalid_no_corpus_match"].strip().lower() == "true",
            }

    for key in groups:
        groups[key].sort(key=lambda x: x[0])

    return groups, query_info


def main():
    judgments_path = os.environ.get("PHASE2_5_JUDGMENTS_PATH")
    if not judgments_path or not os.path.exists(judgments_path):
        print(
            "No human judgment data found. This is expected if Phase 2.5 "
            "retrieval has not been run against the real corpus yet, or if "
            "judgments haven't been filled in. This script will not "
            "fabricate or simulate judgment data or metrics.\n\n"
            "To use this script for real:\n"
            "  1. Run 01_run_retrieval_and_export_judgment_template.py on a "
            "machine with the real corpus -> produces judgment_template.csv\n"
            "  2. Have a human open judgment_template.csv and replace "
            "'UNJUDGED' in the relevance column with one of: Relevant, "
            "Partially relevant, Not relevant, for every row.\n"
            "  3. Set PHASE2_5_JUDGMENTS_PATH to that judged file and "
            "re-run this script.\n"
        )
        sys.exit(0)

    rows = load_judgments(judgments_path)
    print(f"Loaded {len(rows)} judgment rows from {judgments_path}")

    groups, query_info = build_ranked_lists(rows)
    all_query_ids = sorted(query_info.keys())
    print(f"Covers {len(all_query_ids)} distinct queries.")

    # -------------------------------------------------------------
    # Per (query, mode) metrics -- excluding invalid-no-corpus-match
    # queries, and skipping (with a warning) any (query, mode) pair
    # that still has UNJUDGED rows.
    # -------------------------------------------------------------
    per_query_mode_metrics = {}
    skipped_unjudged = []
    skipped_invalid = []

    for (qid, mode), ranked in groups.items():
        if query_info[qid]["invalid_no_corpus_match"]:
            skipped_invalid.append((qid, mode))
            continue
        gradeds = [g for _, _, g in ranked]
        if any(g is None for g in gradeds):
            skipped_unjudged.append((qid, mode))
            continue
        per_query_mode_metrics[(qid, mode)] = compute_metrics_for_ranked_list(gradeds)

    if skipped_invalid:
        n_invalid_queries = len(set(qid for qid, _ in skipped_invalid))
        print(f"\n{n_invalid_queries} quer(ies) flagged INVALID_NO_CORPUS_MATCH "
              f"-- excluded from metrics, NOT counted as retrieval failure "
              f"(per Step 5 of the brief).")

    if skipped_unjudged:
        n_unjudged_queries = len(set(qid for qid, _ in skipped_unjudged))
        print(f"\nWARNING: {len(skipped_unjudged)} (query, mode) pairs across "
              f"{n_unjudged_queries} queries still contain UNJUDGED rows and "
              f"were excluded from metrics. Fill in the remaining relevance "
              f"judgments and re-run for a complete analysis. Affected:")
        for qid, mode in sorted(skipped_unjudged)[:20]:
            print(f"    {qid} / {mode}")
        if len(skipped_unjudged) > 20:
            print(f"    ... and {len(skipped_unjudged) - 20} more")

    if not per_query_mode_metrics:
        print("\nNo fully-judged (query, mode) pairs available. Nothing to "
              "report. Fill in relevance judgments and re-run.")
        sys.exit(0)

    # -------------------------------------------------------------
    # Aggregation helper
    # -------------------------------------------------------------
    def aggregate(filter_fn, modes=PRIMARY_MODES + DIAGNOSTIC_MODES):
        out = {}
        for mode in modes:
            vals = defaultdict(list)
            for (qid, m), metrics in per_query_mode_metrics.items():
                if m != mode:
                    continue
                if not filter_fn(qid):
                    continue
                for metric_name, v in metrics.items():
                    if v is not None:
                        vals[metric_name].append(v)
            if vals:
                out[mode] = {
                    metric_name: {
                        "mean": sum(v) / len(v),
                        "n": len(v),
                    }
                    for metric_name, v in vals.items()
                }
        return out

    report = {
        "judgments_path": judgments_path,
        "num_queries_total": len(all_query_ids),
        "num_query_mode_pairs_scored": len(per_query_mode_metrics),
        "num_query_mode_pairs_skipped_unjudged": len(skipped_unjudged),
        "num_queries_invalid_no_corpus_match": len(set(qid for qid, _ in skipped_invalid)),
        "primary_modes": PRIMARY_MODES,
        "diagnostic_modes": DIAGNOSTIC_MODES,
        "decision_thresholds": {
            "DECISION_THRESHOLD": DECISION_THRESHOLD,
            "DECISION_MAJORITY_FRACTION": DECISION_MAJORITY_FRACTION,
            "MIN_QUERIES_FOR_DECISION": MIN_QUERIES_FOR_DECISION,
        },
        "breakdown": {},
        "decision": {},
    }

    print("\n" + "=" * 70)
    print("BREAKDOWN BY RETRIEVAL MODE (overall, all judged queries)")
    print("=" * 70)
    overall = aggregate(lambda qid: True)
    report["breakdown"]["overall_by_mode"] = overall
    for mode, metrics in overall.items():
        print(f"\n{mode}:")
        for name, stat in metrics.items():
            print(f"  {name:<10} mean={stat['mean']:.4f}  (n={stat['n']})")

    print("\n" + "=" * 70)
    print("BREAKDOWN BY WORD COUNT")
    print("=" * 70)
    report["breakdown"]["by_word_count"] = {}
    for wc in WORD_BUCKETS_OF_INTEREST + WORD_BUCKETS_FOR_CONTEXT:
        agg = aggregate(lambda qid, wc=wc: query_info[qid]["word_count"] == wc)
        if agg:
            report["breakdown"]["by_word_count"][wc] = agg
            print(f"\n-- {wc} words --")
            for mode, metrics in agg.items():
                ndcg = metrics.get("nDCG@15", {})
                print(f"  {mode:<24} nDCG@15 mean={ndcg.get('mean', float('nan')):.4f} (n={ndcg.get('n', 0)})")

    print("\n" + "=" * 70)
    print("BREAKDOWN BY SCRIPT (Urdu vs Roman Urdu)")
    print("=" * 70)
    report["breakdown"]["by_script"] = {}
    for script in ["urdu", "roman"]:
        agg = aggregate(lambda qid, script=script: query_info[qid]["script"] == script)
        if agg:
            report["breakdown"]["by_script"][script] = agg
            print(f"\n-- script={script} --")
            for mode, metrics in agg.items():
                ndcg = metrics.get("nDCG@15", {})
                print(f"  {mode:<24} nDCG@15 mean={ndcg.get('mean', float('nan')):.4f} (n={ndcg.get('n', 0)})")

    print("\n" + "=" * 70)
    print("BREAKDOWN BY QUERY TYPE (bare-event §4 vs anchor)")
    print("=" * 70)
    report["breakdown"]["by_query_type"] = {}
    for qtype_label, qtype_check in [
        ("bare_event", lambda qid: query_info[qid]["rule_type"].startswith("§4")),
        ("anchor", lambda qid: query_info[qid]["tag"] == "anchor"),
    ]:
        agg = aggregate(qtype_check)
        if agg:
            report["breakdown"]["by_query_type"][qtype_label] = agg
            print(f"\n-- {qtype_label} --")
            for mode, metrics in agg.items():
                ndcg = metrics.get("nDCG@15", {})
                print(f"  {mode:<24} nDCG@15 mean={ndcg.get('mean', float('nan')):.4f} (n={ndcg.get('n', 0)})")

    # -------------------------------------------------------------
    # Cross-tabulation against pre_registered_hypothesis (per query)
    # -------------------------------------------------------------
    print("\n" + "=" * 70)
    print("PER-QUERY: FULL_CONTENT vs HEADLINE (nDCG@15) vs pre-registered hypothesis")
    print("=" * 70)
    crosstab = []
    for qid in all_query_ids:
        h = per_query_mode_metrics.get((qid, "HEADLINE"), {}).get("nDCG@15")
        f = per_query_mode_metrics.get((qid, "FULL_CONTENT"), {}).get("nDCG@15")
        if h is None or f is None:
            continue
        diff = f - h
        implied = "LONG" if diff > 0 else ("SHORT" if diff < 0 else "TIE")
        hyp = query_info[qid]["pre_registered_hypothesis"]
        crosstab.append({
            "query_id": qid,
            "word_count": query_info[qid]["word_count"],
            "script": query_info[qid]["script"],
            "tag": query_info[qid]["tag"],
            "headline_nDCG@15": round(h, 4),
            "full_content_nDCG@15": round(f, 4),
            "diff_full_minus_headline": round(diff, 4),
            "implied_by_retrieval": implied,
            "pre_registered_hypothesis": hyp,
            "matches_hypothesis": implied == hyp,
        })
        print(f"  {qid:<8} {query_info[qid]['tag']:<6} headline={h:.3f} full={f:.3f} "
              f"diff={diff:+.3f} implied={implied:<5} pre_registered={hyp:<6} "
              f"{'MATCH' if implied == hyp else 'MISMATCH'}")
    report["crosstab_headline_vs_fullcontent"] = crosstab

    # -------------------------------------------------------------
    # Decision logic (Step 8 / Step 9)
    # -------------------------------------------------------------
    def decide_bucket(query_filter):
        diffs = []
        for qid in all_query_ids:
            if not query_filter(qid):
                continue
            h = per_query_mode_metrics.get((qid, "HEADLINE"), {}).get("nDCG@15")
            f = per_query_mode_metrics.get((qid, "FULL_CONTENT"), {}).get("nDCG@15")
            if h is None or f is None:
                continue
            diffs.append(f - h)  # positive => favors FULL_CONTENT (LONG)

        n = len(diffs)
        if n < MIN_QUERIES_FOR_DECISION:
            return {"verdict": "INSUFFICIENT_DATA", "n_queries": n, "diffs": diffs}

        mean_diff = sum(diffs) / n
        n_favor_long = sum(1 for d in diffs if d > 0)
        n_favor_short = sum(1 for d in diffs if d < 0)
        frac_long = n_favor_long / n
        frac_short = n_favor_short / n

        if mean_diff > DECISION_THRESHOLD and frac_long >= DECISION_MAJORITY_FRACTION:
            verdict = "LONG"
        elif -mean_diff > DECISION_THRESHOLD and frac_short >= DECISION_MAJORITY_FRACTION:
            verdict = "SHORT"
        else:
            verdict = "QUERY-DEPENDENT / INCONCLUSIVE"

        return {
            "verdict": verdict,
            "n_queries": n,
            "mean_diff_full_minus_headline": round(mean_diff, 4),
            "fraction_favoring_LONG": round(frac_long, 3),
            "fraction_favoring_SHORT": round(frac_short, 3),
            "raw_diffs": [round(d, 4) for d in diffs],
        }

    print("\n" + "=" * 70)
    print("DECISION: SHORT vs LONG vs QUERY-DEPENDENT for 5-6 word bare-event queries")
    print("=" * 70)

    decisions = {}
    for wc in WORD_BUCKETS_OF_INTEREST:
        d = decide_bucket(lambda qid, wc=wc: query_info[qid]["word_count"] == wc
                           and query_info[qid]["rule_type"].startswith("§4"))
        decisions[f"{wc}w_bare_event_overall"] = d
        print(f"\n{wc}-word bare-event queries (both scripts): {d['verdict']}  (n={d['n_queries']})")

        for script in ["urdu", "roman"]:
            d_s = decide_bucket(lambda qid, wc=wc, script=script: (
                query_info[qid]["word_count"] == wc
                and query_info[qid]["rule_type"].startswith("§4")
                and query_info[qid]["script"] == script
            ))
            decisions[f"{wc}w_bare_event_{script}"] = d_s
            print(f"  -> {script:<6}: {d_s['verdict']}  (n={d_s['n_queries']})")

    # Combined 5-6w bucket (the core unresolved question)
    d_combined = decide_bucket(lambda qid: query_info[qid]["word_count"] in ("5", "6")
                                and query_info[qid]["rule_type"].startswith("§4"))
    decisions["5_6w_bare_event_combined"] = d_combined
    print(f"\n5-6 word bare-event queries COMBINED: {d_combined['verdict']}  (n={d_combined['n_queries']})")

    report["decision"] = decisions

    with open(DEFAULT_METRICS_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\nFull report (all breakdowns, per-query crosstab, decisions) "
          f"written to {DEFAULT_METRICS_OUTPUT}")
    print("\nThis script does not train, retrain, or modify anything. It "
          "only reports what the judged retrieval evidence shows. If the "
          "verdict is QUERY-DEPENDENT / INCONCLUSIVE, that is a valid, "
          "reportable scientific result -- do not force a binary label "
          "onto it.")


if __name__ == "__main__":
    main()
