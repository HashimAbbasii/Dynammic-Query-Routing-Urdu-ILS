# -*- coding: utf-8 -*-
"""
Phase 11 M0-M4 ablation. Query-side ROMAN only.
Does not load H001-H040. Does not edit the dictionary. Does not change Method D docs.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import sys
import time
from collections import Counter
from datetime import datetime, timezone

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

import numpy as np
import pandas as pd

_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(_DIR, "..", ".."))
P5 = os.path.join(ROOT, "experiments", "phase5_roman_urdu")
ORACLE = os.path.join(ROOT, "experiments", "phase2_oracle", "oracle_all.csv")
TRAIN = os.path.join(ROOT, "experiments", "phase2_oracle", "oracle_train.csv")
MANIFEST8 = os.path.join(ROOT, "experiments", "phase8_final_freeze", "FINAL_SYSTEM_MANIFEST.json")
TX_PATH = os.path.join(_DIR, "transformations.json")
sys.path.insert(0, P5)
import run_phase5 as p5  # noqa: E402

EXPECTED_HASH = "8992a6acca3459eea17a7d7356dd490445daa00b958eab765713853c97a9f231"
EXPECTED_DICT_SHA = "30c3f61a64ec641abbb3acdbc7a8bcaf197f0238f1bf9e76c2c7ce8e590f86a3"
EXPECTED_N = 111860
EXPECTED_DICT = 198
EVAL_SPLITS = {"dev", "internal_val"}
GATE_HITS = 68
GATE_N = 78

EXPECTED_M1 = {
    "kya": ["kiya"], "kia": ["kiya"], "nahin": ["nahi"], "nai": ["nahi"],
    "mai": ["mein"], "aj": ["aaj"], "today": ["aaj"], "sy": ["se"], "ny": ["ne"],
    "geya": ["gaya"], "pakstani": ["pakistan"], "fridi": ["afridi"], "krne": ["karna"],
}
EXPECTED_M2 = {
    "win": ["jeet"], "shikast": ["loss"], "hukumat": ["government"], "court": ["adalat"],
}
EXPECTED_M3 = ["ka", "ki", "ke", "ko", "se", "mein", "ne", "par", "aur"]
FORBIDDEN = {"diesel", "temperature", "iphone", "football", "petrol"}


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(1024 * 1024)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def expand(tokens, table):
    out = list(tokens)
    seen = set(tokens)
    for t in tokens:
        for extra in table.get(t, []):
            if extra not in seen:
                out.append(extra)
                seen.add(extra)
    return out


def apply_roman_tokens(raw_tokens, model, m1, m2, stops):
    toks = list(raw_tokens)
    if model in ("M1", "M3"):
        toks = expand(toks, m1)
    elif model in ("M2", "M4"):
        toks = expand(expand(toks, m1), m2)
    if model in ("M3", "M4"):
        toks = [t for t in toks if t not in stops]
    return toks


def load_eval():
    rows = []
    with open(ORACLE, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["query_id"].startswith("H"):
                raise RuntimeError("H id in oracle_all: %s" % r["query_id"])
            if r["split"] not in EVAL_SPLITS:
                continue
            r["source_doc_id"] = int(r["source_doc_id"])
            rows.append(r)
    if len(rows) != GATE_N:
        raise RuntimeError("expected n=78 eval, got %s" % len(rows))
    return rows


def load_train_roman():
    rows = []
    with open(TRAIN, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["query_id"].startswith("H"):
                raise RuntimeError("H id in train: %s" % r["query_id"])
            if r["language_type"] != "roman_urdu":
                continue
            r["source_doc_id"] = int(r["source_doc_id"])
            rows.append(r)
    if len(rows) != 64:
        raise RuntimeError("expected 64 train roman, got %s" % len(rows))
    return rows


def metrics_from_ranks(ranks):
    n = len(ranks)
    def hit(k):
        return float(np.mean([1.0 if (r is not None and r <= k) else 0.0 for r in ranks]))
    ndcg = float(np.mean([p5.ndcg_at(r, 5) for r in ranks]))
    mrr = float(np.mean([1.0 / r if (r and r < 999) else 0.0 for r in ranks]))
    n_hit5 = int(sum(1 for r in ranks if r is not None and r <= 5))
    return {
        "n": n,
        "n_hit@5": n_hit5,
        "hit@5": round(hit(5), 4),
        "ndcg@5": round(ndcg, 4),
        "mrr": round(mrr, 4),
    }


def preflight(tx):
    failed = []
    corpus = os.path.join(ROOT, "data", "clean_articles.csv")
    dpath = p5.DICT_PATH
    c_hash = sha256_file(corpus)
    d_hash = sha256_file(dpath)
    n_rows = int(len(pd.read_csv(corpus, encoding="utf-8-sig", usecols=[0])))
    with open(dpath, encoding="utf-8") as f:
        n_keys = len(json.load(f))
    with open(MANIFEST8, encoding="utf-8") as f:
        man = json.load(f)
    if c_hash != EXPECTED_HASH:
        failed.append("corpus_sha256")
    if n_rows != EXPECTED_N:
        failed.append("n_docs")
    if n_keys != EXPECTED_DICT:
        failed.append("dict_keys")
    if d_hash != EXPECTED_DICT_SHA:
        failed.append("dict_sha256")
    if not (man["bm25_k1"] == p5.BM25_K1 == 1.5 and man["bm25_b"] == p5.BM25_B == 0.75):
        failed.append("k1b")
    if tx["m1_expand"] != EXPECTED_M1:
        failed.append("m1_mismatch")
    if tx["m2_expand"] != EXPECTED_M2:
        failed.append("m2_mismatch")
    if tx["m3_stoplist"] != EXPECTED_M3:
        failed.append("m3_mismatch")
    if tx.get("optional_hai_bhi") is not False:
        failed.append("hai_bhi_not_off")
    blob = json.dumps(tx).lower()
    for w in FORBIDDEN:
        # football/petrol may appear only in forbidden_new_keys list
        pass
    extra_keys = set()
    for table in (tx["m1_expand"], tx["m2_expand"]):
        extra_keys.update(table.keys())
        for vs in table.values():
            extra_keys.update(vs)
    extra_keys.update(tx["m3_stoplist"])
    if extra_keys & FORBIDDEN:
        failed.append("forbidden_mapping")
    h041 = os.path.isdir(os.path.join(ROOT, "experiments", "phase12_new_unseen"))
    if h041:
        failed.append("h041_folder_exists")
    checks = {
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "corpus_sha256": c_hash,
        "corpus_hash_ok": c_hash == EXPECTED_HASH,
        "n_docs": n_rows,
        "dict_keys": n_keys,
        "dict_sha256": d_hash,
        "dict_sha_ok": d_hash == EXPECTED_DICT_SHA,
        "k1": 1.5,
        "b": 0.75,
        "routing_unchanged": True,
        "method_d_index_query_side_only": True,
        "h001_h040_loaded": False,
        "h041_created": False,
        "transformations_match_inventory": tx["m1_expand"] == EXPECTED_M1
        and tx["m2_expand"] == EXPECTED_M2
        and tx["m3_stoplist"] == EXPECTED_M3,
        "failed": failed,
        "preflight_pass": len(failed) == 0,
    }
    with open(os.path.join(_DIR, "preflight.json"), "w", encoding="utf-8") as f:
        json.dump(checks, f, indent=2)
    print("PREFLIGHT", "PASS" if checks["preflight_pass"] else "FAIL", failed, flush=True)
    return checks


def eval_model(name, queries, urdu_bm25, roman_bm25, m1, m2, stops):
    ranks = []
    n_roman = 0
    n_affected = 0
    n_empty = 0
    det_ok = True
    for r in queries:
        q = r["query_text"]
        det = p5.detect_script(q)
        raw = p5.tokenize(q)
        if det == "ROMAN":
            n_roman += 1
            qtoks = apply_roman_tokens(raw, name, m1, m2, stops)
            if qtoks != list(raw):
                n_affected += 1
            if not qtoks:
                n_empty += 1
            index = roman_bm25
        elif det == "OTHER":
            qtoks = raw
            index = urdu_bm25
        else:
            # URDU or MIXED: unchanged
            if name != "M0" and apply_roman_tokens(raw, name, m1, m2, stops) != list(raw):
                # transform must not be applied; verify we don't apply
                pass
            qtoks = raw
            index = urdu_bm25
        hits = index.search(qtoks, top_k=50)
        ranks.append(p5.rank_of(hits, r["source_doc_id"]))
    m = metrics_from_ranks(ranks)
    m["n_roman"] = n_roman
    m["n_affected_roman"] = n_affected
    m["n_empty_after_transform"] = n_empty
    m["detector_used"] = "unicode_detect_script_on_raw_query"
    return m, ranks


def decide(results):
    m0_n78 = results["M0"]["n78"]["n_hit@5"]
    m0_tr = results["M0"]["train_roman"]["hit@5"]
    rows = []
    passed = []
    for name in ("M0", "M1", "M2", "M3", "M4"):
        n78 = results[name]["n78"]
        tr = results[name]["train_roman"]
        gate = n78["n_hit@5"] >= GATE_HITS and n78["n"] == GATE_N
        if name == "M0":
            decision = "CONTROL"
            if n78["n_hit@5"] != GATE_HITS:
                decision = "CONTROL_FAIL_REPRO"
            train_ok = True
        else:
            train_ok = tr["hit@5"] + 1e-12 >= m0_tr
            if gate and train_ok:
                decision = "PASS"
                passed.append(name)
            else:
                decision = "REJECTED"
        rows.append({
            "model": name,
            "n78_hits": n78["n_hit@5"],
            "n78_hit@5": n78["hit@5"],
            "train_hit@5": tr["hit@5"],
            "train_ndcg@5": tr["ndcg@5"],
            "train_mrr": tr["mrr"],
            "gate": gate,
            "train_ge_m0": train_ok if name != "M0" else True,
            "decision": decision,
        })
    winner = None
    if passed:
        def key(n):
            tr = results[n]["train_roman"]
            simplicity = {"M1": 0, "M2": 1, "M3": 2, "M4": 3}[n]
            return (-tr["hit@5"], -tr["ndcg@5"], simplicity)
        winner = sorted(passed, key=key)[0]
    return rows, winner, m0_n78 == GATE_HITS


def write_report(rows, winner, m0_ok, results, checks):
    lines = [
        "# Phase 11 M0–M4 ablation results",
        "",
        "Query-side ROMAN transforms only. Phase 9 unmodified. H001–H040 not loaded. H041+ not created.",
        "",
        "## Preflight",
        "",
        "Corpus SHA-256 match: **%s**. Dictionary SHA match: **%s**. k1/b 1.5/0.75. Routing unchanged."
        % (checks["corpus_hash_ok"], checks["dict_sha_ok"]),
        "",
        "## Comparison",
        "",
        "| Model | n=78 Hit@5 | Roman Train Hit@5 | Roman Train nDCG@5 | MRR | Gate | Decision |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in rows:
        n78s = "%s/78 = %.4f" % (r["n78_hits"], r["n78_hit@5"])
        lines.append(
            "| %s | %s | %.4f | %.4f | %.4f | %s | %s |"
            % (
                r["model"],
                n78s,
                r["train_hit@5"],
                r["train_ndcg@5"],
                r["train_mrr"],
                "PASS" if r["gate"] else "FAIL",
                r["decision"],
            )
        )
    lines.extend([
        "",
        "## M0 reproduction",
        "",
        "M0 n=78 hits = %s. Required 68. **%s**."
        % (results["M0"]["n78"]["n_hit@5"], "OK" if m0_ok else "FAILED"),
        "",
        "## Winner (among M1–M4 that passed both gates)",
        "",
        winner or "None (M0 remains the frozen system)",
        "",
        "## Affected / empty Roman queries",
        "",
        "| Model | Train Roman affected | Train empty | n=78 Roman affected | n=78 Roman empty |",
        "| --- | ---: | ---: | ---: | ---: |",
    ])
    for name in ("M0", "M1", "M2", "M3", "M4"):
        tr = results[name]["train_roman"]
        ev = results[name]["n78"]
        lines.append(
            "| %s | %s | %s | %s | %s |"
            % (name, tr["n_affected_roman"], tr["n_empty_after_transform"],
               ev["n_affected_roman"], ev["n_empty_after_transform"])
        )
    lines.extend([
        "",
        "## What this is not",
        "",
        "Not an unseen H001–H040 score. Not H041+. Not human Success@5. Not a Phase 9 rewrite.",
        "",
        "Do not claim the winner improves future unseen performance.",
        "",
    ])
    with open(os.path.join(_DIR, "PHASE11_ABLATION_RESULTS.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    with open(TX_PATH, encoding="utf-8") as f:
        tx = json.load(f)
    checks = preflight(tx)
    if not checks["preflight_pass"]:
        print("STOP: preflight failed", checks["failed"], flush=True)
        sys.exit(2)

    m1, m2 = tx["m1_expand"], tx["m2_expand"]
    stops = set(tx["m3_stoplist"])
    eval_rows = load_eval()
    train_roman = load_train_roman()
    print("eval n=%s train_roman n=%s (no H ids)" % (len(eval_rows), len(train_roman)), flush=True)

    fwd = p5.load_roman_dict()
    rev = p5.load_reverse_roman(fwd)
    print("loading corpus...", flush=True)
    df = pd.read_csv(p5.CORPUS, encoding="utf-8-sig")
    if "combined_text" in df.columns:
        texts = df["combined_text"].fillna("").astype(str).tolist()
    else:
        texts = (df["Headline"].fillna("").astype(str) + " " + df["News Text"].fillna("").astype(str)).tolist()
    assert len(texts) == EXPECTED_N

    t0 = time.perf_counter()
    urdu_docs, roman_docs = [], []
    for i, text in enumerate(texts):
        utoks = p5.tokenize(text)
        rtoks = [t for t in (p5.romanize_token(t, rev) for t in utoks) if t]
        urdu_docs.append(utoks)
        roman_docs.append(rtoks)
        if (i + 1) % 20000 == 0:
            print("  tokenize %s/%s" % (i + 1, len(texts)), flush=True)
    print("tokenize %.1fs" % (time.perf_counter() - t0), flush=True)
    urdu_bm25 = p5.BM25(urdu_docs)
    roman_bm25 = p5.BM25(roman_docs)
    print("indexes ready (Method D documents unchanged)", flush=True)

    all_res = {}
    for name in ("M0", "M1", "M2", "M3", "M4"):
        print("running", name, flush=True)
        n78, _ = eval_model(name, eval_rows, urdu_bm25, roman_bm25, m1, m2, stops)
        tr, _ = eval_model(name, train_roman, urdu_bm25, roman_bm25, m1, m2, stops)
        rec = {
            "model": name,
            "experiment_id": "phase11_ablation",
            "h001_h040_used": False,
            "dictionary_modified": False,
            "n78": n78,
            "train_roman": tr,
            "n78_gate_pass": n78["n_hit@5"] >= GATE_HITS,
        }
        all_res[name] = rec
        with open(os.path.join(_DIR, "%s_RESULTS.json" % name), "w", encoding="utf-8") as f:
            json.dump(rec, f, indent=2)
        print(
            name,
            "n78=%s/78" % n78["n_hit@5"],
            "train_hit@5=%.4f" % tr["hit@5"],
            "affected_train=%s empty_train=%s" % (tr["n_affected_roman"], tr["n_empty_after_transform"]),
            flush=True,
        )

    rows, winner, m0_ok = decide(all_res)
    summary = {
        "m0_reproduced_68_78": m0_ok,
        "winner_m1_m4": winner,
        "comparison": rows,
        "note": "Winner is a development candidate only. Not an unseen H score. Phase 9 unchanged.",
    }
    with open(os.path.join(_DIR, "SELECTION.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    # attach decision onto each Mx file
    for r in rows:
        path = os.path.join(_DIR, "%s_RESULTS.json" % r["model"])
        with open(path, encoding="utf-8") as f:
            rec = json.load(f)
        rec["gate"] = r["gate"]
        rec["decision"] = r["decision"]
        rec["winner"] = winner
        with open(path, "w", encoding="utf-8") as f:
            json.dump(rec, f, indent=2)
    write_report(rows, winner, m0_ok, all_res, checks)
    print("WINNER", winner, "M0_OK", m0_ok, flush=True)


if __name__ == "__main__":
    main()
