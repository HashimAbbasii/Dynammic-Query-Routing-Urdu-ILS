"""
validation/phase2_5/01_run_retrieval_and_export_judgment_template.py

PROVENANCE: NEW CONSTRUCTION for this audit phase. Not a reconstruction of a
lost historical script -- no Phase 2.5 infrastructure previously existed in
this repository (verified via `git log --all --diff-filter=A`, zero hits).
Written now per the design already agreed in the prior audit conversation.

WHAT THIS SCRIPT DOES (when actually run, on a machine with the real local
retrieval corpus present):
  1. Loads validation/phase2_5/pilot_queries.json (33 queries).
  2. Loads the retrieval corpus:
       data/clean_articles.csv   (columns: Index, Headline, News Text,
                                   Category, Date, URL, Source, News length,
                                   combined_text)
       data/embeddings.npy       (111860 x 384, paraphrase-multilingual-
                                   MiniLM-L12-v2)
       data/chromadb/            (collection name: "urdu_news")
  3. Reuses the EXISTING retrieval implementation in
     validate/phase4_retrieval_verification.py rather than reinventing one,
     per the hard constraint in the project brief.
  4. For each pilot query, runs retrieval in three modes:
       - headline-only retrieval
       - full-content (combined_text) retrieval
       - hybrid retrieval (if validate/phase4_retrieval_verification.py
         already implements a hybrid mode; otherwise this mode is skipped
         and explicitly marked "not available" in the export, not faked)
  5. Exports a judgment template (CSV/JSON) with the top-K (P@15 minimum)
     retrieved documents per query per mode, WITHOUT any relevance judgment
     filled in -- a human reviewer fills in relevance judgments separately.
     This script does not itself decide relevance or compute metrics; see
     02_compute_metrics_from_judgments.py for that, which runs strictly
     AFTER human judgments exist.

THIS SCRIPT HAS NOT BEEN EXECUTED IN THIS SESSION. The retrieval corpus
(data/clean_articles.csv, data/embeddings.npy, data/chromadb/) is gitignored
and was confirmed ABSENT from this sandboxed environment. Running this
script requires the real local corpus on Hashim's machine. No results file
has been created or fabricated.

Do NOT modify pre_registered_hypothesis in pilot_queries.json based on
anything this script produces. Do NOT hand-pick which mode "wins."
"""

import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PILOT_QUERIES_PATH = os.path.join(REPO_ROOT, "validation", "phase2_5", "pilot_queries.json")
CORPUS_CSV = os.path.join(REPO_ROOT, "data", "clean_articles.csv")
EMBEDDINGS_PATH = os.path.join(REPO_ROOT, "data", "embeddings.npy")
CHROMADB_DIR = os.path.join(REPO_ROOT, "data", "chromadb")
EXISTING_RETRIEVAL_MODULE = os.path.join(REPO_ROOT, "validate", "phase4_retrieval_verification.py")

TOP_K = 15  # covers P@5, P@10, P@15, MRR, nDCG@15 in the downstream metrics script


def check_corpus_available():
    missing = []
    for label, path in [
        ("data/clean_articles.csv", CORPUS_CSV),
        ("data/embeddings.npy", EMBEDDINGS_PATH),
        ("data/chromadb/", CHROMADB_DIR),
    ]:
        if not os.path.exists(path):
            missing.append(label)
    return missing


def load_pilot_queries():
    with open(PILOT_QUERIES_PATH, encoding="utf-8") as f:
        payload = json.load(f)
    return payload["queries"]


def main():
    missing = check_corpus_available()
    if missing:
        print("Retrieval corpus unavailable in this environment.")
        print("Missing:")
        for m in missing:
            print(f"  - {m}")
        print(
            "\nThis is expected in the sandboxed audit environment (corpus is "
            "gitignored). Run this script on the local machine that has the "
            "real corpus. Refusing to fabricate, simulate, or substitute "
            "retrieval results."
        )
        sys.exit(0)

    if not os.path.exists(EXISTING_RETRIEVAL_MODULE):
        print(f"ERROR: expected existing retrieval implementation not found "
              f"at {EXISTING_RETRIEVAL_MODULE}. Refusing to reinvent a new "
              f"retrieval system per project constraints. Stopping.")
        sys.exit(1)

    queries = load_pilot_queries()
    print(f"Loaded {len(queries)} pilot queries.")
    print(f"Would run retrieval (headline / full-content / hybrid-if-available) "
          f"for each, top-{TOP_K}, and export an unjudged template.")
    print("NOTE: retrieval execution logic against the real corpus and "
          "validate/phase4_retrieval_verification.py's actual API is "
          "intentionally not wired up further in this sandboxed session, "
          "since the corpus is absent and there is nothing real to test it "
          "against. Complete the ChromaDB/embedding-loading calls here on "
          "the machine that has data/clean_articles.csv, data/embeddings.npy, "
          "and data/chromadb/ before running for real.")


if __name__ == "__main__":
    main()
