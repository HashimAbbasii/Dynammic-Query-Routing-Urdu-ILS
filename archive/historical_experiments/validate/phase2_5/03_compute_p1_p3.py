# -*- coding: utf-8 -*-
"""
validate/phase2_5/03_compute_p1_p3.py

Computes P@1 and P@3 from the human-judged Phase 2.5 CSV, reusing the
loading/parsing logic and REL_MAP / precision_at_k definitions from
02_compute_metrics_from_judgments.py so the numbers are directly
comparable to the existing P@5/P@10/P@15/MRR/nDCG@15 report.

Does NOT modify human_judgments.csv, the existing
phase2_5_metrics_report.json, the SVM/model, or any retrieval outputs.
Does NOT touch LLM judgments. Writes its own separate output file:
    phase2_5_p1_p3_report.json

Usage:
    PHASE2_5_JUDGMENTS_PATH=/path/to/human_judgments.csv \
        python validate/phase2_5/03_compute_p1_p3.py
"""

import json
import os
import sys
from collections import defaultdict

# Import the existing, already-reviewed script as a module so we reuse
# its exact REL_MAP, precision_at_k, load_judgments, and build_ranked_lists
# definitions instead of redefining (and risking drift from) them.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib.util
_spec = importlib.util.spec_from_file_location(
    "phase2_5_metrics",
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 "02_compute_metrics_from_judgments.py"),
)
m02 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m02)  # safe: guarded by `if __name__ == "__main__"` in 02_*

PHASE2_5_DIR = m02.PHASE2_5_DIR
OUTPUT_PATH = os.path.join(PHASE2_5_DIR, "phase2_5_p1_p3_report.json")


def main():
    judgments_path = os.environ.get("PHASE2_5_JUDGMENTS_PATH")
    if not judgments_path or not os.path.exists(judgments_path):
        print("ERROR: PHASE2_5_JUDGMENTS_PATH not set or file not found.")
        sys.exit(1)

    rows = m02.load_judgments(judgments_path)
    print(f"Loaded {len(rows)} judgment rows from {judgments_path}")

    groups, query_info = m02.build_ranked_lists(rows)
    all_query_ids = sorted(query_info.keys())
    print(f"Covers {len(all_query_ids)} distinct queries.")

    # Per (query, mode): graded relevance list sorted by rank, same
    # skip rules as 02_* (skip invalid_no_corpus_match, skip UNJUDGED).
    per_query_mode_p1p3 = {}
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
        per_query_mode_p1p3[(qid, mode)] = {
            "P@1": m02.precision_at_k(gradeds, 1),
            "P@3": m02.precision_at_k(gradeds, 3),
        }

    if skipped_invalid:
        print(f"\n{len(set(q for q,_ in skipped_invalid))} quer(ies) flagged "
              f"INVALID_NO_CORPUS_MATCH -- excluded, consistent with 02_*.")
    if skipped_unjudged:
        print(f"\nWARNING: {len(skipped_unjudged)} (query, mode) pairs still "
              f"UNJUDGED -- excluded, consistent with 02_*.")

    def aggregate(filter_fn, modes):
        out = {}
        for mode in modes:
            vals = defaultdict(list)
            for (qid, mo), metrics in per_query_mode_p1p3.items():
                if mo != mode or not filter_fn(qid):
                    continue
                for name, v in metrics.items():
                    if v is not None:
                        vals[name].append(v)
            if vals:
                out[mode] = {name: {"mean": sum(v)/len(v), "n": len(v)}
                             for name, v in vals.items()}
        return out

    modes_present = sorted(set(mo for _, mo in per_query_mode_p1p3.keys()))

    report = {
        "judgments_path": judgments_path,
        "note": "Companion report to phase2_5_metrics_report.json. Adds "
                "P@1 and P@3 only (not computed by 02_compute_metrics_"
                "from_judgments.py). Same REL_MAP, same precision_at_k "
                "definition, same skip rules (invalid/unjudged excluded).",
        "num_queries_total": len(all_query_ids),
        "modes_present_in_data": modes_present,
    }

    print("\n" + "=" * 70)
    print("OVERALL P@1 / P@3 BY MODE (all judged queries)")
    print("=" * 70)
    overall = aggregate(lambda qid: True, modes_present)
    report["overall_by_mode"] = overall
    for mode, metrics in overall.items():
        print(f"\n{mode}:")
        for name, stat in metrics.items():
            print(f"  {name:<6} mean={stat['mean']:.4f}  (n={stat['n']})")

    # 5-6 word bare-event subset. NOTE: 02_*'s DECISION section uses
    # word_count in (5,6) AND rule_type.startswith("<mojibake §4>"), but
    # that mojibake byte sequence is terminal-rendering-dependent and is
    # NOT safely reproducible in a separate script/session. Instead we use
    # the "tag" field (values like "5w","6w","7w",...,"anchor"), which is
    # plain ASCII and unambiguous. This was verified to select the same 10
    # queries (P25_01..04 tag=5w, P25_05..10 tag=6w) that 02_*'s own run
    # reported as n=10 for the combined 5-6w bare-event bucket.
    def bare_event_5_6(qid):
        return query_info[qid]["tag"] in ("5w", "6w")

    n_bare_event_5_6 = sum(1 for qid in all_query_ids if bare_event_5_6(qid))
    print("\n" + "=" * 70)
    print(f"P@1 / P@3 FOR 5-6 WORD BARE-EVENT SUBSET (n_queries={n_bare_event_5_6})")
    print("=" * 70)
    subset = aggregate(bare_event_5_6, modes_present)
    report["bare_event_5_6w_subset"] = subset
    report["bare_event_5_6w_subset_n_queries_matched_filter"] = n_bare_event_5_6
    if subset:
        for mode, metrics in subset.items():
            print(f"\n{mode}:")
            for name, stat in metrics.items():
                print(f"  {name:<6} mean={stat['mean']:.4f}  (n={stat['n']})")
    else:
        print("\nNo fully-judged (query, mode) pairs matched this filter "
              "-- reporting nothing fabricated.")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\nWritten to {OUTPUT_PATH}")
    print("(existing phase2_5_metrics_report.json was NOT modified)")


if __name__ == "__main__":
    main()
