# -*- coding: utf-8 -*-
"""Draw PLOS figures from frozen official numbers only. No retrieval."""
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

HERE = Path(__file__).resolve().parent
FIG = HERE / "figures"
FIG.mkdir(exist_ok=True)


def fig1_routing() -> None:
    fig, ax = plt.subplots(figsize=(10.2, 4.2))
    ax.set_xlim(0, 10.2)
    ax.set_ylim(0, 4.2)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    def box(x, y, w, h, text, fc="#e8eef6"):
        p = FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
            facecolor=fc, edgecolor="#1f3a5f", linewidth=1.4,
        )
        ax.add_patch(p)
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=9)

    box(0.25, 1.55, 1.7, 1.1, "Query", "#d9e8d3")
    box(2.3, 1.55, 2.35, 1.1, "Unicode detector\nURDU / ROMAN\nMIXED / OTHER", "#fff3cd")
    box(6.55, 2.55, 3.3, 1.15, "Urdu BM25\n(article text)", "#cfe2ff")
    box(6.55, 0.45, 3.3, 1.15, "Method D BM25\n(romanized docs)", "#f8d7da")
    ax.annotate(
        "", xy=(2.25, 2.1), xytext=(1.95, 2.1),
        arrowprops=dict(arrowstyle="->", color="#1f3a5f", lw=1.5),
    )
    ax.annotate(
        "URDU / MIXED / OTHER",
        xy=(6.55, 3.12), xytext=(4.7, 3.12),
        fontsize=8, ha="center", va="center",
        arrowprops=dict(arrowstyle="->", color="#1f3a5f", lw=1.5),
    )
    ax.annotate(
        "ROMAN",
        xy=(6.55, 1.02), xytext=(4.7, 1.02),
        fontsize=8, ha="center", va="center",
        arrowprops=dict(arrowstyle="->", color="#1f3a5f", lw=1.5),
    )
    ax.text(5.1, 0.12, "Official frozen system M0  |  Top-50 retrieve, Top-5 official cutoff", ha="center", fontsize=8, color="#333")
    fig.tight_layout()
    fig.savefig(FIG / "Fig1_m0_routing.png", dpi=200, bbox_inches="tight")
    plt.close()


def fig2_script() -> None:
    labels = ["URDU\n(17/18)", "ROMAN\n(6/18)", "MIXED\n(0/4)"]
    vals = [17 / 18 * 100, 6 / 18 * 100, 0.0]
    colors = ["#4c78a8", "#f58518", "#e45756"]
    fig, ax = plt.subplots(figsize=(6.2, 3.8))
    bars = ax.bar(labels, vals, color=colors, width=0.62, edgecolor="#222", linewidth=0.6)
    ax.set_ylabel("Human Success@5 (%)")
    ax.set_ylim(0, 110)
    ax.set_title("U001–U040 Success@5 by detector label (descriptive)")
    for b, v, n in zip(bars, vals, ["17/18", "6/18", "0/4"]):
        ax.text(b.get_x() + b.get_width() / 2, v + 3, f"{v:.1f}%\n{n}", ha="center", va="bottom", fontsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIG / "Fig2_u_script_split.png", dpi=200, bbox_inches="tight")
    plt.close()


if __name__ == "__main__":
    fig1_routing()
    fig2_script()
    print("wrote Fig1 and Fig2")
