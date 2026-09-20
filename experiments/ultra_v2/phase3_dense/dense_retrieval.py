# -*- coding: utf-8 -*-
"""Zero-shot dense retrieval helpers for ULTRA v2 DENSE-BASELINE.

Isolated under experiments/ultra_v2/phase3_dense/. Does not edit M0, R2, or TEST.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from typing import Iterable

os.environ.setdefault("MKL_THREADING_LAYER", "SEQUENTIAL")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import numpy as np

MODEL_ID = "intfloat/multilingual-e5-small"
MODEL_REVISION = "8d923955b027282ba975c0a4c825486c9ca4c490"
EMBED_DIM = 384
MAX_SEQ_LENGTH = 512
QUERY_PREFIX = "query: "
PASSAGE_PREFIX = "passage: "
ENCODE_BATCH_SIZE = 64
TOP_K = 50
HIT_K = 5
EXPECTED_CORPUS_SHA = "8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231"
EXPECTED_N_DOCS = 111860


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(1024 * 1024)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def l2_normalize(mat: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    norms = np.linalg.norm(mat, axis=1, keepdims=True)
    return (mat / np.maximum(norms, eps)).astype(np.float32, copy=False)


def prefixed(texts: Iterable[str], prefix: str) -> list[str]:
    return [prefix + (t or "") for t in texts]


def load_encoder():
    import torch
    from sentence_transformers import SentenceTransformer

    torch.set_num_threads(max(1, os.cpu_count() or 1))
    model = SentenceTransformer(
        MODEL_ID,
        revision=MODEL_REVISION,
        device="cpu",
    )
    model.max_seq_length = MAX_SEQ_LENGTH
    model.eval()
    prompts = getattr(model, "prompts", None) or {}
    # Apply documented prefixes exactly once. Empty ST prompt strings do not count.
    def _is_query_prefix(val: object) -> bool:
        s = str(val)
        return s == QUERY_PREFIX or s.strip() == QUERY_PREFIX.strip()

    def _is_passage_prefix(val: object) -> bool:
        s = str(val)
        return s == PASSAGE_PREFIX or s.strip() == PASSAGE_PREFIX.strip()

    auto_query = any(_is_query_prefix(v) for v in (prompts.values() if isinstance(prompts, dict) else []))
    auto_passage = any(_is_passage_prefix(v) for v in (prompts.values() if isinstance(prompts, dict) else []))
    prefix_mode = "manual_concat"
    query_prompt_name = None
    passage_prompt_name = None
    if isinstance(prompts, dict) and _is_query_prefix(prompts.get("query", None)):
        p_name = "passage" if "passage" in prompts else ("document" if "document" in prompts else None)
        if p_name and _is_passage_prefix(prompts.get(p_name)):
            prefix_mode = "sentence_transformers_prompt_name"
            query_prompt_name = "query"
            passage_prompt_name = p_name
    if prefix_mode == "manual_concat":
        # Prevent empty ST prompts from replacing the frozen E5 prefixes.
        try:
            model.default_prompt_name = None
        except Exception:
            pass
    info = {
        "model_id": MODEL_ID,
        "model_revision_pinned": MODEL_REVISION,
        "embedding_dimension_expected": EMBED_DIM,
        "max_seq_length": int(model.max_seq_length),
        "prefix_mode": prefix_mode,
        "query_prefix": QUERY_PREFIX,
        "passage_prefix": PASSAGE_PREFIX,
        "query_prompt_name": query_prompt_name,
        "passage_prompt_name": passage_prompt_name,
        "st_prompts": {k: str(v) for k, v in (prompts.items() if isinstance(prompts, dict) else [])},
        "auto_query_prefix_detected": bool(auto_query),
        "auto_passage_prefix_detected": bool(auto_passage),
        "pooling": "mean (SentenceTransformer module / E5 default)",
        "normalize_embeddings": True,
        "similarity": "cosine (inner product of L2-normalized vectors)",
        "encode_batch_size": ENCODE_BATCH_SIZE,
        "device": "cpu",
    }
    return model, info


def encode_texts(
    model,
    texts: list[str],
    *,
    kind: str,
    prefix_mode: str,
    prompt_name: str | None,
    batch_size: int = ENCODE_BATCH_SIZE,
    show_progress: bool = True,
) -> np.ndarray:
    if kind not in ("query", "passage"):
        raise ValueError("kind must be query or passage")
    prefix = QUERY_PREFIX if kind == "query" else PASSAGE_PREFIX
    if prefix_mode == "sentence_transformers_prompt_name" and prompt_name:
        payload = list(texts)
        kwargs = {"prompt_name": prompt_name}
    else:
        payload = prefixed(texts, prefix)
        kwargs = {}
    vecs = model.encode(
        payload,
        batch_size=batch_size,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=show_progress,
        **kwargs,
    )
    arr = np.asarray(vecs, dtype=np.float32)
    if arr.ndim != 2:
        raise RuntimeError("encoder returned unexpected shape %s" % (arr.shape,))
    if arr.shape[1] != EMBED_DIM:
        raise RuntimeError("embedding dim %s != frozen %s" % (arr.shape[1], EMBED_DIM))
    return l2_normalize(arr)


def load_corpus_texts(corpus_path: str) -> tuple[list[str], dict]:
    import pandas as pd

    df = pd.read_csv(corpus_path, encoding="utf-8-sig")
    if "combined_text" in df.columns:
        texts = df["combined_text"].fillna("").astype(str).tolist()
        source_col = "combined_text"
    else:
        texts = (
            df["Headline"].fillna("").astype(str)
            + " "
            + df["News Text"].fillna("").astype(str)
        ).tolist()
        source_col = "Headline+News Text"
    n = len(texts)
    if n != EXPECTED_N_DOCS:
        raise SystemExit("BLOCKED — corpus size %s != %s" % (n, EXPECTED_N_DOCS))
    n_empty = sum(1 for t in texts if not t.strip())
    char_lens = np.fromiter((len(t) for t in texts), dtype=np.int32, count=n)
    ws_lens = np.fromiter((len(t.split()) for t in texts), dtype=np.int32, count=n)
    hashes = [hashlib.sha256(t.encode("utf-8")).hexdigest() for t in texts]
    from collections import Counter

    counts = Counter(hashes)
    n_unique = len(counts)
    dup_groups = {h: c for h, c in counts.items() if c > 1}
    extra_copies = sum(c - 1 for c in dup_groups.values())
    stats = {
        "n_docs": n,
        "text_column": source_col,
        "n_empty": n_empty,
        "char_len_mean": float(char_lens.mean()),
        "char_len_median": float(np.median(char_lens)),
        "char_len_max": int(char_lens.max()),
        "whitespace_tokens_mean": float(ws_lens.mean()),
        "whitespace_tokens_median": float(np.median(ws_lens)),
        "n_unique_texts": n_unique,
        "n_exact_duplicate_groups": len(dup_groups),
        "n_exact_duplicate_extra_copies": extra_copies,
        "deduplicated_for_index": False,
        "note": "Exact duplicates reported only. Frozen corpus is not modified.",
    }
    return texts, stats


def embed_corpus(
    model,
    texts: list[str],
    encoder_info: dict,
    out_npy: str,
    progress_json: str,
    chunk: int = 2048,
) -> np.ndarray:
    os.makedirs(os.path.dirname(out_npy), exist_ok=True)
    n = len(texts)
    dim = EMBED_DIM
    mem_path = os.path.join(os.path.dirname(out_npy), "dense_doc_embeddings.memmap")
    start = 0
    if os.path.isfile(mem_path) and os.path.isfile(progress_json):
        with open(progress_json, encoding="utf-8") as f:
            prog = json.load(f)
        if (
            prog.get("model_id") == MODEL_ID
            and prog.get("model_revision") == MODEL_REVISION
            and prog.get("n_docs") == n
            and prog.get("dim") == dim
            and prog.get("prefix_mode") == encoder_info.get("prefix_mode")
        ):
            start = int(prog.get("next_index", 0))
            if start > n:
                start = 0
            print("resume corpus embed at %s/%s" % (start, n), flush=True)
        else:
            start = 0
            print("progress meta mismatch; restarting corpus embed", flush=True)
    mode = "r+" if start > 0 and os.path.isfile(mem_path) else "w+"
    mm = np.memmap(mem_path, dtype=np.float32, mode=mode, shape=(n, dim))
    t0 = time.perf_counter()
    prefix_mode = encoder_info["prefix_mode"]
    prompt_name = encoder_info.get("passage_prompt_name")
    i = start
    while i < n:
        j = min(i + chunk, n)
        vecs = encode_texts(
            model,
            texts[i:j],
            kind="passage",
            prefix_mode=prefix_mode,
            prompt_name=prompt_name,
            batch_size=ENCODE_BATCH_SIZE,
            show_progress=True,
        )
        mm[i:j] = vecs
        mm.flush()
        with open(progress_json, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "model_id": MODEL_ID,
                    "model_revision": MODEL_REVISION,
                    "n_docs": n,
                    "dim": dim,
                    "prefix_mode": prefix_mode,
                    "next_index": j,
                    "elapsed_sec": round(time.perf_counter() - t0, 1),
                },
                f,
            )
        elapsed = time.perf_counter() - t0
        done = j - start
        rate = done / max(elapsed, 1e-6)
        remain = (n - j) / max(rate, 1e-6)
        print(
            "corpus embed %s/%s  rate=%.2f docs/s  eta=%.0fs" % (j, n, rate, remain),
            flush=True,
        )
        i = j
    mm.flush()
    arr = l2_normalize(np.array(mm, dtype=np.float32, copy=True))
    del mm
    np.save(out_npy, arr)
    try:
        os.remove(mem_path)
    except OSError:
        pass
    return arr


def load_or_build_doc_matrix(
    model,
    texts: list[str],
    encoder_info: dict,
    out_npy: str,
    progress_json: str,
    corpus_sha: str,
    meta_json: str,
) -> np.ndarray:
    if os.path.isfile(out_npy) and os.path.isfile(meta_json):
        with open(meta_json, encoding="utf-8") as f:
            meta = json.load(f)
        ok = (
            meta.get("model_id") == MODEL_ID
            and meta.get("model_revision") == MODEL_REVISION
            and meta.get("corpus_sha256") == corpus_sha
            and meta.get("n_docs") == len(texts)
            and meta.get("complete") is True
            and meta.get("prefix_mode") == encoder_info.get("prefix_mode")
        )
        if ok:
            arr = np.load(out_npy, mmap_mode="r")
            if arr.shape == (len(texts), EMBED_DIM):
                print("dense document matrix cache hit", flush=True)
                return np.asarray(arr, dtype=np.float32)
            print("cache shape mismatch; rebuilding", flush=True)
    print("embedding %s documents..." % len(texts), flush=True)
    t0 = time.perf_counter()
    arr = embed_corpus(model, texts, encoder_info, out_npy, progress_json)
    elapsed = time.perf_counter() - t0
    meta = {
        "complete": True,
        "model_id": MODEL_ID,
        "model_revision": MODEL_REVISION,
        "corpus_sha256": corpus_sha,
        "n_docs": len(texts),
        "dim": EMBED_DIM,
        "prefix_mode": encoder_info.get("prefix_mode"),
        "normalize": True,
        "embed_seconds": round(elapsed, 2),
    }
    with open(meta_json, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    return arr


def gold_rank_and_score(scores: np.ndarray, gold_id: int) -> tuple[int, float]:
    """1-indexed rank with deterministic ties (higher score, then smaller id)."""
    g = int(gold_id)
    if g < 0 or g >= scores.shape[0]:
        raise SystemExit("BLOCKED — gold doc id out of corpus: %s" % gold_id)
    gs = float(scores[g])
    strictly_better = int(np.sum(scores > gs))
    tie_earlier = int(np.sum((scores == gs) & (np.arange(scores.shape[0]) < g)))
    rank = 1 + strictly_better + tie_earlier
    return rank, gs


def topk_ids(scores: np.ndarray, k: int = TOP_K) -> list[tuple[int, float]]:
    n = int(scores.shape[0])
    k = min(int(k), n)
    part = np.argpartition(-scores, kth=k - 1)[:k]
    ordered = sorted((int(i) for i in part), key=lambda i: (-float(scores[i]), i))
    return [(i, float(scores[i])) for i in ordered]


def search_query_vec(doc_matrix: np.ndarray, qvec: np.ndarray, gold_id: int, k: int = TOP_K) -> dict:
    scores = doc_matrix @ qvec.astype(np.float32)
    rank, gold_sim = gold_rank_and_score(scores, gold_id)
    top = topk_ids(scores, k)
    return {
        "gold_rank": rank,
        "gold_similarity": gold_sim,
        "rank1_doc_id": top[0][0],
        "rank1_similarity": top[0][1],
        "topk": top,
    }
