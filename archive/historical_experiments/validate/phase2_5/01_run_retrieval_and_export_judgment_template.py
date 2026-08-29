# -*- coding: utf-8 -*-
"""
validate/phase2_5/01_run_retrieval_and_export_judgment_template.py

PHASE 2.5 -- empirical test of whether 5-6 word bare-event queries behave
like SHORT (headline-sufficient) or LONG (need full article content)
queries. This script performs retrieval only. It NEVER judges relevance,
NEVER computes metrics, and NEVER touches the SVM, training labels, or
V3/V2 training in any way.

PROVENANCE NOTE (replaces the earlier stub version of this file):
An earlier audit session created a version of this script that only
PRINTED what it would do and never actually implemented the retrieval
calls. That was a real gap, not evidence of anything -- it just meant the
promised infrastructure did not exist yet. This version is the actual,
runnable implementation. It still has NOT been executed against the real
corpus (corpus is gitignored / absent in this sandboxed environment), so
no results file has been produced or fabricated by this session either.

METHODOLOGICAL FINDING FROM RE-INSPECTING THE EXISTING CODE (must be
reported, not silently patched around):

notebooks/04_retrieval.ipynb defines `ultra_retrieve()` with a docstring
claiming:
    "Short query: uses CLS pooling on headlines"
    "Long query: uses mean pooling on full content"
...but the actual function body never branches on `query_type` in any
way that changes what is embedded or searched. It always encodes the
query with the same SentenceTransformer call and always queries the same
single ChromaDB collection -- and that collection's documents are
`combined_text` (Headline + " " + News Text), per notebooks/02_embeddings
and notebooks/03_chromadb. In other words: **no true headline-only
semantic index has ever actually existed in this codebase.** The
docstring describes a design that was never implemented.

The only genuinely headline-scoped retrieval that pre-exists (in
validate/phase3_retrieval_verification.py and
validate/phase4_retrieval_verification.py) is TF-IDF keyword search over
the Headline column. That is a different *method* (lexical) from the
full-content path (semantic/embedding), not just a different *scope*
(headline vs. full text). Using "TF-IDF-on-headline vs.
semantic-on-full-content" as the HEADLINE vs. FULL_CONTENT comparison
would confound retrieval method with content scope, and a result showing
"FULL_CONTENT wins" could just mean "semantic search beats TF-IDF",
telling us nothing about whether 5-6 word queries specifically need
article body content.

DESIGN DECISION FOR THIS SCRIPT (stated explicitly so it can be
challenged): to isolate content scope from retrieval method, this script
builds a genuine headline-only SEMANTIC index by encoding the Headline
column with the exact same SentenceTransformer model already used for
the full-content embeddings (paraphrase-multilingual-MiniLM-L12-v2), and
compares it against the existing full-content ChromaDB collection using
the same similarity metric (cosine). This is not a new retrieval
architecture -- it is the existing embedding pipeline applied to a
different field, which is what notebooks/04_retrieval.ipynb's own
docstring already claimed to do. The pre-existing TF-IDF headline search
is preserved and exported too, but labeled explicitly as a DIAGNOSTIC
column, not part of the primary SHORT/LONG evidence, to avoid the
method/scope confound above.

Retrieval modes exported per pilot query (top-15 each):
  HEADLINE            - semantic search, query embedding vs. headline-only
                         embeddings (primary; isolates content scope)
  FULL_CONTENT         - semantic search, query embedding vs. existing
                         ChromaDB collection (combined_text embeddings)
  HYBRID               - 0.5/0.5 normalized-score fusion of HEADLINE and
                         FULL_CONTENT (both semantic, so this is a clean
                         scope-fusion, not a method-fusion)
  HEADLINE_KEYWORD_TFIDF (diagnostic only, NOT used for the SHORT/LONG
                         decision in script 02 by default) - TF-IDF
                         cosine over headlines, reusing the exact
                         implementation from
                         validate/phase4_retrieval_verification.py

Requires (on the machine with the real corpus):
    pip install pandas numpy chromadb sentence-transformers scikit-learn torch
"""

import csv
import hashlib
import json
import os
import platform
import sys
from datetime import datetime, timezone

import numpy as np

# ---------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PHASE2_5_DIR = os.path.join(REPO_ROOT, "validate", "phase2_5")
PILOT_QUERIES_PATH = os.path.join(PHASE2_5_DIR, "pilot_queries.json")

CORPUS_CSV = os.path.join(REPO_ROOT, "data", "clean_articles.csv")
EMBEDDINGS_PATH = os.path.join(REPO_ROOT, "data", "embeddings.npy")
CHROMADB_DIR = os.path.join(REPO_ROOT, "data", "chromadb")
CHROMADB_COLLECTION_NAME = "urdu_news"

# New cache file this script creates the first time it runs -- NOT the
# committed embeddings.npy (that one is combined_text, per
# notebooks/02_embeddings.ipynb). This one is headline-only. Cached so
# repeat runs don't re-encode ~112k headlines every time.
HEADLINE_EMBEDDINGS_CACHE = os.path.join(REPO_ROOT, "data", "headline_embeddings_phase2_5_cache.npy")

JUDGMENT_TEMPLATE_PATH = os.path.join(PHASE2_5_DIR, "judgment_template.csv")
RUN_METADATA_PATH = os.path.join(PHASE2_5_DIR, "run_metadata.json")

TOP_K = 15  # covers P@5, P@10, P@15, MRR, nDCG@15 downstream
EMBEDDING_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

HEADLINE_COL = "Headline"
CATEGORY_COL = "Category"
COMBINED_COL = "combined_text"


# ---------------------------------------------------------------------
# Corpus availability check -- hard stop, no fabrication
# ---------------------------------------------------------------------
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
    return payload["queries"], payload.get("categories_used", [])


def file_sha256(path, chunk_size=8192):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------
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
            "retrieval results.\n"
            "\nOn the local machine, run from the repo root:\n"
            "    pip install pandas numpy chromadb sentence-transformers scikit-learn torch\n"
            "    python validate/phase2_5/01_run_retrieval_and_export_judgment_template.py\n"
        )
        sys.exit(0)

    import pandas as pd
    import chromadb
    from sentence_transformers import SentenceTransformer
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import torch

    run_started_at = datetime.now(timezone.utc).isoformat()

    print("[1/7] Loading clean_articles.csv...", flush=True)
    df = pd.read_csv(CORPUS_CSV, encoding="utf-8-sig")
    print(f"      Loaded {len(df)} rows. Columns: {list(df.columns)}", flush=True)
    for required_col in (HEADLINE_COL, CATEGORY_COL, COMBINED_COL):
        if required_col not in df.columns:
            print(f"ERROR: expected column '{required_col}' not found in "
                  f"clean_articles.csv. Found: {list(df.columns)}. Stopping "
                  f"-- refusing to guess an alternate schema.")
            sys.exit(1)

    print("[2/7] Loading embeddings.npy (combined_text embeddings)...", flush=True)
    fullcontent_embeddings = np.load(EMBEDDINGS_PATH)
    print(f"      Shape: {fullcontent_embeddings.shape}", flush=True)
    if fullcontent_embeddings.shape[0] != len(df):
        print(f"WARNING: embeddings.npy has {fullcontent_embeddings.shape[0]} "
              f"rows but clean_articles.csv has {len(df)} rows. Row-index "
              f"alignment between CSV and embeddings/ChromaDB IDs may be "
              f"broken. Proceeding, but treat retrieval results with "
              f"caution and report this mismatch.")

    print("[3/7] Connecting to ChromaDB...", flush=True)
    client = chromadb.PersistentClient(path=CHROMADB_DIR)
    try:
        collection = client.get_collection(CHROMADB_COLLECTION_NAME)
    except Exception as e:
        print(f"ERROR: could not open ChromaDB collection "
              f"'{CHROMADB_COLLECTION_NAME}' at {CHROMADB_DIR}: {e}")
        sys.exit(1)
    chroma_count = collection.count()
    print(f"      {chroma_count} documents in collection.", flush=True)

    print("[4/7] Loading SentenceTransformer model...", flush=True)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    sem_model = SentenceTransformer(EMBEDDING_MODEL_NAME, device=device)
    print(f"      Ready on {device}.", flush=True)

    print("[5/7] Building/loading headline-only semantic embeddings "
          "(this is NEW -- no headline-only embedding index previously "
          "existed in this repo; see script docstring)...", flush=True)
    if os.path.exists(HEADLINE_EMBEDDINGS_CACHE):
        headline_embeddings = np.load(HEADLINE_EMBEDDINGS_CACHE)
        if headline_embeddings.shape[0] != len(df):
            print("      Cache row count doesn't match current corpus size; "
                  "re-encoding headlines.", flush=True)
            headline_embeddings = None
        else:
            print(f"      Loaded cached headline embeddings, shape "
                  f"{headline_embeddings.shape}.", flush=True)
    else:
        headline_embeddings = None

    if headline_embeddings is None:
        headlines = df[HEADLINE_COL].fillna("").astype(str).tolist()
        print(f"      Encoding {len(headlines)} headlines with "
              f"{EMBEDDING_MODEL_NAME} (one-time cost, cached afterward)...",
              flush=True)
        headline_embeddings = sem_model.encode(
            headlines, batch_size=64, show_progress_bar=True, convert_to_numpy=True
        )
        np.save(HEADLINE_EMBEDDINGS_CACHE, headline_embeddings)
        print(f"      Saved cache to {HEADLINE_EMBEDDINGS_CACHE}", flush=True)

    print("[6/7] Building TF-IDF keyword index over headlines "
          "(diagnostic mode only; reused verbatim from "
          "validate/phase4_retrieval_verification.py)...", flush=True)
    headline_corpus = df[HEADLINE_COL].fillna("").astype(str).tolist()
    tfidf = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4), max_features=50000)
    tfidf_matrix = tfidf.fit_transform(headline_corpus)
    print(f"      TF-IDF shape: {tfidf_matrix.shape}", flush=True)

    # -------------------------------------------------------------
    # Retrieval functions
    # -------------------------------------------------------------
    def headline_keyword_search(query, top_k=TOP_K):
        qv = tfidf.transform([query])
        sims = cosine_similarity(qv, tfidf_matrix)[0]
        idx = np.argsort(-sims)[:top_k]
        return [(int(i), float(sims[i])) for i in idx]

    def headline_semantic_search(query, top_k=TOP_K):
        qemb = sem_model.encode(query)
        sims = cosine_similarity([qemb], headline_embeddings)[0]
        idx = np.argsort(-sims)[:top_k]
        return [(int(i), float(sims[i])) for i in idx]

    def fullcontent_semantic_search(query, top_k=TOP_K):
        qemb = sem_model.encode(query).tolist()
        res = collection.query(query_embeddings=[qemb], n_results=top_k)
        ids = [int(x) for x in res["ids"][0]]
        dists = res["distances"][0]
        sims = [1 - d for d in dists]
        return list(zip(ids, sims))

    def _normalize(pairs):
        if not pairs:
            return {}
        d = dict(pairs)
        vals = np.array(list(d.values()))
        lo, hi = vals.min(), vals.max()
        rng = hi - lo if hi > lo else 1.0
        return {k: (v - lo) / rng for k, v in d.items()}

    def hybrid_semantic_search(query, top_k=TOP_K, alpha=0.5):
        # Fuses HEADLINE (semantic) and FULL_CONTENT (semantic) -- both
        # the same method, different content scope. Deliberately NOT
        # fusing in the TF-IDF keyword scores here, to avoid re-mixing
        # method with scope in the primary comparison.
        head = dict(headline_semantic_search(query, top_k=50))
        full = dict(fullcontent_semantic_search(query, top_k=50))
        all_ids = set(head) | set(full)
        head_n, full_n = _normalize(head), _normalize(full)
        scores = {i: alpha * full_n.get(i, 0) + (1 - alpha) * head_n.get(i, 0) for i in all_ids}
        return sorted(scores.items(), key=lambda x: -x[1])[:top_k]

    corpus_categories = set(df[CATEGORY_COL].dropna().astype(str).unique().tolist())

    def is_invalid_no_corpus_match(category):
        return category not in corpus_categories

    def is_tied_or_zero(ranked):
        if not ranked:
            return True
        scores = [s for _, s in ranked]
        if all(s == 0 for s in scores):
            return True
        if len(set(round(s, 8) for s in scores)) == 1:
            return True
        return False

    # -------------------------------------------------------------
    # Run retrieval for every pilot query x every mode
    # -------------------------------------------------------------
    print("[7/7] Running retrieval for all pilot queries "
          "(HEADLINE / FULL_CONTENT / HYBRID / HEADLINE_KEYWORD_TFIDF)...",
          flush=True)

    pilot_queries, categories_used = load_pilot_queries()
    print(f"      Loaded {len(pilot_queries)} pilot queries.", flush=True)

    rows = []
    for q in pilot_queries:
        query_id = q.get("id") or q.get("query_id")
        query_text = q["query"]
        category = q.get("category", "")
        invalid = is_invalid_no_corpus_match(category)

        modes = {
            "HEADLINE": headline_semantic_search(query_text),
            "FULL_CONTENT": fullcontent_semantic_search(query_text),
            "HYBRID": hybrid_semantic_search(query_text),
            "HEADLINE_KEYWORD_TFIDF": headline_keyword_search(query_text),
        }

        for mode_name, ranked in modes.items():
            tie_flag = is_tied_or_zero(ranked)
            for rank, (doc_idx, score) in enumerate(ranked, start=1):
                if 0 <= doc_idx < len(df):
                    doc_row = df.iloc[doc_idx]
                    doc_headline = str(doc_row[HEADLINE_COL])[:120]
                    doc_category = str(doc_row[CATEGORY_COL])
                else:
                    doc_headline = "<INDEX_OUT_OF_RANGE>"
                    doc_category = "<UNKNOWN>"

                rows.append({
                    "query_id": query_id,
                    "query": query_text,
                    "word_count": q.get("word_count"),
                    "script": q.get("script"),
                    "rule_type": q.get("rule_type"),
                    "tag": q.get("tag"),
                    "category": category,
                    "pre_registered_hypothesis": q.get("pre_registered_hypothesis"),
                    "retrieval_mode": mode_name,
                    "rank": rank,
                    "doc_id": doc_idx,
                    "doc_headline": doc_headline,
                    "doc_category": doc_category,
                    "score": round(score, 6),
                    "invalid_no_corpus_match": invalid,
                    "tied_or_zero_similarity_flag": tie_flag,
                    "relevance": "UNJUDGED",
                })

    with open(JUDGMENT_TEMPLATE_PATH, "w", newline="", encoding="utf-8-sig") as f:
        fieldnames = list(rows[0].keys())
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nWrote {len(rows)} rows ({len(pilot_queries)} queries x 4 modes x "
          f"up to {TOP_K} ranks) to {JUDGMENT_TEMPLATE_PATH}", flush=True)
    print("Every row has relevance = UNJUDGED. A human reviewer must fill "
          "these in (Relevant / Partially relevant / Not relevant) before "
          "running 02_compute_metrics_from_judgments.py.", flush=True)
    print("NOTE: HEADLINE_KEYWORD_TFIDF is exported for completeness/"
          "diagnostics but is excluded from the primary SHORT/LONG decision "
          "logic by default in script 02 (method/scope confound -- see "
          "script docstring).", flush=True)

    # -------------------------------------------------------------
    # Reproducibility metadata
    # -------------------------------------------------------------
    metadata = {
        "run_started_at_utc": run_started_at,
        "run_finished_at_utc": datetime.now(timezone.utc).isoformat(),
        "python_version": sys.version,
        "platform": platform.platform(),
        "embedding_model": EMBEDDING_MODEL_NAME,
        "device": device,
        "top_k": TOP_K,
        "corpus_csv_path": CORPUS_CSV,
        "corpus_csv_sha256": file_sha256(CORPUS_CSV),
        "corpus_row_count": len(df),
        "embeddings_npy_shape": list(fullcontent_embeddings.shape),
        "chromadb_collection": CHROMADB_COLLECTION_NAME,
        "chromadb_document_count": chroma_count,
        "headline_embeddings_cache_path": HEADLINE_EMBEDDINGS_CACHE,
        "headline_embeddings_shape": list(headline_embeddings.shape),
        "pilot_queries_path": PILOT_QUERIES_PATH,
        "pilot_queries_sha256": file_sha256(PILOT_QUERIES_PATH),
        "num_pilot_queries": len(pilot_queries),
        "retrieval_modes_exported": ["HEADLINE", "FULL_CONTENT", "HYBRID", "HEADLINE_KEYWORD_TFIDF"],
        "primary_modes_for_short_long_decision": ["HEADLINE", "FULL_CONTENT", "HYBRID"],
        "diagnostic_only_modes": ["HEADLINE_KEYWORD_TFIDF"],
        "categories_in_corpus": sorted(corpus_categories),
        "categories_used_in_pilot": categories_used,
    }
    with open(RUN_METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"Wrote reproducibility metadata to {RUN_METADATA_PATH}", flush=True)


if __name__ == "__main__":
    main()
