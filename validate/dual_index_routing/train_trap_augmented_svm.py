# -*- coding: utf-8 -*-
"""
Retrain the deployed SVM on 409 V2 queries + 40 trap labels.

Does not use notebooks/15_gap_fill_retraining.ipynb (that notebook's
extract_features() is 9-wide and does not match the deployed 8-feature V2).

Writes:
  models/backup_v2_pre_trap_retrain_2026-08-22/   (V2 pickle copy)
  models/svm_classifier.pkl
  models/scaler.pkl
  models/training_info.json
  validate/dual_index_routing/trap_retrain_report.json

Does NOT overwrite frozen Phase 3B prediction CSVs.
"""
from __future__ import annotations

import csv
import json
import os
import shutil
import sys
from collections import Counter
from datetime import date

import numpy as np
from sklearn.metrics import accuracy_score
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(_DIR, "..", ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "validate", "phase3"))
sys.path.insert(0, _DIR)

from extractor_v3 import FEATURE_ORDER_V3, extract_features_v3  # noqa: E402
from phase3a_extractor import (  # noqa: E402
    CANONICAL_FEATURE_ORDER,
    extract_features_phase3a,
    load_roman_dict,
    load_training_queries,
)

BACKUP_DIR = os.path.join(REPO_ROOT, "models", "backup_v2_pre_trap_retrain_2026-08-22")
SVM_PATH = os.path.join(REPO_ROOT, "models", "svm_classifier.pkl")
SCALER_PATH = os.path.join(REPO_ROOT, "models", "scaler.pkl")
INFO_PATH = os.path.join(REPO_ROOT, "models", "training_info.json")
TRAP_CSV = os.path.join(_DIR, "labels", "trap_label_sheet.csv")
PHASE3_CSV = os.path.join(REPO_ROOT, "validate", "phase3", "phase3_evaluation_set.csv")
REPORT_PATH = os.path.join(_DIR, "trap_retrain_report.json")
RANDOM_STATE = 42
WORDCOUNT_LONG_MIN = 6


def _norm_label(x: str) -> str:
    return str(x).strip().lower()


def load_traps():
    with open(TRAP_CSV, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    out = []
    for r in rows:
        a = _norm_label(r["gold_label_A"])
        b = _norm_label(r["gold_label_B"])
        if a != b or a not in ("short", "long"):
            raise ValueError(f"{r['query_id']}: labels disagree or blank ({a!r} vs {b!r})")
        out.append(
            {
                "query_id": r["query_id"],
                "query": r["query"],
                "label": a,
                "trap_type": r["trap_type"],
                "word_count": int(r["word_count"]),
            }
        )
    return out


def load_phase3_primary():
    with open(PHASE3_CSV, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    out = []
    for r in rows:
        if r.get("set_type") != "primary":
            continue
        gold = _norm_label(r.get("gold_label") or "")
        if gold not in ("short", "long"):
            continue
        out.append({"query_id": r["query_id"], "query": r["query"], "label": gold})
    return out


def wordcount_label(query: str) -> str:
    return "long" if len(query.split()) >= WORDCOUNT_LONG_MIN else "short"


def backup_v2():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    for src in (SVM_PATH, SCALER_PATH, INFO_PATH):
        if not os.path.isfile(src):
            raise FileNotFoundError(src)
        shutil.copy2(src, os.path.join(BACKUP_DIR, os.path.basename(src)))


def build_xy(pairs, roman, kind: str):
    extract = extract_features_phase3a if kind == "v2_8" else extract_features_v3
    X = np.array([extract(q, roman) for q, _ in pairs], dtype=float)
    y = np.array([lab for _, lab in pairs])
    return X, y


def cv_scores(X, y, sample_weight=None):
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    scores = []
    for tr, te in skf.split(X, y):
        scaler = StandardScaler().fit(X[tr])
        m = SVC(kernel="rbf", C=1.0, gamma="scale", probability=True, random_state=RANDOM_STATE)
        w = None if sample_weight is None else sample_weight[tr]
        m.fit(scaler.transform(X[tr]), y[tr], sample_weight=w)
        scores.append(m.score(scaler.transform(X[te]), y[te]))
    return float(np.mean(scores)), float(np.std(scores))


def fit_final(X, y, sample_weight=None):
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)
    m = SVC(kernel="rbf", C=1.0, gamma="scale", probability=True, random_state=RANDOM_STATE)
    m.fit(Xs, y, sample_weight=sample_weight)
    return scaler, m


def predict_labels(scaler, model, X):
    return np.array([str(p).lower() for p in model.predict(scaler.transform(X))])


def acc(y_true, y_pred) -> float:
    return float(accuracy_score(y_true, y_pred))


def eval_slice(scaler, model, roman, kind, items, pred_key="query"):
    extract = extract_features_phase3a if kind == "v2_8" else extract_features_v3
    queries = [it[pred_key] for it in items]
    y = np.array([it["label"] for it in items])
    X = np.array([extract(q, roman) for q in queries], dtype=float)
    pred = predict_labels(scaler, model, X)
    wc = np.array([wordcount_label(q) for q in queries])
    return {
        "n": len(items),
        "svm_acc": acc(y, pred),
        "wordcount_acc": acc(y, wc),
        "n_svm_correct": int((y == pred).sum()),
        "n_wordcount_correct": int((y == wc).sum()),
    }


def main():
    backup_v2()
    roman = load_roman_dict()
    original = [(q, _norm_label(lab)) for q, lab in load_training_queries()]
    traps = load_traps()
    orig_set = {q for q, _ in original}
    traps_new = [t for t in traps if t["query"] not in orig_set]
    skipped = [t["query_id"] for t in traps if t["query"] in orig_set]

    train_pairs = original + [(t["query"], t["label"]) for t in traps_new]
    y_all = np.array([lab for _, lab in train_pairs])
    trap_weight_mask = np.array(
        [0.0] * len(original) + [1.0] * len(traps_new), dtype=float
    )

    p3 = load_phase3_primary()
    trap_q = {t["query"] for t in traps}
    p3_overlap = [r for r in p3 if r["query"] in trap_q]
    p3_held = [r for r in p3 if r["query"] not in trap_q]

    variants = [
        {"name": "v2_8", "kind": "v2_8", "trap_weight": 1.0},
        {"name": "v3_12", "kind": "v3_12", "trap_weight": 1.0},
        {"name": "v3_12_w4", "kind": "v3_12", "trap_weight": 4.0},
    ]

    results = []
    fitted = {}
    for v in variants:
        X, y = build_xy(train_pairs, roman, v["kind"])
        sw = np.where(trap_weight_mask > 0, v["trap_weight"], 1.0)
        cv_mean, cv_std = cv_scores(X, y, sample_weight=sw)
        scaler, model = fit_final(X, y, sample_weight=sw)
        trap_m = eval_slice(scaler, model, roman, v["kind"], traps)
        p3_m = eval_slice(scaler, model, roman, v["kind"], p3)
        held_m = eval_slice(scaler, model, roman, v["kind"], p3_held)
        orig_m = eval_slice(
            scaler,
            model,
            roman,
            v["kind"],
            [{"query": q, "label": lab} for q, lab in original],
        )
        beats_wc = trap_m["svm_acc"] > trap_m["wordcount_acc"] + 1e-9
        row = {
            "name": v["name"],
            "n_features": int(X.shape[1]),
            "trap_weight": v["trap_weight"],
            "cv_mean": cv_mean,
            "cv_std": cv_std,
            "train_acc": acc(y, predict_labels(scaler, model, X)),
            "original_409_acc": orig_m["svm_acc"],
            "traps": trap_m,
            "phase3b_primary": p3_m,
            "phase3b_nonoverlap": held_m,
            "beats_wordcount_on_traps": beats_wc,
        }
        results.append(row)
        fitted[v["name"]] = (scaler, model, v["kind"], X.shape[1])
        print(
            f"{v['name']:10} feat={X.shape[1]:2d} w={v['trap_weight']:.0f} "
            f"CV={cv_mean:.3f} traps={trap_m['svm_acc']:.3f} "
            f"(wc={trap_m['wordcount_acc']:.3f}) "
            f"P3B={p3_m['svm_acc']:.3f} held={held_m['svm_acc']:.3f} "
            f"409={orig_m['svm_acc']:.3f}"
        )

    # Prefer a model that beats the 6-word rule on the 40 traps, then
    # the non-overlapping Phase 3B slice, then trap accuracy.
    ranked = sorted(
        results,
        key=lambda r: (
            int(r["beats_wordcount_on_traps"]),
            r["phase3b_nonoverlap"]["svm_acc"],
            r["traps"]["svm_acc"],
            r["original_409_acc"],
        ),
        reverse=True,
    )
    winner_name = ranked[0]["name"]
    scaler, model, kind, n_feat = fitted[winner_name]
    feature_order = CANONICAL_FEATURE_ORDER if kind == "v2_8" else FEATURE_ORDER_V3

    import pickle

    with open(SVM_PATH, "wb") as f:
        pickle.dump(model, f)
    with open(SCALER_PATH, "wb") as f:
        pickle.dump(scaler, f)

    counts = Counter(y_all)
    info = {
        "feature_order": feature_order,
        "training_queries": int(len(train_pairs)),
        "n_original_409": len(original),
        "n_traps_added": len(traps_new),
        "traps_skipped_already_in_409": skipped,
        "short": int(counts.get("short", 0)),
        "long": int(counts.get("long", 0)),
        "kernel": "rbf",
        "C": 1.0,
        "gamma": "scale",
        "probability": True,
        "random_state": RANDOM_STATE,
        "selected_variant": winner_name,
        "cv_accuracy_mean": ranked[0]["cv_mean"],
        "cv_accuracy_std": ranked[0]["cv_std"],
        "trained_on": date.today().isoformat(),
        "notes": (
            "Trap-augmented retrain on feat/dual-index-svm-routing. "
            "409 queries keep their original SHORT/LONG labels (mostly length). "
            "40 trap queries use headline-enough vs need-full-article labels "
            "(gold_A/gold_B agreed after correction; not independent raters). "
            "Frozen Phase 3B 86% vs 84% is the V2 result and was not overwritten. "
            "New Phase 3B numbers below leak on trap queries that also appear in the 50."
        ),
        "backup_dir": os.path.relpath(BACKUP_DIR, REPO_ROOT).replace("\\", "/"),
        "variant_table": results,
    }
    with open(INFO_PATH, "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)

    report = {
        "winner": winner_name,
        "n_features": n_feat,
        "n_train": len(train_pairs),
        "skipped_traps_in_409": skipped,
        "n_phase3b_primary": len(p3),
        "n_phase3b_overlap_with_traps": len(p3_overlap),
        "n_phase3b_nonoverlap": len(p3_held),
        "variants": results,
        "backup_dir": info["backup_dir"],
    }
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print()
    print("Deployed:", winner_name, "n_features=", n_feat)
    print("Train size:", len(train_pairs), "(skipped traps already in 409:", skipped, ")")
    print("Phase 3B overlap with traps:", len(p3_overlap), "/", len(p3))
    print("Wrote", SVM_PATH)
    print("Wrote", SCALER_PATH)
    print("Wrote", INFO_PATH)
    print("Wrote", REPORT_PATH)
    print("V2 backup:", BACKUP_DIR)


if __name__ == "__main__":
    main()
