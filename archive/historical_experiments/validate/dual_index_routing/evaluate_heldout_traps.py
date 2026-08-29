# -*- coding: utf-8 -*-
"""
Score the FROZEN held-out 40 traps. Never trains. Never writes model pickles.

Writes:
  labels/heldout_trap_sheet.csv          (student labels blank)
  labels/heldout_classification.json
  labels/heldout_classification.txt
"""
from __future__ import annotations

import ast
import csv
import json
import os
import sys
from collections import defaultdict

_DIR = os.path.dirname(os.path.abspath(__file__))
LABELS = os.path.join(_DIR, "labels")
sys.path.insert(0, _DIR)
sys.path.insert(0, LABELS)
sys.path.insert(0, os.path.join(os.path.dirname(_DIR), "phase3"))

from extractor_v3 import intent_flags  # noqa: E402
from heldout_traps import HELDOUT_TRAPS  # noqa: E402
from phase3a_extractor import load_training_queries  # noqa: E402
from router import decide  # noqa: E402

REPO_ROOT = os.path.abspath(os.path.join(_DIR, "..", ".."))
STUDENT_CSV = os.path.join(LABELS, "heldout_trap_sheet.csv")
OUT_JSON = os.path.join(LABELS, "heldout_classification.json")
OUT_TXT = os.path.join(LABELS, "heldout_classification.txt")
FROZEN_NOTE = os.path.join(LABELS, "HELD_OUT_FROZEN.txt")

TRAP_CONSTRAINTS = {
    "SHORT_WORDS_LONG_NEED": lambda n: n <= 5,
    "LONG_WORDS_SHORT_NEED": lambda n: 6 <= n <= 9,
    "CONTROL_EASY_SHORT": lambda n: n <= 3,
    "CONTROL_EASY_LONG": lambda n: n >= 12,
}


def _norm(q: str) -> str:
    return " ".join(q.strip().lower().split())


def load_blocked_queries():
    blocked = {}

    def add(q, src):
        k = _norm(q)
        if k:
            blocked.setdefault(k, src)

    for q, _ in load_training_queries():
        add(q, "training_409")
    trap_path = os.path.join(LABELS, "trap_label_sheet.csv")
    with open(trap_path, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            add(r["query"], "train_traps_T001_T040")
    p3 = os.path.join(REPO_ROOT, "validate", "phase3", "phase3_evaluation_set.csv")
    with open(p3, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            add(r["query"], "phase3b")
    p25 = os.path.join(REPO_ROOT, "validate", "phase2_5", "pilot_queries.json")
    with open(p25, encoding="utf-8") as f:
        data = json.load(f)
    for row in data["queries"]:
        add(row["query"], "phase2_5")
    # notebooks 14 holdout / other python lists if present
    tq = os.path.join(REPO_ROOT, "data", "training_queries_real.py")
    with open(tq, encoding="utf-8") as f:
        content = f.read()
    start = content.find("training_queries = [")
    queries = ast.literal_eval(content[start + len("training_queries = ") :])
    for q, _ in queries:
        add(q, "training_409")
    return blocked


def mcnemar(gold, a, b):
    """Return n01 (a wrong b right), n10 (a right b wrong) for McNemar."""
    n01 = n10 = 0
    for g, pa, pb in zip(gold, a, b):
        a_ok, b_ok = pa == g, pb == g
        if (not a_ok) and b_ok:
            n01 += 1
        elif a_ok and (not b_ok):
            n10 += 1
    n = n01 + n10
    if n == 0:
        p = 1.0
    else:
        from math import comb

        b = min(n01, n10)
        tail = sum(comb(n, k) for k in range(0, b + 1))
        p = tail / (2 ** n)
        if b * 2 != n:
            p = min(1.0, 2.0 * p)
        else:
            p = 1.0
    return {"n01_svm_wrong_wc_right": n01, "n10_svm_right_wc_wrong": n10, "n_discordant": n, "p_exact": p}


def main():
    blocked = load_blocked_queries()
    leaks = []
    rows = []
    for qid, trap_type, script, category, query, gold in HELDOUT_TRAPS:
        n = len(query.split())
        if not TRAP_CONSTRAINTS[trap_type](n):
            raise ValueError(f"{qid}: word_count={n} violates {trap_type}")
        src = blocked.get(_norm(query))
        if src:
            leaks.append((qid, query, src))
        cues = intent_flags(query)
        cue_hit = int(any(cues))
        d_svm = decide(query, "svm_v2")
        d_wc = decide(query, "wordcount")
        d_th = decide(query, "theta150")
        gold_u = gold.upper()
        rows.append(
            {
                "query_id": qid,
                "query": query,
                "script": script,
                "word_count": n,
                "trap_type": trap_type,
                "category": category,
                "gold_label": gold_u,
                "cue_has_causal": cues[0],
                "cue_has_manner": cues[1],
                "cue_has_synthesis": cues[2],
                "cue_has_fact": cues[3],
                "v3_cue_hit": cue_hit,
                "svm": d_svm["label"],
                "svm_conf": d_svm["confidence"],
                "svm_tier": d_svm["tier"],
                "wordcount": d_wc["label"],
                "theta150": d_th["label"],
                "svm_ok": int(d_svm["label"] == gold_u),
                "wordcount_ok": int(d_wc["label"] == gold_u),
                "theta150_ok": int(d_th["label"] == gold_u),
            }
        )

    if leaks:
        raise SystemExit("LEAKAGE: " + "; ".join(f"{a} in {c}" for a, _, c in leaks))

    def acc(key):
        return sum(r[key] for r in rows) / len(rows)

    gold = [r["gold_label"] for r in rows]
    svm = [r["svm"] for r in rows]
    wc = [r["wordcount"] for r in rows]
    th = [r["theta150"] for r in rows]

    by_type = defaultdict(lambda: {"n": 0, "svm": 0, "wordcount": 0, "theta150": 0})
    by_cue = defaultdict(lambda: {"n": 0, "svm": 0, "wordcount": 0})
    for r in rows:
        by_type[r["trap_type"]]["n"] += 1
        by_type[r["trap_type"]]["svm"] += r["svm_ok"]
        by_type[r["trap_type"]]["wordcount"] += r["wordcount_ok"]
        by_type[r["trap_type"]]["theta150"] += r["theta150_ok"]
        tag = "v3_cue" if r["v3_cue_hit"] else "no_v3_cue"
        by_cue[tag]["n"] += 1
        by_cue[tag]["svm"] += r["svm_ok"]
        by_cue[tag]["wordcount"] += r["wordcount_ok"]

    def pct(d, k):
        return d[k] / d["n"] if d["n"] else None

    type_tbl = {
        t: {
            "n": d["n"],
            "svm": pct(d, "svm"),
            "wordcount": pct(d, "wordcount"),
            "theta150": pct(d, "theta150"),
        }
        for t, d in by_type.items()
    }
    cue_tbl = {
        t: {"n": d["n"], "svm": pct(d, "svm"), "wordcount": pct(d, "wordcount")}
        for t, d in by_cue.items()
    }

    misses = [r for r in rows if not r["svm_ok"]]
    report = {
        "frozen": True,
        "n": len(rows),
        "do_not_train": True,
        "label_source": "designer protocol in heldout_traps.py; student labels not used yet",
        "accuracy": {
            "svm": acc("svm_ok"),
            "wordcount": acc("wordcount_ok"),
            "theta150": acc("theta150_ok"),
        },
        "mcnemar_svm_vs_wordcount": mcnemar(gold, svm, wc),
        "mcnemar_svm_vs_theta150": mcnemar(gold, svm, th),
        "by_trap_type": type_tbl,
        "by_v3_cue": cue_tbl,
        "svm_misses": [
            {
                "query_id": r["query_id"],
                "query": r["query"],
                "gold": r["gold_label"],
                "svm": r["svm"],
                "wordcount": r["wordcount"],
                "v3_cue_hit": r["v3_cue_hit"],
            }
            for r in misses
        ],
        "per_query": rows,
    }

    os.makedirs(LABELS, exist_ok=True)
    with open(STUDENT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "query_id",
                "query",
                "script",
                "word_count",
                "trap_type",
                "category",
                "gold_label_student",
                "notes",
            ],
        )
        w.writeheader()
        for r in rows:
            w.writerow(
                {
                    "query_id": r["query_id"],
                    "query": r["query"],
                    "script": r["script"],
                    "word_count": r["word_count"],
                    "trap_type": r["trap_type"],
                    "category": r["category"],
                    "gold_label_student": "",
                    "notes": "",
                }
            )

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    lines = []
    lines.append("FROZEN HELD-OUT TRAP CLASSIFICATION (do not train on these 40)")
    lines.append(f"n = {len(rows)}")
    lines.append("Labels = designer protocol (headline-enough rule). Confirm before IEEE.")
    lines.append("")
    lines.append(f"  SVM        {report['accuracy']['svm']:.2%}")
    lines.append(f"  word-count {report['accuracy']['wordcount']:.2%}")
    lines.append(f"  theta=150  {report['accuracy']['theta150']:.2%}")
    m = report["mcnemar_svm_vs_wordcount"]
    lines.append(
        f"  McNemar SVM vs word-count: SVM-only-right={m['n10_svm_right_wc_wrong']} "
        f"WC-only-right={m['n01_svm_wrong_wc_right']} p_exact={m['p_exact']:.4f}"
    )
    lines.append("")
    lines.append("By trap type")
    for t, d in type_tbl.items():
        lines.append(
            f"  {t:24} n={d['n']:2d}  SVM={d['svm']:.2%}  WC={d['wordcount']:.2%}  θ={d['theta150']:.2%}"
        )
    lines.append("")
    lines.append("By V3 keyword cue (honest split: did has_causal/manner/synthesis/fact fire?)")
    for t, d in cue_tbl.items():
        lines.append(f"  {t:12} n={d['n']:2d}  SVM={d['svm']:.2%}  WC={d['wordcount']:.2%}")
    lines.append("")
    lines.append("SVM misses")
    if not misses:
        lines.append("  (none)")
    for r in misses:
        lines.append(f"  {r['query_id']} gold={r['gold_label']} svm={r['svm']} wc={r['wordcount']}  {r['query']}")
    text = "\n".join(lines) + "\n"
    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write(text)
    with open(FROZEN_NOTE, "w", encoding="utf-8") as f:
        f.write(
            "FROZEN held-out set: validate/dual_index_routing/labels/heldout_traps.py\n"
            "H001-H040. Do not add to SVM training. Do not overwrite this file to chase accuracy.\n"
            "Student labels go in heldout_trap_sheet.csv (gold_label_student only).\n"
            "Draft scores use protocol labels in heldout_traps.py.\n"
        )
    print(text)
    print("Wrote", STUDENT_CSV)
    print("Wrote", OUT_JSON)
    print("Wrote", OUT_TXT)


if __name__ == "__main__":
    main()
