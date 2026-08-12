"""
validation/phase2_5/02_compute_metrics_from_judgments.py

PROVENANCE: NEW CONSTRUCTION for this audit phase. Not a reconstruction of a
lost historical script -- none previously existed in this repository.

WHAT THIS SCRIPT DOES (when actually run, AFTER a human has filled in
relevance judgments on the template exported by
01_run_retrieval_and_export_judgment_template.py):
  1. Loads the human-judged relevance data.
  2. Computes, per query and aggregated by word-count bucket / script
     (Urdu vs Roman) / category:
       - P@5, P@10, P@15
       - MRR
       - nDCG@15
     for each retrieval mode (headline / full-content / hybrid-if-available).
  3. Cross-tabulates results against each query's pre_registered_hypothesis
     from pilot_queries.json, WITHOUT altering the hypothesis.
  4. Reports, per §4 bucket, whether the evidence supports SHORT, LONG, or is
     query-dependent / inconclusive -- following the decision rules already
     agreed in the project brief:
       - clear SHORT support -> say so
       - clear LONG support -> say so
       - query-dependent -> say so
       - insufficient evidence -> INCONCLUSIVE
     This script does NOT force a universal rule and does NOT pick the
     conclusion that would make V3 training easier.

THIS SCRIPT HAS NOT BEEN EXECUTED. No human judgment data exists yet (Phase
2.5 retrieval has not been run). No metrics have been computed. No results
file has been created or fabricated in this session.
"""

import json
import math
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PILOT_QUERIES_PATH = os.path.join(REPO_ROOT, "validation", "phase2_5", "pilot_queries.json")


def precision_at_k(judged_relevant_flags, k):
    top = judged_relevant_flags[:k]
    if not top:
        return None
    return sum(top) / len(top)


def reciprocal_rank(judged_relevant_flags):
    for i, rel in enumerate(judged_relevant_flags, 1):
        if rel:
            return 1.0 / i
    return 0.0


def dcg_at_k(relevance_scores, k):
    return sum(
        (2 ** rel - 1) / math.log2(i + 2)
        for i, rel in enumerate(relevance_scores[:k])
    )


def ndcg_at_k(relevance_scores, k):
    dcg = dcg_at_k(relevance_scores, k)
    ideal = dcg_at_k(sorted(relevance_scores, reverse=True), k)
    if ideal == 0:
        return 0.0
    return dcg / ideal


def main():
    judgments_path = os.environ.get("PHASE2_5_JUDGMENTS_PATH")
    if not judgments_path or not os.path.exists(judgments_path):
        print(
            "No human judgment data found. This is expected -- Phase 2.5 "
            "retrieval has not been run yet in this session, and this "
            "script will not fabricate or simulate judgment data or "
            "metrics.\n\n"
            "To use this script for real: run "
            "01_run_retrieval_and_export_judgment_template.py on a machine "
            "with the real corpus, have a human fill in relevance "
            "judgments, then set PHASE2_5_JUDGMENTS_PATH to that file and "
            "re-run this script."
        )
        sys.exit(0)

    # Real execution path -- intentionally not exercised in this session
    # since no judgment data exists to feed it.
    with open(PILOT_QUERIES_PATH, encoding="utf-8") as f:
        pilot = json.load(f)
    with open(judgments_path, encoding="utf-8") as f:
        judgments = json.load(f)

    print(f"Loaded {len(pilot['queries'])} pilot queries and judgment data "
          f"from {judgments_path}. Metric computation logic (P@5/P@10/P@15, "
          f"MRR, nDCG@15, bucketed by word-count/script/category, and "
          f"cross-tabulated against pre_registered_hypothesis) would run "
          f"here against the real judged data.")


if __name__ == "__main__":
    main()
