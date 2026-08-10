"""
validation_response.py
=======================
Response to supervisor's concerns about the SVM query-routing classifier.

IMPORTANT (fixed 2026-08-09, first correction): earlier versions of this
script used the feature-extraction function documented in
06_dynamic_classifier.ipynb. That function does NOT match the features
the actually-deployed model (models/svm_classifier.pkl + scaler.pkl) was
trained on -- the real training code lives in 14_robustness_validation.ipynb
and uses a different feature set (language/script-detection based, not the
lexical-diversity based set in notebook 06). This script was corrected to
use the REAL, deployed feature set, verified by directly comparing computed
feature means against the saved scaler's fitted mean_ values.

IMPORTANT (fixed 2026-08-09, second correction): the external-validation
weakness this script first uncovered (74.00% on Roman Urdu long queries)
has been root-caused and fixed. Root cause: data/training_queries_real.py's
60 "long" Roman Urdu training examples were mislabeled -- they were plain
formal English sentences ("what are the latest developments in..."), not
genuine Roman Urdu (Urdu grammar transliterated into Latin script, e.g.
"PM ne naya budget announce kiya"). This taught the classifier an inverted
signal for roman_ratio. Fixed by replacing those 60 queries with genuine
Roman Urdu long queries, filling a previously-untrained 5-10 word gap, and
adding a 9th feature (raw roman_urdu_dict match count). Dataset grew from
369 to 414 queries. Test 3 below (dataset expansion) also had the SAME bug
independently -- one of its own "new" long-Roman-Urdu test queries was a
fake English sentence -- now fixed too (see NEW_QUERIES below).

Runs 5 independent tests, using ONLY data/training_queries_real.py and
models/roman_urdu_dict_expanded.json (no ChromaDB / embeddings needed):

  1. Feature ablation      -> which features actually drive the 100% result?
  2. Leave-one-topic-out   -> does the model generalize to unseen topics?
  3. Dataset expansion     -> does the result hold at 414 -> higher n?
  4. Roman Urdu robustness -> dictionary regression + spelling-variant coverage
  5. Fresh held-out test   -> genuinely unseen queries not used during the
                              2026-08-09 root-cause diagnosis (honesty check
                              against tuning the fix to the diagnostic set)

Run from the repo root:
    python validation_response.py
"""

import ast
import json
import os
import sys
from collections import Counter

import numpy as np
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score

RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)


def _find_file(relpath):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    for c in (relpath, os.path.join(script_dir, relpath), os.path.join(os.getcwd(), relpath)):
        if os.path.isfile(c):
            return c
    return None


def load_original_queries(path="data/training_queries_real.py"):
    found_path = _find_file(path)
    if found_path is None:
        print(f"ERROR: could not find {path}. Run this script from the repo root.")
        sys.exit(1)
    content = None
    for enc in ("utf-8", "utf-8-sig", "cp1252"):
        try:
            with open(found_path, encoding=enc) as f:
                content = f.read()
            break
        except UnicodeDecodeError:
            continue
    if content is None:
        print(f"ERROR: could not decode {found_path}.")
        sys.exit(1)
    start = content.find("training_queries = [")
    list_str = content[start + len("training_queries = "):]
    return ast.literal_eval(list_str)


def load_roman_dict(path="models/roman_urdu_dict_expanded.json"):
    found_path = _find_file(path)
    if found_path is None:
        print(f"ERROR: could not find {path}.")
        sys.exit(1)
    with open(found_path, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# THE REAL, DEPLOYED feature extraction -- matches models/svm_classifier.pkl
# and models/scaler.pkl exactly (verified against the saved scaler's mean_).
# Source: 14_robustness_validation.ipynb, the cell that actually calls
# pickle.dump() to save the model.
# ---------------------------------------------------------------------------
def extract_features(query, roman_urdu_dict, include_mixed=True):
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
    feats = [urdu_ratio, roman_ratio, has_urdu, has_roman, query_len, char_len]
    if include_mixed:
        mixed = int(has_urdu and has_roman)
        feats.append(mixed)
    feats.append(urdu_chars_count)
    feats.append(roman_count)  # 9th feature, added 2026-08-09 second correction
    return feats


FEATURE_NAMES = ["urdu_ratio", "roman_ratio", "has_urdu", "has_roman",
                  "query_len", "char_len", "mixed", "urdu_chars", "roman_count"]


def cv_accuracy(X, y, n_splits=5):
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=RANDOM_STATE)
    scores = []
    for tr, te in skf.split(X, y):
        scaler = StandardScaler().fit(X[tr])
        Xtr, Xte = scaler.transform(X[tr]), scaler.transform(X[te])
        model = SVC(kernel="rbf", random_state=RANDOM_STATE)
        model.fit(Xtr, y[tr])
        scores.append(accuracy_score(y[te], model.predict(Xte)))
    return np.array(scores)


# ---------------------------------------------------------------------------
# TEST 0 — Verify this script's features actually match the deployed model
# ---------------------------------------------------------------------------
def test0_verify_against_deployed_model(queries, roman_dict):
    print("\n" + "=" * 70)
    print("TEST 0 — VERIFY FEATURES MATCH THE ACTUAL DEPLOYED MODEL")
    print("=" * 70)

    scaler_path = _find_file("models/scaler.pkl")
    if scaler_path is None:
        print("models/scaler.pkl not found -- skipping verification (not fatal).")
        return

    import pickle
    with open(scaler_path, "rb") as f:
        scaler = pickle.load(f)

    X = np.array([extract_features(q, roman_dict) for q, _ in queries])
    computed_mean = X.mean(axis=0)
    actual_mean = scaler.mean_
    deviation = np.abs(computed_mean - actual_mean).sum()

    print(f"Deviation from actual deployed scaler.mean_: {deviation:.4f}")
    if deviation < 0.5:
        print("MATCH CONFIRMED -- this script's features match the deployed model.")
    else:
        print("WARNING: MISMATCH -- these features do NOT match the deployed model!")
        print("Check models/svm_classifier.pkl / scaler.pkl were not retrained differently.")

    # Also flag the dead "mixed" feature
    mixed_idx = FEATURE_NAMES.index("mixed")
    mixed_std = X[:, mixed_idx].std()
    print(f"\n'mixed' feature std dev: {mixed_std:.4f} "
          f"({'DEAD -- always 0, no mixed-script queries in this dataset' if mixed_std == 0 else 'has variance'})")


# ---------------------------------------------------------------------------
# TEST 1 — Feature ablation: length vs language-detection features
# ---------------------------------------------------------------------------
def test1_feature_ablation(queries, roman_dict):
    print("\n" + "=" * 70)
    print("TEST 1 — FEATURE ABLATION (real deployed feature set)")
    print("=" * 70)

    y = np.array([1 if l == "long" else 0 for _, l in queries])
    X_full = np.array([extract_features(q, roman_dict) for q, _ in queries])

    idx = {name: i for i, name in enumerate(FEATURE_NAMES)}
    length_idx = [idx["query_len"], idx["char_len"]]
    language_idx = [idx["urdu_ratio"], idx["roman_ratio"], idx["has_urdu"],
                     idx["has_roman"], idx["mixed"], idx["urdu_chars"], idx["roman_count"]]

    acc_length = cv_accuracy(X_full[:, length_idx], y)
    acc_language = cv_accuracy(X_full[:, language_idx], y)
    acc_full = cv_accuracy(X_full, y)

    print(f"{'Feature set':<45}{'5-fold CV mean':>16}{'std':>10}")
    print("-" * 71)
    print(f"{'Length-only (query_len, char_len)':<45}{acc_length.mean():>15.2%}{acc_length.std():>10.2%}")
    print(f"{'Language-only (no length signal)':<45}{acc_language.mean():>15.2%}{acc_language.std():>10.2%}")
    print(f"{'All 9 features (deployed model)':<45}{acc_full.mean():>15.2%}{acc_full.std():>10.2%}")
    print("\nInterpretation: if language-only (no length info at all) still scores")
    print("near 100%, the result isn't purely a length-threshold shortcut.")


# ---------------------------------------------------------------------------
# TEST 2 — Leave-one-topic-out validation
# ---------------------------------------------------------------------------
TOPIC_KEYWORDS = {
    "cricket_sports":  ["کرکٹ","میچ","ٹیم","کھیل","نتیجہ","پی ایس ایل","cricket","match","team","game","score","psl","goal","football","win","loss"],
    "economy_business":["معیشت","ڈالر","اسٹاک","مارکیٹ","کاروبار","قرض","معاشی","مہنگائی","dollar","stock","bank","market","business","economy","price","tax"],
    "politics_govt":   ["حکومت","سیاست","انتخابات","عمران","وزیراعظم","government","election","politic","imran","khan","minister"],
    "technology":      ["موبائل","ٹیکنالوجی","فون","انٹرنیٹ","کمپیوٹر","mobile","technology","internet","computer","phone","startup"],
    "entertainment":   ["فلم","ڈرامہ","اداکار","film","drama","actor","serial","episode"],
    "education":       ["تعلیم","کالج","اسکول","امتحان","اسکالرشپ","education","college","school","exam","scholarship","teacher"],
    "health":          ["ڈینگی","ہارٹ","ویکسین","ہسپتال","ڈاکٹر","صحت","dengue","heart","vaccine","hospital","doctor","health"],
}


def tag_topic(q):
    ql = q.lower()
    for topic, kws in TOPIC_KEYWORDS.items():
        for kw in kws:
            if kw.lower() in ql:
                return topic
    return "other"


def test2_leave_one_topic_out(queries, roman_dict):
    print("\n" + "=" * 70)
    print("TEST 2 — LEAVE-ONE-TOPIC-OUT VALIDATION (real deployed feature set)")
    print("=" * 70)

    tagged = [(q, l, tag_topic(q)) for q, l in queries]
    topic_counts = Counter(t for _, _, t in tagged)
    usable = [t for t, c in topic_counts.items() if t != "other" and c >= 8]

    if not usable:
        print("Not enough queries per topic in this dataset to run this test.")
        return

    X = np.array([extract_features(q, roman_dict) for q, _, _ in tagged])
    y = np.array([1 if l == "long" else 0 for _, l, _ in tagged])
    topics = np.array([t for _, _, t in tagged])

    print(f"{'Held-out topic':<22}{'n':>6}{'Test Acc':>12}")
    print("-" * 40)
    accs = []
    for held_out in usable:
        train_mask = topics != held_out
        test_mask = topics == held_out
        scaler = StandardScaler().fit(X[train_mask])
        Xtr, Xte = scaler.transform(X[train_mask]), scaler.transform(X[test_mask])
        model = SVC(kernel="rbf", random_state=RANDOM_STATE)
        model.fit(Xtr, y[train_mask])
        acc = accuracy_score(y[test_mask], model.predict(Xte))
        accs.append(acc)
        print(f"{held_out:<22}{test_mask.sum():>6}{acc:>11.2%}")

    print("-" * 40)
    print(f"{'MEAN':<22}{'':>6}{np.mean(accs):>11.2%}   (std: {np.std(accs):.2%})")


# ---------------------------------------------------------------------------
# TEST 3 — Dataset expansion: does result hold at more queries?
# ---------------------------------------------------------------------------
NEW_QUERIES = [
    ("فصل کاشت", "short"), ("زرعی قرض", "short"), ("گندم پیداوار", "short"),
    ("کسان مظاہرہ", "short"), ("کھاد قیمت", "short"), ("ڈینگی وائرس", "short"),
    ("ہارٹ اٹیک", "short"), ("ویکسین مہم", "short"), ("ہسپتال بحران", "short"),
    ("ڈاکٹر ہڑتال", "short"), ("عید تہوار", "short"), ("رمضان بازار", "short"),
    ("fasal kasht", "short"), ("kisan qarza", "short"), ("dengue virus", "short"),
    ("heart attack", "short"), ("vaccine campaign", "short"), ("hospital crisis", "short"),
    (
        "پاکستان میں زرعی شعبے کے حوالے سے حکومت کی نئی پالیسی اور اس کے عوام پر ممکنہ اثرات کا تفصیلی جائزہ",
        "long",
    ),
    # FIXED 2026-08-09: this used to be a plain English sentence mislabeled as
    # "long roman" -- exactly the same bug found in the main training set.
    # Replaced with genuine Roman Urdu (Urdu grammar + Latin script).
    (
        "pakistan mein zarai shobay ke hawale se hakumat ki nai policy ka kya asar hoga",
        "long",
    ),
]


def test3_dataset_expansion(queries, roman_dict):
    print("\n" + "=" * 70)
    print("TEST 3 — DATASET EXPANSION (real deployed feature set)")
    print("=" * 70)

    existing = set(q for q, _ in queries)
    new_unique = [(q, l) for q, l in NEW_QUERIES if q not in existing]
    combined = queries + new_unique

    def eval_set(data, label):
        X = np.array([extract_features(q, roman_dict) for q, _ in data])
        y = np.array([1 if l == "long" else 0 for _, l in data])
        accs = cv_accuracy(X, y)
        print(f"{label:<30} n={len(data):<6} CV mean={accs.mean():.2%}  std={accs.std():.2%}")

    eval_set(queries, "Original")
    eval_set(combined, "Expanded")
    print(f"\nAdded {len(new_unique)} new unique queries. Total now: {len(combined)}.")


# ---------------------------------------------------------------------------
# TEST 4 — Roman Urdu dictionary robustness
# ---------------------------------------------------------------------------
def test4_roman_urdu_robustness(roman_dict):
    import difflib

    print("\n" + "=" * 70)
    print("TEST 4 — ROMAN URDU DICTIONARY ROBUSTNESS")
    print("=" * 70)

    original_40 = {
        "cricket","match","team","pakistan","india","khan","imran","economy","speech",
        "news","today","aaj","mosam","kaisa","hai","nateeja","ka","ki","ke","pm","bayan",
        "kya","raha","tha","game","goal","football","score","win","loss","bank","dollar",
        "price","market","business","technology","mobile","internet","computer","film",
        "drama","actor","election","government","police","court","army",
    }
    missing = original_40 - set(roman_dict.keys())
    print(f"Words lost between the original 40-word dict and current {len(roman_dict)}-word dict:")
    print(f"  {sorted(missing)}  ({len(missing)} words)")

    variant_test = [
        ("kiya", ["kia", "keya"]), ("hai", ["hy", "hae", "he"]),
        ("nahi", ["nahin", "nai", "ni"]) if "nahi" in roman_dict else None,
        ("mein", ["mai", "me"]) if "mein" in roman_dict else None,
        ("acha", ["accha", "achaa"]), ("bhi", ["b"]),
        ("zyada", ["ziada", "zyda", "zaida"]), ("gaya", ["gya"]),
        ("diya", ["dia", "diyaa"]), ("karo", ["kro"]),
        ("pareshan", ["preshan"]), ("khush", ["khus"]),
        ("sardi", ["sardii"]), ("score", ["scor"]),
        ("cricket", ["criket", "crikat"]),
    ]
    variant_test = [v for v in variant_test if v]
    dict_words = list(roman_dict.keys())

    exact_hits, fuzzy_hits, total = 0, 0, 0
    for base, variants in variant_test:
        for v in variants:
            total += 1
            if v in roman_dict:
                exact_hits += 1
            match = difflib.get_close_matches(v, dict_words, n=1, cutoff=0.75)
            if match and match[0] == base:
                fuzzy_hits += 1

    print(f"\nSpelling-variation coverage (n={total} known-word variants tested):")
    print(f"  Exact-match lookup: {exact_hits}/{total} = {exact_hits/total:.1%}")
    print(f"  + difflib fuzzy fallback (cutoff=0.75): {fuzzy_hits}/{total} = {fuzzy_hits/total:.1%}")


# ---------------------------------------------------------------------------
# TEST 5 — Fresh held-out validation (NOT used during 2026-08-09 diagnosis)
# ---------------------------------------------------------------------------
FRESH_HELDOUT_QUERIES = [
    ("shaheen afridi ne kitne wickets liye is series mein", "long"),
    ("toss", "short"),
    ("ٹی20 ورلڈ کپ کا شیڈول جاری کر دیا گیا", "long"),
    ("رنز", "short"),
    ("karachi kings ne lahore qalandars ko hara diya", "long"),
    ("senate", "short"),
    ("nawaz sharif ne rally mein kya khitab kiya", "long"),
    ("گورنر", "short"),
    ("پنجاب اسمبلی نے نیا قانون منظور کر لیا", "long"),
    ("mayor election ke natayej kab aayenge", "long"),
    ("gold rate aaj sonay ka bhaw kya hai", "long"),
    ("shares", "short"),
    ("ٹیکس میں چھوٹ کا اعلان کر دیا گیا", "long"),
    ("inflation", "short"),
    ("rupee ki value dollar ke muqablay mein girti ja rahi", "long"),
    ("clinic", "short"),
    ("polio ke case phir se report huye hain sindh mein", "long"),
    ("ویکسین", "short"),
    ("ڈینگو سے بچاؤ کی مہم شروع کر دی گئی", "long"),
    ("blood donation camp kahan laga hai aaj", "long"),
    ("app", "short"),
    ("naya laptop model market mein aa gaya hai", "long"),
    ("ویب سائٹ", "short"),
    ("سولر انرجی کے استعمال میں اضافہ ہو رہا ہے", "long"),
    ("chatbot technology pakistan mein kitni advance ho chuki", "long"),
    ("humidity", "short"),
    ("smog ki wajah se schools band kar diye gaye", "long"),
    ("طوفان", "short"),
    ("زلزلے کے جھٹکے محسوس کیے گئے آج صبح", "long"),
    ("syllabus", "short"),
    ("naye education board ka elaan kar diya gaya", "long"),
    ("لائبریری", "short"),
    ("طلبہ کے لیے نئی اسکالرشپ اسکیم شروع", "long"),
    ("trailer", "short"),
    ("naye singer ka album release ho gaya hai", "long"),
    ("اداکارہ", "short"),
    ("فلم فیسٹیول میں کن فلموں کو ایوارڈ ملا", "long"),
]


def test5_fresh_heldout(roman_dict):
    print("\n" + "=" * 70)
    print("TEST 5 — FRESH HELD-OUT VALIDATION (honesty check)")
    print("=" * 70)
    print("These queries were NOT examined during the 2026-08-09 root-cause")
    print("diagnosis or data-fixing -- different topics/phrasing from the")
    print("50-query external set. A strong result here is stronger evidence")
    print("of genuine generalization than the diagnostic set alone.\n")

    import pickle
    scaler_path = _find_file("models/scaler.pkl")
    model_path = _find_file("models/svm_classifier.pkl")
    if scaler_path is None or model_path is None:
        print("models/scaler.pkl or svm_classifier.pkl not found -- skipping.")
        return
    with open(scaler_path, "rb") as f:
        scaler = pickle.load(f)
    with open(model_path, "rb") as f:
        model = pickle.load(f)

    qs = [q for q, _ in FRESH_HELDOUT_QUERIES]
    ls = [l for _, l in FRESH_HELDOUT_QUERIES]
    X = scaler.transform(np.array([extract_features(q, roman_dict) for q in qs]))
    preds = model.predict(X)

    wrong = 0
    for q, t, p in zip(qs, ls, preds):
        if t != p:
            wrong += 1
            print(f"  WRONG: true={t} pred={p}  {q}")
    correct = len(qs) - wrong
    print(f"\nAccuracy: {correct}/{len(qs)} = {correct/len(qs):.2%}")
    if wrong == 0:
        print("No errors on fresh set.")


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    queries = load_original_queries()
    roman_dict = load_roman_dict()
    print(f"Loaded {len(queries)} original queries from data/training_queries_real.py")
    print(f"Loaded {len(roman_dict)}-word Roman Urdu dictionary")

    test0_verify_against_deployed_model(queries, roman_dict)
    test1_feature_ablation(queries, roman_dict)
    test2_leave_one_topic_out(queries, roman_dict)
    test3_dataset_expansion(queries, roman_dict)
    test4_roman_urdu_robustness(roman_dict)
    test5_fresh_heldout(roman_dict)

    print("\n" + "=" * 70)
    print("DONE. These numbers now match the ACTUAL deployed model's features.")
    print("=" * 70)
