# -*- coding: utf-8 -*-
"""Machine-checkable isolation of H001–H040 and other blocked eval/train text."""
from __future__ import annotations

import ast
import csv
import json
import os
import sys

_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(_DIR, "..", ".."))
sys.path.insert(0, _DIR)
sys.path.insert(0, os.path.join(ROOT, "validate", "dual_index_routing", "labels"))

from heldout_traps import HELDOUT_TRAPS  # noqa: E402
from textnorm import jaccard, normalize_query  # noqa: E402

FROZEN_TEST_IDS = tuple(f"H{i:03d}" for i in range(1, 41))
NEAR_DUP_JACCARD = 0.75


def frozen_rows():
    out = []
    for row in HELDOUT_TRAPS:
        qid, trap_type, script, category, query, gold = row
        out.append(
            {
                "query_id": qid,
                "query": query,
                "norm": normalize_query(query),
                "trap_type": trap_type,
                "script": script,
                "gold": gold,
            }
        )
    ids = [r["query_id"] for r in out]
    if ids != list(FROZEN_TEST_IDS):
        raise RuntimeError(f"Frozen ID list mismatch: {ids[:5]}...")
    return out


def _load_pairs_from_py(path, varname="training_queries"):
    if not os.path.isfile(path):
        return []
    with open(path, encoding="utf-8") as f:
        content = f.read()
    start = content.find(f"{varname} = [")
    if start < 0:
        return []
    blob = content[start + len(f"{varname} = ") :]
    data = ast.literal_eval(blob)
    texts = []
    for item in data:
        if isinstance(item, (list, tuple)):
            texts.append(str(item[0]))
        elif isinstance(item, dict):
            texts.append(str(item.get("query") or item.get("query_text") or ""))
        else:
            texts.append(str(item))
    return [t for t in texts if t.strip()]


def extra_blocked_texts():
    """Other project queries we must not clone. Not the frozen test, but overlap is still contamination."""
    texts = []
    trap_csv = os.path.join(ROOT, "validate", "dual_index_routing", "labels", "trap_label_sheet.csv")
    if os.path.isfile(trap_csv):
        with open(trap_csv, encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                texts.append(r.get("query") or "")
    p3 = os.path.join(ROOT, "validate", "phase3", "phase3_evaluation_set.csv")
    if os.path.isfile(p3):
        with open(p3, encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                texts.append(r.get("query") or "")
    p25 = os.path.join(ROOT, "validate", "phase2_5", "pilot_queries.json")
    if os.path.isfile(p25):
        obj = json.loads(open(p25, encoding="utf-8").read())
        for q in obj.get("queries") or []:
            texts.append(q.get("query") or "")
    texts.extend(_load_pairs_from_py(os.path.join(ROOT, "data", "training_queries_real.py")))
    return [t for t in texts if str(t).strip()]


def blocked_norm_set():
    s = {r["norm"] for r in frozen_rows()}
    s |= {normalize_query(t) for t in extra_blocked_texts()}
    s.discard("")
    return s


def collision_report(query_id: str, query_text: str, blocked_norms: set[str], frozen: list[dict]):
    """Return None if clean; else a dict describing the leak."""
    n = normalize_query(query_text)
    if not n:
        return {"query_id": query_id, "reason": "empty"}
    if n in blocked_norms:
        return {"query_id": query_id, "reason": "exact_or_normalized_match", "norm": n}
    for fr in frozen:
        jac = jaccard(query_text, fr["query"])
        if jac >= NEAR_DUP_JACCARD:
            return {
                "query_id": query_id,
                "reason": "near_duplicate_frozen_test",
                "frozen_id": fr["query_id"],
                "jaccard": round(jac, 4),
            }
    return None


def assert_pool_isolated(rows: list[dict]) -> dict:
    frozen = frozen_rows()
    blocked = blocked_norm_set()
    pool_ids = {r["query_id"] for r in rows}
    leaks = []
    if pool_ids & set(FROZEN_TEST_IDS):
        leaks.append({"reason": "frozen_id_in_pool", "ids": sorted(pool_ids & set(FROZEN_TEST_IDS))})
    seen_norm = {}
    for r in rows:
        hit = collision_report(r["query_id"], r["query_text"], blocked, frozen)
        if hit:
            leaks.append(hit)
        n = normalize_query(r["query_text"])
        if n in seen_norm:
            leaks.append(
                {
                    "reason": "duplicate_within_pool",
                    "query_id": r["query_id"],
                    "other_id": seen_norm[n],
                }
            )
        else:
            seen_norm[n] = r["query_id"]
    if leaks:
        raise AssertionError(f"LEAKAGE: {len(leaks)} problem(s). First: {leaks[0]}")
    return {
        "ok": True,
        "n_pool": len(rows),
        "frozen_test_ids": list(FROZEN_TEST_IDS),
        "n_blocked_norms": len(blocked),
        "near_dup_jaccard_threshold": NEAR_DUP_JACCARD,
    }
