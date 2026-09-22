#!/usr/bin/env python3
"""
C1 — Query-only expert detectability diagnostic.

TRAIN/DEV only (Phase 13 scoring population n=80).
TEST is never loaded.

Policies declared BEFORE fitting (do not change after seeing results):

PRIMARY label set:
  Queries with exactly one Hit@5 success among {BM25, NG3, Dense}.

SECONDARY tie policy (for sensitivity / full at-least-one set):
  Among experts with Hit@5==1, assign label by fixed priority
  Dense > NG3 > BM25
  (priority declared from frozen Program B aggregate Hit@5 strength order
   on n=80: Dense 20 > NG3 10 > BM25 5; Phase 14 SoT — not fitted in C1).

Models (pre-declared):
  - Majority-class baseline (train-fold majority)
  - Stratified multinomial logistic regression (class_weight='balanced', max_iter=2000)
  - Optional shallow DecisionTreeClassifier(max_depth=3) as secondary interpretability check

CV:
  Leave-one-out on the PRIMARY unique-winner set (n small; BM25 has 1 unique win).
  Same LOO for secondary sensitivity set.

Random seed: 42 (used only where sklearn requires it; LOO has no fold shuffle).

No retrieval rerun. No TEST. No gold text features. No retrieval-score features.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.model_selection import LeaveOneOut
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = Path(__file__).resolve().parent
PHASE13 = ROOT / "experiments/ultra_v2/phase13_population/artifacts/scoring/PHASE13_SCORING_PER_QUERY.csv"
DICT_PATH = ROOT / "models/roman_urdu_dict_expanded.json"

EXPERTS = ("BM25", "NG3", "Dense")
TIE_PRIORITY = ("Dense", "NG3", "BM25")  # declared a priori
SEED = 42

# Fixed English function-word list (common closed-class + ultra-common content stop list).
# NOT derived from ULTRA queries, gold, or TEST.
ENGLISH_STOP = frozenset(
    """
    a an the and or but if then else when while for of to in on at by from with
    as into onto over under about against between through during before after
    above below up down out off again further once here there all any both each
    few more most other some such no nor not only own same so than too very can
    will just don should now is are was were be been being have has had do does
    did having this that these those i you he she it we they me him her us them
    my your his its our their what which who whom whose how why where
    """.split()
)

FEATURE_GROUPS = {
    "length": [
        "char_len",
        "token_count",
        "mean_tok_len",
        "median_tok_len",
        "max_tok_len",
        "tok_len_var",
    ],
    "orthographic": [
        "repeated_char_count",
        "repeated_char_ratio",
        "vowel_ratio",
        "consonant_ratio",
        "tok_len_var",
    ],
    "script_codemix": [
        "digit_ratio",
        "punct_ratio",
        "uppercase_ratio",
        "has_digit",
        "has_alnum_mix",
        "ru_dict_hit_ratio",
        "unknown_token_ratio",
        "english_stop_ratio",
        "code_mix_indicator",
    ],
    "lexical_surface": [
        "unique_token_ratio",
        "short_token_ratio",
        "long_token_ratio",
        "acronym_like_count",
        "digit_token_count",
        "max_tok_len",
    ],
}


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        for k in list(r.keys()):
            if "query_id" in k and k != "query_id":
                r["query_id"] = r[k]
    return rows


def tokenize(q: str) -> list[str]:
    return [t for t in re.findall(r"[A-Za-z0-9']+|[^\sA-Za-z0-9]", q) if t.strip()]


def alpha_tokens(tokens: list[str]) -> list[str]:
    return [t for t in tokens if re.search(r"[A-Za-z]", t)]


def compute_features(query: str, ru_keys: set[str]) -> dict:
    q = query.strip()
    tokens = tokenize(q)
    alphas = alpha_tokens(tokens)
    lower_alphas = [t.lower() for t in alphas]
    char_len = len(q)
    token_count = max(len(alphas), 1)  # avoid div0; empty handled below
    if not alphas:
        # Degenerate empty alpha query — still return zeros
        base = {k: 0.0 for group in FEATURE_GROUPS.values() for k in group}
        base.update(
            {
                "char_len": float(char_len),
                "token_count": 0.0,
                "mean_tok_len": 0.0,
                "median_tok_len": 0.0,
                "max_tok_len": 0.0,
                "tok_len_var": 0.0,
            }
        )
        return base

    lengths = [len(t) for t in alphas]
    mean_tok_len = float(statistics.mean(lengths))
    median_tok_len = float(statistics.median(lengths))
    max_tok_len = float(max(lengths))
    tok_len_var = float(statistics.pvariance(lengths)) if len(lengths) > 1 else 0.0

    # repeated consecutive characters within tokens (e.g. "aa", "lll")
    rep_count = 0
    for t in alphas:
        for a, b in zip(t, t[1:]):
            if a.lower() == b.lower() and a.isalpha():
                rep_count += 1
    letters = [c for c in q if c.isalpha()]
    vowels = sum(1 for c in letters if c.lower() in "aeiou")
    consonants = sum(1 for c in letters if c.isalpha() and c.lower() not in "aeiou")
    n_letters = max(len(letters), 1)

    digits = sum(1 for c in q if c.isdigit())
    punct = sum(1 for c in q if not c.isalnum() and not c.isspace())
    upper = sum(1 for c in q if c.isupper())
    n_chars = max(char_len, 1)

    unique_ratio = len(set(lower_alphas)) / len(alphas)
    short_ratio = sum(1 for L in lengths if L <= 3) / len(alphas)
    long_ratio = sum(1 for L in lengths if L >= 8) / len(alphas)

    ru_hits = sum(1 for t in lower_alphas if t in ru_keys)
    eng_hits = sum(1 for t in lower_alphas if t in ENGLISH_STOP)
    ru_ratio = ru_hits / len(alphas)
    eng_ratio = eng_hits / len(alphas)
    unknown_ratio = 1.0 - ru_ratio

    # acronym-like: short alphabetic token, mostly consonants or all-caps in original
    acronym_like = 0
    for t, tl in zip(alphas, lower_alphas):
        if not t.isalpha():
            continue
        if len(t) <= 4 and (t.isupper() or sum(1 for c in tl if c not in "aeiou") >= max(len(tl) - 1, 1)):
            if len(t) >= 2:
                acronym_like += 1
    digit_tok = sum(1 for t in alphas if any(c.isdigit() for c in t))
    has_alnum_mix = 1.0 if any(re.search(r"[A-Za-z]", t) and re.search(r"\d", t) for t in alphas) else 0.0

    return {
        "char_len": float(char_len),
        "token_count": float(len(alphas)),
        "mean_tok_len": mean_tok_len,
        "median_tok_len": median_tok_len,
        "max_tok_len": max_tok_len,
        "tok_len_var": tok_len_var,
        "repeated_char_count": float(rep_count),
        "repeated_char_ratio": float(rep_count) / max(sum(lengths), 1),
        "vowel_ratio": vowels / n_letters,
        "consonant_ratio": consonants / n_letters,
        "digit_ratio": digits / n_chars,
        "punct_ratio": punct / n_chars,
        "uppercase_ratio": upper / n_chars,
        "has_digit": 1.0 if digits else 0.0,
        "has_alnum_mix": has_alnum_mix,
        "unique_token_ratio": unique_ratio,
        "short_token_ratio": short_ratio,
        "long_token_ratio": long_ratio,
        "ru_dict_hit_ratio": ru_ratio,
        "unknown_token_ratio": unknown_ratio,
        "english_stop_ratio": eng_ratio,
        "code_mix_indicator": 1.0 if (ru_hits > 0 and eng_hits > 0) else 0.0,
        "acronym_like_count": float(acronym_like),
        "digit_token_count": float(digit_tok),
    }


def expert_hits(row: dict) -> dict[str, int]:
    return {
        "BM25": int(row["bm25_hit@5"]),
        "NG3": int(row["ng3_hit@5"]),
        "Dense": int(row["dense_hit@5"]),
    }


def unique_winner(hits: dict[str, int]) -> str | None:
    winners = [e for e in EXPERTS if hits[e] == 1]
    if len(winners) == 1:
        return winners[0]
    return None


def tie_broken_label(hits: dict[str, int]) -> str | None:
    winners = [e for e in EXPERTS if hits[e] == 1]
    if not winners:
        return None
    if len(winners) == 1:
        return winners[0]
    for e in TIE_PRIORITY:
        if e in winners:
            return e
    return winners[0]


def wilson_interval(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / denom
    margin = z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    return (max(0.0, centre - margin), min(1.0, centre + margin))


def build_matrix(feat_dicts: list[dict], names: list[str]) -> np.ndarray:
    return np.array([[fd[n] for n in names] for fd in feat_dicts], dtype=float)


def loo_predict(X: np.ndarray, y: np.ndarray, labels: list[str], model_kind: str) -> np.ndarray:
    loo = LeaveOneOut()
    preds = np.empty(len(y), dtype=object)
    for train_idx, test_idx in loo.split(X):
        Xtr, Xte = X[train_idx], X[test_idx]
        ytr = y[train_idx]
        # train-fold majority for baseline
        if model_kind == "majority":
            maj = Counter(ytr).most_common(1)[0][0]
            preds[test_idx[0]] = maj
            continue
        # If a class is missing in train (possible with BM25 n=1 LOO), fall back to majority
        present = set(ytr)
        if len(present) < 2:
            preds[test_idx[0]] = Counter(ytr).most_common(1)[0][0]
            continue
        if model_kind == "logreg":
            clf = Pipeline(
                [
                    ("scaler", StandardScaler()),
                    (
                        "lr",
                        LogisticRegression(
                            multi_class="multinomial",
                            class_weight="balanced",
                            max_iter=2000,
                            random_state=SEED,
                            solver="lbfgs",
                        ),
                    ),
                ]
            )
        elif model_kind == "tree":
            clf = DecisionTreeClassifier(
                max_depth=3,
                class_weight="balanced",
                random_state=SEED,
            )
        else:
            raise ValueError(model_kind)
        clf.fit(Xtr, ytr)
        preds[test_idx[0]] = clf.predict(Xte)[0]
    return preds


def eval_preds(y_true: np.ndarray, y_pred: np.ndarray, labels: list[str]) -> dict:
    acc = accuracy_score(y_true, y_pred)
    macro = f1_score(y_true, y_pred, labels=labels, average="macro", zero_division=0)
    bal = balanced_accuracy_score(y_true, y_pred)
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    report = classification_report(
        y_true, y_pred, labels=labels, zero_division=0, digits=3
    )
    lo, hi = wilson_interval(int(acc * len(y_true) + 1e-12), len(y_true))
    # exact count for wilson
    k = int(np.sum(y_true == y_pred))
    lo, hi = wilson_interval(k, len(y_true))
    return {
        "n": len(y_true),
        "correct": k,
        "accuracy": acc,
        "wilson95": (lo, hi),
        "macro_f1": macro,
        "balanced_accuracy": bal,
        "confusion_matrix": cm,
        "labels": labels,
        "report": report,
    }


def routing_hit5(rows: list[dict], predicted: dict[str, str]) -> int:
    """predicted: query_id -> expert name; uses frozen Hit@5 of that expert."""
    key = {"BM25": "bm25_hit@5", "NG3": "ng3_hit@5", "Dense": "dense_hit@5"}
    return sum(int(r[key[predicted[r["query_id"]]]]) for r in rows)


def main() -> int:
    assert PHASE13.is_file(), PHASE13
    assert DICT_PATH.is_file(), DICT_PATH

    # Safety: refuse any path containing benchmark/test
    for p in (PHASE13, DICT_PATH):
        if "benchmark/test" in str(p).replace("\\", "/"):
            print("REFUSING TEST PATH", p)
            return 2

    phase13_sha = file_sha256(PHASE13)
    dict_sha = file_sha256(DICT_PATH)
    ru_dict = json.loads(DICT_PATH.read_text(encoding="utf-8"))
    ru_keys = set(k.lower() for k in ru_dict.keys())

    rows = load_rows(PHASE13)
    assert len(rows) == 80, len(rows)

    # --- Complementarity ---
    pattern_counts = Counter()
    bucket = Counter()
    for r in rows:
        h = expert_hits(r)
        pattern_counts[(h["BM25"], h["NG3"], h["Dense"])] += 1
        uw = unique_winner(h)
        if uw:
            bucket[f"UNIQUE_{uw}"] += 1
        elif sum(h.values()) == 0:
            bucket["ALL_FAIL"] += 1
        else:
            w = [e for e in EXPERTS if h[e]]
            bucket["TIE_" + "+".join(w)] += 1

    # pairwise
    def pair_stats(a: str, b: str):
        both = sum(1 for r in rows if expert_hits(r)[a] and expert_hits(r)[b])
        a_only = sum(1 for r in rows if expert_hits(r)[a] and not expert_hits(r)[b])
        b_only = sum(1 for r in rows if expert_hits(r)[b] and not expert_hits(r)[a])
        return both, a_only, b_only

    # --- Features for all rows ---
    all_feat_names = sorted({n for g in FEATURE_GROUPS.values() for n in g})
    feat_by_id = {}
    feature_rows_out = []
    for r in rows:
        # NEVER write source_doc_id / ranks / hit flags into feature CSV
        fd = compute_features(r["query_text"], ru_keys)
        feat_by_id[r["query_id"]] = fd
        out = {"query_id": r["query_id"], "split": r["split"], "cohort": r["cohort"]}
        out.update(fd)
        feature_rows_out.append(out)

    feat_csv = OUT_DIR / "C1_QUERY_FEATURES.csv"
    with feat_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["query_id", "split", "cohort"] + all_feat_names)
        w.writeheader()
        for row in feature_rows_out:
            w.writerow(row)

    # --- Primary / secondary sets ---
    primary = []
    secondary = []
    for r in rows:
        h = expert_hits(r)
        uw = unique_winner(h)
        tb = tie_broken_label(h)
        if uw:
            primary.append((r, uw))
        if tb:
            secondary.append((r, tb))

    results = {
        "phase13_sha": phase13_sha,
        "dict_sha": dict_sha,
        "n_total": len(rows),
        "pattern_counts": {str(k): v for k, v in pattern_counts.items()},
        "buckets": dict(bucket),
        "pairwise": {
            "BM25_vs_NG3": pair_stats("BM25", "NG3"),
            "BM25_vs_Dense": pair_stats("BM25", "Dense"),
            "NG3_vs_Dense": pair_stats("NG3", "Dense"),
        },
        "primary_n": len(primary),
        "secondary_n": len(secondary),
        "primary_label_counts": dict(Counter(y for _, y in primary)),
        "secondary_label_counts": dict(Counter(y for _, y in secondary)),
    }

    def run_set(name: str, items: list[tuple[dict, str]], feature_names: list[str]):
        y = np.array([lab for _, lab in items], dtype=object)
        X = build_matrix([feat_by_id[r["query_id"]] for r, _ in items], feature_names)
        labels_present = [e for e in EXPERTS if e in set(y)]
        out = {"label_counts": dict(Counter(y))}
        for kind in ("majority", "logreg", "tree"):
            preds = loo_predict(X, y, labels_present, kind)
            out[kind] = eval_preds(y, preds, labels_present)
            out[kind]["predictions"] = list(zip([r["query_id"] for r, _ in items], list(y), list(preds)))
        return out

    results["primary_combined"] = run_set("primary", primary, all_feat_names)
    results["secondary_combined"] = run_set("secondary", secondary, all_feat_names)

    # Feature-group ablation on PRIMARY only (pre-declared groups)
    results["primary_ablation"] = {}
    for gname, gfeats in FEATURE_GROUPS.items():
        # dedupe while preserving order
        names = list(dict.fromkeys(gfeats))
        results["primary_ablation"][gname] = run_set(gname, primary, names)

    # --- Offline routing simulation on full n=80 ---
    # Fit logreg on PRIMARY unique-winners with LOO predictions for those;
    # for non-primary queries use a model trained on all primary (full fit) —
    # BUT that would leak for reporting accuracy on primary.
    # For routing: use LOO predictions on primary; for other queries, predict with
    # model trained on all primary (they were not in the accuracy set's test circularity
    # for ALL_FAIL / TIE queries). Document clearly.
    y_pri = np.array([lab for _, lab in primary], dtype=object)
    X_pri = build_matrix([feat_by_id[r["query_id"]] for r, _ in primary], all_feat_names)
    loo_preds_pri = loo_predict(X_pri, y_pri, [e for e in EXPERTS if e in set(y_pri)], "logreg")
    loo_map = {r["query_id"]: pred for (r, _), pred in zip(primary, loo_preds_pri)}

    # Model on all primary for out-of-primary queries (ALL_FAIL + ties)
    full_clf = Pipeline(
        [
            ("scaler", StandardScaler()),
            (
                "lr",
                LogisticRegression(
                    multi_class="multinomial",
                    class_weight="balanced",
                    max_iter=2000,
                    random_state=SEED,
                    solver="lbfgs",
                ),
            ),
        ]
    )
    if len(set(y_pri)) >= 2:
        full_clf.fit(X_pri, y_pri)
        can_full = True
    else:
        can_full = False
    maj_global = Counter(y_pri).most_common(1)[0][0]

    routed_pred = {}
    for r in rows:
        qid = r["query_id"]
        if qid in loo_map:
            routed_pred[qid] = loo_map[qid]
        elif can_full:
            x = build_matrix([feat_by_id[qid]], all_feat_names)
            routed_pred[qid] = full_clf.predict(x)[0]
        else:
            routed_pred[qid] = maj_global

    majority_pred = {r["query_id"]: maj_global for r in rows}
    always = {e: {r["query_id"]: e for r in rows} for e in EXPERTS}
    oracle_pred = {}
    for r in rows:
        h = expert_hits(r)
        tb = tie_broken_label(h)
        # oracle: any success counts; pick a succeeding expert if any (priority)
        if tb:
            oracle_pred[r["query_id"]] = tb
        else:
            oracle_pred[r["query_id"]] = "Dense"  # dummy; Hit@5 will be 0 for all

    routing = {
        "BM25_fixed": routing_hit5(rows, always["BM25"]),
        "NG3_fixed": routing_hit5(rows, always["NG3"]),
        "Dense_fixed": routing_hit5(rows, always["Dense"]),
        "majority_routing": routing_hit5(rows, majority_pred),
        "query_only_logreg_routing": routing_hit5(rows, routed_pred),
        "oracle_upper_bound": sum(
            1 for r in rows if sum(expert_hits(r).values()) > 0
        ),
        "majority_expert": maj_global,
        "n": 80,
    }
    results["routing"] = routing

    # Coefficient inspection on full primary fit (interpretability, not CV)
    coef_info = {}
    if can_full:
        lr = full_clf.named_steps["lr"]
        classes = list(lr.classes_)
        coefs = lr.coef_  # shape (n_classes, n_features) or (1, n) for binary
        if coefs.shape[0] == 1 and len(classes) == 2:
            # binary: coefs for classes[1]
            coef_info["classes"] = classes
            coef_info["top"] = sorted(
                zip(all_feat_names, coefs[0]), key=lambda x: -abs(x[1])
            )[:10]
        else:
            coef_info["classes"] = classes
            coef_info["per_class_top"] = {}
            for i, cls in enumerate(classes):
                coef_info["per_class_top"][cls] = sorted(
                    zip(all_feat_names, coefs[i]), key=lambda x: -abs(x[1])
                )[:8]
    results["coef_info"] = coef_info

    # Write JSON summary for the markdown author
    summary_path = OUT_DIR / "C1_RESULTS_SUMMARY.json"
    # make JSON-serializable
    def conv(o):
        if isinstance(o, np.ndarray):
            return o.tolist()
        if isinstance(o, np.floating):
            return float(o)
        if isinstance(o, np.integer):
            return int(o)
        if isinstance(o, dict):
            return {str(k): conv(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)):
            return [conv(x) for x in o]
        return o

    summary_path.write_text(json.dumps(conv(results), indent=2), encoding="utf-8")

    # Console report
    print("=== C1 DETECTABILITY ===")
    print("TEST_CONTENT_ACCESSED = FALSE")
    print("phase13_sha", phase13_sha)
    print("dict_sha", dict_sha)
    print("buckets", dict(bucket))
    print("primary_n", len(primary), "labels", Counter(y for _, y in primary))
    print("secondary_n", len(secondary), "labels", Counter(y for _, y in secondary))
    for setname in ("primary_combined", "secondary_combined"):
        print(f"\n-- {setname} --")
        for kind in ("majority", "logreg", "tree"):
            e = results[setname][kind]
            print(
                f"{kind}: acc={e['accuracy']:.4f} [{e['wilson95'][0]:.3f},{e['wilson95'][1]:.3f}] "
                f"macroF1={e['macro_f1']:.4f} bal={e['balanced_accuracy']:.4f} "
                f"correct={e['correct']}/{e['n']}"
            )
            print("cm labels", e["labels"])
            print(np.array(e["confusion_matrix"]))
    print("\n-- ablation primary logreg --")
    for g, res in results["primary_ablation"].items():
        e = res["logreg"]
        print(f"{g}: acc={e['accuracy']:.4f} macroF1={e['macro_f1']:.4f} bal={e['balanced_accuracy']:.4f}")
    print("\n-- routing n=80 --")
    for k, v in routing.items():
        print(k, v)
    print("Wrote", feat_csv)
    print("Wrote", summary_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
