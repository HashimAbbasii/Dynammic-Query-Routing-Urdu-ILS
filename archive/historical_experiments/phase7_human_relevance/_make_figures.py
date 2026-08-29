# -*- coding: utf-8 -*-
"""Figures for Phase 7 (labels already frozen in CSVs)."""
from __future__ import annotations

import csv
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

_DIR = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(_DIR, "figures")
os.makedirs(FIG, exist_ok=True)


def load_query_flags(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append(r)
    return rows


def main():
    analysis = load_query_flags(os.path.join(_DIR, "RESIDUAL_RELEVANCE_ANALYSIS.csv"))
    dev = [r for r in analysis if r["split"] == "dev"]
    val = [r for r in analysis if r["split"] == "internal_val"]

    def count(rows, key):
        return sum(int(r[key]) for r in rows)

    labels = ["Relevant@5", "Partial@5", "Rel or partial", "Ambiguous query"]
    dev_y = [
        count(dev, "relevant_in_top5"),
        count(dev, "partially_relevant_in_top5"),
        count(dev, "evaluation_mismatch"),
        count(dev, "query_ambiguous"),
    ]
    val_y = [
        count(val, "relevant_in_top5"),
        count(val, "partially_relevant_in_top5"),
        count(val, "evaluation_mismatch"),
        count(val, "query_ambiguous"),
    ]

    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    import numpy as np
    x = np.arange(len(labels))
    ax.bar(x - 0.2, dev_y, 0.4, label="DEV (n=4)", color="#3b6ea5")
    ax.bar(x + 0.2, val_y, 0.4, label="INTERNAL_VAL (n=6)", color="#c47b2b")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("queries")
    ax.set_title("Phase 7 secondary labels (residual misses only)")
    ax.set_ylim(0, 7)
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "dev_vs_val_secondary.png"), dpi=140)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6.2, 4.2))
    labs = ["Exact-source\nHit@5", "Relevant@5", "Rel or\npartial@5"]
    ax.bar(labs, [0, 3, 8], color=["#8b3a3a", "#3b6ea5", "#5b8c5a"])
    ax.set_ylim(0, 10)
    ax.set_ylabel("of 10 residual misses")
    ax.set_title("Official vs secondary (residuals only; not n=78)")
    for i, v in enumerate([0, 3, 8]):
        ax.text(i, v + 0.15, str(v), ha="center")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "official_vs_secondary.png"), dpi=140)
    plt.close(fig)
    print("wrote figures")


if __name__ == "__main__":
    main()
