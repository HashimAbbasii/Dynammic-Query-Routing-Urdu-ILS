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
from router import (  # noqa: E402
    FULL_CONTENT,
    HEADLINE,
    HYBRID,
    decide,
    svm_v2_label,
)

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


def _normalize(pairs):
    if not pairs:
        return {}
    d = dict(pairs)
    vals = np.array(list(d.values()), dtype=float)
    lo, hi = float(vals.min()), float(vals.max())
    rng = hi - lo if hi > lo else 1.0
    return {k: (v - lo) / rng for k, v in d.items()}


def search_hybrid(query: str, top_k: int = 15, alpha: float = 0.5):
    """MEDIUM light: same method, mix headline room + full-article room."""
    head = dict(search_headlines(query, top_k=50))
    full = dict(search_full_content(query, top_k=50))
    all_ids = set(head) | set(full)
    head_n, full_n = _normalize(head), _normalize(full)
    scores = {
        i: alpha * full_n.get(i, 0.0) + (1.0 - alpha) * head_n.get(i, 0.0)
        for i in all_ids
    }
    return sorted(scores.items(), key=lambda x: -x[1])[:top_k]


def expand_query(query: str) -> str:
    """LOW light: add a few extra words so search is wider, not a new model."""
    urdu = sum(1 for c in query if "\u0600" <= c <= "\u06FF")
    if urdu > 0:
        extra = "تفصیل وجوہات"
    else:
        extra = "detail reasons news"
    if extra in query:
        return query
    return f"{query} {extra}"


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


def ultra_retrieve_dynamic(
    query: str,
    top_k: int = 15,
    system: str = "svm_v2",
    use_confidence_tiers: bool = True,
):
    """
    End-to-end replacement for ULTRA static routing.

    1. Optional Roman Urdu dictionary transliteration
    2. SVM (or a baseline) chooses SHORT vs LONG
    3. If use_confidence_tiers and system is svm_v2:
         HIGH   -> one room (headline or full)
         MEDIUM -> hybrid (both rooms)
         LOW    -> expand query, then hybrid
       Baselines (wordcount / theta150) have no light; they always use one room.
    """
    processed, was_roman = transliterate_roman(query)
    decision = decide(processed, system)
    label = decision["label"]
    one_room = decision["mode"]
    tier = decision["tier"]
    search_query = processed
    expanded = False
    action = one_room

    if system == "svm_v2" and use_confidence_tiers and tier is not None:
        if tier == "HIGH":
            action = one_room
            if one_room == HEADLINE:
                ranked = search_headlines(search_query, top_k=top_k)
            else:
                ranked = search_full_content(search_query, top_k=top_k)
        elif tier == "MEDIUM":
            action = HYBRID
            ranked = search_hybrid(search_query, top_k=top_k)
        else:
            action = "EXPAND_THEN_HYBRID"
            search_query = expand_query(processed)
            expanded = True
            ranked = search_hybrid(search_query, top_k=top_k)
    else:
        if one_room == HEADLINE:
            ranked = search_headlines(search_query, top_k=top_k)
        else:
            ranked = search_full_content(search_query, top_k=top_k)

    hits = _format_hits(ranked)
    return {
        "raw_query": query,
        "processed_query": processed,
        "search_query": search_query,
        "roman_transliterated": was_roman,
        "query_expanded": expanded,
        "system": system,
        "label": label,
        "svm_room": one_room,
        "action": action,
        "mode": action,
        "confidence": decision["confidence"],
        "tier": tier,
        "use_confidence_tiers": use_confidence_tiers,
        "svm_label_on_raw": svm_v2_label(query)[0] if system == "svm_v2" else None,
        "results": hits,
    }
