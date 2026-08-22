# -*- coding: utf-8 -*-
"""
Dual-index retrieval: SHORT -> headline semantic search,
LONG -> full-article semantic search.

Replaces the old ultra_retrieve() behaviour, which labelled queries with
θ=150 but always searched the same combined_text Chroma collection.
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np

_DIR = os.path.dirname(os.path.abspath(__file__))
if _DIR not in sys.path:
    sys.path.insert(0, _DIR)
from router import HEADLINE, FULL_CONTENT, decide, svm_v2_label  # noqa: E402

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
HEADLINE_CACHE = os.path.join(REPO_ROOT, "data", "headline_embeddings_phase2_5_cache.npy")
CORPUS_CSV = os.path.join(REPO_ROOT, "data", "clean_articles.csv")
CHROMA_PATH = os.path.join(REPO_ROOT, "data", "chromadb")
DICT_PATH = os.path.join(REPO_ROOT, "models", "roman_urdu_dict_expanded.json")

_state = {}


def _urdu_ratio(query: str) -> float:
    urdu = sum(1 for c in query if "\u0600" <= c <= "\u06FF")
    latin = sum(1 for c in query if ("a" <= c.lower() <= "z"))
    return urdu / max(1, urdu + latin)


def transliterate_roman(query: str) -> tuple[str, bool]:
    if _urdu_ratio(query) >= 0.3:
        return query, False
    if "roman_dict" not in _state:
        with open(DICT_PATH, encoding="utf-8") as f:
            _state["roman_dict"] = json.load(f)
    d = _state["roman_dict"]
    toks = query.split()
    out = [d.get(t.lower(), t) for t in toks]
    new = " ".join(out)
    return new, new != query


def _ensure_indexes(top_k_default=15):
    if "sem_model" in _state:
        return
    import pandas as pd
    import chromadb
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity

    import torch

    device = "cuda" if torch.cuda.is_available() else "cpu"
    _state["sem_model"] = SentenceTransformer(
        "paraphrase-multilingual-MiniLM-L12-v2", device=device
    )
    _state["cosine_similarity"] = cosine_similarity
    df = pd.read_csv(CORPUS_CSV, encoding="utf-8-sig")
    _state["df"] = df
    if not os.path.isfile(HEADLINE_CACHE):
        raise FileNotFoundError(
            f"Headline index cache missing: {HEADLINE_CACHE}. "
            "Run validate/phase2_5/01_run_retrieval_and_export_judgment_template.py once."
        )
    _state["headline_embeddings"] = np.load(HEADLINE_CACHE)
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    _state["collection"] = client.get_collection("urdu_news")
    _state["top_k_default"] = top_k_default


def search_headlines(query: str, top_k: int = 15):
    _ensure_indexes()
    qemb = _state["sem_model"].encode(query)
    sims = _state["cosine_similarity"]([qemb], _state["headline_embeddings"])[0]
    idx = np.argsort(-sims)[:top_k]
    return [(int(i), float(sims[i])) for i in idx]


def search_full_content(query: str, top_k: int = 15):
    _ensure_indexes()
    qemb = _state["sem_model"].encode(query).tolist()
    res = _state["collection"].query(query_embeddings=[qemb], n_results=top_k)
    ids = [int(x) for x in res["ids"][0]]
    dists = res["distances"][0]
    sims = [1.0 - d for d in dists]
    return list(zip(ids, sims))


def _format_hits(ranked):
    df = _state["df"]
    out = []
    for rank, (doc_id, score) in enumerate(ranked, 1):
        row = df.iloc[doc_id]
        out.append({
            "rank": rank,
            "doc_id": doc_id,
            "headline": str(row.get("Headline", ""))[:180],
            "category": str(row.get("Category", "")),
            "score": score,
        })
    return out


def ultra_retrieve_dynamic(query: str, top_k: int = 15, system: str = "svm_v2"):
    """
    End-to-end replacement for ULTRA static routing.

    1. Optional Roman Urdu dictionary transliteration
    2. Router chooses SHORT (headlines) or LONG (full content)
    3. Semantic search on the chosen index only
    """
    processed, was_roman = transliterate_roman(query)
    decision = decide(processed, system)
    mode = decision["mode"]
    if mode == HEADLINE:
        ranked = search_headlines(processed, top_k=top_k)
    else:
        ranked = search_full_content(processed, top_k=top_k)
    hits = _format_hits(ranked)
    return {
        "raw_query": query,
        "processed_query": processed,
        "roman_transliterated": was_roman,
        "system": system,
        "label": decision["label"],
        "mode": mode,
        "confidence": decision["confidence"],
        "svm_label_on_raw": svm_v2_label(query)[0] if system == "svm_v2" else None,
        "results": hits,
    }
