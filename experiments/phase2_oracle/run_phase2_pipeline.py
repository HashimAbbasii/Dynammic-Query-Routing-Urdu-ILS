# -*- coding: utf-8 -*-
"""
Phase 2: new train/dev pool + known-item retrieval-oracle labels.

Does NOT:
  - train or reload-write the SVM
  - read H001-H040 relevance judgments as training labels
  - change frozen test files

Oracle definition (pre-registered, not tuned on H001-H040):
  Known-item: the article the query was written from is the single relevant doc.
  Primary score = nDCG@5 on that binary label.
  MIXED if abs(nDCG_headline - nDCG_full) < 0.05 or both are zero.
"""
from __future__ import annotations

import csv
import json
import math
import os
import random
import sys
from collections import Counter, defaultdict

import numpy as np
import pandas as pd

_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(_DIR, "..", ".."))
sys.path.insert(0, _DIR)
sys.path.insert(0, os.path.join(ROOT, "validate", "dual_index_routing"))

from frozen_guard import (  # noqa: E402
    FROZEN_TEST_IDS,
    assert_pool_isolated,
    blocked_norm_set,
    collision_report,
    frozen_rows,
)
from retrieve import search_full_content, search_headlines, transliterate_roman  # noqa: E402
from textnorm import normalize_query  # noqa: E402

SEED = 42
N_TARGET = 260
TOP_K_SEARCH = 20
CUTOFF = 5
MIXED_DELTA = 0.05  # pre-registered nDCG@5 gap
CORPUS = os.path.join(ROOT, "data", "clean_articles.csv")
DICT_PATH = os.path.join(ROOT, "models", "roman_urdu_dict_expanded.json")
OUT = _DIR

WHY = "کیوں ہوا"
HOW = "کیسے ہوا"
EFFECT = "کے اثرات کیا ہیں"


def ndcg_at_k(binary_hits, k=CUTOFF):
    rel = list(binary_hits[:k]) + [0] * (k - len(binary_hits[:k]))
    dcg = sum((2 ** r - 1) / math.log2(i + 2) for i, r in enumerate(rel))
    ideal = 1.0  # one relevant document
    return dcg / ideal


def p_at_k(binary_hits, k=CUTOFF):
    rel = list(binary_hits[:k])
    if len(rel) < k:
        rel = rel + [0] * (k - len(rel))
    return sum(rel) / k


def load_reverse_roman():
    with open(DICT_PATH, encoding="utf-8") as f:
        fwd = json.load(f)
    rev = {}
    for lat, ur in fwd.items():
        rev.setdefault(ur, lat)
    return rev


_CHAR_ROMAN = {
    "ا": "a", "آ": "aa", "ب": "b", "پ": "p", "ت": "t", "ٹ": "t", "ث": "s",
    "ج": "j", "چ": "ch", "ح": "h", "خ": "kh", "د": "d", "ڈ": "d", "ذ": "z",
    "ر": "r", "ڑ": "r", "ز": "z", "ژ": "zh", "س": "s", "ش": "sh", "ص": "s",
    "ض": "z", "ط": "t", "ظ": "z", "ع": "a", "غ": "gh", "ف": "f", "ق": "q",
    "ک": "k", "گ": "g", "ل": "l", "م": "m", "ن": "n", "ں": "n", "و": "o",
    "ہ": "h", "ھ": "h", "ء": "", "ی": "i", "ے": "e", "ئ": "i", "ؤ": "o",
    "أ": "a", "إ": "i", "ة": "h",
}


def naive_roman_word(word: str) -> str:
    buf = []
    for ch in word:
        if ch in _CHAR_ROMAN:
            buf.append(_CHAR_ROMAN[ch])
        elif ch.isascii() and ch.isalnum():
            buf.append(ch)
    return "".join(buf)


def romanize(title: str, rev: dict) -> str | None:
    toks = title.split()[:12]
    out = []
    for t in toks:
        key = t.strip("،۔!?؟,.")
        lat = rev.get(key)
        if not lat:
            if any("a" <= c.lower() <= "z" for c in key):
                lat = key
            else:
                lat = naive_roman_word(key)
        if lat:
            out.append(lat)
    if len(out) < 2:
        return None
    return " ".join(out)


def clip_words(text: str, n: int) -> str:
    w = str(text).split()
    return " ".join(w[:n]).strip()


def protocol_from_template(template: str) -> str:
    if template in ("title_short", "title_roman", "mixed_short"):
        return "SHORT"
    return "LONG"


def query_category(template: str) -> str:
    return {
        "title_short": "short",
        "title_roman": "short",
        "mixed_short": "ambiguous",
        "why": "contextual",
        "how": "contextual",
        "lead": "detailed",
        "effects": "contextual",
    }[template]


def language_type(template: str) -> str:
    if template == "title_roman":
        return "roman_urdu"
    if template == "mixed_short":
        return "mixed"
    return "urdu"


def build_pool(df: pd.DataFrame, rev: dict, n_target: int = N_TARGET) -> list[dict]:
    rng = random.Random(SEED)
    frozen = frozen_rows()
    blocked = blocked_norm_set()
    usable = []
    for i, row in df.iterrows():
        title = str(row.get("Headline") or "").strip()
        body = str(row.get("News Text") or "").strip()
        if len(title) < 14 or len(title) > 96:
            continue
        if len(body) < 280:
            continue
        if len(title.split()) < 3:
            continue
        usable.append(int(i))
    rng.shuffle(usable)

    rows = []
    used_docs = set()
    templates_cycle = [
        "title_short",
        "title_roman",
        "why",
        "title_roman",
        "lead",
        "how",
        "title_roman",
        "effects",
        "mixed_short",
    ]
    t_i = 0
    for doc_id in usable:
        if len(rows) >= n_target:
            break
        if doc_id in used_docs:
            continue
        row = df.iloc[doc_id]
        title = str(row["Headline"]).strip()
        body = str(row["News Text"]).strip()
        cat = str(row.get("Category") or "")
        template = templates_cycle[t_i % len(templates_cycle)]
        t_i += 1
        if template == "title_short":
            q = clip_words(title, 8)
        elif template == "title_roman":
            q = romanize(title, rev)
            if not q:
                q = clip_words(title, 8)
                template = "title_short"
        elif template == "why":
            q = clip_words(title, 10) + " " + WHY
        elif template == "how":
            q = clip_words(title, 10) + " " + HOW
        elif template == "effects":
            q = clip_words(title, 8) + " " + EFFECT
        elif template == "lead":
            q = clip_words(body, 14)
        else:
            q = clip_words(title, 4) + " Pakistan news update"
        q = " ".join(q.split())
        if len(q.split()) < 2:
            continue
        qid = f"QTRN_{len(rows)+1:03d}"
        hit = collision_report(qid, q, blocked, frozen)
        if hit:
            continue
        rec = {
            "query_id": qid,
            "query_text": q,
            "language_type": language_type(template),
            "query_category": query_category(template),
            "source": "corpus_derived",
            "creation_method": template,
            "source_doc_id": int(doc_id),
            "source_headline": title[:180],
            "article_category": cat,
            "protocol_label": protocol_from_template(template),
            "char_len": len(q),
            "word_count": len(q.split()),
        }
        rows.append(rec)
        used_docs.add(doc_id)
        blocked.add(normalize_query(q))
    return rows


def rank_source(hits, source_id):
    for rank, (doc_id, _s) in enumerate(hits, 1):
        if int(doc_id) == int(source_id):
            return rank
    return None


def metrics_from_hits(hits, source_id, k=CUTOFF):
    top = [int(d) for d, _ in hits[:k]]
    binary = [1 if d == int(source_id) else 0 for d in top]
    rank = rank_source(hits, source_id)
    return {
        "p5": p_at_k(binary, k),
        "ndcg5": ndcg_at_k(binary, k),
        "hit5": int(any(binary)),
        "rank": rank if rank is not None else 999,
        "rr": (1.0 / rank) if rank is not None else 0.0,
        "top5_ids": top,
    }


def oracle_route(h_ndcg, f_ndcg, delta=MIXED_DELTA):
    if h_ndcg == 0.0 and f_ndcg == 0.0:
        return "MIXED", 0.0
    if abs(h_ndcg - f_ndcg) < delta:
        return "MIXED", abs(h_ndcg - f_ndcg)
    if h_ndcg > f_ndcg:
        return "HEADLINE", h_ndcg - f_ndcg
    return "FULL", f_ndcg - h_ndcg


def wordcount_route(n_words):
    return "FULL" if n_words >= 6 else "HEADLINE"


def protocol_route(label):
    return "FULL" if str(label).upper() == "LONG" else "HEADLINE"


def stratified_split(rows, seed=SEED):
    rng = random.Random(seed)
    buckets = defaultdict(list)
    for r in rows:
        buckets[r["oracle_route"]].append(r)
    train, dev, ival = [], [], []
    for _k, items in buckets.items():
        rng.shuffle(items)
        n = len(items)
        n_train = int(round(n * 0.70))
        n_dev = int(round(n * 0.15))
        train.extend(items[:n_train])
        dev.extend(items[n_train : n_train + n_dev])
        ival.extend(items[n_train + n_dev :])
    rng.shuffle(train)
    rng.shuffle(dev)
    rng.shuffle(ival)
    return train, dev, ival


def write_csv(path, rows, fields):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def confusion(a_key, b_key, rows, labels):
    m = {la: {lb: 0 for lb in labels} for la in labels}
    for r in rows:
        m[r[a_key]][r[b_key]] += 1
    return m


def main():
    random.seed(SEED)
    np.random.seed(SEED)
    os.makedirs(os.path.join(OUT, "figures"), exist_ok=True)

    print("Loading corpus...")
    df = pd.read_csv(CORPUS, encoding="utf-8-sig")
    rev = load_reverse_roman()
    pool = build_pool(df, rev, N_TARGET)
    isolation = assert_pool_isolated(pool)
    print(f"Pool size {len(pool)} isolated={isolation['ok']}")

    print("Running dual-index known-item retrieval (new queries only)...")
    labelled = []
    for i, rec in enumerate(pool, 1):
        q = rec["query_text"]
        processed, _ = transliterate_roman(q)
        src = rec["source_doc_id"]
        h_hits = search_headlines(processed, top_k=TOP_K_SEARCH)
        f_hits = search_full_content(processed, top_k=TOP_K_SEARCH)
        hm = metrics_from_hits(h_hits, src)
        fm = metrics_from_hits(f_hits, src)
        route, margin = oracle_route(hm["ndcg5"], fm["ndcg5"])
        rec = dict(rec)
        rec.update(
            {
                "headline_p5": round(hm["p5"], 4),
                "headline_ndcg5": round(hm["ndcg5"], 4),
                "headline_hit5": hm["hit5"],
                "headline_rank": hm["rank"],
                "full_p5": round(fm["p5"], 4),
                "full_ndcg5": round(fm["ndcg5"], 4),
                "full_hit5": fm["hit5"],
                "full_rank": fm["rank"],
                "oracle_route": route,
                "oracle_margin": round(margin, 4),
                "oracle_primary_metric": "ndcg@5_known_item",
                "wordcount_route": wordcount_route(rec["word_count"]),
                "protocol_route": protocol_route(rec["protocol_label"]),
                "processed_query": processed,
            }
        )
        labelled.append(rec)
        if i % 20 == 0:
            print(f"  {i}/{len(pool)}")

    isolation2 = assert_pool_isolated(labelled)
    train, dev, ival = stratified_split(labelled)
    for r in labelled:
        if r["query_id"] in {x["query_id"] for x in train}:
            r["split"] = "train"
        elif r["query_id"] in {x["query_id"] for x in dev}:
            r["split"] = "dev"
        else:
            r["split"] = "internal_val"

    train_ids, dev_ids, ival_ids = (
        {r["query_id"] for r in train},
        {r["query_id"] for r in dev},
        {r["query_id"] for r in ival},
    )
    assert not (train_ids & set(FROZEN_TEST_IDS))
    assert not (dev_ids & set(FROZEN_TEST_IDS))
    assert not (ival_ids & set(FROZEN_TEST_IDS))
    assert train_ids.isdisjoint(dev_ids)
    assert train_ids.isdisjoint(ival_ids)
    assert dev_ids.isdisjoint(ival_ids)
    assert len(train) + len(dev) + len(ival) == len(labelled)

    fields = [
        "query_id",
        "split",
        "query_text",
        "language_type",
        "query_category",
        "source",
        "creation_method",
        "source_doc_id",
        "article_category",
        "word_count",
        "char_len",
        "protocol_label",
        "protocol_route",
        "wordcount_route",
        "headline_p5",
        "headline_ndcg5",
        "headline_hit5",
        "headline_rank",
        "full_p5",
        "full_ndcg5",
        "full_hit5",
        "full_rank",
        "oracle_route",
        "oracle_margin",
        "oracle_primary_metric",
    ]
    write_csv(os.path.join(OUT, "oracle_all.csv"), labelled, fields)
    write_csv(os.path.join(OUT, "oracle_train.csv"), train, fields)
    write_csv(os.path.join(OUT, "oracle_dev.csv"), dev, fields)
    write_csv(os.path.join(OUT, "oracle_internal_val.csv"), ival, fields)

    routes = ["HEADLINE", "FULL", "MIXED"]
    n = len(labelled)
    counts = Counter(r["oracle_route"] for r in labelled)
    proto_agree = sum(r["protocol_route"] == r["oracle_route"] for r in labelled if r["oracle_route"] != "MIXED")
    proto_comp = sum(r["oracle_route"] != "MIXED" for r in labelled)
    wc_agree = sum(r["wordcount_route"] == r["oracle_route"] for r in labelled if r["oracle_route"] != "MIXED")
    margins = [r["oracle_margin"] for r in labelled]
    by_lang = defaultdict(lambda: Counter())
    by_cat = defaultdict(lambda: Counter())
    by_len = defaultdict(lambda: Counter())
    for r in labelled:
        by_lang[r["language_type"]][r["oracle_route"]] += 1
        by_cat[r["query_category"]][r["oracle_route"]] += 1
        bucket = "1-5" if r["word_count"] <= 5 else ("6-12" if r["word_count"] <= 12 else "13+")
        by_len[bucket][r["oracle_route"]] += 1

    # length vs oracle on TRAIN only (no frozen test, no peeking at internal_val for this descriptive table is OK for Phase 2 report on all? User asked relationship. Report on TRAIN to be clean.)
    train_len = defaultdict(lambda: Counter())
    for r in train:
        bucket = "1-5" if r["word_count"] <= 5 else ("6-12" if r["word_count"] <= 12 else "13+")
        train_len[bucket][r["oracle_route"]] += 1

    both_miss = sum(1 for r in labelled if r["headline_hit5"] == 0 and r["full_hit5"] == 0)
    h_only = sum(1 for r in labelled if r["headline_hit5"] == 1 and r["full_hit5"] == 0)
    f_only = sum(1 for r in labelled if r["headline_hit5"] == 0 and r["full_hit5"] == 1)

    summary = {
        "experiment_id": "phase2-known-item-oracle-v1",
        "seed": SEED,
        "n_new_queries": n,
        "n_train": len(train),
        "n_dev": len(dev),
        "n_internal_val": len(ival),
        "n_frozen_test": 40,
        "frozen_test_ids": list(FROZEN_TEST_IDS),
        "mixed_delta_ndcg5": MIXED_DELTA,
        "mixed_delta_selected_on": "pre_registered_not_tuned",
        "oracle_counts": dict(counts),
        "oracle_pct": {k: round(100 * counts[k] / n, 2) for k in routes},
        "mean_oracle_margin": round(float(np.mean(margins)), 4),
        "median_oracle_margin": round(float(np.median(margins)), 4),
        "mean_headline_ndcg5": round(float(np.mean([r["headline_ndcg5"] for r in labelled])), 4),
        "mean_full_ndcg5": round(float(np.mean([r["full_ndcg5"] for r in labelled])), 4),
        "mean_headline_p5": round(float(np.mean([r["headline_p5"] for r in labelled])), 4),
        "mean_full_p5": round(float(np.mean([r["full_p5"] for r in labelled])), 4),
        "known_item_hit5": {
            "headline": int(sum(r["headline_hit5"] for r in labelled)),
            "full": int(sum(r["full_hit5"] for r in labelled)),
            "headline_only": h_only,
            "full_only": f_only,
            "both_miss_top5": both_miss,
        },
        "protocol_vs_oracle_nonmixed": {
            "n_comparable": proto_comp,
            "agree": proto_agree,
            "disagree": proto_comp - proto_agree,
            "agreement_pct": round(100 * proto_agree / proto_comp, 2) if proto_comp else None,
        },
        "wordcount_vs_oracle_nonmixed": {
            "n_comparable": proto_comp,
            "agree": wc_agree,
            "disagree": proto_comp - wc_agree,
            "agreement_pct": round(100 * wc_agree / proto_comp, 2) if proto_comp else None,
        },
        "confusion_protocol_vs_oracle": confusion("protocol_route", "oracle_route", labelled, routes),
        "confusion_wordcount_vs_oracle": confusion("wordcount_route", "oracle_route", labelled, routes),
        "by_language": {k: dict(v) for k, v in by_lang.items()},
        "by_query_category": {k: dict(v) for k, v in by_cat.items()},
        "by_length_all": {k: dict(v) for k, v in by_len.items()},
        "by_length_train_only": {k: dict(v) for k, v in train_len.items()},
        "language_n": dict(Counter(r["language_type"] for r in labelled)),
        "category_n": dict(Counter(r["query_category"] for r in labelled)),
        "limitations": [
            "Labels are known-item (source article), not human graded P@5 over all retrieved news.",
            "Known-item P@5 is 0 or 0.2 because only one document is treated as relevant.",
            "Queries are derived from corpus titles/leads, not independent user logs.",
            "Protocol labels are template-based (creation_method), not a new human annotation pass.",
        ],
    }
    with open(os.path.join(OUT, "oracle_statistics.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    leak = {
        "frozen_test_untouched": True,
        "isolation": isolation2,
        "train_dev_internal_disjoint": True,
        "assert_no_frozen_ids_in_pool": True,
        "svm_retrained": False,
        "used_heldout_p5_judgments_for_labels": False,
        "mixed_delta_tuned_on_frozen_test": False,
    }
    with open(os.path.join(OUT, "leakage_check.json"), "w", encoding="utf-8") as f:
        json.dump(leak, f, indent=2)

    proto_rows = []
    for r in labelled:
        proto_rows.append(
            {
                "query_id": r["query_id"],
                "split": r["split"],
                "protocol_label": r["protocol_label"],
                "protocol_route": r["protocol_route"],
                "oracle_route": r["oracle_route"],
                "agree": int(r["protocol_route"] == r["oracle_route"]),
                "wordcount_route": r["wordcount_route"],
                "query_category": r["query_category"],
                "language_type": r["language_type"],
            }
        )
    write_csv(
        os.path.join(OUT, "protocol_vs_oracle.csv"),
        proto_rows,
        [
            "query_id",
            "split",
            "protocol_label",
            "protocol_route",
            "oracle_route",
            "agree",
            "wordcount_route",
            "query_category",
            "language_type",
        ],
    )

    try:
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(6, 4))
        xs = routes
        ys = [counts[x] for x in xs]
        ax.bar(xs, ys, color=["#4C78A8", "#F58518", "#54A24B"])
        ax.set_title("Phase 2 known-item oracle routes (new pool only)")
        ax.set_ylabel("Queries")
        fig.tight_layout()
        fig.savefig(os.path.join(OUT, "figures", "oracle_route_counts.png"), dpi=140)
        plt.close()
    except Exception as e:
        print("figure skipped:", e)

    print(json.dumps({k: summary[k] for k in ("n_new_queries", "n_train", "n_dev", "n_internal_val", "oracle_pct")}, indent=2))
    print("Phase 2 retrieval+labels done. SVM not trained.")


if __name__ == "__main__":
    main()
