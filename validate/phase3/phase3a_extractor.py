"""
validate/phase3/phase3a_extractor.py
=====================================
Phase 3A — Standalone canonical 8-feature extractor for the frozen,
deployed V2 SVM (models/svm_classifier.pkl + models/scaler.pkl).

WHY THIS FILE EXISTS
---------------------
validation_response.py's extract_features() returns 9 values (it appends
an undocumented `roman_count` as a 9th feature on 2026-08-09). The
deployed scaler/model expect exactly 8 features
(scaler.n_features_in_ == model.n_features_in_ == 8), so that function
cannot be passed directly to scaler.transform() / model.predict() --
doing so raises:
    ValueError: X has 9 features, but StandardScaler is expecting 8
                features as input.

This file provides a standalone extractor that returns ONLY the
canonical 8 features, plus a verification routine that confirms --
from repository evidence, not assumption -- that those 8 values are in
the exact order the deployed scaler was fit on.

CANONICAL FEATURE ORDER (8 features)
-------------------------------------
    1. urdu_ratio
    2. roman_ratio
    3. has_urdu
    4. has_roman
    5. query_len
    6. char_len
    7. mixed
    8. urdu_chars

EVIDENCE THIS ORDER IS CORRECT (not merely "slice off the 9th value")
-----------------------------------------------------------------------
1. models/training_info.json ships a "feature_order" key, committed
   alongside the trained model, listing exactly these 8 names in this
   exact order.
2. Computing this 8-feature extractor over all 409 rows of
   data/training_queries_real.py and taking the column-wise mean
   reproduces models/scaler.pkl's fitted `mean_` array EXACTLY
   (elementwise abs difference sums to 0.0 -- see
   verify_against_deployed_scaler() below, and the run log in
   PHASE3A_VERIFICATION_REPORT.md). Since StandardScaler.mean_ is the
   per-feature training mean in fit order, an exact match across all
   8 dimensions is only possible if this extractor's feature order
   matches the order the scaler was actually fit on.
3. The 7th value ("mixed") has scaler.scale_[6] == 1.0 with
   scaler.mean_[6] == 0.0 -- consistent with the already-documented
   fact that `mixed` is a dead feature (no mixed-script queries existed
   in the 409-query training set, so StandardScaler falls back to
   scale=1 to avoid division by zero). This is an independent
   consistency check, not just a coincidence of order.
4. The first 8 values computed by validation_response.extract_features()
   are, line for line, the same 8 expressions (same variable names, same
   order of list construction) as this file's extract_features_phase3a() --
   this file does not invent new feature logic, it isolates the existing,
   already-used logic and drops the 9th append.

This file does NOT modify, retrain, or re-fit anything:
    - models/svm_classifier.pkl and models/scaler.pkl are only ever
      opened with pickle.load() (pure deserialize) and passed through
      .transform() / .predict() (pure inference).
    - No .fit(), .partial_fit(), or StandardScaler(...) construction
      occurs anywhere in this file.
    - Phase 3B evaluation set files are never opened by this file.

Run from the repo root:
    python validate/phase3/phase3a_extractor.py
"""

import json
import os
import pickle

import numpy as np

CANONICAL_FEATURE_ORDER = [
    "urdu_ratio", "roman_ratio", "has_urdu", "has_roman",
    "query_len", "char_len", "mixed", "urdu_chars",
]


def extract_features_phase3a(query, roman_urdu_dict):
    """
    Return the canonical 8-feature vector for `query`, in the exact
    order the deployed models/scaler.pkl was fit on (see module
    docstring for evidence). Does not append roman_count (the 9th,
    unused-by-the-deployed-model feature present in
    validation_response.extract_features()).
    """
    urdu_chars_count = sum(1 for c in query if "\u0600" <= c <= "\u06FF")
    total_chars = len(query.replace(" ", "")) + 1e-9
    urdu_ratio = urdu_chars_count / total_chars
    words = query.split()
    roman_count = sum(1 for w in words if w.lower() in roman_urdu_dict)
    roman_ratio = roman_count / (len(words) + 1e-9)
    has_urdu = int(urdu_chars_count > 0)
    has_roman = int(roman_count > 0)
    query_len = len(words)
    char_len = len(query)
    mixed = int(has_urdu and has_roman)
    return [urdu_ratio, roman_ratio, has_urdu, has_roman,
            query_len, char_len, mixed, urdu_chars_count]


def _find_file(relpath):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
    for c in (relpath, os.path.join(repo_root, relpath), os.path.join(os.getcwd(), relpath)):
        if os.path.isfile(c):
            return c
    return None


def load_roman_dict():
    path = _find_file("models/roman_urdu_dict_expanded.json")
    if path is None:
        raise FileNotFoundError("models/roman_urdu_dict_expanded.json not found.")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_training_queries():
    """Read-only load of data/training_queries_real.py, used ONLY to
    reproduce the scaler's fitted mean_ as an evidence check. Nothing
    is fit here."""
    import ast
    path = _find_file("data/training_queries_real.py")
    if path is None:
        raise FileNotFoundError("data/training_queries_real.py not found.")
    with open(path, encoding="utf-8") as f:
        content = f.read()
    start = content.find("training_queries = [")
    list_str = content[start + len("training_queries = "):]
    return ast.literal_eval(list_str)


def verify_against_deployed_scaler():
    """
    Evidence check (read-only): recompute the 8-feature column means
    over all 409 training queries and compare against
    models/scaler.pkl's fitted mean_. This scaler is loaded via
    pickle.load() only -- never fit here.
    """
    scaler_path = _find_file("models/scaler.pkl")
    if scaler_path is None:
        raise FileNotFoundError("models/scaler.pkl not found.")

    with open(scaler_path, "rb") as f:
        scaler = pickle.load(f)  # pure deserialize, no .fit()

    roman_dict = load_roman_dict()
    queries = load_training_queries()

    X = np.array([extract_features_phase3a(q, roman_dict) for q, _ in queries])
    computed_mean = X.mean(axis=0)
    deviation = np.abs(computed_mean - scaler.mean_).sum()

    return {
        "scaler_n_features_in": int(scaler.n_features_in_),
        "extractor_output_width": int(X.shape[1]),
        "computed_mean": computed_mean.tolist(),
        "scaler_mean": scaler.mean_.tolist(),
        "deviation_sum": float(deviation),
        "match": bool(deviation < 1e-9),
    }


def run_representative_tests():
    """
    Test the extractor on one Urdu, one Roman Urdu, and one mixed
    query. For each: confirm exactly 8 features are returned, load
    models/scaler.pkl via pickle.load() only, and confirm
    scaler.transform() accepts the resulting vector without error.
    No .fit() is called anywhere in this function.
    """
    roman_dict = load_roman_dict()

    scaler_path = _find_file("models/scaler.pkl")
    model_path = _find_file("models/svm_classifier.pkl")
    with open(scaler_path, "rb") as f:
        scaler = pickle.load(f)  # pure deserialize
    with open(model_path, "rb") as f:
        model = pickle.load(f)  # pure deserialize

    test_queries = {
        "urdu":       "کراچی میں بارش کے بعد ٹریفک کی صورتحال کیا ہے",
        "roman_urdu": "karachi mein barish ke baad traffic ki surat e hal kya hai",
        "mixed":      "PM ne budget پیش کیا aaj",
    }

    results = {}
    for label, q in test_queries.items():
        feats = extract_features_phase3a(q, roman_dict)
        assert len(feats) == 8, f"{label}: expected 8 features, got {len(feats)}"

        X = np.array([feats])
        Xt = scaler.transform(X)  # pure inference, raises if shape mismatched
        pred = model.predict(Xt)[0]  # pure inference

        results[label] = {
            "query": q,
            "raw_features": feats,
            "vector_length": len(feats),
            "scaled_vector": Xt[0].tolist(),
            "prediction": str(pred),
        }
    return results


if __name__ == "__main__":
    print("=" * 70)
    print("PHASE 3A — STANDALONE 8-FEATURE EXTRACTOR VERIFICATION")
    print("=" * 70)

    print("\n[1] Verifying feature order against deployed scaler.mean_")
    print("    (read-only: pickle.load() only, no .fit() anywhere)")
    ev = verify_against_deployed_scaler()
    print(f"    scaler.n_features_in_      : {ev['scaler_n_features_in']}")
    print(f"    extractor output width     : {ev['extractor_output_width']}")
    print(f"    deviation from scaler.mean_: {ev['deviation_sum']:.10f}")
    print(f"    MATCH: {ev['match']}")

    print("\n[2] Representative test queries (Urdu / Roman Urdu / mixed)")
    res = run_representative_tests()
    for label, r in res.items():
        print(f"\n  -- {label} --")
        print(f"     query          : {r['query']}")
        print(f"     vector length  : {r['vector_length']}")
        print(f"     raw features   : {r['raw_features']}")
        print(f"     scaler.transform() succeeded, scaled vector:")
        print(f"       {r['scaled_vector']}")
        print(f"     model.predict(): {r['prediction']} (informational only -- "
              f"NOT a Phase 3B run, no prediction file written)")

    print("\n" + "=" * 70)
    print("DONE. No files modified. No .fit()/.partial_fit() called.")
    print("Phase 3B CSV/metadata were never opened by this script.")
    print("=" * 70)
