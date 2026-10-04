# -*- coding: utf-8 -*-
"""Phase 15 step 1 — Colab T4 pilot for one dense encoder.

Run this on a CUDA GPU (Colab T4). It refuses to download weights or embed
when CUDA is absent. It encodes 500 corpus documents only. It does not open
TEST, does not read queries, and does not compute Hit@k or any other score.

Colab setup (do not pip-install torch; the Colab CUDA wheel is already there):

    pip install "sentence-transformers>=5.1.2" "transformers>=4.57.3" huggingface_hub pandas numpy
    python step1_pilot_colab.py --corpus /content/clean_articles.csv --out-dir /content/phase15_granite_step1

Put the corpus and the JSON output on Colab local disk. Do not write them
under OneDrive or inside this git repo. A later full-corpus matrix is large
enough for sync locking to corrupt it.

The Hugging Face id pinned here is ibm-granite/granite-embedding-311m-multilingual-r2
at revision 44399559930365213510b1ee2eb15ded83374f0e. The task string
ibm-granite/granite-embedding-multilingual-r2 returned HTTP 401 and has no
public card. See STEP1_LOCAL_REPORT.md.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import sys
import time

os.environ.setdefault("MKL_THREADING_LAYER", "SEQUENTIAL")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

# Task string that did not resolve to a public model card (HTTP 401).
TASK_MODEL_ID = "ibm-granite/granite-embedding-multilingual-r2"
# Public 311M card retrieved 2026-10-04. Not a second model.
MODEL_ID = "ibm-granite/granite-embedding-311m-multilingual-r2"
MODEL_REVISION = "44399559930365213510b1ee2eb15ded83374f0e"

EXPECTED_CORPUS_SHA = "8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231"
EXPECTED_N_DOCS = 111860
EXPECTED_DIM = 768
# sentence_bert_config.json max_seq_length and config.json max_position_embeddings.
# One candidate. Not swept.
CANDIDATE_MAX_LENGTH = 32768
# One pilot batch so the encode can be timed. Not selected by a retrieval score.
CANDIDATE_BATCH_SIZE = 8
SAMPLE_N = 500
SAMPLE_SEED = 15

IGNORE_WEIGHT_EXTRAS = [
    "onnx/*",
    "openvino/*",
    "openvino_model.bin",
    "openvino_model.xml",
    "*.onnx",
]


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            block = f.read(8 * 1024 * 1024)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def refuse_test_path(path: str) -> None:
    norm = os.path.abspath(path).replace("\\", "/").lower()
    if "/benchmark/test" in norm or norm.endswith("/benchmark/test"):
        raise SystemExit("BLOCKED - TEST path is forbidden: %s" % path)


def inside_ultra_repo(path: str) -> bool:
    cur = os.path.abspath(path)
    while True:
        if os.path.isdir(os.path.join(cur, ".git")) and os.path.isdir(
            os.path.join(cur, "experiments", "ultra_v2")
        ):
            return True
        parent = os.path.dirname(cur)
        if parent == cur:
            return False
        cur = parent


def assert_safe_output_dir(path: str) -> None:
    ap = os.path.abspath(path)
    norm = ap.replace("\\", "/").lower()
    if "onedrive" in norm:
        raise SystemExit(
            "BLOCKED - output dir is under OneDrive (%s). "
            "Write on Colab local disk or a folder excluded from sync." % ap
        )
    if inside_ultra_repo(ap):
        raise SystemExit(
            "BLOCKED - output dir is inside the ULTRA git repo (%s). "
            "Pilot output stays outside the repo." % ap
        )


def load_corpus_texts(corpus_path: str) -> tuple[list[str], str]:
    """Same text rule as phase3_dense/dense_retrieval.py load_corpus_texts.

    The frozen file has combined_text. The Headline fallback is only here so
    a missing column stops nothing silently relative to Phase 3.
    """
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
    return texts, source_col


def length_report(lengths) -> dict:
    import numpy as np

    arr = np.asarray(lengths)
    return {
        "n": int(arr.size),
        "p50": float(np.percentile(arr, 50)),
        "p90": float(np.percentile(arr, 90)),
        "p99": float(np.percentile(arr, 99)),
        "max": int(arr.max()) if arr.size else None,
        "min": int(arr.min()) if arr.size else None,
        "gt_512": int((arr > 512).sum()),
        "gt_1024": int((arr > 1024).sum()),
        "gt_2048": int((arr > 2048).sum()),
        "gt_candidate_max_length": int((arr > CANDIDATE_MAX_LENGTH).sum()),
        "percentile_definition": "numpy.percentile default (linear)",
        "add_special_tokens": True,
        "truncation": False,
    }


def token_length_census(tokenizer, texts: list[str], batch_size: int = 32):
    import numpy as np

    old_max = tokenizer.model_max_length
    # Census must not truncate. The model ceiling is restored before encode.
    tokenizer.model_max_length = 10**9
    lengths = np.empty(len(texts), dtype=np.int32)
    batch_failures = 0
    n = len(texts)
    t0 = time.perf_counter()
    for start in range(0, n, batch_size):
        batch = texts[start : start + batch_size]
        try:
            enc = tokenizer(
                batch,
                add_special_tokens=True,
                truncation=False,
                padding=False,
                return_attention_mask=False,
            )
            for j, row in enumerate(enc["input_ids"]):
                lengths[start + j] = len(row)
        except Exception as exc:
            batch_failures += 1
            print(
                "token census batch failed at %s (%s); retrying one by one" % (start, type(exc).__name__),
                flush=True,
            )
            for j, text in enumerate(batch):
                one = tokenizer(
                    text,
                    add_special_tokens=True,
                    truncation=False,
                    padding=False,
                    return_attention_mask=False,
                )
                lengths[start + j] = len(one["input_ids"])
        if start % 10240 == 0:
            print("token census %s/%s" % (start, n), flush=True)
    tokenizer.model_max_length = old_max
    elapsed = time.perf_counter() - t0
    return lengths, elapsed, batch_failures


def require_cuda():
    import torch

    if not torch.cuda.is_available():
        raise SystemExit(
            "BLOCKED - CUDA is not available. This pilot does not download weights "
            "and does not embed on CPU."
        )
    return torch


def assert_checkpoint_contract(local_dir: str) -> dict:
    with open(os.path.join(local_dir, "config.json"), encoding="utf-8") as f:
        cfg = json.load(f)
    with open(os.path.join(local_dir, "sentence_bert_config.json"), encoding="utf-8") as f:
        sbert = json.load(f)
    with open(os.path.join(local_dir, "config_sentence_transformers.json"), encoding="utf-8") as f:
        st_cfg = json.load(f)
    with open(os.path.join(local_dir, "1_Pooling", "config.json"), encoding="utf-8") as f:
        pool = json.load(f)
    with open(os.path.join(local_dir, "modules.json"), encoding="utf-8") as f:
        modules = json.load(f)

    if int(cfg["hidden_size"]) != EXPECTED_DIM:
        raise SystemExit("BLOCKED - hidden_size %s != %s" % (cfg["hidden_size"], EXPECTED_DIM))
    if int(cfg["max_position_embeddings"]) != CANDIDATE_MAX_LENGTH:
        raise SystemExit(
            "BLOCKED - max_position_embeddings %s != documented %s"
            % (cfg["max_position_embeddings"], CANDIDATE_MAX_LENGTH)
        )
    if int(sbert["max_seq_length"]) != CANDIDATE_MAX_LENGTH:
        raise SystemExit(
            "BLOCKED - sentence_bert max_seq_length %s != %s"
            % (sbert["max_seq_length"], CANDIDATE_MAX_LENGTH)
        )
    prompts = st_cfg.get("prompts") or {}
    if prompts.get("query") != "" or prompts.get("document") != "":
        raise SystemExit(
            "BLOCKED - checkpoint prompts are not the empty strings recorded at step 1: %s" % prompts
        )
    if pool.get("pooling_mode_cls_token") is not True or pool.get("pooling_mode_mean_tokens") is not False:
        raise SystemExit("BLOCKED - pooling config is not CLS-only: %s" % pool)
    module_types = [m.get("type", "") for m in modules]
    if "sentence_transformers.models.Normalize" not in module_types:
        raise SystemExit("BLOCKED - Normalize module missing from modules.json")
    return {
        "config_dtype": cfg.get("dtype"),
        "hidden_size": cfg.get("hidden_size"),
        "max_position_embeddings": cfg.get("max_position_embeddings"),
        "classifier_pooling": cfg.get("classifier_pooling"),
        "prompts": prompts,
        "default_prompt_name": st_cfg.get("default_prompt_name"),
        "similarity_fn_name": st_cfg.get("similarity_fn_name"),
        "pooling_mode_cls_token": pool.get("pooling_mode_cls_token"),
        "include_prompt": pool.get("include_prompt"),
        "module_types": module_types,
    }


def load_model_fp16(local_dir: str, torch):
    from sentence_transformers import SentenceTransformer

    errors = []
    model = None
    dtype_key = None
    for key in ("dtype", "torch_dtype"):
        try:
            model = SentenceTransformer(
                local_dir,
                device="cuda",
                model_kwargs={key: torch.float16},
            )
            dtype_key = key
            break
        except TypeError as exc:
            errors.append("%s: %s" % (key, exc))
            model = None
    if model is None:
        raise SystemExit("BLOCKED - fp16 load failed: %s" % " | ".join(errors))

    param_dtypes = sorted({str(p.dtype) for p in model.parameters()})
    cast = "from_pretrained(%s=float16)" % dtype_key
    if not any(d == "torch.float16" for d in param_dtypes):
        model = model.to(torch.float16)
        cast = cast + " then model.to(float16)"
        param_dtypes = sorted({str(p.dtype) for p in model.parameters()})
    if not any(d == "torch.float16" for d in param_dtypes):
        raise SystemExit("BLOCKED - parameters are not fp16 after cast: %s" % param_dtypes)
    device_types = {p.device.type for p in model.parameters()}
    if device_types != {"cuda"}:
        raise SystemExit("BLOCKED - parameters are not all on cuda: %s" % sorted(device_types))
    prompts = getattr(model, "prompts", {}) or {}
    if prompts.get("query", "") not in ("", None) or prompts.get("document", "") not in ("", None):
        raise SystemExit("BLOCKED - loaded model prompts are not empty: %s" % prompts)
    max_before = int(model.max_seq_length)
    if max_before != CANDIDATE_MAX_LENGTH:
        model.max_seq_length = CANDIDATE_MAX_LENGTH
    return model, {
        "cast": cast,
        "parameter_dtypes": param_dtypes,
        "prompts": prompts,
        "max_seq_length_before_set": max_before,
        "max_seq_length": int(model.max_seq_length),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Phase 15 step 1 Colab pilot (docs only, no scores).")
    parser.add_argument("--corpus", required=True, help="Path to the frozen clean_articles.csv copy.")
    parser.add_argument(
        "--out-dir",
        required=True,
        help="Directory for the JSON summary. Must not be OneDrive or the git repo.",
    )
    args = parser.parse_args()

    refuse_test_path(args.corpus)
    refuse_test_path(args.out_dir)
    assert_safe_output_dir(args.out_dir)

    corpus_sha = sha256_file(args.corpus)
    if corpus_sha != EXPECTED_CORPUS_SHA:
        raise SystemExit(
            "BLOCKED - corpus SHA-256 mismatch.\nexpected %s\ngot      %s"
            % (EXPECTED_CORPUS_SHA, corpus_sha)
        )

    # Stop before parsing the CSV or contacting Hugging Face when this is the CPU box.
    torch = require_cuda()

    texts, source_col = load_corpus_texts(args.corpus)
    if len(texts) != EXPECTED_N_DOCS:
        raise SystemExit("BLOCKED - corpus size %s != %s" % (len(texts), EXPECTED_N_DOCS))
    n_empty = sum(1 for t in texts if not str(t).strip())

    from huggingface_hub import snapshot_download

    print("downloading pinned Granite snapshot (no onnx/openvino)", flush=True)
    local_dir = snapshot_download(
        repo_id=MODEL_ID,
        revision=MODEL_REVISION,
        ignore_patterns=IGNORE_WEIGHT_EXTRAS,
    )
    contract = assert_checkpoint_contract(local_dir)

    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(local_dir, use_fast=True)
    print("token census: full corpus, truncation off", flush=True)
    full_lengths, census_seconds, census_batch_failures = token_length_census(tokenizer, texts)

    random.seed(SAMPLE_SEED)
    sample_index = random.sample(range(len(texts)), SAMPLE_N)
    sample_texts = [texts[i] for i in sample_index]
    sample_lengths = full_lengths[sample_index]

    print("loading model in fp16 on cuda", flush=True)
    model, load_info = load_model_fp16(local_dir, torch)

    torch.cuda.reset_peak_memory_stats()
    torch.cuda.synchronize()
    t0 = time.perf_counter()
    emb = model.encode(
        sample_texts,
        batch_size=CANDIDATE_BATCH_SIZE,
        convert_to_numpy=True,
        normalize_embeddings=False,
        show_progress_bar=True,
    )
    torch.cuda.synchronize()
    encode_seconds = time.perf_counter() - t0

    import numpy as np

    arr = np.asarray(emb)
    if arr.shape != (SAMPLE_N, EXPECTED_DIM):
        raise SystemExit("BLOCKED - embedding shape %s != (%s, %s)" % (arr.shape, SAMPLE_N, EXPECTED_DIM))
    norms = np.linalg.norm(arr.astype(np.float32), axis=1)
    hours = (encode_seconds / SAMPLE_N) * EXPECTED_N_DOCS / 3600.0

    summary = {
        "experiment": "phase15-step1-pilot",
        "test_accessed": False,
        "queries_encoded": 0,
        "scores_computed": False,
        "hit_at_k": None,
        "task_model_id_unresolved": TASK_MODEL_ID,
        "model_id": MODEL_ID,
        "model_revision": MODEL_REVISION,
        "corpus_sha256": corpus_sha,
        "n_docs": len(texts),
        "text_column": source_col,
        "n_empty": n_empty,
        "sample_seed": SAMPLE_SEED,
        "sample_n": SAMPLE_N,
        "sample_index": sample_index,
        "python": sys.version,
        "candidate_max_length": CANDIDATE_MAX_LENGTH,
        "candidate_max_length_source": "sentence_bert_config.json max_seq_length; config.json max_position_embeddings",
        "candidate_batch_size": CANDIDATE_BATCH_SIZE,
        "checkpoint_contract": contract,
        "load": load_info,
        "tokenizer_add_bos_token": bool(getattr(tokenizer, "add_bos_token", None)),
        "tokenizer_add_eos_token": bool(getattr(tokenizer, "add_eos_token", None)),
        "token_census_seconds": census_seconds,
        "token_census_batch_failures": census_batch_failures,
        "token_length_full_corpus": length_report(full_lengths),
        "token_length_sample_500": length_report(sample_lengths),
        "encode_seconds": encode_seconds,
        "docs_per_second": SAMPLE_N / encode_seconds if encode_seconds else None,
        "estimated_full_corpus_hours": hours,
        "estimate_assumption": (
            "linear in document count at this batch size and this max_length; "
            "excludes model load and the token census; dynamic padding, not padded to 32768"
        ),
        "embedding_shape": list(arr.shape),
        "embedding_dtype": str(arr.dtype),
        "nan_count": int(np.isnan(arr).sum()),
        "inf_count": int(np.isinf(arr).sum()),
        "l2_norm_min": float(norms.min()),
        "l2_norm_mean": float(norms.mean()),
        "l2_norm_max": float(norms.max()),
        "peak_vram_allocated_bytes": int(torch.cuda.max_memory_allocated()),
        "peak_vram_reserved_bytes": int(torch.cuda.max_memory_reserved()),
        "gpu_name": torch.cuda.get_device_name(0),
        "gpu_total_memory_bytes": int(torch.cuda.get_device_properties(0).total_memory),
        "script_sha256": sha256_file(os.path.abspath(__file__)),
        "embeddings_written": False,
    }

    os.makedirs(args.out_dir, exist_ok=True)
    out_path = os.path.join(args.out_dir, "step1_pilot_summary.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
        f.write("\n")

    print(json.dumps({k: summary[k] for k in (
        "corpus_sha256",
        "n_docs",
        "embedding_shape",
        "embedding_dtype",
        "nan_count",
        "inf_count",
        "encode_seconds",
        "estimated_full_corpus_hours",
        "peak_vram_allocated_bytes",
        "token_length_full_corpus",
        "token_length_sample_500",
    )}, indent=2))
    print("wrote %s" % out_path, flush=True)
    print("TEST not opened. No queries. No scores.", flush=True)


if __name__ == "__main__":
    main()
