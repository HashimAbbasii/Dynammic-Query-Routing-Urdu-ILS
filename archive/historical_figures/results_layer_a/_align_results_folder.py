# -*- coding: utf-8 -*-
"""Keep results/ aligned with the frozen dual-index story. Archive old 100%-headline files."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(r"c:\Users\User\OneDrive\Documents\ULTRA_Project")
RES = ROOT / "results"
ARCH = RES / "_archive_development_cv"
FIGS = ROOT / "validate" / "dual_index_routing" / "figures"
DEST_FIGS = RES / "figures"

KEEP = {
    "roman_urdu_results.json",
    "phase3_retrieval_results.json",
    "phase4_retrieval_results.json",
    "robustness_report.csv",
    "CURRENT.json",
    "CURRENT.txt",
    "README.md",
    "_align_results_folder.py",
}

CURRENT = {
    "as_of": "2026-08-23",
    "do_not_mix": True,
    "dictionary_pairs_on_disk": 198,
    "deployed_svm_features": 12,
    "development_cv": {
        "note": "Learnability only. Not the defense headline.",
        "svm_some_splits_pct": 100.0,
        "theta150_pct": 50.0,
        "roman_urdu_p15_pct": 92.5,
        "llm_style_routing_match": "development 14-query comparison; SVM ~0.45 ms",
    },
    "frozen_phase3b_v2_primary_n50": {
        "svm_pct": 86.0,
        "wordcount_pct": 84.0,
        "svm_correct": 43,
        "wordcount_correct": 42,
        "mcnemar_svm_only": 2,
        "mcnemar_wc_only": 1,
        "mcnemar_p": 1.0,
        "note": "Eight-feature V2. Not overwritten by 12-feature retrain.",
    },
    "frozen_traps_H001_H040": {
        "svm_pct": 60.0,
        "wordcount_pct": 20.0,
        "theta150_pct": 50.0,
        "mcnemar_16_0_p": "<0.001",
        "cue_n": 18,
        "cue_svm_pct": 100.0,
        "cue_wc_pct": 11.11,
        "no_cue_n": 22,
        "no_cue_both_pct": 27.27,
    },
    "heldout_dual_index_p5_n40_judgments_400": {
        "wordcount_p5_pct": 36.50,
        "always_headline_or_theta_p5_pct": 35.00,
        "always_full_p5_pct": 34.25,
        "svm_p5_pct": 33.00,
        "ndcg5_always_headline": 0.6868,
        "ndcg5_wordcount": 0.6476,
        "ndcg5_svm": 0.6149,
        "ndcg5_always_full": 0.6020,
        "note": "Classification win did not transfer to P@5.",
    },
    "phase25_dual_index_p5_n33_depth5": {
        "svm_p5_pct": 35.76,
        "wordcount_p5_pct": 35.15,
        "theta150_p5_pct": 32.73,
    },
    "do_not_report": ["96% Phase 3B after trap retrain (leakage)"],
    "figures": [
        "figures/fig_two_rooms_lights.png",
        "figures/fig_three_evaluation_layers.png",
        "figures/fig_cue_split.png",
        "figures/fig_heldout_p5.png",
    ],
}


def main():
    ARCH.mkdir(exist_ok=True)
    DEST_FIGS.mkdir(exist_ok=True)
    moved = []
    for src in RES.iterdir():
        if not src.is_file():
            continue
        if src.name in KEEP or src.suffix.lower() not in {".json", ".txt", ".csv"}:
            continue
        low = src.name.lower()
        if low.startswith("phase3_") or low.startswith("phase4_"):
            continue
        if "roman" in low or "robust" in low:
            continue
        dest = ARCH / src.name
        if dest.exists():
            dest.unlink()
        shutil.move(str(src), str(dest))
        moved.append(src.name)
    for png in FIGS.glob("fig_*.png"):
        shutil.copy2(png, DEST_FIGS / png.name)
    (RES / "CURRENT.json").write_text(
        json.dumps(CURRENT, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    lines = [
        "CURRENT FROZEN RESULTS (23 Aug 2026)",
        "Do not mix these tables. Do not report 96%.",
        "",
        "Dictionary on disk: 198 pairs. Deployed SVM: 12 features.",
        "Phase 3B V2 (50 primary): SVM 86% vs word count 84% (McNemar p=1.0).",
        "Traps H001-H040: SVM 60% vs word count 20% vs theta=150 50% (McNemar 16-0).",
        "Cue split: 18/18 vs 2/18 with cue words; both 27.27% without (n=22).",
        "Held-out dual-index P@5: WC 36.50, headline/theta 35.00, full 34.25, SVM 33.00.",
        "nDCG@5 highest for always-headline (0.6868).",
        "Phase 2.5 P@5 n=33: SVM 35.76 vs WC 35.15 vs theta 32.73.",
        "",
        "Figures: results/figures/",
        "Archived development/CV 100%-headline files: results/_archive_development_cv/",
        "Kept as supporting history: roman_urdu_results.json, phase3/4 retrieval json, robustness_report.csv",
    ]
    (RES / "CURRENT.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    readme = """# results/

**Current numbers:** `CURRENT.txt` and `CURRENT.json` (frozen dual-index story).

**Current figures:** `figures/` (two rooms, three layers, cue split, held-out P@5).

**Archive:** `_archive_development_cv/` — old files that treated development 100% vs θ=150 as the headline. Do not cite them in defense.

**Still here as supporting history (not headline):**
- `roman_urdu_results.json` — development Roman Urdu P@15 (92.5% vs 0%)
- `phase3_retrieval_results.json` / `phase4_retrieval_results.json` — earlier retrieval checks
- `robustness_report.csv` — development robustness (includes 100% CV; not Phase 3B)
"""
    (RES / "README.md").write_text(readme, encoding="utf-8")
    print("archived", moved)
    print("wrote CURRENT.txt / CURRENT.json / figures/")


if __name__ == "__main__":
    main()
