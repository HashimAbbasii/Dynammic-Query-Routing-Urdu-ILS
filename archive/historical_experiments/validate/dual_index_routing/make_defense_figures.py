# -*- coding: utf-8 -*-
"""Frozen-number figures for defense and thesis. Does not retrain."""
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

OUT = Path(__file__).resolve().parent / "figures"
OUT.mkdir(exist_ok=True)
plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})


def save(fig, name):
    p = OUT / name
    fig.savefig(p, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print("wrote", p)


def fig_layers():
    labels = ["Dev/CV", "Frozen 3B V2", "Frozen traps"]
    x = np.arange(3)
    w = 0.25
    fig, ax = plt.subplots(figsize=(8.0, 4.3))
    ax.bar(x - w, [100, 86, 60], w, label="SVM", color="#1f4e79")
    ax.bar(x, [0, 84, 20], w, label="Word count >= 6", color="#7a7a7a")
    ax.bar(x + w, [50, 0, 50], w, label="theta = 150", color="#c4a35a")
    ax.set_xticks(x)
    ax.set_xticklabels(["Dev/CV\n(learnability)", "Frozen Phase 3B\nV2 n=50", "Frozen traps\nn=40"])
    ax.set_ylabel("Routing accuracy (%)")
    ax.set_title("Do not mix these three tables")
    ax.set_ylim(0, 112)
    ax.legend(frameon=False)
    save(fig, "fig_three_evaluation_layers.png")


def fig_cues():
    x = np.arange(2)
    w = 0.32
    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    ax.bar(x - w / 2, [100, 27.27], w, label="SVM 12-feature", color="#1f4e79")
    ax.bar(x + w / 2, [11.11, 27.27], w, label="Word count >= 6", color="#7a7a7a")
    ax.set_xticks(x)
    ax.set_xticklabels(["Cue words fire\n(n = 18)", "No cue words\n(n = 22)"])
    ax.set_ylabel("Accuracy (%)")
    ax.set_title("Held-out traps: gain is cue words, not generic need")
    ax.set_ylim(0, 115)
    ax.legend(frameon=False)
    save(fig, "fig_cue_split.png")


def fig_p5():
    x = np.arange(4)
    w = 0.35
    fig, ax = plt.subplots(figsize=(8.2, 4.3))
    ax.bar(x - w / 2, [36.50, 35.00, 34.25, 33.00], w, label="Graded P@5 (%)", color="#1f4e79")
    ax.bar(x + w / 2, [64.76, 68.68, 60.20, 61.49], w, label="nDCG@5 x 100", color="#5b8fa8")
    ax.set_xticks(x)
    ax.set_xticklabels(["Word count", "Always headline\n/ theta=150", "Always full", "SVM"])
    ax.set_title("Held-out dual-index retrieval (n=40, 400 judgments)")
    ax.set_ylim(0, 85)
    ax.legend(frameon=False)
    save(fig, "fig_heldout_p5.png")


def fig_rooms():
    fig, ax = plt.subplots(figsize=(9.0, 3.3))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)
    ax.axis("off")
    ax.set_title("What theta=150 is replaced with", loc="left")
    boxes = [
        (0.2, 1.3, "Query + Roman dict", "#e8e8e8"),
        (2.6, 1.3, "SVM SHORT/LONG", "#1f4e79"),
        (5.0, 2.35, "Headline room", "#2e7d4f"),
        (5.0, 0.35, "Full-article room", "#8a3b12"),
        (7.6, 2.35, "HIGH: one room", "#2e7d4f"),
        (7.6, 1.3, "MED: mix both", "#c4a35a"),
        (7.6, 0.25, "LOW: expand+mix", "#a33b3b"),
    ]
    for x, y, t, c in boxes:
        ax.add_patch(plt.Rectangle((x, y), 2.1, 0.95, facecolor=c, edgecolor="#222", lw=0.8))
        col = "#111" if c in ("#e8e8e8", "#c4a35a") else "white"
        ax.text(x + 1.05, y + 0.48, t, ha="center", va="center", fontsize=8, color=col)
    save(fig, "fig_two_rooms_lights.png")


if __name__ == "__main__":
    fig_layers()
    fig_cues()
    fig_p5()
    fig_rooms()
