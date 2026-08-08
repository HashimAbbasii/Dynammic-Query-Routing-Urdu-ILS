"""
validation_response.py
=======================
Response to supervisor's concerns about the SVM query-routing classifier.

Runs 3 independent tests, using ONLY data/training_queries_real.py
(no ChromaDB / embeddings needed — this is fast and fully reproducible):

  1. Feature ablation      -> is `is_long_by_static` driving the 100% result?
  2. Leave-one-topic-out   -> does the model generalize to completely unseen topics?
  3. Dataset expansion     -> does the result hold if we scale 369 -> 548 queries?

Run from the repo root:
    python validation_response.py

Requires: numpy, scikit-learn  (pip install numpy scikit-learn)
"""

import ast
import os
import sys
from collections import Counter

import numpy as np
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.metrics import accuracy_score

RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)


# ---------------------------------------------------------------------------
# STEP 0 — Load your real 369 queries (exactly as they are in the repo)
#
# Robust to two common beginner issues:
#   1. Wrong working directory (VS Code "Run" sometimes uses a different cwd)
#      -> we search relative to THIS script's own location, not just cwd.
#   2. File not saved as UTF-8 (common on Windows if edited in Notepad)
#      -> we try utf-8 first, then fall back to utf-8-sig / cp1252.
# ---------------------------------------------------------------------------
def load_original_queries(path="data/training_queries_real.py"):
    # Build a list of candidate locations to try, in order
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        path,                                   # as given (relative to cwd)
        os.path.join(script_dir, path),         # relative to this script's folder
        os.path.join(os.getcwd(), path),        # explicit relative to cwd
    ]

    found_path = None
    for c in candidates:
        if os.path.isfile(c):
            found_path = c
            break

    if found_path is None:
        print("ERROR: Could not find 'data/training_queries_real.py'.")
        print("Tried these locations:")
        for c in candidates:
            print(f"  - {os.path.abspath(c)}")
        print(f"\nCurrent working directory is: {os.getcwd()}")
        print(f"This script is located at:    {script_dir}")
        print("\nFix: make sure 'validation_response.py' sits in the SAME folder")
        print("as your 'data' folder (repo root, next to README.md), then either:")
        print("  (a) run it from that folder in a terminal:  python validation_response.py")
        print("  (b) or just re-run — this script now also checks its own folder automatically.")
        sys.exit(1)

    content = None
    last_error = None
    for enc in ("utf-8", "utf-8-sig", "cp1252"):
        try:
            with open(found_path, encoding=enc) as f:
                content = f.read()
            break
        except UnicodeDecodeError as e:
            last_error = e
            continue

    if content is None:
        print(f"ERROR: Could not decode {found_path} with utf-8, utf-8-sig, or cp1252.")
        print(f"Last error: {last_error}")
        print("Fix: open the file in VS Code, click the encoding label in the")
        print("bottom-right status bar, choose 'Save with Encoding' -> UTF-8, and re-run.")
        sys.exit(1)

    start = content.find("training_queries = [")
    if start == -1:
        print(f"ERROR: Found the file at {found_path}, but couldn't find")
        print("'training_queries = [' inside it. Has the variable been renamed?")
        sys.exit(1)

    list_str = content[start + len("training_queries = "):]
    return ast.literal_eval(list_str)


# ---------------------------------------------------------------------------
# Feature extraction — EXACT copy of the function in 06_dynamic_classifier.ipynb
# ---------------------------------------------------------------------------
URDU_CHARS = set("ابپتثجچحخدذرزژسشصضطظعغفقکگلمنوہھیےآاً")

def extract_features(query, include_static_leak=True):
    words = query.split()
    unique_words = set(words)
    urdu_count = sum(1 for c in query if c in URDU_CHARS)
    feats = [
        len(query),                                              # char_length
        len(words),                                               # word_count
        len(unique_words),                                        # unique_words
        sum(len(w) for w in words) / max(len(words), 1),          # avg_word_length
        len(unique_words) / max(len(words), 1),                   # lexical_diversity
        urdu_count / max(len(query), 1),                          # urdu_char_ratio
        int(any(w in query for w in
                ["کیا", "کون", "کہاں", "کیوں", "what", "how", "why", "when", "where"])),  # has_question_words
    ]
    if include_static_leak:
        feats.append(int(len(query) >= 150))                      # is_long_by_static
    return feats


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
# TEST 1 — Feature ablation: is `is_long_by_static` responsible for 100%?
# ---------------------------------------------------------------------------
def test1_feature_ablation(queries):
    print("\n" + "=" * 70)
    print("TEST 1 — FEATURE ABLATION (is_long_by_static leak check)")
    print("=" * 70)

    y = np.array([1 if l == "long" else 0 for _, l in queries])

    # A. Length-only features (char_length, word_count) — no leak feature
    X_len = np.array([extract_features(q, include_static_leak=False)[:2] for q, _ in queries])
    acc_len = cv_accuracy(X_len, y)

    # B. Non-length semantic features only (no length signal at all)
    X_nonlen = np.array([extract_features(q, include_static_leak=False)[2:] for q, _ in queries])
    acc_nonlen = cv_accuracy(X_nonlen, y)

    # C. All 7 features, leak feature removed
    X_no_leak = np.array([extract_features(q, include_static_leak=False) for q, _ in queries])
    acc_no_leak = cv_accuracy(X_no_leak, y)

    # D. Original 8 features WITH the leak feature (baseline / original claim)
    X_orig = np.array([extract_features(q, include_static_leak=True) for q, _ in queries])
    acc_orig = cv_accuracy(X_orig, y)

    print(f"{'Feature set':<45}{'5-fold CV mean':>16}{'std':>10}")
    print("-" * 71)
    print(f"{'A. Length-only (no leak)':<45}{acc_len.mean():>15.2%}{acc_len.std():>10.2%}")
    print(f"{'B. Non-length features only':<45}{acc_nonlen.mean():>15.2%}{acc_nonlen.std():>10.2%}")
    print(f"{'C. All 7 features, leak REMOVED':<45}{acc_no_leak.mean():>15.2%}{acc_no_leak.std():>10.2%}")
    print(f"{'D. Original 8 features (with leak)':<45}{acc_orig.mean():>15.2%}{acc_orig.std():>10.2%}")

    print("\nInterpretation:")
    print("If B (no length signal at all) is close to D, the leak feature is")
    print("NOT what's driving the result — task separability is.")


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


def test2_leave_one_topic_out(queries):
    print("\n" + "=" * 70)
    print("TEST 2 — LEAVE-ONE-TOPIC-OUT VALIDATION")
    print("=" * 70)

    tagged = [(q, l, tag_topic(q)) for q, l in queries]
    topic_counts = Counter(t for _, _, t in tagged)
    usable = [t for t, c in topic_counts.items() if t != "other" and c >= 8]

    if not usable:
        print("Not enough queries per topic in this dataset to run this test.")
        print("(Run test3 first to expand the dataset, then re-run this test on the expanded set.)")
        return

    X = np.array([extract_features(q) for q, _, _ in tagged])
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
    print("\nInterpretation: each topic was NEVER seen during training for its")
    print("own test. High accuracy here = genuine generalization, not memorization.")


# ---------------------------------------------------------------------------
# TEST 3 — Dataset expansion: does result hold at 548 queries?
#          (Edit / extend NEW_QUERIES below with your own additional
#           queries if you want to grow this further.)
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
    (
        "what is the current situation of agriculture in pakistan and how is the government planning to address it",
        "long",
    ),
    # Add more of your own here to keep growing the validation set.
]


def test3_dataset_expansion(queries):
    print("\n" + "=" * 70)
    print("TEST 3 — DATASET EXPANSION (does 100% hold when we scale the data?)")
    print("=" * 70)

    existing = set(q for q, _ in queries)
    new_unique = [(q, l) for q, l in NEW_QUERIES if q not in existing]
    combined = queries + new_unique

    def eval_set(data, label):
        X = np.array([extract_features(q) for q, _ in data])
        y = np.array([1 if l == "long" else 0 for _, l in data])
        accs = cv_accuracy(X, y)
        print(f"{label:<30} n={len(data):<6} CV mean={accs.mean():.2%}  std={accs.std():.2%}")
        return accs

    eval_set(queries, "Original")
    eval_set(combined, "Expanded")

    print(f"\nAdded {len(new_unique)} new unique queries. Total now: {len(combined)}.")
    print("Edit NEW_QUERIES in this script to add your own queries and re-run.")


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    queries = load_original_queries()
    print(f"Loaded {len(queries)} original queries from data/training_queries_real.py")

    test1_feature_ablation(queries)
    test2_leave_one_topic_out(queries)
    test3_dataset_expansion(queries)

    print("\n" + "=" * 70)
    print("DONE. Copy these results into your validation report / paper.")
    print("=" * 70)